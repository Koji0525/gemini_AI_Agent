#!/usr/bin/env python3
"""
Reflexionループエンジン

目的: タスク実行結果を自己批評し、品質を向上させる
アーキテクチャ: Execute → Critique → Improve → Re-execute

品質向上の流れ:
1. 初回実行: 60点（現在の平均）
2. Reflexion Loop 1回目: +10点 → 70点
3. Reflexion Loop 2回目: +10点 → 80点
4. Reflexion Loop 3回目: +5点 → 85点

目標: 平均品質スコア 85点以上
"""

import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

class ReflexionLoop:
    """
    Reflexionループエンジン
    
    責務:
    - タスク実行結果の評価
    - 批評フィードバック生成
    - 改善案の提示
    - 再実行の管理
    
    使用例:
        loop = ReflexionLoop(
            task_id="task_001",
            quality_threshold=80,
            max_loops=3
        )
        
        result = loop.execute_with_reflexion(
            executor=task_executor,
            task_data=task_data
        )
    """
    
    # 品質基準
    QUALITY_THRESHOLD = 80  # この点数以上で合格
    MAX_LOOPS = 3  # 最大ループ回数
    
    def __init__(
        self,
        task_id: str,
        quality_threshold: int = QUALITY_THRESHOLD,
        max_loops: int = MAX_LOOPS,
        log_dir: str = "agent_outputs/reflexion_logs"
    ):
        """
        初期化
        
        Args:
            task_id: タスクID
            quality_threshold: 品質基準点（これ以上で合格）
            max_loops: 最大ループ回数
            log_dir: ログ出力ディレクトリ
        """
        self.task_id = task_id
        self.quality_threshold = quality_threshold
        self.max_loops = max_loops
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # ループ履歴
        self.history: List[Dict] = []
    
    def execute_with_reflexion(
        self,
        executor_func: callable,
        task_data: Dict,
        evaluator_func: Optional[callable] = None
    ) -> Tuple[Dict, bool]:
        """
        Reflexionループ付きでタスクを実行
        
        Args:
            executor_func: タスク実行関数
            task_data: タスクデータ
            evaluator_func: 品質評価関数（Noneの場合はダミー評価）
        
        Returns:
            (実行結果, 成功フラグ)
        """
        print(f"\n{'='*60}")
        print(f"🔄 Reflexionループ開始: {self.task_id}")
        print(f"{'='*60}")
        
        feedback = None
        
        for loop_num in range(1, self.max_loops + 1):
            print(f"\n[ループ {loop_num}/{self.max_loops}]")
            
            # 1. タスク実行
            print("   📝 タスク実行中...")
            if feedback:
                # フィードバックを追加
                task_data['reflexion_feedback'] = feedback
            
            result = executor_func(task_data)
            
            # 2. 品質評価
            print("   📊 品質評価中...")
            if evaluator_func:
                quality_score = evaluator_func(result)
            else:
                # ダミー評価（実装デモ用）
                quality_score = self._dummy_evaluate(result, loop_num)
            
            print(f"   品質スコア: {quality_score}点")
            
            # 履歴記録
            iteration = {
                'loop_num': loop_num,
                'quality_score': quality_score,
                'result': result,
                'feedback': feedback,
                'timestamp': datetime.now().isoformat()
            }
            self.history.append(iteration)
            
            # 3. 品質判定
            if quality_score >= self.quality_threshold:
                print(f"\n✅ 品質基準達成: {quality_score} >= {self.quality_threshold}")
                self._save_log(success=True)
                return result, True
            
            # 4. 批評とフィードバック生成
            if loop_num < self.max_loops:
                print("   🤔 批評フィードバック生成中...")
                feedback = self._generate_feedback(result, quality_score)
                print(f"   フィードバック: {feedback[:100]}...")
        
        # 最大ループ数に達した
        print(f"\n⚠️  最大ループ数に達しました（最終スコア: {quality_score}）")
        print(f"   人間にエスカレーション推奨")
        
        self._save_log(success=False)
        
        return result, False
    
    def _dummy_evaluate(self, result: Dict, loop_num: int) -> int:
        """
        ダミー品質評価（実装デモ用）
        
        実際は外部のCriticエージェントを使用
        
        Args:
            result: タスク実行結果
            loop_num: 現在のループ番号
        
        Returns:
            品質スコア（0-100）
        """
        # 初回: 60点
        # 2回目: 70点
        # 3回目: 85点
        base_score = 60
        improvement = (loop_num - 1) * 10 + (5 if loop_num == 3 else 0)
        
        return min(base_score + improvement, 100)
    
    def _generate_feedback(self, result: Dict, quality_score: int) -> str:
        """
        批評フィードバックを生成
        
        実際はCriticエージェント（GPT-4o-mini）を使用
        
        Args:
            result: タスク実行結果
            quality_score: 品質スコア
        
        Returns:
            フィードバック文字列
        """
        # ダミーフィードバック
        if quality_score < 70:
            return """
以下の点を改善してください：
1. データの完全性: すべての必須フィールドを埋めてください
2. 具体性: 抽象的な表現を避け、具体例や数値を追加してください
3. 構造化: 見出しや箇条書きを使って読みやすくしてください
"""
        else:
            return """
以下の点をさらに改善できます：
1. 詳細度: より詳細な分析や説明を追加してください
2. 検証: データの出典や根拠を明記してください
3. 図表: 適切な図表や可視化を追加してください
"""
    
    def _save_log(self, success: bool):
        """ログを保存"""
        log_file = self.log_dir / f"{self.task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        log_data = {
            'task_id': self.task_id,
            'success': success,
            'total_loops': len(self.history),
            'final_score': self.history[-1]['quality_score'] if self.history else 0,
            'history': self.history,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 ログ保存: {log_file}")
    
    def get_statistics(self) -> Dict:
        """統計情報を取得"""
        if not self.history:
            return {}
        
        scores = [h['quality_score'] for h in self.history]
        
        return {
            'total_loops': len(self.history),
            'initial_score': scores[0],
            'final_score': scores[-1],
            'improvement': scores[-1] - scores[0],
            'avg_score': sum(scores) / len(scores)
        }

# ========================================
# 使用例とテスト
# ========================================
if __name__ == "__main__":
    print("="*60)
    print("🧪 Reflexionループエンジン テスト")
    print("="*60)
    
    # ダミータスク実行関数
    def dummy_executor(task_data):
        return {
            'status': 'completed',
            'output': '実行結果のダミーデータ',
            'feedback_applied': 'reflexion_feedback' in task_data
        }
    
    # Reflexionループ実行
    loop = ReflexionLoop(task_id="test_task_001")
    
    result, success = loop.execute_with_reflexion(
        executor_func=dummy_executor,
        task_data={'description': 'テストタスク'}
    )
    
    # 統計表示
    stats = loop.get_statistics()
    print(f"\n📊 統計情報:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    print(f"\n✅ テスト完了")
