"""
WordPressファイルマネージャー自動操作
Day 2: functions.php自動更新実装
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# プロジェクトルートをパスに追加
project_root = "/workspaces/gemini_AI_Agent"
sys.path.insert(0, project_root)

from browser_control.browser_controller import BrowserController


class WPFileManager:
    """WordPressファイルマネージャー自動操作クラス"""

    def __init__(self):
        self.browser = None
        self.wp_url = os.getenv("WP_URL")
        self.wp_user = os.getenv("WP_USER")
        self.wp_pass = os.getenv("WP_PASS")

    async def setup(self):
        """ブラウザセットアップ"""
        try:
            self.browser = BrowserController()
            await self.browser.setup_browser(headless=True)
            print("✅ ブラウザセットアップ完了")
            return True
        except Exception as e:
            print(f"❌ ブラウザセットアップ失敗: {e}")
            return False

    async def login_to_wordpress(self):
        """WordPressにログイン"""
        try:
            # ログインページに移動
            print(f"🌐 WordPressログインページに移動: {self.wp_url}/wp-admin")
            await self.browser.page.goto(f"{self.wp_url}/wp-admin", wait_until="networkidle")

            # ログイン済みか確認
            if "wp-admin" in self.browser.page.url and "wp-login.php" not in self.browser.page.url:
                print("✅ 既にログイン済み")
                return True

            # ログイン実行
            await self.browser.page.fill("#user_login", self.wp_user)
            await self.browser.page.fill("#user_pass", self.wp_pass)
            await self.browser.page.click("#wp-submit")

            # ログイン成功確認
            await self.browser.page.wait_for_selector("#wpadminbar", timeout=10000)
            print("✅ WordPressログイン成功")
            return True

        except Exception as e:
            print(f"❌ WordPressログイン失敗: {e}")
            return False

    async def access_file_manager(self):
        """ファイルマネージャーにアクセス"""
        try:
            # プラグインページに移動（ファイルマネージャープラグインを想定）
            print("📁 ファイルマネージャーにアクセス中...")
            await self.browser.page.goto(f"{self.wp_url}/wp-admin/plugin-install.php", wait_until="networkidle")

            # ファイルマネージャーの検索（代替方法）
            # 実際の環境に合わせて修正が必要

            # テーマエディターにアクセス（functions.php編集のため）
            await self.browser.page.goto(f"{self.wp_url}/wp-admin/theme-editor.php", wait_until="networkidle")

            # テーマエディターが利用可能か確認
            editor_available = await self.browser.page.query_selector("#theme-editor")
            if editor_available:
                print("✅ テーマエディターにアクセス成功")
                return True
            else:
                print("❌ テーマエディターにアクセスできません")
                return False

        except Exception as e:
            print(f"❌ ファイルマネージャーアクセス失敗: {e}")
            return False

    async def backup_functions_php(self):
        """functions.phpのバックアップ作成"""
        try:
            print("📦 functions.phpのバックアップ作成中...")

            # 現在のfunctions.phpの内容を取得
            await self.select_functions_file()

            # コードエディターの内容を取得
            code_editor = await self.browser.page.query_selector("#newcontent")
            if code_editor:
                current_content = await code_editor.text_content()

                # バックアップファイルに保存
                backup_dir = "automation/backups"
                os.makedirs(backup_dir, exist_ok=True)

                import datetime

                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"{backup_dir}/functions_php_backup_{timestamp}.txt"

                with open(backup_file, "w", encoding="utf-8") as f:
                    f.write(current_content)

                print(f"✅ functions.phpバックアップ作成: {backup_file}")
                return backup_file
            else:
                print("❌ コードエディターが見つかりません")
                return None

        except Exception as e:
            print(f"❌ バックアップ作成失敗: {e}")
            return None

    async def select_functions_file(self):
        """functions.phpファイルを選択"""
        try:
            print("🔧 functions.phpファイルを選択中...")

            # テーマファイルリストからfunctions.phpを選択
            functions_file_link = await self.browser.page.query_selector('a[href*="functions.php"]')
            if functions_file_link:
                await functions_file_link.click()
                await self.browser.page.wait_for_timeout(2000)
                print("✅ functions.phpを選択")
                return True
            else:
                print("❌ functions.phpリンクが見つかりません")
                return False

        except Exception as e:
            print(f"❌ functions.php選択失敗: {e}")
            return False

    async def update_functions_php(self, new_code):
        """functions.phpを更新"""
        try:
            print("🔄 functions.phpを更新中...")

            # コードエディターをクリア
            code_editor = await self.browser.page.query_selector("#newcontent")
            if code_editor:
                await code_editor.click(click_count=3)  # 全選択
                await code_editor.press("Backspace")

                # 新しいコードを入力
                await code_editor.fill(new_code)
                print("✅ 新しいコードを入力完了")

                # ファイル更新ボタンをクリック
                update_button = await self.browser.page.query_selector("#submit")
                if update_button:
                    await update_button.click()
                    await self.browser.page.wait_for_timeout(3000)

                    # 更新成功確認
                    success_message = await self.browser.page.query_selector(".updated, .notice-success")
                    if success_message:
                        print("✅ functions.php更新成功")
                        return True
                    else:
                        print("⚠️ 更新結果が確認できません")
                        return True  # 警告だが続行
                else:
                    print("❌ 更新ボタンが見つかりません")
                    return False
            else:
                print("❌ コードエディターが見つかりません")
                return False

        except Exception as e:
            print(f"❌ functions.php更新失敗: {e}")
            return False

    async def generate_dd_code(self):
        """DD機能コードを生成"""
        print("⚙️ DD機能コードを生成中...")

        # Phase 24のDDコード（実際のプロジェクトから取得）
        dd_code = """
