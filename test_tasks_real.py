#!/usr/bin/env python3
"""
実タスクテスト（修正版）
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from wordpress.wp_agent import WordPressAgent  # 正しいクラス名
from agents.content_agent import ContentAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_wordpress_connection():
    """WordPress接続テスト"""
    logger.info("🔌 WordPress接続テスト開始...")
    try:
        wp = WordPressAgent()
        logger.info("✅ WordPressエージェント初期化成功")
        return True
    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        return False

def test_content_generation():
    """コンテンツ生成テスト"""
    logger.info("�� コンテンツ生成テスト開始...")
    try:
        agent = ContentAgent()
        content = agent.generate_simple_content(
            topic="AIと自動化",
            style="informative"
        )
        logger.info(f"✅ コンテンツ生成成功: {len(content)} 文字")
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
        ("コンテンツ生成", test_content_generation),
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
