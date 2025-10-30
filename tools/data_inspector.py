#!/usr/bin/env python3
"""
データ構造調査ツール
変更理由: 実データの構造を確認して適切な解析方法を決定
"""

import sys
from pathlib import Path
from collections import Counter

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.sheets_manager import GoogleSheetsManager


def inspect_data():
    print("🔍 データ構造調査")
    print("=" * 60)

    sheets = GoogleSheetsManager()

    # タスク実行ログの調査
    print("\n📊 task_execution_log の調査:")
    try:
        data = sheets.read_range("task_execution_log")
        if data and len(data) > 1:
            headers = data[0]
            print(f"   列: {headers}")
            print(f"   行数: {len(data) - 1}件")

            # 各列のサンプル値
            print("\n   サンプル値（最初の3行）:")
            for i, row in enumerate(data[1:4], 1):
                print(f"\n   行{i}:")
                for j, header in enumerate(headers):
                    value = row[j] if j < len(row) else "(空)"
                    print(f"      {header}: {value}")

            # status列の全ユニーク値
            if "status" in headers:
                status_idx = headers.index("status")
                statuses = [row[status_idx] for row in data[1:] if len(row) > status_idx]
                status_counter = Counter(statuses)
                print(f"\n   status列の全ユニーク値:")
                for status, count in status_counter.most_common():
                    print(f"      '{status}': {count}件")
    except Exception as e:
        print(f"   ❌ エラー: {e}")

    # ナレッジベースの調査
    print("\n📚 knowledge_base の調査:")
    try:
        data = sheets.read_range("knowledge_base")
        if data and len(data) > 1:
            headers = data[0]
            print(f"   列: {headers}")
            print(f"   行数: {len(data) - 1}件")

            # サンプル
            print("\n   サンプル値（最初の2行）:")
            for i, row in enumerate(data[1:3], 1):
                print(f"\n   行{i}:")
                for j, header in enumerate(headers):
                    value = row[j] if j < len(row) else "(空)"
                    # 長いコンテンツは省略
                    if len(str(value)) > 50:
                        value = str(value)[:50] + "..."
                    print(f"      {header}: {value}")
    except Exception as e:
        print(f"   ❌ エラー: {e}")

    print("\n" + "=" * 60)
    print("✅ 調査完了")


if __name__ == "__main__":
    inspect_data()
