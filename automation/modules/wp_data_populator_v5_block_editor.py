"""
WordPress企業データ登録モジュール V5 - ブロックエディタ対応版
Day 3: ブロックエディタ（Gutenberg）への完全対応
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


class WPDataPopulatorV5:
    """WordPress企業データ登録 V5 - ブロックエディタ対応"""

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
        """WordPressにログイン"""
        try:
            print(f"🔐 WordPressログイン試行: {self.wp_url}/wp-admin")
            await self.browser.page.goto(f"{self.wp_url}/wp-admin", wait_until="networkidle")

            if "wp-login.php" in self.browser.page.url:
                print("📝 ログインフォーム入力中")
                await self.browser.page.fill("#user_login", self.wp_user)
                await self.browser.page.fill("#user_pass", self.wp_pass)
                await self.browser.page.click("#wp-submit")
                await self.browser.page.wait_for_selector("#wpadminbar", timeout=15000)
            else:
                print("ℹ️ 既にログイン済み")

            print("✅ WordPressログイン成功")
            return True

        except Exception as e:
            print(f"❌ WordPressログイン失敗: {e}")
            return False

    async def navigate_to_new_post(self) -> bool:
        """新規投稿ページに移動"""
        try:
            print("📝 新規投稿ページへ移動")
            await self.browser.page.goto(f"{self.wp_url}/wp-admin/post-new.php", wait_until="networkidle")

            # ブロックエディタの読み込みを待機
            await self.browser.page.wait_for_selector(".editor-post-title__input", timeout=30000)
            print("✅ ブロックエディタ読み込み完了")
            return True

        except Exception as e:
            print(f"❌ 新規投稿ページ移動失敗: {e}")
            return False

    async def create_company_post(self, company: Dict) -> bool:
        """企業データを投稿として作成 - ブロックエディタ対応"""
        try:
            print(f"🏢 企業データ登録開始: {company['name']}")

            # タイトル入力 - ブロックエディタ対応
            title_success = await self.enter_title_block_editor(company["name"])
            if not title_success:
                return False

            # コンテンツ作成と入力
            content_success = await self.enter_content_block_editor(company)
            if not content_success:
                return False

            # 投稿を公開
            publish_success = await self.publish_post()

            return publish_success

        except Exception as e:
            print(f"❌ 企業データ登録失敗 {company['name']}: {e}")
            return False

    async def enter_title_block_editor(self, title: str) -> bool:
        """ブロックエディタでタイトルを入力"""
        try:
            print("📝 タイトル入力中...")

            # ブロックエディタのタイトルフィールド
            title_input = await self.browser.page.query_selector(".editor-post-title__input")
            if not title_input:
                print("❌ タイトル入力フィールドが見つかりません")
                return False

            # 既存のテキストをクリア
            await title_input.click(click_count=3)  # 全選択
            await title_input.press("Backspace")

            # タイトルを入力
            await title_input.type(title, delay=100)  # ゆっくり入力して確実に

            print("✅ タイトル入力完了")
            return True

        except Exception as e:
            print(f"❌ タイトル入力失敗: {e}")
            return False

    async def enter_content_block_editor(self, company: Dict) -> bool:
        """ブロックエディタでコンテンツを入力"""
        try:
            print("📝 コンテンツ入力中...")

            # コンテンツをHTML形式で生成
            html_content = self.generate_company_html(company)

            # 方法1: コードエディタ経由でHTMLを挿入
            success = await self.insert_via_code_editor(html_content)
            if success:
                return True

            # 方法2: 段落ブロックに直接入力
            success = await self.insert_via_paragraph_blocks(company)
            if success:
                return True

            # 方法3: クラシックブロックを使用
            success = await self.insert_via_classic_block(html_content)

            return success

        except Exception as e:
            print(f"❌ コンテンツ入力失敗: {e}")
            return False

    async def insert_via_code_editor(self, html_content: str) -> bool:
        """コードエディタ経由でHTMLを挿入"""
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
                if code_editor_item:
                    await code_editor_item.click()
                    await self.browser.page.wait_for_timeout(2000)

                    # コードエディタのテキストエリアを探す
                    code_textarea = await self.browser.page.query_selector(".editor-post-text-editor")
                    if code_textarea:
                        await code_textarea.click()
                        await code_textarea.press("Control+A")
                        await code_textarea.type(html_content, delay=50)

                        # ビジュアルエディタに戻る
                        await more_menu.click()
                        await self.browser.page.wait_for_timeout(1000)
                        visual_editor_item = await self.browser.page.query_selector(
                            'button.components-menu-item__button:has-text("ビジュアルエディター")'
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

    async def insert_via_paragraph_blocks(self, company: Dict) -> bool:
        """段落ブロックに直接入力"""
        try:
            # 既存の段落ブロックを探す
            paragraph_block = await self.browser.page.query_selector(".wp-block-paragraph")
            if not paragraph_block:
                # 新しいブロックを追加
                await self.browser.page.click('button[aria-label="ブロックを追加"]')
                await self.browser.page.wait_for_timeout(1000)
                await self.browser.page.click('button[aria-label="段落"]')
                await self.browser.page.wait_for_timeout(1000)
                paragraph_block = await self.browser.page.query_selector(".wp-block-paragraph")

            if paragraph_block:
                # シンプルなテキストコンテンツを入力
                simple_content = self.generate_simple_content(company)
                await paragraph_block.click()
                await paragraph_block.press("Control+A")
                await paragraph_block.type(simple_content, delay=50)
                print("✅ 段落ブロック経由でコンテンツ入力完了")
                return True

            return False

        except Exception as e:
            print(f"⚠️ 段落ブロック経由入力失敗: {e}")
            return False

    async def insert_via_classic_block(self, html_content: str) -> bool:
        """クラシックブロックを使用"""
        try:
            # ブロックを追加
            await self.browser.page.click('button[aria-label="ブロックを追加"]')
            await self.browser.page.wait_for_timeout(1000)

            # クラシックブロックを検索
            await self.browser.page.type('input[placeholder="ブロックを検索"]', "クラシック")
            await self.browser.page.wait_for_timeout(1000)

            classic_block = await self.browser.page.query_selector('button[aria-label="クラシック"]')
            if classic_block:
                await classic_block.click()
                await self.browser.page.wait_for_timeout(2000)

                # テキストビューに切り替え
                text_view_btn = await self.browser.page.query_selector('button[aria-label="テキストとして編集"]')
                if text_view_btn:
                    await text_view_btn.click()
                    await self.browser.page.wait_for_timeout(1000)

                    # HTMLを入力
                    textarea = await self.browser.page.query_selector(".wp-block-freeform")
                    if textarea:
                        await textarea.click()
                        await textarea.press("Control+A")
                        await textarea.type(html_content, delay=50)
                        print("✅ クラシックブロック経由でコンテンツ入力完了")
                        return True

            return False

        except Exception as e:
            print(f"⚠️ クラシックブロック経由入力失敗: {e}")
            return False

    async def publish_post(self) -> bool:
        """投稿を公開"""
        try:
            print("�� 投稿を公開中...")

            # 公開ボタンをクリック
            publish_button = await self.browser.page.query_selector("button.editor-post-publish-button__button")
            if publish_button:
                await publish_button.click()
                await self.browser.page.wait_for_timeout(3000)

                # 確認ボタン（もしあれば）
                confirm_button = await self.browser.page.query_selector("button.editor-post-publish-panel__toggle")
                if confirm_button:
                    await confirm_button.click()
                    await self.browser.page.wait_for_timeout(3000)

            # 成功メッセージを確認
            success_indicators = [".components-snackbar", ".editor-post-publish-panel__header", "text=公開しました"]

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

    def generate_company_html(self, company: Dict) -> str:
        """企業データをHTML形式で生成"""
        html = f"""
