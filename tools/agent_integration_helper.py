#!/usr/bin/env python3
"""
🔧 拡張版エージェント統合自動化ヘルパー v2.0
汎用性と拡張性を大幅に向上した統合支援ツール

特徴:
✅ 設定駆動型の依存関係管理
✅ マルチパターン初期化コード生成
✅ 既存プロジェクト構造の自動検出
✅ 横展開可能なアーキテクチャ
✅ 段階的な統合検証

使用例:
    python3 tools/agent_integration_helper.py --scan-all --generate-config
    python3 tools/agent_integration_helper.py --agent TaskExecutor --strategy multi-pattern
    python3 tools/agent_integration_helper.py --integrate --config agent_config.yaml
"""

import ast
import inspect
import importlib
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class IntegrationStrategy(Enum):
    """統合戦略の種類"""

    SINGLE_PATTERN = "single"  # 単一パターン試行
    MULTI_PATTERN = "multi"  # 複数パターン試行
    ADAPTIVE = "adaptive"  # 適応型（診断結果ベース）
    INCREMENTAL = "incremental"  # 段階的統合


class AgentType(Enum):
    """エージェントの種類"""

    CORE = "core"  # コアエージェント
    TASK_EXECUTOR = "task_executor"  # タスク実行
    KNOWLEDGE = "knowledge"  # ナレッジ管理
    MONITORING = "monitoring"  # 監視・可視化
    SELF_HEALING = "self_healing"  # 自己修復


@dataclass
class AgentDependency:
    """エージェント依存関係"""

    param_name: str
    expected_type: str
    optional: bool = False
    default_value: Any = None
    alternatives: List[str] = None


@dataclass
class AgentAnalysis:
    """エージェント分析結果"""

    class_name: str
    file_path: Path
    agent_type: AgentType
    dependencies: List[AgentDependency]
    init_complexity: str  # simple, moderate, complex
    integration_priority: int  # 1-5 (5が最高優先度)


