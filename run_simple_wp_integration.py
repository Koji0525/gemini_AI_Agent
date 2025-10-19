#!/usr/bin/env python3
"""
シンプルWordPress連携版 - 確実に動作するバージョン
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

os.environ['DISPLAY'] = ':1'

print("🔧 モジュールインポート中...")

try:
    from configuration.config_loader import get_spreadsheet_id, get_service_account_file
    from browser_control.browser_controller import BrowserController
    from tools.sheets_manager import GoogleSheetsManager
    from configuration.wp_config_loader_fixed import wp_config_loader
    print("✅ すべてのモジュールインポート成功")
except ImportError as e:
    print(f"❌ モジュールインポートエラー: {e}")
    sys.exit(1)

class SimpleWPExecutor:
    """シンプルなWordPress連携エグゼキューター"""
    
    def __init__(self, sheets_manager, browser_controller):
        self.sheets = sheets_manager
        self.browser = browser_controller
        self.wp_initialized = False
        
        # WordPress設定チェック
        if wp_config_loader.has_valid_config():
            print("🎯 WordPress連携: 準備完了")
        else:
            print("⚠️  WordPress連携: 設定不足")
    
    async def initialize_wordpress(self):
        """WordPressを初期化"""
        if not wp_config_loader.has_valid_config():
            return False
        
        try:
            print("🔐 WordPressログイン試行...")
            
            # 新しいタブでWordPressを開く
            wp_page = await self.browser.context.new_page()
            
            # 一時的にWordPressページを使用
            original_page = self.browser.page
            self.browser.page = wp_page
            
            # WordPressログイン
            wp_url = wp_config_loader.get_wp_url()
            username = wp_config_loader.get_wp_username()
            password = wp_config_loader.get_wp_password()
            
            print(f"   URL: {wp_url}")
            print(f"   ユーザー: {username}")
            
            # ログインページに移動
            login_url = f"{wp_url}/wp-admin"
            await self.browser.page.goto(login_url, wait_until='networkidle')
            
            # ログインフォーム入力
            await self.browser.page.fill('#user_login', username)
            await self.browser.page.fill('#user_pass', password)
            await self.browser.page.click('#wp-submit')
            
            # ログイン成功確認
            await self.browser.page.wait_for_selector('#wpadminbar', timeout=15000)
            
            print("✅ WordPressログイン成功")
            
            # 元のページに戻る
            self.browser.page = original_page
            self.wp_initialized = True
            return True
            
        except Exception as e:
            print(f"❌ WordPressログイン失敗: {e}")
            # 元のページに戻る
            self.browser.page = original_page
            return False
    
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
        """タスクを実行"""
        
        print(f"\n🚀 タスク実行開始 (最大{max_tasks}タスク)")
        
        # Gemini初期化
        print("🔗 Geminiに接続...")
        if not await self.browser.navigate_to_gemini():
            print("❌ Gemini接続失敗")
            return
        
        print("✅ Gemini準備完了")
        
        # WordPress初期化（設定がある場合）
        if wp_config_loader.has_valid_config():
            await self.initialize_wordpress()
        
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
                    # ステータスを完了に更新
                    await self.sheets.update_task_status(task_id, "completed", "pm_tasks")
                    success_count += 1
                    print(f"✅ 完了 - {len(output):,}文字")
                else:
                    # ステータスを失敗に更新
                    await self.sheets.update_task_status(task_id, "failed", "pm_tasks")
                    print(f"❌ 失敗: {error}")
                
                # ログ記録
                await self.log_execution(task, output, success)
                
                # 待機（レート制限）
                if i < len(pending_tasks):
                    print("⏳ 10秒待機...")
                    await asyncio.sleep(10)
                    
            except Exception as e:
                print(f"❌ タスク実行エラー: {e}")
        
        print(f"\n📊 実行結果: {success_count}/{len(pending_tasks)} 成功")
    
    async def log_execution(self, task: Dict, output: str, success: bool):
        """実行結果をログに記録"""
        try:
            log_data = {
                'task_id': task.get('task_id'),
                'task_description': task.get('description', ''),
                'agent_role': task.get('required_role', ''),
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
    
    print("🎯 シンプルWordPress連携版")
    print("=" * 50)
    
    # 設定確認
    wp_config_loader.has_valid_config()
    
    sheets = GoogleSheetsManager(
        spreadsheet_id=get_spreadsheet_id(),
        service_account_file=get_service_account_file()
    )
    
    async with BrowserController(download_folder="./downloads") as browser:
        executor = SimpleWPExecutor(sheets, browser)
        await executor.run_tasks(max_tasks=args.max_tasks)
    
    print("\n🏁 実行完了")

if __name__ == "__main__":
    asyncio.run(main())

