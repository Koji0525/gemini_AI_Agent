#!/usr/bin/env python3
"""
🤖 AI支援型コードリファクタリングツール

覚醒性向上機能:
- コードパターン自動検出
- リファクタリング提案生成
- 安全な修正設定自動作成
- 変更影響自動分析
"""

import ast
import sys
from pathlib import Path
from typing import Any, Dict, List


class AICodeAssistant:
    """AI支援コード改善アシスタント"""

    def analyze_code_quality(self, file_path: Path) -> Dict[str, Any]:
        """コード品質を自動分析"""

        analysis = {"issues": [], "suggestions": [], "refactoring_opportunities": []}

        try:
            code = file_path.read_text(encoding="utf-8")
            tree = ast.parse(code)

            # コードメトリクス分析
            metrics = self._calculate_metrics(tree)

            # 問題パターン検出
            analysis["issues"].extend(self._detect_antipatterns(tree))

            # リファクタリング提案
            analysis["suggestions"].extend(self._suggest_improvements(tree, metrics))

            # 修正設定自動作成
            if analysis["suggestions"]:
                analysis["auto_config"] = self._generate_auto_config(analysis["suggestions"])

            return analysis

        except Exception as e:
            return {"error": f"分析エラー: {e}"}

    def _calculate_metrics(self, tree: ast.AST) -> Dict[str, int]:
        """コードメトリクス計算"""
        try:
            code_str = ast.unparse(tree)
            line_count = len(code_str.split("\n"))
        except:
            code_str = "無法解析"
            line_count = 0

        return {
            "line_count": line_count,
            "class_count": len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
            "function_count": len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
            "complexity": self._calculate_complexity(tree),
        }

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """コード複雑度を計算（簡易版）"""
        complexity = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
        return complexity

    def _detect_antipatterns(self, tree: ast.AST) -> List[str]:
        """アンチパターン検出"""
        antipatterns = []

        # 長いメソッド検出
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # メソッドの行数を概算
                try:
                    method_code = ast.unparse(node)
                    method_lines = len(method_code.split("\n"))
                    if method_lines > 50:  # 50行以上のメソッド
                        antipatterns.append(f"長いメソッド: {node.name} ({method_lines}行)")
                except:
                    pass

        # 重複インポート検出
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                try:
                    import_str = ast.unparse(node)
                    if import_str in imports:
                        antipatterns.append(f"重複インポート: {import_str}")
                    imports.append(import_str)
                except:
                    pass

        return antipatterns

    def _suggest_improvements(self, tree: ast.AST, metrics: Dict) -> List[Dict]:
        """改善提案生成"""
        suggestions = []

        # メソッド分割提案
        if metrics["function_count"] == 0 and metrics["line_count"] > 100:
            suggestions.append(
                {
                    "type": "extract_methods",
                    "description": "長いスクリプトをメソッドに分割",
                    "priority": "high",
                }
            )

        # 型アノテーション提案
        suggestions.append(
            {
                "type": "add_type_annotations",
                "description": "型アノテーションを追加",
                "priority": "medium",
            }
        )

        # 複雑度が高い場合の提案
        if metrics["complexity"] > 10:
            suggestions.append(
                {
                    "type": "reduce_complexity",
                    "description": f"コード複雑度が高い ({metrics['complexity']})",
                    "priority": "medium",
                }
            )

        return suggestions

    def _generate_auto_config(self, suggestions: List[Dict]) -> Dict:
        """自動修正設定を生成"""
        operations = []

        for suggestion in suggestions:
            if suggestion["type"] == "add_type_annotations":
                operations.append({"type": "add_type_annotations", "auto_generate": True})

        return {"file": "auto_detected.py", "operations": operations}


def main():
    """AI支援リファクタリングデモ"""
    assistant = AICodeAssistant()

    if len(sys.argv) > 1:
        target_file = Path(sys.argv[1])
        if target_file.exists():
            analysis = assistant.analyze_code_quality(target_file)

            print("🔍 コード分析結果:")
            print(f"ファイル: {target_file}")

            if "error" in analysis:
                print(f"❌ {analysis['error']}")
                return

            print("\n📋 検出された問題:")
            for issue in analysis.get("issues", []):
                print(f"  ⚠️  {issue}")

            if not analysis.get("issues"):
                print("  ✅ 重大な問題は見つかりませんでした")

            print("\n💡 改善提案:")
            for suggestion in analysis.get("suggestions", []):
                print(f"  ✅ {suggestion['description']} (優先度: {suggestion['priority']})")

            if "auto_config" in analysis:
                print("\n🤖 自動修正設定:")
                import yaml

                print(yaml.dump(analysis["auto_config"], default_flow_style=False))
        else:
            print("❌ ファイルが見つかりません")
    else:
        print("使用方法: python3 ai_assisted_refactor.py <対象ファイル>")


if __name__ == "__main__":
    main()