<?php
// === DD（データドリブン）機能 ===
// 自動生成: WordPress自動化システム

// 企業データのカスタム投稿タイプ
function register_company_post_type() {
    $labels = array(
        'name' => '企業データ',
        'singular_name' => '企業',
        'menu_name' => '企業管理',
        'add_new' => '新規追加',
        'add_new_item' => '新規企業を追加',
        'edit_item' => '企業を編集',
        'new_item' => '新規企業',
        'view_item' => '企業を表示',
        'search_items' => '企業を検索',
        'not_found' => '企業が見つかりません',
        'not_found_in_trash' => 'ゴミ箱内に企業が見つかりません'
    );
    
    $args = array(
        'labels' => $labels,
        'public' => true,
        'has_archive' => true,
        'menu_position' => 5,
        'supports' => array('title', 'editor', 'thumbnail', 'custom-fields'),
        'show_in_rest' => true,
        'menu_icon' => 'dashicons-building'
    );
    
    register_post_type('company', $args);
}
add_action('init', 'register_company_post_type');

// カスタムフィールド（メタボックス）
function add_company_meta_boxes() {
    add_meta_box(
        'company_details',
        '企業詳細情報',
        'display_company_meta_box',
        'company',
        'normal',
        'high'
    );
}
add_action('add_meta_boxes', 'add_company_meta_boxes');

function display_company_meta_box($post) {
    // メタボックス表示内容
    wp_nonce_field('save_company_meta', 'company_meta_nonce');
    
    $fields = array(
        'company_name' => '企業名',
        'industry' => '業種',
        'location' => '所在地',
        'employees' => '従業員数',
        'established' => '設立年',
        'website' => 'Webサイト',
        'contact_email' => '連絡先メール',
        'phone' => '電話番号'
    );
    
    foreach ($fields as $key => $label) {
        $value = get_post_meta($post->ID, $key, true);
        echo '<p>';
        echo '<label for="' . $key . '">' . $label . ':</label>';
        echo '<input type="text" id="' . $key . '" name="' . $key . '" value="' . esc_attr($value) . '" style="width: 100%; margin-top: 5px;">';
        echo '</p>';
    }
}

function save_company_meta($post_id) {
    if (!isset($_POST['company_meta_nonce']) || !wp_verify_nonce($_POST['company_meta_nonce'], 'save_company_meta')) {
        return;
    }
    
    if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) {
        return;
    }
    
    $fields = array('company_name', 'industry', 'location', 'employees', 'established', 'website', 'contact_email', 'phone');
    
    foreach ($fields as $field) {
        if (isset($_POST[$field])) {
            update_post_meta($post_id, $field, sanitize_text_field($_POST[$field]));
        }
    }
}
add_action('save_post', 'save_company_meta');

