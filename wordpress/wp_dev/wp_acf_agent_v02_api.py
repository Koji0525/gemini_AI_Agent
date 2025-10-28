#!/usr/bin/env python3
"""
WordPressACFエージェント v02 - API版
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


class WordPressACFAgent:
    """WordPressACFエージェント（API版）"""

    def __init__(self, output_folder: Path = None):
        self.gemini_client = GeminiAPIClient()
        self.output_folder = output_folder or Path("agent_outputs/acf")
        self.output_folder.mkdir(parents=True, exist_ok=True)

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """ACFフィールド作成タスクを実行"""
        try:
            print("📋 wp_acf 💬 🔧 ACFフィールド作成開始")

            # ACF仕様を取得
            cpt_name = task.get("cpt_name", "")
            fields = task.get("fields", [])

            # プロンプト構築
            prompt = f"""
あなたはWordPress開発の専門家です。

【タスク】
カスタム投稿タイプ「{cpt_name}」用のAdvanced Custom Fields (ACF)フィールドグループを作成するPHPコードを生成してください。

【フィールド仕様】
{json.dumps(fields, ensure_ascii=False, indent=2)}

【要件】
- functions.phpに追加できる完全なコード
- acf_add_local_field_group()を使用
- 各フィールドのタイプに応じた適切な設定
- 日本語ラベル対応
- フィールドの並び順を保持

PHPコードのみを出力してください。説明は不要です。
"""

            # API経由でコード生成
            response = await self.gemini_client.send_prompt(prompt)

            # PHPコード保存
            output_file = self.output_folder / f"acf_{cpt_name}.php"

            # ```php ``` を削除
            php_code = response
            if "```php" in php_code:
                php_code = php_code.split("```php")[1].split("```")[0].strip()
            elif "```" in php_code:
                php_code = php_code.split("```")[1].split("```")[0].strip()

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(php_code)

            print(f"✅ ACFフィールド作成完了: {output_file}")

            return {"success": True, "message": f"ACFフィールド作成完了: {cpt_name}", "output_file": str(output_file)}

        except Exception as e:
            print(f"📋 wp_acf ❌ ERROR ❌ ACFフィールド作成エラー: {e}")
            return {"success": False, "error": str(e)}


if __name__ == "__main__":

    async def test():
        agent = WordPressACFAgent()

        test_task = {
            "cpt_name": "ma_deal",
            "fields": [
                {"name": "price", "type": "number", "required": True},
                {"name": "industry", "type": "text", "required": True},
                {"name": "description", "type": "textarea", "required": False},
            ],
        }

        result = await agent.execute(test_task)
        print(f"\n結果: {result}")

    asyncio.run(test())
