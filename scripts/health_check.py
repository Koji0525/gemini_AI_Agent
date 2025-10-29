"""
システムヘルスチェック
システムの健全性を確認し、問題を検出
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from datetime import datetime
from tools.sheets_manager import GoogleSheetsManager
from agents.self_healing.logging import KnowledgeBaseManager, SimilaritySearchEngine, DecisionSupportSystem
from agents.self_healing.self_learning.intelligent_feedback import IntelligentFeedbackGenerator
from configuration.config_loader import get_config


async def health_check():
    """ヘルスチェック実行"""
    print("=" * 70)
    print("🏥 システムヘルスチェック")
    print(f"実行時刻: {datetime.now()}")
    print("=" * 70)

    try:
        # Google Sheets初期化
        spreadsheet_id = get_config("SPREADSHEET_ID")
        service_account_file = get_config("SERVICE_ACCOUNT_FILE")
        sheets_manager = GoogleSheetsManager(spreadsheet_id=spreadsheet_id, service_account_file=service_account_file)

        # コンポーネント初期化チェック
        print("\n1️⃣ コンポーネント初期化チェック...")
        kb_manager = KnowledgeBaseManager(sheets_manager)
        search_engine = SimilaritySearchEngine(kb_manager)
        feedback_gen = IntelligentFeedbackGenerator(kb_manager, search_engine)
        print("   ✅ 全コンポーネント正常")

        # ナレッジベース接続チェック
        print("\n2️⃣ ナレッジベース接続チェック...")
        stats = kb_manager.get_statistics()
        print(f"   ✅ 接続成功 ({stats.get('total_knowledge', 0)}件)")

        # システム健全性分析
        print("\n3️⃣ システム健全性分析...")
        health = feedback_gen.analyze_system_health()  # await 削除
        print(f"   📊 健全性スコア: {health['health_score']:.1f}/100")
        print(f"   ステータス: {health['status']}")

        if health["issues"]:
            print(f"   ⚠️ 検出された問題:")
            for issue in health["issues"]:
                print(f"      - {issue}")
        else:
            print("   ✅ 問題なし")

        print("\n" + "=" * 70)
        print("✅ ヘルスチェック完了")
        print("=" * 70)

        return health["health_score"] >= 60

    except Exception as e:
        print(f"\n❌ ヘルスチェック失敗: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(health_check())
    sys.exit(0 if success else 1)
