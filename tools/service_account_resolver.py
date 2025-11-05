"""
サービスアカウントファイルを確実に解決するユーティリティ
"""

import os
from typing import Optional


def resolve_service_account_file(provided_path: Optional[str] = None) -> str:
    """
    サービスアカウントファイルを確実に解決する

    Args:
        provided_path: 提供されたパス（オプション）

    Returns:
        サービスアカウントファイルの絶対パス
    """
    # 検索パスのリスト（優先順位順）
    search_paths = []

    # 1. 提供されたパス
    if provided_path:
        search_paths.append(provided_path)
        search_paths.append(os.path.abspath(provided_path))

    # 2. 環境変数から
    env_paths = [
        os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE"),
        os.getenv("SERVICE_ACCOUNT_FILE"),
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
    ]
    search_paths.extend([p for p in env_paths if p])

    # 3. 一般的なパス
    common_paths = [
        "configuration/service_account.json",
        "service_account.json",
        "../configuration/service_account.json",
        "../service_account.json",
        "../../configuration/service_account.json",
        "../../service_account.json",
        "/workspaces/gemini_AI_Agent/configuration/service_account.json",
        "/workspaces/gemini_AI_Agent/service_account.json",
    ]
    search_paths.extend(common_paths)

    # 4. 絶対パスに変換して追加
    absolute_paths = [os.path.abspath(p) for p in search_paths if p]
    search_paths.extend(absolute_paths)

    # 重複を除去
    search_paths = list(dict.fromkeys(search_paths))

    print("🔍 サービスアカウントファイルを検索中...")
    for i, path in enumerate(search_paths, 1):
        if path and os.path.exists(path):
            print(f"✅ パス {i}/{len(search_paths)}: {path} -> 存在します")
            return os.path.abspath(path)
        elif path:
            print(f"  ❌ パス {i}/{len(search_paths)}: {path} -> 存在しません")

    # ファイルが見つからない場合
    error_msg = "❌ サービスアカウントファイルが見つかりません。以下のパスを確認してください:"
    for path in search_paths:
        error_msg += f"\n  - {path}"

    raise FileNotFoundError(error_msg)


def validate_service_account_file(file_path: str) -> bool:
    """
    サービスアカウントファイルを検証する

    Args:
        file_path: ファイルパス

    Returns:
        有効な場合はTrue
    """
    try:
        if not os.path.exists(file_path):
            print(f"❌ ファイルが存在しません: {file_path}")
            return False

        # ファイルサイズチェック
        file_size = os.path.getsize(file_path)
        if file_size < 100:  # 最小サイズ
            print(f"❌ ファイルサイズが小さすぎます: {file_size} bytes")
            return False

        # JSON形式チェック
        import json

        with open(file_path, "r") as f:
            content = json.load(f)

        # 必須フィールドのチェック
        required_fields = ["type", "project_id", "private_key_id", "private_key", "client_email"]
        for field in required_fields:
            if field not in content:
                print(f"❌ 必須フィールド '{field}' が見つかりません")
                return False

        print(f"✅ サービスアカウントファイルが有効です: {file_path}")
        return True

    except json.JSONDecodeError:
        print(f"❌ JSON形式が無効です: {file_path}")
        return False
    except Exception as e:
        print(f"❌ ファイル検証エラー: {e}")
        return False


# テストコード
if __name__ == "__main__":
    print("🧪 サービスアカウント解決テスト")
    try:
        resolved_path = resolve_service_account_file()
        print(f"✅ 解決されたパス: {resolved_path}")

        if validate_service_account_file(resolved_path):
            print("🎉 サービスアカウントファイルは有効です")
        else:
            print("❌ サービスアカウントファイルが無効です")

    except FileNotFoundError as e:
        print(e)
