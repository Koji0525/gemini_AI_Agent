#!/usr/bin/env python3
"""
既存システムとの統合ブリッジ

目的: 既存システム（complete_engine_ultimate.py）を変更せずに、
     新機能（共有黒板、Reflexion）を利用可能にする

設計原則:
- 既存ファイルは一切変更しない
- ラッパーパターンで機能追加
- 後方互換性100%維持
"""

from typing import Dict, Optional
from pathlib import Path
import sys

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class LegacySystemBridge:
    """
    既存システムとの統合ブリッジ
    
    使用例:
        bridge = LegacySystemBridge()
        
        # 既存システムのタスクを新システムで実行
        result = bridge.execute_task_with_enhancements(
            task_id="task_001",
            task_data={...},
            use_reflexion=True,
            use_blackboard=True
        )
    """
    
    def __init__(self):
        """初期化"""
        # 既存システムのインポート（変更なし）
        try:
            from tools.sheets_manager import GoogleSheetsManager
            self.sheets_manager = GoogleSheetsManager()
            print("✅ 既存システム接続成功")
        except Exception as e:
            print(f"⚠️  既存システム接続スキップ: {e}")
            self.sheets_manager = None
        
        # 新システム
        from agents.integration.shared_blackboard_manager import SharedBlackboardManager
        from agents.quality.reflexion_loop import ReflexionLoop
        
        self.blackboard_class = SharedBlackboardManager
        self.reflexion_class = ReflexionLoop
    
    def execute_task_with_enhancements(
        self,
        task_id: str,
        task_data: Dict,
        use_reflexion: bool = False,
        use_blackboard: bool = False
    ) -> Dict:
        """
        タスクを新機能付きで実行
        
        Args:
            task_id: タスクID
            task_data: タスクデータ
            use_reflexion: Reflexionループを使用するか
            use_blackboard: 共有黒板を使用するか
        
        Returns:
            実行結果
        """
        print(f"\n{'='*60}")
        print(f"🚀 拡張タスク実行: {task_id}")
        print(f"   Reflexion: {'ON' if use_reflexion else 'OFF'}")
        print(f"   Blackboard: {'ON' if use_blackboard else 'OFF'}")
        print(f"{'='*60}")
        
        # 1. 既存システムでタスク実行
        result = self._execute_legacy_task(task_data)
        
        # 2. Reflexionループ（オプション）
        if use_reflexion:
            print("\n🔄 Reflexionループ適用中...")
            loop = self.reflexion_class(task_id=task_id)
            result, success = loop.execute_with_reflexion(
                executor_func=lambda td: self._execute_legacy_task(td),
                task_data=task_data
            )
        
        # 3. 共有黒板に記録（オプション）
        if use_blackboard:
            print("\n📋 共有黒板に記録中...")
            goal_id = task_data.get('goal_id', 'default')
            blackboard = self.blackboard_class(goal_id=goal_id)
            
            blackboard.write_section(f"task_{task_id}", {
                'status': 'completed',
                'result': result,
                'used_reflexion': use_reflexion
            })
        
        print(f"\n✅ タスク完了: {task_id}")
        
        return result
    
    def _execute_legacy_task(self, task_data: Dict) -> Dict:
        """
        既存システムでタスクを実行（ダミー実装）
        
        実際は既存の高品質実行エンジンを呼び出す
        """
        return {
            'status': 'completed',
            'output': 'タスク実行結果',
            'quality_score': 60  # 既存システムの平均
        }

# ========================================
# テスト
# ========================================
if __name__ == "__main__":
    bridge = LegacySystemBridge()
    
    # テスト実行
    result = bridge.execute_task_with_enhancements(
        task_id="test_001",
        task_data={
            'goal_id': '6',
            'description': 'テストタスク'
        },
        use_reflexion=True,
        use_blackboard=True
    )
    
    print(f"\n最終結果: {result}")
