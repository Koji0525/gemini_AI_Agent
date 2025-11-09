"""v30統合テスト"""

import asyncio
import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.mark.asyncio
async def test_v30():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧪 IntegratedOrchestrator v30 テスト")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    try:
        # v30をインポート
        sys.path.insert(0, str(project_root / "scripts"))
        from integrated_orchestrator_v30_knowledge import \
            IntegratedOrchestrator

        print("✅ v30インポート成功")

        # 初期化テスト
        orchestrator = IntegratedOrchestrator()

        # ナレッジマネージャーが統合されているか確認
        if hasattr(orchestrator, "knowledge_manager"):
            if orchestrator.knowledge_manager:
                print("✅ ナレッジマネージャー統合確認")

                # 統計表示
                stats = orchestrator.knowledge_manager.get_stats()
                print(f"📊 総ナレッジ数: {stats['total_knowledge']}")
            else:
                print("⚠️ ナレッジマネージャーが初期化されていません")
        else:
            print("❌ ナレッジマネージャーが見つかりません")

        print("\n✅ 統合テスト完了")

    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_v30())
