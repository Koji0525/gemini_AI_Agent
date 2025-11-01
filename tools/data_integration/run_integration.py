#!/usr/bin/env python3
"""
データ統合パイプライン実行スクリプト - 修正版
"""

import os
import yaml
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.data_integration.pipeline import DataIntegrationPipeline


def load_config():
    """設定ファイルを読み込み"""
    config_path = project_root / "config" / "data_integration.yaml"

    if not config_path.exists():
        print(f"❌ 設定ファイルが見つかりません: {config_path}")
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        print("✅ 設定ファイル読み込み完了")
        return config
    except Exception as e:
        print(f"❌ 設定ファイル読み込みエラー: {e}")
        return None


def main():
    """メイン実行関数"""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 データ統合パイプライン")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    # 設定ファイル読み込み
    print("⚙️  設定ファイル読み込み中...")
    config = load_config()
    if not config:
        return

    # パイプライン実行 - 修正: 引数を1つだけ渡す
    try:
        pipeline = DataIntegrationPipeline(config)  # sheets_managerは内部で初期化
        metrics = pipeline.run()

        # 結果表示
        print()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📊 実行結果")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📥 抽出エントリ: {metrics['total_entries']}件")
        print(f"💾 保存エントリ: {metrics['saved_count']}件")
        print(f"🔍 検出パターン: {metrics['patterns_found']}個")
        print(f"⏰ 実行時刻: {metrics['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        print(f"❌ パイプライン実行エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
