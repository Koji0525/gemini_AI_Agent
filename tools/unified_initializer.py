#!/usr/bin/env python3
"""
統一初期化マネージャー - システム全体の依存性注入を一元管理

引数不一致問題を根本解決するための統一パターン
"""

import os
import inspect
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class InitPattern:
    """初期化パターン定義"""

    class_name: str
    module_path: str
    required_args: List[str]
    optional_args: Dict[str, Any]
    description: str
    version: str = "1.0"


class UnifiedInitializer:
    """統一初期化マネージャー"""

    def __init__(self):
        self.patterns = self._load_standard_patterns()
        self.instance_cache = {}

    def _load_standard_patterns(self) -> Dict[str, InitPattern]:
        """標準的な初期化パターンを定義"""
        return {
            # Google Sheets関連
            "GoogleSheetsManager": InitPattern(
                class_name="GoogleSheetsManager",
                module_path="tools.sheets_manager",
                required_args=["spreadsheet_id"],
                optional_args={"service_account_file": "config/service_account.json"},
                description="Google Sheets操作マネージャー",
            ),
            # ブラウザ制御関連
            "BrowserController": InitPattern(
                class_name="BrowserController",
                module_path="browser_control.browser_controller",
                required_args=[],
                optional_args={"headless": True, "timeout": 30},
                description="ブラウザ自動操作コントローラー",
            ),
            # タスク実行関連
            "TaskExecutor": InitPattern(
                class_name="TaskExecutor",
                module_path="task_executor.task_executor",
                required_args=["sheets_manager", "browser_controller"],
                optional_args={"max_retries": 3, "timeout": 60},
                description="タスク実行オーケストレーター",
            ),
            # エージェント関連
            "DesignAgent": InitPattern(
                class_name="DesignAgent",
                module_path="core_agents.design_agent",
                required_args=["sheets_manager", "browser_controller"],
                optional_args={"model": "gemini-pro"},
                description="設計エージェント",
            ),
            "DevAgent": InitPattern(
                class_name="DevAgent",
                module_path="core_agents.dev_agent",
                required_args=["sheets_manager", "browser_controller"],
                optional_args={"model": "gemini-pro"},
                description="開発エージェント",
            ),
            # WordPress関連
            "WordPressPluginManager": InitPattern(
                class_name="WordPressPluginManager",
                module_path="wordpress.wp_plugin_manager",
                required_args=["browser_controller"],
                optional_args={"timeout": 30},
                description="WordPressプラグイン管理",
            ),
            "WordPressPostEditor": InitPattern(
                class_name="WordPressPostEditor",
                module_path="wordpress.wp_agent",
                required_args=["browser_controller"],
                optional_args={"auto_save": True},
                description="WordPress投稿編集",
            ),
        }

    def get_initialization_code(self, class_name: str, variable_name: str = None) -> str:
        """クラスの正しい初期化コードを生成"""
        if class_name not in self.patterns:
            return f"# ❌ {class_name} の初期化パターンが定義されていません"

        pattern = self.patterns[class_name]
        if not variable_name:
            variable_name = class_name.lower()

        # 必須引数の構築
        required_args = []
        for arg in pattern.required_args:
            if arg == "spreadsheet_id":
                required_args.append('os.getenv("SPREADSHEET_ID")')
            elif arg == "sheets_manager":
                required_args.append('self.get("GoogleSheetsManager")')
            elif arg == "browser_controller":
                required_args.append('self.get("BrowserController")')
            else:
                required_args.append(f'"{arg}_value"')  # プレースホルダー

        # オプション引数の構築
        optional_args = []
        for key, value in pattern.optional_args.items():
            if isinstance(value, str):
                optional_args.append(f'{key}="{value}"')
            else:
                optional_args.append(f"{key}={value}")

        # コード生成
        all_args = required_args + optional_args
        args_str = ", ".join(all_args)

        code = f"{variable_name} = {class_name}({args_str})"

        return code

    def get(self, class_name: str) -> Any:
        """クラスインスタンスを取得（シングルトン風）"""
        if class_name in self.instance_cache:
            return self.instance_cache[class_name]

        if class_name not in self.patterns:
            raise ValueError(f"未定義のクラス: {class_name}")

        pattern = self.patterns[class_name]

        try:
            # 動的インポート
            module = __import__(pattern.module_path, fromlist=[class_name])
            cls = getattr(module, class_name)

            # 引数準備
            kwargs = {}

            # 必須引数
            for arg in pattern.required_args:
                if arg == "spreadsheet_id":
                    kwargs[arg] = os.getenv("SPREADSHEET_ID")
                elif arg in ["sheets_manager", "browser_controller"]:
                    # 依存関係の解決
                    dep_class = "GoogleSheetsManager" if arg == "sheets_manager" else "BrowserController"
                    kwargs[arg] = self.get(dep_class)
                else:
                    # デフォルト値
                    kwargs[arg] = f"default_{arg}"

            # オプション引数
            kwargs.update(pattern.optional_args)

            # インスタンス化
            instance = cls(**kwargs)
            self.instance_cache[class_name] = instance
            return instance

        except Exception as e:
            print(f"❌ {class_name} の初期化失敗: {e}")
            raise

    def validate_initialization(self, file_path: str) -> List[Dict[str, Any]]:
        """ファイル内の初期化コードを検証"""
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")

            for i, line in enumerate(lines):
                line = line.strip()

                # クラス初期化を検出
                for class_name in self.patterns:
                    if f"{class_name}(" in line and "=" in line:
                        pattern = self.patterns[class_name]

                        # 簡易的な引数カウント検証
                        args_part = line.split(f"{class_name}(")[1].split(")")[0]
                        args_count = len([arg for arg in args_part.split(",") if arg.strip()])

                        expected_count = len(pattern.required_args) + len(pattern.optional_args)

                        if args_count != expected_count:
                            issues.append(
                                {
                                    "file": file_path,
                                    "line": i + 1,
                                    "class": class_name,
                                    "issue": f"引数不一致: 期待{expected_count}引数, 実際{args_count}引数",
                                    "expected_args": pattern.required_args + list(pattern.optional_args.keys()),
                                    "code_snippet": line,
                                }
                            )

            return issues

        except Exception as e:
            print(f"❌ 検証エラー {file_path}: {e}")
            return []

    def generate_migration_report(self) -> str:
        """移行レポート生成"""
        report = ["🏗️ 統一初期化移行レポート", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"]

        report.append("📋 定義済み初期化パターン:")
        for class_name, pattern in self.patterns.items():
            report.append(
                f"  ✅ {class_name}: {len(pattern.required_args)}必須 + {len(pattern.optional_args)}オプション"
            )

        report.append("")
        report.append("🚀 推奨初期化コード例:")
        for class_name in ["GoogleSheetsManager", "BrowserController", "TaskExecutor"]:
            code = self.get_initialization_code(class_name)
            report.append(f"  📝 {code}")

        return "\n".join(report)


# グローバルインスタンス
initializer = UnifiedInitializer()


def init(class_name: str, **kwargs) -> Any:
    """統一初期化関数"""
    return initializer.get(class_name)


def get_init_code(class_name: str, var_name: str = None) -> str:
    """初期化コード取得"""
    return initializer.get_initialization_code(class_name, var_name)


def validate_file(file_path: str) -> List[Dict[str, Any]]:
    """ファイル検証"""
    return initializer.validate_initialization(file_path)


if __name__ == "__main__":
    # レポート表示
    print(initializer.generate_migration_report())
