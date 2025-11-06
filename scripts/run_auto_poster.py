#!/usr/bin/env python3
"""
M&A企業情報 自動投稿バッチ実行スクリプト
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "agents"))

from ma_auto_poster_agent import MAAutoPosterAgent, generate_demo_companies


def main():
    print("🚀 M&A企業情報 自動投稿バッチ実行")

    # 環境変数から設定を取得（安全な方法）
    WP_URL = os.getenv("WP_URL", "https://your-wordpress-site.com")
    USERNAME = os.getenv("WP_USERNAME", "admin")
    PASSWORD = os.getenv("WP_PASSWORD", "your_password")

    if PASSWORD == "your_password":
        print("❌ 環境変数を設定してください:")
        print("export WP_URL=https://your-site.com")
        print("export WP_USERNAME=admin")
        print("export WP_PASSWORD=your_application_password")
        return

    # 自動投稿エージェント初期化
    poster = MAAutoPosterAgent(WP_URL, USERNAME, PASSWORD)

    print("🔍 接続テスト中...")
    if not poster.test_connection():
        print("❌ WordPress接続失敗")
        return

    print("🔍 カスタム投稿タイプ確認中...")
    if not poster.check_ma_company_cpt():
        print("❌ ma_company CPTが登録されていません")
        print("💡 まずCPT定義をfunctions.phpに追加してください")
        return

    print("📊 デモデータ生成中...")
    companies = generate_demo_companies()

    print("🚀 自動投稿開始...")
    results = poster.batch_create_companies(companies)

    # 結果サマリー
    success_count = sum(1 for r in results if r["status"] == "success")
    failed_count = len(results) - success_count

    print(f"\n🎯 バッチ実行完了")
    print(f"✅ 成功: {success_count}件")
    print(f"❌ 失敗: {failed_count}件")

    # 詳細結果

    # 標準環境変数ローダー（自動追加）import sysfrom pathlib import Pathsys.path.insert(0, str(Path(__file__).parent.parent))from tools.env_loader import StandardEnvLoaderif not StandardEnvLoader.load_and_verify():    print("環境変数の読み込みに失敗しました")    sys.exit(1)
    print("\n📋 詳細結果:")
    for result in results:
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"  {status_icon} {result['title']}")


if __name__ == "__main__":
    main()
