"""
WordPress自動設定エージェント v1.2.5
ACFフィールドを完全自動でWordPressに設定
テーマエディター対応強化版
"""

import asyncio
import json
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# プロジェクトルートをパスに追加（.parent を4回使用）
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 直接インポート（__init__.py を経由しない）
from configuration.config_loader import ConfigLoader

# Playwright使用
try:
    from playwright.async_api import async_playwright, Browser, Page

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright未インストール: pip install playwright")

# ロガー設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class WPAutoConfigAgent:
    """WordPress自動設定エージェント"""

    def __init__(self):
        """初期化"""
        # ロガー初期化
        self.logger = logging.getLogger("WPAutoConfigAgent")

        # 設定読み込み
        self.config = ConfigLoader()
        self.wp_url = self.config.get("WP_URL")
        self.wp_user = self.config.get("WP_USER")
        self.wp_pass = self.config.get("WP_PASS")

        # Playwright
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

        self.logger.info("🚀 WPAutoConfigAgent v1.2.5 初期化完了")

    async def setup_browser(self):
        """ブラウザ起動"""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwrightがインストールされていません")

        self.logger.info("ブラウザ起動中...")
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        self.logger.info("✅ ブラウザ起動完了")

    async def login_wordpress(self) -> bool:
        """WordPress管理画面にログイン"""
        try:
            login_url = f"{self.wp_url}/wp-admin"
            self.logger.info(f"WordPressログイン: {login_url}")

            await self.page.goto(login_url, wait_until="networkidle")

            # ログインフォーム入力
            await self.page.fill('input[name="log"]', self.wp_user)
            await self.page.fill('input[name="pwd"]', self.wp_pass)
            await self.page.click('input[type="submit"]')

            # ログイン完了待機
            await self.page.wait_for_url("**/wp-admin/**", timeout=10000)

            self.logger.info("✅ WordPressログイン成功")
            return True

        except Exception as e:
            self.logger.error(f"❌ ログイン失敗: {e}")
            return False

    async def check_acf_plugin(self) -> bool:
        """ACFプラグインの存在確認"""
        try:
            plugins_url = f"{self.wp_url}/wp-admin/plugins.php"
            await self.page.goto(plugins_url, wait_until="networkidle")

            # ACFプラグインを検索
            content = await self.page.content()
            acf_exists = "Advanced Custom Fields" in content

            if acf_exists:
                self.logger.info("✅ ACFプラグイン検出")
            else:
                self.logger.warning("⚠️ ACFプラグイン未検出")

            return acf_exists

        except Exception as e:
            self.logger.error(f"❌ ACFプラグイン確認失敗: {e}")
            return False

    async def add_acf_code_to_functions(self, php_file_path: Path) -> bool:
        """functions.phpにACFコードを追加（改善版）"""
        try:
            self.logger.info(f"📄 PHPファイル読み込み: {php_file_path}")

            # PHPコード読み込み
            with open(php_file_path, "r", encoding="utf-8") as f:
                acf_code = f.read()

            self.logger.info(f"📦 読み込んだコードサイズ: {len(acf_code)} 文字")

            # Theme File Editorにアクセス
            editor_url = f"{self.wp_url}/wp-admin/theme-editor.php"
            await self.page.goto(editor_url, wait_until="networkidle")

            # ページの状態をスクリーンショット
            screenshot_path = "agent_outputs/theme_editor_debug.png"
            await self.page.screenshot(path=screenshot_path)
            self.logger.info(f"📸 スクリーンショット保存: {screenshot_path}")

            # テキストエリアの存在確認（visible ではなく attached で待機）
            self.logger.info("⏳ テキストエリア待機中...")

            try:
                # 複数のセレクタを試す
                selectors = ['textarea[name="newcontent"]', "#newcontent", "textarea#newcontent"]

                textarea = None
                for selector in selectors:
                    try:
                        self.logger.info(f"🔍 セレクタ試行: {selector}")
                        textarea = await self.page.wait_for_selector(
                            selector, state="attached", timeout=10000  # visible ではなく attached
                        )
                        if textarea:
                            self.logger.info(f"✅ テキストエリア検出: {selector}")
                            break
                    except Exception as e:
                        self.logger.warning(f"⚠️ {selector} 失敗: {e}")
                        continue

                if not textarea:
                    self.logger.error("❌ テキストエリアが見つかりません")
                    return False

                # テキストエリアが非表示の場合、表示させる
                is_visible = await textarea.is_visible()
                self.logger.info(f"📊 テキストエリア表示状態: {is_visible}")

                if not is_visible:
                    self.logger.info("🔧 テキストエリアを強制表示...")
                    await self.page.evaluate(
                        """
                        const textarea = document.querySelector('textarea[name="newcontent"]');
                        if (textarea) {
                            textarea.style.display = 'block';
                            textarea.style.visibility = 'visible';
                            textarea.style.opacity = '1';
                        }
                    """
                    )
                    await asyncio.sleep(1)

                # 既存のコンテンツを取得
                current_content = await self.page.evaluate(
                    """
                    document.querySelector('textarea[name="newcontent"]').value
                """
                )

                self.logger.info(f"📝 現在のコンテンツサイズ: {len(current_content)} 文字")

                # ACFコードが既に存在するか確認
                if "acf_add_local_field_group" in current_content:
                    self.logger.warning("⚠️ ACFコードは既に存在します")
                    return True

                # 新しいコードを追加（<?php の後に挿入）
                new_content = current_content.replace("<?php", f"<?php\n\n{acf_code}\n", 1)

                # コンテンツを更新（JavaScriptで直接設定）
                self.logger.info("📝 コンテンツ更新中...")
                await self.page.evaluate(
                    f"""
                    document.querySelector('textarea[name="newcontent"]').value = `{new_content.replace('`', '\\`')}`;
                """
                )

                # 保存ボタンをクリック
                self.logger.info("💾 保存ボタンクリック...")
                await self.page.click('input[name="submit"]')

                # 保存完了待機（複数のセレクタを試す）
                try:
                    await self.page.wait_for_selector(".notice-success", timeout=5000)
                    self.logger.info("✅ functions.phpにACFコード追加完了")
                    return True
                except:
                    # 成功メッセージが見つからなくても、エラーがなければ成功とみなす
                    await asyncio.sleep(2)
                    error_notice = await self.page.query_selector(".notice-error")
                    if error_notice:
                        error_text = await error_notice.text_content()
                        self.logger.error(f"❌ 保存エラー: {error_text}")
                        return False
                    else:
                        self.logger.info("✅ functions.php更新完了（エラーなし）")
                        return True

            except Exception as e:
                self.logger.error(f"❌ テキストエリア操作失敗: {e}")
                return False

        except Exception as e:
            self.logger.error(f"❌ functions.php更新失敗: {e}")
            return False

    async def verify_acf_fields(self, post_type: str = "portfolio") -> Dict[str, Any]:
        """ACFフィールドの表示確認"""
        try:
            # 新規投稿画面へ
            new_post_url = f"{self.wp_url}/wp-admin/post-new.php?post_type={post_type}"
            self.logger.info(f"🔍 投稿画面確認: {new_post_url}")

            await self.page.goto(new_post_url, wait_until="networkidle")
            await asyncio.sleep(3)  # ACFフィールド読み込み待機

            # スクリーンショット
            screenshot_path = "agent_outputs/acf_fields_debug.png"
            await self.page.screenshot(path=screenshot_path)
            self.logger.info(f"📸 スクリーンショット保存: {screenshot_path}")

            # ACFフィールドグループを検索
            acf_fields = await self.page.query_selector_all(".acf-field")
            field_count = len(acf_fields)

            self.logger.info(f"✅ ACFフィールド検出数: {field_count}")

            # フィールド詳細を取得
            field_details = []
            for field in acf_fields[:10]:  # 最初の10フィールド
                label = await field.query_selector(".acf-label label")
                if label:
                    label_text = await label.text_content()
                    field_details.append(label_text.strip())

            return {"found": field_count, "details": field_details, "success": field_count > 0}

        except Exception as e:
            self.logger.error(f"❌ フィールド確認失敗: {e}")
            return {"found": 0, "details": [], "success": False}

    async def execute(self, php_file_path: str) -> Dict[str, Any]:
        """自動設定を実行"""
        results = {"timestamp": datetime.now().isoformat(), "php_file": php_file_path, "steps": {}, "success": False}

        try:
            # ブラウザ起動
            await self.setup_browser()
            results["steps"]["browser_setup"] = True

            # ログイン
            login_success = await self.login_wordpress()
            results["steps"]["login"] = login_success
            if not login_success:
                return results

            # ACFプラグイン確認
            acf_exists = await self.check_acf_plugin()
            results["steps"]["acf_plugin_check"] = acf_exists
            if not acf_exists:
                self.logger.warning("⚠️ ACFプラグインが見つかりません")

            # PHPコードを追加
            php_path = Path(php_file_path)
            if not php_path.exists():
                self.logger.error(f"❌ PHPファイルが見つかりません: {php_file_path}")
                return results

            code_added = await self.add_acf_code_to_functions(php_path)
            results["steps"]["code_added"] = code_added
            if not code_added:
                return results

            # フィールド確認
            verification = await self.verify_acf_fields()
            results["steps"]["fields_verification"] = verification

            # 全体成功判定
            results["success"] = login_success and code_added and verification["success"]

            # サマリー出力
            self.print_summary(results)

            return results

        except Exception as e:
            self.logger.error(f"❌ 実行エラー: {e}")
            results["error"] = str(e)
            return results

        finally:
            if self.browser:
                await self.browser.close()
                self.logger.info("🔒 ブラウザクローズ")

    def print_summary(self, results: Dict[str, Any]):
        """実行サマリーを出力"""
        print("\n" + "=" * 60)
        print("📊 WPAutoConfigAgent 実行結果")
        print("=" * 60)
        print(f"⏰ 実行時刻: {results['timestamp']}")
        print(f"📄 PHPファイル: {results.get('php_file', 'N/A')}")
        print(f"✅ 全体成功: {'成功' if results['success'] else '失敗'}")
        print("\n【ステップ詳細】")

        for step, status in results.get("steps", {}).items():
            if isinstance(status, dict):
                print(f"  📋 {step}:")
                for key, value in status.items():
                    print(f"    - {key}: {value}")
            else:
                icon = "✅" if status else "❌"
                print(f"  {icon} {step}: {status}")

        if "error" in results:
            print(f"\n❌ エラー: {results['error']}")

        print("=" * 60 + "\n")


async def main():
    """メイン実行"""
    print("🚀 WordPress自動設定エージェント v1.2.5 起動")
    print("=" * 60)

    # 実際のACF PHPファイルのパス
    php_file = "agent_outputs/wordpress_acf/php/acf_group_portfolio_details_20251028_212632.php"

    # ファイル存在確認
    if not Path(php_file).exists():
        print(f"❌ エラー: PHPファイルが見つかりません: {php_file}")
        return

    print(f"📄 使用するPHPファイル: {php_file}")
    print(f"✅ ファイル確認完了\n")

    agent = WPAutoConfigAgent()
    results = await agent.execute(php_file)

    # 結果をJSONで保存
    output_file = Path("agent_outputs/wp_auto_config_results.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"💾 結果を保存: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
