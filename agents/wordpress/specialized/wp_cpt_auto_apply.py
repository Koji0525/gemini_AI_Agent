"""
WP CPT Auto Apply Agent v1.0
カスタム投稿タイプのPHPコードをWordPressに自動適用
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from playwright.async_api import async_playwright, Browser, Page

# ロガー設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class WPCPTAutoApply:
    """CPT自動適用エージェント"""

    def __init__(self, wp_url: str, wp_user: str, wp_pass: str):
        self.logger = logging.getLogger("WPCPTAutoApply")
        self.wp_url = wp_url
        self.wp_user = wp_user
        self.wp_pass = wp_pass
        self.browser = None
        self.page = None

    async def setup_browser(self):
        """ブラウザ起動"""
        self.logger.info("ブラウザ起動中...")
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        self.logger.info("✅ ブラウザ起動完了")

    async def login_wordpress(self) -> bool:
        """WordPressログイン"""
        try:
            login_url = f"{self.wp_url}/wp-admin"
            self.logger.info(f"ログイン: {login_url}")

            await self.page.goto(login_url, wait_until="networkidle")
            await self.page.fill('input[name="log"]', self.wp_user)
            await self.page.fill('input[name="pwd"]', self.wp_pass)
            await self.page.click('input[type="submit"]')
            await self.page.wait_for_url("**/wp-admin/**", timeout=10000)

            self.logger.info("✅ ログイン成功")
            return True
        except Exception as e:
            self.logger.error(f"❌ ログイン失敗: {e}")
            return False

    async def add_cpt_to_functions(self, php_file: Path) -> bool:
        """functions.phpにCPTコードを追加"""
        try:
            self.logger.info(f"📄 PHPファイル読み込み: {php_file}")

            with open(php_file, "r", encoding="utf-8") as f:
                cpt_code = f.read()

            # テーマエディターへ
            editor_url = f"{self.wp_url}/wp-admin/theme-editor.php"
            await self.page.goto(editor_url, wait_until="networkidle")

            # テキストエリア待機
            await self.page.wait_for_selector('textarea[name="newcontent"]', state="attached", timeout=10000)

            # 非表示の場合は表示
            await self.page.evaluate(
                """
                const textarea = document.querySelector('textarea[name="newcontent"]');
                if (textarea) {
                    textarea.style.display = 'block';
                    textarea.style.visibility = 'visible';
                }
            """
            )
            await asyncio.sleep(1)

            # 既存コンテンツ取得
            current_content = await self.page.evaluate("document.querySelector('textarea[name=\"newcontent\"]').value")

            # CPTコードが既に存在するか確認
            post_type_name = self._extract_post_type_name(cpt_code)
            if post_type_name and post_type_name in current_content:
                self.logger.warning(f"⚠️ {post_type_name} は既に存在します")
                return True

            # 新しいコードを追加
            new_content = current_content.replace("<?php", f"<?php\n\n{cpt_code}\n", 1)

            # 更新
            await self.page.evaluate(
                f"""
                document.querySelector('textarea[name="newcontent"]').value = `{new_content.replace('`', '\\`')}`;
            """
            )

            # 保存
            self.logger.info("💾 保存中...")
            await self.page.click('input[name="submit"]')
            await asyncio.sleep(2)

            self.logger.info("✅ functions.phpにCPTコード追加完了")
            return True

        except Exception as e:
            self.logger.error(f"❌ CPT追加失敗: {e}")
            return False

    def _extract_post_type_name(self, php_code: str) -> str:
        """PHPコードから投稿タイプ名を抽出"""
        import re

        match = re.search(r"register_post_type\(\s*['\"](\w+)['\"]", php_code)
        return match.group(1) if match else ""

    async def verify_cpt_exists(self, post_type: str) -> bool:
        """CPTが存在するか確認"""
        try:
            new_post_url = f"{self.wp_url}/wp-admin/post-new.php?post_type={post_type}"
            self.logger.info(f"🔍 CPT確認: {new_post_url}")

            await self.page.goto(new_post_url, wait_until="networkidle", timeout=15000)

            # タイトルが表示されているか確認
            title_input = await self.page.query_selector('input[name="post_title"], #title')

            if title_input:
                self.logger.info(f"✅ {post_type} 投稿タイプが正常に動作中")
                return True
            else:
                self.logger.warning(f"⚠️ {post_type} 投稿タイプが見つかりません")
                return False

        except Exception as e:
            self.logger.error(f"❌ CPT確認失敗: {e}")
            return False

    async def execute(self, php_file: str) -> Dict[str, Any]:
        """実行"""
        results = {"timestamp": datetime.now().isoformat(), "php_file": php_file, "steps": {}, "success": False}

        try:
            await self.setup_browser()
            results["steps"]["browser_setup"] = True

            if not await self.login_wordpress():
                return results
            results["steps"]["login"] = True

            php_path = Path(php_file)
            if not php_path.exists():
                self.logger.error(f"❌ ファイル未発見: {php_file}")
                return results

            # CPT追加
            cpt_added = await self.add_cpt_to_functions(php_path)
            results["steps"]["cpt_added"] = cpt_added

            if not cpt_added:
                return results

            # 投稿タイプ名を抽出
            with open(php_path, "r") as f:
                code = f.read()
            post_type = self._extract_post_type_name(code)

            if post_type:
                # CPT確認
                cpt_verified = await self.verify_cpt_exists(post_type)
                results["steps"]["cpt_verified"] = cpt_verified
                results["post_type"] = post_type
                results["success"] = cpt_verified

            return results

        except Exception as e:
            self.logger.error(f"❌ 実行エラー: {e}")
            results["error"] = str(e)
            return results
        finally:
            if self.browser:
                await self.browser.close()
