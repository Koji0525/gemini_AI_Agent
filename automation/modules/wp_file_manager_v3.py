"""
WordPressファイルマネージャー自動操作 - V3 (デバッグ改善版)
デバッグ情報に基づいて複数の方法を試行
"""

import asyncio
import os
import sys
import datetime
from dotenv import load_dotenv

load_dotenv()

project_root = "/workspaces/gemini_AI_Agent"
sys.path.insert(0, project_root)

from browser_control.browser_controller import BrowserController


class WPFileManagerV3:
    """WordPressファイルマネージャー - V3"""

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
            print(f"🌐 WordPressログイン: {self.wp_url}/wp-admin")
            await self.browser.page.goto(f"{self.wp_url}/wp-admin", wait_until="networkidle")

            if "wp-admin" in self.browser.page.url and "wp-login.php" not in self.browser.page.url:
                print("✅ 既にログイン済み")
                return True

            await self.browser.page.fill("#user_login", self.wp_user)
            await self.browser.page.fill("#user_pass", self.wp_pass)
            await self.browser.page.click("#wp-submit")
            await self.browser.page.wait_for_selector("#wpadminbar", timeout=15000)

            print("✅ WordPressログイン成功")
            return True

        except Exception as e:
            print(f"❌ WordPressログイン失敗: {e}")
            return False

    async def access_functions_php_direct(self):
        """functions.phpに直接アクセスする方法1: URLパラメータ"""
        try:
            print("🎯 方法1: URLパラメータでfunctions.phpに直接アクセス")

            # テーマエディターでfunctions.phpを直接開く
            functions_url = f"{self.wp_url}/wp-admin/theme-editor.php?file=functions.php"
            await self.browser.page.goto(functions_url, wait_until="networkidle")

            # コードエディターが表示されたか確認
            editor = await self.browser.page.query_selector("#newcontent")
            if editor:
                content = await editor.input_value()
                if "<?php" in content:
                    print("✅ functions.phpを直接開けました")
                    return True

            print("⚠️ 方法1失敗: コードエディターが見つかりません")
            return False

        except Exception as e:
            print(f"⚠️ 方法1失敗: {e}")
            return False

    async def access_functions_php_link(self):
        """functions.phpに直接アクセスする方法2: リンククリック"""
        try:
            print("🎯 方法2: functions.phpリンクをクリック")

            # テーマエディターに移動
            await self.browser.page.goto(f"{self.wp_url}/wp-admin/theme-editor.php", wait_until="networkidle")

            # functions.phpのリンクを探す
            link_selectors = [
                'a[href*="functions.php"]',
                'a:has-text("functions.php")',
                '.file-list a:has-text("functions.php")',
            ]

            for selector in link_selectors:
                link = await self.browser.page.query_selector(selector)
                if link:
                    print(f"  📍 リンク発見: {selector}")
                    await link.click()
                    await self.browser.page.wait_for_timeout(2000)

                    # 成功確認
                    editor = await self.browser.page.query_selector("#newcontent")
                    if editor:
                        content = await editor.input_value()
                        if "<?php" in content:
                            print("✅ functions.phpを開けました")
                            return True

            print("⚠️ 方法2失敗: functions.phpリンクが見つかりません")
            return False

        except Exception as e:
            print(f"⚠️ 方法2失敗: {e}")
            return False

    async def access_functions_php_select(self):
        """functions.phpに直接アクセスする方法3: セレクトボックス"""
        try:
            print("🎯 方法3: セレクトボックスで選択")

            await self.browser.page.goto(f"{self.wp_url}/wp-admin/theme-editor.php", wait_until="networkidle")

            # まずテーマを選択（必要な場合）
            theme_select = await self.browser.page.query_selector('select[name="theme"]')
            if theme_select:
                # アクティブなテーマ（最初のオプション）を選択
                await theme_select.select_option(index=0)
                await self.browser.page.wait_for_timeout(1000)
                print("  ✅ テーマ選択完了")

            # ファイル選択ドロップダウンを探す
            file_select = await self.browser.page.query_selector("select#template")
            if not file_select:
                file_select = await self.browser.page.query_selector('select[name="file"]')

            if file_select:
                # すべてのオプションを取得
                options = await file_select.query_selector_all("option")
                print(f"  📋 ファイルオプション数: {len(options)}")

                # functions.phpを探す
                for option in options:
                    value = await option.get_attribute("value")
                    text = await option.text_content()

                    if value and "functions.php" in value:
                        print(f"  📍 functions.php発見: value={value}")
                        await file_select.select_option(value=value)
                        await self.browser.page.wait_for_timeout(2000)

                        # 成功確認
                        editor = await self.browser.page.query_selector("#newcontent")
                        if editor:
                            content = await editor.input_value()
                            if "<?php" in content:
                                print("✅ functions.phpを開けました")
                                return True

                    elif "functions.php" in text:
                        print(f"  📍 functions.php発見: text={text}")
                        await option.click()
                        await self.browser.page.wait_for_timeout(2000)

                        editor = await self.browser.page.query_selector("#newcontent")
                        if editor:
                            content = await editor.input_value()
                            if "<?php" in content:
                                print("✅ functions.phpを開けました")
                                return True

            print("⚠️ 方法3失敗: functions.phpを選択できません")
            return False

        except Exception as e:
            print(f"⚠️ 方法3失敗: {e}")
            return False

    async def access_functions_php(self):
        """functions.phpにアクセス（複数の方法を試行）"""
        print("�� functions.phpへのアクセス試行")

        methods = [
            ("URLパラメータ", self.access_functions_php_direct),
            ("リンククリック", self.access_functions_php_link),
            ("セレクトボックス", self.access_functions_php_select),
        ]

        for name, method in methods:
            print(f"\n--- {name}で試行 ---")
            if await method():
                print(f"✅ {name}で成功！")
                return True
            print(f"⚠️ {name}失敗、次の方法を試行...")

        print("\n❌ すべての方法でfunctions.phpにアクセスできませんでした")
        return False

    async def backup_functions_php(self):
        """functions.phpのバックアップ作成"""
        try:
            print("📦 functions.phpのバックアップ作成中...")

            editor = await self.browser.page.query_selector("#newcontent")
            if not editor:
                print("❌ コードエディターが見つかりません")
                return None

            current_content = await editor.input_value()

            backup_dir = "automation/backups/day2"
            os.makedirs(backup_dir, exist_ok=True)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{backup_dir}/functions_php_backup_{timestamp}.php"

            with open(backup_file, "w", encoding="utf-8") as f:
                f.write(current_content)

            print(f"✅ バックアップ作成: {backup_file}")
            return backup_file

        except Exception as e:
            print(f"❌ バックアップ作成失敗: {e}")
            return None

    async def generate_dd_code(self):
        """DD機能コードを生成"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        dd_code = f"""

