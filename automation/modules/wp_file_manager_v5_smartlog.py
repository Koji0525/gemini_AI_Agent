"""
WordPressファイルマネージャー V5 - SmartLog対応版
Day 2: functions.php自動更新

【改善点】
1. SmartLog形式のログ（30回に1回タイムスタンプ）
2. hidden状態の#newcontentへの対応
3. JavaScriptによる動的表示の待機処理
"""

import asyncio
import os
import sys
import datetime
import json
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from browser_control.browser_controller import BrowserController


class SmartLogger:
    """
    SmartLog実装 - 30回に1回タイムスタンプ表示

    【表示ルール】
    - 30回に1回タイムスタンプ表示
    - 10分（600秒）経過時は強制表示
    - 日付が変わった時も強制表示
    - ファイルには常に完全なタイムスタンプを記録
    """

    def __init__(self, log_file: str):
        self.log_file = log_file
        self._log_count = 0
        self._last_timestamp = None
        self._last_date = None

        # ログディレクトリ作成
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        """SmartLog形式でログ出力"""
        current_time = datetime.datetime.now()
        timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        current_date = current_time.date()

        # カウント増加
        self._log_count += 1

        # タイムスタンプ表示判定
        show_timestamp = False
        show_date = False

        # 初回は必ず表示
        if self._last_timestamp is None:
            show_timestamp = True
            show_date = True
        # 30回に1回
        elif self._log_count % 30 == 1:
            show_timestamp = True
        # 10分（600秒）経過
        elif (current_time.timestamp() - self._last_timestamp) > 600:
            show_timestamp = True
        # 日付が変わった
        elif self._last_date != current_date:
            show_timestamp = True
            show_date = True

        # レベル別の絵文字と色
        level_config = {
            "INFO": ("📝", ""),
            "SUCCESS": ("✅", "\033[92m"),
            "WARNING": ("⚠️", "\033[93m"),
            "ERROR": ("❌", "\033[91m"),
            "DEBUG": ("🔍", "\033[94m"),
        }

        emoji, color = level_config.get(level, ("📝", ""))
        reset_color = "\033[0m" if color else ""

        # コンソール表示
        if show_timestamp:
            if show_date:
                console_msg = f"\n[{timestamp_str}] {emoji} {message}"
            else:
                console_msg = f"[{current_time.strftime('%H:%M:%S')}] {emoji} {message}"
            self._last_timestamp = current_time.timestamp()
            self._last_date = current_date
        else:
            console_msg = f"{emoji} {message}"

        print(f"{color}{console_msg}{reset_color}")

        # ファイルには常に完全なタイムスタンプを記録
        file_msg = f"[{timestamp_str}] [{level}] {message}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(file_msg)


