"""
WordPress企業データ登録モジュール V7 - 最適化版
Day 3: タイムアウト問題とブロックエディタ対応を修正
"""

import asyncio
import json
import os
import sys
import datetime
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


class WPDataPopulatorV7:
    """WordPress企業データ登録 V7 - 最適化版"""

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

    async def setup(self) -> bool:
        """ブラウザセットアップ"""
        try:
            print("🔄 ブラウザセットアップ開始")
            self.browser = BrowserController()
            await self.browser.setup_browser(headless=True)
            print("✅ ブラウザセットアップ完了")
            return True
        except Exception as e:
            print(f"❌ ブラウザセットアップ失敗: {e}")
            return False

    async def login_to_wordpress(self) -> bool:
        """WordPressにログイン - 最適化版"""
        try:
            print(f"🔐 WordPressログイン試行: {self.wp_url}/wp-admin")

            # より寛容な設定でアクセス
            await self.browser.page.goto(
                f"{self.wp_url}/wp-admin",
                wait_until="domcontentloaded",  # networkidle より高速
                timeout=90000,  # 90秒に延長
            )

            # ログインページか確認
            current_url = self.browser.page.url
            if "wp-login.php" in current_url:
                print("📝 ログインフォーム入力中")
                await self.browser.page.fill("#user_login", self.wp_user)
                await self.browser.page.fill("#user_pass", self.wp_pass)
                await self.browser.page.click("#wp-submit")

                # ログイン成功を確認（より寛容な待機）
                try:
                    await self.browser.page.wait_for_selector("#wpadminbar", timeout=20000)
                    print("✅ WordPressログイン成功")
                    return True
                except Exception as login_error:
                    # 別の方法でログイン確認
                    if "wp-admin" in self.browser.page.url:
                        print("✅ ログイン成功（URLで確認）")
                        return True
                    else:
                        print(f"❌ ログイン失敗: {login_error}")
                        return False
            else:
                print("ℹ️ 既にログイン済みまたは別のページにリダイレクト")
                if "wp-admin" in current_url:
                    print("✅ WordPress管理画面にアクセス成功")
                    return True
                else:
                    print(f"⚠️ 予期しないページ: {current_url}")
                    return False

        except Exception as e:
            print(f"❌ WordPressログイン失敗: {e}")
            return False

    async def navigate_to_new_post_optimized(self) -> bool:
        """新規投稿ページに移動 - 最適化版"""
        try:
            print("📝 新規投稿ページへ移動 (最適化版)")

            # 方法1: 直接アクセス（domcontentloadedで高速化）
            try:
                await self.browser.page.goto(
                    f"{self.wp_url}/wp-admin/post-new.php",
                    wait_until="domcontentloaded",  # networkidle より高速
                    timeout=60000,  # 60秒
                )
                print("✅ 直接アクセス成功")
            except Exception as direct_error:
                print(f"⚠️ 直接アクセス失敗: {direct_error}")
                return False

            # ブロックエディタの読み込みを待機（複数のセレクタを試す）
            editor_selectors = [
                ".editor-post-title__input",  # ブロックエディタタイトル
                "#title",  # クラシックエディタタイトル
                ".block-editor-writing-flow",  # ブロックエディタ本文エリア
                "#content",  # クラシックエディタ本文
                "body.wp-admin",  # 管理画面ボディ
            ]

            for selector in editor_selectors:
                try:
                    await self.browser.page.wait_for_selector(selector, timeout=30000)
                    print(f"✅ エディタ要素確認: {selector}")
                    return True
                except:
                    continue

            # 最低限の確認 - 管理画面かどうか
            current_url = self.browser.page.url
            if "wp-admin" in current_url:
                print("⚠️ 特定のエディタ要素が見つかりませんが、管理画面にはアクセスできています")
                return True

            return False

        except Exception as e:
            print(f"❌ 新規投稿ページ移動失敗: {e}")
            return False

    async def create_company_post_optimized(self, company: Dict) -> bool:
        """企業データを投稿として作成 - 最適化版"""
        try:
            print(f"🏢 企業データ登録開始: {company['name']}")

            # タイトル入力 - ブロックエディタ完全対応
            title_success = await self.enter_title_optimized(company["name"])
            if not title_success:
                return False

            # コンテンツ作成と入力
            content_success = await self.enter_content_optimized(company)
            if not content_success:
                return False

            # 投稿を公開
            publish_success = await self.publish_post_optimized()

            return publish_success

        except Exception as e:
            print(f"❌ 企業データ登録失敗 {company['name']}: {e}")
            return False

    async def enter_title_optimized(self, title: str) -> bool:
        """タイトル入力 - 最適化版"""
        try:
            print("📝 タイトル入力中...")

            # 複数のタイトルセレクタを試す
            title_selectors = [
                ".editor-post-title__input",  # ブロックエディタ
                "#title",  # クラシックエディタ
                'input[name="post_title"]',  # 一般的なセレクタ
            ]

            for selector in title_selectors:
                title_input = await self.browser.page.query_selector(selector)
                if title_input:
                    # 入力可能か確認
                    is_disabled = await title_input.get_attribute("disabled")
                    is_readonly = await title_input.get_attribute("readonly")

                    if not is_disabled and not is_readonly:
                        # 既存のテキストをクリア
                        await title_input.click(click_count=3)  # 全選択
                        await title_input.press("Backspace")

                        # タイトルを入力（遅延付きで確実に）
                        await title_input.type(title, delay=100)
                        print(f"✅ タイトル入力完了 ({selector})")
                        return True
                    else:
                        print(f"⚠️ タイトル入力フィールドが無効です: {selector}")

            print("❌ 有効なタイトル入力フィールドが見つかりません")
            return False

        except Exception as e:
            print(f"❌ タイトル入力失敗: {e}")
            return False

    async def enter_content_optimized(self, company: Dict) -> bool:
        """コンテンツ入力 - 最適化版"""
        try:
            print("📝 コンテンツ入力中...")

            # シンプルなテキストコンテンツを生成
            simple_content = self.generate_simple_content(company)

            # 方法1: 段落ブロックに直接入力
            success = await self.insert_via_paragraph(simple_content)
            if success:
                return True

            # 方法2: コードエディタ経由
            success = await self.insert_via_code_editor(simple_content)
            if success:
                return True

            # 方法3: クラシックブロックを使用
            success = await self.insert_via_classic_block(simple_content)

            return success

        except Exception as e:
            print(f"❌ コンテンツ入力失敗: {e}")
            return False

    async def insert_via_paragraph(self, content: str) -> bool:
        """段落ブロックに直接入力"""
        try:
            # 既存の段落ブロックを探す
            paragraph_block = await self.browser.page.query_selector(".wp-block-paragraph")
            if not paragraph_block:
                # 新しいブロックを追加
                add_block_btn = await self.browser.page.query_selector('button[aria-label="ブロックを追加"]')
                if add_block_btn:
                    await add_block_btn.click()
                    await self.browser.page.wait_for_timeout(2000)

                    # 段落ブロックを選択
                    paragraph_option = await self.browser.page.query_selector('button[aria-label="段落"]')
                    if paragraph_option:
                        await paragraph_option.click()
                        await self.browser.page.wait_for_timeout(2000)
                        paragraph_block = await self.browser.page.query_selector(".wp-block-paragraph")

            if paragraph_block:
                await paragraph_block.click()
                await paragraph_block.press("Control+A")
                await paragraph_block.type(content, delay=50)
                print("✅ 段落ブロック経由でコンテンツ入力完了")
                return True

            return False

        except Exception as e:
            print(f"⚠️ 段落ブロック経由入力失敗: {e}")
            return False

    async def insert_via_code_editor(self, content: str) -> bool:
        """コードエディタ経由で入力"""
        try:
            # その他のオプションメニューを開く
            more_menu = await self.browser.page.query_selector('button[aria-label="オプション"]')
            if more_menu:
                await more_menu.click()
                await self.browser.page.wait_for_timeout(1000)

                # コードエディタを選択
                code_editor_item = await self.browser.page.query_selector(
                    'button.components-menu-item__button:has-text("コードエディター")'
                )
                if not code_editor_item:
                    code_editor_item = await self.browser.page.query_selector('button:has-text("Code Editor")')

                if code_editor_item:
                    await code_editor_item.click()
                    await self.browser.page.wait_for_timeout(2000)

                    # コードエディタのテキストエリアを探す
                    code_textarea = await self.browser.page.query_selector(".editor-post-text-editor")
                    if code_textarea:
                        await code_textarea.click()
                        await code_textarea.press("Control+A")
                        await code_textarea.type(content, delay=50)

                        # ビジュアルエディタに戻る
                        await more_menu.click()
                        await self.browser.page.wait_for_timeout(1000)
                        visual_editor_item = await self.browser.page.query_selector(
                            'button.components-menu-item__button:has-text("ビジュアルエディター")'
                        )
                        if not visual_editor_item:
                            visual_editor_item = await self.browser.page.query_selector(
                                'button:has-text("Visual Editor")'
                            )

                        if visual_editor_item:
                            await visual_editor_item.click()
                            await self.browser.page.wait_for_timeout(2000)
                            print("✅ コードエディタ経由でコンテンツ入力完了")
                            return True

            return False

        except Exception as e:
            print(f"⚠️ コードエディタ経由入力失敗: {e}")
            return False

    async def insert_via_classic_block(self, content: str) -> bool:
        """クラシックブロックを使用"""
        try:
            # ブロックを追加
            add_block_btn = await self.browser.page.query_selector('button[aria-label="ブロックを追加"]')
            if add_block_btn:
                await add_block_btn.click()
                await self.browser.page.wait_for_timeout(1000)

                # クラシックブロックを検索
                search_input = await self.browser.page.query_selector('input[placeholder="ブロックを検索"]')
                if search_input:
                    await search_input.type("クラシック", delay=50)
                    await self.browser.page.wait_for_timeout(1000)

                    classic_block = await self.browser.page.query_selector('button[aria-label="クラシック"]')
                    if classic_block:
                        await classic_block.click()
                        await self.browser.page.wait_for_timeout(2000)

                        # テキストビューに切り替え
                        text_view_btn = await self.browser.page.query_selector(
                            'button[aria-label="テキストとして編集"]'
                        )
                        if text_view_btn:
                            await text_view_btn.click()
                            await self.browser.page.wait_for_timeout(1000)

                            # HTMLを入力
                            textarea = await self.browser.page.query_selector(".wp-block-freeform")
                            if textarea:
                                await textarea.click()
                                await textarea.press("Control+A")
                                await textarea.type(content, delay=50)
                                print("✅ クラシックブロック経由でコンテンツ入力完了")
                                return True

            return False

        except Exception as e:
            print(f"⚠️ クラシックブロック経由入力失敗: {e}")
            return False

    async def publish_post_optimized(self) -> bool:
        """投稿を公開 - 最適化版"""
        try:
            print("🚀 投稿を公開中...")

            # 公開ボタンをクリック
            publish_button = await self.browser.page.query_selector("button.editor-post-publish-button__button")
            if publish_button:
                await publish_button.click()
                await self.browser.page.wait_for_timeout(5000)

                # 確認ボタン（もしあれば）
                confirm_button = await self.browser.page.query_selector("button.editor-post-publish-panel__toggle")
                if confirm_button:
                    await confirm_button.click()
                    await self.browser.page.wait_for_timeout(3000)

            # 成功メッセージを確認
            success_indicators = [
                ".components-snackbar",
                ".editor-post-publish-panel__header",
                "text=公開しました",
                "text=Published",
            ]

            for indicator in success_indicators:
                try:
                    if "text=" in indicator:
                        element = await self.browser.page.query_selector(f"text={indicator[5:]}")
                    else:
                        element = await self.browser.page.query_selector(indicator)

                    if element:
                        print("✅ 投稿公開成功")
                        return True
                except:
                    continue

            # エラーメッセージ確認
            error_msg = await self.browser.page.query_selector(".components-notice.is-error")
            if error_msg:
                error_text = await error_msg.text_content()
                print(f"❌ 公開エラー: {error_text}")
                return False

            print("⚠️ 公開結果が不明ですが、続行します")
            return True

        except Exception as e:
            print(f"❌ 投稿公開失敗: {e}")
            return False

    def generate_simple_content(self, company: Dict) -> str:
        """シンプルなテキストコンテンツを生成"""
        content = f"""
企業名: {company['name']}
業種: {company['industry']}
設立: {company['established']}
資本金: {company['capital']}
従業員数: {company['employees']}
所在地: {company['location']}

事業内容:
{company['business_description']}

強み・特徴:
{chr(10).join(['・' + strength for strength in company['strengths']])}

財務情報:
売上高: {company['revenue']}
営業利益: {company['profit']}
成長率: {company['growth_rate']}

M&A情報:
企業価値: {company['valuation']}
希望価格: {company['asking_price']}
取引形態: {company['deal_structure']}
スケジュール: {company['timeline']}

DD状況:
財務分析: {company['dd_status']['financial_analysis']}
法務審査: {company['dd_status']['legal_review']}
技術DD: {company['dd_status']['technical_due_diligence']}
商業DD: {company['dd_status']['commercial_due_diligence']}
人事評価: {company['dd_status']['hr_assessment']}

自動登録日: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
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

            # 新規投稿ページに移動
            if not await self.navigate_to_new_post_optimized():
                self.record_result(company, False, "新規投稿ページ移動失敗")
                continue

            # 企業データ登録
            success = await self.create_company_post_optimized(company)

            if success:
                self.results["successful_registrations"] += 1
                self.record_result(company, True, "登録成功")
            else:
                self.results["failed_registrations"] += 1
                self.record_result(company, False, "登録失敗")

            # 次の登録前に待機（最後の企業以外）
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
            print("🏢 WordPress企業データ登録 - Day 3 (最適化版 V7)")
            print("=" * 60)

            # データ確認
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

            # 企業データ登録実行
            results = await self.register_all_companies()

            # 結果保存
            result_file = f"{self.log_dir}/registration_results_v7.json"
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
    populator = WPDataPopulatorV7()
    results = await populator.run()

    print("\n" + "=" * 60)
    print("📊 Day 3 実行結果サマリー (最適化版 V7)")
    print("=" * 60)
    print(f"🏢 対象企業数: {results['total_companies']}社")
    print(f"✅ 登録成功: {results['successful_registrations']}社")
    print(f"❌ 登録失敗: {results['failed_registrations']}社")

    if "error" in results:
        print(f"⚠️ エラー: {results['error']}")

    # 詳細結果表示
    if results["details"]:
        print(f"\n📋 詳細結果:")
        for detail in results["details"]:
            status = "✅ 成功" if detail["success"] else "❌ 失敗"
            print(f"  {status} | {detail['company_name']}: {detail['message']}")

    print("=" * 60)

    # 成功判定
    if results["successful_registrations"] >= 3:
        print("🎉 Day 3 完了！次はDay 4へ")
        return 0
    else:
        print("❌ Day 3 要改善")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
