#!/usr/bin/env python3
"""
functions.php 解析スクリプト
使い方: 既存の functions.php の内容を FUNCTIONS_CODE に貼り付けて実行
"""

import re


def analyze_functions_php(code):
    """functions.php を解析して競合をチェック"""

    print("🔍 functions.php 解析開始")
    print("=" * 70)

    # カスタム投稿タイプを検出
    cpt_pattern = r"register_post_type\s*\(\s*['\"]([^'\"]+)['\"]"
    cpts = re.findall(cpt_pattern, code)

    if cpts:
        print("\n📋 検出されたカスタム投稿タイプ:")
        for cpt in cpts:
            if cpt == "ma_company":
                print(f"   ⚠️ {cpt} - 競合あり！別名を使用してください")
            else:
                print(f"   • {cpt}")
    else:
        print("\n✅ カスタム投稿タイプなし - 安全に作成可能")

    # タクソノミーを検出
    tax_pattern = r"register_taxonomy\s*\(\s*['\"]([^'\"]+)['\"]"
    taxonomies = re.findall(tax_pattern, code)

    if taxonomies:
        print("\n🏷️ 検出されたタクソノミー:")
        for tax in taxonomies:
            if tax == "ma_industry":
                print(f"   ⚠️ {tax} - 競合あり！別名を使用してください")
            else:
                print(f"   • {tax}")
    else:
        print("\n✅ カスタムタクソノミーなし - 安全に作成可能")

    # 関数名を検出
    func_pattern = r"function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\("
    functions = re.findall(func_pattern, code)

    if functions:
        print(f"\n🔧 検出された関数: {len(functions)}個")

        risky_names = [
            "create_ma_company_post_type",
            "create_ma_industries",
            "ma_company",
        ]

        for func in functions[:10]:  # 最初の10個のみ表示
            if any(risky in func for risky in risky_names):
                print(f"   ⚠️ {func} - 名前が競合する可能性")
            else:
                print(f"   • {func}")

        if len(functions) > 10:
            print(f"   ... 他 {len(functions) - 10}個")

    # ACF関連を検出
    acf_pattern = r"acf|advanced.custom.fields"
    if re.search(acf_pattern, code, re.IGNORECASE):
        print("\n📝 ACF関連コードが検出されました")

    # 総合判定
    print("\n" + "=" * 70)
    print("📊 総合判定")
    print("=" * 70)

    conflicts = []
    if "ma_company" in cpts:
        conflicts.append("カスタム投稿タイプ 'ma_company' が既に存在")
    if "ma_industry" in taxonomies:
        conflicts.append("タクソノミー 'ma_industry' が既に存在")

    if conflicts:
        print("\n⚠️ 競合が検出されました:")
        for conflict in conflicts:
            print(f"   • {conflict}")

        print("\n💡 推奨対応:")
        print("   1. 既存のものを使用する")
        print("   2. または別名で作成（例: ma_company_v2）")
    else:
        print("\n✅ 競合なし - 安全に実装可能")
        print("\n📝 推奨実装コード:")
        print(
            """
// M&A企業情報カスタム投稿タイプ
function uzbek_ma_create_company_post_type() {
    register_post_type('ma_company', array(
        'labels' => array(
            'name' => 'M&A企業情報',
            'singular_name' => '企業情報'
        ),
        'public' => true,
        'has_archive' => true,
        'supports' => array('title', 'editor', 'thumbnail'),
        'menu_icon' => 'dashicons-building',
        'show_in_rest' => true,
    ));
    
    register_taxonomy('ma_industry', 'ma_company', array(
        'labels' => array(
            'name' => '業種',
        ),
        'hierarchical' => true,
        'show_in_rest' => true,
    ));
}
add_action('init', 'uzbek_ma_create_company_post_type');
        """
        )


# ==================================================
# 使い方
# ==================================================

if __name__ == "__main__":
    print("📝 使い方:")
    print("=" * 70)
    print("1. WordPress管理画面で functions.php の内容をコピー")
    print("2. このファイルの FUNCTIONS_CODE 変数に貼り付け")
    print("3. 再実行して解析結果を確認")
    print("")
    print("現在: サンプルコードで実行中...")
    print("")

    # サンプルコード（実際のコードに置き換えてください）
    FUNCTIONS_CODE = """
    <?php
    // 既存の functions.php の内容をここに貼り付けてください
    
    // サンプル: 既存のカスタム投稿タイプ
    // function my_custom_post_types() {
    //     register_post_type('blog_post', array(...));
    // }
    """

    analyze_functions_php(FUNCTIONS_CODE)

    print("\n" + "=" * 70)
    print("⚠️ 注意: 上記はサンプル解析結果です")
    print("実際の functions.php の内容を貼り付けて再実行してください")
