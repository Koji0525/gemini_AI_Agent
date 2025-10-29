"""
.env設定を統一 - GoogleSheetsManagerが期待する変数名に合わせる
"""

import os
import re
from pathlib import Path


def find_service_account_json():
    """Google Cloud サービスアカウントJSONを探す"""

    print("🔍 サービスアカウントJSONファイルを検索中...")

    for json_file in Path(".").glob("*.json"):
        try:
            content = json_file.read_text()

            # サービスアカウントの特徴をチェック
            if all(key in content for key in ["private_key", "client_email", "project_id"]):
                print(f"✅ サービスアカウント発見: {json_file.name}")

                # プロジェクトIDを抽出
                match = re.search(r'"project_id":\s*"([^"]+)"', content)
                if match:
                    print(f"   プロジェクトID: {match.group(1)}")

                # client_emailを抽出
                match = re.search(r'"client_email":\s*"([^"]+)"', content)
                if match:
                    print(f"   クライアントメール: {match.group(1)}")

                return json_file.name
        except:
            continue

    return None


def read_env_file():
    """現在の.envファイルを読み込む"""
    env_path = Path(".env")
    if not env_path.exists():
        return {}

    env_vars = {}
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            env_vars[key.strip()] = value.strip()

    return env_vars


def update_env_file(service_account_file):
    """
    .envファイルを更新

    GoogleSheetsManagerが期待する変数名:
    - SERVICE_ACCOUNT_FILE
    - (またはGOOGLE_APPLICATION_CREDENTIALS)
    """

    env_vars = read_env_file()

    print("\n" + "=" * 70)
    print("📝 .env更新")
    print("=" * 70)

    # 現在の設定を表示
    print("\n【現在の設定】")
    for key in [
        "SERVICE_ACCOUNT_FILE",
        "GOOGLE_SERVICE_ACCOUNT_FILE",
        "GOOGLE_APPLICATION_CREDENTIALS",
        "SPREADSHEET_ID",
    ]:
        value = env_vars.get(key, "未設定")
        if value != "未設定" and len(value) > 40:
            value = value[:40] + "..."
        print(f"  {key}: {value}")

    # 更新
    updates = {}

    # GoogleSheetsManagerが最初にチェックする変数
    if service_account_file:
        updates["SERVICE_ACCOUNT_FILE"] = service_account_file
        updates["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_file

    # SPREADSHEET_IDは維持
    if "SPREADSHEET_ID" in env_vars:
        updates["SPREADSHEET_ID"] = env_vars["SPREADSHEET_ID"]

    # その他の重要な設定も維持
    for key in ["GEMINI_API_KEY", "OPENAI_API_KEY", "WP_URL", "WP_USER", "WP_PASS"]:
        if key in env_vars:
            updates[key] = env_vars[key]

    # .envファイルを書き直す
    env_path = Path(".env")
    lines = []

    # コメント行と既存の設定を保持しつつ更新
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.strip().startswith("#") or not line.strip():
                lines.append(line)
            elif "=" in line:
                key = line.split("=", 1)[0].strip()
                if key in updates:
                    lines.append(f"{key}={updates[key]}")
                    del updates[key]
                elif key not in [
                    "SERVICE_ACCOUNT_FILE",
                    "GOOGLE_SERVICE_ACCOUNT_FILE",
                    "GOOGLE_APPLICATION_CREDENTIALS",
                ]:
                    # 認証関連以外の設定は維持
                    lines.append(line)

    # 新規追加が必要な設定
    if updates:
        lines.append("")
        lines.append("# Google Sheets認証設定 (自動更新)")
        for key, value in updates.items():
            lines.append(f"{key}={value}")

    # 書き込み
    env_path.write_text("\n".join(lines) + "\n")

    print("\n【更新後の設定】")
    env_vars = read_env_file()
    for key in ["SERVICE_ACCOUNT_FILE", "GOOGLE_APPLICATION_CREDENTIALS", "SPREADSHEET_ID"]:
        value = env_vars.get(key, "未設定")
        if value != "未設定" and len(value) > 40:
            value = value[:40] + "..."
        status = "✅" if value != "未設定" else "❌"
        print(f"  {status} {key}: {value}")

    print("\n" + "=" * 70)


def main():
    print("=" * 70)
    print("🔧 .env設定統一ツール")
    print("=" * 70)
    print()

    # サービスアカウントJSONを探す
    service_account_file = find_service_account_json()

    if not service_account_file:
        print("\n❌ サービスアカウントJSONファイルが見つかりません")
        print("\n📝 次の手順で取得してください:")
        print("   1. Google Cloud Console でサービスアカウント作成")
        print("   2. JSONキーをダウンロード")
        print("   3. プロジェクトルートに配置")
        print("   4. このスクリプトを再実行")
        return False

    # .envを更新
    update_env_file(service_account_file)

    print("\n✅ .env設定を統一しました")
    print("\n🚀 次のステップ:")
    print("   python3 scripts/create_retry_history_sheet.py")

    return True


if __name__ == "__main__":
    main()
