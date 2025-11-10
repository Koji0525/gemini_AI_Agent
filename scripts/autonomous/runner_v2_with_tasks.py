#!/usr/bin/env python3
"""
24時間自律稼働ランナー v2.0
VersionTrackerで本番環境版を自動選択
"""

import asyncio
import sys
from pathlib import Path
import importlib.util

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# VersionTrackerを読み込み
from tools.file_version_manager import VersionTracker


def load_production_orchestrator():
    """VersionTrackerから本番環境版を読み込む"""

    print("🔍 本番環境版を検索中...")

    tracker = VersionTracker()
    prod_info = tracker.get_production_version()

    if not prod_info:
        print("❌ 本番環境版が登録されていません")
        print("\n📋 登録方法:")
        print("   python3 tools/file_version_manager.py track")
        return None

    prod_path = Path(prod_info.get("path", ""))

    if not prod_path.exists():
        print(f"❌ ファイルが見つかりません: {prod_path}")
        return None

    print(f"✅ 本番環境版発見: {prod_info.get('file')}")
    print(f"   ステータス: {prod_info.get('status')}")
    print(f"   説明: {prod_info.get('description', 'N/A')}")

    # モジュールとして読み込み
    try:
        spec = importlib.util.spec_from_file_location("orchestrator", prod_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "IntegratedOrchestrator"):
            print(f"   ✅ IntegratedOrchestrator読み込み成功")
            return module.IntegratedOrchestrator
        else:
            print(f"   ❌ IntegratedOrchestratorが見つかりません")
            return None

    except Exception as e:
        print(f"   ❌ 読み込みエラー: {e}")

        # エラーをVersionTrackerに記録
        tracker.mark_as_broken(file_name=prod_info.get("file"), error=str(e))

        return None


async def main():
    print("=" * 70)
    print("🚀 24時間自律稼働システム起動（v2.0）")
    print("=" * 70)
    print("")

    # 本番環境版を読み込み
    OrchestratorClass = load_production_orchestrator()

    if OrchestratorClass is None:
        print("\n❌ システムを読み込めませんでした")
        return

    # 初期化
    print("\n🔧 初期化中...")
    try:
        orchestrator = OrchestratorClass()
        print("   ✅ 初期化完了")
    except Exception as e:
        print(f"   ❌ 初期化エラー: {e}")
        return

    # 実行
    print("\n" + "=" * 70)
    print("実行開始...")
    print("=" * 70 + "\n")

    try:
        if hasattr(orchestrator, "run_continuous_cycle"):
            await orchestrator.run_continuous_cycle()
        elif hasattr(orchestrator, "run"):
            await orchestrator.run()
        else:
            print("❌ 実行メソッドが見つかりません")

    except KeyboardInterrupt:
        print("\n⚠️  停止シグナル受信 - 正常終了")
    except Exception as e:
        print(f"\n❌ 実行エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
