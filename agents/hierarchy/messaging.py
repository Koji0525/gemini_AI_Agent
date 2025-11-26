#!/usr/bin/env python3
"""
Message Bus
エージェント間メッセージング

【責務】
- メッセージ配送
- 優先度管理
- ログ記録

Google Docstring形式
"""
import logging
import queue
from datetime import datetime
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Message:
    """メッセージクラス

    Attributes:
        from_agent (str): 送信元エージェントID
        to_agent (str): 宛先エージェントID
        type (str): メッセージタイプ
        priority (int): 優先度（1-5）
        content (Dict): メッセージ本体
        timestamp (str): タイムスタンプ
    """

    def __init__(
        self, from_agent: str, to_agent: str, msg_type: str, content: Dict, priority: int = 3
    ):
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.type = msg_type
        self.content = content
        self.priority = priority
        self.timestamp = datetime.now().isoformat()


class MessageBus:
    """
    Message Bus - エージェント間通信

    Attributes:
        message_queue (queue.PriorityQueue): 優先度付きキュー
        message_history (List[Message]): メッセージ履歴
    """

    def __init__(self):
        """初期化"""
        self.message_queue = queue.PriorityQueue()
        self.message_history = []

        logger.info("📬 Message Bus 初期化")

    def send(self, message: Message):
        """メッセージ送信

        Args:
            message: メッセージオブジェクト
        """
        # 優先度の高い順に取り出すため、優先度を反転（1が最高）
        priority = 6 - message.priority

        self.message_queue.put((priority, message))
        self.message_history.append(message)

        logger.info(f"📤 メッセージ送信: {message.from_agent} → {message.to_agent}")

    def receive(self, agent_id: str) -> List[Message]:
        """メッセージ受信

        Args:
            agent_id: エージェントID

        Returns:
            該当エージェント宛のメッセージ一覧
        """
        messages = []
        temp_queue = queue.PriorityQueue()

        # キューから全メッセージを取り出し
        while not self.message_queue.empty():
            priority, msg = self.message_queue.get()

            if msg.to_agent == agent_id:
                messages.append(msg)
            else:
                # 該当しないメッセージは戻す
                temp_queue.put((priority, msg))

        # 残りのメッセージをキューに戻す
        self.message_queue = temp_queue

        logger.info(f"📥 メッセージ受信: {agent_id} - {len(messages)}件")

        return messages
