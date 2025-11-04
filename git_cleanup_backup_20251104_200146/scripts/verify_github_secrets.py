#!/usr/bin/env python3
"""
🔍 GitHub Secrets検証スクリプト

GitHub Actions実行時に環境変数が正しく設定されているか確認
"""

import os
import sys

def check_secret(name: str, required: bool = True) -> bool:
    """環境変数の存在確認"""
    value = os.getenv(name)
    
    if value:
        # 値の一部だけ表示（セキュリティのため）
        masked = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
        print(f"✅ {name}: {masked}")
        return True
    else:
        if required:
            print(f"❌ {name}: 未設定")
        else:
            print(f"⚠️ {name}: 未設定（オプション）")
        return not required

def main():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔍 GitHub Secrets 検証")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    required_secrets = [
        'SPREADSHEET_ID',
        'WP_URL',
        'WP_USER',
        'WP_PASS',
        'GEMINI_API_KEY',
        'WP_API_URL',
    ]
    
    optional_secrets = [
        'APPLICATION_PASSWORDS',
        'APPLICATION_PASSWORDS_NAME',
    ]
    
    all_ok = True
    
    print("\n【必須のSecrets】")
    for secret in required_secrets:
        if not check_secret(secret, required=True):
            all_ok = False
    
    print("\n【オプションのSecrets】")
    for secret in optional_secrets:
        check_secret(secret, required=False)
    
    # GOOGLE_CREDENTIALSの確認（特殊処理）
    print("\n【認証情報ファイル】")
    if os.path.exists('service_account.json'):
        print("✅ service_account.json: 存在")
    else:
        print("❌ service_account.json: 未作成")
        all_ok = False
    
    if os.path.exists('.env'):
        print("✅ .env: 存在")
    else:
        print("⚠️ .env: 未作成（GitHub Actions内で生成されます）")
    
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    if all_ok:
        print("✅ すべての必須Secretsが設定されています")
        sys.exit(0)
    else:
        print("❌ 一部のSecretsが未設定です")
        sys.exit(1)

if __name__ == "__main__":
    main()
