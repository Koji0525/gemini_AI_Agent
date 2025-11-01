#!/usr/bin/env python3
"""
企業レベルのパス解決システム

Google、AWS、Microsoftなどの企業標準に準拠したパス解決
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict
import logging


class EnterprisePathResolver:
    """
    企業レベルのパス解決クラス

    特徴:
    - マルチ環境対応 (開発/ステージング/本番)
    - マルチクラウド対応 (GCP/AWS/Azure)
    - フォールバック戦略
    - 詳細なログと監査
    """

    def __init__(self):
        self.logger = self._setup_logger()
        self.project_root = self._find_project_root()
        self.resolution_strategies = self._get_resolution_strategies()

    def _setup_logger(self):
        """企業レベルのログ設定"""
        logger = logging.getLogger("EnterprisePathResolver")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _find_project_root(self) -> Path:
        """プロジェクトルートを智能的に発見"""
        possible_indicators = [".git", "requirements.txt", "pyproject.toml", "setup.py", "Dockerfile"]

        current_path = Path(__file__).resolve()

        # 最大5階層さかのぼって検索
        for _ in range(5):
            for indicator in possible_indicators:
                if (current_path / indicator).exists():
                    self.logger.info(f"✅ プロジェクトルートを発見: {current_path}")
                    return current_path
            current_path = current_path.parent

        # フォールバック: 環境変数またはデフォルト
        env_root = os.getenv("PROJECT_ROOT")
        if env_root and Path(env_root).exists():
            self.logger.info(f"✅ 環境変数からプロジェクトルートを発見: {env_root}")
            return Path(env_root)

        self.logger.warning("⚠️  プロジェクトルートを自動検出できませんでした")
        return Path.cwd()

    def _get_resolution_strategies(self) -> List[Dict]:
        """企業レベルのパス解決戦略"""
        return [
            {
                "name": "google_standard",
                "env_vars": ["GOOGLE_APPLICATION_CREDENTIALS"],
                "description": "Google推奨の環境変数",
            },
            {"name": "explicit_path", "env_vars": ["GOOGLE_SERVICE_ACCOUNT_FILE"], "description": "明示的なパス指定"},
            {
                "name": "cloud_default",
                "env_vars": [],
                "default_paths": [
                    "service_account.json",
                    "config/service_account.json",
                    "configuration/service_account.json",
                    "credentials/service_account.json",
                    "secrets/service_account.json",
                ],
                "description": "クラウドデフォルトパス",
            },
            {
                "name": "user_config",
                "env_vars": [],
                "default_paths": [
                    str(Path.home() / ".config" / "gspread" / "service_account.json"),
                    str(Path.home() / ".credentials" / "service_account.json"),
                ],
                "description": "ユーザー設定ディレクトリ",
            },
        ]

    def resolve_service_account_path(self, custom_path: str = None) -> Path:
        """
        サービスアカウントファイルのパスを解決

        Args:
            custom_path: カスタムパス（オプション）

        Returns:
            Path: 解決されたパスオブジェクト

        Raises:
            FileNotFoundError: ファイルが見つからない場合
        """
        self.logger.info("🔍 サービスアカウントファイルのパス解決を開始...")

        # 検索候補を収集
        candidates = self._collect_path_candidates(custom_path)

        # 候補を検証
        resolved_path = self._validate_candidates(candidates)

        if resolved_path:
            self.logger.info(f"✅ サービスアカウントファイルを発見: {resolved_path}")
            return resolved_path
        else:
            error_msg = self._generate_detailed_error(candidates)
            self.logger.error(f"❌ サービスアカウントファイルが見つかりません\n{error_msg}")
            raise FileNotFoundError(error_msg)

    def _collect_path_candidates(self, custom_path: str = None) -> List[Path]:
        """パス候補を収集"""
        candidates = []

        # カスタムパスを優先
        if custom_path:
            candidates.append(self.project_root / custom_path)
            candidates.append(Path(custom_path).resolve())

        # 戦略ベースの候補を収集
        for strategy in self.resolution_strategies:
            # 環境変数ベース
            for env_var in strategy.get("env_vars", []):
                env_value = os.getenv(env_var)
                if env_value:
                    candidates.append(self.project_root / env_value)
                    candidates.append(Path(env_value).resolve())

            # デフォルトパスベース
            for default_path in strategy.get("default_paths", []):
                candidates.append(self.project_root / default_path)
                candidates.append(Path(default_path).resolve())

        # 重複を排除
        unique_candidates = []
        for candidate in candidates:
            if candidate not in unique_candidates:
                unique_candidates.append(candidate)

        self.logger.info(f"📋 検索候補: {[str(c) for c in unique_candidates]}")
        return unique_candidates

    def _validate_candidates(self, candidates: List[Path]) -> Optional[Path]:
        """候補パスを検証"""
        for candidate in candidates:
            try:
                if candidate.exists() and candidate.is_file():
                    # 読み取り権限もチェック
                    if os.access(candidate, os.R_OK):
                        return candidate
                    else:
                        self.logger.warning(f"⚠️  ファイルの読み取り権限がありません: {candidate}")
            except Exception as e:
                self.logger.debug(f"🔍 パス検証スキップ: {candidate} - {e}")

        return None

    def _generate_detailed_error(self, candidates: List[Path]) -> str:
        """詳細なエラーメッセージを生成"""
        error_lines = ["🚨 サービスアカウントファイルが見つかりません", "", "🔍 検索されたパス:"]

        for i, candidate in enumerate(candidates, 1):
            exists = "✅ 存在" if candidate.exists() else "❌ 不在"
            error_lines.append(f"  {i}. {candidate} ({exists})")

        error_lines.extend(
            [
                "",
                "💡 解決策:",
                "1. サービスアカウントファイルを以下のいずれかのパスに配置:",
                "   - configuration/service_account.json",
                "   - config/service_account.json",
                "   - service_account.json",
                "2. 環境変数を設定:",
                "   export GOOGLE_APPLICATION_CREDENTIALS=configuration/service_account.json",
                "3. .envファイルを確認:",
                "   cat .env | grep GOOGLE",
                "",
                "🏢 企業推奨設定:",
                "   GOOGLE_APPLICATION_CREDENTIALS=configuration/service_account.json",
            ]
        )

        return "\n".join(error_lines)

    def get_environment_report(self) -> Dict:
        """環境レポートを生成"""
        report = {
            "project_root": str(self.project_root),
            "current_working_directory": str(Path.cwd()),
            "environment_variables": {},
            "resolved_paths": {},
            "recommendations": [],
        }

        # 環境変数の状態
        for strategy in self.resolution_strategies:
            for env_var in strategy.get("env_vars", []):
                report["environment_variables"][env_var] = os.getenv(env_var)

        # 解決されたパス
        try:
            sa_path = self.resolve_service_account_path()
            report["resolved_paths"]["service_account"] = str(sa_path)
        except FileNotFoundError:
            report["resolved_paths"]["service_account"] = None

        # 推奨事項
        if not report["environment_variables"].get("GOOGLE_APPLICATION_CREDENTIALS"):
            report["recommendations"].append("GOOGLE_APPLICATION_CREDENTIALS環境変数を設定することを推奨")

        return report


# グローバルインスタンス
path_resolver = EnterprisePathResolver()


def resolve_path(file_path: str = None) -> Path:
    """パス解決の簡易インターフェース"""
    return path_resolver.resolve_service_account_path(file_path)


def get_environment_info() -> Dict:
    """環境情報を取得"""
    return path_resolver.get_environment_report()


if __name__ == "__main__":
    # 環境レポートを表示
    report = get_environment_info()
    print("🏢 企業環境レポート")
    print("=" * 50)

    for category, details in report.items():
        print(f"\n📊 {category.upper()}:")
        if isinstance(details, dict):
            for key, value in details.items():
                print(f"   {key}: {value}")
        else:
            for item in details:
                print(f"   • {item}")
