#!/usr/bin/env python3
"""
🔍 Google Sheets メソッド検証ツール v1.0
目的: コード生成前にメソッド名・引数を検証
"""

import inspect
from typing import List, Dict


class MethodValidator:
    """メソッド名と引数の検証"""

    @staticmethod
    def validate_method_call(class_obj, method_name: str, args: List, kwargs: Dict) -> Dict:
        """
        メソッド呼び出しの妥当性を検証

        Args:
            class_obj: クラスオブジェクト
            method_name: メソッド名
            args: 位置引数
            kwargs: キーワード引数

        Returns:
            検証結果
        """
        result = {"valid": True, "issues": [], "suggestions": []}

        # 1. メソッドの存在確認
        if not hasattr(class_obj, method_name):
            result["valid"] = False
            result["issues"].append(f"メソッド '{method_name}' が存在しません")

            # 類似メソッドを提案
            all_methods = [m for m in dir(class_obj) if not m.startswith("_")]
            similar = [m for m in all_methods if method_name.lower() in m.lower()]

            if similar:
                result["suggestions"].append(f"類似メソッド: {similar}")

            return result

        # 2. 引数の検証
        method = getattr(class_obj, method_name)
        sig = inspect.signature(method)

        try:
            sig.bind(*args, **kwargs)
        except TypeError as e:
            result["valid"] = False
            result["issues"].append(f"引数エラー: {e}")

        return result

    @staticmethod
    def get_method_signature(class_obj, method_name: str) -> str:
        """メソッドのシグネチャを取得"""
        if not hasattr(class_obj, method_name):
            return f"メソッド '{method_name}' は存在しません"

        method = getattr(class_obj, method_name)
        sig = inspect.signature(method)
        return f"{method_name}{sig}"


def main():
    """メイン実行"""
    import sys

    sys.path.insert(0, "/workspaces/gemini_AI_Agent")

    from tools.sheets_manager import GoogleSheetsManager

    print("=" * 60)
    print("🔍 GoogleSheetsManager メソッド一覧")
    print("=" * 60)

    validator = MethodValidator()

    # 全メソッドを表示
    methods = [m for m in dir(GoogleSheetsManager) if not m.startswith("_")]

    for method_name in methods:
        sig = validator.get_method_signature(GoogleSheetsManager, method_name)
        print(f"✅ {sig}")

    print("=" * 60)


if __name__ == "__main__":
    main()
