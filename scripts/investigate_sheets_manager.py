"""
GoogleSheetsManagerの実際のAPIを調査
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.sheets_manager import GoogleSheetsManager
import inspect


def investigate_sheets_manager():
    """GoogleSheetsManagerクラスの構造を調査"""

    print("=" * 60)
    print("GoogleSheetsManager API調査")
    print("=" * 60)
    print()

    # クラスのメソッド一覧
    print("【パブリックメソッド】")
    for name, method in inspect.getmembers(GoogleSheetsManager, predicate=inspect.isfunction):
        if not name.startswith("_"):
            sig = inspect.signature(method)
            print(f"  - {name}{sig}")

    print()
    print("【属性】")

    # __init__メソッドのシグネチャ確認
    init_sig = inspect.signature(GoogleSheetsManager.__init__)
    print(f"  __init__{init_sig}")

    print()
    print("=" * 60)
    print()

    # 推奨される使用方法を提案
    print("【推奨される使用方法】")
    print()
    print("1. シート確認方法:")
    print("   ※上記のメソッド一覧から適切なメソッドを選択")
    print()
    print("2. 行追加方法:")
    print("   ※上記のメソッド一覧から適切なメソッドを選択")
    print()


if __name__ == "__main__":
    investigate_sheets_manager()
