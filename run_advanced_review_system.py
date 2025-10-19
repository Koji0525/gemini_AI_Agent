#!/usr/bin/env python3
"""
高度なレビューシステム - 複数専門エージェント連携版
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

os.environ['DISPLAY'] = ':1'

print("🔧 高度なレビューシステム モジュールインポート中...")

try:
    from configuration.config_loader import get_spreadsheet_id, get_service_account_file
    from browser_control.browser_controller import BrowserController
    from tools.sheets_manager_final import GoogleSheetsManagerFinal
    from review_agents.review_orchestrator import ReviewOrchestrator
    print("✅ すべてのモジュールインポート成功")
except ImportError as e:
    print(f"❌ モジュールインポートエラー: {e}")
    sys.exit(1)

class AdvancedReviewSystem:
    """高度なレビューシステム"""
    
    def __init__(self, sheets_manager, browser_controller):
        self.sheets = sheets_manager
        self.browser = browser_controller
        self.review_orchestrator = ReviewOrchestrator(browser_controller)
    
    async def execute_task_with_advanced_review(self, task_id: int, task_description: str) -> Dict:
        """タスクを実行し高度なレビューを行う"""
        print(f"\n🎯 高度なレビュー付きタスク実行: タスク{task_id}")
        print(f"📝 内容: {task_description}")
        
        try:
            # ステータス更新
            await self.sheets.update_task_status(task_id, "in_progress", "pm_tasks")
            
            # 1. Geminiでタスク実行
            print("🤖 Geminiでタスク実行中...")
            prompt = self._create_comprehensive_prompt(task_description)
            success, output, error = await self._execute_with_gemini(prompt)
            
            if not success:
                await self._handle_execution_failure(task_id, task_description, error)
                return {"success": False, "error": error}
            
            print(f"✅ タスク実行完了 - {len(output):,}文字")
            
            # 2. 高度なレビュー実行
            print("🔍 複数専門エージェントでレビュー実行中...")
            review_result = await self.review_orchestrator.execute_reviews(task_description, output)
            
            if not review_result.get('success'):
                print("❌ レビュー実行に失敗")
                review_result = self._create_fallback_review()
            
            final_score = review_result['final_score']
            overall_rating = review_result['overall_rating']
            
            # 3. ステータス更新
            final_status = "completed" if final_score >= 6.0 else "needs_revision"
            await self.sheets.update_task_status(task_id, final_status, "pm_tasks")
            
            # 4. 詳細な評価テキスト生成
            quality_evaluation = await self.review_orchestrator.get_detailed_quality_evaluation(review_result)
            
            # 5. 出力を生成
            final_output = self._generate_final_output(task_description, output, review_result, quality_evaluation)
            
            # 6. ログ記録
            await self._log_advanced_execution(
                task_id, task_description, final_output, final_status, 
                final_score, quality_evaluation, review_result
            )
            
            print(f"✅ 高度なレビュー完了")
            print(f"📊 総合スコア: {final_score}/10 ({overall_rating})")
            print(f"🎯 ステータス: {final_status}")
            
            return {
                "success": True,
                "final_score": final_score,
                "overall_rating": overall_rating,
                "status": final_status,
                "output": final_output,
                "review_result": review_result,
                "quality_evaluation": quality_evaluation
            }
            
        except Exception as e:
            print(f"❌ 高度なレビュー実行エラー: {e}")
            await self.sheets.update_task_status(task_id, "failed", "pm_tasks")
            return {"success": False, "error": str(e)}
    
    def _create_comprehensive_prompt(self, task_description: str) -> str:
        """包括的なプロンプトを作成"""
        return f"""以下のタスクを専門家として詳細に実行してください:

【タスク】
{task_description}

【要求事項】
- 具体的で実用的な成果物を作成
- 実際の実装に使用できるコード例や具体的な手順を含める
- 技術的に正確で最新の情報を使用
- 読みやすく整理された構成で出力
- 必要に応じて図表や例を追加

専門家としての知識を最大限に活かし、高品質な成果物を作成してください。"""
    
    async def _execute_with_gemini(self, prompt: str) -> tuple:
        """Geminiで実行"""
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
    
    async def _handle_execution_failure(self, task_id: int, description: str, error: str):
        """実行失敗時の処理"""
        await self.sheets.update_task_status(task_id, "failed", "pm_tasks")
        await self._log_advanced_execution(
            task_id, description, error, "failed", 0, 
            "実行失敗のためレビュー不可", {}
        )
    
    def _create_fallback_review(self) -> Dict:
        """フォールバックレビューを作成"""
        return {
            "success": True,
            "final_score": 5.0,
            "overall_rating": "評価エラー",
            "reviewers_used": ["fallback"],
            "detailed_reviews": [{
                "reviewer_type": "fallback",
                "score": 5,
                "status": "completed",
                "improvements_needed": ["レビュープロセスに問題が発生しました"]
            }],
            "summary": "レビューシステムに問題が発生したため保守的評価"
        }
    
    def _generate_final_output(self, task_description: str, output: str, 
                             review_result: Dict, quality_evaluation: str) -> str:
        """最終出力を生成"""
        final_output = f"""# タスク実行レポート - 高度なレビュー付き

