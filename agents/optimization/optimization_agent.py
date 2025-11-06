"""
OptimizationAgent - パフォーマンス最適化

機能:
1. ボトルネック自動検出
2. 改善提案の生成
3. 自動最適化の適用
4. パフォーマンステスト
"""

import ast
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import asyncio


class OptimizationAgent:
    """パフォーマンス最適化エージェント"""

    def __init__(self, knowledge_path: str = "mvp_v4/knowledge/learned"):
        """
        初期化

        Args:
            knowledge_path: ナレッジ保存先パス
        """
        self.knowledge_path = knowledge_path
        self.optimization_rules = self._load_optimization_rules()
        self.performance_data = []

    def _load_optimization_rules(self) -> List[Dict[str, Any]]:
        """最適化ルールを読み込み"""
        return [
            {
                "rule_id": "avoid_nested_loops",
                "pattern": "nested_for_loops",
                "severity": "high",
                "suggestion": "リスト内包表記やnumpyの使用を検討",
            },
            {
                "rule_id": "use_generators",
                "pattern": "large_list_creation",
                "severity": "medium",
                "suggestion": "大量データの場合はジェネレータを使用",
            },
            {
                "rule_id": "cache_expensive_calls",
                "pattern": "repeated_function_calls",
                "severity": "high",
                "suggestion": "@functools.lru_cache を使用",
            },
            {
                "rule_id": "async_io_operations",
                "pattern": "blocking_io",
                "severity": "high",
                "suggestion": "I/O操作は非同期処理に変更",
            },
            {
                "rule_id": "optimize_database_queries",
                "pattern": "n_plus_one_queries",
                "severity": "critical",
                "suggestion": "クエリの一括実行やJOINの使用",
            },
        ]

    async def analyze_code_performance(self, file_path: str) -> Dict[str, Any]:
        """
        コードのパフォーマンスを分析

        Args:
            file_path: 解析対象ファイル

        Returns:
            分析結果とボトルネック情報
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source)

            bottlenecks = []

            # ネストしたループの検出
            nested_loops = self._detect_nested_loops(tree)
            if nested_loops:
                bottlenecks.append(
                    {
                        "type": "nested_loops",
                        "severity": "high",
                        "locations": nested_loops,
                        "suggestion": "リスト内包表記やnumpyの使用を検討",
                    }
                )

            # 同期的なI/O操作の検出
            blocking_io = self._detect_blocking_io(tree)
            if blocking_io:
                bottlenecks.append(
                    {
                        "type": "blocking_io",
                        "severity": "high",
                        "locations": blocking_io,
                        "suggestion": "asyncioを使用した非同期処理に変更",
                    }
                )

            # 大量のオブジェクト生成の検出
            large_creations = self._detect_large_object_creation(tree)
            if large_creations:
                bottlenecks.append(
                    {
                        "type": "large_object_creation",
                        "severity": "medium",
                        "locations": large_creations,
                        "suggestion": "ジェネレータやイテレータの使用を検討",
                    }
                )

            result = {
                "file_path": file_path,
                "analyzed_at": datetime.now().isoformat(),
                "bottlenecks": bottlenecks,
                "optimization_score": self._calculate_score(bottlenecks),
            }

            return result

        except Exception as e:
            return {
                "file_path": file_path,
                "error": str(e),
                "analyzed_at": datetime.now().isoformat(),
            }

    def _detect_nested_loops(self, tree: ast.AST) -> List[int]:
        """ネストしたループを検出"""
        nested_loops = []

        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # 内部にさらにForループがあるか確認
                for child in ast.walk(node):
                    if child != node and isinstance(child, ast.For):
                        nested_loops.append(node.lineno)
                        break

        return nested_loops

    def _detect_blocking_io(self, tree: ast.AST) -> List[int]:
        """ブロッキングI/O操作を検出"""
        blocking_calls = []
        blocking_functions = ["open", "read", "write", "requests.get", "requests.post"]

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_function_name(node.func)
                if any(bf in func_name for bf in blocking_functions):
                    # async/awaitコンテキスト内でない場合
                    if not self._is_in_async_context(tree, node):
                        blocking_calls.append(node.lineno)

        return blocking_calls

    def _detect_large_object_creation(self, tree: ast.AST) -> List[int]:
        """大量のオブジェクト生成を検出"""
        large_creations = []

        for node in ast.walk(tree):
            # 大きなリスト内包表記
            if isinstance(node, ast.ListComp):
                # rangeの引数が大きい場合
                for generator in node.generators:
                    if isinstance(generator.iter, ast.Call):
                        if self._get_function_name(generator.iter.func) == "range":
                            if generator.iter.args and isinstance(
                                generator.iter.args[0], ast.Constant
                            ):
                                if generator.iter.args[0].value > 10000:
                                    large_creations.append(node.lineno)

        return large_creations

    def _get_function_name(self, node) -> str:
        """関数名を取得"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_function_name(node.value)}.{node.attr}"
        return ""

    def _is_in_async_context(self, tree: ast.AST, target_node: ast.AST) -> bool:
        """ノードがasyncコンテキスト内にあるか確認"""
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                for child in ast.walk(node):
                    if child == target_node:
                        return True
        return False

    def _calculate_score(self, bottlenecks: List[Dict]) -> float:
        """最適化スコアを計算（0-100）"""
        if not bottlenecks:
            return 100.0

        severity_weights = {"critical": 30, "high": 20, "medium": 10, "low": 5}

        total_penalty = sum(severity_weights.get(b["severity"], 5) for b in bottlenecks)
        score = max(0, 100 - total_penalty)

        return score

    async def benchmark_function(
        self, func: Callable, args: tuple = (), kwargs: dict = None, iterations: int = 100
    ) -> Dict[str, Any]:
        """
        関数のベンチマーク実行

        Args:
            func: ベンチマーク対象関数
            args: 位置引数
            kwargs: キーワード引数
            iterations: 実行回数

        Returns:
            ベンチマーク結果
        """
        kwargs = kwargs or {}
        times = []

        for _ in range(iterations):
            start_time = time.perf_counter()

            if asyncio.iscoroutinefunction(func):
                await func(*args, **kwargs)
            else:
                func(*args, **kwargs)

            end_time = time.perf_counter()
            times.append(end_time - start_time)

        result = {
            "function": func.__name__,
            "iterations": iterations,
            "avg_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "total_time": sum(times),
            "benchmarked_at": datetime.now().isoformat(),
        }

        return result

    async def generate_optimization_report(
        self, project_path: str, output_path: str = "MD/system_docs/optimization_report.md"
    ) -> str:
        """
        最適化レポートを生成

        Args:
            project_path: プロジェクトルートパス
            output_path: 出力先パス

        Returns:
            レポート内容
        """
        python_files = list(Path(project_path).rglob("*.py"))

        all_analyses = []
        for py_file in python_files:
            if "__pycache__" not in str(py_file):
                analysis = await self.analyze_code_performance(str(py_file))
                if "error" not in analysis:
                    all_analyses.append(analysis)

        # レポート生成
        report = self._build_optimization_report(all_analyses)

        # ファイル出力
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)

        return report

    def _build_optimization_report(self, analyses: List[Dict]) -> str:
        """最適化レポートを構築"""
        total_bottlenecks = sum(len(a.get("bottlenecks", [])) for a in analyses)
        avg_score = (
            sum(a.get("optimization_score", 0) for a in analyses) / len(analyses) if analyses else 0
        )

        report = f"""# パフォーマンス最適化レポート

**生成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 サマリー

- 解析ファイル数: {len(analyses)}
- 検出されたボトルネック: {total_bottlenecks}件
- 平均最適化スコア: {avg_score:.1f}/100

## 🎯 優先度別ボトルネック

"""

        # 重要度でグループ化
        critical_issues = []
        high_issues = []
        medium_issues = []

        for analysis in analyses:
            for bottleneck in analysis.get("bottlenecks", []):
                issue = {
                    "file": analysis["file_path"],
                    "type": bottleneck["type"],
                    "severity": bottleneck["severity"],
                    "suggestion": bottleneck["suggestion"],
                    "locations": bottleneck.get("locations", []),
                }

                if bottleneck["severity"] == "critical":
                    critical_issues.append(issue)
                elif bottleneck["severity"] == "high":
                    high_issues.append(issue)
                elif bottleneck["severity"] == "medium":
                    medium_issues.append(issue)

        # クリティカル
        if critical_issues:
            report += f"### 🚨 クリティカル ({len(critical_issues)}件)\n\n"
            for issue in critical_issues:
                report += f"- **{issue['file']}** (行: {', '.join(map(str, issue['locations']))})\n"
                report += f"  - 問題: {issue['type']}\n"
                report += f"  - 推奨: {issue['suggestion']}\n\n"

        # 高優先度
        if high_issues:
            report += f"### ⚠️ 高優先度 ({len(high_issues)}件)\n\n"
            for issue in high_issues:
                report += f"- **{issue['file']}** (行: {', '.join(map(str, issue['locations']))})\n"
                report += f"  - 問題: {issue['type']}\n"
                report += f"  - 推奨: {issue['suggestion']}\n\n"

        # 中優先度
        if medium_issues:
            report += f"### ℹ️ 中優先度 ({len(medium_issues)}件)\n\n"
            for issue in medium_issues:
                report += f"- **{issue['file']}** (行: {', '.join(map(str, issue['locations']))})\n"
                report += f"  - 問題: {issue['type']}\n"
                report += f"  - 推奨: {issue['suggestion']}\n\n"

        report += "\n## 📈 ファイル別スコア\n\n"
        for analysis in sorted(analyses, key=lambda x: x.get("optimization_score", 0)):
            score = analysis.get("optimization_score", 0)
            file_path = os.path.basename(analysis["file_path"])
            report += f"- {file_path}: {score:.1f}/100\n"

        return report

    async def save_knowledge(self, event: str, details: Dict[str, Any]) -> bool:
        """
        ナレッジベースに登録

        Args:
            event: イベント名
            details: 詳細情報

        Returns:
            成功/失敗
        """
        try:
            knowledge_file = f"{self.knowledge_path}/auto_registered_knowledge.json"

            # 既存データ読み込み
            if os.path.exists(knowledge_file):
                with open(knowledge_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {"knowledge_base": [], "total_entries": 0, "last_updated": None}

            # 新規エントリ追加
            entry = {
                "event": event,
                "details": details,
                "timestamp": datetime.now().isoformat(),
                "agent": "OptimizationAgent",
            }

            data["knowledge_base"].append(entry)
            data["total_entries"] = len(data["knowledge_base"])
            data["last_updated"] = datetime.now().isoformat()

            # 保存
            os.makedirs(os.path.dirname(knowledge_file), exist_ok=True)
            with open(knowledge_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"❌ ナレッジ登録失敗: {e}")
            return False

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        タスク実行（統一インターフェース）

        Args:
            task: タスク情報

        Returns:
            実行結果
        """
        task_type = task.get("type")

        if task_type == "analyze":
            file_path = task.get("file_path")
            result = await self.analyze_code_performance(file_path)

            if result.get("bottlenecks"):
                await self.save_knowledge("bottlenecks_detected", result)

            return {"status": "success", "analysis": result}

        elif task_type == "benchmark":
            # ベンチマーク実行（実装は呼び出し側で準備）
            return {"status": "success", "message": "Benchmark requires function object"}

        elif task_type == "generate_report":
            project_path = task.get("project_path", ".")
            output_path = task.get("output_path", "MD/system_docs/optimization_report.md")
            report = await self.generate_optimization_report(project_path, output_path)

            await self.save_knowledge(
                "optimization_report_generated",
                {"project_path": project_path, "output_path": output_path},
            )

            return {"status": "success", "report": report}

        else:
            return {"status": "error", "message": f"Unknown task type: {task_type}"}
