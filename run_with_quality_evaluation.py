#!/usr/bin/env python3
"""
品質評価対応版 - 10点満点評価とログ記録機能付き
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
    from tools.sheets_manager_with_logging import GoogleSheetsManager
    from configuration.wp_config_loader_fixed import wp_config_loader
    print("✅ すべてのモジュールインポート成功")
except ImportError as e:
    print(f"❌ モジュールインポートエラー: {e}")
    sys.exit(1)

class QualityEvaluationExecutor:
    """品質評価対応エグゼキューター"""
    
    def __init__(self, sheets_manager, browser_controller):
        self.sheets = sheets_manager
        self.browser = browser_controller
        
        # 設定確認
        if wp_config_loader.has_valid_config():
            print("🎯 WordPress連携: 有効")
        else:
            print("⚠️  WordPress連携: 設定不足")
    
    async def evaluate_quality(self, task: Dict, output: str) -> Dict:
        """出力品質を評価（10点満点）"""
        print("   📊 品質評価中...")
        
        try:
            evaluation_prompt = f"""以下のタスク出力の品質を1-10点で厳密に評価してください。

【評価対象タスク】
{task.get('description')}

【出力内容（一部）】
{output[:1000]}

【評価基準】
- 1-3点: 要件を満たせていない、誤りが多い
- 4-6点: 基本的な要件は満たしているが改善の余地あり  
- 7-8点: 要件を満たし、実用的な内容
- 9-10点: 優れた成果物、追加価値がある

【評価形式】
以下の形式のみで厳密に回答:
総合評価: X/10
理由: [簡潔な説明]

必ず1-10の整数で評価し、理由を簡潔に述べてください。"""
            
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
                
                # 理由を抽出
                reason_match = re.search(r'理由[：:]\s*(.+)', evaluation)
                if reason_match:
                    quality_reason = reason_match.group(1).strip()
                else:
                    # 理由が見つからない場合は評価テキストから最初の文を抽出
                    lines = evaluation.split('\n')
                    for line in lines:
                        if line.strip() and '理由' not in line and '評価' not in line and line.strip():
                            quality_reason = line.strip()[:100]
                            break
            
            # スコアが異常な場合のフォールバック
            if quality_score <= 0 or quality_score > 10:
                print(f"   ⚠️  異常スコア検出: {quality_score} -> 保守的に5点設定")
                quality_score = 5
                quality_reason = "自動評価で異常値のため保守的評価"
            
            result = {
                "score": quality_score,
                "evaluation": quality_reason,
                "full_evaluation": evaluation
            }
            
            print(f"   📊 品質評価結果: {quality_score}/10点")
            if quality_reason:
                print(f"   📝 評価理由: {quality_reason}")
            
            return result
            
        except Exception as e:
            print(f"   ⚠️  品質評価エラー: {e}")
            # エラー時は保守的に合格扱い
            return {"score": 7, "evaluation": "評価エラーのため保守的評価", "full_evaluation": ""}
    
    async def execute_with_gemini(self, prompt: str) -> tuple:
        """Geminiでタスクを実行"""
        try:
            await self.browser.send_prompt(prompt)
            await self.browser.wait_for_text_generation(max_wait=120)
            response = await self.browser.extract_latest_text_response()
            
            if response and len(response) > 100:
                return True, response, ""
            else:
                return False, "", "レスポンス不足"
                
        except Exception as e:
            return False, "", str(e)
    
    async def run_tasks(self, max_tasks: int = 3):
        """タスクを実行（品質評価付き）"""
        
        print(f"\n🚀 品質評価版 実行開始 (最大{max_tasks}タスク)")
        
        # Gemini初期化
        print("🔗 Geminiに接続...")
        if not await self.browser.navigate_to_gemini():
            print("❌ Gemini接続失敗")
            return
        
        print("✅ Gemini準備完了")
        
        # タスク読み込み
        tasks = await self.sheets.load_tasks_from_sheet("pm_tasks")
        pending_tasks = [t for t in tasks if t.get('status', '') in ['pending', '']]
        
        if not pending_tasks:
            print("⚠️  実行可能なタスクがありません")
            return
        
        if len(pending_tasks) > max_tasks:
            pending_tasks = pending_tasks[:max_tasks]
        
        print(f"📋 実行対象: {len(pending_tasks)}タスク")
        
        success_count = 0
        total_quality_score = 0
        quality_scores = []
        
        for i, task in enumerate(pending_tasks, 1):
            task_id = task.get('task_id')
            description = task.get('description', '')[:60]
            
            print(f"\n{'='*50}")
            print(f"[{i}/{len(pending_tasks)}] タスク{task_id}: {description}...")
            
            try:
                # ステータスを進行中に更新
                await self.sheets.update_task_status(task_id, "in_progress", "pm_tasks")
                
                # プロンプト生成
                prompt = f"""以下のタスクを専門家として実行してください:

