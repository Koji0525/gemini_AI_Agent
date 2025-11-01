#!/usr/bin/env python3
"""統一環境変数ローダー"""

import os
from pathlib import Path
from dotenv import load_dotenv


class EnvLoader:
    """環境変数を確実に読み込む"""

    _loaded = False

    @classmethod
    def load(cls):
        """環境変数を読み込み（1回のみ）"""
        if cls._loaded:
            return

        # プロジェクトルートの.envを読み込み
        project_root = Path(__file__).parent.parent
        env_path = project_root / ".env"

        if env_path.exists():
            load_dotenv(env_path)
            cls._loaded = True
            print(f"✅ .env読み込み: {env_path}")
        else:
            raise FileNotFoundError(f".envが見つかりません: {env_path}")

    @classmethod
    def get(cls, key: str, default=None):
        """環境変数取得（自動ロード）"""
        if not cls._loaded:
            cls.load()

        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"環境変数 {key} が設定されていません")

        return value


# 自動ロード
EnvLoader.load()
