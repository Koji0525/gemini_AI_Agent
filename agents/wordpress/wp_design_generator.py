#!/usr/bin/env python3
"""
WordPress設計図生成エージェント
Gemini AIを使ってWordPressサイトの設計図を自動生成
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from browser_control.browser_controller import BrowserController
from configuration.config_loader import ConfigLoader


class WPDesignGenerator:
    """WordPress設計図生成エージェント"""

    def __init__(self, browser_controller: BrowserController):
        self.browser = browser_controller
        self.design_templates = self._load_design_templates()

    def _load_design_templates(self) -> Dict[str, Any]:
        """設計図テンプレートを読み込み"""
        return {
            "ma_portal": {
                "name": "M&Aポータルサイト",
                "description": "ウズベキスタンのM&A市場向けポータルサイト",
                "components": ["custom_post_types", "taxonomies", "acf_fields", "user_roles", "plugins"],
            },
            "news_site": {
                "name": "ニュースサイト",
                "description": "多言語ニュース配信サイト",
                "components": ["post_types", "categories", "tags", "rss_feeds"],
            },
        }

    async def generate_design_from_goal(self, goal_description: str) -> Dict[str, Any]:
        """目標説明から設計図を生成"""
        print(f"🎨 設計図生成開始: {goal_description[:50]}...")

        # Gemini AIを使って設計図を生成
        design_spec = await self._generate_with_gemini(goal_description)

        # テンプレートとマージ
        final_design = await self._merge_with_template(design_spec, goal_description)

        # 設計図を保存
        await self._save_design(final_design)

        return final_design

    async def _generate_with_gemini(self, goal_description: str) -> Dict[str, Any]:
        """Gemini AIで設計図を生成"""
        print("🤖 Gemini AIで設計図を生成中...")

        # ブラウザでGeminiにアクセス
        await self.browser.page.goto("https://gemini.google.com/")
        await asyncio.sleep(3)

        # プロンプトを作成
        prompt = self._create_design_prompt(goal_description)

        # プロンプトを送信
        await self.browser.send_prompt(prompt)
        await asyncio.sleep(10)  # 応答待機

        # レスポンスを取得
        response = await self.browser.extract_latest_text_response()

        # JSON形式でパース
        design_spec = self._parse_design_response(response)

        return design_spec

    def _create_design_prompt(self, goal_description: str) -> str:
        """設計図生成用のプロンプトを作成"""
        return f"""
以下の目標に基づいて、WordPressサイトの詳細な設計図を作成してください。

【目標】
{goal_description}

【出力形式】
以下のJSON形式で出力してください：

{{
  "site_type": "サイトの種類（例: ma_portal, news_site, corporate_site）",
  "site_name": "サイト名",
  "description": "サイトの詳細説明",
  "target_audience": "ターゲットユーザー",
  "languages": ["使用言語の配列"],
  "custom_post_types": [
    {{
      "name": "投稿タイプ名",
      "singular_name": "単数形名",
      "plural_name": "複数形名", 
      "description": "説明",
      "fields": [
        {{
          "name": "フィールド名",
          "type": "フィールドタイプ",
          "required": true/false,
          "description": "フィールド説明"
        }}
      ]
    }}
  ],
  "taxonomies": [
    {{
      "name": "タクソノミー名",
      "post_types": ["関連投稿タイプ"],
      "hierarchical": true/false
    }}
  ],
  "required_plugins": ["必要なプラグインの配列"],
  "theme_settings": {{
    "header_type": "ヘッダータイプ",
    "color_scheme": "カラースキーム",
    "layout": "レイアウト"
  }},
  "page_structure": ["必要なページの配列"]
}}

【重要】
- 具体的で実装可能な設計図にしてください
- ウズベキスタンのM&A市場向けの場合は、多言語対応（英語、ロシア語、ウズベク語）を考慮
- 既存のプラグイン（Polylang, ACF Proなど）を活用
- コクーンテーマを前提として設計
"""

    def _parse_design_response(self, response: str) -> Dict[str, Any]:
        """Geminiのレスポンスをパース"""
        try:
            # JSON部分を抽出
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response

            # JSONパース
            design_spec = json.loads(json_str)
            return design_spec

        except Exception as e:
            print(f"❌ 設計図のパースエラー: {e}")
            # フォールバック設計図を返す
            return self._create_fallback_design()

    def _create_fallback_design(self) -> Dict[str, Any]:
        """フォールバック設計図"""
        return {
            "site_type": "ma_portal",
            "site_name": "M&Aポータル",
            "description": "ウズベキスタンM&A市場向けポータルサイト",
            "custom_post_types": [
                {
                    "name": "ma_case",
                    "singular_name": "M&A案件",
                    "plural_name": "M&A案件",
                    "description": "M&A案件情報",
                    "fields": [
                        {"name": "price", "type": "number", "required": True, "description": "希望価格"},
                        {"name": "industry", "type": "text", "required": True, "description": "業種"},
                        {"name": "location", "type": "text", "required": True, "description": "所在地"},
                    ],
                }
            ],
            "taxonomies": [{"name": "industry_category", "post_types": ["ma_case"], "hierarchical": True}],
            "required_plugins": ["polylang", "advanced-custom-fields"],
            "languages": ["en", "ru", "uz"],
        }

    async def _merge_with_template(self, design_spec: Dict[str, Any], goal_description: str) -> Dict[str, Any]:
        """テンプレートとマージ"""
        site_type = design_spec.get("site_type", "ma_portal")
        template = self.design_templates.get(site_type, self.design_templates["ma_portal"])

        merged_design = {
            **template,
            **design_spec,
            "generated_from": goal_description,
            "timestamp": asyncio.get_event_loop().time(),
            "version": "1.0",
        }

        return merged_design

    async def _save_design(self, design: Dict[str, Any]):
        """設計図を保存"""
        timestamp = int(asyncio.get_event_loop().time())
        filename = f"wp_design_{timestamp}.json"
        design_dir = Path("agent_outputs/wordpress_designs")
        design_dir.mkdir(exist_ok=True)

        design_file = design_dir / filename
        with open(design_file, "w", encoding="utf-8") as f:
            json.dump(design, f, indent=2, ensure_ascii=False)

        print(f"💾 設計図を保存: {design_file}")


async def test_design_generator():
    """設計図生成のテスト"""
    try:
        from browser_control.browser_controller import BrowserController

        print("🎨 WordPress設計図生成エージェント テスト開始")

        # ブラウザを初期化
        browser = BrowserController()
        await browser.initialize()

        # 設計図生成エージェントを作成
        generator = WPDesignGenerator(browser)

        # テスト用の目標
        test_goal = "ウズベキスタンのM&A市場向け多言語ポータルサイトを構築する。投資家と事業主をつなぎ、案件情報を共有できるプラットフォームを作りたい。"

        # 設計図を生成
        design = await generator.generate_design_from_goal(test_goal)

        print("✅ 設計図生成完了:")
        print(json.dumps(design, indent=2, ensure_ascii=False))

        # クリーンアップ
        await browser.cleanup()

    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_design_generator())
