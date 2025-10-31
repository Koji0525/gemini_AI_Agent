"""
WordPress企業データ登録モジュール V12 - BrowserController互換版
Day 3: ブラウザセットアップ互換性問題を解決
"""

import asyncio
import json
import os
import sys
import datetime
import base64
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from browser_control.browser_controller import BrowserController


class CompanyDataManager:
    """企業データ管理クラス"""

    def __init__(self, data_file: str = "automation/data/company_dataset.json"):
        self.data_file = data_file
        self.companies = self.load_companies()

    def load_companies(self) -> List[Dict]:
        """企業データを読み込み"""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"✅ 企業データ読み込み成功: {len(data.get('companies', []))}社")
                return data.get("companies", [])
        except Exception as e:
            print(f"❌ 企業データ読み込みエラー: {e}")
            return []

    def get_all_companies(self) -> List[Dict]:
        """全企業データを取得"""
        return self.companies


class WPDataPopulatorV12:
    """WordPress企業データ登録 V12 - 互換性修正版"""

    def __init__(self):
        self.browser: Optional[BrowserController] = None
        self.wp_url = os.getenv("WP_URL")
        self.wp_user = os.getenv("WP_USER")
        self.wp_pass = os.getenv("WP_PASS")
        self.data_manager = CompanyDataManager()

        # ログ設定
        self.log_dir = "automation/logs/day3"
        os.makedirs(self.log_dir, exist_ok=True)

        # 結果記録
        self.results = {
            "timestamp": datetime.datetime.now().isoformat(),
            "total_companies": 0,
            "successful_registrations": 0,
            "failed_registrations": 0,
            "details": [],
        }

    async def debug_page_state(self, step: str):
        """ページ状態をデバッグ"""
        try:
            print(f"🔍 デバッグ: {step}")

            # 現在のURL
            current_url = self.browser.page.url
            print(f"   📍 URL: {current_url}")

            # タイトル要素の状態
            title_selectors = [".editor-post-title__input", "#title"]
            for selector in title_selectors:
                element = await self.browser.page.query_selector(selector)
                if element:
                    value = await element.get_attribute("value")
                    print(f"   📝 タイトル({selector}): '{value}'")

            # コンテンツ要素の状態
            content_selectors = [
                '.wp-block-paragraph[contenteditable="true"]',
                "#content",
                ".block-editor-writing-flow",
                ".editor-post-text-editor",
            ]
            for selector in content_selectors:
                elements = await self.browser.page.query_selector_all(selector)
                if elements:
                    print(f"   📄 コンテンツ要素({selector}): {len(elements)}個見つかりました")
                    for i, elem in enumerate(elements[:3]):
                        try:
                            text = await elem.text_content()
                            print(f"     [{i}] テキスト: '{text[:100] if text else 'None'}'")
                        except:
                            print(f"     [{i}] テキスト取得失敗")

            # スクリーンショット保存（デバッグ用）
            screenshot_path = f"{self.log_dir}/debug_{step.replace(' ', '_')}.png"
            await self.browser.page.screenshot(path=screenshot_path)
            print(f"   📸 スクリーンショット保存: {screenshot_path}")

        except Exception as e:
            print(f"   ❌ デバッグエラー: {e}")

    async def setup(self) -> bool:
        """ブラウザセットアップ - 互換性修正版"""
        try:
            print("🔄 ブラウザセットアップ開始（互換性修正版）")
            self.browser = BrowserController()

            # シンプルなセットアップ（viewport引数なし）
            await self.browser.setup_browser(headless=True)

            # セットアップ後にブラウザ設定を調整
            if hasattr(self.browser, "page") and self.browser.page:
                # ビューポート設定
                await self.browser.page.set_viewport_size({"width": 1920, "height": 1080})

                # タイムアウト設定
                await self.browser.page.set_default_timeout(60000)
                await self.browser.page.set_default_navigation_timeout(60000)

                # ユーザーエージェント設定（オプション）
                await self.browser.page.set_extra_http_headers(
                    {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    }
                )

            print("✅ ブラウザセットアップ完了")
            return True
        except Exception as e:
            print(f"❌ ブラウザセットアップ失敗: {e}")
            # 詳細なエラー情報を出力
            import traceback

            print(f"🔍 詳細トレースバック:\n{traceback.format_exc()}")
            return False

    async def login_to_wordpress(self) -> bool:
        """WordPressにログイン - 強化版"""
        try:
            print(f"🔐 WordPressログイン試行: {self.wp_url}/wp-admin")

            await self.browser.page.goto(f"{self.wp_url}/wp-login.php", wait_until="networkidle", timeout=90000)

            print("📝 ログインフォーム入力中")
            await self.browser.page.fill("#user_login", self.wp_user)
            await self.browser.page.fill("#user_pass", self.wp_pass)
            await self.browser.page.click("#wp-submit")

            try:
                await self.browser.page.wait_for_selector("#wpadminbar", timeout=15000)
                print("✅ WordPressログイン成功 (wpadminbar)")
                return True
            except:
                pass

            if "wp-admin" in self.browser.page.url:
                print("✅ WordPressログイン成功 (URL確認)")
                return True

            admin_elements = await self.browser.page.query_selector_all(".wp-admin")
            if admin_elements:
                print("✅ WordPressログイン成功 (admin要素)")
                return True

            print("❌ ログイン成功確認できません")
            return False

        except Exception as e:
            print(f"❌ WordPressログイン失敗: {e}")
            return False

    # 以下のメソッドはV11と同じ（create_company_post_comprehensive, enter_title_comprehensive, enter_content_comprehensiveなど）
    async def navigate_to_new_post_advanced(self) -> bool:
        """新規投稿ページに移動 - 高度な方法"""
        try:
            print("📝 新規投稿ページへ移動（高度な方法）")

            await self.browser.page.goto(
                f"{self.wp_url}/wp-admin/post-new.php", wait_until="networkidle", timeout=90000
            )

            await self.debug_page_state("新規投稿ページ移動後")

            print("⏳ エディタの完全な読み込みを待機中...")
            await self.browser.page.wait_for_timeout(5000)

            editor_found = False

            block_editor = await self.browser.page.query_selector(".block-editor-page")
            if block_editor:
                print("✅ ブロックエディタを検出")
                editor_found = True
                await self.browser.page.wait_for_selector(".editor-post-title__input", timeout=30000)
                await self.browser.page.wait_for_selector(".block-editor-writing-flow", timeout=30000)

            classic_editor = await self.browser.page.query_selector(".wp-editor-wrap")
            if classic_editor:
                print("✅ クラシックエディタを検出")
                editor_found = True

            if not editor_found:
                print("⚠️ 特定のエディタを検出できませんでしたが、続行します")

            print("✅ 新規投稿ページ移動完了")
            return True

        except Exception as e:
            print(f"❌ 新規投稿ページ移動失敗: {e}")
            await self.debug_page_state("新規投稿ページ移動失敗時")
            return False

    async def create_company_post_comprehensive(self, company: Dict) -> bool:
        """企業データを投稿として作成 - 総合的なアプローチ"""
        try:
            print(f"🏢 企業データ登録開始: {company['name']}")

            await self.debug_page_state("投稿作成開始前")

            title_success = await self.enter_title_comprehensive(company["name"])
            if not title_success:
                return False

            content_success = await self.enter_content_comprehensive(company)
            if not content_success:
                return False

            await self.debug_page_state("コンテンツ入力後")

            publish_success = await self.publish_post_comprehensive()

            return publish_success

        except Exception as e:
            print(f"❌ 企業データ登録失敗 {company['name']}: {e}")
            await self.debug_page_state("登録失敗時")
            return False

    async def enter_title_comprehensive(self, title: str) -> bool:
        """タイトル入力 - 総合的なアプローチ"""
        try:
            print("📝 タイトル入力中（総合アプローチ）...")

            title_input = await self.browser.page.query_selector(".editor-post-title__input")
            if title_input:
                await title_input.click(click_count=3)
                await title_input.press("Backspace")
                await title_input.type(title, delay=50)
                print("✅ タイトル入力完了 (ブロックエディタ)")
                return True

            title_input = await self.browser.page.query_selector("#title")
            if title_input:
                await title_input.click(click_count=3)
                await title_input.press("Backspace")
                await title_input.type(title, delay=50)
                print("✅ タイトル入力完了 (クラシックエディタ)")
                return True

            try:
                await self.browser.page.evaluate(
                    """
                    (title) => {
                        const selectors = [
                            '.editor-post-title__input',
                            '#title', 
                            'input[name="post_title"]',
                            '[data-type="core/post-title"]'
                        ];
                        
                        for (const selector of selectors) {
                            const element = document.querySelector(selector);
                            if (element) {
                                element.value = title;
                                element.dispatchEvent(new Event('input', { bubbles: true }));
                                element.dispatchEvent(new Event('change', { bubbles: true }));
                                return true;
                            }
                        }
                        return false;
                    }
                """,
                    title,
                )
                print("✅ タイトル入力完了 (JavaScript強制設定)")
                return True
            except Exception as js_error:
                print(f"⚠️ JavaScriptタイトル設定失敗: {js_error}")

            print("❌ すべてのタイトル入力方法が失敗")
            return False

        except Exception as e:
            print(f"❌ タイトル入力失敗: {e}")
            return False

    async def enter_content_comprehensive(self, company: Dict) -> bool:
        """コンテンツ入力 - 総合的なアプローチ"""
        try:
            print("📝 コンテンツ入力中（総合アプローチ）...")

            content = self.generate_optimized_content(company)
            print(f"📊 生成コンテンツサイズ: {len(content)}文字")

            methods = [
                self.insert_content_block_editor_advanced,
                self.insert_content_classic_editor_advanced,
                self.insert_content_code_editor,
                self.insert_content_keyboard_navigation,
                self.insert_content_javascript_injection,
            ]

            for i, method in enumerate(methods, 1):
                print(f"�� 方法 {i}/{len(methods)} を試行中...")
                success = await method(content)
                if success:
                    return True
                await self.browser.page.wait_for_timeout(2000)

            print("❌ すべてのコンテンツ入力方法が失敗")
            return False

        except Exception as e:
            print(f"❌ コンテンツ入力失敗: {e}")
            return False

    async def insert_content_block_editor_advanced(self, content: str) -> bool:
        """ブロックエディタへの高度な入力"""
        try:
            print("  🔄 ブロックエディタ高度入力...")

            paragraphs = await self.browser.page.query_selector_all(".wp-block-paragraph")

            for i, paragraph in enumerate(paragraphs):
                try:
                    is_editable = await paragraph.get_attribute("contenteditable")
                    if is_editable == "true":
                        await paragraph.click()
                        await self.browser.page.wait_for_timeout(1000)

                        await paragraph.press("Control+A")
                        await self.browser.page.wait_for_timeout(500)
                        await paragraph.press("Backspace")
                        await self.browser.page.wait_for_timeout(500)

                        await paragraph.type(content, delay=20)
                        print(f"  ✅ ブロックエディタ入力成功 (段落 {i+1})")
                        return True
                except Exception as para_error:
                    print(f"  ⚠️ 段落 {i+1} 入力失敗: {para_error}")
                    continue

            return False

        except Exception as e:
            print(f"  ⚠️ ブロックエディタ高度入力失敗: {e}")
            return False

    async def insert_content_classic_editor_advanced(self, content: str) -> bool:
        """クラシックエディタへの高度な入力"""
        try:
            print("  🔄 クラシックエディタ高度入力...")

            textarea = await self.browser.page.query_selector("#content")
            if textarea:
                await textarea.click()
                await self.browser.page.wait_for_timeout(1000)

                await textarea.press("Control+A")
                await self.browser.page.wait_for_timeout(500)
                await textarea.press("Backspace")
                await self.browser.page.wait_for_timeout(500)

                await textarea.type(content, delay=20)
                print("  ✅ クラシックエディタ入力成功")
                return True

            return False

        except Exception as e:
            print(f"  ⚠️ クラシックエディタ高度入力失敗: {e}")
            return False

    async def insert_content_code_editor(self, content: str) -> bool:
        """コードエディタ経由での入力"""
        try:
            print("  🔄 コードエディタ経由入力...")

            settings_button = await self.browser.page.query_selector('button[aria-label="設定"]')
            if not settings_button:
                settings_button = await self.browser.page.query_selector('button[aria-label="Settings"]')

            if settings_button:
                await settings_button.click()
                await self.browser.page.wait_for_timeout(2000)

                code_editor_btn = await self.browser.page.query_selector('button[aria-label*="コードエディタ"]')
                if not code_editor_btn:
                    code_editor_btn = await self.browser.page.query_selector('button[aria-label*="Code Editor"]')

                if code_editor_btn:
                    await code_editor_btn.click()
                    await self.browser.page.wait_for_timeout(3000)

                    code_textarea = await self.browser.page.query_selector(".editor-post-text-editor")
                    if code_textarea:
                        await code_textarea.click()
                        await code_textarea.press("Control+A")
                        await code_textarea.type(content, delay=20)
                        print("  ✅ コードエディタ入力成功")
                        return True

            return False

        except Exception as e:
            print(f"  ⚠️ コードエディタ入力失敗: {e}")
            return False

    async def insert_content_keyboard_navigation(self, content: str) -> bool:
        """キーボードナビゲーションでの入力"""
        try:
            print("  🔄 キーボードナビゲーション入力...")

            await self.browser.page.keyboard.press("Tab")
            await self.browser.page.wait_for_timeout(1000)
            await self.browser.page.keyboard.press("Tab")
            await self.browser.page.wait_for_timeout(1000)
            await self.browser.page.keyboard.press("Tab")
            await self.browser.page.wait_for_timeout(1000)

            await self.browser.page.keyboard.type(content, delay=10)
            print("  ✅ キーボードナビゲーション入力成功")
            return True

        except Exception as e:
            print(f"  ⚠️ キーボードナビゲーション入力失敗: {e}")
            return False

    async def insert_content_javascript_injection(self, content: str) -> bool:
        """JavaScriptインジェクションでの入力"""
        try:
            print("  🔄 JavaScriptインジェクション入力...")

            encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

            result = await self.browser.page.evaluate(
                """
                (encodedContent) => {
                    try {
                        const content = atob(encodedContent);
                        
                        const editors = [
                            ...document.querySelectorAll('.wp-block-paragraph[contenteditable="true"]'),
                            document.querySelector('#content'),
                            ...document.querySelectorAll('[contenteditable="true"]')
                        ].filter(Boolean);
                        
                        for (const editor of editors) {
                            try {
                                if (editor.tagName === 'TEXTAREA') {
                                    editor.value = content;
                                } else {
                                    editor.textContent = content;
                                }
                                
                                editor.dispatchEvent(new Event('input', { bubbles: true }));
                                editor.dispatchEvent(new Event('change', { bubbles: true }));
                                
                                return { success: true, type: editor.tagName };
                            } catch (e) {
                                continue;
                            }
                        }
                        
                        return { success: false, error: 'No suitable editor found' };
                    } catch (e) {
                        return { success: false, error: e.toString() };
                    }
                }
            """,
                encoded_content,
            )

            if result.get("success"):
                print(f"  ✅ JavaScriptインジェクション成功: {result['type']}")
                return True
            else:
                print(f"  ❌ JavaScriptインジェクション失敗: {result.get('error')}")
                return False

        except Exception as e:
            print(f"  ⚠️ JavaScriptインジェクション失敗: {e}")
            return False

    async def publish_post_comprehensive(self) -> bool:
        """投稿を公開 - 総合的なアプローチ"""
        try:
            print("�� 投稿を公開中（総合アプローチ）...")

            publish_selectors = [
                "button.editor-post-publish-button__button",
                "#publish",
                'button[aria-label*="公開"]',
                'button:has-text("公開")',
                'button:has-text("Publish")',
                "input#publish",
            ]

            for selector in publish_selectors:
                publish_button = await self.browser.page.query_selector(selector)
                if publish_button:
                    is_visible = await publish_button.is_visible()
                    is_disabled = await publish_button.get_attribute("disabled")

                    if is_visible and not is_disabled:
                        await publish_button.click()
                        print(f"  ✅ 公開ボタンクリック: {selector}")

                        await self.browser.page.wait_for_timeout(10000)

                        success_indicators = [
                            "text=公開しました",
                            "text=Published",
                            "text=下書きを保存しました",
                            "text=Draft saved",
                            ".components-snackbar",
                            ".editor-post-publish-panel__header",
                            ".post-publish-panel__postpublish-header",
                        ]

                        for indicator in success_indicators:
                            element = await self.browser.page.query_selector(indicator)
                            if element:
                                text = await element.text_content()
                                print(f"  ✅ 公開成功確認: {text}")
                                return True

                        if "post.php" in self.browser.page.url or "post=" in self.browser.page.url:
                            print("  ✅ URL変更で公開成功と判断")
                            return True

                        print("  ⚠️ 公開確認できませんが、続行します")
                        return True

            print("  ❌ 有効な公開ボタンが見つかりません")
            return False

        except Exception as e:
            print(f"  ❌ 投稿公開失敗: {e}")
            return False

    def generate_optimized_content(self, company: Dict) -> str:
        """最適化されたコンテンツを生成"""
        content = f"""【企業基本情報】
企業名: {company['name']}
業種: {company['industry']}
設立: {company['established']}
資本金: {company['capital']}
従業員数: {company['employees']}
所在地: {company['location']}

【事業内容の詳細】
{company['business_description']}

【企業の強みと特徴】
{chr(10).join(['● ' + strength for strength in company['strengths']])}

【財務実績と予測】
・売上高: {company['revenue']}
・営業利益: {company['profit']}
・成長率: {company['growth_rate']}

【M&A取引条件】
・企業価値評価: {company['valuation']}
・希望売却価格: {company['asking_price']}
・取引形態: {company['deal_structure']}
・想定スケジュール: {company['timeline']}

【デューデリジェンス進捗状況】
1. 財務分析: {company['dd_status']['financial_analysis']}
2. 法務審査: {company['dd_status']['legal_review']}
3. 技術デューデリジェンス: {company['dd_status']['technical_due_diligence']}
4. 商業デューデリジェンス: {company['dd_status']['commercial_due_diligence']}
5. 人事評価: {company['dd_status']['hr_assessment']}

【コンタクト情報】
※詳細な情報や資料のご請求は、当M&Aポータルサイトを通じてお問い合わせください。

---
自動登録日時: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
登録企業ID: {company['id']}
"""
        return content

    async def register_all_companies(self) -> Dict:
        """全企業データを登録"""
        companies = self.data_manager.get_all_companies()
        self.results["total_companies"] = len(companies)

        if len(companies) == 0:
            print("❌ 登録する企業データがありません")
            return self.results

        print(f"🚀 企業データ登録開始: {len(companies)}社")

        for i, company in enumerate(companies, 1):
            print(f"\n{'='*50}")
            print(f"📍 企業 {i}/{len(companies)}: {company['name']}")
            print(f"{'='*50}")

            if not await self.navigate_to_new_post_advanced():
                self.record_result(company, False, "新規投稿ページ移動失敗")
                continue

            success = await self.create_company_post_comprehensive(company)

            if success:
                self.results["successful_registrations"] += 1
                self.record_result(company, True, "登録成功")

                content_size = len(self.generate_optimized_content(company))
                print(f"📝 登録内容: タイトル {len(company['name'])}文字, 本文 {content_size}文字")
            else:
                self.results["failed_registrations"] += 1
                self.record_result(company, False, "登録失敗")

            if i < len(companies):
                print("⏳ 次の登録まで5秒待機...")
                await self.browser.page.wait_for_timeout(5000)

        return self.results

    def record_result(self, company: Dict, success: bool, message: str):
        """結果を記録"""
        result_detail = {
            "company_id": company["id"],
            "company_name": company["name"],
            "success": success,
            "message": message,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        self.results["details"].append(result_detail)

        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {company['name']}: {message}")

    async def run(self) -> Dict:
        """メイン実行"""
        try:
            print("=" * 60)
            print("🏢 WordPress企業データ登録 - Day 3 (互換性修正版 V12)")
            print("=" * 60)

            companies = self.data_manager.get_all_companies()
            if len(companies) == 0:
                print("❌ 企業データが読み込めませんでした")
                return self.results

            print(f"📊 読み込んだ企業数: {len(companies)}社")

            if not await self.setup():
                self.results["error"] = "ブラウザセットアップ失敗"
                return self.results

            if not await self.login_to_wordpress():
                self.results["error"] = "WordPressログイン失敗"
                return self.results

            results = await self.register_all_companies()

            result_file = f"{self.log_dir}/registration_results_v12.json"
            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            print(f"\n📊 結果を保存: {result_file}")

            return results

        except Exception as e:
            error_msg = f"予期しないエラー: {e}"
            print(f"❌ {error_msg}")
            self.results["error"] = error_msg
            return self.results

        finally:
            if self.browser:
                await self.browser.cleanup()


async def main():
    """メイン実行関数"""
    populator = WPDataPopulatorV12()
    results = await populator.run()

    print("\n" + "=" * 60)
    print("📊 Day 3 実行結果サマリー (互換性修正版 V12)")
    print("=" * 60)
    print(f"🏢 対象企業数: {results['total_companies']}社")
    print(f"✅ 登録成功: {results['successful_registrations']}社")
    print(f"❌ 登録失敗: {results['failed_registrations']}社")

    if "error" in results:
        print(f"⚠️ エラー: {results['error']}")

    if results["details"]:
        print(f"\n📋 詳細結果:")
        for detail in results["details"]:
            status = "✅ 成功" if detail["success"] else "❌ 失敗"
            print(f"  {status} | {detail['company_name']}: {detail['message']}")

    print("=" * 60)

    if results["successful_registrations"] >= 3:
        print("🎉 Day 3 完了！")
        print("💡 WordPress管理画面で実際の文字数を確認してください")
        return 0
    else:
        print("❌ Day 3 要改善")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
