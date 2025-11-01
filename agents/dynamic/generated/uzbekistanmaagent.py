"""
UzbekistanMAAgent - ウズベキスタンM&Aサイト構築エージェント

Description: Uzbekistan M&A site content generation and publishing agent
Version: 1.0.0
Author: Dynamic Agent System
Created: 2025-10-29T07:38:33.803378
"""

import asyncio
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from agents.dynamic.agent_template import AgentTemplate, AgentMetadata, AgentConfig
from agents.wordpress.wordpress_client import WordPressClient
from dotenv import load_dotenv

load_dotenv()


class Uzbekistanmaagent(AgentTemplate):
    """
    Uzbekistan M&A site content generation and publishing agent

    ウズベキスタンのM&A市場に特化したコンテンツ生成・投稿エージェント
    """

    def __init__(self):
        metadata = AgentMetadata(
            name="UzbekistanMAAgent",
            version="1.0.0",
            description="Uzbekistan M&A site content generation and publishing agent",
            author="Dynamic Agent System",
            created_at=datetime.fromisoformat("2025-10-29T07:38:33.803378"),
            dependencies=["requests", "python-dotenv"],
            capabilities=["uzbekistan_ma_content", "multilingual_support", "market_analysis", "wordpress_publishing"],
            tags=["uzbekistan", "m&a", "cms", "auto-generated"],
        )

        config = AgentConfig(max_retries=3, timeout=60, async_mode=True, logging_enabled=True)

        super().__init__(metadata, config)

        # WordPress接続設定
        self.wp_url = os.getenv("WORDPRESS_URL")
        self.wp_username = os.getenv("WORDPRESS_USERNAME")
        self.wp_password = os.getenv("WORDPRESS_APP_PASSWORD")

        if not all([self.wp_url, self.wp_username, self.wp_password]):
            raise ValueError("WordPress credentials not configured in .env")

        self.wp_client = WordPressClient(self.wp_url, self.wp_username, self.wp_password)

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        ウズベキスタンM&A関連記事を生成・投稿

        Args:
            article_type: 記事タイプ（'market_overview', 'deal_analysis', 'sector_report', 'investment_guide'）
            title: 記事タイトル（省略時は自動生成）
            content: 記事内容（省略時は自動生成）
            language: 言語（'ja', 'en', 'uz' - デフォルト: 'ja'）
            sector: セクター（'manufacturing', 'it', 'agriculture', 'energy', etc.）
            tags: タグリスト
            status: 投稿ステータス（'draft' or 'publish'）

        Returns:
            投稿結果
        """
        article_type = kwargs.get("article_type", "market_overview")
        title = kwargs.get("title")
        content = kwargs.get("content")
        language = kwargs.get("language", "ja")
        sector = kwargs.get("sector", "general")
        tags = kwargs.get("tags", [])
        status = kwargs.get("status", "draft")

        # タイトルが指定されていない場合は自動生成
        if not title:
            title = self._generate_title(article_type, sector, language)

        # コンテンツが指定されていない場合は自動生成
        if not content:
            content = self._generate_content(article_type, sector, language)

        # WordPress投稿データ作成
        post_data = {"title": title, "content": content, "status": status}

        # カテゴリ設定（M&A専用）
        post_data["categories"] = ["M&A", "Uzbekistan"]

        # タグ設定
        default_tags = ["ウズベキスタン", "M&A", sector]
        all_tags = list(set(default_tags + tags))
        post_data["tags"] = all_tags

        try:
            # WordPress投稿
            result = self.wp_client.create_post(**post_data)

            return {
                "post_id": result.get("id"),
                "title": result.get("title", {}).get("rendered"),
                "link": result.get("link"),
                "status": result.get("status"),
                "date": result.get("date"),
                "article_type": article_type,
                "sector": sector,
                "language": language,
            }

        except Exception as e:
            raise RuntimeError(f"WordPress post failed: {e}")

    def _generate_title(self, article_type: str, sector: str, language: str) -> str:
        """
        記事タイトルを自動生成

        Args:
            article_type: 記事タイプ
            sector: セクター
            language: 言語

        Returns:
            生成されたタイトル
        """
        titles = {
            "ja": {
                "market_overview": f"ウズベキスタンM&A市場概況 - {sector}セクター",
                "deal_analysis": f"ウズベキスタン{sector}セクターのM&A事例分析",
                "sector_report": f"ウズベキスタン{sector}業界レポート - M&A動向",
                "investment_guide": f"ウズベキスタン{sector}セクター投資ガイド",
            },
            "en": {
                "market_overview": f"Uzbekistan M&A Market Overview - {sector} Sector",
                "deal_analysis": f"M&A Deal Analysis in Uzbekistan {sector} Sector",
                "sector_report": f"Uzbekistan {sector} Industry Report - M&A Trends",
                "investment_guide": f"Investment Guide to Uzbekistan {sector} Sector",
            },
            "uz": {
                "market_overview": f"O'zbekiston M&A bozori sharhi - {sector} sektori",
                "deal_analysis": f"O'zbekiston {sector} sektorida M&A bitimlarini tahlil",
                "sector_report": f"O'zbekiston {sector} sanoati hisoboti - M&A tendentsiyalari",
                "investment_guide": f"O'zbekiston {sector} sektoriga investitsiya qo'llanmasi",
            },
        }

        return titles.get(language, titles["ja"]).get(article_type, "ウズベキスタンM&A記事")

    def _generate_content(self, article_type: str, sector: str, language: str) -> str:
        """
        記事コンテンツを自動生成

        Args:
            article_type: 記事タイプ
            sector: セクター
            language: 言語

        Returns:
            生成されたコンテンツ
        """
        timestamp = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")

        if language == "ja":
            return f"""
