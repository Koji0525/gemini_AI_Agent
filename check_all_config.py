#!/usr/bin/env python3
"""
全設定を確認
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .env を読み込み
load_dotenv()

print("=" * 70)
print("🔍 環境変数チェック")
print("=" * 70)

# 必須の環境変数
required_vars = {
    'GEMINI_API_KEY': 'Gemini API',
    'OPENAI_API_KEY': 'OpenAI API',
    'WORDPRESS_URL': 'WordPress URL',
}

optional_vars = {
    'WORDPRESS_ADMIN_USER': 'WP管理者名',
    'WORDPRESS_ADMIN_PASSWORD': 'WP管理者パスワード',
    'BROWSER_DATA_DIR': 'ブラウザデータディレクトリ',
}

# 必須変数のチェック
print("\n📌 必須設定:")
all_ok = True
for var, desc in required_vars.items():
    value = os.getenv(var)
    if value:
        masked = value[:8] + "..." if len(value) > 8 else "***"
        print(f"  ✅ {desc}: {masked}")
    else:
        print(f"  ❌ {desc}: 未設定")
        all_ok = False

# オプション変数のチェック
print("\n📋 オプション設定:")
for var, desc in optional_vars.items():
    value = os.getenv(var)
    if value:
        if 'PASSWORD' in var:
            masked = "***"
        else:
            masked = value[:20] + "..." if len(value) > 20 else value
        print(f"  ✅ {desc}: {masked}")
    else:
        print(f"  ⚠️  {desc}: 未設定（デフォルト値を使用）")

# ディレクトリ設定
print("\n📁 ディレクトリ設定:")
dirs = {
    'downloads': 'ダウンロードフォルダ',
    'browser_data': 'ブラウザデータ',
    'logs': 'ログディレクトリ',
}

for dir_name, desc in dirs.items():
    dir_path = Path(dir_name)
    if dir_path.exists():
        print(f"  ✅ {desc}: {dir_path}")
    else:
        print(f"  ⚠️  {desc}: 未作成 → 自動作成します")
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"     ✅ 作成完了: {dir_path}")

print("\n" + "=" * 70)
if all_ok:
    print("✅ 全ての必須設定が完了しています！")
    print("\n次のステップ:")
    print("  python autonomous_system.py --test-only")
else:
    print("⚠️  一部の設定が不足しています")
    print("\n.env ファイルを編集してください:")
    print("  nano .env")

print("=" * 70)
