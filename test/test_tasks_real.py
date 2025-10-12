#!/usr/bin/env python3
"""
実タスクテスト（既存モジュールのみ使用）
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_wordpress_connection():
    """WordPress接続テスト"""
    logger.info("🔌 WordPress接続テスト開始...")
    try:
        from wordpress.wp_agent import WordPressAgent
        wp = WordPressAgent()
        logger.info("✅ WordPressエージェント初期化成功")
        return True
    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        return False

def test_sheets_connection():
    """Google Sheets接続テスト"""
    logger.info("📊 Google Sheets接続テスト開始...")
    try:
        from google_sheets.sheets_manager import GoogleSheetsManager
        sheets = GoogleSheetsManager()
        logger.info("✅ Google Sheetsマネージャー初期化成功")
        return True
    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        return False

def test_task_executor():
    """タスクエグゼキューター テスト"""
    logger.info("⚙️ タスクエグゼキューター テスト開始...")
    try:
        from scripts.task_executor import ContentTaskExecutor
        executor = ContentTaskExecutor()
        logger.info("✅ タスクエグゼキューター初期化成功")
        return True
    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        return False

def test_fix_system():
    """自動修正システム テスト"""
    logger.info("🔧 自動修正システム テスト開始...")
    try:
        from fix_agents.hybrid_fix_orchestrator import HybridFixOrchestrator
        orchestrator = HybridFixOrchestrator()
        logger.info("✅ 自動修正システム初期化成功")
        return True
    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        return False

def main():
    logger.info("=" * 80)
    logger.info("🧪 実タスクテスト実行")
    logger.info("=" * 80)
    
    tests = [
        ("WordPress接続", test_wordpress_connection),
        ("Google Sheets接続", test_sheets_connection),
        ("タスクエグゼキューター", test_task_executor),
        ("自動修正システム", test_fix_system),
    ]
    
    results = []
    for name, test_func in tests:
        logger.info(f"\n▶️ {name}テスト...")
        result = test_func()
        results.append((name, result))
    
    logger.info("\n" + "=" * 80)
    logger.info("📊 テスト結果サマリー")
    logger.info("=" * 80)
    
    for name, result in results:
        status = "✅ 成功" if result else "❌ 失敗"
        logger.info(f"{name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    logger.info(f"\n成功: {success_count}/{len(tests)}")
    
    return all(result for _, result in results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
