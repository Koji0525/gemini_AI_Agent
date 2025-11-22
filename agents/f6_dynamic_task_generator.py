"""
F6: 動的タスク追加エージェント
品質不合格時に自動的にタスクを分解・追加
"""

import sys
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class F6DynamicTaskGenerator:
    """F6: 動的タスク追加エージェント"""
    
    def __init__(self, sheets_manager=None):
        self.sheets = sheets_manager
        
    def generate_improvement_tasks(
        self, 
        failed_task: Dict[str, Any],
        quality_evaluation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """品質不合格タスクに対して改善タスクを生成"""
        print("\n" + "=" * 80)
        print("🔧 F6: 動的タスク追加")
        print("=" * 80)
        
        print(f"\n【不合格タスク】")
        print(f"  タスクID: {failed_task['task_id']}")
        print(f"  品質スコア: {quality_evaluation.get('score', 0):.1f}/10点")
        print(f"  実用性: {quality_evaluation.get('usability', '不明')}")
        
        # 問題分析
        issues = self._analyze_issues(quality_evaluation)
        
        print(f"\n【問題分析】")
        for issue in issues:
            print(f"  - {issue}")
        
        # 改善タスクを生成
        improvement_tasks = []
        
        # タスク1: 詳細要件定義
        if quality_evaluation['evaluation']['total_lines'] < 300:
            task1 = self._generate_detailed_requirements_task(failed_task)
            improvement_tasks.append(task1)
        
        # タスク2: 実装強化
        if quality_evaluation['evaluation']['code_files'] < 2:
            task2 = self._generate_implementation_task(failed_task)
            improvement_tasks.append(task2)
        
        # タスク3: ドキュメント充実
        if quality_evaluation['evaluation']['doc_files'] < 2:
            task3 = self._generate_documentation_task(failed_task)
            improvement_tasks.append(task3)
        
        # タスク4: テスト追加
        if quality_evaluation['evaluation']['file_count'] < 4:
            task4 = self._generate_testing_task(failed_task)
            improvement_tasks.append(task4)
        
        print(f"\n【生成タスク】{len(improvement_tasks)}個")
        for i, task in enumerate(improvement_tasks, 1):
            print(f"  {i}. {task['task_id']}")
        
        return improvement_tasks
    
    def _analyze_issues(self, quality_evaluation: Dict[str, Any]) -> List[str]:
        """問題を分析"""
        issues = []
        eval_data = quality_evaluation['evaluation']
        
        if eval_data['total_lines'] < 300:
            issues.append(f"行数不足（{eval_data['total_lines']}行 < 300行）")
        
        if eval_data['total_bytes'] < 5000:
            issues.append(f"サイズ不足（{eval_data['total_bytes']}バイト < 5000バイト）")
        
        if eval_data['code_files'] < 1:
            issues.append("コード実装なし")
        elif eval_data['code_files'] < 2:
            issues.append("コードファイル不足")
        
        if eval_data['doc_files'] < 2:
            issues.append("ドキュメント不足")
        
        if not eval_data['has_readme']:
            issues.append("README.md なし")
        
        if eval_data['file_count'] < 3:
            issues.append("ファイル数不足")
        
        return issues
    
    def _generate_detailed_requirements_task(self, failed_task: Dict[str, Any]) -> Dict[str, Any]:
        """詳細要件定義タスクを生成"""
        timestamp = datetime.now().strftime('%H%M%S')
        base_task_id = failed_task['task_id'].split('_')[0]
        
        return {
            'task_id': f"{base_task_id}_詳細要件定義_{timestamp}_F6_01",
            'parent_goal_id': failed_task.get('parent_goal_id', ''),
            'description': f"""
【F6動的追加】{failed_task['task_id']}の詳細要件定義

【目的】
元タスク「{failed_task.get('description', '')[:50]}...」の品質不足を解消するため、
詳細な要件定義を作成する。

【作業内容】
1. 元タスクの目的を明確化
2. 具体的な機能要件を定義（10項目以上）
3. 非機能要件を定義（性能、セキュリティ、保守性）
4. 技術スタック選定
5. 実装スコープの明確化
6. 成功基準の具体化（テスト可能な形式）
7. 制約条件と前提条件の明記
8. 詳細な実装計画の作成

【成功基準】
・要件定義書が300行以上
・機能要件が10項目以上定義されている
・成功基準が具体的かつテスト可能
・次のフェーズで実装可能なレベルの詳細度

【期待する成果物】
・agent_outputs/design/{base_task_id}_詳細要件定義/requirements.md（200行以上）
・agent_outputs/design/{base_task_id}_詳細要件定義/architecture.md（100行以上）
・agent_outputs/design/{base_task_id}_詳細要件定義/implementation_plan.md（100行以上）

【コンテキスト】
元タスクの成果物が不十分だったため、まず詳細な要件を定義してから再実装する戦略を採用。
""",
            'required_role': 'developer',
            'status': 'pending',
            'priority': 'high',
            'estimated_time': '2h',
            'dependencies': '',
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'batch_id': f'f6_dynamic_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'detail_file_path': '',
            'blank': '',
            'execution_type': 'design'
        }
    
    def _generate_implementation_task(self, failed_task: Dict[str, Any]) -> Dict[str, Any]:
        """実装強化タスクを生成"""
        timestamp = datetime.now().strftime('%H%M%S')
        base_task_id = failed_task['task_id'].split('_')[0]
        
        return {
            'task_id': f"{base_task_id}_実装強化_{timestamp}_F6_02",
            'parent_goal_id': failed_task.get('parent_goal_id', ''),
            'description': f"""
【F6動的追加】{failed_task['task_id']}の実装強化

【目的】
元タスクの成果物（54行程度）を、実用化レベル（300行以上）に強化する。

【作業内容】
1. 詳細要件定義に基づく実装
2. メインモジュールの実装（150行以上）
3. サブモジュールの実装（2-3ファイル、各50行以上）
4. ユーティリティ関数の実装
5. エラーハンドリングの実装
6. ロギング機能の追加
7. 設定ファイルの作成
8. 実装ドキュメントの作成

【成功基準】
・コードファイルが3個以上
・総行数が300行以上
・各モジュールが適切に分離されている
・エラーハンドリングが実装されている
・実装ドキュメントが存在する

【期待する成果物】
・agent_outputs/implementation/{base_task_id}_実装強化/main.py（150行以上）
・agent_outputs/implementation/{base_task_id}_実装強化/utils.py（50行以上）
・agent_outputs/implementation/{base_task_id}_実装強化/config.py（30行以上）
・agent_outputs/implementation/{base_task_id}_実装強化/IMPLEMENTATION.md（100行以上）

【コンテキスト】
詳細要件定義に基づき、実用化レベルの実装を行う。
既存の成果物は参考程度にとどめ、全面的に再実装する。
""",
            'required_role': 'developer',
            'status': 'pending',
            'priority': 'high',
            'estimated_time': '3h',
            'dependencies': f"{base_task_id}_詳細要件定義_{timestamp}_F6_01",
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'batch_id': f'f6_dynamic_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'detail_file_path': '',
            'blank': '',
            'execution_type': 'implementation'
        }
    
    def _generate_documentation_task(self, failed_task: Dict[str, Any]) -> Dict[str, Any]:
        """ドキュメント充実タスクを生成"""
        timestamp = datetime.now().strftime('%H%M%S')
        base_task_id = failed_task['task_id'].split('_')[0]
        
        return {
            'task_id': f"{base_task_id}_ドキュメント充実_{timestamp}_F6_03",
            'parent_goal_id': failed_task.get('parent_goal_id', ''),
            'description': f"""
【F6動的追加】{failed_task['task_id']}のドキュメント充実

【目的】
実装された機能について、包括的なドキュメントを作成し、実用化レベルに引き上げる。

【作業内容】
1. README.md の充実（インストール、使用方法、サンプル）
2. API仕様書の作成（全関数・クラスの詳細）
3. アーキテクチャドキュメントの作成
4. トラブルシューティングガイドの作成
5. 変更履歴の記録
6. ライセンス情報の追加

【成功基準】
・README.md が100行以上
・API仕様書が完備されている
・サンプルコードが含まれている
・トラブルシューティングガイドがある
・ドキュメント総行数が200行以上

【期待する成果物】
・agent_outputs/documentation/{base_task_id}_ドキュメント/README.md（100行以上）
・agent_outputs/documentation/{base_task_id}_ドキュメント/API.md（80行以上）
・agent_outputs/documentation/{base_task_id}_ドキュメント/ARCHITECTURE.md（50行以上）
・agent_outputs/documentation/{base_task_id}_ドキュメント/TROUBLESHOOTING.md（30行以上）

【コンテキスト】
実装強化タスクで作成された機能について、ユーザーが実際に使用できるレベルのドキュメントを作成。
""",
            'required_role': 'developer',
            'status': 'pending',
            'priority': 'medium',
            'estimated_time': '2h',
            'dependencies': f"{base_task_id}_実装強化_{timestamp}_F6_02",
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'batch_id': f'f6_dynamic_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'detail_file_path': '',
            'blank': '',
            'execution_type': 'documentation'
        }
    
    def _generate_testing_task(self, failed_task: Dict[str, Any]) -> Dict[str, Any]:
        """テスト追加タスクを生成"""
        timestamp = datetime.now().strftime('%H%M%S')
        base_task_id = failed_task['task_id'].split('_')[0]
        
        return {
            'task_id': f"{base_task_id}_テスト追加_{timestamp}_F6_04",
            'parent_goal_id': failed_task.get('parent_goal_id', ''),
            'description': f"""
【F6動的追加】{failed_task['task_id']}のテスト追加

【目的】
実装された機能について、包括的なテストを作成し、品質を保証する。

【作業内容】
1. ユニットテストの作成（カバレッジ80%以上）
2. 統合テストの作成
3. エンドツーエンドテストの作成
4. テストドキュメントの作成
5. CI/CD設定の作成
6. テスト実行スクリプトの作成

【成功基準】
・テストファイルが3個以上
・テストケースが20個以上
・テストドキュメントが存在する
・全テストが合格する
・テスト総行数が150行以上

【期待する成果物】
・agent_outputs/testing/{base_task_id}_テスト/test_main.py（80行以上）
・agent_outputs/testing/{base_task_id}_テスト/test_integration.py（50行以上）
・agent_outputs/testing/{base_task_id}_テスト/test_e2e.py（30行以上）
・agent_outputs/testing/{base_task_id}_テスト/TEST_PLAN.md（50行以上）

【コンテキスト】
実装強化タスクで作成された機能について、包括的なテストを実施し、品質を保証する。
""",
            'required_role': 'tester',
            'status': 'pending',
            'priority': 'medium',
            'estimated_time': '2h',
            'dependencies': f"{base_task_id}_実装強化_{timestamp}_F6_02",
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'batch_id': f'f6_dynamic_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'detail_file_path': '',
            'blank': '',
            'execution_type': 'testing'
        }
    
    def add_tasks_to_sheet(self, tasks: List[Dict[str, Any]]) -> bool:
        """タスクをGoogle Sheetsに追加"""
        try:
            for task in tasks:
                row_data = [
                    task['task_id'],
                    task['parent_goal_id'],
                    task['description'],
                    task['required_role'],
                    task['status'],
                    task['priority'],
                    task['estimated_time'],
                    task['dependencies'],
                    task['created_at'],
                    task['batch_id'],
                    task['detail_file_path'],
                    task['blank'],
                    task['execution_type']
                ]
                
                self.sheets.service.spreadsheets().values().append(
                    spreadsheetId=self.sheets.spreadsheet_id,
                    range="pm_tasks!A:M",
                    valueInputOption="RAW",
                    body={"values": [row_data]}
                ).execute()
                
                print(f"  ✅ タスク追加: {task['task_id']}")
            
            print(f"\n✅ F6: {len(tasks)}個のタスクを動的追加しました")
            return True
            
        except Exception as e:
            print(f"❌ F6: タスク追加エラー: {e}")
            return False

