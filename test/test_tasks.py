"""
test_tasks.py - 既存タスクのテスト実行用スクリプト
"""
import logging
import asyncio
from pathlib import Path

# 基本インポート
from configuration.config_utils import config, ErrorHandler, PathManager

# ロガー設定
logger = logging.getLogger(__name__)

async def main():
    """メイン関数"""
    print("=" * 80)
    print("🚀 タスク実行システム テスト")
    print("=" * 80)
    
    # 1. Config テスト
    try:
        print("\n📋 Config 確認:")
        print(f"  - Config object: {type(config)}")
        print(f"  - PC ID: {getattr(config, 'pc_id', 'N/A')}")
        print("  ✅ Config OK")
    except Exception as e:
        print(f"  ❌ Config Error: {e}")
    
    # 2. PathManager テスト
    try:
        print("\n📁 PathManager 確認:")
        pm = PathManager()
        print(f"  - PathManager: {type(pm)}")
        # 利用可能なメソッドを確認
        methods = [m for m in dir(pm) if not m.startswith('_')]
        print(f"  - Available methods: {methods[:5]}...")
        print("  ✅ PathManager OK")
    except Exception as e:
        print(f"  ❌ PathManager Error: {e}")
    
    # 3. GoogleSheetsManager テスト（引数付き）
    try:
        print("\n📊 GoogleSheetsManager 確認:")
        from tools.sheets_manager import GoogleSheetsManager
        # スプレッドシートIDを指定
        sheets = GoogleSheetsManager(spreadsheet_id="test_id")
        print("  ✅ GoogleSheetsManager OK")
    except Exception as e:
        print(f"  ❌ GoogleSheetsManager Error: {e}")
    
    # 4. BrowserController テスト（引数付き）
    try:
        print("\n🌐 BrowserController 確認:")
        from browser_control.browser_controller import BrowserController
        # ダウンロードフォルダを指定
        browser = BrowserController(download_folder="./downloads")
        print("  ✅ BrowserController OK")
        
        # クリーンアップ
        if hasattr(browser, 'cleanup'):
            await browser.cleanup()
    except Exception as e:
        print(f"  ❌ BrowserController Error: {e}")
    
    # 5. ハイブリッド修正システムのテスト
    try:
        print("\n🔧 HybridFixSystem 確認:")
        from main_hybrid_fix import HybridFixSystem
        print("  ✅ HybridFixSystem imported OK")
    except Exception as e:
        print(f"  ❌ HybridFixSystem Error: {e}")
    
    print("\n" + "=" * 80)
    print("✅ 全テスト完了")
    print("=" * 80)

if __name__ == "__main__":
    # ログレベル設定（DEBUGを抑制）
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
