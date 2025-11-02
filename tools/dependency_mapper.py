"""
dependency_mapper.py

依存関係マッピングシステム

【目的】
- プロジェクト全体の依存関係を可視化
- 未使用エージェントの特定
- 統合候補の発見
"""

import ast
import logging
from pathlib import Path
from typing import Dict, List
import json

logger = logging.getLogger(__name__)


class DependencyMapper:
    """
    依存関係マッパー
    """

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.dependencies = {}
        self.agents = {}
        self.unused_files = set()

    def scan_project(self):
        """プロジェクト全体をスキャン"""
        logger.info("🔍 プロジェクトスキャン開始...")

        # Python ファイルを検索
        py_files = list(self.project_root.rglob("*.py"))

        # 除外ディレクトリ
        excluded_dirs = {"_ARCHIVE", "_BACKUP", "_WIP", "__pycache__", "venv", ".git"}

        for py_file in py_files:
            # 除外ディレクトリチェック
            if any(excluded in py_file.parts for excluded in excluded_dirs):
                continue

            self._analyze_file(py_file)

        logger.info(f"✅ {len(self.dependencies)}個のファイルを分析")

    def _analyze_file(self, file_path: Path):
        """ファイルを分析"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            imports = set()
            classes = []
            functions = []

            for node in ast.walk(tree):
                # インポート文
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)

                # クラス定義
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)

                # 関数定義
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)

            relative_path = file_path.relative_to(self.project_root)

            self.dependencies[str(relative_path)] = {
                "imports": list(imports),
                "classes": classes,
                "functions": functions,
                "is_agent": "agent" in str(file_path).lower(),
                "size": file_path.stat().st_size,
            }

            # エージェントファイルを記録
            if "agent" in str(file_path).lower():
                self.agents[str(relative_path)] = {
                    "classes": classes,
                    "type": self._classify_agent(file_path, classes),
                }

        except Exception as e:
            logger.debug(f"⚠️ {file_path} 分析エラー: {e}")

    def _classify_agent(self, file_path: Path, classes: List[str]) -> str:
        """エージェントタイプを分類"""
        path_lower = str(file_path).lower()

        if "wordpress" in path_lower or "wp_" in path_lower:
            return "wordpress"
        elif "content" in path_lower or "writer" in path_lower:
            return "content"
        elif "feedback" in path_lower:
            return "feedback"
        elif "self_healing" in path_lower or "retry" in path_lower:
            return "self_healing"
        elif "knowledge" in path_lower:
            return "knowledge_base"
        elif "decision" in path_lower:
            return "decision_support"
        elif "orchestrator" in path_lower:
            return "orchestrator"
        else:
            return "other"

    def find_unused_files(self) -> List[str]:
        """未使用ファイルを検出"""
        all_imports = set()

        for file_info in self.dependencies.values():
            all_imports.update(file_info["imports"])

        unused = []

        for file_path, info in self.dependencies.items():
            # ファイルのモジュール名を生成
            module_name = file_path.replace("/", ".").replace(".py", "")

            # どこからもインポートされていない
            if not any(module_name in imp or imp in module_name for imp in all_imports):
                # メインファイルやテストファイルは除外
                if not any(x in file_path for x in ["__main__", "test_", "_test", "main.py"]):
                    unused.append(file_path)

        self.unused_files = set(unused)
        return unused

    def find_integration_candidates(self) -> Dict[str, List[str]]:
        """統合候補を検出"""
        candidates = {}

        # タイプ別にエージェントをグループ化
        by_type = {}
        for agent_path, info in self.agents.items():
            agent_type = info["type"]
            if agent_type not in by_type:
                by_type[agent_type] = []
            by_type[agent_type].append(agent_path)

        # 同じタイプで複数ある場合は統合候補
        for agent_type, agents in by_type.items():
            if len(agents) > 1:
                candidates[agent_type] = agents

        return candidates

    def generate_report(self, output_file: str = "dependency_report.json"):
        """レポート生成"""
        unused = self.find_unused_files()
        candidates = self.find_integration_candidates()

        report = {
            "summary": {
                "total_files": len(self.dependencies),
                "total_agents": len(self.agents),
                "unused_files": len(unused),
                "integration_candidates": len(candidates),
            },
            "agents_by_type": {},
            "unused_files": list(unused),
            "integration_candidates": candidates,
        }

        # タイプ別集計
        for agent_path, info in self.agents.items():
            agent_type = info["type"]
            if agent_type not in report["agents_by_type"]:
                report["agents_by_type"][agent_type] = []
            report["agents_by_type"][agent_type].append(agent_path)

        # JSON保存
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ レポート生成: {output_file}")

        return report

    def print_summary(self):
        """サマリー表示"""
        unused = self.find_unused_files()
        candidates = self.find_integration_candidates()

        print("\n" + "=" * 80)
        print("📊 依存関係分析サマリー")
        print("=" * 80)
        print(f"  総ファイル数: {len(self.dependencies)}")
        print(f"  エージェント数: {len(self.agents)}")
        print(f"  未使用ファイル: {len(unused)}")
        print(f"  統合候補: {len(candidates)}グループ")

        if candidates:
            print("\n🔀 統合候補:")
            for agent_type, agents in candidates.items():
                print(f"\n  【{agent_type}】 {len(agents)}個")
                for agent in agents[:5]:  # 最初の5個のみ表示
                    print(f"    - {agent}")
                if len(agents) > 5:
                    print(f"    ... 他{len(agents) - 5}個")

        if unused:
            print(f"\n⚠️  未使用ファイル: {len(unused)}個")
            for file in list(unused)[:10]:  # 最初の10個のみ表示
                print(f"    - {file}")
            if len(unused) > 10:
                print(f"    ... 他{len(unused) - 10}個")

        print("=" * 80)


def main():
    """メイン実行"""
    mapper = DependencyMapper()
    mapper.scan_project()
    mapper.print_summary()
    # report = mapper.generate_report()

    print("\n✅ 詳細レポート: dependency_report.json")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