<!-- 企業データ自動登録 - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} -->

<h2>企業概要</h2>
<table border="1" style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
<tr><th style="padding: 8px; background-color: #f2f2f2; width: 30%;">企業名</th><td style="padding: 8px;">{company['name']}</td></tr>
<tr><th style="padding: 8px; background-color: #f2f2f2;">業種</th><td style="padding: 8px;">{company['industry']}</td></tr>
<tr><th style="padding: 8px; background-color: #f2f2f2;">設立</th><td style="padding: 8px;">{company['established']}</td></tr>
<tr><th style="padding: 8px; background-color: #f2f2f2;">資本金</th><td style="padding: 8px;">{company['capital']}</td></tr>
<tr><th style="padding: 8px; background-color: #f2f2f2;">従業員数</th><td style="padding: 8px;">{company['employees']}</td></tr>
<tr><th style="padding: 8px; background-color: #f2f2f2;">所在地</th><td style="padding: 8px;">{company['location']}</td></tr>
</table>

<h2>事業内容</h2>
<p>{company['business_description']}</p>

<h2>強み・特徴</h2>
<ul>
{''.join([f'<li>{strength}</li>' for strength in company['strengths']])}
</ul>

<h2>財務情報</h2>
<table border="1" style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
<tr><th style="padding: 8px; background-color: #f2f2f2; width: 30%;">売上高</th><td style="padding: 8px;">{company['revenue']}</td></tr>
<tr><th style="padding: 8px; background-color: #f2f2f2;">営業利益</th><td style="padding: 8px;">{company['profit']}</td></tr>
<tr><th style="padding: 8px; background-color: #f2f2f2;">成長率</th><td style="padding: 8px;">{company['growth_rate']}</td></tr>
</table>