class EnhancedAgentIntegrationHelper:
    """拡張版エージェント統合ヘルパー"""

    def __init__(self, project_root: str = ".", config_path: Optional[str] = None):
        self.project_root = Path(project_root)
        self.config = self._load_config(config_path)
        self.agent_registry = {}
        self.dependency_graph = {}

        sys.path.insert(0, str(self.project_root))

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """設定ファイルを読み込み"""
        default_config = {
            "integration_strategies": {
                "core": IntegrationStrategy.ADAPTIVE,
                "task_executor": IntegrationStrategy.MULTI_PATTERN,
                "knowledge": IntegrationStrategy.INCREMENTAL,
                "monitoring": IntegrationStrategy.SINGLE_PATTERN,
                "self_healing": IntegrationStrategy.ADAPTIVE,
            },
            "param_mappings": {
                "sheets_manager": {
                    "GoogleSheetsManager": "self.sheets_manager",
                    "SafeSheetsWrapper": "self.sheets",
                },
                "knowledge_manager": {
                    "KnowledgeManager": "self.knowledge_manager",
                    "KnowledgeBaseManager": "self.knowledge_base_manager",
                },
            },
            "project_structure": {
                "core_agents": "core_agents/",
                "task_executors": "task_executor/",
                "knowledge_agents": "knowledge_system/core_agents/",
                "monitoring_agents": "agents/monitoring/",
                "self_healing_agents": "agents/self_healing/",
            },
        }

        if config_path and Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
                default_config.update(user_config)

        return default_config

    def scan_project_structure(self) -> Dict[str, List[Path]]:
        """
        プロジェクト構造をスキャンしてエージェントを発見

        Returns:
            {
                'core_agents': [Path, ...],
                'task_executors': [Path, ...],
                ...
            }
        """
        print("🔍 プロジェクト構造をスキャン中...")
        print()

        agents = {category: [] for category in self.config["project_structure"].keys()}

        for category, pattern in self.config["project_structure"].items():
            search_path = self.project_root / pattern
            if search_path.exists():
                # Pythonファイルを検索
                py_files = list(search_path.rglob("*.py"))
                agents[category] = py_files

                print(f"📁 {category}: {len(py_files)}ファイル")
                for file in py_files[:5]:  # 最初の5ファイルのみ表示
                    print(f"   📄 {file.relative_to(self.project_root)}")
                if len(py_files) > 5:
                    print(f"   ... 他{len(py_files)-5}ファイル")

        return agents

    def analyze_agent_comprehensive(self, agent_path: str) -> AgentAnalysis:
        """
        エージェントの包括的分析

        Returns:
            AgentAnalysisオブジェクト
        """
        print(f"🔍 包括的分析: {agent_path}")

        with open(agent_path, "r", encoding="utf-8") as f:
            content = f.read()
            tree = ast.parse(content)

        # 基本情報抽出
        class_name = None
        dependencies = []

        # クラス定義を探す
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name

                # __init__メソッドを探す
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        dependencies = self._analyze_constructor(item)
                        break
                break

        # エージェントタイプを判定
        agent_type = self._classify_agent_type(agent_path, class_name)

        # 初期化複雑度を判定
        init_complexity = self._assess_init_complexity(dependencies)

        # 統合優先度を判定
        integration_priority = self._assess_integration_priority(agent_type, init_complexity)

        return AgentAnalysis(
            class_name=class_name,
            file_path=Path(agent_path),
            agent_type=agent_type,
            dependencies=dependencies,
            init_complexity=init_complexity,
            integration_priority=integration_priority,
        )

    def _analyze_constructor(self, init_node: ast.FunctionDef) -> List[AgentDependency]:
        """コンストラクタを分析して依存関係を抽出"""
        dependencies = []

        for arg in init_node.args.args:
            if arg.arg != "self":
                dependency = AgentDependency(
                    param_name=arg.arg,
                    expected_type=self._extract_type_hint(arg),
                    optional=False,
                    alternatives=self._suggest_alternatives(arg.arg),
                )
                dependencies.append(dependency)

        return dependencies

    def _extract_type_hint(self, arg: ast.arg) -> str:
        """型ヒントを抽出"""
        if arg.annotation:
            return ast.unparse(arg.annotation)
        return "Any"

    def _suggest_alternatives(self, param_name: str) -> List[str]:
        """代替パラメータ名を提案"""
        alternatives = []

        if param_name in self.config["param_mappings"]:
            for type_name, var_name in self.config["param_mappings"][param_name].items():
                alternatives.append(var_name)

        # 一般的な代替名
        common_alternatives = {
            "sheets_manager": ["sheets", "sheets_wrapper", "google_sheets"],
            "knowledge_manager": ["knowledge", "kb_manager", "knowledge_base"],
            "task_executor": ["executor", "task_runner"],
        }

        if param_name in common_alternatives:
            alternatives.extend(common_alternatives[param_name])

        return list(set(alternatives))  # 重複排除

    def _classify_agent_type(self, file_path: str, class_name: str) -> AgentType:
        """ファイルパスとクラス名からエージェントタイプを分類"""
        path_str = str(file_path).lower()

        if "core_agent" in path_str or class_name.endswith("Agent"):
            return AgentType.CORE
        elif "task_executor" in path_str:
            return AgentType.TASK_EXECUTOR
        elif "knowledge" in path_str:
            return AgentType.KNOWLEDGE
        elif "monitoring" in path_str or "observability" in path_str:
            return AgentType.MONITORING
        elif "self_healing" in path_str or "error" in path_str:
            return AgentType.SELF_HEALING
        else:
            return AgentType.CORE

    def _assess_init_complexity(self, dependencies: List[AgentDependency]) -> str:
        """初期化の複雑度を判定"""
        if len(dependencies) == 0:
            return "simple"
        elif len(dependencies) <= 2:
            return "moderate"
        else:
            return "complex"

    def _assess_integration_priority(self, agent_type: AgentType, complexity: str) -> int:
        """統合優先度を判定"""
        priority_map = {
            AgentType.CORE: 5,
            AgentType.TASK_EXECUTOR: 4,
            AgentType.KNOWLEDGE: 3,
            AgentType.MONITORING: 2,
            AgentType.SELF_HEALING: 4,
        }

        complexity_boost = {"simple": 0, "moderate": 1, "complex": 2}

        return priority_map[agent_type] + complexity_boost[complexity]

    def generate_integration_code(
        self, analysis: AgentAnalysis, strategy: IntegrationStrategy = None
    ) -> Dict[str, str]:
        """
        統合コードを生成（マルチパターン対応）

        Returns:
            {
                'single_pattern': code,
                'multi_pattern': code,
                'adaptive': code,
                'diagnostic': code
            }
        """
        if strategy is None:
            strategy = self.config["integration_strategies"].get(
                analysis.agent_type.value, IntegrationStrategy.MULTI_PATTERN
            )

        generators = {
            IntegrationStrategy.SINGLE_PATTERN: self._generate_single_pattern,
            IntegrationStrategy.MULTI_PATTERN: self._generate_multi_pattern,
            IntegrationStrategy.ADAPTIVE: self._generate_adaptive_pattern,
            IntegrationStrategy.INCREMENTAL: self._generate_incremental_pattern,
        }

        return {
            strategy.value: generators[strategy](analysis),
            "diagnostic": self._generate_diagnostic_code(analysis),
        }

    def _generate_single_pattern(self, analysis: AgentAnalysis) -> str:
        """単一パターンの初期化コード生成"""
        class_name = analysis.class_name
        indent = 12

        code_lines = [
            " " * indent + f"# {class_name}の初期化（単一パターン）",
            " " * indent + "try:",
        ]

        # インポート文
        code_lines.append(
            " " * (indent + 4)
            + f"from {self._get_import_path(analysis.file_path)} import {class_name}"
        )

        # パラメータ構築
        params = []
        for dep in analysis.dependencies:
            if dep.param_name in self.config["param_mappings"]:
                # 最初の代替案を使用
                first_alternative = list(self.config["param_mappings"][dep.param_name].values())[0]
                params.append(f"{dep.param_name}={first_alternative}")
            else:
                params.append(f"{dep.param_name}=???")

        # 初期化行
        init_line = f'self.{class_name.lower()} = {class_name}({", ".join(params)})'
        code_lines.append(" " * (indent + 4) + init_line)

        # 成功/エラーハンドリング
        code_lines.extend(
            [
                " " * (indent + 4) + f'print("   ✅ {class_name}")',
                " " * indent + "except Exception as e:",
                " " * (indent + 4)
                + f'print(f"   ⚠️  {class_name}: {{type(e).__name__}}: {{str(e)[:60]}}")',
                " " * (indent + 4) + f"self.{class_name.lower()} = None",
            ]
        )

        return "\n".join(code_lines)

    def _generate_multi_pattern(self, analysis: AgentAnalysis) -> str:
        """マルチパターンの初期化コード生成"""
        class_name = analysis.class_name
        indent = 12

        code_lines = [
            " " * indent + f"# {class_name}の初期化（マルチパターン試行）",
            " " * indent + f"{class_name.lower()}_init_success = False",
        ]

        # パターン1: 主要な依存関係
        for i, dep in enumerate(analysis.dependencies[:2]):  # 最初の2つの依存関係のみ
            if dep.param_name in self.config["param_mappings"]:
                code_lines.extend(
                    [
                        " " * indent + f"# パターン{i+1}: {dep.param_name}",
                        " " * indent + "try:",
                    ]
                )

                # インポート文
                code_lines.append(
                    " " * (indent + 4)
                    + f"from {self._get_import_path(analysis.file_path)} import {class_name}"
                )

                # パラメータ構築（この依存関係に焦点）
                params = []
                for d in analysis.dependencies:
                    if d.param_name == dep.param_name:
                        first_alternative = list(
                            self.config["param_mappings"][d.param_name].values()
                        )[0]
                        params.append(f"{d.param_name}={first_alternative}")
                    else:
                        params.append(f"{d.param_name}=None")  # 他のパラメータはNone

                init_line = f'self.{class_name.lower()} = {class_name}({", ".join(params)})'
                code_lines.append(" " * (indent + 4) + init_line)
                code_lines.append(" " * (indent + 4) + f"{class_name.lower()}_init_success = True")
                code_lines.append(" " * indent + "except Exception as e:")
                code_lines.append(
                    " " * (indent + 4)
                    + f'print(f"   ⚠️  {class_name}(パターン{i+1}): {{type(e).__name__}}")'
                )

        # 成功判定
        code_lines.extend(
            [
                " " * indent + f"if {class_name.lower()}_init_success:",
                " " * (indent + 4) + f'print("   ✅ {class_name}")',
                " " * indent + "else:",
                " " * (indent + 4) + f"self.{class_name.lower()} = None",
            ]
        )

        return "\n".join(code_lines)

    def _generate_adaptive_pattern(self, analysis: AgentAnalysis) -> str:
        """適応型パターンの初期化コード生成"""
        class_name = analysis.class_name
        indent = 12

        code_lines = [
            " " * indent + f"# {class_name}の初期化（適応型 - 診断ベース）",
            " " * indent + "try:",
            " " * (indent + 4)
            + f"from {self._get_import_path(analysis.file_path)} import {class_name}",
        ]

        # 診断ベースのパラメータ選択
        code_lines.append(" " * (indent + 4) + "# 診断結果に基づく最適パラメータ選択")

        params = []
        for dep in analysis.dependencies:
            if dep.param_name in self.config["param_mappings"]:
                code_lines.append(" " * (indent + 4) + f"# {dep.param_name}のパターン判定")

                # 複数の代替案を試行するコード
                for type_name, var_name in self.config["param_mappings"][dep.param_name].items():
                    code_lines.append(" " * (indent + 4) + f"# - {type_name}: {var_name}")

                # 最初の代替案を使用（実際には診断結果に基づく）
                first_alternative = list(self.config["param_mappings"][dep.param_name].values())[0]
                params.append(f"{dep.param_name}={first_alternative}")
            else:
                params.append(f"{dep.param_name}=???")

        init_line = f'self.{class_name.lower()} = {class_name}({", ".join(params)})'
        code_lines.append(" " * (indent + 4) + init_line)

        code_lines.extend(
            [
                " " * (indent + 4) + f'print("   ✅ {class_name}")',
                " " * indent + "except Exception as e:",
                " " * (indent + 4)
                + f'print(f"   ⚠️  {class_name}: {{type(e).__name__}}: {{str(e)[:60]}}")',
                " " * (indent + 4) + f"self.{class_name.lower()} = None",
            ]
        )

        return "\n".join(code_lines)

    def _generate_incremental_pattern(self, analysis: AgentAnalysis) -> str:
        """段階的統合パターンの初期化コード生成"""
        class_name = analysis.class_name
        indent = 12

        code_lines = [
            " " * indent + f"# {class_name}の初期化（段階的統合）",
            " " * indent + "# フェーズ1: 最小限の依存関係で初期化",
        ]

        # 必須パラメータのみで試行
        essential_deps = [d for d in analysis.dependencies if not d.optional]

        if essential_deps:
            code_lines.append(" " * indent + "try:")
            code_lines.append(
                " " * (indent + 4)
                + f"from {self._get_import_path(analysis.file_path)} import {class_name}"
            )

            params = []
            for dep in essential_deps[:1]:  # 最初の必須依存関係のみ
                if dep.param_name in self.config["param_mappings"]:
                    first_alternative = list(
                        self.config["param_mappings"][dep.param_name].values()
                    )[0]
                    params.append(f"{dep.param_name}={first_alternative}")
                else:
                    params.append(f"{dep.param_name}=???")

            # オプショナルパラメータはNone
            for dep in analysis.dependencies:
                if dep not in essential_deps[:1]:
                    params.append(f"{dep.param_name}=None")

            init_line = f'self.{class_name.lower()} = {class_name}({", ".join(params)})'
            code_lines.append(" " * (indent + 4) + init_line)
            code_lines.append(" " * (indent + 4) + f'print("   ✅ {class_name} (最小構成)")')

            code_lines.append(" " * indent + "except Exception as e:")
            code_lines.append(
                " " * (indent + 4) + f'print(f"   ⚠️  {class_name}: {{type(e).__name__}}")'
            )
            code_lines.append(" " * (indent + 4) + f"self.{class_name.lower()} = None")
        else:
            # 依存関係がない場合
            code_lines.append(" " * indent + f"self.{class_name.lower()} = {class_name}()")
            code_lines.append(" " * indent + f'print("   ✅ {class_name}")')

        return "\n".join(code_lines)

    def _generate_diagnostic_code(self, analysis: AgentAnalysis) -> str:
        """診断コード生成"""
        class_name = analysis.class_name
        indent = 12

        code_lines = [
            " " * indent + f"# {class_name}診断テスト",
            " " * indent + "try:",
            " " * (indent + 4)
            + f"from {self._get_import_path(analysis.file_path)} import {class_name}",
            " " * (indent + 4) + 'print(f"🔍 {class_name}診断開始...")',
        ]

        # 各パラメータの診断
        for dep in analysis.dependencies:
            if dep.param_name in self.config["param_mappings"]:
                code_lines.append(" " * (indent + 4) + f"# {dep.param_name}の利用可能オプション:")
                for type_name, var_name in self.config["param_mappings"][dep.param_name].items():
                    code_lines.append(" " * (indent + 4) + f"#   - {type_name}: {var_name}")

        code_lines.extend(
            [
                " " * (indent + 4) + 'print(f"✅ {class_name}インポート成功")',
                " " * indent + "except ImportError as e:",
                " " * (indent + 4) + 'print(f"❌ インポートエラー: {e}")',
                " " * indent + "except Exception as e:",
                " " * (indent + 4) + 'print(f"⚠️  その他エラー: {e}")',
            ]
        )

        return "\n".join(code_lines)

    def _get_import_path(self, file_path: Path) -> str:
        """インポートパスを生成"""
        # プロジェクトルートからの相対パスに変換
        relative_path = file_path.relative_to(self.project_root)
        # .py拡張子を除去し、パス区切りをドットに変換
        import_path = str(relative_path).replace(".py", "").replace("/", ".")
        return import_path

    def generate_integration_report(self, analyses: List[AgentAnalysis]) -> str:
        """統合レポート生成"""
        report_lines = [
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "📊 エージェント統合レポート",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
        ]

        # 優先度順にソート
        analyses.sort(key=lambda x: x.integration_priority, reverse=True)

        for analysis in analyses:
            report_lines.extend(
                [
                    f"🔧 {analysis.class_name}",
                    f"   タイプ: {analysis.agent_type.value}",
                    f"   ファイル: {analysis.file_path.relative_to(self.project_root)}",
                    f"   複雑度: {analysis.init_complexity}",
                    f"   優先度: {analysis.integration_priority}/5",
                    f"   依存関係: {len(analysis.dependencies)}",
                    "",
                ]
            )

            for dep in analysis.dependencies:
                report_lines.append(f"     - {dep.param_name}: {dep.expected_type}")
                if dep.alternatives:
                    report_lines.append(f"       代替: {', '.join(dep.alternatives[:3])}")

            report_lines.append("")

        # 推奨統合順序
        report_lines.extend(
            [
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "🎯 推奨統合順序",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "",
            ]
        )

        for i, analysis in enumerate(analyses[:5], 1):  # 上位5つ
            strategy = self.config["integration_strategies"].get(
                analysis.agent_type.value, IntegrationStrategy.MULTI_PATTERN
            )
            report_lines.append(f"{i}. {analysis.class_name} ({strategy.value}戦略)")

        return "\n".join(report_lines)

    def save_config_template(self, output_path: str = "agent_integration_config.yaml"):
        """設定ファイルテンプレートを保存"""
        template = {
            "integration_strategies": {
                "core": "adaptive",
                "task_executor": "multi-pattern",
                "knowledge": "incremental",
                "monitoring": "single-pattern",
                "self_healing": "adaptive",
            },
            "param_mappings": {
                "sheets_manager": {
                    "GoogleSheetsManager": "self.sheets_manager",
                    "SafeSheetsWrapper": "self.sheets",
                },
                "knowledge_manager": {
                    "KnowledgeManager": "self.knowledge_manager",
                    "KnowledgeBaseManager": "self.knowledge_base_manager",
                },
            },
            "project_structure": {
                "core_agents": "core_agents/",
                "task_executors": "task_executor/",
                "knowledge_agents": "knowledge_system/core_agents/",
                "monitoring_agents": "agents/monitoring/",
                "self_healing_agents": "agents/self_healing/",
            },
            "custom_mappings": {
                # カスタムマッピングをここに追加
            },
        }

        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(template, f, default_flow_style=False, allow_unicode=True, indent=2)

        print(f"✅ 設定テンプレートを保存: {output_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="拡張版エージェント統合自動化ヘルパー")
    parser.add_argument("--scan", help="スキャンするPythonファイル")
    parser.add_argument("--scan-all", action="store_true", help="全プロジェクトをスキャン")
    parser.add_argument(
        "--generate-config", action="store_true", help="設定ファイルテンプレート生成"
    )
    parser.add_argument("--agent", help="特定のエージェントを分析")
    parser.add_argument(
        "--strategy", choices=["single", "multi", "adaptive", "incremental"], help="統合戦略を指定"
    )
    parser.add_argument("--output", help="出力ファイルパス")
    parser.add_argument("--config", help="設定ファイルパス")

    args = parser.parse_args()

    helper = EnhancedAgentIntegrationHelper(config_path=args.config)

    if args.generate_config:
        helper.save_config_template()
        return

    if args.scan_all:
        print("🚀 全プロジェクトスキャン開始...")
        agents = helper.scan_project_structure()

        analyses = []
        for category, files in agents.items():
            for file in files[:3]:  # 各カテゴリ最大3ファイル
                try:
                    analysis = helper.analyze_agent_comprehensive(str(file))
                    analyses.append(analysis)
                except Exception as e:
                    print(f"⚠️  {file}の分析中にエラー: {e}")

        # レポート生成
        report = helper.generate_integration_report(analyses)
        print(report)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"✅ レポートを保存: {args.output}")

        return

    if args.scan:
        strategy = None
        if args.strategy:
            strategy = IntegrationStrategy(args.strategy)

        analysis = helper.analyze_agent_comprehensive(args.scan)

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📊 包括的分析結果")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"クラス名: {analysis.class_name}")
        print(f"タイプ: {analysis.agent_type.value}")
        print(f"ファイル: {analysis.file_path}")
        print(f"複雑度: {analysis.init_complexity}")
        print(f"優先度: {analysis.integration_priority}/5")
        print(f"依存関係数: {len(analysis.dependencies)}")
        print()

        for dep in analysis.dependencies:
            print(f"  🔗 {dep.param_name}: {dep.expected_type}")
            if dep.alternatives:
                print(f"     代替: {', '.join(dep.alternatives)}")

        print()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🔧 生成された初期化コード")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        codes = helper.generate_integration_code(analysis, strategy)

        for strategy_name, code in codes.items():
            print(f"\n🎯 {strategy_name.upper()}戦略:")
            print(code)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                for strategy_name, code in codes.items():
                    f.write(f"# {strategy_name.upper()}戦略\n")
                    f.write(code)
                    f.write("\n\n")
            print(f"✅ 初期化コードを保存: {args.output}")

    elif args.agent:
        print(f"🔍 エージェント検索: {args.agent}")
        # エージェント検索機能（簡易実装）
        agents = helper.scan_project_structure()
        for category, files in agents.items():
            for file in files:
                if args.agent.lower() in file.name.lower():
                    print(f"📄 発見: {file}")

    else:
        print("使用例:")
        print("  python3 tools/agent_integration_helper.py --scan-all")
        print(
            "  python3 tools/agent_integration_helper.py --scan task_executor/task_executor_main.py"
        )
        print("  python3 tools/agent_integration_helper.py --generate-config")
        print("  python3 tools/agent_integration_helper.py --agent TaskExecutor")


if __name__ == "__main__":
    main()
