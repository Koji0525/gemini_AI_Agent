#!/usr/bin/env python3
"""
WordPressプラグイン実行システム - インストール・設定・レビュー一貫処理
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
    from wordpress.wp_plugin_agent import WordPressPluginAgent
    from wordpress.wp_review_agent import WordPressReviewAgent
    print("✅ すべてのモジュールインポート成功")
except ImportError as e:
    print(f"❌ モジュールインポートエラー: {e}")
    sys.exit(1)

class WordPressPluginSystem:
    """WordPressプラグイン実行システム"""
    
    def __init__(self, sheets_manager, browser_controller):
        self.sheets = sheets_manager
        self.browser = browser_controller
        self.plugin_agent = WordPressPluginAgent(browser_controller)
        self.review_agent = WordPressReviewAgent(browser_controller)
        
        # 設定確認
        if wp_config_loader.has_valid_config():
            print("🎯 WordPressプラグインシステム: 有効")
        else:
            print("⚠️  WordPressプラグインシステム: 設定不足")
    
    async def execute_plugin_task_with_review(self, task_id: int, task_description: str) -> Dict:
        """プラグインタスクを実行しレビューまで行う"""
        print(f"\n🎯 プラグインタスク実行: タスク{task_id}")
        print(f"📝 内容: {task_description}")
        
        try:
            # ステータスを進行中に更新
            await self.sheets.update_task_status(task_id, "in_progress", "pm_tasks")
            
            # 1. プラグインタスク実行
            print("🔧 プラグインタスクを実行中...")
            plugin_result = await self.plugin_agent.execute_plugin_task(task_description)
            
            # 2. レビュー実行
            print("🔍 実行結果をレビュー中...")
            review_report = await self.review_agent.generate_review_report(plugin_result)
            
            # 3. 結果を統合
            final_success = plugin_result.get('success', False) and review_report.get('success', False)
            review_score = review_report.get('review_score', 0)
            
            # 4. ステータス更新
            final_status = "completed" if final_success else "failed"
            await self.sheets.update_task_status(task_id, final_status, "pm_tasks")
            
            # 5. 出力を生成
            output = self._generate_output(plugin_result, review_report, task_description)
            
            # 6. ログ記録
            await self.log_execution(
                task_id, task_description, output, final_success, review_score, review_report
            )
            
            print(f"✅ プラグインタスク{task_id} 完了")
            print(f"📊 レビュースコア: {review_score}/10")
            
            return {
                "success": final_success,
                "review_score": review_score,
                "output": output,
                "plugin_result": plugin_result,
                "review_report": review_report
            }
            
        except Exception as e:
            print(f"❌ プラグインタスク実行エラー: {e}")
            await self.sheets.update_task_status(task_id, "failed", "pm_tasks")
            await self.log_execution(
                task_id, task_description, str(e), False, 0, {}
            )
            return {"success": False, "error": str(e)}
    
    def _generate_output(self, plugin_result: Dict, review_report: Dict, task_description: str) -> str:
        """実行結果から出力を生成"""
        plugin_slug = plugin_result.get('plugin_slug', 'unknown')
        review_score = review_report.get('review_score', 0)
        overall_rating = review_report.get('overall_rating', '不明')
        
        output = f"""# プラグインタスク実行レポート

## タスク概要
- **タスク**: {task_description}
- **プラグイン**: {plugin_slug}
- **実行日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 実行結果
- **レビュースコア**: {review_score}/10
- **総合評価**: {overall_rating}
- **インストール状態**: {review_report.get('installation_status', '不明')}

