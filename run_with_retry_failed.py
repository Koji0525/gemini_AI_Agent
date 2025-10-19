#!/usr/bin/env python3
"""
失敗タスク再実行版 - 重複ヘッダー問題解決 & 失敗タスク自動再実行
"""
import asyncio
import sys
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

os.environ['DISPLAY'] = ':1'

print("🔧 モジュールインポート中...")

try:
    from configuration.config_loader import get_spreadsheet_id, get_service_account_file
    from browser_control.browser_controller import BrowserController
    from tools.sheets_manager_final import GoogleSheetsManagerFinal
    from configuration.wp_config_loader_fixed import wp_config_loader
    print("✅ すべてのモジュールインポート成功")
except ImportError as e:
    print(f"❌ モジュールインポートエラー: {e}")
    sys.exit(1)

class RetryFailedExecutor:
    """失敗タスク再実行対応エグゼキューター"""
    
    def __init__(self, sheets_manager, browser_controller):
        self.sheets = sheets_manager
        self.browser = browser_controller
        
        # 設定確認
        if wp_config_loader.has_valid_config():
            print("🎯 WordPress連携: 有効")
        else:
            print("⚠️  WordPress連携: 設定不足")
    
    async def evaluate_quality(self, task: Dict, output: str) -> Dict:
        """出力品質を評価（10点満点 + 詳細な根拠）"""
        print("   📊 品質評価中...")
        
        try:
            evaluation_prompt = f"""以下のタスク出力の品質を1-10点で厳密に評価してください。

【評価対象タスク】
{task.get('description')}

【出力内容（一部）】
{output[:800]}

【評価基準（詳細）】
- 1-3点: 要件を満たせていない、重大な誤りがある、実用性がない
- 4-6点: 基本的な要件は満たしているが、不完全・不正確な部分がある、改善の余地が大きい
- 7-8点: 要件を満たし、実用的な内容、正確性が高い、若干の改善点がある
- 9-10点: 優れた成果物、追加価値がある、完成度が高い、実用的で正確

【評価形式】
以下の形式で厳密に回答してください:
総合評価: X/10
評価根拠: [具体的な理由を3点程度挙げて説明]
改善提案: [もしあれば]

必ず1-10の整数で評価し、具体的な根拠を述べてください。"""
            
            await self.browser.send_prompt(evaluation_prompt)
            await self.browser.wait_for_text_generation(max_wait=60)
            evaluation = await self.browser.extract_latest_text_response()
            
            # スコア抽出
            quality_score = 0
            quality_reason = ""
            
            if evaluation:
                # 複数のパターンでスコアを抽出
                patterns = [
                    r'総合評価[：:]\s*(\d+)/10',
                    r'評価[：:]\s*(\d+)/10', 
                    r'総合点[：:]\s*(\d+)',
                    r'(\d+)/10',
                    r'評価.*?(\d+)点'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, evaluation)
                    if match:
                        score = int(match.group(1))
                        if 1 <= score <= 10:
                            quality_score = score
                            break
                
                # 評価根拠を抽出
                reason_patterns = [
                    r'評価根拠[：:]\s*(.+?)(?=改善提案|$|\n\n)',
                    r'理由[：:]\s*(.+?)(?=改善|$|\n\n)',
                ]
                
                for pattern in reason_patterns:
                    match = re.search(pattern, evaluation, re.DOTALL)
                    if match:
                        quality_reason = match.group(1).strip()
                        break
            
            # スコアが異常な場合のフォールバック
            if quality_score <= 0 or quality_score > 10:
                quality_score = 6
                quality_reason = "自動評価で異常値のため保守的評価"
            
            result = {
                "score": quality_score,
                "evaluation": quality_reason,
            }
            
            print(f"   ✅ 品質評価完了: {quality_score}/10点")
            return result
            
        except Exception as e:
            print(f"   ⚠️  品質評価エラー: {e}")
            return {"score": 6, "evaluation": "評価プロセスでエラーが発生しました"}
    
    async def execute_with_gemini(self, prompt: str) -> tuple:
        """Geminiでタスクを実行"""
        try:
            await self.browser.send_prompt(prompt)
            await self.browser.wait_for_text_generation(max_wait=120)
            response = await self.browser.extract_latest_text_response()
            
            if response and len(response) > 100:
                print(f"      ✅ {len(response):,}文字のレスポンス生成")
                return True, response, ""
            else:
                return False, "", "レスポンス不足"
                
        except Exception as e:
            return False, "", str(e)
    
    async def run_specific_task(self, task_id: int, description: str) -> bool:
        """特定のタスクを実行（失敗タスク用）"""
        print(f"\n🎯 特定タスク実行: タスク{task_id}")
        print(f"📝 内容: {description}")
        
        try:
            # ステータスを進行中に更新
            await self.sheets.update_task_status(task_id, "in_progress", "pm_tasks")
            
            # プロンプト生成（より詳細な指示）
            prompt = self._create_detailed_prompt(description, task_id)
            
            # Geminiで実行
            success, output, error = await self.execute_with_gemini(prompt)
            
            if success:
                # 品質評価を実行
                task_data = {"task_id": task_id, "description": description}
                quality_result = await self.evaluate_quality(task_data, output)
                
                # ステータスを完了に更新
                await self.sheets.update_task_status(task_id, "completed", "pm_tasks")
                
                # ログ記録
                await self.log_execution(
                    task_data, output, True, quality_result
                )
                
                print(f"✅ タスク{task_id} 完了 - 品質: {quality_result['score']}/10")
                return True
            else:
                await self.sheets.update_task_status(task_id, "failed", "pm_tasks")
                await self.log_execution(
                    {"task_id": task_id, "description": description}, 
                    error, False, {"score": 0, "evaluation": "実行失敗"}
                )
                print(f"❌ タスク{task_id} 失敗: {error}")
                return False
                
        except Exception as e:
            print(f"❌ タスク{task_id} 実行エラー: {e}")
            return False
    
    def _create_detailed_prompt(self, description: str, task_id: int) -> str:
        """詳細なプロンプトを作成"""
        
        # 特定のタスクに対するカスタムプロンプト
        custom_prompts = {
            "提携パートナー管理機能": f"""以下の提携パートナー管理機能の具体的な仕様定義書を作成してください。

【要件】
{description}

【必要な構成要素】
1. WordPressユーザーロール設計
   - パートナー企業用のカスタムロール
   - 権限設定（閲覧、編集、削除など）

2. 案件登録/編集フォーム設計
   - カスタム投稿タイプ（CPT）設計
   - カスタムフィールド（ACF）設計
   - フォームバリデーション

3. ステータス管理システム
   - 案件ステータス（下書き、公開、完了など）
   - ステータス遷移フロー

4. アクセス制御システム
   - 自身が登録した案件のみ表示/編集
   - 権限に基づくコンテンツフィルタリング

【出力形式】
- 具体的なコード例を含む実装ガイド
- データベース設計図
- ユーザーフロー図
- 権限設定表

実際に実装可能な詳細な仕様書を作成してください。"""
        }
        
        # カスタムプロンプトがあれば使用、なければデフォルト
        for key, custom_prompt in custom_prompts.items():
            if key in description:
                return custom_prompt
        
        # デフォルトプロンプト
        return f"""以下のタスクを専門家として詳細に実行してください:

【タスク】
{description}

【要求事項】
- 具体的で実用的な成果物を作成
- 実際の実装に使用できるコード例を含める
- ステップバイステップの説明を追加
- 図表や例を使ってわかりやすく説明

専門家としての知識を活かして、完成度の高い成果物を作成してください。"""
    
    async def run_failed_tasks(self, max_retries: int = 3):
        """失敗したタスクを再実行"""
        print("\n🔍 失敗タスクを検索中...")
        
        failed_tasks = await self.sheets.get_failed_tasks()
        
        if not failed_tasks:
            print("✅ 失敗タスクはありません")
            return
        
        print(f"🔄 {len(failed_tasks)}件の失敗タスクを発見")
        
        for i, task in enumerate(failed_tasks, 1):
            task_id = task.get('task_id')
            description = task.get('description', '')
            
            print(f"\n{'='*60}")
            print(f"[{i}/{len(failed_tasks)}] 失敗タスク再実行: タスク{task_id}")
            print(f"{'='*60}")
            
            success = await self.run_specific_task(task_id, description)
            
            if success:
                print(f"✅ タスク{task_id} の再実行成功")
            else:
                print(f"❌ タスク{task_id} の再実行失敗")
            
            # 待機
            if i < len(failed_tasks):
                print("⏳ 15秒待機...")
                await asyncio.sleep(15)
    
    async def run_pending_tasks(self, max_tasks: int = 3):
        """pendingタスクを実行"""
        print(f"\n🔍 pendingタスクを実行 (最大{max_tasks}件)")
        
        # タスク読み込み
        tasks = await self.sheets.load_tasks_from_sheet("pm_tasks")
        pending_tasks = [t for t in tasks if t.get('status', '') in ['pending', '']]
        
        if not pending_tasks:
            print("✅ 実行可能なpendingタスクはありません")
            return
        
        if len(pending_tasks) > max_tasks:
            pending_tasks = pending_tasks[:max_tasks]
        
        print(f"📋 実行対象: {len(pending_tasks)}タスク")
        
        success_count = 0
        
        for i, task in enumerate(pending_tasks, 1):
            task_id = task.get('task_id')
            description = task.get('description', '')[:60]
            
            print(f"\n{'='*50}")
            print(f"[{i}/{len(pending_tasks)}] タスク{task_id}: {description}...")
            
            success = await self.run_specific_task(task_id, task.get('description', ''))
            if success:
                success_count += 1
            
            # 待機
            if i < len(pending_tasks):
                print("⏳ 12秒待機...")
                await asyncio.sleep(12)
        
        print(f"\n📊 pendingタスク実行結果: {success_count}/{len(pending_tasks)} 成功")
    
    async def log_execution(self, task: Dict, output: str, success: bool, quality_result: Dict):
        """実行結果をログに記録"""
        try:
            log_data = {
                'task_id': task.get('task_id'),
                'task_description': task.get('description', ''),
                'agent_role': 'retry_executor',
                'output_summary': output[:100] if output else '',
                'output_data': output[:500] if output else '',
                'status': 'completed' if success else 'failed',
                'quality_score': quality_result.get('score', 0),
                'quality_evaluation': quality_result.get('evaluation', '')
            }
            await self.sheets.log_task_execution(log_data)
            print(f"   📋 ログ記録完了 - 品質: {quality_result.get('score', 0)}/10")
        except Exception as e:
            print(f"   ⚠️  ログ記録エラー: {e}")

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='失敗タスク再実行システム')
    parser.add_argument('--retry-failed', action='store_true', help='失敗タスクを再実行')
    parser.add_argument('--run-pending', action='store_true', help='pendingタスクを実行')
    parser.add_argument('--max-tasks', type=int, default=3, help='最大タスク数')
    parser.add_argument('--task-id', type=int, help='特定のタスクIDを実行')
    
    args = parser.parse_args()
    
    print("🎯 失敗タスク再実行システム")
    print("=" * 60)
    print("📊 機能:")
    print("  ✅ 失敗タスク自動検出と再実行")
    print("  ✅ 重複ヘッダー問題解決")
    print("  ✅ 品質評価付き実行")
    print("  ✅ 特定タスクの個別実行")
    print("=" * 60)
    
    sheets = GoogleSheetsManagerFinal(
        spreadsheet_id=get_spreadsheet_id(),
        service_account_file=get_service_account_file()
    )
    
    async with BrowserController(download_folder="./downloads") as browser:
        executor = RetryFailedExecutor(sheets, browser)
        
        # Gemini初期化
        print("🔗 Geminiに接続...")
        if not await browser.navigate_to_gemini():
            print("❌ Gemini接続失敗")
            return
        print("✅ Gemini準備完了")
        
        # 実行モード
        if args.task_id:
            # 特定タスク実行
            tasks = await sheets.load_tasks_from_sheet("pm_tasks")
            target_task = next((t for t in tasks if t.get('task_id') == args.task_id), None)
            if target_task:
                await executor.run_specific_task(args.task_id, target_task.get('description', ''))
            else:
                print(f"❌ タスク{args.task_id} が見つかりません")
        
        elif args.retry_failed:
            # 失敗タスク再実行
            await executor.run_failed_tasks()
        
        elif args.run_pending:
            # pendingタスク実行
            await executor.run_pending_tasks(args.max_tasks)
        
        else:
            # デフォルト: 失敗タスクを検索して実行
            await executor.run_failed_tasks()
    
    print("\n�� 実行完了")

if __name__ == "__main__":
    asyncio.run(main())

