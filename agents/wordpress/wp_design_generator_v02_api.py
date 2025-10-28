#!/usr/bin/env python3
"""
WordPress設計図生成エージェント v02 - API版
Gemini APIを使用してブラウザ不要
"""
import asyncio
import json
import sys
from typing import Dict, Any
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from browser_control.gemini_api_client import GeminiAPIClient

class WPDesignGenerator:
    """WordPress設計図生成エージェント（API版）"""
    
    def __init__(self):
        """初期化（ブラウザ不要）"""
        self.gemini_client = GeminiAPIClient()
        self.design_templates = self._load_design_templates()
    
    def _load_design_templates(self) -> Dict[str, Any]:
        """設計図テンプレートを読み込み"""
        return {
            "ma_portal": {
                "name": "M&Aポータルサイト",
                "description": "M&A市場向けポータルサイト",
                "components": ["案件一覧", "検索機能", "問い合わせ"]
            }
        }
    
    def _create_design_prompt(self, goal_description: str) -> str:
        """設計図生成プロンプトを作成"""
        return f"""
以下の目標に基づいて、WordPressサイトの詳細な設計図を作成してください。

【目標】
{goal_description}

【出力形式】
JSON形式で以下の構造で出力してください：

{{
    "site_name": "サイト名",
    "site_type": "サイトタイプ",
    "description": "サイト説明",
    "custom_post_types": [
        {{
            "slug": "投稿タイプスラッグ",
            "name": "投稿タイプ名",
            "singular_name": "単数形名",
            "plural_name": "複数形名",
            "fields": [
                {{"name": "フィールド名", "type": "フィールドタイプ", "required": true}}
            ]
        }}
    ],
    "taxonomies": [
        {{
            "name": "タクソノミー名",
            "slug": "タクソノミースラッグ",
            "post_types": ["関連する投稿タイプ"],
            "hierarchical": true
        }}
    ],
    "required_plugins": ["必要なプラグイン名"]
}}

必ずJSON形式のみで回答してください。説明文は不要です。
"""
    
    async def generate_design_from_goal(self, goal_description: str) -> Dict[str, Any]:
        """
        目標から設計図を生成（API版）
        
        Args:
            goal_description: プロジェクト目標の説明
            
        Returns:
            生成された設計図
        """
        try:
            print(f"🎨 設計図生成開始: {goal_description}...")
            print("🤖 Gemini APIで設計図を生成中...")
            
            # プロンプトを作成
            prompt = self._create_design_prompt(goal_description)
            
            # API経由でプロンプトを送信
            response = await self.gemini_client.send_prompt(prompt)
            
            # JSON形式でパース
            design = self._parse_design_response(response)
            
            print(f"✅ 設計図生成完了: {design.get('site_name', 'Unknown')}")
            
            return design
            
        except Exception as e:
            print(f"❌ 設計図生成エラー: {e}")
            raise
    
    def _parse_design_response(self, response_text: str) -> Dict[str, Any]:
        """API応答をパースして設計図として整形"""
        try:
            # JSONブロックを抽出（```json ``` で囲まれている場合）
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                json_str = response_text.strip()
            
            design = json.loads(json_str)
            return design
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON解析エラー: {e}")
            print(f"応答内容: {response_text[:500]}")
            raise Exception("設計図のJSON解析に失敗しました")

# 後方互換性のため
async def main():
    """テスト用メイン関数"""
    generator = WPDesignGenerator()
    
    test_goal = "ウズベキスタンのM&A市場向け多言語ポータルサイト"
    design = await generator.generate_design_from_goal(test_goal)
    
    print("\n📋 生成された設計図:")
    print(json.dumps(design, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
