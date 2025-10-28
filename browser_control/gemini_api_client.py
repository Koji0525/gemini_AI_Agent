#!/usr/bin/env python3
"""
Gemini API クライアント
ブラウザ操作の代わりにAPIを使用
"""
import google.generativeai as genai
import os
from dotenv import load_dotenv


class GeminiAPIClient:
    """Gemini APIクライアント"""

    def __init__(self):
        """初期化"""
        # .envファイルを読み込み
        load_dotenv()

        # APIキーを取得（GEMINI_API_KEY → GOOGLE_API_KEYの順で試す）
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY または GOOGLE_API_KEY が設定されていません")

        genai.configure(api_key=api_key)

        # モデル設定（最新の高速モデル）
        self.model = genai.GenerativeModel("gemini-2.5-flash")

        print(f"🤖 Gemini APIクライアント初期化完了")
        print(f"   モデル: gemini-2.5-flash")

    async def send_prompt(self, prompt: str) -> str:
        """
        プロンプトを送信して応答を取得

        Args:
            prompt: 送信するプロンプト

        Returns:
            応答テキスト
        """
        try:
            print(f"📝 Gemini APIにプロンプト送信: {prompt[:80]}...")

            response = self.model.generate_content(prompt)

            result = response.text

            print(f"✅ 応答受信: {len(result)}文字")
            return result

        except Exception as e:
            print(f"❌ API送信エラー: {e}")
            raise Exception(f"Gemini API送信失敗: {e}")

    def cleanup(self):
        """クリーンアップ（互換性のため）"""
        print("✅ Gemini APIクライアント クリーンアップ完了")
