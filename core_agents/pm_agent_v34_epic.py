"""
PMAgentV34Epic - Gemini API 2000文字詳細タスク分解版

Version: v34
変更内容:
- Gemini APIで実際のゴール内容を詳細分析
- 各タスク1500-2000文字の説明生成
- 目的、作業内容、成功基準、前提条件、制約事項を含む
- JSONフォーマットでの構造化レスポンス
"""

import asyncio
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

# Gemini API
import google.generativeai as genai

from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
from tools.sheets_manager import GoogleSheetsManager


class DetailedStoryGenerator:
    """詳細ストーリー生成クラス（Gemini API使用）"""

    def __init__(self, epic: Dict[str, Any], start_task_id: int):
        self.epic = epic
        self.epic_id = epic.get("goal_id", "UNKNOWN")
        self.start_task_id = start_task_id
        self.stories: List[Dict[str, Any]] = []

        # Gemini API初期化
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY環境変数が設定されていません")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")

    def generate_stories(self) -> List[Dict[str, Any]]:
        """エピックから詳細ストーリーを生成（2000文字レベル）"""
        description = self.epic.get("goal_description", "")

        print(f"    🤖 Gemini APIで詳細タスク分解中（2000文字レベル）...")

        # Gemini APIプロンプト
        prompt = f"""
あなたは経験豊富なプロジェクトマネージャーです。以下のゴールを5つの詳細な実行可能タスクに分解してください。

【ゴールID】
{self.epic_id}

【ゴール内容】
{description[:3000]}

【タスク分解指示】

以下のフェーズに沿って5つのタスクを作成：
1. 要件定義と設計フェーズ
2. 基盤実装フェーズ
3. コア機能実装フェーズ
4. テストと品質保証フェーズ
5. デプロイと運用準備フェーズ

各タスクは以下の構造で**1500-2000文字**の詳細な説明を含めてください：
```
【目的】
このタスクで達成すべきゴールを明確に記述（200-300文字）

【作業内容】
具体的な作業ステップを箇条書きで詳細に（500-700文字）
- ステップ1: ...
- ステップ2: ...
- ステップ3: ...
（以下、必要なだけ）

【成功基準】
タスク完了の判断基準を具体的に（200-300文字）
1. ...
2. ...
3. ...

【前提条件】
タスク開始前に必要な条件やリソース（200-300文字）

【制約事項】
注意すべき制限や制約（200-300文字）

【チェックポイント】
進捗確認のためのマイルストーン（200-300文字）
```

【出力形式】
JSON形式で以下のように出力してください：

{{
  "tasks": [
    {{
      "title": "フェーズ1: 要件定義と設計",
      "description": "上記の構造に従った1500-2000文字の詳細説明",
      "priority": "high",
      "estimated_time": 16,
      "acceptance_criteria": ["基準1", "基準2", "基準3"]
    }},
    {{
      "title": "フェーズ2: 基盤実装",
      "description": "上記の構造に従った1500-2000文字の詳細説明",
      "priority": "high",
      "estimated_time": 24,
      "acceptance_criteria": ["基準1", "基準2", "基準3"]
    }},
    {{
      "title": "フェーズ3: コア機能実装",
      "description": "上記の構造に従った1500-2000文字の詳細説明",
      "priority": "medium",
      "estimated_time": 32,
      "acceptance_criteria": ["基準1", "基準2", "基準3"]
    }},
    {{
      "title": "フェーズ4: テストと品質保証",
      "description": "上記の構造に従った1500-2000文字の詳細説明",
      "priority": "high",
      "estimated_time": 16,
      "acceptance_criteria": ["基準1", "基準2", "基準3"]
    }},
    {{
      "title": "フェーズ5: デプロイと運用準備",
      "description": "上記の構造に従った1500-2000文字の詳細説明",
      "priority": "medium",
      "estimated_time": 8,
      "acceptance_criteria": ["基準1", "基準2", "基準3"]
    }}
  ]
}}

【重要な指示】
1. 各タスクのdescriptionは必ず1500文字以上にする
2. ゴール内容を深く分析し、具体的で実行可能な手順を記載
3. 技術的な詳細、使用ツール、実装方針を含める
4. 見積もり時間は現実的な値を設定
5. JSON形式で出力（```json マーカーは不要）
"""

        try:
            # Gemini API呼び出し
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # JSONマーカー除去
            response_text = re.sub(r"^```json\s*", "", response_text)
            response_text = re.sub(r"\s*```$", "", response_text)
            response_text = response_text.strip()

            # JSONパース
            result = json.loads(response_text)

            # ストーリー生成
            self.stories = []
            current_task_id = self.start_task_id

            for i, task_data in enumerate(result["tasks"], 1):
                # 依存関係設定
                dependencies = []
                if i > 1:
                    dependencies.append(str(current_task_id - 1))

                desc_length = len(task_data["description"])
                print(f"      📝 タスク{current_task_id}: {desc_length}文字")

                story = {
                    "task_id": str(current_task_id),
                    "epic_id": self.epic_id,
                    "title": task_data["title"],
                    "description": task_data["description"],
                    "priority": task_data.get("priority", "medium"),
                    "estimated_time": task_data.get("estimated_time", 8),
                    "dependencies": dependencies,
                    "acceptance_criteria": task_data.get("acceptance_criteria", []),
                }

                self.stories.append(story)
                current_task_id += 1

            print(f"    ✅ Gemini APIで{len(self.stories)}件の詳細タスク生成完了")

            return self.stories

        except json.JSONDecodeError as e:
            print(f"    ⚠️  JSON解析エラー: {e}")
            print(f"    応答内容: {response_text[:200]}...")
            print(f"    → 再試行...")

            # 再試行（よりシンプルなプロンプト）
            return self._retry_with_simple_prompt(description)

        except Exception as e:
            print(f"    ⚠️  Gemini APIエラー: {e}")
            print(f"    → 再試行...")
            return self._retry_with_simple_prompt(description)

    def _retry_with_simple_prompt(self, description: str) -> List[Dict[str, Any]]:
        """シンプルなプロンプトで再試行"""
        try:
            prompt = f"""
以下のゴールを5つのタスクに分解し、各タスクの説明を1500文字以上で記述してください。

ゴール: {description[:2000]}

各タスクには以下を含めてください：
- 目的（何を達成するか）
- 作業内容（具体的な手順）
- 成功基準（完了の判断基準）
- 前提条件
- 制約事項

JSON形式で出力：
{{
  "tasks": [
    {{"title": "...", "description": "1500文字以上の詳細説明", "priority": "high/medium/low", "estimated_time": 数値, "acceptance_criteria": ["...", "..."]}},
    ...
  ]
}}
"""

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            response_text = re.sub(r"^```json\s*", "", response_text)
            response_text = re.sub(r"\s*```$", "", response_text)

            result = json.loads(response_text.strip())

            self.stories = []
            current_task_id = self.start_task_id

            for i, task_data in enumerate(result["tasks"], 1):
                dependencies = []
                if i > 1:
                    dependencies.append(str(current_task_id - 1))

                story = {
                    "task_id": str(current_task_id),
                    "epic_id": self.epic_id,
                    "title": task_data["title"],
                    "description": task_data["description"],
                    "priority": task_data.get("priority", "medium"),
                    "estimated_time": task_data.get("estimated_time", 8),
                    "dependencies": dependencies,
                    "acceptance_criteria": task_data.get("acceptance_criteria", []),
                }

                self.stories.append(story)
                current_task_id += 1

            return self.stories

        except Exception as e:
            print(f"    ❌ 再試行も失敗: {e}")
            return []


