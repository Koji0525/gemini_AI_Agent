#!/usr/bin/env python3
"""
🎯 Day 3 ミッション実行スクリプト
目標: 5社の企業データをWordPressに完全登録
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))

from ma_auto_poster_day3 import MAAutoPosterDay3, get_day3_companies


def print_header():
    """ヘッダー表示"""
    print("\n" + "=" * 70)
    print("🎯 Day 3 ミッション: 5社データ完全登録".center(70))
    print("=" * 70 + "\n")


def print_summary(results):
    """結果サマリー表示"""
    print("\n" + "=" * 70)
    print("📊 Day 3 完了レポート".center(70))
    print("=" * 70 + "\n")

    success = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "failed"]

    print(f"✅ 成功: {len(success)}社")
    for r in success:
        dd_count = r.get("dd_items", 0)
        print(f"   • {r['title']}")
        print(f"     └─ ID: {r['post_id']} | 業種: {r['industry']} | DD項目: {dd_count}件")

    if failed:
        print(f"\n❌ 失敗: {len(failed)}社")
        for r in failed:
            print(f"   • {r['title']}")

    completion_rate = (len(success) / len(results)) * 100
    print(f"\n{'='*70}")
    print(f"📈 達成率: {completion_rate:.1f}%".center(70))
    print(f"{'='*70}\n")

    if completion_rate == 100:
        print("🎉" * 20)
        print("\n�� Day 3 完全達成！ 🎉\n")
        print("🎉" * 20)
        print("\n✨ 次のステップ:")
        print("   📌 Day 4: Task Executor統合")
        print("   📌 レポート生成機能の実装")
        print("   📌 Google Sheetsログ記録\n")
    elif completion_rate >= 80:
        print(f"💪 素晴らしい！あと{len(failed)}社で完全達成です！")
    else:
        print(f"⚠️ もう一度実行してみましょう")


def main():
    """メイン処理"""
    print_header()

    try:
        # エージェント初期化
        print("🤖 エージェント初期化中...")
        poster = MAAutoPosterDay3()

        # 接続テスト
        print("\n🔍 WordPress接続テスト中...")
        if not poster.test_connection():
            print("\n❌ 接続失敗。以下を確認してください:")
            print("   • .env ファイルの存在")
            print("   • WP_URL, WP_USERNAME, WP_PASSWORD の設定")
            print("   • WordPressサイトの稼働状況")
            return

        # データ取得
        companies = get_day3_companies()
        print(f"\n📊 登録予定企業数: {len(companies)}社")

        # 一括投稿実行
        results = poster.batch_create_companies(companies)

        # 結果表示
        print_summary(results)

    except ValueError as e:
        print(f"\n❌ 設定エラー: {e}")
        print("\n💡 解決方法:")
        print("   1. .env ファイルを確認")
        print("   2. 必要な環境変数を設定")

    except Exception as e:
        print(f"\n❌ 予期せぬエラー: {e}")
        import traceback

        print("\n📋 詳細:")
        traceback.print_exc()


if __name__ == "__main__":
    main()
