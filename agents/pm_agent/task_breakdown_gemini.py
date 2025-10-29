#!/usr/bin/env python3
"""Gemini APIでタスク分解（完全API版）"""

import os
import json
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

    async def generate_tasks_for_goal(
        self, goal_id: int, goal_description: str, **kwargs  # 他の引数を無視
    ) -> List[Dict[str, Any]]:
        """タスク生成（goal_id対応）"""

        print(f"🤖 Geminiにタスク分解を依頼中（Goal {goal_id}）...")

        prompt = f"""あなたは経験豊富なプロジェクトマネージャーです。
以下の目標を達成するために、実行可能な小タスクに分解してください。

【目標】
{goal_description}

【出力形式】JSON配列で返してください:
[
  {{"task_name": "タスク名", "description": "詳細", "priority": "高/中/低"}},
  ...
]
"""

        try:
            response = self.model.generate_content(prompt)

            # JSON抽出
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]

            tasks = json.loads(text.strip())

            if isinstance(tasks, list):
                print(f"✅ {len(tasks)}個のタスクを生成しました")
                return tasks
            else:
                print("❌ タスク形式が不正です")
                return []

        except Exception as e:
            print(f"❌ Gemini生成エラー: {e}")
            return []
