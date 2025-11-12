"""
エラー自動解決ツール
エラーメッセージから正しい解決方法を提案
"""

import re
from typing import Dict

from tools.api_reference import APIReference


class ErrorResolver:
    """エラーメッセージから自動的に解決方法を提案"""

    # エラーパターンと解決方法
    ERROR_PATTERNS = {
        r"'(\w+)' object has no attribute '(\w+)'": {
            "type": "attribute_error",
            "handler": "handle_attribute_error",
        },
        r"missing (\d+) required positional argument": {
            "type": "argument_error",
            "handler": "handle_argument_error",
        },
        r"'(\w+)' object is not callable": {
            "type": "callable_error",
            "handler": "handle_callable_error",
        },
    }

    def __init__(self):
        self.api_ref = APIReference()

    def analyze_error(self, error_message: str) -> Dict[str, any]:
        """
        エラーメッセージを分析

        Args:
            error_message: エラーメッセージ

        Returns:
            解決方法の辞書
        """
        for pattern, info in self.ERROR_PATTERNS.items():
            match = re.search(pattern, error_message)
            if match:
                handler = getattr(self, info["handler"], None)
                if handler:
                    return handler(error_message, match)

        return {"error_type": "unknown", "solution": "エラーパターンが不明です", "suggestions": []}

    def handle_attribute_error(self, error_message: str, match) -> Dict:
        """AttributeError の解決方法を提案"""
        object_type = match.group(1)
        wrong_attr = match.group(2)

        # 正しいメソッド名を検索
        correct_method = self.api_ref.get_correct_method(object_type, wrong_attr)

        # 類似メソッドを検索
        similar_methods = self.api_ref.search_method(wrong_attr)

        solution = {
            "error_type": "attribute_error",
            "object": object_type,
            "wrong_attribute": wrong_attr,
            "correct_attribute": correct_method,
            "solution": f"❌ {wrong_attr} → ✅ {correct_method}",
            "similar_methods": similar_methods[:3],
        }

        return solution

    def handle_argument_error(self, error_message: str, match) -> Dict:
        """引数エラーの解決方法を提案"""
        missing_count = match.group(1)

        return {
            "error_type": "argument_error",
            "missing_count": missing_count,
            "solution": f"{missing_count}個の引数が不足しています。メソッドのシグネチャを確認してください。",
            "suggestions": ["APIリファレンスで正しいシグネチャを確認"],
        }

    def handle_callable_error(self, error_message: str, match) -> Dict:
        """呼び出しエラーの解決方法を提案"""
        object_type = match.group(1)

        return {
            "error_type": "callable_error",
            "object": object_type,
            "solution": "オブジェクトが呼び出し可能ではありません。()を付けずに使用してください。",
            "suggestions": ["変数名とメソッド名を確認"],
        }

    def print_solution(self, error_message: str):
        """解決方法を表示"""
        solution = self.analyze_error(error_message)

        print("\n" + "=" * 80)
        print("🔧 エラー自動解決")
        print("=" * 80)
        print(f"\nエラータイプ: {solution['error_type']}")
        print(f"\n解決方法:")
        print(f"  {solution['solution']}")

        if "similar_methods" in solution and solution["similar_methods"]:
            print(f"\n類似メソッド:")
            for method in solution["similar_methods"]:
                print(f"  • {method['component']}.{method['method']}")
                print(f"    {method['signature']}")
                print(f"    例: {method['example']}")

        print("=" * 80 + "\n")


# テスト
if __name__ == "__main__":
    resolver = ErrorResolver()

    print("🧪 テスト1: append_row エラー")
    resolver.print_solution("'GoogleSheetsManager' object has no attribute 'append_row'")

    print("\n🧪 テスト2: log_metric エラー")
    resolver.print_solution("'ObservabilityManager' object has no attribute 'log_metric'")
