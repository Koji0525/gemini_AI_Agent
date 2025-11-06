"""
Gemini API利用可能モデル確認ツール
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


def check_available_models():
    """利用可能なモデルを確認"""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("❌ GEMINI_API_KEY が設定されていません")
        return

    genai.configure(api_key=api_key)

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📋 Gemini API 利用可能モデル一覧")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    try:
        models = genai.list_models()

        generation_models = []

        for model in models:
            # generateContent をサポートするモデルのみ抽出
            if "generateContent" in model.supported_generation_methods:
                generation_models.append(model.name)
                print(f"✅ {model.name}")
                print(f"   説明: {model.display_name}")
                print(f"   サポート: {', '.join(model.supported_generation_methods)}")
                print()

        if generation_models:
            print(f"📊 合計 {len(generation_models)} 個のモデルが利用可能")
            print(f"\n推奨設定（.env）:")
            print(f"GEMINI_MODEL={generation_models[0].replace('models/', '')}")
        else:
            print("⚠️ 利用可能なモデルが見つかりませんでした")

    except Exception as e:
        print(f"❌ エラー: {e}")


if __name__ == "__main__":
    check_available_models()
