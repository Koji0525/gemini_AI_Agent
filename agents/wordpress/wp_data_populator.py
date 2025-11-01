#!/usr/bin/env python3
"""
WordPress企業データ自動登録エージェント
DD項目を含む完全な企業情報を自動投稿
"""
import asyncio
from browser_control.browser_controller import BrowserController


class WPDataPopulator:
    """企業データ自動登録エージェント"""

    def __init__(self, browser: BrowserController):
        self.browser = browser
        self.wp_url = "https://uzbek-ma.com"

    async def login(self):
        """WordPress管理画面にログイン"""
        await self.browser.goto(f"{self.wp_url}/wp-admin/")
        await self.browser.fill_form({"user_login": "uzbek", "user_pass": "57QV*sUgdJ3OJie1dD7P1^DC"})
        await self.browser.click('input[type="submit"]')
        await asyncio.sleep(3)
        return True

    async def create_company(self, company_data):
        """企業情報を1件登録"""
        print(f"\n📝 企業登録: {company_data['title']}")

        # 新規投稿ページへ
        await self.browser.goto(f"{self.wp_url}/wp-admin/post-new.php?post_type=ma_company")
        await asyncio.sleep(2)

        # タイトル入力
        await self.browser.fill('input[name="post_title"]', company_data["title"])

        # 本文入力
        await self.browser.fill("textarea.wp-editor-area", company_data["content"])

        # 基本情報入力
        for field, value in company_data["basic"].items():
            await self.browser.fill(f'input[name="{field}"]', str(value))

        # DD情報入力（33項目）
        for category, fields in company_data["dd"].items():
            for field_key, value in fields.items():
                meta_key = f"dd_{category}_{field_key}"

                # フィールドタイプに応じた入力
                if isinstance(value, str) and len(value) > 100:
                    await self.browser.fill(f'textarea[name="{meta_key}"]', value)
                else:
                    await self.browser.fill(f'input[name="{meta_key}"], select[name="{meta_key}"]', str(value))

        # 業種選択
        industry_checkbox = f'input[name="tax_input[ma_industry][]"][value="{company_data["industry"]}"]'
        await self.browser.check(industry_checkbox)

        # 公開
        await self.browser.click("#publish")
        await asyncio.sleep(3)

        print(f"  ✅ {company_data['title']} 登録完了")
        return True

    async def populate_all_companies(self):
        """全企業データを自動登録"""

        # 企業データ（5社分）
        companies = [
            {
                "title": "テクノロジー株式会社",
                "industry": "it",
                "content": "最先端のAI・機械学習ソリューション...",
                "basic": {
                    "founded_year": "2018",
                    "employees": "150",
                    "revenue": "30億円",
                },
                "dd": {
                    "financial": {
                        "audit_firm": "大手監査法人ABC",
                        "audit_opinion": "無限定適正",
                        "internal_control": "整備済",
                    },
                    "ma": {
                        "bcp": "あり",
                        "ma_purpose": "技術力強化とエンジニア人材獲得",
                    },
                    # ... 残りのDD項目
                },
            },
            # ... 残り4社
        ]

        await self.login()

        results = []
        for company in companies:
            success = await self.create_company(company)
            results.append({"company": company["title"], "success": success})

        return results


async def main():
    browser = BrowserController()
    await browser.initialize()

    populator = WPDataPopulator(browser)
    results = await populator.populate_all_companies()

    print("\n" + "=" * 60)
    print("📊 企業データ登録結果")
    print("=" * 60)
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"{status} {r['company']}")

    await browser.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
