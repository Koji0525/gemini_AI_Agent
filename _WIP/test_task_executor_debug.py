#!/usr/bin/env python3
"""TaskExecutor統合テスト（デバッグモード）"""
import asyncio
import sys
import logging
from pathlib import Path

# ログレベルをDEBUGに
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_debug():
    print("🔍 TaskExecutor デバッグモード")
    print("=" * 70)
    
    try:
        # インポート
        from browser_control.browser_controller import EnhancedBrowserController
        from scripts.task_executor import TaskExecutor
        
        # BrowserController準備
        print("\n📦 BrowserController準備")
        browser = EnhancedBrowserController(
            download_folder=Path("temp_workspace/downloads"),
            mode="text",
            service="google"
        )
        await browser.setup_browser()
        print(f"   ✅ browser準備完了: {browser}")
        print(f"   ✅ browser.is_initialized: {browser.is_initialized}")
        
        # TaskExecutor初期化（ログ詳細出力）
        print("\n⚙️ TaskExecutor初期化開始")
        print("   （初期化ログを注視してください）")
        print("-" * 70)
        
        task_executor = TaskExecutor(
            sheets_manager=None,
            browser_controller=browser
        )
        
        print("-" * 70)
        print("   TaskExecutor初期化完了")
        
        # エージェント状態確認
        print("\n🔍 エージェント状態:")
        print(f"   task_executor.browser: {task_executor.browser}")
        print(f"   task_executor.design_agent: {task_executor.design_agent}")
        print(f"   task_executor.dev_agent: {task_executor.dev_agent}")
        print(f"   task_executor.review_agent_instance: {task_executor.review_agent_instance}")
        
        # エージェント辞書確認
        print("\n🔍 self.agents辞書:")
        for key, value in task_executor.agents.items():
            print(f"   {key}: {value}")
        
        await browser.cleanup()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_debug())
    sys.exit(0 if result else 1)