class PMAgentV34Epic:
    """PMエージェント v34 - 詳細タスク分解版"""

    def __init__(self, sheets_manager=None, knowledge_manager=None):
        self.sheets = sheets_manager or GoogleSheetsManager()
        self.knowledge = knowledge_manager or KnowledgeManager()
        self.batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _get_next_task_id(self) -> int:
        """次のtask_IDを取得"""
        try:
            tasks_data = self.sheets.read_range("pm_tasks!A:A")

            if not tasks_data or len(tasks_data) <= 1:
                return 1

            max_id = 0
            for row in tasks_data[1:]:
                if row and row[0]:
                    try:
                        task_id = int(row[0])
                        max_id = max(max_id, task_id)
                    except ValueError:
                        continue

            next_id = max_id + 1
            print(f"    📊 既存タスク最大ID: {max_id} → 次のID: {next_id}")

            return next_id

        except Exception as e:
            print(f"    ⚠️  task_ID取得エラー: {e}")
            return 1

    async def process_epics(self) -> bool:
        """アクティブなエピックを処理"""
        try:
            print("=" * 80)
            print("PMAgentV34Epic: 詳細タスク分解開始（2000文字レベル）")
            print("=" * 80)
            print()

            # アクティブなエピック取得
            print("[1/4] アクティブなエピック取得中...")
            goals_data = self.sheets.read_range("project_goal!A:Z")

            if not goals_data or len(goals_data) < 2:
                print("⚠️  ゴールデータが見つかりません")
                return False

            headers = goals_data[0]
            rows = goals_data[1:]

            goal_id_idx = headers.index("goal_id")
            status_idx = headers.index("status")
            desc_idx = headers.index("goal_description") if "goal_description" in headers else 1

            active_epics = []
            for row in rows:
                if len(row) > max(goal_id_idx, status_idx, desc_idx):
                    if row[status_idx].lower() == "active":
                        epic = {
                            "goal_id": row[goal_id_idx],
                            "status": row[status_idx],
                            "goal_description": row[desc_idx] if len(row) > desc_idx else "",
                        }
                        active_epics.append(epic)

            if not active_epics:
                print("⚠️  アクティブなエピックがありません")
                return False

            print(f"✅ {len(active_epics)}件のアクティブなエピック取得")
            print()

            # 次のtask_ID確認
            print("[2/4] 次のtask_ID確認中...")
            next_task_id = self._get_next_task_id()
            print()

            # エピック処理
            print("[3/4] 詳細タスク分解実行中...")
            success_count = 0
            current_task_id = next_task_id

            for i, epic in enumerate(active_epics, 1):
                print(f"  [{i}/{len(active_epics)}] エピック{epic['goal_id']}処理中...")

                success, tasks_created = await self._process_single_epic(epic, current_task_id)
                if success:
                    success_count += 1
                    current_task_id += tasks_created
                    print(f"  ✅ エピック{epic['goal_id']}処理成功（{tasks_created}タスク作成）")
                else:
                    print(f"  ⚠️  エピック{epic['goal_id']}処理失敗")
                print()

            print(f"[4/4] 処理完了: {success_count}/{len(active_epics)}件成功")
            print()

            print("=" * 80)
            print(f"✅ PMAgentV34Epic処理完了")
            print("=" * 80)

            return success_count > 0

        except Exception as e:
            print(f"❌ エラー: {e}")
            import traceback

            traceback.print_exc()
            return False

    async def _process_single_epic(self, epic: Dict[str, Any], start_task_id: int) -> tuple:
        """単一エピックを処理"""
        try:
            generator = DetailedStoryGenerator(epic, start_task_id)
            stories = generator.generate_stories()

            if not stories:
                print(f"    ⚠️  ストーリー生成失敗")
                return False, 0

            success = await self._write_stories_to_sheets(epic_id=epic["goal_id"], stories=stories)

            return success, len(stories)

        except Exception as e:
            print(f"    ❌ エラー: {e}")
            import traceback

            traceback.print_exc()
            return False, 0

    async def _write_stories_to_sheets(self, epic_id: str, stories: List[Dict[str, Any]]) -> bool:
        """ストーリーをpm_tasksシートに書き込み"""
        try:
            rows_to_append = []

            for story in stories:
                row = [
                    story["task_id"],
                    epic_id,
                    story["description"],
                    "developer",
                    "pending",
                    story["priority"],
                    str(story["estimated_time"]),
                    ",".join(story["dependencies"]),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    self.batch_id,
                    "",
                    "",
                    "auto",
                ]

                rows_to_append.append(row)

            print(f"    📝 {len(rows_to_append)}行をpm_tasksシートに書き込み中...")
            success = self.sheets.append_rows("pm_tasks", rows_to_append)

            if success:
                print(f"    ✅ 書き込み成功")
            else:
                print(f"    ❌ 書き込み失敗")

            return success

        except Exception as e:
            print(f"    ❌ 書き込みエラー: {e}")
            import traceback

            traceback.print_exc()
            return False


async def main():
    """テスト実行用メイン関数"""
    print("\n")
    print("=" * 80)
    print("PMAgentV34Epic テスト実行（2000文字詳細タスク分解）")
    print("=" * 80)
    print("\n")

    agent = PMAgentV34Epic()
    success = await agent.process_epics()

    if success:
        print("\n✅ テスト成功")
    else:
        print("\n⚠️  テスト失敗")


if __name__ == "__main__":
    asyncio.run(main())
