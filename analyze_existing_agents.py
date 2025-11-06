#!/usr/bin/env python3
"""
🔍 既存エージェント分析ツール
目的: 24時間稼働システムに統合可能なエージェントを特定
"""

import os
import ast
from pathlib import Path
from typing import Dict, List


class AgentAnalyzer:
    def __init__(self):
        self.agents = []
        self.categories = {
            "学習系": [],
            "実行系": [],
            "監視系": [],
            "Git系": [],
            "スプレッドシート系": [],
            "ブラウザ系": [],
            "WordPress系": [],
            "統合系": [],
        }

    def analyze_file(self, filepath: Path) -> Dict:
        """ファイルを解析してエージェント情報を抽出"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content)

            classes = []
            functions = []
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    if node.name.startswith("_"):
                        continue
                    functions.append(node.name)
                elif isinstance(node, ast.Import):
                    imports.extend([alias.name for alias in node.names])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            # 行数カウント
            lines = len(content.split("\n"))

            return {
                "path": str(filepath),
                "name": filepath.stem,
                "classes": classes,
                "functions": functions,
                "imports": imports,
                "lines": lines,
                "has_async": "async def" in content,
                "has_sheets": any("sheets" in imp.lower() for imp in imports),
                "has_browser": any(
                    "playwright" in imp.lower() or "selenium" in imp.lower() for imp in imports
                ),
                "has_git": any("git" in imp.lower() for imp in imports),
                "has_rag": any("rag" in imp.lower() for imp in imports),
                "has_knowledge": any("knowledge" in imp.lower() for imp in imports),
            }
        except Exception as e:
            return None

    def scan_directory(self, base_path: Path):
        """ディレクトリをスキャン"""
        for py_file in base_path.rglob("*.py"):
            # 除外パターン
            if any(
                exclude in str(py_file)
                for exclude in ["_BACKUP", "_ARCHIVE", "__pycache__", "test_", ".venv"]
            ):
                continue

            info = self.analyze_file(py_file)
            if info and info["classes"]:  # クラスを持つファイルのみ
                self.agents.append(info)

    def categorize_agents(self):
        """エージェントをカテゴリ分け"""
        for agent in self.agents:
            name_lower = agent["name"].lower()

            if any(
                kw in name_lower
                for kw in ["knowledge", "learning", "rag", "pattern", "log_integrator"]
            ):
                self.categories["学習系"].append(agent)

            if any(kw in name_lower for kw in ["executor", "task"]):
                self.categories["実行系"].append(agent)

            if any(kw in name_lower for kw in ["monitor", "health", "diagnostic"]):
                self.categories["監視系"].append(agent)

            if agent["has_git"]:
                self.categories["Git系"].append(agent)

            if agent["has_sheets"]:
                self.categories["スプレッドシート系"].append(agent)

            if agent["has_browser"]:
                self.categories["ブラウザ系"].append(agent)

            if "wordpress" in name_lower or "wp_" in name_lower:
                self.categories["WordPress系"].append(agent)

            if any(kw in name_lower for kw in ["orchestrator", "pipeline", "coordinator"]):
                self.categories["統合系"].append(agent)

    def generate_report(self) -> str:
        """レポート生成"""
        report = []
        report.append("=" * 80)
        report.append("🔍 既存エージェント分析レポート")
        report.append("=" * 80)
        report.append(f"\n📊 総エージェント数: {len(self.agents)}件\n")

        for category, agents in self.categories.items():
            if not agents:
                continue

            report.append(f"\n{'='*60}")
            report.append(f"📁 {category} ({len(agents)}件)")
            report.append("=" * 60)

            for agent in sorted(agents, key=lambda x: x["lines"], reverse=True):
                report.append(f"\n✅ {agent['name']}")
                report.append(f"   パス: {agent['path']}")
                report.append(f"   行数: {agent['lines']}行")
                report.append(f"   クラス: {', '.join(agent['classes'][:3])}")

                features = []
                if agent["has_async"]:
                    features.append("非同期")
                if agent["has_sheets"]:
                    features.append("スプレッドシート")
                if agent["has_browser"]:
                    features.append("ブラウザ")
                if agent["has_git"]:
                    features.append("Git")
                if agent["has_rag"]:
                    features.append("RAG")
                if agent["has_knowledge"]:
                    features.append("ナレッジ")

                if features:
                    report.append(f"   機能: {', '.join(features)}")

        report.append("\n" + "=" * 80)
        report.append("🎯 24時間稼働システム統合候補")
        report.append("=" * 80)

        # 統合候補の提案
        high_priority = []
        for agent in self.agents:
            score = 0
            reasons = []

            # 学習系は高優先度
            if agent["has_rag"] or agent["has_knowledge"]:
                score += 3
                reasons.append("学習機能")

            # 非同期対応は高優先度
            if agent["has_async"]:
                score += 2
                reasons.append("非同期対応")

            # 統合系は高優先度
            if any(kw in agent["name"].lower() for kw in ["orchestrator", "pipeline"]):
                score += 3
                reasons.append("統合機能")

            # 行数が適切（500-2000行）
            if 500 <= agent["lines"] <= 2000:
                score += 1
                reasons.append("適切なサイズ")

            if score >= 3:
                high_priority.append({"agent": agent, "score": score, "reasons": reasons})

        for item in sorted(high_priority, key=lambda x: x["score"], reverse=True)[:10]:
            agent = item["agent"]
            report.append(f"\n🌟 優先度: {item['score']}/10")
            report.append(f"   名前: {agent['name']}")
            report.append(f"   理由: {', '.join(item['reasons'])}")
            report.append(f"   パス: {agent['path']}")

        return "\n".join(report)


if __name__ == "__main__":
    analyzer = AgentAnalyzer()

    # プロジェクトルートをスキャン
    project_root = Path("/workspaces/gemini_AI_Agent")
    print("🔍 エージェントをスキャン中...")
    analyzer.scan_directory(project_root)

    print("📊 カテゴリ分類中...")
    analyzer.categorize_agents()

    # レポート生成
    report = analyzer.generate_report()
    print(report)

    # ファイルに保存
    output_path = project_root / "docs" / "agent_analysis_report.md"
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n✅ レポート保存: {output_path}")