class WPFileManagerV5:
    """WordPressファイルマネージャー V5 - SmartLog対応"""

    def __init__(self):
        self.browser: Optional[BrowserController] = None
        self.wp_url = os.getenv("WP_URL")
        self.wp_user = os.getenv("WP_USER")
        self.wp_pass = os.getenv("WP_PASS")
        self.current_theme = "cocoon-child-master"

        # SmartLogger初期化
        log_dir = "automation/logs/day2"
        os.makedirs(log_dir, exist_ok=True)
        self.logger = SmartLogger(f"{log_dir}/wp_file_manager.log")

        self.backup_dir = "automation/backups/day2"
        os.makedirs(self.backup_dir, exist_ok=True)

    async def setup(self) -> bool:
        """ブラウザセットアップ"""
        try:
            self.logger.log("ブラウザセットアップ開始", "INFO")
            self.browser = BrowserController()
            await self.browser.setup_browser(headless=True)
            self.logger.log("ブラウザセットアップ完了", "SUCCESS")
            return True
        except Exception as e:
            self.logger.log(f"ブラウザセットアップ失敗: {e}", "ERROR")
            return False

    async def login_to_wordpress(self) -> bool:
        """WordPressにログイン"""
        try:
            self.logger.log(f"WordPressログイン試行: {self.wp_url}/wp-admin", "INFO")
            await self.browser.page.goto(f"{self.wp_url}/wp-admin", wait_until="networkidle")

            if "wp-login.php" in self.browser.page.url:
                self.logger.log("ログインフォーム入力中", "INFO")
                await self.browser.page.fill("#user_login", self.wp_user)
                await self.browser.page.fill("#user_pass", self.wp_pass)
                await self.browser.page.click("#wp-submit")
                await self.browser.page.wait_for_selector("#wpadminbar", timeout=15000)
            else:
                self.logger.log("既にログイン済み", "INFO")

            self.logger.log("WordPressログイン成功", "SUCCESS")
            return True

        except Exception as e:
            self.logger.log(f"WordPressログイン失敗: {e}", "ERROR")
            return False

    async def open_functions_php_with_wait(self) -> bool:
        """
        functions.phpを開く - hidden要素対応版

        【重要】#newcontentがhiddenの場合の対処:
        1. 直接URLでアクセス
        2. ページ読み込み完了を待機
        3. JavaScriptの実行完了を待機
        4. #newcontentがattached状態になるまで待機
        5. visibleになるまで待機（最大30秒）
        """
        try:
            self.logger.log("functions.phpを開いています...", "INFO")

            # Step 1: 直接URLでアクセス
            functions_url = f"{self.wp_url}/wp-admin/theme-editor.php?file=functions.php&theme={self.current_theme}"
            self.logger.log(f"URL: {functions_url}", "DEBUG")

            await self.browser.page.goto(functions_url, wait_until="networkidle")
            self.logger.log("ページ読み込み完了", "INFO")

            # Step 2: JavaScriptの実行完了を待機
            await self.browser.page.wait_for_timeout(2000)
            self.logger.log("JavaScript実行待機完了", "INFO")

            # Step 3: #newcontentがDOM上に存在することを確認
            editor_exists = await self.browser.page.query_selector("#newcontent")
            if not editor_exists:
                self.logger.log("#newcontentが存在しません", "ERROR")
                return False

            self.logger.log("#newcontent要素を発見", "INFO")

            # Step 4: hidden属性を確認し、JavaScriptで強制的に表示
            is_hidden = await self.browser.page.evaluate(
                """
                () => {
                    const editor = document.querySelector('#newcontent');
                    if (!editor) return true;
                    
                    // hidden属性をチェック
                    const isHidden = editor.hasAttribute('hidden') || 
                                   editor.style.display === 'none' ||
                                   editor.offsetParent === null;
                    
                    // hiddenの場合は強制的に表示
                    if (isHidden) {
                        editor.removeAttribute('hidden');
                        editor.style.display = 'block';
                        editor.style.visibility = 'visible';
                    }
                    
                    return !isHidden;
                }
            """
            )

            if not is_hidden:
                self.logger.log("#newcontentが非表示だったため強制表示", "WARNING")
                await self.browser.page.wait_for_timeout(1000)

            # Step 5: 要素が操作可能になるまで待機
            await self.browser.page.wait_for_selector("#newcontent", state="attached", timeout=10000)
            self.logger.log("#newcontent attached状態確認", "INFO")

            # Step 6: 内容を取得して確認
            content = await self.browser.page.input_value("#newcontent")

            if "<?php" not in content:
                self.logger.log("PHPコードが見つかりません。別のファイルが開かれている可能性", "WARNING")

            file_size = len(content)
            self.logger.log(f"functions.phpを開きました（サイズ: {file_size} バイト）", "SUCCESS")

            return True

        except Exception as e:
            self.logger.log(f"functions.phpを開けませんでした: {e}", "ERROR")

            # デバッグ情報を追加
            try:
                # スクリーンショット保存
                await self.browser.page.screenshot(path="automation/logs/day2/error_screenshot.png")
                self.logger.log("エラー時のスクリーンショットを保存", "DEBUG")

                # #newcontentの状態を詳細確認
                editor_state = await self.browser.page.evaluate(
                    """
                    () => {
                        const editor = document.querySelector('#newcontent');
                        if (!editor) return { exists: false };
                        
                        return {
                            exists: true,
                            hasHidden: editor.hasAttribute('hidden'),
                            display: editor.style.display,
                            visibility: editor.style.visibility,
                            offsetParent: editor.offsetParent !== null,
                            value_length: editor.value ? editor.value.length : 0
                        };
                    }
                """
                )
                self.logger.log(f"#newcontent状態: {json.dumps(editor_state, indent=2)}", "DEBUG")
            except:
                pass

            return False

    async def backup_file(self) -> Optional[str]:
        """ファイルをバックアップ"""
        try:
            self.logger.log("バックアップ作成中...", "INFO")

            content = await self.browser.page.input_value("#newcontent")

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{self.backup_dir}/functions_backup_{timestamp}.php"

            with open(backup_file, "w", encoding="utf-8") as f:
                f.write(content)

            self.logger.log(f"バックアップ完了: {backup_file}", "SUCCESS")
            return backup_file

        except Exception as e:
            self.logger.log(f"バックアップ失敗: {e}", "ERROR")
            return None

    async def append_code(self, code: str) -> bool:
        """コードを追加"""
        try:
            self.logger.log("コード追加開始", "INFO")

            current_code = await self.browser.page.input_value("#newcontent")

            # 重複チェック
            if "DD（デューデリジェンス）機能" in current_code:
                self.logger.log("DDコードが既に存在します", "WARNING")
                return False

            updated_code = current_code + "\n" + code

            await self.browser.page.fill("#newcontent", updated_code)

            code_size = len(code)
            self.logger.log(f"コード追加完了（追加サイズ: {code_size} バイト）", "SUCCESS")
            return True

        except Exception as e:
            self.logger.log(f"コード追加失敗: {e}", "ERROR")
            return False

    async def save_file(self) -> bool:
        """ファイルを保存"""
        try:
            self.logger.log("ファイル保存中...", "INFO")

            await self.browser.page.click("#submit")
            await self.browser.page.wait_for_timeout(5000)

            # 成功メッセージ確認
            success_msg = await self.browser.page.query_selector(".updated, .notice-success")
            if success_msg:
                msg_text = await success_msg.text_content()
                self.logger.log(f"ファイル保存成功: {msg_text.strip()}", "SUCCESS")
                return True

            # エラーメッセージ確認
            error_msg = await self.browser.page.query_selector(".error, .notice-error")
            if error_msg:
                err_text = await error_msg.text_content()
                self.logger.log(f"ファイル保存エラー: {err_text.strip()}", "ERROR")
                return False

            self.logger.log("保存結果が不明です", "WARNING")
            return False

        except Exception as e:
            self.logger.log(f"ファイル保存失敗: {e}", "ERROR")
            return False

    def generate_dd_code(self) -> str:
        """DD機能コードを生成"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        code = f"""

