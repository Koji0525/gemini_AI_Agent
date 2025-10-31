#!/usr/bin/env python3
"""
修正版自動投稿スクリプト - エンドポイント自動検出対応
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "agents"))

from ma_auto_poster_fixed import MAAutoPosterAgentFixed, get_companies_data


def main():
    print("🚀 M&A企業情報 自動投稿バッチ実行 - 修正版")
    print("=" * 50)

    try:
        # 自動投稿エージェント初期化
        poster = MAAutoPosterAgentFixed()

        print("🔍 接続テスト中...")
        if not poster.test_connection():
            print("❌ WordPress接続失敗")
            return

        print("🔍 カスタム投稿タイプ確認中...")
        if not poster.check_ma_company_cpt():
            print("❌ カスタム投稿タイプのエンドポイントが見つかりません")
            print("\n💡 解決策:")
            print("   1. WordPressのfunctions.phpにCPT定義を追加")
            print("   2. パーマリンク設定を更新（設定 → パーマリンク → 保存）")
            print("   3. 以下のコードをfunctions.phpに追加:")
            print(
                """
// M&A企業情報カスタム投稿タイプ
function ma_company_register_post_type() {
    register_post_type('ma_company', array(
        'labels' => array('name' => 'M&A企業情報'),
        'public' => true,
        'has_archive' => true,
        'show_in_rest' => true,
        'rest_base' => 'ma_company', // REST APIエンドポイント
        'supports' => array('title', 'editor', 'custom-fields')
    ));
    flush_rewrite_rules(false);
}
add_action('init', 'ma_company_register_post_type');

// 業種タクソノミー
function ma_industry_taxonomy() {
    register_taxonomy('ma_industry', 'ma_company', array(
        'hierarchical' => true,
        'labels' => array('name' => '業種'),
        'show_in_rest' => true,
        'rest_base' => 'ma_industry'
    ));
}
add_action('init', 'ma_industry_taxonomy');
"""
            )
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

        if failed_count > 0:
            print("\n💡 失敗時の対策:")
            print("   1. WordPress管理画面で手動で企業を追加")
            print("   2. functions.phpのCPT定義を確認")
            print("   3. パーマリンク設定を更新")

    except ValueError as e:
        print(f"❌ 設定エラー: {e}")
        print("\n💡 環境変数を設定してください:")
        print("   export WP_URL=https://uzbek-ma.com")
        print("   export WP_USERNAME=uzbek")
        print("   export WP_PASSWORD='RkLU 07Fk rNpe iENd Fx3s wseJ'")
    except Exception as e:
        print(f"❌ 予期せぬエラー: {e}")


if __name__ == "__main__":
    main()
