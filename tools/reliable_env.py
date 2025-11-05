"""
確実な環境変数読み込みモジュール
dotenvに依存しない安全な方法
"""

import os
import re
from pathlib import Path
from typing import Dict, Optional


class ReliableEnv:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.env_file = self.project_root / ".env"
        self._cached_env_vars = None

    def load_env_vars(self) -> Dict[str, str]:
        """安全に.envファイルを読み込み"""
        if self._cached_env_vars is not None:
            return self._cached_env_vars

        env_vars = {}

        if not self.env_file.exists():
            print("❌ .envファイルが存在しません")
            return env_vars

        try:
            with open(self.env_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    # = で分割
                    if "=" not in line:
                        continue

                    parts = line.split("=", 1)
                    key = parts[0].strip()
                    value = parts[1].strip()

                    # キーのバリデーション
                    if not key or not re.match(r"^[A-Z_][A-Z0-9_]*$", key):
                        continue

                    # 値をクリーンアップ（引用符を除去）
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    env_vars[key] = value

            self._cached_env_vars = env_vars
            print(f"✅ .envファイルから {len(env_vars)} 件の環境変数を読み込み")
            return env_vars

        except Exception as e:
            print(f"❌ .envファイルの読み込みエラー: {e}")
            return {}

    def get(self, key: str, default: Optional[str] = None) -> str:
        """環境変数を安全に取得"""
        env_vars = self.load_env_vars()
        return env_vars.get(key, os.getenv(key, default))

    def require(self, key: str) -> str:
        """必須環境変数を取得（ない場合はエラー）"""
        value = self.get(key)
        if value is None:
            raise ValueError(f"必須環境変数 {key} が設定されていません")
        return value


# グローバルインスタンス
reliable_env = ReliableEnv()


def get_env(key: str, default: Optional[str] = None) -> str:
    """環境変数を安全に取得（簡易インターフェース）"""
    return reliable_env.get(key, default)


def require_env(key: str) -> str:
    """必須環境変数を取得"""
    return reliable_env.require(key)
