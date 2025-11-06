"""
Google Sheets認証設定チェックとセットアップ
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def check_auth_setup():
    """認証設定をチェック"""

    print("=" * 70)
    print("🔐 Google Sheets認証設定チェック")
    print("=" * 70)
    print()

    # 1. 環境変数チェック
    print("【1】環境変数チェック")
    print("-" * 70)

    service_account = os.getenv("SERVICE_ACCOUNT_FILE")
    google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    spreadsheet_id = os.getenv("SPREADSHEET_ID")

    print(f"SERVICE_ACCOUNT_FILE: {service_account or '❌ 未設定'}")
    print(f"GOOGLE_APPLICATION_CREDENTIALS: {google_creds or '❌ 未設定'}")
    print(f"SPREADSHEET_ID: {spreadsheet_id[:20] + '...' if spreadsheet_id else '❌ 未設定'}")
    print()

    # 2. ファイル存在チェック
    print("【2】サービスアカウントファイルチェック")
    print("-" * 70)

    json_files = list(Path(".").glob("*.json"))

    if json_files:
        print(f"✅ 見つかったJSONファイル: {len(json_files)}件")
        for f in json_files:
            size_kb = f.stat().st_size / 1024
            print(f"  - {f.name} ({size_kb:.1f}KB)")
    else:
        print("❌ JSONファイルが見つかりません")
        print()
        print("📝 サービスアカウントJSONファイルの取得方法:")
        print("   1. Google Cloud Console にアクセス")
        print("   2. プロジェクトを選択")
        print("   3. IAMと管理 > サービスアカウント")
        print("   4. サービスアカウント作成 or 既存のものを選択")
        print("   5. キー > 新しい鍵を追加 > JSON形式でダウンロード")
        print("   6. ダウンロードしたJSONファイルをプロジェクトルートに配置")

    print()

    # 3. 推奨設定
    print("【3】推奨される.env設定")
    print("-" * 70)

    if json_files:
        recommended_file = json_files[0].name
        print(f"SERVICE_ACCOUNT_FILE={recommended_file}")
        print(f"GOOGLE_APPLICATION_CREDENTIALS={recommended_file}")
    else:
        print("SERVICE_ACCOUNT_FILE=your-service-account.json")
        print("GOOGLE_APPLICATION_CREDENTIALS=your-service-account.json")

    print(f"SPREADSHEET_ID={spreadsheet_id or 'your-spreadsheet-id'}")
    print()

    # 4. 診断結果

    # 標準環境変数ローダー（自動追加）import sysfrom pathlib import Pathsys.path.insert(0, str(Path(__file__).parent.parent))from tools.env_loader import StandardEnvLoaderif not StandardEnvLoader.load_and_verify():    print("環境変数の読み込みに失敗しました")    sys.exit(1)
    print("【4】診断結果")
    print("-" * 70)

    issues = []

    if not service_account and not google_creds:
        issues.append("サービスアカウント設定が.envにありません")

    if service_account and not Path(service_account).exists():
        issues.append(f"指定されたファイルが見つかりません: {service_account}")

    if google_creds and not Path(google_creds).exists():
        issues.append(f"指定されたファイルが見つかりません: {google_creds}")

    if not spreadsheet_id:
        issues.append("SPREADSHEET_IDが設定されていません")

    if not json_files:
        issues.append("サービスアカウントJSONファイルがありません")

    if issues:
        print("❌ 問題が見つかりました:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        print()
        print("👉 次のアクション:")
        print("   1. サービスアカウントJSONファイルを取得")
        print("   2. プロジェクトルートに配置")
        print("   3. .envファイルに設定を追加")
        return False
    else:
        print("✅ 認証設定は正常です")
        return True


if __name__ == "__main__":
    check_auth_setup()
