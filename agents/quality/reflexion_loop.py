#!/usr/bin/env python3
"""
Reflexionループエンジン（Critic統合版）

目的: タスク実行結果をCriticエージェントで評価し、品質を向上させる
アーキテクチャ: Execute → Critique → Improve → Re-execute

品質向上の流れ:
1. 初回実行: 60点（現在の平均）
2. Reflexion Loop 1回目: Critic評価 → フィードバック → 再実行
3. Reflexion Loop 2回目: Critic評価 → フィードバック → 再実行
4. Reflexion Loop 3回目: Critic評価 → フィードバック → 再実行

目標: 平均品質スコア 80点以上
"""

import json
from typing import Dict, List, Optional, Tuple, Callable
from datetime import datetime
from pathlib import Path

# Critic統合
try:
    from agents.quality.critic_agent import CriticAgent
    from agents.quality.feedback_generator import FeedbackGenerator
    CRITIC_AVAILABLE = True
except ImportError:
    CRITIC_AVAILABLE = False
    print("⚠️  Criticエージェントが利用できません")

class ReflexionLoop:
    """
    Reflexionループエンジン（Critic統合版）
    
    責務:
    - タスク実行結果の評価（Critic使用）
    - 実行可能なフィードバック生成
    - 改善案に基づく再実行
    - 履歴ログ管理
    
    使用例:
        loop = ReflexionLoop(
            task_id="task_001",
            quality_threshold=80,
            max_loops=3,
            use_critic=True
        )
        
        result, success = loop.execute_with_reflexion(
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
        use_critic: bool = True,
        log_dir: str = "agent_outputs/reflexion_logs"
    ):
        """
        初期化
        
        Args:
            task_id: タスクID
            quality_threshold: 品質基準点（これ以上で合格）
            max_loops: 最大ループ回数
            use_critic: Criticエージェントを使用するか
            log_dir: ログ出力ディレクトリ
        """
        self.task_id = task_id
        self.quality_threshold = quality_threshold
        self.max_loops = max_loops
        self.use_critic = use_critic and CRITIC_AVAILABLE
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Critic初期化
        if self.use_critic:
            self.critic = CriticAgent()
            self.feedback_gen = FeedbackGenerator()
            print("✅ Critic統合モード")
        else:
            self.critic = None
            self.feedback_gen = None
            print("🤖 ダミーモード")
        
        # ループ履歴
        self.history: List[Dict] = []
    
    def execute_with_reflexion(
        self,
        executor_func: Callable,
        task_data: Dict,
        evaluator_func: Optional[Callable] = None
    ) -> Tuple[Dict, bool]:
        """
        Reflexionループ付きでタスクを実行
        
        Args:
            executor_func: タスク実行関数
            task_data: タスクデータ
            evaluator_func: 品質評価関数（Criticを使わない場合）
        
        Returns:
            (実行結果, 成功フラグ)
        """
        print(f"\n{'='*60}")
        print(f"🔄 Reflexionループ開始: {self.task_id}")
        print(f"   モード: {'Critic統合' if self.use_critic else 'ダミー'}")
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
            if self.use_critic and self.critic:
                # Criticで評価
                quality_score, critic_feedback = self.critic.evaluate(result)
            elif evaluator_func:
                # カスタム評価関数
                quality_score = evaluator_func(result)
                critic_feedback = "カスタム評価"
            else:
                # ダミー評価
                quality_score = self._dummy_evaluate(result, loop_num)
                critic_feedback = "ダミー評価"
            
            print(f"   品質スコア: {quality_score}点")
            
            # 履歴記録
            iteration = {
                'loop_num': loop_num,
                'quality_score': quality_score,
                'result': result,
                'feedback': feedback,
                'critic_feedback': critic_feedback,
                'timestamp': datetime.now().isoformat()
            }
            self.history.append(iteration)
            
            # 3. 品質判定
            if quality_score >= self.quality_threshold:
                print(f"\n✅ 品質基準達成: {quality_score} >= {self.quality_threshold}")
                self._save_log(success=True, final_score=quality_score)
                return result, True
            
            # 4. フィードバック生成
            if loop_num < self.max_loops:
                print("   🤔 改善提案生成中...")
                if self.use_critic and self.feedback_gen:
                    # 実行可能なフィードバック生成
                    feedback = self.feedback_gen.generate_actionable_feedback(
                        scores={'completeness': 15, 'accuracy': 18, 'detail': 12, 'structure': 10},
                        original_feedback=critic_feedback
                    )
                else:
                    feedback = self._generate_dummy_feedback(quality_score)
                
                print(f"   フィードバック: {feedback[:100]}...")
        
        # 最大ループ数に達した
        print(f"\n⚠️  最大ループ数に達しました（最終スコア: {quality_score}）")
        print(f"   人間にエスカレーション推奨")
        
        self._save_log(success=False, final_score=quality_score)
        
        return result, False
    
    def _dummy_evaluate(self, result: Dict, loop_num: int) -> int:
        """ダミー品質評価"""
        base_score = 60
        improvement = (loop_num - 1) * 10
        return min(base_score + improvement, 85)
    
    def _generate_dummy_feedback(self, quality_score: int) -> str:
        """ダミーフィードバック生成"""
        if quality_score < 70:
            return "データの完全性と具体性を改善してください"
        else:
            return "詳細度と検証可能性をさらに向上させてください"
    
    def _save_log(self, success: bool, final_score: int):
        """ログを保存"""
        log_file = self.log_dir / f"{self.task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        log_data = {
            'task_id': self.task_id,
            'success': success,
            'total_loops': len(self.history),
            'final_score': final_score,
            'threshold': self.quality_threshold,
            'used_critic': self.use_critic,
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
            'avg_score': sum(scores) / len(scores),
            'used_critic': self.use_critic
        }

# ========================================
# テスト
# ========================================
if __name__ == "__main__":
    print("="*60)
    print("🧪 Reflexionループエンジン（Critic統合版）テスト")
    print("="*60)
    
    def dummy_executor(task_data):
        return {
            'status': 'completed',
            'output': '実行結果のダミーデータ' * (10 if 'reflexion_feedback' in task_data else 1),
            'feedback_applied': 'reflexion_feedback' in task_data
        }
    
    loop = ReflexionLoop(task_id="test_critic_integration", use_critic=True)
    
    result, success = loop.execute_with_reflexion(
        executor_func=dummy_executor,
        task_data={'description': 'テストタスク'}
    )
    
    stats = loop.get_statistics()
    print(f"\n📊 統計情報:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    print(f"\n✅ テスト完了")
