#!/usr/bin/env python3
"""
共有黒板マネージャー (Shared Blackboard Manager)

目的: エージェント間で構造化された情報を共有
アーキテクチャ: ファイルベースJSON + 楽観的ロック

データ構造:
{
    "meta": {
        "goal_id": "6",
        "version": 15,
        "last_updated": "2025-11-26T10:00:00",
        "locked_by": null,
        "lock_expires_at": null
    },
    "goal_info": {
        "description": "金融市場分析レポート作成",
        "target_completion": "2025-12-01",
        "priority": "high",
        "assigned_to": "executive_manager"
    },
    "progress": {
        "total_tasks": 50,
        "completed": 30,
        "in_progress": 10,
        "pending": 10,
        "percentage": 60.0,
        "estimated_completion": "2025-11-30"
    },
    "quality_metrics": {
        "avg_score": 75.5,
        "low_quality_count": 5,
        "reflexion_loops_total": 20,
        "reflexion_success_rate": 0.75
    },
    "sections": {
        "data_collection": {
            "owner": "worker_agent_1",
            "status": "completed",
            "quality_score": 85,
            "output": "data/market_data.csv",
            "metadata": {...}
        },
        "financial_analysis": {
            "owner": "worker_agent_2",
            "status": "in_progress",
            "depends_on": ["data_collection"],
            "progress_percent": 60,
            "estimated_completion": "2025-11-27"
        }
    },
    "dependencies": {
        "financial_analysis": ["data_collection"],
        "report_generation": ["financial_analysis", "visualization"]
    },
    "milestones": [
        {
            "name": "データ収集完了",
            "target": "2025-11-25",
            "achieved": true,
            "achieved_at": "2025-11-25T14:30:00"
        }
    ],
    "alerts": [
        {
            "level": "warning",
            "message": "品質スコアが低いタスクあり",
            "created_at": "2025-11-26T10:00:00",
            "acknowledged": false
        }
    ]
}
"""

import json
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from filelock import FileLock
import time

