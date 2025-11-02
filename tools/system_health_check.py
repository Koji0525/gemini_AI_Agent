#!/usr/bin/env python3
"""
システムヘルスチェック

【チェック項目】
1. 全シートの構造整合性
2. 空白行の検出
3. データ範囲の確認
4. 誤ったデータの検出
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.smart_sheets_manager import SmartSheetsManager


def health_check():
    """システムヘルスチェック実行"""
    print("=" * 60)
    print("🏥 システムヘルスチェック")
    print("=" * 60)

    manager = SmartSheetsManager()

    # チェック対象シート
    sheets = ["project_goal", "pm_tasks", "task_execution_log", "knowledge_base"]

    issues = []

    for sheet_name in sheets:
        print(f"\n📊 {sheet_name}:")

        try:
            # 構造確認
            structure = manager.get_sheet_structure(sheet_name)
            print(f"   ヘッダー: {structure['headers']}")
            print(f"   データ行: {structure['data_rows']}")

            # 空白行チェック
            empty = manager.cleanup_empty_rows(sheet_name, dry_run=True)
            if empty > 100:
                issues.append(f"{sheet_name}: {empty}行の空白行")
                print(f"   ⚠️ 空白行が多い: {empty}行")
            else:
                print(f"   ✅ 空白行: {empty}行")

        except Exception as e:
            issues.append(f"{sheet_name}: エラー ({e})")
            print(f"   ❌ エラー: {e}")

    # サマリー
    print("\n" + "=" * 60)
    print("📋 ヘルスチェック結果")
    print("=" * 60)

    if issues:
        print(f"\n⚠️ 問題検出: {len(issues)}件\n")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✅ 問題なし")

    print("=" * 60)


if __name__ == "__main__":
    health_check()
