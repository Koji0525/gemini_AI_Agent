"""
TechBlogAgent - Auto-generated WordPress agent

Description: Technical blog article generation and publishing agent
Version: 1.0.0
Author: Integration Test
Created: 2025-10-29T07:25:32.622544
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


class Techblogagent(AgentTemplate):
    """
    Technical blog article generation and publishing agent

    This agent is auto-generated for WordPress content management.
    """

    def __init__(self):
        metadata = AgentMetadata(
            name="TechBlogAgent",
            version="1.0.0",
            description="Technical blog article generation and publishing agent",
            author="Integration Test",
            created_at=datetime.fromisoformat("2025-10-29T07:25:32.622544"),
            dependencies=["requests", "python-dotenv"],
            capabilities=["wordpress_post", "content_generation", "auto_publish"],
            tags=["wordpress", "auto-generated", "cms"],
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
        WordPress記事を生成・投稿

        Args:
            title: 記事タイトル
            content: 記事内容（省略時は自動生成）
            category: カテゴリ（省略時はデフォルト）
            tags: タグリスト
            status: 投稿ステータス（'draft' or 'publish'）

        Returns:
            投稿結果
        """
        title = kwargs.get("title")
        content = kwargs.get("content")
        category = kwargs.get("category", "Uncategorized")
        tags = kwargs.get("tags", [])
        status = kwargs.get("status", "draft")

        if not title:
            raise ValueError("Title is required")

        # コンテンツが指定されていない場合は簡単な自動生成
        if not content:
            content = self._generate_default_content(title)

        # WordPress投稿データ作成
        post_data = {"title": title, "content": content, "status": status}

        # カテゴリ設定
        if category != "Uncategorized":
            post_data["categories"] = [category]

        # タグ設定
        if tags:
            post_data["tags"] = tags

        try:
            # WordPress投稿
            result = self.wp_client.create_post(**post_data)

            return {
                "post_id": result.get("id"),
                "title": result.get("title", {}).get("rendered"),
                "link": result.get("link"),
                "status": result.get("status"),
                "date": result.get("date"),
            }

        except Exception as e:
            raise RuntimeError(f"WordPress post failed: {e}")

    def _generate_default_content(self, title: str) -> str:
        """
        デフォルトコンテンツを生成

        Args:
            title: 記事タイトル

        Returns:
            生成されたコンテンツ
        """
        return f"""
<h2>Introduction</h2>
<p>This article discusses: {title}</p>

<h2>Main Content</h2>
<p>Auto-generated content by TechBlogAgent.</p>
<p>Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

<h2>Conclusion</h2>
<p>This article was automatically generated and published by the dynamic agent system.</p>
"""

    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters"""
        return "title" in kwargs

    def get_required_params(self) -> List[str]:
        """Get required parameters"""
        return ["title"]


async def main():
    """Demo execution"""
    agent = Techblogagent()

    print(f"Agent: {agent}")
    print(f"Metadata: {agent.get_metadata()}")

    # WordPress接続テスト
    print("\nTesting WordPress connection...")

    try:
        # テスト投稿（ドラフト）

        # 標準環境変数ローダー（自動追加）import sysfrom pathlib import Pathsys.path.insert(0, str(Path(__file__).parent.parent))from tools.env_loader import StandardEnvLoaderif not StandardEnvLoader.load_and_verify():    print("環境変数の読み込みに失敗しました")    sys.exit(1)
        result = await agent.run(title="Test Post from TechBlogAgent", status="draft")

        if result["success"]:
            print(f"\n✅ Test post created successfully!")
            print(f"   Post ID: {result['data']['post_id']}")
            print(f"   Link: {result['data']['link']}")
        else:
            print(f"\n❌ Test post failed: {result.get('error')}")

    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
