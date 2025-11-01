"""
Day 3: 企業データ登録テスト
"""

import asyncio
import sys
import os

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from automation.modules.wp_data_populator_v3 import WPDataPopulatorV3


async def test_data_loading():
    """データ読み込みテスト"""
    print("🧪 企業データ読み込みテスト")

    from automation.modules.wp_data_populator_v3 import CompanyDataManager

    manager = CompanyDataManager()
    companies = manager.get_all_companies()

    print(f"📊 読み込んだ企業数: {len(companies)}")

    for company in companies:
        print(f"  🏢 {company['id']}: {company['name']} - {company['industry']}")

    assert len(companies) == 5, f"企業数が5社ではありません: {len(companies)}社"
    print("✅ データ読み込みテスト完了")


async def test_single_company_registration():
    """単一企業登録テスト"""
    print("\n🧪 単一企業登録テスト")

    populator = WPDataPopulatorV3()

    # セットアップのみ実行（実際の登録はスキップ）
    if await populator.setup() and await populator.login_to_wordpress():
        print("✅ セットアップテスト成功")

        # テスト用の企業データ
        test_company = {
            "id": 999,
            "name": "テスト企業株式会社",
            "industry": "テスト業種",
            "established": "2020年1月",
            "capital": "1000万円",
            "employees": "10名",
            "location": "テスト県テスト市",
            "business_description": "テスト事業内容",
            "strengths": ["テスト強み1", "テスト強み2"],
            "revenue": "1億円",
            "profit": "1000万円",
            "growth_rate": "10%",
            "dd_status": {
                "financial_analysis": "テスト",
                "legal_review": "テスト",
                "technical_due_diligence": "テスト",
                "commercial_due_diligence": "テスト",
                "hr_assessment": "テスト",
            },
            "valuation": "2億円",
            "asking_price": "1億8000万円",
            "deal_structure": "テスト",
            "timeline": "テスト",
        }

        content = populator.generate_company_content(test_company)
        print(f"📝 生成コンテンツサイズ: {len(content)}文字")
        print("✅ コンテンツ生成テスト成功")
    else:
        print("❌ セットアップテスト失敗")

    await populator.browser.cleanup()


async def main():
    """メインテスト"""
    print("🚀 Day 3 企業データ登録テスト開始")
    print("=" * 50)

    try:
        await test_data_loading()
        await test_single_company_registration()

        print("\n🎉 すべてのテストが完了しました！")
        print("💡 実際の登録を実行するには以下を実行:")
        print("   python3 automation/modules/wp_data_populator_v3.py")

    except Exception as e:
        print(f"❌ テスト中にエラー: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
