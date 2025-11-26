#!/usr/bin/env python3
"""
Reflexion統合Executorラッパー

目的: 既存の high_quality_executor_v8.py を変更せずに、
     Reflexionループ機能を追加

設計原則:
- 既存Executorは一切変更しない
- デコレーターパターンで機能追加
- 後方互換性100%維持
"""

import sys
from pathlib import Path
from typing import Dict, Optional, Callable

# プロジェクトルート
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class ReflexionExecutorWrapper:
    """
    Reflexion統合Executorラッパー
    
    既存のExecutorをラップしてReflexion機能を追加
    
    使用例:
        # 既存Executorをラップ
        from agents.task_execution.high_quality_executor_v8 import HighQualityExecutorV8
        
        executor = HighQualityExecutorV8()
        reflexion_executor = ReflexionExecutorWrapper(
            base_executor=executor,
            enable_reflexion=True
        )
        
        # Reflexion付きで実行
        result = reflexion_executor.execute_task(task_data)
    """
    
    def __init__(
        self,
        base_executor: Optional[object] = None,
        enable_reflexion: bool = True,
        quality_threshold: int = 80,
        max_loops: int = 3
    ):
        """
        初期化
        
        Args:
            base_executor: 既存のExecutor（Noneの場合はダミー）
            enable_reflexion: Reflexionを有効にするか
            quality_threshold: 品質基準点
            max_loops: 最大ループ回数
        """
        self.base_executor = base_executor
        self.enable_reflexion = enable_reflexion
        self.quality_threshold = quality_threshold
        self.max_loops = max_loops
        
        # Reflexionループ初期化（遅延ロード）
        self.reflexion_loop = None
        
        print(f"✅ ReflexionExecutorWrapper初期化")
        print(f"   Reflexion: {'ON' if enable_reflexion else 'OFF'}")
        print(f"   品質基準: {quality_threshold}点")
    
    def execute_task(self, task_data: Dict) -> Dict:
        """
        タスクを実行（Reflexion付き）
        
        Args:
            task_data: タスクデータ
        
        Returns:
            実行結果
        """
        task_id = task_data.get('task_id', 'unknown')
        
        if not self.enable_reflexion:
            # Reflexion無効 → 通常実行
            return self._execute_base(task_data)
        
        # Reflexion有効 → ループ実行
        from agents.quality.reflexion_loop import ReflexionLoop
        
        self.reflexion_loop = ReflexionLoop(
            task_id=task_id,
            quality_threshold=self.quality_threshold,
            max_loops=self.max_loops
        )
        
        result, success = self.reflexion_loop.execute_with_reflexion(
            executor_func=self._execute_base,
            task_data=task_data
        )
        
        # 成功フラグを結果に追加
        result['reflexion_success'] = success
        result['reflexion_loops'] = len(self.reflexion_loop.history)
        
        return result
    
    def _execute_base(self, task_data: Dict) -> Dict:
        """
        ベースExecutorで実行
        
        Args:
            task_data: タスクデータ
        
        Returns:
            実行結果
        """
        if self.base_executor and hasattr(self.base_executor, 'execute_task'):
            # 既存Executorを使用
            return self.base_executor.execute_task(task_data)
        else:
            # ダミー実行（開発・テスト用）
            return self._dummy_execute(task_data)
    
    def _dummy_execute(self, task_data: Dict) -> Dict:
        """ダミー実行（開発・テスト用）"""
        description = task_data.get('description', 'No description')
        
        # フィードバックが含まれている場合は改善版を返す
        has_feedback = 'reflexion_feedback' in task_data
        
        output = f"""
# タスク実行結果

## 概要
{description}

## 実行内容
タスクを実行しました。

## 結果
{'改善版の' if has_feedback else '初回の'}実行結果です。

{'## フィードバック適用' if has_feedback else ''}
{'以下の改善を実施しました：' if has_feedback else ''}
{'- データの完全性を向上' if has_feedback else ''}
{'- 具体例を追加' if has_feedback else ''}
{'- 構造を整理' if has_feedback else ''}
"""
        
        return {
            'status': 'completed',
            'output': output,
            'description': description,
            'quality_score': 65 if has_feedback else 60
        }
    
    def get_statistics(self) -> Dict:
        """統計情報を取得"""
        if self.reflexion_loop:
            return self.reflexion_loop.get_statistics()
        return {}

# ========================================
# テスト
# ========================================
if __name__ == "__main__":
    print("="*60)
    print("🧪 ReflexionExecutorWrapper テスト")
    print("="*60)
    
    # ラッパー作成
    wrapper = ReflexionExecutorWrapper(
        base_executor=None,  # ダミーモード
        enable_reflexion=True,
        quality_threshold=80
    )
    
    # テストタスク
    test_task = {
        'task_id': 'test_wrapper_001',
        'description': '金融市場分析レポート作成'
    }
    
    print("\n🚀 タスク実行...")
    result = wrapper.execute_task(test_task)
    
    print(f"\n✅ 実行完了")
    print(f"   ステータス: {result.get('status')}")
    print(f"   Reflexion成功: {result.get('reflexion_success')}")
    print(f"   ループ回数: {result.get('reflexion_loops')}")
    
    # 統計情報
    stats = wrapper.get_statistics()
    if stats:
        print(f"\n📊 統計情報:")
        import json
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    print("\n" + "="*60)
    print("✅ テスト完了")
    print("="*60)