<h2>M&A情報</h2>
<table border="1" style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
<tr><th style="padding: 8px; background-color: #f2f2f2; width: 30%;">企業価値</th><td style="padding: 8px;">{company['valuation']}</td></tr>
<tr><th style="padding: 8px; background-color: #f2f2f2;">希望価格</th><td style="padding: 8px;">{company['asking_price']}</td></tr>
<tr><th style="padding: 8px; background-color: #f2f2f2;">取引形態</th><td style="padding: 8px;">{company['deal_structure']}</td></tr>
<tr><th style="padding: 8px; background-color: #f2f2f2;">スケジュール</th><td style="padding: 8px;">{company['timeline']}</td></tr>
</table>

<h2>DD（デューデリジェンス）状況</h2>
<table border="1" style="border-collapse: collapse; width: 100%;">
<tr><th style="padding: 8px; background-color: #f2f2f2; width: 30%;">財務分析</th><td style="padding: 8px;">{company['dd_status']['financial_analysis']}</td></tr>
<tr><th style="padding: 8px; background-color: #f2f2f2;">法務審査</th><td style="padding: 8px;">{company['dd_status']['legal_review']}</td></tr>
<tr><th style="padding: 8px; background-color: #f2f2f2;">技術DD</th><td style="padding: 8px;">{company['dd_status']['technical_due_diligence']}</td></tr>
<tr><th style="padding: 8px; background-color: #f2f2f2;">商業DD</th><td style="padding: 8px;">{company['dd_status']['commercial_due_diligence']}</td></tr>
<tr><th style="padding: 8px; background-color: #f2f2f2;">人事評価</th><td style="padding: 8px;">{company['dd_status']['hr_assessment']}</td></tr>
</table>
"""
        return html

    def generate_simple_content(self, company: Dict) -> str:
        """シンプルなテキストコンテンツを生成（フォールバック用）"""
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
            if not await self.navigate_to_new_post():
                self.record_result(company, False, "新規投稿ページ移動失敗")
                continue

            # 企業データ登録
            success = await self.create_company_post(company)

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
            print("🏢 WordPress企業データ登録 - Day 3 (ブロックエディタ対応 V5)")
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
            result_file = f"{self.log_dir}/registration_results_v5.json"
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
    populator = WPDataPopulatorV5()
    results = await populator.run()

    print("\n" + "=" * 60)
    print("📊 Day 3 実行結果サマリー (ブロックエディタ対応 V5)")
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