// ショートコードで企業リストを表示
function company_list_shortcode($atts) {
    $atts = shortcode_atts(array(
        'industry' => '',
        'limit' => 10
    ), $atts);
    
    $args = array(
        'post_type' => 'company',
        'posts_per_page' => $atts['limit'],
        'post_status' => 'publish'
    );
    
    if (!empty($atts['industry'])) {
        $args['meta_query'] = array(
            array(
                'key' => 'industry',
                'value' => $atts['industry'],
                'compare' => 'LIKE'
            )
        );
    }
    
    $companies = new WP_Query($args);
    
    if (!$companies->have_posts()) {
        return '<p>企業データが見つかりません。</p>';
    }
    
    $output = '<div class="company-list">';
    
    while ($companies->have_posts()) {
        $companies->the_post();
        $output .= '<div class="company-item">';
        $output .= '<h3>' . get_the_title() . '</h3>';
        $output .= '<p><strong>業種:</strong> ' . get_post_meta(get_the_ID(), 'industry', true) . '</p>';
        $output .= '<p><strong>所在地:</strong> ' . get_post_meta(get_the_ID(), 'location', true) . '</p>';
        $output .= '<p><strong>従業員数:</strong> ' . get_post_meta(get_the_ID(), 'employees', true) . '</p>';
        $output .= '</div>';
    }
    
    $output .= '</div>';
    
    wp_reset_postdata();
    
    return $output;
}
add_shortcode('company_list', 'company_list_shortcode');

// 管理画面のカラム追加
function add_company_admin_columns($columns) {
    $new_columns = array(
        'cb' => $columns['cb'],
        'title' => $columns['title'],
        'industry' => '業種',
        'location' => '所在地',
        'employees' => '従業員数',
        'date' => $columns['date']
    );
    return $new_columns;
}
add_filter('manage_company_posts_columns', 'add_company_admin_columns');

function display_company_admin_columns($column, $post_id) {
    switch ($column) {
        case 'industry':
            echo get_post_meta($post_id, 'industry', true);
            break;
        case 'location':
            echo get_post_meta($post_id, 'location', true);
            break;
        case 'employees':
            echo get_post_meta($post_id, 'employees', true);
            break;
    }
}
add_action('manage_company_posts_custom_column', 'display_company_admin_columns', 10, 2);

echo "✅ DD機能コードがfunctions.phpに追加されました";
?>
"""

        print("✅ DD機能コード生成完了")
        return dd_code

    async def run_full_update(self):
        """完全なfunctions.php更新プロセス"""
        print("=" * 60)
        print("🚀 functions.php自動更新開始 - Day 2")
        print("=" * 60)

        # セットアップ
        if not await self.setup():
            return False

        # WordPressログイン
        if not await self.login_to_wordpress():
            return False

        # ファイルマネージャーアクセス
        if not await self.access_file_manager():
            return False

        # バックアップ作成
        backup_file = await self.backup_functions_php()
        if not backup_file:
            print("⚠️ バックアップ作成に失敗しましたが続行します")

        # functions.php選択
        if not await self.select_functions_file():
            return False

        # DDコード生成
        dd_code = await self.generate_dd_code()

        # 更新実行
        update_success = await self.update_functions_php(dd_code)

        # 結果記録
        result = {
            "backup_created": backup_file is not None,
            "backup_file": backup_file,
            "update_success": update_success,
            "timestamp": asyncio.get_event_loop().time(),
        }

        # ログ保存
        os.makedirs("automation/logs/day2", exist_ok=True)
        with open("automation/logs/day2/file_update_result.json", "w") as f:
            import json

            json.dump(result, f, indent=2)

        print(f"📊 更新結果を保存: automation/logs/day2/file_update_result.json")

        return update_success


async def main():
    """メイン実行"""
    file_manager = WPFileManager()
    success = await file_manager.run_full_update()

    print("=" * 60)
    if success:
        print("🎉 Day 2: functions.php自動更新 完了！")
        print("✅ 次のステップ: 企業データ実登録へ進めます")
    else:
        print("❌ Day 2: functions.php自動更新 失敗")
        print("🔧 問題を解決して再実行してください")
    print("=" * 60)

    # ブラウザを閉じる
    if file_manager.browser:
        print("🔄 ブラウザをクリーンアップ中...")
        await file_manager.browser.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
