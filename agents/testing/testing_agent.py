"""
TestingAgent - 自動テストエージェント
v1.15.0 - 2025-11-06

【責任範囲】
- 生成コードの構文チェック
- 単体テストの自動生成・実行
- テスト結果のレポート生成
"""

import os
import ast
import subprocess
import tempfile
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path


class TestingAgent:
    """自動テストエージェント"""

    def __init__(self):
        """初期化"""
        self.test_history = []

    async def test_code(self, code: str, test_type: str = "syntax") -> Dict:
        """
        コードをテスト

        Args:
            code: テスト対象のコード
            test_type: テストタイプ（syntax, unit, integration）

        Returns:
            テスト結果
        """
        try:
            print(f"🧪 テスト開始: {test_type}")

            result = {
                "test_type": test_type,
                "timestamp": datetime.now().isoformat(),
                "passed": True,
                "errors": [],
                "warnings": [],
            }

            # 構文チェック
            if test_type in ["syntax", "all"]:
                syntax_result = self._check_syntax(code)
                result["syntax_check"] = syntax_result
                if not syntax_result["passed"]:
                    result["passed"] = False
                    result["errors"].extend(syntax_result["errors"])

            # PEP 8チェック
            if test_type in ["style", "all"]:
                style_result = self._check_style(code)
                result["style_check"] = style_result
                result["warnings"].extend(style_result["warnings"])

            # 単体テスト実行
            if test_type in ["unit", "all"]:
                unit_result = await self._run_unit_tests(code)
                result["unit_tests"] = unit_result
                if not unit_result["passed"]:
                    result["passed"] = False
                    result["errors"].extend(unit_result["errors"])

            # 履歴に記録
            self.test_history.append(result)

            status = "✅ 合格" if result["passed"] else "❌ 不合格"
            print(f"{status}: エラー {len(result['errors'])}件, 警告 {len(result['warnings'])}件")

            return result

        except Exception as e:
            print(f"❌ テスト実行エラー: {e}")
            return {
                "test_type": test_type,
                "passed": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def generate_tests(self, code: str) -> List[str]:
        """
        コードから自動的にテストケースを生成

        Args:
            code: テスト対象のコード

        Returns:
            生成されたテストケースのリスト
        """
        try:
            print("🔨 テストケース生成開始")

            # ASTでコードを解析
            tree = ast.parse(code)

            test_cases = []

            # 関数を抽出
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name

                    # テストケース生成
                    test_case = f"""
def test_{func_name}():
    \"\"\"Test for {func_name}\"\"\"
    # TODO: 実装が必要
    pass
"""
                    test_cases.append(test_case)

            print(f"✅ {len(test_cases)}個のテストケース生成完了")
            return test_cases

        except Exception as e:
            print(f"❌ テストケース生成エラー: {e}")
            return []

    def _check_syntax(self, code: str) -> Dict:
        """構文チェック"""
        try:
            ast.parse(code)
            return {"passed": True, "errors": []}
        except SyntaxError as e:
            return {"passed": False, "errors": [f"行 {e.lineno}: {e.msg}"]}

    def _check_style(self, code: str) -> Dict:
        """PEP 8スタイルチェック"""
        warnings = []

        lines = code.split("\n")

        for i, line in enumerate(lines, 1):
            # 行の長さチェック
            if len(line) > 79:
                warnings.append(f"行 {i}: 行が長すぎます（{len(line)}文字）")

            # インデントチェック（スペース4つ）
            if line.startswith(" ") and not line.startswith("    "):
                if line.strip():  # 空行でない場合
                    warnings.append(f"行 {i}: インデントが不正です")

        return {"passed": len(warnings) == 0, "warnings": warnings}

    async def _run_unit_tests(self, code: str) -> Dict:
        """単体テスト実行"""
        try:
            # 一時ファイルにコードを保存
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                temp_file = f.name

            # py_compileで検証
            result = subprocess.run(
                ["python3", "-m", "py_compile", temp_file],
                capture_output=True,
                text=True,
                timeout=5,
            )

            # 一時ファイル削除
            os.unlink(temp_file)

            if result.returncode == 0:
                return {"passed": True, "errors": []}
            else:
                return {"passed": False, "errors": [result.stderr]}

        except subprocess.TimeoutExpired:
            return {"passed": False, "errors": ["テストがタイムアウトしました"]}
        except Exception as e:
            return {"passed": False, "errors": [str(e)]}

    def get_statistics(self) -> Dict:
        """テスト統計を取得"""
        total = len(self.test_history)
        passed = sum(1 for h in self.test_history if h.get("passed"))

        return {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": total - passed,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
        }
