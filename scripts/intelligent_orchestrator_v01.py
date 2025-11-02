"""
インテリジェント・オーケストレーター v1.0

v07の教訓を統合:
- ErrorClassifier: エラーの自動分類
- DecisionSupportSystem: 最適な修正戦略の選択
- KnowledgeBaseManager: 過去の成功パターン活用
- ContextLogger: 判断プロセスの記録
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json

sys.path.insert(0, str(Path.cwd()))

from tools.sheets_manager import GoogleSheetsManager
from core_agents.pm_agent import PMAgent
from task_executor.task_coordinator import TaskCoordinator


class ErrorClassifier:
    """エラーを9種類に自動分類"""
    
    ERROR_PATTERNS = {
        'network': ['connection', 'timeout', 'unreachable', 'dns'],
        'auth': ['authentication', 'permission', 'unauthorized', '401', '403'],
        'selector': ['element not found', 'selector', 'xpath'],
        'timeout': ['timeout', 'timed out', 'deadline exceeded'],
        'import': ['import error', 'module not found', 'no module named'],
        'argument': ['argument', 'parameter', 'missing', 'takes'],
        'api': ['api', 'rate limit', '429', '500', '502', '503'],
        'validation': ['validation', 'invalid', 'format error'],
        'resource': ['memory', 'disk', 'cpu', 'resource']
    }
    
    @classmethod
    def classify(cls, error_message: str) -> str:
        """エラーメッセージを分類"""
        error_lower = error_message.lower()
        
        for category, patterns in cls.ERROR_PATTERNS.items():
            for pattern in patterns:
                if pattern in error_lower:
                    return category
        
        return 'unknown'


class DecisionSupportSystem:
    """ナレッジベースから最適な戦略を選択"""
    
    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets_manager = sheets_manager
    
    def get_best_solution(self, error_type: str, error_message: str) -> Optional[Dict]:
        """最適な解決策を取得"""
        # ナレッジベースから検索
        kb_data = self.sheets_manager.read_range('knowledge_base!A2:F100')
        
        candidates = []
        for row in kb_data:
            if len(row) >= 4:
                kb_error_type = row[0]
                solution = row[1]
                confidence = float(row[3]) if row[3] else 0.0
                
                if kb_error_type == error_type:
                    candidates.append({
                        'solution': solution,
                        'confidence': confidence,
                        'details': row[2] if len(row) > 2 else ''
                    })
        
        # 信頼度順にソート
        candidates.sort(key=lambda x: x['confidence'], reverse=True)
        
        return candidates[0] if candidates else None


class ContextLogger:
    """判断プロセスを記録"""
    
    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets_manager = sheets_manager
        self.context_history = []
    
    def log_decision(self, decision_type: str, context: Dict):
        """判断をログに記録"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'decision_type': decision_type,
            'context': context
        }
        self.context_history.append(log_entry)
        
        # decision_logシートに記録
        log_data = [[
            datetime.now().isoformat(),
            decision_type,
            json.dumps(context, ensure_ascii=False),
            context.get('confidence', 0.0)
        ]]
        self.sheets_manager.append_rows('decision_log', log_data)