<h2>はじめに</h2>
<p>ウズベキスタンの{sector}セクターにおけるM&A動向について解説します。</p>

<h2>市場概況</h2>
<p>ウズベキスタンは中央アジア最大の人口を擁し、経済改革が進む注目市場です。
{sector}セクターは特に成長が著しく、M&A活動も活発化しています。</p>

<h3>主要トレンド</h3>
<ul>
<li>外資参入の増加</li>
<li>国内企業の統合・再編</li>
<li>デジタル化の加速</li>
<li>規制緩和による市場開放</li>
</ul>

<h2>投資機会</h2>
<p>{sector}セクターでは以下のような投資機会が存在します：</p>
<ul>
<li>市場拡大期における先行者利益</li>
<li>政府の産業振興政策</li>
<li>若年層人口による労働力確保</li>
<li>周辺国への展開拠点</li>
</ul>

<h2>留意事項</h2>
<p>ウズベキスタンでのM&A実施にあたっては、以下の点に注意が必要です：</p>
<ul>
<li>現地法規制の理解</li>
<li>デューデリジェンスの徹底</li>
<li>文化・言語の違いへの配慮</li>
<li>長期的な事業計画の策定</li>
</ul>

<h2>まとめ</h2>
<p>ウズベキスタン{sector}セクターは、今後も成長が期待される魅力的な市場です。
適切な戦略とパートナーシップにより、成功の可能性が高まります。</p>

<p><em>本記事は{timestamp}に{{UzbekistanMAAgent}}により自動生成されました。</em></p>
"""
        elif language == "en":
            return f"""
<h2>Introduction</h2>
<p>This article discusses M&A trends in Uzbekistan's {sector} sector.</p>

<h2>Market Overview</h2>
<p>Uzbekistan, with the largest population in Central Asia, is an emerging market 
undergoing significant economic reforms. The {sector} sector is experiencing 
particularly strong growth, with M&A activities becoming increasingly active.</p>

<h3>Key Trends</h3>
<ul>
<li>Increasing foreign investment</li>
<li>Domestic corporate consolidation</li>
<li>Accelerating digitalization</li>
<li>Market liberalization through deregulation</li>
</ul>

<h2>Investment Opportunities</h2>
<p>The {sector} sector offers various investment opportunities:</p>
<ul>
<li>First-mover advantages in expanding markets</li>
<li>Government industrial promotion policies</li>
<li>Young workforce availability</li>
<li>Gateway to neighboring markets</li>
</ul>

<h2>Considerations</h2>
<p>When conducting M&A in Uzbekistan, consider:</p>
<ul>
<li>Understanding local regulations</li>
<li>Thorough due diligence</li>
<li>Cultural and language sensitivity</li>
<li>Long-term business planning</li>
</ul>

<h2>Conclusion</h2>
<p>Uzbekistan's {sector} sector is an attractive market with high growth potential. 
Success can be achieved through proper strategy and partnerships.</p>

<p><em>Auto-generated by {{UzbekistanMAAgent}} on {timestamp}</em></p>
"""
        else:  # uz
            return f"""
<h2>Kirish</h2>
<p>Ushbu maqolada O'zbekistonning {sector} sektorida M&A tendentsiyalari muhokama qilinadi.</p>

<h2>Bozor sharhi</h2>
<p>O'zbekiston, Markaziy Osiyodagi eng ko'p aholiga ega mamlakat sifatida, 
muhim iqtisodiy islohotlar o'tkazayotgan rivojlanayotgan bozordir.</p>

<h2>Xulosa</h2>
<p>O'zbekistonning {sector} sektori yuqori o'sish potentsialiga ega jozibador bozordir.</p>

<p><em>{{UzbekistanMAAgent}} tomonidan {timestamp}da avtomatik yaratilgan</em></p>
"""

    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters"""
        # article_typeは必須ではないが、指定する場合は有効な値のみ
        valid_types = ["market_overview", "deal_analysis", "sector_report", "investment_guide"]
        article_type = kwargs.get("article_type")

        if article_type and article_type not in valid_types:
            return False

        return True

    def get_required_params(self) -> List[str]:
        """Get required parameters"""
        return []  # すべてオプショナル（デフォルト値あり）


async def main():
    """Demo execution"""
    agent = Uzbekistanmaagent()

    print(f"Agent: {agent}")
    print(f"Metadata: {agent.get_metadata()}")

    print("\n🇺🇿 ウズベキスタンM&Aエージェントテスト")
    print("=" * 70)

    try:
        # テスト投稿1: 市場概況（日本語）
        print("\n【テスト1】市場概況記事（日本語）")
        result1 = await agent.run(article_type="market_overview", sector="IT", language="ja", status="draft")

        if result1["success"]:
            print(f"✅ 投稿成功！")
            print(f"   Post ID: {result1['data']['post_id']}")
            print(f"   Title: {result1['data']['title']}")
            print(f"   Link: {result1['data']['link']}")
        else:
            print(f"❌ 投稿失敗: {result1.get('error')}")

        # テスト投稿2: 投資ガイド（英語）
        print("\n【テスト2】投資ガイド（英語）")
        result2 = await agent.run(
            article_type="investment_guide", sector="manufacturing", language="en", status="draft"
        )

        if result2["success"]:
            print(f"✅ 投稿成功！")
            print(f"   Post ID: {result2['data']['post_id']}")
            print(f"   Link: {result2['data']['link']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
