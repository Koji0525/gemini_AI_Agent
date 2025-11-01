#!/usr/bin/env python3
"""
config_utils.py に service_account.json のパス設定を追加
"""


def update_config():
    config_file = "configuration/config_utils.py"

    # ファイル読み込み
    with open(config_file, "r", encoding="utf-8") as f:
        content = f.read()

    # バックアップ
    with open(f"{config_file}.backup_service_account", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ バックアップ作成")

    # service_account のパス設定を追加
    service_account_config = """
# Google Sheets Service Account Configuration
SERVICE_ACCOUNT_FILE = "configuration/service_account.json"
SERVICE_ACCOUNT_PATH = Path(__file__).parent / "service_account.json"
"""

    # ファイルの先頭に追加（import文の後）
    if "SERVICE_ACCOUNT_FILE" not in content:
        # import文を探す
        lines = content.split("\n")
        insert_index = 0

        for i, line in enumerate(lines):
            if line.strip().startswith("from pathlib import Path") or line.strip().startswith("import os"):
                insert_index = i + 1

        # 挿入
        lines.insert(insert_index, service_account_config)

        new_content = "\n".join(lines)

        # 保存
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(new_content)

        print("✅ config_utils.py を更新しました")
        print("\n追加された設定:")
        print(service_account_config)
    else:
        print("⚠️  SERVICE_ACCOUNT_FILE 設定は既に存在します")

    return True


if __name__ == "__main__":
    import os

    os.chdir("/workspaces/gemini_AI_Agent")

    success = update_config()

    if success:
        print("\n✅ 設定更新完了！")
        print("\n次のステップ:")
        print("  1. configuration/service_account.json の存在を確認")
        print("  2. 統合テストを実行")
    else:
        print("\n❌ 設定更新失敗")
