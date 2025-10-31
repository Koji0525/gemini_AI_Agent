"""
WordPressファイルマネージャー V4 - 全体最適設計版
Day 2: functions.php自動更新

【設計方針】
1. 再利用性: 他のテーマファイル編集にも対応できる汎用設計
2. 堅牢性: 複数の方法をフォールバックで試行
3. 保守性: ログ記録とエラーハンドリングの徹底
4. 拡張性: Day 3以降のタスクに対応できる構造
"""

import asyncio
import os
import sys
import datetime
import json
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from browser_control.browser_controller import BrowserController


class WPFileManagerV4:
    """
    WordPressファイルマネージャー - 全体最適設計版

    【責任範囲】
    - WordPressテーマファイルへのアクセス
    - ファイルの読み取り・バックアップ・更新
    - 更新結果のログ記録

    【依存関係】
    - BrowserController: ブラウザ操作（外部から注入）
    - 環境変数: WP_URL, WP_USER, WP_PASS
    """

    def __init__(self):
        self.browser: Optional[BrowserController] = None
        self.wp_url = os.getenv("WP_URL")
        self.wp_user = os.getenv("WP_USER")
        self.wp_pass = os.getenv("WP_PASS")
        self.current_theme = "cocoon-child-master"  # デバッグで判明
        self.log_dir = "automation/logs/day2"
        self.backup_dir = "automation/backups/day2"

        # ログディレクトリ作成
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)

    def _log(self, message: str, level: str = "INFO"):
        """ログ記録（ファイルとコンソール）"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"

        print(log_message)

        # ログファイルに追記
        log_file = f"{self.log_dir}/wp_file_manager.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")

    async def setup(self) -> bool:
        """ブラウザセットアップ"""
        try:
            self._log("ブラウザセットアップ開始")
            self.browser = BrowserController()
            await self.browser.setup_browser(headless=True)
            self._log("✅ ブラウザセットアップ完了", "SUCCESS")
            return True
        except Exception as e:
            self._log(f"❌ ブラウザセットアップ失敗: {e}", "ERROR")
            return False

    async def login_to_wordpress(self) -> bool:
        """WordPressにログイン"""
        try:
            self._log(f"WordPressログイン試行: {self.wp_url}/wp-admin")
            await self.browser.page.goto(f"{self.wp_url}/wp-admin", wait_until="networkidle")

            current_url = self.browser.page.url

            # 既にログイン済みか確認
            if "wp-admin" in current_url and "wp-login.php" not in current_url:
                self._log("✅ 既にログイン済み", "SUCCESS")
                return True

            # ログイン実行
            await self.browser.page.fill("#user_login", self.wp_user)
            await self.browser.page.fill("#user_pass", self.wp_pass)
            await self.browser.page.click("#wp-submit")

            # ログイン完了を確認
            await self.browser.page.wait_for_selector("#wpadminbar", timeout=15000)
            self._log("✅ WordPressログイン成功", "SUCCESS")
            return True

        except Exception as e:
            self._log(f"❌ WordPressログイン失敗: {e}", "ERROR")
            return False

    async def open_theme_file(self, filename: str, theme: Optional[str] = None) -> bool:
        """
        テーマファイルを開く（汎用メソッド）

        【重要】この方法が最も確実:
        - 直接URLでファイルを指定
        - select要素の操作は不要

        Args:
            filename: 開くファイル名（例: "functions.php"）
            theme: テーマ名（省略時は現在のテーマ）

        Returns:
            bool: 成功/失敗
        """
        try:
            if theme is None:
                theme = self.current_theme

            self._log(f"テーマファイルを開く: {filename} (テーマ: {theme})")

            # 【重要】直接リンクでアクセス（デバッグで判明した方法）
            file_url = f"{self.wp_url}/wp-admin/theme-editor.php?file={filename}&theme={theme}"
            await self.browser.page.goto(file_url, wait_until="networkidle")

            # コードエディターが表示されるまで待機
            await self.browser.page.wait_for_selector("#newcontent", state="visible", timeout=10000)

            # ファイル内容を確認
            content = await self.browser.page.input_value("#newcontent")

            # PHPファイルの場合は<?phpの存在を確認
            if filename.endswith(".php"):
                if "<?php" not in content:
                    self._log(f"⚠️ PHPファイルですが<?phpがありません", "WARNING")

            self._log(f"✅ {filename} を開きました（サイズ: {len(content)} バイト）", "SUCCESS")
            return True

        except Exception as e:
            self._log(f"❌ {filename} を開けませんでした: {e}", "ERROR")
            return False

    async def backup_file(self, filename: str) -> Optional[str]:
        """
        現在開いているファイルをバックアップ

        Returns:
            str: バックアップファイルのパス（失敗時はNone）
        """
        try:
            self._log(f"バックアップ作成: {filename}")

            # 現在のファイル内容を取得
            content = await self.browser.page.input_value("#newcontent")

            # バックアップファイル名（タイムスタンプ付き）
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = filename.replace(".php", "").replace(".css", "")
            backup_file = f"{self.backup_dir}/{base_name}_backup_{timestamp}.php"

            # バックアップ保存
            with open(backup_file, "w", encoding="utf-8") as f:
                f.write(content)

            self._log(f"✅ バックアップ完了: {backup_file}", "SUCCESS")
            return backup_file

        except Exception as e:
            self._log(f"❌ バックアップ失敗: {e}", "ERROR")
            return None

    async def append_code(self, code: str) -> bool:
        """
        現在開いているファイルにコードを追加

        【重要】既存コードを壊さない安全な追加方式

        Args:
            code: 追加するコード

        Returns:
            bool: 成功/失敗
        """
        try:
            self._log("コード追加開始")

            # 現在のコードを取得
            current_code = await self.browser.page.input_value("#newcontent")

            # 既に同じコードが存在するかチェック
            if code.strip() in current_code:
                self._log("⚠️ 同じコードが既に存在します", "WARNING")
                return False

            # コードを末尾に追加
            updated_code = current_code + "\n" + code

            # エディターに入力
            await self.browser.page.fill("#newcontent", updated_code)

            self._log(f"✅ コード追加完了（追加サイズ: {len(code)} バイト）", "SUCCESS")
            return True

        except Exception as e:
            self._log(f"❌ コード追加失敗: {e}", "ERROR")
            return False

    async def save_file(self) -> bool:
        """
        ファイルを保存

        Returns:
            bool: 成功/失敗
        """
        try:
            self._log("ファイル保存開始")

            # 更新ボタンをクリック
            await self.browser.page.click("#submit")

            # 保存完了を待機
            await self.browser.page.wait_for_timeout(5000)

            # 成功メッセージを確認
            success_msg = await self.browser.page.query_selector(".updated, .notice-success")
            if success_msg:
                msg_text = await success_msg.text_content()
                self._log(f"✅ ファイル保存成功: {msg_text.strip()}", "SUCCESS")
                return True

            # エラーメッセージを確認
            error_msg = await self.browser.page.query_selector(".error, .notice-error")
            if error_msg:
                err_text = await error_msg.text_content()
                self._log(f"❌ ファイル保存エラー: {err_text.strip()}", "ERROR")
                return False

            self._log("⚠️ 保存結果が不明です", "WARNING")
            return False

        except Exception as e:
            self._log(f"❌ ファイル保存失敗: {e}", "ERROR")
            return False

    def generate_dd_code(self) -> str:
        """
        DD機能コードを生成

        【全体最適】Day 3以降のタスクに対応できるよう、
        基本的な投稿タイプ登録とショートコードのみを実装

        Returns:
            str: 生成されたPHPコード
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        code = f"""

// ============================================================
// DD（デューデリジェンス）機能 - Day 2 自動追加
// 追加日: {timestamp}
// ============================================================

/**
 * M&A企業データ カスタム投稿タイプ
 * Day 3以降で企業データを登録するための基盤
 */
if (!function_exists('register_ma_company_post_type')) {{
    function register_ma_company_post_type() {{
        register_post_type('ma_company', array(
            'labels' => array(
                'name' => 'M&A企業データ',
                'singular_name' => '企業',
                'add_new' => '新規追加',
                'add_new_item' => '新しい企業を追加',
                'edit_item' => '企業を編集',
                'view_item' => '企業を表示'
            ),
            'public' => true,
            'show_in_rest' => true,
            'supports' => array('title', 'editor', 'thumbnail', 'custom-fields'),
            'menu_icon' => 'dashicons-building',
            'has_archive' => true,
            'rewrite' => array('slug' => 'ma-companies')
        ));
    }}
    add_action('init', 'register_ma_company_post_type');
}}

/**
 * 企業リスト表示ショートコード
 * 使用方法: [ma_company_list]
 */
if (!function_exists('ma_company_list_shortcode')) {{
    function ma_company_list_shortcode($atts) {{
        $args = array(
            'post_type' => 'ma_company',
            'posts_per_page' => -1,
            'orderby' => 'title',
            'order' => 'ASC'
        );
        
        $companies = get_posts($args);
        
        if (empty($companies)) {{
            return '<p>企業データがまだ登録されていません。</p>';
        }}
        
        $output = '<div class="ma-company-list">';
        foreach ($companies as $company) {{
            $output .= '<div class="ma-company-item">';
            $output .= '<h3>' . esc_html($company->post_title) . '</h3>';
            $output .= '<a href="' . get_permalink($company->ID) . '">詳細を見る</a>';
            $output .= '</div>';
        }}
        $output .= '</div>';
        
        return $output;
    }}
    add_shortcode('ma_company_list', 'ma_company_list_shortcode');
}}

/**
 * DD機能ステータス確認関数
 * Day 3以降のタスクで機能の有効化を確認するために使用
 */
if (!function_exists('dd_functionality_status')) {{
    function dd_functionality_status() {{
        return array(
            'status' => 'active',
            'version' => '1.0.0',
            'installed_at' => '{timestamp}',
            'post_type' => 'ma_company'
        );
    }}
}}

// 管理画面通知（初回のみ表示）
add_action('admin_notices', function() {{
    $dismissed = get_option('ma_dd_notice_dismissed', false);
    if (!$dismissed) {{
        echo '<div class="notice notice-success is-dismissible">';
        echo '<p><strong>DD機能が有効化されました！</strong>（{timestamp}）</p>';
        echo '<p>これで企業データの登録が可能になりました。</p>';
        echo '</div>';
        // 一度表示したらフラグを立てる
        update_option('ma_dd_notice_dismissed', true);
    }}
}});
"""

        self._log("✅ DD機能コード生成完了", "SUCCESS")
        return code

    async def update_functions_php(self) -> Dict:
        """
        functions.phpを更新するメイン処理

        Returns:
            Dict: 実行結果の詳細
        """
        result = {
            "success": False,
            "backup_created": False,
            "backup_file": None,
            "code_added": False,
            "file_saved": False,
            "timestamp": datetime.datetime.now().isoformat(),
            "errors": [],
        }

        try:
            self._log("=" * 60)
            self._log("functions.php自動更新開始 - Day 2", "INFO")
            self._log("=" * 60)

            # Step 1: ブラウザセットアップ
            if not await self.setup():
                result["errors"].append("ブラウザセットアップ失敗")
                return result

            # Step 2: WordPressログイン
            if not await self.login_to_wordpress():
                result["errors"].append("WordPressログイン失敗")
                return result

            # Step 3: functions.phpを開く
            if not await self.open_theme_file("functions.php"):
                result["errors"].append("functions.phpを開けない")
                return result

            # Step 4: バックアップ作成
            backup_file = await self.backup_file("functions.php")
            if backup_file:
                result["backup_created"] = True
                result["backup_file"] = backup_file
            else:
                self._log("⚠️ バックアップ作成失敗。続行します", "WARNING")

            # Step 5: DDコード生成
            dd_code = self.generate_dd_code()

            # Step 6: コード追加
            if await self.append_code(dd_code):
                result["code_added"] = True
            else:
                result["errors"].append("コード追加失敗")
                return result

            # Step 7: ファイル保存
            if await self.save_file():
                result["file_saved"] = True
                result["success"] = True
            else:
                result["errors"].append("ファイル保存失敗")
                return result

            self._log("=" * 60)
            self._log("✅ functions.php自動更新完了！", "SUCCESS")
            self._log("=" * 60)

        except Exception as e:
            self._log(f"❌ 予期しないエラー: {e}", "ERROR")
            result["errors"].append(str(e))

        finally:
            # 結果をJSONで保存
            result_file = f"{self.log_dir}/update_result.json"
            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            self._log(f"実行結果を保存: {result_file}")

            # ブラウザクリーンアップ
            if self.browser:
                await self.browser.cleanup()

        return result


async def main():
    """メイン実行関数"""
    manager = WPFileManagerV4()
    result = await manager.update_functions_php()

    # 結果サマリー表示
    print("\n" + "=" * 60)
    print("📊 Day 2 実行結果サマリー")
    print("=" * 60)
    print(f"✅ 成功: {result['success']}")
    print(f"📦 バックアップ: {result['backup_created']}")
    print(f"📝 コード追加: {result['code_added']}")
    print(f"💾 ファイル保存: {result['file_saved']}")

    if result["errors"]:
        print(f"\n❌ エラー:")
        for err in result["errors"]:
            print(f"  - {err}")

    if result["backup_file"]:
        print(f"\n📦 バックアップファイル:")
        print(f"  {result['backup_file']}")

    print("=" * 60)

    if result["success"]:
        print("\n🎉 Day 2 完了！次はDay 3（企業データ登録）へ進めます")
    else:
        print("\n❌ Day 2 失敗。ログを確認してください:")
        print(f"  automation/logs/day2/wp_file_manager.log")


if __name__ == "__main__":
    asyncio.run(main())
