#!/usr/bin/env python3
"""
メッセージング層
階層型エージェント間の通信プロトコル

Google Docstring形式
"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """メッセージ種別"""
    TASK_ASSIGNMENT = "task_assignment"      # タスク割り当て
    PROGRESS_REPORT = "progress_report"      # 進捗報告
    ESCALATION = "escalation"                # エスカレーション
    COMPLETION = "completion"                # 完了通知
    REQUEST = "request"                      # 要求
    RESPONSE = "response"                    # 応答

@dataclass
class Message:
    """
    エージェント間メッセージ
    
    Attributes:
        from_agent (str): 送信元エージェントID
        to_agent (str): 宛先エージェントID
        type (MessageType): メッセージ種別
        priority (int): 優先度 1(低) - 5(高)
        content (Dict): メッセージ本体
        timestamp (str): タイムスタンプ
        message_id (str): メッセージID
    """
    from_agent: str
    to_agent: str
    type: MessageType
    priority: int
    content: Dict
    timestamp: str = None
    message_id: str = None
    
    def __post_init__(self):
        """初期化後処理"""
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.message_id is None:
            self.message_id = f"msg_{self.from_agent}_{self.to_agent}_{self.timestamp}"
    
    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        data = asdict(self)
        data['type'] = self.type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        """辞書から生成"""
        data = data.copy()
        data['type'] = MessageType(data['type'])
        return cls(**data)

class MessageBus:
    """
    メッセージバス
    エージェント間メッセージの配送を管理
    
    Attributes:
        storage_dir (Path): メッセージ保存先
        subscribers (Dict): メッセージ購読者
    """
    
    def __init__(self, storage_dir: str = "shared_states/messages"):
        """
        初期化
        
        Args:
            storage_dir (str): メッセージ保存ディレクトリ
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.subscribers: Dict[str, List[Callable]] = {}
        logger.info(f"MessageBus初期化: {self.storage_dir}")
    
    def send(self, message: Message) -> bool:
        """
        メッセージ送信
        
        Args:
            message (Message): 送信メッセージ
            
        Returns:
            bool: 送信成功
        """
        try:
            # ファイルに保存
            inbox_dir = self.storage_dir / message.to_agent / "inbox"
            inbox_dir.mkdir(parents=True, exist_ok=True)
            
            msg_file = inbox_dir / f"{message.message_id}.json"
            with open(msg_file, 'w') as f:
                json.dump(message.to_dict(), f, indent=2)
            
            logger.info(f"メッセージ送信: {message.from_agent} → {message.to_agent} ({message.type.value})")
            
            # 購読者に通知
            self._notify_subscribers(message)
            
            return True
            
        except Exception as e:
            logger.error(f"メッセージ送信失敗: {e}")
            return False
    
    def receive(self, agent_id: str, message_type: Optional[MessageType] = None) -> List[Message]:
        """
        メッセージ受信
        
        Args:
            agent_id (str): 受信者ID
            message_type (MessageType, optional): メッセージ種別フィルタ
            
        Returns:
            List[Message]: 受信メッセージリスト
        """
        inbox_dir = self.storage_dir / agent_id / "inbox"
        if not inbox_dir.exists():
            return []
        
        messages = []
        for msg_file in inbox_dir.glob("*.json"):
            try:
                with open(msg_file, 'r') as f:
                    data = json.load(f)
                    message = Message.from_dict(data)
                    
                    # フィルタ適用
                    if message_type is None or message.type == message_type:
                        messages.append(message)
            except Exception as e:
                logger.error(f"メッセージ読み取り失敗: {msg_file} - {e}")
        
        # 優先度でソート
        messages.sort(key=lambda m: m.priority, reverse=True)
        return messages
    
    def mark_as_read(self, agent_id: str, message_id: str):
        """
        メッセージを既読にする（アーカイブ）
        
        Args:
            agent_id (str): エージェントID
            message_id (str): メッセージID
        """
        inbox_file = self.storage_dir / agent_id / "inbox" / f"{message_id}.json"
        if not inbox_file.exists():
            return
        
        archive_dir = self.storage_dir / agent_id / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        archive_file = archive_dir / f"{message_id}.json"
        inbox_file.rename(archive_file)
        logger.debug(f"メッセージアーカイブ: {message_id}")
    
    def subscribe(self, agent_id: str, callback: Callable[[Message], None]):
        """
        メッセージ通知を購読
        
        Args:
            agent_id (str): 購読者ID
            callback (Callable): コールバック関数
        """
        if agent_id not in self.subscribers:
            self.subscribers[agent_id] = []
        self.subscribers[agent_id].append(callback)
        logger.info(f"購読登録: {agent_id}")
    
    def _notify_subscribers(self, message: Message):
        """
        購読者に通知
        
        Args:
            message (Message): 通知メッセージ
        """
        if message.to_agent in self.subscribers:
            for callback in self.subscribers[message.to_agent]:
                try:
                    callback(message)
                except Exception as e:
                    logger.error(f"購読者通知失敗: {e}")
    
    def get_statistics(self, agent_id: str) -> Dict:
        """
        統計情報取得
        
        Args:
            agent_id (str): エージェントID
            
        Returns:
            Dict: 統計情報
        """
        inbox_dir = self.storage_dir / agent_id / "inbox"
        archive_dir = self.storage_dir / agent_id / "archive"
        
        inbox_count = len(list(inbox_dir.glob("*.json"))) if inbox_dir.exists() else 0
        archive_count = len(list(archive_dir.glob("*.json"))) if archive_dir.exists() else 0
        
        return {
            'agent_id': agent_id,
            'inbox_count': inbox_count,
            'archive_count': archive_count,
            'total_messages': inbox_count + archive_count
        }

