#!/usr/bin/env python3
"""Gemini APIでタスク分解（完全API版）"""

import os
import json
import traceback
import google.generativeai as genai
from typing import Dict, List, Any


class GeminiTaskBreakdownAgent:
    """Gemini APIでタスク分解"""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY環境変数が必要です")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
        print(f"✅ Geminiモデル初期化: gemini-2.0-flash-exp")

    async def generate_tasks_for_goal(self, goal_id: int, goal_description: str, **kwargs) -> List[Dict[str, Any]]:
        """タスク生成（goal_id対応）"""

        print(f"🤖 Geminiにタスク分解を依頼中（Goal {goal_id}）...")
        print(f"�� 目標: {goal_description[:100]}...")

        prompt = f"""あなたは経験豊富なプロジェクトマネージャーです。
以下の目標を達成するために、実行可能な小タスクに分解してください。

【目標】
{goal_description}

【制約】
- タスク数: 2個のみ生成（デバッグ用）
- 最重要なタスクのみ

【出力形式】JSON配列で返してください:
[
  {{"task_name": "タスク名", "description": "詳細", "priority": "高/中/低"}},
  ...
]
"""

        try:
            print("📤 Gemini APIにリクエスト送信中...")
            response = self.model.generate_content(prompt)
            print(f"✅ レスポンス受信: {len(response.text)}文字")

            # JSON抽出
            text = response.text
            print(f"📄 レスポンス内容:\n{text[:500]}...")

            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            print(f"🔍 JSON抽出結果:\n{text[:300]}...")

            tasks = json.loads(text.strip())

            if isinstance(tasks, list) and len(tasks) > 0:
                print(f"✅ {len(tasks)}個のタスクを生成しました")
                return tasks
            else:
                print(
                    f"❌ タスク形式が不正: type={type(tasks)}, len={len(tasks) if isinstance(tasks, list) else 'N/A'}"
                )
                return []

        except json.JSONDecodeError as e:
            print(f"❌ JSON解析エラー: {e}")
            print(f"📄 解析対象テキスト:\n{text}")
            return []
        except Exception as e:
            print(f"❌ Gemini生成エラー: {type(e).__name__}: {e}")
            print(f"📋 詳細トレースバック:")
            traceback.print_exc()
            return []