// ============================================================
// DD（デューデリジェンス）機能 - Day 2 自動追加
// 追加日: {timestamp}
// ============================================================

// M&A企業データ カスタム投稿タイプ
if (!function_exists('register_ma_company_post_type')) {{
    function register_ma_company_post_type() {{
        register_post_type('ma_company', array(
            'labels' => array(
                'name' => 'M&A企業データ',
                'singular_name' => '企業',
                'add_new' => '新規追加',
                'add_new_item' => '新しい企業を追加'
            ),
            'public' => true,
            'show_in_rest' => true,
            'supports' => array('title', 'editor', 'thumbnail', 'custom-fields'),
            'menu_icon' => 'dashicons-building',
            'has_archive' => true
        ));
    }}
    add_action('init', 'register_ma_company_post_type');
}}

// 企業リスト表示ショートコード
if (!function_exists('ma_company_list_shortcode')) {{
    function ma_company_list_shortcode() {{
        $companies = get_posts(array('post_type' => 'ma_company', 'posts_per_page' => -1));
        $output = '<div class="ma-company-list">';
        foreach ($companies as $c) {{
            $output .= '<div class="ma-item"><h3>' . esc_html($c->post_title) . '</h3></div>';
        }}
        $output .= '</div>';
        return $output;
    }}
    add_shortcode('ma_company_list', 'ma_company_list_shortcode');
}}

// DD機能ステータス確認
if (!function_exists('dd_status')) {{
    function dd_status() {{
        return array('status' => 'active', 'version' => '1.0', 'installed' => '{timestamp}');
    }}
}}
"""

        self.logger.log("DD機能コード生成完了", "SUCCESS")
        return code

    async def run(self) -> Dict:
        """メイン処理"""
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
            self.logger.log("=" * 60, "INFO")
            self.logger.log("functions.php自動更新開始 - Day 2 V5", "INFO")
            self.logger.log("=" * 60, "INFO")

            if not await self.setup():
                result["errors"].append("ブラウザセットアップ失敗")
                return result

            if not await self.login_to_wordpress():
                result["errors"].append("WordPressログイン失敗")
                return result

            if not await self.open_functions_php_with_wait():
                result["errors"].append("functions.phpを開けない")
                return result

            backup_file = await self.backup_file()
            if backup_file:
                result["backup_created"] = True
                result["backup_file"] = backup_file

            dd_code = self.generate_dd_code()

            if await self.append_code(dd_code):
                result["code_added"] = True
            else:
                result["errors"].append("コード追加失敗")
                return result

            if await self.save_file():
                result["file_saved"] = True
                result["success"] = True
            else:
                result["errors"].append("ファイル保存失敗")
                return result

            self.logger.log("=" * 60, "INFO")
            self.logger.log("functions.php自動更新完了！", "SUCCESS")
            self.logger.log("=" * 60, "INFO")

        except Exception as e:
            self.logger.log(f"予期しないエラー: {e}", "ERROR")
            result["errors"].append(str(e))

        finally:
            # 結果保存
            result_file = "automation/logs/day2/update_result.json"
            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            if self.browser:
                await self.browser.cleanup()

        return result


async def main():
    """メイン実行"""
    manager = WPFileManagerV5()
    result = await manager.run()

    print("\n" + "=" * 60)
    print("📊 Day 2 実行結果")
    print("=" * 60)
    print(f"✅ 成功: {result['success']}")
    print(f"📦 バックアップ: {result['backup_created']}")
    print(f"📝 コード追加: {result['code_added']}")
    print(f"💾 保存: {result['file_saved']}")

    if result["errors"]:
        print(f"\n❌ エラー: {', '.join(result['errors'])}")

    if result["success"]:
        print("\n🎉 Day 2 完了！次はDay 3へ")
    else:
        print("\n❌ Day 2 失敗")
        print("📄 ログ: automation/logs/day2/wp_file_manager.log")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
