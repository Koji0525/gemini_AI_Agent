"""
Gemini APIを使用してゴールをタスクに分解するエージェント
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiTaskBreakdownAgent:
    """Gemini APIでゴールをタスクに分解"""

    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """
        初期化

        Args:
            model_name: 使用するGeminiモデル名
        """
        self.model_name = model_name
        self.model = None
        self._initialize_gemini()

    def _initialize_gemini(self):
        """Gemini APIの初期化"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY が環境変数に設定されていません")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.model_name)
        logger.info(f"✅ Geminiモデル初期化: {self.model_name}")

    async def generate_tasks_for_goal(
        self, goal_id: str, goal_description: str, num_tasks: int = 8, context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        ゴールをタスクに分解

        Args:
            goal_id: ゴールID
            goal_description: ゴールの説明
            num_tasks: 生成するタスク数（デフォルト8）
            context: 追加コンテキスト情報

        Returns:
            タスクのリスト
        """
        logger.info(f"🤖 Geminiにタスク分解を依頼中（Goal {goal_id}）...")
        logger.info(f"📝 目標: {goal_description[:100]}...")

        # プロンプト作成（タスク数を明示）
        prompt = self._create_prompt(goal_description, num_tasks, context)

        try:
            logger.info("📤 Gemini APIにリクエスト送信中...")
            response = self.model.generate_content(prompt)

            logger.info(f"✅ レスポンス受信: {len(response.text)}文字")
            logger.info(f"📄 レスポンス内容:\n{response.text[:500]}...")

            # JSON部分を抽出
            tasks = self._extract_json_from_response(response.text)

            if not tasks:
                logger.warning("⚠️ タスクを抽出できませんでした。デフォルトタスクを生成します。")
                tasks = self._generate_fallback_tasks(goal_description, num_tasks)

            logger.info(f"✅ {len(tasks)}個のタスクを生成しました")
            return tasks

        except Exception as e:
            logger.error(f"❌ Gemini API呼び出しエラー: {e}")
            logger.info("�� フォールバックタスクを生成します")
            return self._generate_fallback_tasks(goal_description, num_tasks)

    def _create_prompt(
        self, goal_description: str, num_tasks: int, context: Optional[str] = None
    ) -> str:
        """タスク分解用プロンプトを作成"""
        prompt = f"""
あなたは優秀なプロジェクトマネージャーです。以下のゴールを**必ず{num_tasks}個**のタスクに分解してください。

# ゴール
{goal_description}

# タスク分解の要件
1. **必ず{num_tasks}個のタスク**に分解すること（これは絶対条件です）
2. 各タスクは具体的で実行可能であること
3. タスク間の依存関係を考慮すること
4. 優先度（高/中/低）を明確にすること
5. 既存システムを保護しながら実装すること

# タスクの種類（{num_tasks}個すべてを含めること）
- 調査・分析タスク（1-2個）
- 設計タスク（1-2個）
- 実装タスク（2-3個）
- テストタスク（1-2個）
- ドキュメント作成タスク（1個）

# 出力形式
以下のJSON配列形式で**必ず{num_tasks}個**のタスクを出力してください：
```json
[
  {{
    "task_name": "タスク名1",
    "description": "詳細な説明1",
    "priority": "高"
  }},
  {{
    "task_name": "タスク名2",
    "description": "詳細な説明2",
    "priority": "中"
  }},
  ...（合計{num_tasks}個）
]
```

**重要**: 必ず{num_tasks}個のタスクを生成してください。それ以上でも以下でもいけません。
"""

        if context:
            prompt += f"\n\n# 追加コンテキスト\n{context}"

        return prompt

    def _extract_json_from_response(self, response_text: str) -> List[Dict[str, Any]]:
        """レスポンスからJSON部分を抽出"""
        # コードブロック内のJSONを抽出
        json_match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # コードブロックがない場合、全体をJSONとして扱う
            json_str = response_text

        logger.info(f"🔍 JSON抽出結果:\n{json_str[:300]}...")

        try:
            tasks = json.loads(json_str)
            if isinstance(tasks, list):
                return tasks
            else:
                logger.warning("⚠️ JSONはリストではありません")
                return []
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON解析エラー: {e}")
            return []

    def _generate_fallback_tasks(
        self, goal_description: str, num_tasks: int
    ) -> List[Dict[str, Any]]:
        """フォールバックタスクを生成（必ず指定数を生成）"""
        logger.info(f"🔄 {num_tasks}個のフォールバックタスクを生成中...")

        task_templates = [
            {
                "name": "要件分析",
                "desc": "ゴールの詳細な要件を分析し、実現可能性を評価する",
                "priority": "高",
            },
            {
                "name": "既存システム調査",
                "desc": "関連する既存コンポーネントを調査し、影響範囲を特定する",
                "priority": "高",
            },
            {"name": "設計", "desc": "実装方針と詳細設計を作成する", "priority": "高"},
            {"name": "実装（フェーズ1）", "desc": "コア機能を実装する", "priority": "高"},
            {"name": "実装（フェーズ2）", "desc": "追加機能を実装する", "priority": "中"},
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
            template = task_templates[i % len(task_templates)]
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
        """
        Gemini APIから返されたタスク詳細をpm_tasks形式に変換

        Args:
            tasks_detailed: Gemini APIから返されたタスクのリスト

        Returns:
            pm_tasks形式のタスクリスト
        """
        pm_tasks = []

        # 優先度マッピング
        priority_map = {
            "高": "high",
            "中": "medium",
            "低": "low",
            "高い": "high",
            "中程度": "medium",
            "低い": "low",
        }

        for task in tasks_detailed:
            task_name = task.get("task_name", "")
            task_desc = task.get("description", "")
            full_description = f"{task_name}\n{task_desc}" if task_name else task_desc

            priority_raw = task.get("priority", "medium")
            priority = priority_map.get(priority_raw, priority_raw.lower())

            pm_task = {
                "description": full_description,
                "required_role": "autonomous_agent",
                "priority": priority,
                "estimated_time": "未定",
                "dependencies": "",
                "execution_type": "automated",
            }

            pm_tasks.append(pm_task)

        logger.info(f"✅ {len(pm_tasks)}個のタスクをpm_tasks形式に変換しました")
        return pm_tasks