class SharedBlackboardManager:
    """
    共有黒板マネージャー
    
    責務:
    - ゴールステートの読み書き
    - 楽観的ロック（Optimistic Locking）
    - 変更履歴記録
    - イベント通知
    
    使用例:
        blackboard = SharedBlackboardManager(goal_id="6")
        
        # セクション読み取り
        data = blackboard.read_section("data_collection")
        
        # セクション書き込み
        blackboard.write_section("data_collection", {
            "owner": "worker_1",
            "status": "completed",
            "quality_score": 85
        })
        
        # 変更通知購読
        blackboard.subscribe_changes("data_collection", on_data_updated)
    """
    
    def __init__(self, goal_id: str, base_dir: str = "shared_states"):
        """
        初期化
        
        Args:
            goal_id: ゴールID
            base_dir: 黒板ファイルの保存ディレクトリ
        """
        self.goal_id = goal_id
        self.base_dir = Path(base_dir)
        self.state_path = self.base_dir / f"goal_{goal_id}_state.json"
        self.history_dir = self.base_dir / "history" / f"goal_{goal_id}"
        self.lock_path = self.base_dir / f"goal_{goal_id}_state.lock"
        
        # イベント購読者
        self.subscribers: Dict[str, List[Callable]] = {}
        
        # ディレクトリ作成
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
        # 初期化
        if not self.state_path.exists():
            self._initialize_state()
    
    def _initialize_state(self):
        """初期ステートを作成"""
        initial_state = {
            "meta": {
                "goal_id": self.goal_id,
                "version": 1,
                "last_updated": datetime.now().isoformat(),
                "locked_by": None,
                "lock_expires_at": None
            },
            "goal_info": {},
            "progress": {
                "total_tasks": 0,
                "completed": 0,
                "in_progress": 0,
                "pending": 0,
                "percentage": 0.0
            },
            "quality_metrics": {
                "avg_score": 0,
                "low_quality_count": 0,
                "reflexion_loops_total": 0,
                "reflexion_success_rate": 0.0
            },
            "sections": {},
            "dependencies": {},
            "milestones": [],
            "alerts": []
        }
        
        with open(self.state_path, 'w') as f:
            json.dump(initial_state, f, indent=2, ensure_ascii=False)
    
    def read_full_state(self) -> Dict:
        """
        ステート全体を読み取り
        
        Returns:
            ステート全体のDict
        """
        with FileLock(self.lock_path, timeout=5):
            with open(self.state_path, 'r') as f:
                return json.load(f)
    
    def read_section(self, section_name: str) -> Optional[Dict]:
        """
        特定セクションのみ読み取り
        
        Args:
            section_name: セクション名
        
        Returns:
            セクションデータ、存在しない場合はNone
        """
        state = self.read_full_state()
        return state.get("sections", {}).get(section_name)
    
    def write_section(
        self,
        section_name: str,
        data: Dict,
        expected_version: Optional[int] = None
    ) -> bool:
        """
        楽観的ロックでセクションを書き込み
        
        Args:
            section_name: セクション名
            data: 書き込むデータ
            expected_version: 期待されるバージョン番号（楽観的ロック用）
        
        Returns:
            成功した場合True、バージョン競合の場合False
        """
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                with FileLock(self.lock_path, timeout=5):
                    # 現在のステートを読み取り
                    with open(self.state_path, 'r') as f:
                        state = json.load(f)
                    
                    current_version = state["meta"]["version"]
                    
                    # バージョンチェック（楽観的ロック）
                    if expected_version is not None and current_version != expected_version:
                        print(f"⚠️  バージョン競合: 期待={expected_version}, 現在={current_version}")
                        # リトライ
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                    
                    # セクション更新
                    if "sections" not in state:
                        state["sections"] = {}
                    
                    state["sections"][section_name] = data
                    
                    # メタ情報更新
                    state["meta"]["version"] = current_version + 1
                    state["meta"]["last_updated"] = datetime.now().isoformat()
                    
                    # 履歴保存
                    self._save_history(state, current_version)
                    
                    # ステート保存
                    with open(self.state_path, 'w') as f:
                        json.dump(state, f, indent=2, ensure_ascii=False)
                    
                    # イベント通知
                    self._notify_subscribers(section_name, data)
                    
                    return True
                    
            except Exception as e:
                print(f"❌ 書き込みエラー (試行 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    return False
        
        return False
    
    def update_progress(self, progress_data: Dict):
        """進捗情報を更新"""
        with FileLock(self.lock_path, timeout=5):
            with open(self.state_path, 'r') as f:
                state = json.load(f)
            
            state["progress"].update(progress_data)
            state["meta"]["version"] += 1
            state["meta"]["last_updated"] = datetime.now().isoformat()
            
            with open(self.state_path, 'w') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
    
    def update_quality_metrics(self, metrics: Dict):
        """品質メトリクスを更新"""
        with FileLock(self.lock_path, timeout=5):
            with open(self.state_path, 'r') as f:
                state = json.load(f)
            
            state["quality_metrics"].update(metrics)
            state["meta"]["version"] += 1
            state["meta"]["last_updated"] = datetime.now().isoformat()
            
            with open(self.state_path, 'w') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
    
    def add_alert(self, level: str, message: str):
        """アラートを追加"""
        alert = {
            "level": level,
            "message": message,
            "created_at": datetime.now().isoformat(),
            "acknowledged": False
        }
        
        with FileLock(self.lock_path, timeout=5):
            with open(self.state_path, 'r') as f:
                state = json.load(f)
            
            state["alerts"].append(alert)
            state["meta"]["version"] += 1
            state["meta"]["last_updated"] = datetime.now().isoformat()
            
            with open(self.state_path, 'w') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
    
    def subscribe_changes(self, section_name: str, callback: Callable):
        """
        セクションの変更通知を購読
        
        Args:
            section_name: 監視するセクション名
            callback: 変更時に呼び出される関数
        """
        if section_name not in self.subscribers:
            self.subscribers[section_name] = []
        
        self.subscribers[section_name].append(callback)
    
    def _notify_subscribers(self, section_name: str, data: Dict):
        """購読者に変更を通知"""
        if section_name in self.subscribers:
            for callback in self.subscribers[section_name]:
                try:
                    callback(section_name, data)
                except Exception as e:
                    print(f"⚠️  購読者通知エラー: {e}")
    
    def _save_history(self, state: Dict, version: int):
        """変更履歴を保存"""
        history_file = self.history_dir / f"v{version:04d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(history_file, 'w') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        # 古い履歴を削除（直近100件のみ保持）
        history_files = sorted(self.history_dir.glob("*.json"))
        if len(history_files) > 100:
            for old_file in history_files[:-100]:
                old_file.unlink()
    
    def get_version(self) -> int:
        """現在のバージョン番号を取得"""
        state = self.read_full_state()
        return state["meta"]["version"]
    
    def get_statistics(self) -> Dict:
        """統計情報を取得"""
        state = self.read_full_state()
        
        return {
            "version": state["meta"]["version"],
            "total_sections": len(state.get("sections", {})),
            "total_alerts": len(state.get("alerts", [])),
            "progress_percentage": state.get("progress", {}).get("percentage", 0),
            "avg_quality_score": state.get("quality_metrics", {}).get("avg_score", 0)
        }

# ========================================
# 使用例
# ========================================
if __name__ == "__main__":
    # テスト用
    print("="*60)
    print("🧪 共有黒板マネージャー テスト")
    print("="*60)
    
    # インスタンス作成
    blackboard = SharedBlackboardManager(goal_id="test_001")
    
    # セクション書き込み
    print("\n[1/4] セクション書き込み...")
    success = blackboard.write_section("data_collection", {
        "owner": "worker_1",
        "status": "completed",
        "quality_score": 85,
        "output": "data/test.csv"
    })
    print(f"   結果: {'✅ 成功' if success else '❌ 失敗'}")
    
    # セクション読み取り
    print("\n[2/4] セクション読み取り...")
    data = blackboard.read_section("data_collection")
    print(f"   データ: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    # 進捗更新
    print("\n[3/4] 進捗更新...")
    blackboard.update_progress({
        "total_tasks": 10,
        "completed": 5,
        "percentage": 50.0
    })
    print(f"   ✅ 進捗更新完了")
    
    # 統計情報取得
    print("\n[4/4] 統計情報取得...")
    stats = blackboard.get_statistics()
    print(f"   統計: {json.dumps(stats, indent=2, ensure_ascii=False)}")
    
    print("\n" + "="*60)
    print("✅ テスト完了")
    print("="*60)
