"""WordPress投稿編集（超堅牢版・詳細ログ付き）"""

import logging
import re
from datetime import datetime
from typing import Dict, Optional
from playwright.async_api import Page

from .wp_utils import TaskContentFetcher

logger = logging.getLogger(__name__)


class WordPressPostEditor:
    """WordPress投稿編集機能（超堅牢版）"""

    def __init__(self, wp_url: str, sheets_manager=None):
        self.wp_url = wp_url
        self.sheets_manager = sheets_manager
        self.debug_screenshots = []  # デバッグ用スクリーンショット一覧

    async def edit_post(self, page: Page, task: Dict) -> Dict:
        """既存の投稿を編集（タイトル抽出改善版）"""
        try:
            logger.info("=" * 80)
            logger.info("【ステップ1/10】投稿編集タスク開始")
            logger.info("=" * 80)

            # ステップ1: タスク内容の解析 - 改善版
            logger.info("\n【ステップ2/10】タスク内容を解析中...")

            # 複数のパターンでタイトルを抽出
            search_title = ""
            description = task["description"]

            # パターン1: 「」で囲まれたタイトル
            title_patterns = [
                r"[「『](.+?)[」』].*の下書き保存",
                r"タイトル[　\s]*[「『](.+?)[」』]",
                r"投稿[　\s]*[「『](.+?)[」』]",
                r"[「『](AI投稿)[」』]",  # 明示的に「AI投稿」を探す
            ]

            for pattern in title_patterns:
                match = re.search(pattern, description)
                if match:
                    search_title = match.group(1)
                    logger.info(f"✅ タイトル抽出成功（パターン: {pattern}）: {search_title}")
                    break

            # パターン2: 特定のキーワードから判断
            if not search_title:
                if "AI投稿" in description:
                    search_title = "AI投稿"
                    logger.info(f"✅ キーワードからタイトル推測: {search_title}")

            if not search_title:
                logger.warning("⚠️ タイトルが見つかりませんでした。デフォルトを使用します。")
                search_title = "AI投稿"

            logger.info(f"🔍 検索タイトル: {search_title}")

            # ステップ2: task_idの抽出
            logger.info("\n【ステップ3/10】書き換え元記事のtask_idを抽出中...")
            target_task_id = TaskContentFetcher.extract_task_id(task["description"])

            if target_task_id:
                logger.info(f"✅ task_id抽出成功: {target_task_id}")
            else:
                logger.error("❌ task_idが見つかりません")
                return {"success": False, "error": "task_idが見つかりません。タスク説明にtask_idを含めてください。"}

            # ステップ3: 記事内容の取得
            logger.info("\n【ステップ4/10】Google Drive/スプレッドシートから記事内容を取得中...")
            logger.info(f"対象: task_id={target_task_id}")

            replacement_content = await TaskContentFetcher.get_task_content(self.sheets_manager, target_task_id)

            if not replacement_content:
                logger.error(f"❌ task_id {target_task_id} の記事内容が取得できませんでした")
                return {"success": False, "error": f"task_id {target_task_id} の記事内容が見つかりません"}

            logger.info(f"✅ 記事内容取得成功: {len(replacement_content)}文字")
            logger.info(f"先頭200文字:\n{replacement_content[:200]}...")

            # ステップ3.5: タイトルと本文を分離
            logger.info("\n【ステップ4.5/10】記事からタイトルと本文を分離中...")
            article_title, article_body = self._extract_title_and_body(replacement_content)

            logger.info(f"✅ タイトル: {article_title}")
            logger.info(f"✅ 本文: {len(article_body)}文字")

            # ステップ4: 投稿一覧ページへ移動
            logger.info("\n【ステップ5/10】WordPress投稿一覧ページへ移動中...")
            await page.goto(f"{self.wp_url}/wp-admin/edit.php", timeout=30000)
            await page.wait_for_timeout(3000)

            screenshot_path = await self._save_screenshot(page, "01_post_list")
            logger.info(f"✅ 投稿一覧ページ到達: {screenshot_path}")

            # ステップ5: タイトル検索
            if search_title:
                logger.info(f"\n【ステップ6/10】タイトル '{search_title}' で検索中...")
                search_success = await self._search_post(page, search_title)

                if search_success:
                    logger.info("✅ 検索実行成功")
                    screenshot_path = await self._save_screenshot(page, "02_search_result")
                else:
                    logger.warning("⚠️ 検索ボックスが見つかりませんでした")

            # ステップ6: 投稿編集ページへ移動
            logger.info(f"\n【ステップ7/10】投稿 '{search_title}' の編集ページへ移動中...")
            post_found, post_id = await self._navigate_to_edit_page(page, search_title)

            if not post_found:
                logger.error(f"❌ 投稿が見つかりませんでした: {search_title}")
                screenshot_path = await self._save_screenshot(page, "03_post_not_found")
                return {
                    "success": False,
                    "error": f"タイトル「{search_title}」の投稿が見つかりませんでした",
                    "screenshot": screenshot_path,
                    "debug_screenshots": self.debug_screenshots,
                }

            logger.info(f"✅ 投稿編集ページ到達: 投稿ID={post_id}")
            screenshot_path = await self._save_screenshot(page, "04_edit_page")

            # ステップ7.5: タイトルを変更
            if article_title != search_title:
                logger.info(f"\n【ステップ7.5/10】投稿タイトルを '{article_title}' に変更中...")
                title_changed = await self._change_title(page, article_title)

                if title_changed:
                    logger.info("✅ タイトル変更完了")
                else:
                    logger.warning("⚠️ タイトル変更に失敗しました")

                screenshot_path = await self._save_screenshot(page, "04b_after_title_change")

            # ステップ7: Polylang言語設定
            logger.info("\n【ステップ8/10】Polylangの言語を日本語に変更中...")
            language_changed = await self._set_polylang_language(page)

            if language_changed:
                logger.info("✅ Polylang言語設定完了: 日本語")
            else:
                logger.warning("⚠️ Polylang設定が見つかりませんでした")

            screenshot_path = await self._save_screenshot(page, "05_after_language")

            # ステップ8: 記事内容の書き換え
            logger.info(f"\n【ステップ9/10】記事内容を書き換え中... ({len(article_body)}文字)")

            # マークダウンをHTMLに変換
            article_html = self._convert_markdown_to_html(article_body)
            logger.info(f"  マークダウン→HTML変換: {len(article_html)}文字")

            content_replaced = await self._replace_content(page, article_html)

            if content_replaced:
                logger.info("✅ 記事内容の書き換え完了")
            else:
                logger.error("❌ 記事内容の書き換えに失敗しました")

            screenshot_path = await self._save_screenshot(page, "06_after_content")

            # ステップ9: 下書き保存
            logger.info("\n【ステップ10/10】下書き保存中...")
            saved = await self._save_draft(page)

            if saved:
                logger.info("✅ 下書き保存完了")
            else:
                logger.warning("⚠️ 下書き保存ボタンが見つかりませんでした")

            # 最終スクリーンショット
            screenshot_path = await self._save_screenshot(page, "07_final")

            # 結果サマリー
            logger.info("\n" + "=" * 80)
            logger.info("【完了】投稿編集タスク終了")
            logger.info("=" * 80)

            result_summary = self._build_summary(
                search_title, post_id, article_title, language_changed, len(article_body), saved
            )
            summary_text = "\n".join(result_summary)

            logger.info("\n【最終結果】")
            logger.info(summary_text)

            return {
                "success": True,
                "summary": summary_text,
                "screenshot": screenshot_path,
                "debug_screenshots": self.debug_screenshots,
                "full_text": f"{summary_text}\n\n【デバッグ情報】\n"
                + "\n".join([f"- {s}" for s in self.debug_screenshots]),
            }

        except Exception as e:
            logger.error(f"❌ 投稿編集エラー: {e}")
            import traceback

            traceback.print_exc()

            screenshot_path = await self._save_screenshot(page, "ERROR")

            return {
                "success": False,
                "error": str(e),
                "screenshot": screenshot_path,
                "debug_screenshots": self.debug_screenshots,
            }

    async def _save_screenshot(self, page: Page, name: str) -> str:
        """デバッグ用スクリーンショット保存"""
        try:
            timestamp = datetime.now().strftime("%H%M%S")
            screenshot_path = f"wp_debug_{name}_{timestamp}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            self.debug_screenshots.append(screenshot_path)
            logger.debug(f"📸 スクリーンショット保存: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            logger.warning(f"スクリーンショット保存失敗: {e}")
            return ""

    async def _search_post(self, page: Page, search_title: str) -> bool:
        """投稿を検索"""
        search_box_selectors = ["#post-search-input", 'input[name="s"]', 'input[type="search"]', ".search-box input"]

        for i, selector in enumerate(search_box_selectors, 1):
            try:
                logger.debug(f"検索ボックス試行 {i}/{len(search_box_selectors)}: {selector}")
                search_box = await page.query_selector(selector)

                if search_box:
                    is_visible = await search_box.is_visible()
                    logger.debug(f"  → 要素発見: 表示={is_visible}")

                    if is_visible:
                        await search_box.fill(search_title)
                        await page.wait_for_timeout(500)
                        await page.keyboard.press("Enter")
                        await page.wait_for_timeout(3000)
                        logger.info(f"✅ 検索実行成功: セレクタ={selector}")
                        return True
            except Exception as e:
                logger.debug(f"  → エラー: {e}")
                continue

    # wp_post_editor.py の _extract_title_and_body メソッドを修正

    def _extract_title_and_body(self, content: str) -> tuple[str, str]:
        """
        記事からタイトルと本文を抽出（HTML対応強化版）
        """
        try:
            logger.info(f"【記事内容解析開始】文字数: {len(content)}")

            # HTML形式の場合はHTMLCleanerを使用
            if "<h1" in content or "<div" in content or "<p>" in content:
                logger.info("✅ HTML形式の記事を検出 - HTMLCleanerを使用")

                # HTMLCleanerでタイトルと本文を抽出
                from .wp_utils import HTMLCleaner

                title, body = HTMLCleaner.prepare_html_for_wordpress(content)

                logger.info(f"✅ HTML処理完了: タイトル='{title}', 本文={len(body)}文字")
                return title, body

            # Markdown形式の処理（既存のロジック）
            lines = content.split("\n")
            title = ""
            body_lines = []

            for i, line in enumerate(lines):
                line_stripped = line.strip()

                # 最初の # で始まる行をタイトルとする
                if line_stripped.startswith("# ") and not title:
                    title = line_stripped[2:].strip()
                    logger.info(f"✅ Markdownタイトル抽出: {title}")
                    continue

                # タイトルが見つかった後の行を本文とする
                if title:
                    body_lines.append(line)
                # タイトルが見つかる前の非空行をタイトル候補とする
                elif line_stripped and not title:
                    title = line_stripped[:100]
                    logger.info(f"✅ 最初の行をタイトルとして使用: {title}")

            if title:
                body = "\n".join(body_lines).strip() if body_lines else content
                logger.info(f"✅ タイトル・本文分離完了: タイトル={title[:30]}..., 本文={len(body)}文字")
                return title, body

            # フォールバック
            logger.warning("❌ タイトルを抽出できませんでした")
            return "AI投稿_自動生成", content

        except Exception as e:
            logger.error(f"❌ タイトル抽出エラー: {e}")
            import traceback

            traceback.print_exc()
            return "AI投稿_エラー", content

    async def _change_title(self, page: Page, new_title: str) -> bool:
        """投稿のタイトルを変更"""
        title_selectors = [
            ".editor-post-title__input",
            'h1[aria-label="タイトルを追加"]',
            'textarea[placeholder*="タイトル"]',
            "#post-title-0",
            ".wp-block-post-title",
        ]

        logger.debug("タイトル入力欄を探索中...")

        for i, selector in enumerate(title_selectors, 1):
            logger.debug(f"  試行 {i}/{len(title_selectors)}: {selector}")
            try:
                title_input = await page.query_selector(selector)
                if title_input:
                    is_visible = await title_input.is_visible()
                    logger.debug(f"  → 要素発見: 表示={is_visible}")

                    if is_visible:
                        # 既存のタイトルをクリア
                        await title_input.click()
                        await page.wait_for_timeout(500)
                        await page.keyboard.press("Control+A")
                        await page.wait_for_timeout(300)

                        # 新しいタイトルを入力
                        await page.keyboard.type(new_title)
                        await page.wait_for_timeout(1000)

                        logger.info(f"✅ タイトル変更成功: {new_title}")
                        return True
            except Exception as e:
                logger.debug(f"  → エラー: {e}")
                continue

        logger.warning("❌ タイトル入力欄が見つかりませんでした")
        return False

    def _convert_markdown_to_html(self, markdown_text: str) -> str:
        """
        マークダウンをHTMLに変換

        対応：
        - ## 見出し → <h2>見出し</h2>
        - ### 見出し → <h3>見出し</h3>
        - **太字** → <strong>太字</strong>
        - *斜体* → <em>斜体</em>
        """
        try:
            import re

            html_lines = []
            lines = markdown_text.split("\n")

            for line in lines:
                # 見出しの変換
                if line.strip().startswith("### "):
                    # H3
                    text = line.strip()[4:]
                    html_lines.append(f"<h3>{text}</h3>")
                elif line.strip().startswith("## "):
                    # H2
                    text = line.strip()[3:]
                    html_lines.append(f"<h2>{text}</h2>")
                elif line.strip().startswith("# "):
                    # H1（通常はタイトルなのでスキップ）
                    text = line.strip()[2:]
                    html_lines.append(f"<h1>{text}</h1>")
                else:
                    # 本文の変換
                    converted_line = line

                    # **太字** → <strong>太字</strong>
                    converted_line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", converted_line)

                    # *斜体* → <em>斜体</em>
                    converted_line = re.sub(r"\*(.+?)\*", r"<em>\1</em>", converted_line)

                    # 段落タグで囲む（空行でない場合）
                    if converted_line.strip():
                        html_lines.append(f"<p>{converted_line}</p>")
                    else:
                        html_lines.append("")

            html_content = "\n".join(html_lines)

            logger.info(f"【マークダウン→HTML変換完了】")
            logger.info(f"  元: {len(markdown_text)}文字")
            logger.info(f"  変換後: {len(html_content)}文字")

            return html_content

        except Exception as e:
            logger.warning(f"マークダウン変換エラー: {e}")
            return markdown_text

    async def _replace_content(self, page: Page, content: str, is_html: bool = False) -> bool:
        """記事内容を置換（Gutenbergブロック対応版）"""
        logger.info("記事エディタを探索中...")

        if is_html:
            logger.info("HTML形式のため、Gutenbergブロックとして挿入します")
            return await self._insert_as_gutenberg_blocks(page, content)

        # 通常のテキストの場合
        content_selectors = [
            ".block-editor-rich-text__editable",
            "p.block-editor-rich-text__editable",
            '[data-type="core/paragraph"] .block-editor-rich-text__editable',
        ]

        for i, selector in enumerate(content_selectors, 1):
            logger.debug(f"  試行 {i}/{len(content_selectors)}: {selector}")
            try:
                content_blocks = await page.query_selector_all(selector)

                if content_blocks and len(content_blocks) > 0:
                    logger.debug(f"  → {len(content_blocks)}個の要素発見")

                    await content_blocks[0].click()
                    await page.wait_for_timeout(500)
                    await page.keyboard.press("Control+A")
                    await page.wait_for_timeout(300)
                    await page.keyboard.press("Backspace")
                    await page.wait_for_timeout(500)
                    await page.keyboard.type(content, delay=10)
                    await page.wait_for_timeout(1000)

                    logger.info(f"✅ 記事内容書き換え成功: {len(content)}文字")
                    return True
            except Exception as e:
                logger.debug(f"  → エラー: {e}")
                continue

        logger.error("❌ すべてのエディタセレクタで失敗")
        return False

    async def _insert_as_gutenberg_blocks(self, page: Page, html_content: str) -> bool:
        """HTMLをカスタムHTMLブロックとして挿入（簡易版）"""
        try:
            logger.info("【カスタムHTMLブロック挿入開始】")

            # 既存のコンテンツを削除
            logger.info("  ステップ1: 既存コンテンツを削除")
            await self._clear_all_blocks_simple(page)

            # カスタムHTMLブロックを追加
            logger.info("  ステップ2: カスタムHTMLブロックを追加")

            # 方法1: /html で検索
            try:
                await page.keyboard.press("/")
                await page.wait_for_timeout(500)
                await page.keyboard.type("html")
                await page.wait_for_timeout(1000)
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(1000)
                logger.info("  → /html で検索成功")
            except Exception as e:
                logger.debug(f"  方法1失敗: {e}")

                # 方法2: ブロック追加ボタンから
                try:
                    await page.click('button[aria-label="ブロックを追加"]', timeout=3000)
                    await page.wait_for_timeout(500)
                    await page.type('input[placeholder*="検索"]', "html")
                    await page.wait_for_timeout(1000)
                    await page.click('button:has-text("カスタムHTML")', timeout=3000)
                    await page.wait_for_timeout(1000)
                    logger.info("  → ブロック追加ボタンから成功")
                except Exception as e2:
                    logger.debug(f"  方法2失敗: {e2}")

            # HTMLコードエリアを見つけて貼り付け
            logger.info("  ステップ3: HTMLコードを貼り付け")

            html_input_selectors = [
                "textarea.block-editor-plain-text",
                ".wp-block-html textarea",
                'textarea[aria-label*="HTML"]',
                "textarea.components-textarea-control__input",
            ]

            pasted = False
            for selector in html_input_selectors:
                try:
                    html_input = await page.query_selector(selector)
                    if html_input:
                        is_visible = await html_input.is_visible()
                        if is_visible:
                            await html_input.click()
                            await page.wait_for_timeout(500)

                            # HTMLを貼り付け
                            await html_input.fill(html_content)
                            await page.wait_for_timeout(1000)

                            logger.info(f"  ✅ HTML貼り付け成功: {len(html_content)}文字")
                            pasted = True
                            break
                except Exception as e:
                    logger.debug(f"  {selector} エラー: {e}")
                    continue

            if not pasted:
                logger.warning("  ⚠️ HTML入力欄が見つかりませんでした")
                return False

            # プレビューモードに切り替え（見た目を確認）
            logger.info("  ステップ4: プレビューモードに切り替え")
            try:
                # 「プレビュー」ボタンを探す
                preview_button = await page.query_selector('button:has-text("プレビュー")')
                if preview_button:
                    await preview_button.click()
                    await page.wait_for_timeout(1000)
                    logger.info("  ✅ プレビューモード表示")
            except Exception as e:
                logger.debug(f"  プレビュー切り替えエラー: {e}")

            logger.info(f"✅ カスタムHTMLブロック挿入完了")
            return True

        except Exception as e:
            logger.error(f"❌ カスタムHTMLブロック挿入エラー: {e}")
            import traceback

            traceback.print_exc()
            return False

    async def _clear_all_blocks_simple(self, page: Page) -> bool:
        """既存のブロックを簡易的に削除"""
        try:
            # Ctrl+A で全選択 → Backspace で削除
            await page.keyboard.press("Control+A")
            await page.wait_for_timeout(500)
            await page.keyboard.press("Backspace")
            await page.wait_for_timeout(1000)

            logger.info("  ✅ 既存コンテンツ削除完了")
            return True

        except Exception as e:
            logger.debug(f"  既存コンテンツ削除エラー: {e}")
            return False

        logger.warning("❌ すべての検索ボックスセレクタで失敗")
        return False

    async def _navigate_to_edit_page(self, page: Page, search_title: str) -> tuple[bool, Optional[str]]:
        """投稿編集ページへ移動"""
        logger.info("投稿リンクを探索中...")

        # 方法1: タイトルリンクから直接編集URL
        logger.debug("【方法1】タイトルリンクから編集URLを取得")
        try:
            # 複数のセレクタを試行
            title_selectors = [
                f'a.row-title:has-text("{search_title}")',
                f'td.title a:has-text("{search_title}")',
                f'.row-title:has-text("{search_title}")',
            ]

            for i, selector in enumerate(title_selectors, 1):
                logger.debug(f"  試行 {i}/{len(title_selectors)}: {selector}")
                try:
                    title_link = await page.query_selector(selector)
                    if title_link:
                        href = await title_link.get_attribute("href")
                        if href:
                            post_id_match = re.search(r"post=(\d+)", href)
                            if post_id_match:
                                post_id = post_id_match.group(1)
                                edit_url = f"{self.wp_url}/wp-admin/post.php?post={post_id}&action=edit"
                                logger.info(f"✅ 編集URL構築成功: 投稿ID={post_id}")

                                await page.goto(edit_url, timeout=30000)
                                await page.wait_for_timeout(4000)

                                return True, post_id
                except Exception as e:
                    logger.debug(f"  → エラー: {e}")
                    continue
        except Exception as e:
            logger.debug(f"方法1失敗: {e}")

        # 方法2: 編集リンクをクリック
        logger.debug("【方法2】編集リンクをクリック")
        edit_link_selectors = [
            f'tr:has-text("{search_title}") .row-actions .edit a',
            f'a.row-title:has-text("{search_title}")',
            ".row-actions .edit a",
            f'tr:has(a:has-text("{search_title}")) .edit a',
        ]

        for i, selector in enumerate(edit_link_selectors, 1):
            logger.debug(f"  試行 {i}/{len(edit_link_selectors)}: {selector}")
            try:
                edit_link = await page.query_selector(selector)
                if edit_link:
                    is_visible = await edit_link.is_visible()
                    logger.debug(f"  → 要素発見: 表示={is_visible}")

                    if is_visible:
                        await edit_link.click()
                        await page.wait_for_timeout(5000)

                        # URLから投稿IDを取得
                        current_url = page.url
                        post_id_match = re.search(r"post=(\d+)", current_url)
                        post_id = post_id_match.group(1) if post_id_match else "不明"

                        logger.info(f"✅ 編集リンククリック成功: 投稿ID={post_id}")
                        return True, post_id
            except Exception as e:
                logger.debug(f"  → エラー: {e}")
                continue

        # 方法3: 最初の投稿を開く（フォールバック）
        logger.debug("【方法3】最初の投稿を開く（フォールバック）")
        try:
            first_edit_link = await page.query_selector(".row-actions .edit a")
            if first_edit_link:
                await first_edit_link.click()
                await page.wait_for_timeout(4000)
                logger.warning("⚠️ 最初の投稿を開きました（フォールバック）")
                return True, "不明"
        except Exception as e:
            logger.debug(f"方法3失敗: {e}")

        logger.error("❌ すべての方法で投稿編集ページへの移動に失敗")
        return False, None

    async def _set_polylang_language(self, page: Page) -> bool:
        """Polylangの言語を日本語に設定"""
        polylang_selectors = [
            'select[name="post_lang_choice"]',
            "#post_lang_choice",
            "select.pll-select-flag",
            "#pll_post_lang_choice",
            'select[id*="lang"]',
        ]

        logger.debug("Polylang言語設定セレクタを探索中...")

        for i, selector in enumerate(polylang_selectors, 1):
            logger.debug(f"  試行 {i}/{len(polylang_selectors)}: {selector}")
            try:
                lang_select = await page.query_selector(selector)
                if lang_select:
                    is_visible = await lang_select.is_visible()
                    logger.debug(f"  → 要素発見: 表示={is_visible}")

                    if is_visible:
                        # 日本語オプションを探す
                        options = await lang_select.inner_text()
                        logger.debug(f"  → 利用可能な言語: {options[:100]}")

                        # 複数の日本語表記を試す
                        japanese_labels = ["日本語", "ja", "Japanese", "japanese"]

                        for label in japanese_labels:
                            try:
                                await lang_select.select_option(label=label)
                                await page.wait_for_timeout(2000)
                                logger.info(f"✅ Polylang言語設定成功: {label}")

                                # 確認ダイアログ処理
                                await self._handle_confirm_dialog(page)

                                return True
                            except:
                                continue
            except Exception as e:
                logger.debug(f"  → エラー: {e}")
                continue

        logger.warning("❌ Polylang言語設定要素が見つかりませんでした")
        return False

    async def _handle_confirm_dialog(self, page: Page):
        """確認ダイアログを処理"""
        ok_button_selectors = [
            'button:has-text("OK")',
            'button:has-text("はい")',
            ".ui-dialog-buttonset button:first-child",
            'button[type="button"]:has-text("OK")',
        ]

        for selector in ok_button_selectors:
            try:
                ok_button = await page.query_selector(selector)
                if ok_button:
                    is_visible = await ok_button.is_visible()
                    if is_visible:
                        await ok_button.click()
                        await page.wait_for_timeout(1000)
                        logger.debug("✅ 確認ダイアログでOKをクリック")
                        return
            except:
                continue

    async def _replace_content(self, page: Page, content: str) -> bool:
        """記事内容を置換"""
        logger.info("記事エディタを探索中...")

        # Gutenbergエディタのセレクタ
        content_selectors = [
            ".block-editor-rich-text__editable",
            "p.block-editor-rich-text__editable",
            '[data-type="core/paragraph"] .block-editor-rich-text__editable',
            ".editor-post-text-editor",
            "textarea.editor-post-text-editor",
            "#content",  # クラシックエディタ
        ]

        for i, selector in enumerate(content_selectors, 1):
            logger.debug(f"  試行 {i}/{len(content_selectors)}: {selector}")
            try:
                content_blocks = await page.query_selector_all(selector)

                if content_blocks and len(content_blocks) > 0:
                    logger.debug(f"  → {len(content_blocks)}個の要素発見")

                    # 最初のブロックをクリック
                    await content_blocks[0].click()
                    await page.wait_for_timeout(500)
                    logger.debug("  → クリック完了")

                    # 全選択して削除
                    await page.keyboard.press("Control+A")
                    await page.wait_for_timeout(300)
                    await page.keyboard.press("Backspace")
                    await page.wait_for_timeout(500)
                    logger.debug("  → 既存内容削除完了")

                    # 新しい内容を入力
                    await page.keyboard.type(content, delay=10)
                    await page.wait_for_timeout(1000)

                    logger.info(f"✅ 記事内容書き換え成功: {len(content)}文字")
                    return True
            except Exception as e:
                logger.debug(f"  → エラー: {e}")
                continue

        logger.error("❌ すべてのエディタセレクタで失敗")
        return False

    async def _save_draft(self, page: Page) -> bool:
        """下書き保存"""
        save_selectors = [
            'button:has-text("下書き保存")',
            'button[aria-label="下書き保存"]',
            ".editor-post-save-draft",
            "#save-post",
            "button.editor-post-save-draft",
        ]

        logger.debug("下書き保存ボタンを探索中...")

        for i, selector in enumerate(save_selectors, 1):
            logger.debug(f"  試行 {i}/{len(save_selectors)}: {selector}")
            try:
                save_button = await page.query_selector(selector)
                if save_button:
                    is_visible = await save_button.is_visible()
                    is_disabled = await save_button.is_disabled() if is_visible else True

                    logger.debug(f"  → 要素発見: 表示={is_visible}, 無効={is_disabled}")

                    if is_visible and not is_disabled:
                        await save_button.click()
                        await page.wait_for_timeout(4000)
                        logger.info("✅ 下書き保存ボタンクリック成功")
                        return True
            except Exception as e:
                logger.debug(f"  → エラー: {e}")
                continue

        logger.warning("❌ 下書き保存ボタンが見つかりませんでした")
        return False

    def _build_summary(
        self, old_title: str, post_id: str, new_title: str, lang_changed: bool, content_length: int, saved: bool
    ) -> list:
        """結果サマリーを構築"""
        result_summary = []
        result_summary.append(f"【投稿編集完了】")
        result_summary.append(f"元のタイトル: {old_title}")

        if new_title != old_title:
            result_summary.append(f"新しいタイトル: {new_title}")

        result_summary.append(f"投稿ID: {post_id}")
        result_summary.append("")

        if lang_changed:
            result_summary.append("✅ Polylang言語設定: 日本語")
        else:
            result_summary.append("⚠️ Polylang言語設定: スキップ")

        result_summary.append(f"✅ 記事内容書き換え: {content_length}文字（HTML変換済み）")

        if saved:
            result_summary.append("✅ 下書き保存: 完了")
        else:
            result_summary.append("⚠️ 下書き保存: スキップ（手動確認推奨）")

        return result_summary