class IntelligentOrchestrator:
    """インテリジェントな自動実行オーケストレーター"""
    
    def __init__(self):
        self.sheets_manager = GoogleSheetsManager()
        self.pm_agent = PMAgent(self.sheets_manager)
        self.task_coordinator = TaskCoordinator(self.sheets_manager)
        
        # v07の教訓を統合
        self.error_classifier = ErrorClassifier()
        self.decision_support = DecisionSupportSystem(self.sheets_manager)
        self.context_logger = ContextLogger(self.sheets_manager)
    
    async def execute(self):
        """メイン実行ロジック"""
        print("=" * 60)
        print("🚀 インテリジェント・オーケストレーター v1.0 起動")
        print("=" * 60)
        
        try:
            # 1. アクティブな目標を取得
            goals = await self.get_active_goals()
            
            if not goals:
                print("ℹ️ アクティブな目標がありません")
                return
            
            # 2. 各目標に対してタスク生成
            for goal in goals:
                await self.process_goal(goal)
            
            # 3. タスク実行（自動修復機能付き）
            await self.execute_tasks_with_auto_repair()
            
            # 4. 実行結果の分析と学習
            await self.analyze_and_learn()
            
        except Exception as e:
            print(f"❌ 実行エラー: {e}")
            
            # エラーを分類
            error_type = self.error_classifier.classify(str(e))
            print(f"📊 エラー分類: {error_type}")
            
            # 最適な解決策を取得
            solution = self.decision_support.get_best_solution(error_type, str(e))
            
            if solution:
                print(f"💡 推奨される解決策（信頼度{solution['confidence']:.1%}）:")
                print(f"   {solution['solution']}")
                
                # 判断プロセスを記録
                self.context_logger.log_decision('error_recovery', {
                    'error_type': error_type,
                    'error_message': str(e),
                    'solution': solution['solution'],
                    'confidence': solution['confidence']
                })
    
    async def get_active_goals(self) -> List[Dict]:
        """アクティブな目標を取得"""
        goals_data = self.sheets_manager.read_range('pm_goals!A2:F100')
        
        active_goals = []
        for row in goals_data:
            if len(row) >= 4 and row[3] == 'active':
                active_goals.append({
                    'goal_id': row[0],
                    'description': row[1],
                    'priority': row[2],
                    'status': row[3]
                })
        
        return active_goals
    
    async def process_goal(self, goal: Dict):
        """目標を処理"""
        print(f"\n📝 目標処理: {goal['description']}")
        
        # PM Agentで目標を分解
        tasks = await self.pm_agent.decompose_goal(
            goal['goal_id'],
            goal['description'],
            goal['priority']
        )
        
        print(f"✅ {len(tasks)}個のタスクに分解完了")
        
        # 判断プロセスを記録
        self.context_logger.log_decision('goal_decomposition', {
            'goal_id': goal['goal_id'],
            'task_count': len(tasks),
            'priority': goal['priority'],
            'confidence': 0.9
        })
    
    async def execute_tasks_with_auto_repair(self):
        """自動修復機能付きでタスク実行"""
        print("\n🎯 タスク実行開始（自動修復機能有効）")
        
        # pendingタスクを取得
        tasks = self.sheets_manager.read_range('pm_tasks!A2:K100')
        pending_tasks = [t for t in tasks if len(t) > 3 and t[3] == 'pending']
        
        for task in pending_tasks:
            task_id = task[0]
            task_desc = task[1]
            
            print(f"\n📌 タスク実行: {task_desc}")
            
            try:
                # Task Coordinator経由で実行
                result = await self.task_coordinator.execute_task(task_id)
                
                if result['status'] == 'success':
                    print(f"✅ タスク完了")
                else:
                    # エラーが発生した場合、自動修復を試行
                    await self.auto_repair_task(task_id, result['error'])
                    
            except Exception as e:
                await self.auto_repair_task(task_id, str(e))
    
    async def auto_repair_task(self, task_id: str, error_message: str):
        """タスクの自動修復"""
        print(f"🔧 自動修復開始: {task_id}")
        
        # エラー分類
        error_type = self.error_classifier.classify(error_message)
        print(f"📊 エラータイプ: {error_type}")
        
        # 最適な解決策を取得
        solution = self.decision_support.get_best_solution(error_type, error_message)
        
        if solution and solution['confidence'] >= 0.7:
            print(f"💡 自動修復実行（信頼度{solution['confidence']:.1%}）")
            
            # 判断プロセスを記録
            self.context_logger.log_decision('auto_repair', {
                'task_id': task_id,
                'error_type': error_type,
                'solution': solution['solution'],
                'confidence': solution['confidence']
            })
            
            # 修復を試行（ここでは再実行）
            try:
                result = await self.task_coordinator.execute_task(task_id)
                
                if result['status'] == 'success':
                    print("✅ 自動修復成功")
                    
                    # 成功をナレッジベースに記録
                    kb_data = [[
                        error_type,
                        solution['solution'],
                        f"タスク{task_id}で成功",
                        min(solution['confidence'] + 0.1, 1.0),  # 信頼度向上
                        'auto_repair',
                        datetime.now().isoformat()
                    ]]
                    self.sheets_manager.append_rows('knowledge_base', kb_data)
                else:
                    print("⚠️ 自動修復失敗")
                    
            except Exception as e:
                print(f"❌ 自動修復エラー: {e}")
        else:
            print("⚠️ 自動修復不可（信頼できる解決策なし）")
    
    async def analyze_and_learn(self):
        """実行結果を分析して学習"""
        print("\n📊 実行結果分析")
        
        # タスク実行ログを分析
        logs = self.sheets_manager.read_range('task_execution_log!A2:H100')
        
        if not logs:
            return
        
        # 成功パターンの抽出
        successful_tasks = [log for log in logs if len(log) > 4 and log[4] == 'success']
        
        # 品質スコアの分析
        quality_scores = []
        for log in logs:
            if len(log) > 7:
                try:
                    score = float(log[7])
                    quality_scores.append(score)
                except:
                    pass
        
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            print(f"📈 平均品質スコア: {avg_quality:.1f}/10")
            
            # 高品質なタスクのパターンを学習
            high_quality_tasks = [
                log for log in logs 
                if len(log) > 7 and float(log[7]) >= 8.0
            ]
            
            print(f"✨ 高品質タスク: {len(high_quality_tasks)}件")


async def main():
    """メイン関数"""
    orchestrator = IntelligentOrchestrator()
    await orchestrator.execute()


if __name__ == "__main__":
    asyncio.run(main())
