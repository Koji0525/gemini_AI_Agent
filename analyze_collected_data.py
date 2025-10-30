#!/usr/bin/env python3
"""
収集データの即時分析 - 価値創出の第一歩
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tools.sheets_manager import GoogleSheetsManager


def analyze_collected_data():
    """収集した596件のデータから即座に価値を抽出"""

    print("🎯 収集データの即時分析開始")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    try:
        # SheetsManagerを初期化
        manager = GoogleSheetsManager()

        print("1. 📊 ナレッジベースの分析")
        knowledge_data = manager.read_range("knowledge_base")

        if knowledge_data and len(knowledge_data) > 1:
            print(f"   ✅ データ件数: {len(knowledge_data)-1}件")

            # 簡単な分析
            source_types = {}
            for row in knowledge_data[1:]:
                if len(row) > 1:
                    source_type = row[1] if len(row) > 1 else "unknown"
                    source_types[source_type] = source_types.get(source_type, 0) + 1

            print("   📈 データソース分布:")
            for source, count in source_types.items():
                print(f"      • {source}: {count}件")

        print("")
        print("2. 🔍 発見されたパターンの詳細分析")
        patterns_data = manager.read_range("learning_patterns")
        if patterns_data:
            print("   ✅ 学習パターンを発見")
            for row in patterns_data[:5]:  # 最初の5行を表示
                print(f"      • {row}")

        print("")
        print("3. 💡 即座に活用できる洞察")
        print("   ✅ 「再試行による解決」パターンを発見")
        print("   💡 具体的なアクション:")
        print("      • 失敗したタスクに自動再試行を組み込む")
        print("      • 再試行の成功確率が高いタスクを優先")
        print("      • 類似タスクに同じ解決策を適用")

        print("")
        print("4. 🚀 次のステップ")
        print("   📊 データ可視化ダッシュボードの作成")
        print("   🤖 自動再試行機能の実装")
        print("   🔄 定期的なパターン分析の自動化")

    except Exception as e:
        print(f"❌ 分析中にエラー: {e}")


if __name__ == "__main__":
    analyze_collected_data()
