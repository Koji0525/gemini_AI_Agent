#!/usr/bin/env python3
"""
強化版自動投稿スクリプト - 既存エージェント連携版
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "agents"))

from ma_auto_poster_with_healing import MAAutoPosterWithHealing, get_companies_data


def main():
    print("🚀 M&A企業情報 自動投稿バッチ実行 - 強化版")
    print("🔗 既存エージェント連携対応")
    print("=" * 50)

    try:
        # 自動投稿エージェント初期化
        poster = MAAutoPosterWithHealing()

        print("🔍 接続テスト中...")
        if not poster.test_connection():
            print("❌ WordPress接続失敗")
            return

        print("🔍 カスタム投稿タイプ確認中...")
        if not poster.check_ma_company_cpt():
            print("❌ カスタム投稿タイプのエンドポイントが見つかりません")
            return

        # データソースの選択
        data_source = os.getenv("DATA_SOURCE", "demo")
        print(f"📊 データソース: {data_source}")

        print("📊 企業データ取得中...")
        companies = get_companies_data(data_source)

        if not companies:
            print("❌ 企業データを取得できませんでした")
            return

        print(f"🚀 自動投稿開始... ({len(companies)}企業)")
        print("-" * 50)

        results = poster.batch_create_companies(companies)

        # 結果サマリー
        success_count = sum(1 for r in results if r["status"] == "success")
        failed_count = len(results) - success_count

        print("=" * 50)
        print(f"🎯 バッチ実行完了")
        print(f"✅ 成功: {success_count}件")
        print(f"❌ 失敗: {failed_count}件")

        if HAS_SELF_HEALING and failed_count > 0:
            print("\n💡 セルフヒーリング機能が失敗を分析中...")
            # ここでフィードバックを表示

    except ValueError as e:
        print(f"❌ 設定エラー: {e}")
    except Exception as e:
        print(f"❌ 予期せぬエラー: {e}")


if __name__ == "__main__":
    main()