## タスク概要
- **タスク**: {task_description}
- **実行日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **総合評価**: {review_result['final_score']}/10 ({review_result['overall_rating']})
- **使用レビューエージェント**: {', '.join(review_result['reviewers_used'])}

## 品質評価サマリー
{quality_evaluation}

## 生成された成果物
{output}

---
*このレポートは高度なレビューシステムによって自動生成されました*
"""
        return final_output
    
    async def _log_advanced_execution(self, task_id: int, description: str, output: str, 
                                    status: str, final_score: float, 
                                    quality_evaluation: str, review_result: Dict):
        """高度な実行ログを記録"""
        try:
            log_data = {
                'task_id': task_id,
                'task_description': description,
                'agent_role': 'advanced_review_system',
                'output_summary': output[:100],
                'output_data': output[:500],
                'status': status,
                'quality_score': final_score,
                'quality_evaluation': quality_evaluation[:300]  # J列: 詳細な評価
            }
            await self.sheets.log_task_execution(log_data)
            print(f"   📋 高度なログ記録完了 - スコア: {final_score}/10")
        except Exception as e:
            print(f"   ⚠️  ログ記録エラー: {e}")
    
    async def run_tasks_with_advanced_review(self, max_tasks: int = 3):
        """高度なレビュー付きでタスクを実行"""
        print(f"\n🚀 高度なレビューシステム 実行開始 (最大{max_tasks}タスク)")
        
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
            print("✅ 実行可能なタスクはありません")
            return
        
        if len(pending_tasks) > max_tasks:
            pending_tasks = pending_tasks[:max_tasks]
        
        print(f"📋 実行対象: {len(pending_tasks)}タスク")
        
        success_count = 0
        total_scores = []
        
        for i, task in enumerate(pending_tasks, 1):
            task_id = task.get('task_id')
            description = task.get('description', '')
            
            print(f"\n{'='*60}")
            print(f"[{i}/{len(pending_tasks)}] タスク{task_id}: {description[:60]}...")
            print(f"{'='*60}")
            
            result = await self.execute_task_with_advanced_review(task_id, description)
            
            if result['success']:
                success_count += 1
                total_scores.append(result['final_score'])
                
                # 詳細なレビュー結果を表示
                review_result = result.get('review_result', {})
                print(f"   📊 使用レビューアー: {', '.join(review_result.get('reviewers_used', []))}")
            
            # 待機
            if i < len(pending_tasks):
                print("⏳ 15秒待機...")
                await asyncio.sleep(15)
        
        # サマリー
        if success_count > 0:
            avg_score = sum(total_scores) / len(total_scores)
            print(f"\n📊 実行結果: {success_count}/{len(pending_tasks)} 成功")
            print(f"🎯 平均品質スコア: {avg_score:.1f}/10")
            
            # スコア分布
            excellent = len([s for s in total_scores if s >= 9.0])
            good = len([s for s in total_scores if 7.0 <= s < 9.0])
            average = len([s for s in total_scores if 6.0 <= s < 7.0])
            needs_improvement = len([s for s in total_scores if s < 6.0])
            
            print(f"📈 品質分布:")
            print(f"  🌟 優秀(9.0+): {excellent}件")
            print(f"  ✅ 良好(7.0-8.9): {good}件")
            print(f"  ⚠️  平均(6.0-6.9): {average}件")
            print(f"  🔄 要修正(6.0未満): {needs_improvement}件")
        
        print(f"{'='*60}")

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='高度なレビューシステム')
    parser.add_argument('--max-tasks', type=int, default=3, help='最大タスク数')
    parser.add_argument('--task-id', type=int, help='特定のタスクIDを実行')
    
    args = parser.parse_args()
    
    print("🎯 高度なレビューシステム - 複数専門エージェント連携版")
    print("=" * 60)
    print("�� 特徴:")
    print("  ✅ コンテンツ品質レビュー")
    print("  ✅ 技術的実現性レビュー") 
    print("  ✅ WordPress実装レビュー")
    print("  ✅ 自動エージェント選択")
    print("  ✅ 詳細な評価根拠")
    print("=" * 60)
    
    sheets = GoogleSheetsManagerFinal(
        spreadsheet_id=get_spreadsheet_id(),
        service_account_file=get_service_account_file()
    )
    
    async with BrowserController(download_folder="./downloads") as browser:
        system = AdvancedReviewSystem(sheets, browser)
        
        if args.task_id:
            # 特定タスク実行
            tasks = await sheets.load_tasks_from_sheet("pm_tasks")
            target_task = next((t for t in tasks if t.get('task_id') == args.task_id), None)
            if target_task:
                await system.execute_task_with_advanced_review(
                    args.task_id, target_task.get('description', '')
                )
            else:
                print(f"❌ タスク{args.task_id} が見つかりません")
        else:
            # 複数タスク実行
            await system.run_tasks_with_advanced_review(args.max_tasks)
    
    print("\n🏁 実行完了")

if __name__ == "__main__":
    asyncio.run(main())

