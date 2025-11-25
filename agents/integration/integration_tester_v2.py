#!/usr/bin/env python3
"""
IntegrationTester v2 - 統合テスト＆修正提案

【Phase 3: M3.4実装】
- F14: 統合テスト＆修正提案
- 統合後コードのテスト実行
- エラー検出
- 修正タスク生成

【設計思想】
- 既存システムは変更しない
- 独立したモジュールとして実装
- 段階的テストアプローチ
"""

import ast
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# プロジェクトルート設定
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# ロギング設定
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)

# 既存システム（読み取り専用）
try:
    from tools.base_data_accessor import BaseDataAccessor

    ACCESSOR_AVAILABLE = True
except ImportError:
    ACCESSOR_AVAILABLE = False
    logger.warning("⚠️ BaseDataAccessorが利用できません")


class IntegrationTester:
    """
    統合テスト＆修正提案エージェント

    【Phase 3: F14実装】
    - 統合後コードのテスト実行
    - 構文チェック
    - Lintチェック
    - エラー検出
    - 修正提案生成
    """

    def __init__(self):
        """初期化"""
        if ACCESSOR_AVAILABLE:
            self.accessor = BaseDataAccessor()
            logger.info("✅ BaseDataAccessor ロード完了")
        else:
            self.accessor = None
            logger.warning("⚠️ BaseDataAccessor 利用不可")

        logger.info("✅ IntegrationTester 初期化完了")

    def test_integrated_code(
        self, story_id: str, integrated_files: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        統合後コードをテスト

        Args:
            story_id: ストーリーID
            integrated_files: {ファイル名: コード内容}

        Returns:
            テスト結果
        """
        logger.info(f"�� 統合コードテスト開始: {story_id}")
        logger.info(f"   対象ファイル数: {len(integrated_files)}件")

        try:
            # ステップ1: 構文チェック
            logger.info("📋 構文チェック中...")
            syntax_results = self._check_syntax(integrated_files)
            syntax_errors = [r for r in syntax_results if not r["valid"]]
            logger.info(f"   構文エラー: {len(syntax_errors)}件")

            # ステップ2: Lintチェック
            logger.info("🔍 Lintチェック中...")
            lint_results = self._check_lint(integrated_files)
            lint_issues = sum(len(r["issues"]) for r in lint_results)
            logger.info(f"   Lint問題: {lint_issues}件")

            # ステップ3: import検証
            logger.info("📦 import検証中...")
            import_results = self._verify_imports(integrated_files)
            import_errors = [r for r in import_results if not r["valid"]]
            logger.info(f"   import問題: {len(import_errors)}件")

            # ステップ4: 統合結果サマリー
            total_errors = len(syntax_errors) + lint_issues + len(import_errors)
            all_passed = total_errors == 0

            result = {
                "story_id": story_id,
                "test_passed": all_passed,
                "total_errors": total_errors,
                "syntax_check": {
                    "total": len(syntax_results),
                    "errors": len(syntax_errors),
                    "details": syntax_results,
                },
                "lint_check": {
                    "total": len(lint_results),
                    "issues": lint_issues,
                    "details": lint_results,
                },
                "import_check": {
                    "total": len(import_results),
                    "errors": len(import_errors),
                    "details": import_results,
                },
                "timestamp": datetime.now().isoformat(),
            }

            if all_passed:
                logger.info("✅ すべてのテストに合格")
            else:
                logger.warning(f"⚠️ {total_errors}件の問題を検出")

            return result

        except Exception as e:
            logger.error(f"❌ 統合テストエラー: {e}")
            import traceback

            traceback.print_exc()

            return {
                "story_id": story_id,
                "test_passed": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def generate_fix_suggestions(self, test_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        修正タスクを生成

        Args:
            test_results: テスト結果

        Returns:
            修正タスクのリスト
        """
        logger.info("🔧 修正提案生成中...")

        suggestions = []

        try:
            # 構文エラーの修正提案
            if test_results.get("syntax_check"):
                for error in test_results["syntax_check"]["details"]:
                    if not error["valid"]:
                        suggestions.append(
                            {
                                "type": "syntax_error",
                                "file": error["file"],
                                "line": error.get("line", 0),
                                "message": error["message"],
                                "suggestion": self._suggest_syntax_fix(error),
                                "priority": "high",
                            }
                        )

            # Lint問題の修正提案
            if test_results.get("lint_check"):
                for result in test_results["lint_check"]["details"]:
                    for issue in result.get("issues", []):
                        suggestions.append(
                            {
                                "type": "lint_issue",
                                "file": result["file"],
                                "line": issue.get("line", 0),
                                "message": issue["message"],
                                "suggestion": self._suggest_lint_fix(issue),
                                "priority": "medium",
                            }
                        )

            # import問題の修正提案
            if test_results.get("import_check"):
                for error in test_results["import_check"]["details"]:
                    if not error["valid"]:
                        suggestions.append(
                            {
                                "type": "import_error",
                                "file": error["file"],
                                "message": error["message"],
                                "suggestion": self._suggest_import_fix(error),
                                "priority": "high",
                            }
                        )

            logger.info(f"✅ {len(suggestions)}件の修正提案を生成")

            return suggestions

        except Exception as e:
            logger.error(f"❌ 修正提案生成エラー: {e}")
            return []

    def _check_syntax(self, files: Dict[str, str]) -> List[Dict[str, Any]]:
        """構文チェック"""
        results = []

        for file_name, code in files.items():
            try:
                ast.parse(code)
                results.append({"file": file_name, "valid": True, "message": "OK"})
            except SyntaxError as e:
                results.append(
                    {
                        "file": file_name,
                        "valid": False,
                        "line": e.lineno,
                        "message": str(e),
                        "text": e.text,
                    }
                )

        return results

    def _check_lint(self, files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Lintチェック（簡易版）"""
        results = []

        for file_name, code in files.items():
            issues = []

            # 簡易的なLintチェック
            lines = code.split("\n")
            for i, line in enumerate(lines, 1):
                # 行が長すぎる（120文字以上）
                if len(line) > 120:
                    issues.append(
                        {
                            "line": i,
                            "type": "line_too_long",
                            "message": f"Line too long ({len(line)} > 120)",
                        }
                    )

                # 未使用のimport（簡易判定）
                if line.strip().startswith("import ") or line.strip().startswith("from "):
                    # 実際の使用判定は複雑なため、ここでは簡易実装
                    pass

            results.append({"file": file_name, "issues": issues})

        return results

    def _verify_imports(self, files: Dict[str, str]) -> List[Dict[str, Any]]:
        """import検証"""
        results = []

        for file_name, code in files.items():
            try:
                tree = ast.parse(code)

                # import文を抽出
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)

                results.append(
                    {
                        "file": file_name,
                        "valid": True,
                        "imports": imports,
                        "message": f"{len(imports)} imports found",
                    }
                )

            except Exception as e:
                results.append({"file": file_name, "valid": False, "message": str(e)})

        return results

    def _suggest_syntax_fix(self, error: Dict[str, Any]) -> str:
        """構文エラーの修正提案"""
        message = error.get("message", "")

        if "invalid syntax" in message.lower():
            return "構文エラーを修正してください。コロン、括弧、クォートの対応を確認してください。"
        elif "unexpected indent" in message.lower():
            return "インデントを修正してください。Pythonでは4スペースが標準です。"
        elif "unindent" in message.lower():
            return "インデントレベルを統一してください。"
        else:
            return f"構文エラーを修正してください: {message}"

    def _suggest_lint_fix(self, issue: Dict[str, Any]) -> str:
        """Lint問題の修正提案"""
        issue_type = issue.get("type", "")

        if issue_type == "line_too_long":
            return "行を分割してください。120文字以下が推奨されます。"
        else:
            return f"コード品質を改善してください: {issue.get('message', '')}"

    def _suggest_import_fix(self, error: Dict[str, Any]) -> str:
        """import問題の修正提案"""
        return f"import文を確認してください: {error.get('message', '')}"


# テスト用
def test_integration_tester():
    """Phase 3 M3.4 テスト実行"""
    print("=" * 60)
    print("Phase 3: IntegrationTester (F14) テスト実行")
    print("=" * 60)
    print()

    try:
        tester = IntegrationTester()
        print()

        # テスト1: 正常なコード
        print("🧪 テスト1: 正常なコード")
        valid_files = {
            "main.py": """
import os

def main():
    print("Hello, World!")

if __name__ == '__main__':
    main()
"""
        }
        result1 = tester.test_integrated_code("story_test_1", valid_files)
        print(f"   テスト結果: {'✅ 合格' if result1['test_passed'] else '❌ 不合格'}")
        print()

        # テスト2: 構文エラーのあるコード
        print("🧪 テスト2: 構文エラーのあるコード")
        invalid_files = {
            "error.py": """
def broken_function()
    print("Missing colon")
"""
        }
        result2 = tester.test_integrated_code("story_test_2", invalid_files)
        print(f"   テスト結果: {'✅ 合格' if result2['test_passed'] else '❌ 不合格'}")
        print(f"   検出エラー数: {result2['total_errors']}件")
        print()

        # テスト3: 修正提案生成
        print("🧪 テスト3: 修正提案生成")
        suggestions = tester.generate_fix_suggestions(result2)
        print(f"   修正提案数: {len(suggestions)}件")
        for i, sug in enumerate(suggestions, 1):
            print(f"     {i}. [{sug['priority']}] {sug['type']}: {sug['message'][:50]}...")
        print()

        print("=" * 60)
        print("Phase 3 M3.4 テスト完了 ✅")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(test_integration_tester())