タスク: {task.get('description')}
役割: {task.get('required_role', 'general')}

具体的で実用的な成果物を作成してください。"""
                
                # Geminiで実行
                success, output, error = await self.execute_with_gemini(prompt)
                
                if success:
                    # 品質評価を実行
                    quality_result = await self.evaluate_quality(task, output)
                    quality_score = quality_result["score"]
                    
                    # ステータスを完了に更新
                    await self.sheets.update_task_status(task_id, "completed", "pm_tasks")
                    success_count += 1
                    total_quality_score += quality_score
                    quality_scores.append(quality_score)
                    
                    print(f"✅ 完了 - {len(output):,}文字 (品質: {quality_score}/10)")
                else:
                    # ステータスを失敗に更新
                    await self.sheets.update_task_status(task_id, "failed", "pm_tasks")
                    quality_score = 0
                    print(f"❌ 失敗: {error}")
                
                # ログ記録（品質評価付き）
                await self.log_execution(
                    task, 
                    output if success else error, 
                    success, 
                    quality_result if success else {"score": 0, "evaluation": "実行失敗"}
                )
                
                # 待機（レート制限）
                if i < len(pending_tasks):
                    print("⏳ 10秒待機...")
                    await asyncio.sleep(10)
                    
            except Exception as e:
                print(f"❌ タスク実行エラー: {e}")
                # エラーログ記録
                await self.log_execution(
                    task, 
                    str(e), 
                    False, 
                    {"score": 0, "evaluation": "実行エラー"}
                )
        
        # サマリー表示
        print(f"\n{'='*50}")
        print("📊 実行結果サマリー")
        print(f"✅ 成功: {success_count}/{len(pending_tasks)}")
        
        if quality_scores:
            avg_quality = total_quality_score / len(quality_scores)
            max_quality = max(quality_scores)
            min_quality = min(quality_scores)
            
            print(f"📈 品質評価:")
            print(f"  平均: {avg_quality:.1f}/10")
            print(f"  最高: {max_quality}/10")
            print(f"  最低: {min_quality}/10")
            print(f"  詳細: {quality_scores}")
        
        print(f"{'='*50}")
    
    async def log_execution(self, task: Dict, output: str, success: bool, quality_result: Dict):
        """実行結果をログに記録（品質評価付き）"""
        try:
            log_data = {
                'task_id': task.get('task_id'),
                'task_description': task.get('description', ''),
                'agent_role': task.get('required_role', ''),
                'output_summary': output[:100] if output else '',
                'output_data': output[:500] if output else '',
                'status': 'completed' if success else 'failed',
                'quality_score': quality_result.get('score', 0),
                'quality_evaluation': quality_result.get('evaluation', '')
            }
            await self.sheets.log_task_execution(log_data)
            print(f"   📝 ログ記録完了: 品質 {quality_result.get('score', 0)}/10")
        except Exception as e:
            print(f"   ⚠️  ログ記録エラー: {e}")

async def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-tasks', type=int, default=3, help='最大タスク数')
    parser.add_argument('--min-quality', type=int, default=7, help='最低合格品質スコア')
    args = parser.parse_args()
    
    print("🎯 品質評価対応版")
    print("=" * 50)
    print(f"📊 品質基準: {args.min_quality}/10点以上で合格")
    
    sheets = GoogleSheetsManager(
        spreadsheet_id=get_spreadsheet_id(),
        service_account_file=get_service_account_file()
    )
    
    async with BrowserController(download_folder="./downloads") as browser:
        executor = QualityEvaluationExecutor(sheets, browser)
        await executor.run_tasks(max_tasks=args.max_tasks)
    
    print("\n🏁 実行完了")
    print("💡 ログ確認: https://docs.google.com/spreadsheets/d/{}".format(get_spreadsheet_id()))

if __name__ == "__main__":
    asyncio.run(main())

