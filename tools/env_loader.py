"""
環境変数読み込みの標準化ツール
v1.15.1 - 2025-11-06

【機能】
- .envファイルを常に優先
- 古い環境変数を自動クリア
- APIキーの基本検証
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv


class StandardEnvLoader:
    """標準環境変数ローダー"""

    SENSITIVE_KEYS = [
        "GEMINI_API_KEY",
        "OPENAI_API_KEY",
        "GOOGLE_API_KEY",
    ]

    @staticmethod
    def load(env_file: str = ".env", force_reload: bool = True) -> dict:
        """
        環境変数を標準的な方法で読み込む

        Args:
            env_file: .envファイルのパス
            force_reload: 既存の環境変数を上書きするか

        Returns:
            読み込んだ環境変数の辞書
        """
        env_path = Path(env_file)

        if not env_path.exists():
            print(f"⚠️  {env_file} が見つかりません")
            return {}

        # 機密情報の環境変数を事前にクリア
        if force_reload:
            for key in StandardEnvLoader.SENSITIVE_KEYS:
                if key in os.environ:
                    del os.environ[key]

        # .envを読み込み（必ず上書き）
        load_dotenv(env_path, override=True)

        # 読み込んだ環境変数を返す
        loaded_vars = {}
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    loaded_vars[key] = value

        return loaded_vars

    @staticmethod
    def verify_api_key(key_name: str = "GEMINI_API_KEY") -> bool:
        """
        APIキーの有効性を基本検証

        Args:
            key_name: 検証するキーの名前

        Returns:
            有効かどうか
        """
        api_key = os.getenv(key_name)

        if not api_key:
            print(f"❌ {key_name} が設定されていません")
            return False

        # 基本的なフォーマットチェックのみ（漏洩キーはチェックしない）
        if len(api_key) < 10:
            print(f"❌ {key_name} の形式が不正です（短すぎます）")
            return False

        if " " in api_key:
            print(f"❌ {key_name} に空白文字が含まれています")
            return False

        print(f"✅ {key_name}: {api_key[:8]}... (形式チェック合格)")
        return True

    @staticmethod
    def load_and_verify(env_file: str = ".env") -> bool:
        """
        読み込みと基本検証を同時実行

        Args:
            env_file: .envファイルのパス

        Returns:
            成功したかどうか
        """
        print("🔄 環境変数を読み込み中...")

        loaded = StandardEnvLoader.load(env_file)

        if not loaded:
            print("❌ 環境変数の読み込みに失敗")
            return False

        print(f"✅ {len(loaded)} 個の環境変数を読み込みました")

        # APIキーの基本検証（漏洩チェックなし）
        return StandardEnvLoader.verify_api_key()


def main():
    """メイン実行"""
    success = StandardEnvLoader.load_and_verify()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
