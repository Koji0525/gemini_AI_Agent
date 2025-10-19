#!/usr/bin/env python3
"""
完全WordPress連携版 - 記事作成機能対応
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

print("🔧 モジュールインポート中...")

try:
    from configuration.config_loader import get_spreadsheet_id, get_service_account_file
    from browser_control.browser_controller import BrowserController
    from tools.sheets_manager_with_logging import GoogleSheetsManager
    from configuration.wp_config_loader_fixed import wp_config_loader
    from wordpress.simple_wp_agent import SimpleWordPressAgent
    print("✅ すべてのモジュールインポート成功")
except ImportError as e:
    print(f"❌ モジュールインポートエラー: {e}")
    sys.exit(1)

class FullWPExecutor:
    """完全なWordPress連携エグゼキューター"""
    
    def __init__(self, sheets_manager, browser_controller):
        self.sheets = sheets_manager
        self.browser = browser_controller
        self.wp_agent = SimpleWordPressAgent(browser_controller) if wp_config_loader.has_valid_config() else None
        
        # 設定確認
        if self.wp_agent:
            print("🎯 WordPress連携: 有効（記事作成可能）")
        else:
            print("⚠️  WordPress連携: 設定不足")
    
    def is_wp_task(self, task: Dict) -> bool:
        """WordPressタスクか判定"""
        description = task.get('description', '').lower()
        role = task.get('required_role', '').lower()
        
        wp_keywords = ['wordpress', 'wp', '投稿', '記事', 'post', 'page', 'cpt', 'custom post']
        return any(keyword in description or keyword in role for keyword in wp_keywords)
    
    async def execute_wp_task(self, task: Dict) -> tuple:
        """WordPressタスクを実行"""
        try:
            description = task.get('description', '')
            
            # シンプルな記事作成（実際はもっと高度な解析が必要）
            title = f"タスク{task.get('task_id')}: {description[:30]}..."
            content = f"""
# タスク {task.get('task_id')}

**説明**: {description}

**作成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**担当ロール**: {task.get('required_role', 'general')}

この記事はAIエージェントによって自動生成されました。
"""
            
            result = await self.wp_agent.create_post(title, content)
            
            if result['success']:
                output = f"WordPress記事作成完了: {result['message']}"
                return True, output, ""
            else:
                return False, "", f"WordPressエラー: {result.get('error', '不明なエラー')}"
                
        except Exception as e:
            return False, "", f"WordPress実行エラー: {e}"
    
    async def execute_gemini_task(self, task: Dict) -> tuple:
        """Geminiタスクを実行"""
        try:
            prompt = f"""以下のタスクを専門家として実行してください:

タスク: {task.get('description')}
役割: {task.get('required_role', 'general')}

具体的で実用的な成果物を作成してください。"""
            
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
        """タスクを実行"""
        
        print(f"\n🚀 完全WordPress連携版 実行開始 (最大{max_tasks}タスク)")
        
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
        
        # WordPressタスクと通常タスクを分類
        wp_tasks = [t for t in pending_tasks if self.is_wp_task(t)]
        gemini_tasks = [t for t in pending_tasks if not self.is_wp_task(t)]
        
        print(f"  🎯 WordPressタスク: {len(wp_tasks)}件")
        print(f"  🤖 Geminiタスク: {len(gemini_tasks)}件")
        
        success_count = 0
        
        # タスク実行
        all_tasks = pending_tasks  # 元の順序を保持
        
        for i, task in enumerate(all_tasks, 1):
            task_id = task.get('task_id')
            description = task.get('description', '')[:60]
            is_wp = self.is_wp_task(task)
            
            print(f"\n{'='*50}")
            print(f"[{i}/{len(all_tasks)}] タスク{task_id}: {description}...")
            print(f"  種類: {'🎯 WordPress' if is_wp else '🤖 Gemini'}")
            
            try:
                # ステータス更新
                await self.sheets.update_task_status(task_id, "in_progress", "pm_tasks")
                
                # タスク実行
                if is_wp and self.wp_agent:
                    success, output, error = await self.execute_wp_task(task)
                else:
                    success, output, error = await self.execute_gemini_task(task)
                
                # 結果処理
                if success:
                    await self.sheets.update_task_status(task_id, "completed", "pm_tasks")
                    success_count += 1
                    print(f"✅ 完了 - {len(output):,}文字")
                else:
                    await self.sheets.update_task_status(task_id, "failed", "pm_tasks")
                    print(f"❌ 失敗: {error}")
                
                # ログ記録
                await self.log_execution(task, output, success, "wp" if is_wp else "gemini")
                
                # 待機
                if i < len(all_tasks):
                    print("⏳ 10秒待機...")
                    await asyncio.sleep(10)
                    
            except Exception as e:
                print(f"❌ タスク実行エラー: {e}")
        
        print(f"\n📊 実行結果: {success_count}/{len(all_tasks)} 成功")
        
        # WordPressエージェントをクローズ
        if self.wp_agent:
            await self.wp_agent.close()
    
    async def log_execution(self, task: Dict, output: str, success: bool, agent_type: str):
        """実行結果をログに記録"""
        try:
            log_data = {
                'task_id': task.get('task_id'),
                'task_description': task.get('description', ''),
                'agent_role': f"{task.get('required_role', 'general')}({agent_type})",
                'output_summary': output[:100] if output else '',
                'output_data': output[:500] if output else '',
                'status': 'completed' if success else 'failed'
            }
            await self.sheets.log_task_execution(log_data)
        except Exception as e:
            print(f"⚠️  ログ記録エラー: {e}")

async def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-tasks', type=int, default=3, help='最大タスク数')
    args = parser.parse_args()
    
    print("🎯 完全WordPress連携版")
    print("=" * 50)
    
    # 設定確認
    wp_config_loader.has_valid_config()
    
    sheets = GoogleSheetsManager(
        spreadsheet_id=get_spreadsheet_id(),
        service_account_file=get_service_account_file()
    )
    
    async with BrowserController(download_folder="./downloads") as browser:
        executor = FullWPExecutor(sheets, browser)
        await executor.run_tasks(max_tasks=args.max_tasks)
    
    print("\n🏁 実行完了")

if __name__ == "__main__":
    asyncio.run(main())

