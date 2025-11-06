"""
APIキー保護ツール
v1.15.0 - 2025-11-06

【機能】
- APIキーのマスキング表示
- 環境変数の安全な管理
- キー漏洩の事前チェック
"""

import os
import re
from pathlib import Path
from typing import Dict, List


class ApiKeyProtector:
    """APIキー保護クラス"""

    # 危険なパターン
    SENSITIVE_PATTERNS = [
        r"AIzaSy[0-9A-Za-z_-]{33}",  # Gemini API Key
        r"sk-[0-9A-Za-z]{48}",  # OpenAI API Key
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",  # UUID
    ]

    @staticmethod
    def mask_key(api_key: str, visible_chars: int = 5) -> str:
        """
        APIキーをマスキング表示

        Args:
            api_key: APIキー
            visible_chars: 表示する文字数

        Returns:
            マスキングされたキー
        """
        if not api_key or len(api_key) < visible_chars:
            return "*" * 10

        return f"{api_key[:visible_chars]}{'*' * (len(api_key) - visible_chars)}"

    @staticmethod
    def check_file_for_secrets(file_path: Path) -> List[Dict]:
        """
        ファイル内のAPIキーをチェック

        Args:
            file_path: チェック対象ファイル

        Returns:
            発見されたシークレット情報のリスト
        """
        if not file_path.exists():
            return []

        findings = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

                for i, pattern in enumerate(ApiKeyProtector.SENSITIVE_PATTERNS, 1):
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        findings.append(
                            {
                                "file": str(file_path),
                                "pattern_type": f"Pattern_{i}",
                                "matched_text": ApiKeyProtector.mask_key(match.group()),
                                "position": match.start(),
                            }
                        )
        except Exception as e:
            print(f"⚠️ ファイル読み込みエラー: {e}")

        return findings

    @staticmethod
    def scan_project(project_root: Path, exclude_dirs: List[str] = None) -> Dict:
        """
        プロジェクト全体をスキャン

        Args:
            project_root: プロジェクトルート
            exclude_dirs: 除外ディレクトリ

        Returns:
            スキャン結果
        """
        if exclude_dirs is None:
            exclude_dirs = [".git", "__pycache__", "node_modules", ".venv", "venv"]

        all_findings = []
        scanned_files = 0

        for file_path in project_root.rglob("*"):
            # 除外ディレクトリをスキップ
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue

            # ファイルのみ処理
            if not file_path.is_file():
                continue

            # テキストファイルのみ
            if file_path.suffix not in [".py", ".js", ".json", ".txt", ".md", ".sh", ".env"]:
                continue

            scanned_files += 1
            findings = ApiKeyProtector.check_file_for_secrets(file_path)
            all_findings.extend(findings)

        return {
            "scanned_files": scanned_files,
            "total_findings": len(all_findings),
            "findings": all_findings,
        }

    @staticmethod
    def validate_env_file(env_path: Path = Path(".env")) -> bool:
        """
        .envファイルの安全性を検証

        Args:
            env_path: .envファイルのパス

        Returns:
            安全かどうか
        """
        if not env_path.exists():
            print("⚠️ .env ファイルが存在しません")
            return True

        findings = ApiKeyProtector.check_file_for_secrets(env_path)

        if findings:
            print(f"⚠️ .env に {len(findings)} 個のAPIキーパターンが検出されました")
            print("   これは正常です（.envは.gitignoreに含まれているべき）")
            return True

        return True


def main():
    """メイン実行"""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔒 APIキー保護スキャン")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    protector = ApiKeyProtector()

    # プロジェクトスキャン
    project_root = Path.cwd()
    result = protector.scan_project(project_root)

    print(f"\n📊 スキャン結果:")
    print(f"  スキャンファイル数: {result['scanned_files']}")
    print(f"  検出数: {result['total_findings']}")

    if result["total_findings"] > 0:
        print("\n⚠️  以下のファイルにAPIキーパターンが検出されました:")
        for finding in result["findings"]:
            print(f"  - {finding['file']}")
            print(f"    検出: {finding['matched_text']}")

        print("\n🚨 重要: これらのファイルが .gitignore に含まれているか確認してください")
    else:
        print("\n✅ コード内にAPIキーパターンは検出されませんでした")

    # .env検証
    print("\n" + "=" * 60)
    protector.validate_env_file()


if __name__ == "__main__":
    main()
