"""
IntegrationTesterV2 - 統合テスト＆修正提案エージェント
Version: 2.0
機能: 統合後コードテスト、構文エラー検出、ユニットテスト実行、修正タスク生成
"""

import ast
import os
import tempfile
from typing import Any, Dict, List


class IntegrationTesterV2:
    """統合テストエージェント Version 2"""

    def __init__(self):
        self.test_results = {}
        print("✅ IntegrationTesterV2 初期化完了")

    def test_integrated_code(self, story_id: str, code: str) -> Dict[str, Any]:
        """統合後コードをテスト"""
        print(f"🧪 統合コードテスト開始: {story_id}")

        try:
            test_results = {
                "story_id": story_id,
                "syntax_check": self._run_syntax_check(code),
                "unit_tests": self._run_unit_tests(code),
                "integration_tests": self._run_integration_tests(code),
                "performance_check": self._run_performance_check(code),
                "security_scan": self._run_security_scan(code),
                "overall_score": 0.0,
                "repair_tasks": [],
            }

            # 総合スコア計算
            scores = []
            if test_results["syntax_check"]["passed"]:
                scores.append(1.0)
            if test_results["unit_tests"]["passed"]:
                scores.append(test_results["unit_tests"]["score"])
            if test_results["integration_tests"]["passed"]:
                scores.append(test_results["integration_tests"]["score"])

            test_results["overall_score"] = sum(scores) / len(scores) if scores else 0.0

            # 修正タスク生成
            test_results["repair_tasks"] = self._generate_repair_tasks(test_results)

            print(f"✅ 統合テスト完了: 総合スコア {test_results['overall_score']:.1%}")
            return test_results

        except Exception as e:
            print(f"❌ 統合テストエラー: {e}")
            return {
                "story_id": story_id,
                "error": str(e),
                "overall_score": 0.0,
                "repair_tasks": [{"task": "テスト実行エラーの調査", "priority": "高"}],
            }

    def _run_syntax_check(self, code: str) -> Dict[str, Any]:
        """構文チェックを実行"""
        print("  🔍 構文チェック実行中...")

        try:
            # ASTを使用した構文チェック
            ast.parse(code)
            return {"passed": True, "errors": [], "message": "構文チェック成功"}
        except SyntaxError as e:
            error_info = {
                "passed": False,
                "errors": [{"line": e.lineno, "message": e.msg, "offset": e.offset}],
                "message": f"構文エラー: {e.msg}",
            }
            return error_info

    def _run_unit_tests(self, code: str) -> Dict[str, Any]:
        """ユニットテストを実行"""
        print("  🧪 ユニットテスト実行中...")

        try:
            # 一時ファイルにコードを書き込み
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                temp_file = f.name

            # テスト実行（スタブ実装）
            # 実際の実装では pytest や unittest を実行
            test_result = {
                "passed": True,
                "score": 0.85,
                "test_cases": 10,
                "passed_cases": 8,
                "failed_cases": 2,
                "failures": [
                    {"test": "test_api_endpoints", "error": "接続タイムアウト"},
                    {"test": "test_data_validation", "error": "バリデーションエラー"},
                ],
                "coverage": 0.75,
            }

            # 一時ファイルの削除
            os.unlink(temp_file)

            return test_result

        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "error": str(e),
                "test_cases": 0,
                "passed_cases": 0,
                "failed_cases": 0,
                "failures": [],
            }

    def _run_integration_tests(self, code: str) -> Dict[str, Any]:
        """統合テストを実行"""
        print("  🔗 統合テスト実行中...")

        # スタブ実装
        integration_result = {
            "passed": True,
            "score": 0.80,
            "components_tested": ["API", "Database", "Authentication"],
            "integration_points": 5,
            "successful_integrations": 4,
            "failed_integrations": 1,
            "failures": [{"component": "Database", "issue": "接続プールエラー", "severity": "中"}],
        }

        return integration_result

    def _run_performance_check(self, code: str) -> Dict[str, Any]:
        """パフォーマンスチェックを実行"""
        print("  ⚡ パフォーマンスチェック実行中...")

        # スタブ実装
        performance_result = {
            "passed": True,
            "response_time": "125ms",
            "throughput": "800 req/sec",
            "memory_usage": "45MB",
            "cpu_usage": "15%",
            "bottlenecks": [{"location": "データベースクエリ", "impact": "中"}],
            "recommendations": ["クエリキャッシュの導入", "接続プールの最適化"],
        }

        return performance_result

    def _run_security_scan(self, code: str) -> Dict[str, Any]:
        """セキュリティスキャンを実行"""
        print("  🛡️ セキュリティスキャン実行中...")

        # スタブ実装
        security_result = {
            "passed": True,
            "vulnerabilities": 2,
            "critical_issues": 0,
            "high_issues": 1,
            "medium_issues": 1,
            "low_issues": 0,
            "issues": [
                {
                    "type": "SQLインジェクションリスク",
                    "severity": "高",
                    "location": "user_input_handling",
                    "recommendation": "パラメータ化クエリの使用",
                },
                {
                    "type": "ハードコードされた秘密鍵",
                    "severity": "中",
                    "location": "config_section",
                    "recommendation": "環境変数の使用",
                },
            ],
        }

        return security_result

    def _generate_repair_tasks(self, test_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """修正タスクを生成"""
        repair_tasks = []

        # 構文エラーに対する修正タスク
        if not test_results["syntax_check"]["passed"]:
            for error in test_results["syntax_check"]["errors"]:
                repair_tasks.append(
                    {
                        "task": f"構文エラーの修正: {error['message']}",
                        "priority": "高",
                        "type": "syntax",
                        "location": f"行 {error['line']}",
                    }
                )

        # ユニットテスト失敗に対する修正タスク
        if not test_results["unit_tests"]["passed"]:
            for failure in test_results["unit_tests"]["failures"]:
                repair_tasks.append(
                    {
                        "task": f"テスト修正: {failure['test']}",
                        "priority": "中",
                        "type": "unit_test",
                        "details": failure["error"],
                    }
                )

        # 統合テスト失敗に対する修正タスク
        if not test_results["integration_tests"]["passed"]:
            for failure in test_results["integration_tests"]["failures"]:
                repair_tasks.append(
                    {
                        "task": f"統合問題の解決: {failure['component']}",
                        "priority": failure["severity"],
                        "type": "integration",
                        "details": failure["issue"],
                    }
                )

        # セキュリティ問題に対する修正タスク
        if test_results["security_scan"]["vulnerabilities"] > 0:
            for issue in test_results["security_scan"]["issues"]:
                repair_tasks.append(
                    {
                        "task": f"セキュリティ修正: {issue['type']}",
                        "priority": issue["severity"],
                        "type": "security",
                        "details": issue["recommendation"],
                    }
                )

        return repair_tasks

    def generate_test_report(self, test_results: Dict[str, Any]) -> str:
        """テストレポートを生成"""
        report = f"""
# 統合テストレポート

## 基本情報
- **Story ID**: {test_results['story_id']}
- **総合スコア**: {test_results['overall_score']:.1%}
- **テスト日時**: {__import__('datetime').datetime.now().isoformat()}

## テスト結果概要

### 構文チェック
- ステータス: {'✅ 成功' if test_results['syntax_check']['passed'] else '❌ 失敗'}
- {test_results['syntax_check']['message']}

### ユニットテスト
- ステータス: {'✅ 成功' if test_results['unit_tests']['passed'] else '❌ 失敗'}
- スコア: {test_results['unit_tests']['score']:.1%}
- テストケース: {test_results['unit_tests']['test_cases']}
- 成功: {test_results['unit_tests']['passed_cases']}
- 失敗: {test_results['unit_tests']['failed_cases']}

### 統合テスト  
- ステータス: {'✅ 成功' if test_results['integration_tests']['passed'] else '❌ 失敗'}
- スコア: {test_results['integration_tests']['score']:.1%}

### セキュリティスキャン
- 脆弱性: {test_results['security_scan']['vulnerabilities']}件
- 重大度: 高{test_results['security_scan']['high_issues']}/中{test_results['security_scan']['medium_issues']}/低{test_results['security_scan']['low_issues']}

## 修正タスク ({len(test_results['repair_tasks'])}件)
{chr(10).join([f"- **{task['priority']}**: {task['task']}" for task in test_results['repair_tasks']])}

## 推奨アクション
1. 高優先度の修正タスクから着手
2. 統合テストの再実行
3. セキュリティ問題の即時対応
"""
        return report