class HierarchicalMessenger:
    """
    階層型メッセンジャー
    Executive → TeamLeader → Worker の通信を管理
    
    Attributes:
        message_bus (MessageBus): メッセージバス
    """
    
    def __init__(self, message_bus: Optional[MessageBus] = None):
        """
        初期化
        
        Args:
            message_bus (MessageBus, optional): メッセージバス
        """
        self.message_bus = message_bus or MessageBus()
        logger.info("HierarchicalMessenger初期化")
    
    def executive_to_team_leader(
        self,
        executive_id: str,
        team_leader_id: str,
        mission: str,
        tasks: List[str],
        deadline: str
    ) -> bool:
        """
        Executive → TeamLeader: ミッション割り当て
        
        Args:
            executive_id (str): Executive ID
            team_leader_id (str): TeamLeader ID
            mission (str): ミッション内容
            tasks (List[str]): タスクIDリスト
            deadline (str): 期限
            
        Returns:
            bool: 送信成功
        """
        message = Message(
            from_agent=executive_id,
            to_agent=team_leader_id,
            type=MessageType.TASK_ASSIGNMENT,
            priority=4,
            content={
                'mission': mission,
                'tasks': tasks,
                'deadline': deadline
            }
        )
        return self.message_bus.send(message)
    
    def team_leader_to_worker(
        self,
        team_leader_id: str,
        worker_id: str,
        task_id: str,
        task_details: Dict
    ) -> bool:
        """
        TeamLeader → Worker: タスク割り当て
        
        Args:
            team_leader_id (str): TeamLeader ID
            worker_id (str): Worker ID
            task_id (str): タスクID
            task_details (Dict): タスク詳細
            
        Returns:
            bool: 送信成功
        """
        message = Message(
            from_agent=team_leader_id,
            to_agent=worker_id,
            type=MessageType.TASK_ASSIGNMENT,
            priority=3,
            content={
                'task_id': task_id,
                'task_details': task_details
            }
        )
        return self.message_bus.send(message)
    
    def worker_to_team_leader(
        self,
        worker_id: str,
        team_leader_id: str,
        task_id: str,
        progress: int,
        quality_score: Optional[int] = None
    ) -> bool:
        """
        Worker → TeamLeader: 進捗報告
        
        Args:
            worker_id (str): Worker ID
            team_leader_id (str): TeamLeader ID
            task_id (str): タスクID
            progress (int): 進捗率 0-100
            quality_score (int, optional): 品質スコア
            
        Returns:
            bool: 送信成功
        """
        message = Message(
            from_agent=worker_id,
            to_agent=team_leader_id,
            type=MessageType.PROGRESS_REPORT,
            priority=2,
            content={
                'task_id': task_id,
                'progress': progress,
                'quality_score': quality_score
            }
        )
        return self.message_bus.send(message)
    
    def team_leader_to_executive(
        self,
        team_leader_id: str,
        executive_id: str,
        team_progress: Dict,
        blockers: List[Dict]
    ) -> bool:
        """
        TeamLeader → Executive: チーム進捗報告
        
        Args:
            team_leader_id (str): TeamLeader ID
            executive_id (str): Executive ID
            team_progress (Dict): チーム進捗
            blockers (List[Dict]): ブロッカー一覧
            
        Returns:
            bool: 送信成功
        """
        priority = 5 if blockers else 3
        message = Message(
            from_agent=team_leader_id,
            to_agent=executive_id,
            type=MessageType.PROGRESS_REPORT,
            priority=priority,
            content={
                'team_progress': team_progress,
                'blockers': blockers
            }
        )
        return self.message_bus.send(message)
    
    def escalate_issue(
        self,
        from_agent: str,
        to_agent: str,
        issue: str,
        blocked_tasks: List[str],
        suggested_action: Optional[str] = None
    ) -> bool:
        """
        問題エスカレーション
        
        Args:
            from_agent (str): 送信元
            to_agent (str): 宛先
            issue (str): 問題内容
            blocked_tasks (List[str]): ブロックされたタスク
            suggested_action (str, optional): 推奨対応
            
        Returns:
            bool: 送信成功
        """
        message = Message(
            from_agent=from_agent,
            to_agent=to_agent,
            type=MessageType.ESCALATION,
            priority=5,
            content={
                'issue': issue,
                'blocked_tasks': blocked_tasks,
                'suggested_action': suggested_action
            }
        )
        return self.message_bus.send(message)

