"""
環境変数詳細確認スクリプト
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 環境変数詳細確認")
print("=" * 50)

# すべての環境変数を表示（マスクされたパスワード）
env_vars = {"WP_URL": os.getenv("WP_URL"), "WP_USER": os.getenv("WP_USER"), "WP_PASS": os.getenv("WP_PASS")}

for key, value in env_vars.items():
    if value:
        if "PASS" in key:
            masked_value = "*" * len(value)
            print(f"✅ {key}: {masked_value} (長さ: {len(value)})")
        else:
            print(f"✅ {key}: {value}")
    else:
        print(f"❌ {key}: 未設定")

print("=" * 50)

# .envファイルの存在確認
env_file = ".env"
if os.path.exists(env_file):
    print(f"✅ .envファイル存在: {env_file}")
    print("📄 .envファイル内容:")
    with open(env_file, "r") as f:
        for line in f:
            if "WP_" in line and "PASS" not in line:
                print(f"   {line.strip()}")
            elif "WP_PASS" in line:
                parts = line.split("=")
                if len(parts) == 2:
                    print(f"   {parts[0]}=********")
else:
    print(f"❌ .envファイル不存在: {env_file}")

print("=" * 50)
print("🎉 環境変数確認完了")
