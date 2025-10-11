"""
test_tasks.py - 動作するバージョン
"""
import asyncio
import logging

logger = logging.getLogger(__name__)

async def main():
    """メイン関数"""
    print("=" * 60)
    print("🚀 テストタスクシステム")
    print("=" * 60)
    
    # 簡単なテスト
    try:
        from config_utils import config
        print("✅ Config loaded successfully")
    except Exception as e:
        print(f"⚠️ Config error: {e}")
    
    try:
        from browser_controller import BrowserController
        print("✅ BrowserController imported successfully")
    except Exception as e:
        print(f"⚠️ BrowserController error: {e}")
    
    print("=" * 60)
    print("✅ テスト完了")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
