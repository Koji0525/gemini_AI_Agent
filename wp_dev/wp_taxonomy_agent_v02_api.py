#!/usr/bin/env python3
"""
WordPressタクソノミーエージェント v02 - API版
"""
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any
import json

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from browser_control.gemini_api_client import GeminiAPIClient


class WordPressTaxonomyAgent:
    """WordPressタクソノミーエージェント（API版）"""

    def __init__(self, output_folder: Path = None):
        self.gemini_client = GeminiAPIClient()
        self.output_folder = output_folder or Path("agent_outputs/taxonomies")
        self.output_folder.mkdir(parents=True, exist_ok=True)

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """タクソノミー作成タスクを実行"""
        try:
            print("📋 wp_taxonomy 💬 🔧 タクソノミー作成開始")

            # タクソノミー仕様を取得
            taxonomy_spec = task.get("taxonomy_spec", {})

            # プロンプト構築
            prompt = f"""
あなたはWordPress開発の専門家です。

【タスク】
以下の仕様でタクソノミー（分類）を作成するPHPコードを生成してください：

{json.dumps(taxonomy_spec, ensure_ascii=False, indent=2)}

【要件】
- functions.phpに追加できる完全なコード
- register_taxonomy()を使用
- 日本語ラベル対応
- 階層構造（hierarchical）の設定を含む
- 管理画面での表示設定を含む

PHPコードのみを出力してください。説明は不要です。
"""

            # API経由でコード生成
            response = await self.gemini_client.send_prompt(prompt)

            # PHPコード保存
            slug = taxonomy_spec.get("slug", "custom_taxonomy")
            output_file = self.output_folder / f"taxonomy_{slug}.php"

            # ```php ``` を削除
            php_code = response
            if "```php" in php_code:
                php_code = php_code.split("```php")[1].split("```")[0].strip()
            elif "```" in php_code:
                php_code = php_code.split("```")[1].split("```")[0].strip()

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(php_code)

            print(f"✅ タクソノミー作成完了: {output_file}")

            return {"success": True, "message": f"タクソノミー作成完了: {slug}", "output_file": str(output_file)}

        except Exception as e:
            print(f"📋 wp_taxonomy ❌ ERROR ❌ タクソノミー作成エラー: {e}")
            return {"success": False, "error": str(e)}


if __name__ == "__main__":

    async def test():
        agent = WordPressTaxonomyAgent()

        test_task = {
            "taxonomy_spec": {
                "name": "業種",
                "slug": "industry",
                "post_types": ["m_a_deal", "market_news"],
                "hierarchical": True,
            }
        }

        result = await agent.execute(test_task)
        print(f"\n結果: {result}")

    asyncio.run(test())