## 詳細
"""

        # 問題点
        issues = review_report.get('issues', [])
        if issues:
            output += "\n## 🔍 発見された問題点\n"
            for issue in issues:
                output += f"- {issue}\n"
        
        # 推奨事項
        recommendations = review_report.get('recommendations', [])
        if recommendations:
            output += "\n## 💡 推奨事項\n"
            for rec in recommendations:
                output += f"- {rec}\n"
        
        # 実行詳細
        task_results = plugin_result.get('results', {})
        if task_results:
            output += "\n## 🔧 実行詳細\n"
            for step, result in task_results.items():
                success = result.get('success', False)
                status_icon = "✅" if success else "❌"
                output += f"- {status_icon} {step}: {result.get('message', '実行完了')}\n"
        
        return output
    
    async def log_execution(self, task_id: int, description: str, output: str, success: bool, 
                          review_score: int, review_report: Dict):
        """実行結果をログに記録"""
        try:
            log_data = {
                'task_id': task_id,
                'task_description': description,
                'agent_role': 'wp_plugin_system',
                'output_summary': output[:100],
                'output_data': output[:500],
                'status': 'completed' if success else 'failed',
                'quality_score': review_score,
                'quality_evaluation': f"プラグインレビュー: {review_report.get('overall_rating', '不明')} - {review_report.get('details', '')}"
            }
            await self.sheets.log_task_execution(log_data)
            print(f"   📋 ログ記録完了 - レビュースコア: {review_score}/10")
        except Exception as e:
            print(f"   ⚠️  ログ記録エラー: {e}")
    
    async def run_plugin_tasks(self, max_tasks: int = 3):
        """プラグイン関連タスクを実行"""
        print(f"\n🔧 WordPressプラグインタスク実行開始 (最大{max_tasks}件)")
        
        # タスク読み込み
        tasks = await self.sheets.load_tasks_from_sheet("pm_tasks")
        
        # プラグイン関連タスクをフィルタリング
        plugin_tasks = []
        for task in tasks:
            description = task.get('description', '').lower()
            status = task.get('status', '').lower()
            
            # プラグイン関連キーワードでフィルタ
            plugin_keywords = ['プラグイン', 'plugin', 'インストール', 'install', '設定', 'configure']
            is_plugin_task = any(keyword in description for keyword in plugin_keywords)
            is_pending = status in ['pending', '']
            
            if is_plugin_task and is_pending:
                plugin_tasks.append(task)
        
        if not plugin_tasks:
            print("✅ 実行可能なプラグインタスクはありません")
            return
        
        if len(plugin_tasks) > max_tasks:
            plugin_tasks = plugin_tasks[:max_tasks]
        
        print(f"📦 プラグインタスク実行対象: {len(plugin_tasks)}件")
        
        success_count = 0
        total_review_score = 0
        
        for i, task in enumerate(plugin_tasks, 1):
            task_id = task.get('task_id')
            description = task.get('description', '')
            
            print(f"\n{'='*60}")
            print(f"[{i}/{len(plugin_tasks)}] プラグインタスク{task_id}: {description[:60]}...")
            print(f"{'='*60}")
            
            result = await self.execute_plugin_task_with_review(task_id, description)
            
            if result['success']:
                success_count += 1
                total_review_score += result['review_score']
            
            # 待機
            if i < len(plugin_tasks):
                print("⏳ 15秒待機...")
                await asyncio.sleep(15)
        
        # サマリー
        if success_count > 0:
            avg_score = total_review_score / success_count
            print(f"\n📊 プラグインタスク実行結果: {success_count}/{len(plugin_tasks)} 成功")
            print(f"🎯 平均レビュースコア: {avg_score:.1f}/10")
        else:
            print(f"\n❌ プラグインタスク実行結果: 0/{len(plugin_tasks)} 成功")
    
    async def close(self):
        """リソースを解放"""
        await self.plugin_agent.close()
        await self.review_agent.close()

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='WordPressプラグイン実行システム')
    parser.add_argument('--max-tasks', type=int, default=3, help='最大タスク数')
    parser.add_argument('--task-id', type=int, help='特定のタスクIDを実行')
    
    args = parser.parse_args()
    
    print("🎯 WordPressプラグイン実行システム")
    print("=" * 60)
    print("📊 機能:")
    print("  ✅ プラグイン自動インストール")
    print("  ✅ 設定自動適用")
    print("  ✅ インストール状態の自動レビュー")
    print("  ✅ レビュースコア付き品質評価")
    print("=" * 60)
    
    sheets = GoogleSheetsManagerFinal(
        spreadsheet_id=get_spreadsheet_id(),
        service_account_file=get_service_account_file()
    )
    
    async with BrowserController(download_folder="./downloads") as browser:
        system = WordPressPluginSystem(sheets, browser)
        
        # WordPressに接続
        print("🔗 WordPressに接続...")
        
        if args.task_id:
            # 特定タスク実行
            tasks = await sheets.load_tasks_from_sheet("pm_tasks")
            target_task = next((t for t in tasks if t.get('task_id') == args.task_id), None)
            if target_task:
                await system.execute_plugin_task_with_review(
                    args.task_id, target_task.get('description', '')
                )
            else:
                print(f"❌ タスク{args.task_id} が見つかりません")
        else:
            # プラグインタスク実行
            await system.run_plugin_tasks(args.max_tasks)
        
        await system.close()
    
    print("\n�� 実行完了")

if __name__ == "__main__":
    asyncio.run(main())

