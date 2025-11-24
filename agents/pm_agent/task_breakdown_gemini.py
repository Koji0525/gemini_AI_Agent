#!/usr/bin/env python3
"""Gemini APIでタスク分解（完全API版・8個対応）"""

import json
import os
import re
import traceback
from typing import Any, Dict, List

import google.generativeai as genai


class GeminiTaskBreakdownAgent:
    """Gemini APIでタスク分解（8個固定）"""

    def __init__(self, api_key=None):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY環境変数が必要です")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
        print(f"✅ Geminiモデル初期化: gemini-2.0-flash-exp")

    async def generate_tasks_for_goal(
        self, goal_id: int, goal_description: str, num_tasks: int = 8, **kwargs
    ) -> List[Dict[str, Any]]:
        """タスク生成（8個固定）"""

        print(f"🤖 Geminiにタスク分解を依頼中（Goal {goal_id}, {num_tasks}個）...")
        print(f"📝 目標: {goal_description[:100]}...")

        prompt = f"""あなたは経験豊富なプロジェクトマネージャーです。
以下の目標を達成するために、**必ず{num_tasks}個**の実行可能なタスクに分解してください。

【目標】
{goal_description}

【タスク分解の要件】
1. **必ず{num_tasks}個のタスク**を生成すること（絶対条件）
2. 各タスクは具体的で実行可能であること
3. タスクの種類を分散させること:
   - 調査・分析タスク（1-2個）
   - 設計タスク（1-2個）
   - 実装タスク（2-3個）
   - テストタスク（1-2個）
   - ドキュメント作成タスク（1個）

【出力形式】以下のJSON配列形式で**必ず{num_tasks}個**出力:
```json
[
  {{"task_name": "タスク名1", "description": "詳細説明1", "priority": "高"}},
  {{"task_name": "タスク名2", "description": "詳細説明2", "priority": "中"}},
  ...（合計{num_tasks}個）
]
```

**重要**: {num_tasks}個より多くても少なくてもいけません。必ず{num_tasks}個です。
"""

        try:
            print("📤 Gemini APIにリクエスト送信中...")
            response = self.model.generate_content(prompt)

            print(f"✅ レスポンス受信: {len(response.text)}文字")
            print(f"📄 レスポンス内容:\n{response.text[:500]}...")

            # JSON抽出
            tasks = self._extract_json_from_response(response.text)

            if not tasks or len(tasks) < num_tasks:
                print(
                    f"⚠️ タスク数不足（{len(tasks) if tasks else 0}個）。フォールバック生成します。"
                )
                tasks = self._generate_fallback_tasks(goal_description, num_tasks)

            # 指定数に調整
            tasks = tasks[:num_tasks]

            print(f"✅ {len(tasks)}個のタスクを生成しました")
            return tasks

        except Exception as e:
            print(f"❌ Gemini APIエラー: {e}")
            traceback.print_exc()
            return self._generate_fallback_tasks(goal_description, num_tasks)

    def _extract_json_from_response(self, response_text: str) -> List[Dict[str, Any]]:
        """レスポンスからJSON抽出"""
        # コードブロック内のJSONを抽出
        json_match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response_text

        print(f"🔍 JSON抽出結果:\n{json_str[:300]}...")

        try:
            tasks = json.loads(json_str)
            return tasks if isinstance(tasks, list) else []
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析エラー: {e}")
            return []

    def _generate_fallback_tasks(
        self, goal_description: str, num_tasks: int
    ) -> List[Dict[str, Any]]:
        """フォールバックタスク生成（必ず指定数）"""
        print(f"🔄 {num_tasks}個のフォールバックタスクを生成中...")

        templates = [
            {
                "name": "要件分析",
                "desc": "目標の詳細な要件を分析し、実現可能性を評価する",
                "priority": "高",
            },
            {
                "name": "既存システム調査",
                "desc": "関連する既存コンポーネントを調査し、影響範囲を特定する",
                "priority": "高",
            },
            {"name": "設計", "desc": "実装方針と詳細設計を作成する", "priority": "高"},
            {"name": "実装（コア機能）", "desc": "コア機能を実装する", "priority": "高"},
            {"name": "実装（追加機能）", "desc": "追加機能を実装する", "priority": "中"},
            {
                "name": "ユニットテスト",
                "desc": "各コンポーネントの単体テストを作成・実行する",
                "priority": "高",
            },
            {"name": "統合テスト", "desc": "システム全体の統合テストを実行する", "priority": "中"},
            {
                "name": "ドキュメント作成",
                "desc": "実装内容とテスト結果をドキュメント化する",
                "priority": "中",
            },
        ]

        tasks = []
        for i in range(num_tasks):
            template = templates[i % len(templates)]
            tasks.append(
                {
                    "task_name": f"{template['name']}（タスク{i+1}）",
                    "description": f"{template['desc']}\n目標: {goal_description[:100]}",
                    "priority": template["priority"],
                }
            )

        return tasks

    def convert_to_pm_tasks_format(
        self, tasks_detailed: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Gemini APIの出力をpm_tasks形式に変換"""
        pm_tasks = []

        priority_map = {"高": "high", "中": "medium", "低": "low"}

        for task in tasks_detailed:
            task_name = task.get("task_name", "")
            task_desc = task.get("description", "")
            full_description = f"{task_name}\n{task_desc}" if task_name else task_desc

            priority_raw = task.get("priority", "medium")
            priority = priority_map.get(priority_raw, priority_raw.lower())

            pm_tasks.append(
                {
                    "description": full_description,
                    "required_role": "autonomous_agent",
                    "priority": priority,
                    "estimated_time": "未定",
                    "dependencies": "",
                    "execution_type": "automated",
                }
            )

        print(f"✅ {len(pm_tasks)}個のタスクをpm_tasks形式に変換しました")
        return pm_tasks