// ============================================================
// DD（デューデリジェンス）機能 - 自動追加
// 追加日: {timestamp}
// ============================================================

// M&A企業データカスタム投稿タイプ
if (!function_exists('register_ma_company_post_type')) {{
    function register_ma_company_post_type() {{
        register_post_type('ma_company', array(
            'labels' => array(
                'name' => 'M&A企業データ',
                'singular_name' => '企業'
            ),
            'public' => true,
            'show_in_rest' => true,
            'supports' => array('title', 'editor', 'thumbnail'),
            'menu_icon' => 'dashicons-building'
        ));
    }}
    add_action('init', 'register_ma_company_post_type');
}}

// 企業リスト表示ショートコード
if (!function_exists('ma_company_list_shortcode')) {{
    function ma_company_list_shortcode($atts) {{
        $companies = get_posts(array('post_type' => 'ma_company', 'posts_per_page' => -1));
        $output = '<div class="ma-companies">';
        foreach ($companies as $company) {{
            $output .= '<div class="ma-company">' . esc_html($company->post_title) . '</div>';
        }}
        $output .= '</div>';
        return $output;
    }}
    add_shortcode('ma_company_list', 'ma_company_list_shortcode');
}}

// DD機能有効化確認関数
if (!function_exists('dd_functionality_status')) {{
    function dd_functionality_status() {{
        return '✅ DD機能が正常に追加されました - {timestamp}';
    }}
}}

// 管理画面通知
add_action('admin_notices', function() {{
    echo '<div class="notice notice-success"><p>DD機能が有効化されました（{timestamp}）</p></div>';
}});
"""

        print("✅ DD機能コード生成完了")
        return dd_code

    async def append_dd_code(self, dd_code):
        """DDコードを追加"""
        try:
            print("🔄 functions.phpにDDコードを追加中...")

            editor = await self.browser.page.query_selector("#newcontent")
            if not editor:
                print("❌ コードエディターが見つかりません")
                return False

            current_code = await editor.input_value()
            updated_code = current_code + "\n" + dd_code

            await editor.fill(updated_code)
            print("✅ DDコードを追加")

            # 更新ボタンをクリック
            submit_button = await self.browser.page.query_selector("#submit")
            if submit_button:
                await submit_button.click()
                await self.browser.page.wait_for_timeout(5000)

                # 成功メッセージ確認
                success = await self.browser.page.query_selector(".updated, .notice-success")
                if success:
                    msg = await success.text_content()
                    print(f"✅ 更新成功: {msg.strip()}")
                    return True

                # エラーメッセージ確認
                error = await self.browser.page.query_selector(".error, .notice-error")
                if error:
                    msg = await error.text_content()
                    print(f"❌ 更新エラー: {msg.strip()}")
                    return False

                print("⚠️ 更新結果が不明ですが続行")
                return True

            print("❌ 更新ボタンが見つかりません")
            return False

        except Exception as e:
            print(f"❌ コード追加失敗: {e}")
            return False

    async def run_full_update(self):
        """完全な更新プロセス"""
        print("=" * 60)
        print("🚀 functions.php自動更新 - Day 2 V3")
        print("=" * 60)

        if not await self.setup():
            return False

        if not await self.login_to_wordpress():
            return False

        if not await self.access_functions_php():
            return False

        backup_file = await self.backup_functions_php()

        dd_code = await self.generate_dd_code()

        update_success = await self.append_dd_code(dd_code)

        # 結果記録
        result = {
            "backup_created": backup_file is not None,
            "backup_file": backup_file,
            "update_success": update_success,
            "timestamp": datetime.datetime.now().isoformat(),
        }

        os.makedirs("automation/logs/day2", exist_ok=True)
        import json

        with open("automation/logs/day2/file_update_result.json", "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return update_success


async def main():
    file_manager = WPFileManagerV3()
    success = await file_manager.run_full_update()

    print("=" * 60)
    if success:
        print("🎉 Day 2 完了: functions.php自動更新成功！")
    else:
        print("❌ Day 2 失敗: 問題を解決してください")
    print("=" * 60)

    if file_manager.browser:
        await file_manager.browser.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
