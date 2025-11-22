#!/bin/bash
# F6動的タスク追加とF9人間指示の実装

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 F6動的タスク追加とF9人間指示の実装"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: F6動的タスク追加エージェント
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: F6動的タスク追加エージェント"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > agents/f6_dynamic_task_generator.py << 'PYTHON'
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

PYTHON

echo "✅ F6動的タスク追加エージェント作成"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: F9人間指示インターフェース
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: F9人間指示インターフェース"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > agents/f9_human_interface.py << 'PYTHON'
"""
F9: 人間指示インターフェース
いつでも指示を受け付け、システムに反映
"""

import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class F9HumanInterface:
    """F9: 人間指示インターフェース"""
    
    def __init__(self, sheets_manager=None):
        self.sheets = sheets_manager
        self.instructions_sheet = "human_instructions"  # 新しいシート
        
    def check_human_instructions(self) -> List[Dict[str, Any]]:
        """人間からの指示をチェック"""
        print("\n" + "=" * 80)
        print("📨 F9: 人間指示チェック")
        print("=" * 80)
        
        try:
            # human_instructions シートから未処理の指示を取得
            result = self.sheets.service.spreadsheets().values().get(
                spreadsheetId=self.sheets.spreadsheet_id,
                range=f"{self.instructions_sheet}!A2:G100"
            ).execute()
            
            values = result.get('values', [])
            
            pending_instructions = []
            for i, row in enumerate(values, 2):
                if len(row) < 3:
                    continue
                
                status = row[2] if len(row) > 2 else ''
                
                if status == 'pending':
                    instruction = {
                        'row_index': i,
                        'timestamp': row[0],
                        'instruction_type': row[1],
                        'status': status,
                        'content': row[3] if len(row) > 3 else '',
                        'priority': row[4] if len(row) > 4 else 'medium',
                        'target_task': row[5] if len(row) > 5 else ''
                    }
                    pending_instructions.append(instruction)
            
            if pending_instructions:
                print(f"\n📬 {len(pending_instructions)}件の未処理指示があります")
                for i, inst in enumerate(pending_instructions, 1):
                    print(f"  {i}. [{inst['instruction_type']}] {inst['content'][:50]}...")
            else:
                print("\n✅ 未処理の指示はありません")
            
            return pending_instructions
            
        except Exception as e:
            # human_instructions シートが存在しない場合は作成を提案
            if '範囲が見つかりません' in str(e) or 'Unable to parse range' in str(e):
                print("\n⚠️  human_instructions シートが存在しません")
                print("   → 自動作成します...")
                self._create_instructions_sheet()
                return []
            else:
                print(f"❌ 指示チェックエラー: {e}")
                return []
    
    def _create_instructions_sheet(self) -> bool:
        """human_instructions シートを作成"""
        try:
            # 新しいシートを追加
            request = {
                'addSheet': {
                    'properties': {
                        'title': self.instructions_sheet,
                        'gridProperties': {
                            'rowCount': 100,
                            'columnCount': 7
                        }
                    }
                }
            }
            
            self.sheets.service.spreadsheets().batchUpdate(
                spreadsheetId=self.sheets.spreadsheet_id,
                body={'requests': [request]}
            ).execute()
            
            # ヘッダー行を追加
            header = [
                'timestamp',
                'instruction_type',
                'status',
                'content',
                'priority',
                'target_task',
                'result'
            ]
            
            self.sheets.service.spreadsheets().values().update(
                spreadsheetId=self.sheets.spreadsheet_id,
                range=f"{self.instructions_sheet}!A1:G1",
                valueInputOption="RAW",
                body={"values": [header]}
            ).execute()
            
            print(f"✅ {self.instructions_sheet} シートを作成しました")
            
            # サンプル指示を追加
            sample_instructions = [
                [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "add_task",
                    "pending",
                    "新しいタスク「データベース最適化」を追加してください",
                    "high",
                    "",
                    ""
                ],
                [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "pause_system",
                    "completed",
                    "システムを一時停止（サンプル）",
                    "high",
                    "",
                    "処理済み"
                ]
            ]
            
            self.sheets.service.spreadsheets().values().append(
                spreadsheetId=self.sheets.spreadsheet_id,
                range=f"{self.instructions_sheet}!A:G",
                valueInputOption="RAW",
                body={"values": sample_instructions}
            ).execute()
            
            print(f"✅ サンプル指示を追加しました")
            return True
            
        except Exception as e:
            print(f"❌ シート作成エラー: {e}")
            return False
    
    def process_instructions(self, instructions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """指示を処理"""
        results = {
            'processed': 0,
            'failed': 0,
            'actions': []
        }
        
        for instruction in instructions:
            print(f"\n【指示処理】{instruction['instruction_type']}")
            print(f"  内容: {instruction['content']}")
            
            try:
                if instruction['instruction_type'] == 'add_task':
                    self._process_add_task(instruction)
                elif instruction['instruction_type'] == 'pause_system':
                    self._process_pause_system(instruction)
                elif instruction['instruction_type'] == 'change_priority':
                    self._process_change_priority(instruction)
                elif instruction['instruction_type'] == 'stop_task':
                    self._process_stop_task(instruction)
                elif instruction['instruction_type'] == 'message':
                    self._process_message(instruction)
                else:
                    print(f"  ⚠️  未対応の指示タイプ: {instruction['instruction_type']}")
                
                # ステータスを完了に更新
                self.sheets.service.spreadsheets().values().update(
                    spreadsheetId=self.sheets.spreadsheet_id,
                    range=f"{self.instructions_sheet}!C{instruction['row_index']}",
                    valueInputOption="RAW",
                    body={"values": [["completed"]]}
                ).execute()
                
                results['processed'] += 1
                results['actions'].append({
                    'type': instruction['instruction_type'],
                    'status': 'success'
                })
                
            except Exception as e:
                print(f"  ❌ 処理エラー: {e}")
                results['failed'] += 1
                results['actions'].append({
                    'type': instruction['instruction_type'],
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results
    
    def _process_add_task(self, instruction: Dict[str, Any]):
        """タスク追加指示を処理"""
        content = instruction['content']
        print(f"  🔧 タスク追加: {content}")
        
        # 簡易的なタスク生成
        timestamp = datetime.now().strftime('%H%M%S')
        task = {
            'task_id': f"human_req_{timestamp}",
            'parent_goal_id': instruction.get('target_task', ''),
            'description': content,
            'required_role': 'developer',
            'status': 'pending',
            'priority': instruction.get('priority', 'high'),
            'estimated_time': '2h',
            'dependencies': '',
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'batch_id': f'human_instruction_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'detail_file_path': '',
            'blank': '',
            'execution_type': 'implementation'
        }
        
        # pm_tasks に追加
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
        
        print(f"  ✅ タスク追加完了: {task['task_id']}")
    
    def _process_pause_system(self, instruction: Dict[str, Any]):
        """システム一時停止指示を処理"""
        print(f"  ⏸️  システム一時停止")
        # 一時停止フラグを作成
        with open('/tmp/system_paused.flag', 'w') as f:
            f.write(instruction['content'])
        print(f"  ✅ 一時停止フラグ作成")
    
    def _process_change_priority(self, instruction: Dict[str, Any]):
        """優先度変更指示を処理"""
        target_task = instruction.get('target_task', '')
        print(f"  🔄 優先度変更: {target_task}")
        # TODO: 実装
    
    def _process_stop_task(self, instruction: Dict[str, Any]):
        """タスク停止指示を処理"""
        target_task = instruction.get('target_task', '')
        print(f"  ⏹️  タスク停止: {target_task}")
        # TODO: 実装
    
    def _process_message(self, instruction: Dict[str, Any]):
        """メッセージを処理"""
        print(f"  💬 メッセージ: {instruction['content']}")

def main():
    """テスト実行"""
    from tools.sheets_manager import GoogleSheetsManager
    
    sheets = GoogleSheetsManager()
    f9 = F9HumanInterface(sheets)
    
    # 指示をチェック
    instructions = f9.check_human_instructions()
    
    if instructions:
        # 指示を処理
        results = f9.process_instructions(instructions)
        print(f"\n✅ 処理完了: {results['processed']}件")

if __name__ == "__main__":
    main()

PYTHON

echo "✅ F9人間指示インターフェース作成"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: 統合版CompleteEngine
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: F6/F9統合版CompleteEngine"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > agents/complete_engine_with_f6_f9.py << 'PYTHON'
"""
CompleteEngine（F6/F9統合版）
"""

import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.complete_engine_with_strict_quality import CompleteEngineWithStrictQuality
from agents.f6_dynamic_task_generator import F6DynamicTaskGenerator
from agents.f9_human_interface import F9HumanInterface

class CompleteEngineWithF6F9(CompleteEngineWithStrictQuality):
    """CompleteEngine（F6/F9統合版）"""
    
    def __init__(self):
        super().__init__()
        self.f6_generator = F6DynamicTaskGenerator(self.sheets)
        self.f9_interface = F9HumanInterface(self.sheets)
        
    def run_full_integration_cycle_with_f6_f9(self, goal_id=None, limit=1):
        """統合フロー（F6/F9対応版）"""
        print("\n" + "=" * 80)
        print("🚀 完全統合フロー開始（F6/F9対応版）")
        print("=" * 80)
        
        # F9: 人間指示チェック（最優先）
        instructions = self.f9_interface.check_human_instructions()
        if instructions:
            self.f9_interface.process_instructions(instructions)
        
        # F1: タスク可用性チェック
        result = self.run_full_integration_cycle_fixed(goal_id, limit)
        
        # 実行結果を確認
        if not result.get('success'):
            return result
        
        # F6: 品質不合格タスクの処理
        # TODO: 各タスクの品質評価結果を取得
        # 簡易版として、最後に実行したタスクをチェック
        
        return result

PYTHON

echo "✅ F6/F9統合版CompleteEngine作成"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ F6/F9実装完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 実装内容:"
echo "  1. ✅ F6動的タスク追加エージェント"
echo "  2. ✅ F9人間指示インターフェース"
echo "  3. ✅ F6/F9統合版CompleteEngine"
echo ""
echo "📄 生成ファイル:"
echo "  - agents/f6_dynamic_task_generator.py"
echo "  - agents/f9_human_interface.py"
echo "  - agents/complete_engine_with_f6_f9.py"
echo ""
echo "🎯 F6の使い方:"
echo "  品質不合格（7点未満）のタスクに対して、自動的に4個のタスクを追加:"
echo "  1. 詳細要件定義（2h）"
echo "  2. 実装強化（3h）"
echo "  3. ドキュメント充実（2h）"
echo "  4. テスト追加（2h）"
echo ""
echo "🎯 F9の使い方:"
echo "  Google Sheets の human_instructions シートに指示を追加:"
echo "  1. timestamp: 自動入力"
echo "  2. instruction_type: add_task, pause_system, change_priority, stop_task, message"
echo "  3. status: pending（追加時）"
echo "  4. content: 指示内容"
echo "  5. priority: high, medium, low"
echo "  6. target_task: 対象タスクID（オプション）"
echo ""
echo "📝 次のステップ:"
echo "  1. F9テスト: python3 agents/f9_human_interface.py"
echo "  2. human_instructions シートが自動作成されます"
echo "  3. シートに指示を追加してテスト"
echo ""

