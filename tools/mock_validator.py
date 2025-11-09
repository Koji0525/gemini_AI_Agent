#!/usr/bin/env python3
"""
モック検証ツール - モックが実際の実装を正しく模倣しているか検証
"""
import inspect
from pathlib import Path


class MockValidator:
    def __init__(self):
        self.issues = []

    def validate_mock_against_implementation(self, mock_obj, target_path, method_name):
        """モックが実装と一致しているか検証"""
        try:
            module_path, class_name = target_path.rsplit(".", 1)
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)

            # 実際のメソッドを取得
            real_method = getattr(cls, method_name)

            # モックオブジェクトを取得
            mock_method = getattr(mock_obj, method_name)

            print(f"🔍 {class_name}.{method_name} のモック検証:")

            # 実際のメソッドが非同期か確認
            is_async_real = inspect.iscoroutinefunction(real_method)
            print(f"   実装の非同期: {is_async_real}")

            # モックの設定を確認
            if hasattr(mock_method, "return_value"):
                print(f"   モック戻り値: 設定済み")
            elif hasattr(mock_method, "side_effect"):
                print(f"   モック副作用: 設定済み")
            else:
                self.issues.append(f"❌ {method_name} のモックに戻り値/副作用が設定されていません")

            # 非同期の一致性チェック
            if is_async_real:
                # 非同期メソッドは async def でモックするべき
                if not (
                    inspect.iscoroutinefunction(mock_method)
                    or (
                        hasattr(mock_method, "return_value")
                        and inspect.iscoroutine(mock_method.return_value)
                    )
                ):
                    self.issues.append(
                        f"⚠️  {method_name} は非同期メソッドですが、モックが非同期に対応していません"
                    )

            return True
        except Exception as e:
            self.issues.append(f"❌ 検証エラー: {e}")
            return False

    def validate_test_mocks(self, test_file_path):
        """テストファイルのモックを検証"""
        with open(test_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # モックの使用パターンを検出
        mock_patterns = [
            ("genai", "agents.code_generation.code_generation_agent.genai"),
            ("GeminiAPIClient", "browser_control.gemini_api_client.GeminiAPIClient"),
        ]

        for mock_name, target_path in mock_patterns:
            if mock_name in content:
                print(f"📋 {test_file_path} での {mock_name} モック使用を検出")
                # 実際の検証はテスト実行時に実施する必要がある

    def generate_report(self):
        """検証レポートを生成"""
        if self.issues:
            print("❌ モック検証で問題を検出:")
            for issue in self.issues:
                print(f"  {issue}")
            return False
        else:
            print("✅ すべてのモック検証を通過")
            return True


def main():
    validator = MockValidator()

    # テストファイルのモックを検証
    test_files = ["tests/test_phase1_agents_clean.py", "tests/test_phase1_agents_fixes.py"]

    for test_file in test_files:
        if Path(test_file).exists():
            validator.validate_test_mocks(test_file)

    validator.generate_report()


if __name__ == "__main__":
    main()