# テスト実行
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("="*60)
    print("メッセージング層テスト")
    print("="*60)
    
    # メッセージバス初期化
    bus = MessageBus()
    messenger = HierarchicalMessenger(bus)
    
    # 1. Executive → TeamLeader
    print("\n[1/4] Executive → TeamLeader")
    success = messenger.executive_to_team_leader(
        executive_id="exec_001",
        team_leader_id="team_data",
        mission="データ収集・整形",
        tasks=["task_001", "task_002"],
        deadline="2025-11-26T18:00:00"
    )
    print(f"   送信結果: {'✅ 成功' if success else '❌ 失敗'}")
    
    # 2. TeamLeader が受信
    print("\n[2/4] TeamLeader が受信")
    messages = bus.receive("team_data", MessageType.TASK_ASSIGNMENT)
    print(f"   受信数: {len(messages)}")
    if messages:
        msg = messages[0]
        print(f"   From: {msg.from_agent}")
        print(f"   Mission: {msg.content['mission']}")
    
    # 3. Worker → TeamLeader
    print("\n[3/4] Worker → TeamLeader")
    success = messenger.worker_to_team_leader(
        worker_id="worker_a1",
        team_leader_id="team_data",
        task_id="task_001",
        progress=75,
        quality_score=85
    )
    print(f"   送信結果: {'✅ 成功' if success else '❌ 失敗'}")
    
    # 4. TeamLeader → Executive
    print("\n[4/4] TeamLeader → Executive")
    success = messenger.team_leader_to_executive(
        team_leader_id="team_data",
        executive_id="exec_001",
        team_progress={'completed': 2, 'total': 3},
        blockers=[]
    )
    print(f"   送信結果: {'✅ 成功' if success else '❌ 失敗'}")
    
    # 統計表示
    print("\n📊 統計情報")
    for agent_id in ["exec_001", "team_data", "worker_a1"]:
        stats = bus.get_statistics(agent_id)
        print(f"   {agent_id}: inbox={stats['inbox_count']}, archive={stats['archive_count']}")
    
    print("\n✅ メッセージング層テスト完了")
