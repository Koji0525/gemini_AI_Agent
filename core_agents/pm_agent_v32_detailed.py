#!/usr/bin/env python3
"""
PMAgent v32 Detailed - 詳細タスク分解システム (スプレッドシート保存対応)

【追加機能】
- pm_tasksへのタスク保存
- SafeSheetsWrapper使用
- sheets_schema準拠
"""

import asyncio
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# プロジェクトルート設定
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# .env読み込み
try:
    from dotenv import load_dotenv

    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except:
    pass

# ロギング設定
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)

# Gemini API
import google.generativeai as genai

from tools.safe_sheets_wrapper import SafeSheetsWrapper
# Sheets連携
from tools.sheets_manager import GoogleSheetsManager


class DetailedTaskGenerator:
    """詳細タスク生成エンジン"""

    def __init__(self, api_key: Optional[str] = None, knowledge_manager=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY が設定されていません")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            "gemini-2.5-flash",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 20000,
            },
        )
        self.knowledge_manager = knowledge_manager
        logger.info("✅ DetailedTaskGenerator 初期化完了 (model=gemini-2.5-flash)")

    async def generate_tasks_for_goal(
        self, goal_id: str, goal_description: str, num_tasks: int = 8, use_knowledge: bool = True
    ) -> List[Dict[str, Any]]:
        """ゴールから詳細タスクを生成"""
        logger.info(f"🚀 ゴール {goal_id} のタスク生成開始")

        # ナレッジ検索
        knowledge_context = ""
        if use_knowledge and self.knowledge_manager:
            try:
                search_results = await self._search_knowledge(goal_description)
                if search_results:
                    knowledge_context = self._format_knowledge_context(search_results)
                    logger.info(f"✅ {len(search_results)}件のナレッジを取得")
            except Exception as e:
                logger.warning(f"⚠️ ナレッジ検索エラー: {e}")

        # プロンプト作成
        prompt = self._create_detailed_prompt(
            goal_description=goal_description,
            num_tasks=num_tasks,
            knowledge_context=knowledge_context,
        )

        # API呼び出し
        try:
            response = await self._call_gemini_with_retry(prompt, max_retries=3)
            tasks = self._extract_json_from_response(response.text)

            if not tasks:
                raise ValueError("タスクが生成されませんでした")

            # parent_goal_idを設定
            for task in tasks:
                task["parent_goal_id"] = goal_id

            logger.info(f"✅ {len(tasks)}件のタスクを生成")
            return tasks

        except Exception as e:
            logger.error(f"❌ タスク生成エラー: {e}")
            raise

    def _create_detailed_prompt(
        self, goal_description: str, num_tasks: int, knowledge_context: str = ""
    ) -> str:
        """実行可能な詳細タスクを生成するプロンプト"""
        knowledge_section = ""
        if knowledge_context:
            knowledge_section = f"""
【参考情報】過去の成功事例・ナレッジ
{knowledge_context}
"""

        return f"""あなたは経験豊富なプロジェクトマネージャーです。
以下のゴールを達成するために、**実行可能で詳細なタスク**を{num_tasks}個生成してください。

【ゴール】
{goal_description}

{knowledge_section}

【タスク設計の原則】
1. **実行可能性**: AIエージェント（TaskExecutor）が自律的に実行できること
2. **具体性**: 曖昧さがなく、何をすべきか明確であること
3. **完結性**: 各タスクが独立して完結できること
4. **検証可能性**: 完了したかどうかを明確に判断できること

【各タスクに必ず含める情報】
1. **目的**: なぜこのタスクが必要か
2. **具体的な作業手順**: 5-10ステップの明確な手順
3. **入力情報**: タスク開始時に必要な情報・前提条件
4. **期待される成果物**: ファイル名、内容の概要
5. **完了条件**: どうなったら完了か、検証方法
6. **依存関係**: 他のタスクとの関係（あれば）
7. **注意事項**: リスクと対策、制約条件

【出力形式】
以下のJSON形式で出力してください:

[
  {{
    "task_name": "タスク名（50文字以内）",
    "description": "【目的】\\n（理由）\\n\\n【作業手順】\\n1. 手順\\n2. 手順\\n...\\n\\n【入力情報】\\n- 情報\\n\\n【成果物】\\n- ファイル名\\n\\n【完了条件】\\n- 条件\\n\\n【注意事項】\\n- 注意点",
    "priority": "high/medium/low",
    "estimated_time": "30分/1時間/2時間等",
    "required_role": "autonomous_agent",
    "execution_type": "automated",
    "dependencies": ""
  }}
]

それでは、{num_tasks}個の実行可能な詳細タスクをJSON形式で生成してください:
"""

    async def _search_knowledge(self, query: str) -> List[Dict]:
        """ナレッジベース検索"""
        if not self.knowledge_manager:
            return []
        try:
            if hasattr(self.knowledge_manager, "search_knowledge"):
                results = self.knowledge_manager.search_knowledge(query=query, top_k=3)
            else:
                return []
            return results if results else []
        except Exception as e:
            logger.warning(f"⚠️ ナレッジ検索エラー: {e}")
            return []

    def _format_knowledge_context(self, search_results: List[Dict]) -> str:
        """ナレッジ検索結果をプロンプト用に整形"""
        context = []
        for i, result in enumerate(search_results[:3], 1):
            title = result.get("title", "無題")
            content = result.get("content", "")[:300]
            context.append(f"{i}. {title}\n   {content}")
        return "\n\n".join(context)

    async def _call_gemini_with_retry(self, prompt: str, max_retries: int = 3) -> Any:
        """Gemini API呼び出し（リトライ付き）"""
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"🔄 Gemini API呼び出し (試行 {attempt}/{max_retries})")
                response = await asyncio.to_thread(self.model.generate_content, prompt)
                return response
            except Exception as e:
                logger.warning(f"⚠️ API呼び出し失敗 (試行 {attempt}): {e}")
                if attempt == max_retries:
                    raise
                await asyncio.sleep(2)
        raise Exception("Gemini API呼び出しに失敗しました")

    def _extract_json_from_response(self, response_text: str) -> List[Dict[str, Any]]:
        """レスポンスからJSON抽出"""
        cleaned = re.sub(r"```json\s*", "", response_text)
        cleaned = re.sub(r"```\s*$", "", cleaned)
        cleaned = cleaned.strip()

        match = re.search(r"\[\s*\{.*\}\s*\]", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(0)

        try:
            tasks = json.loads(cleaned)
            logger.info(f"✅ JSON解析成功 ({len(tasks)}件のタスク)")
            return tasks
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON解析エラー: {e}")
            raise


class PMAgentV32Detailed:
    """PMAgent v32 Detailed - スプレッドシート保存対応"""

    def __init__(self, sheets_manager=None, knowledge_manager=None):
        """初期化"""
        self.sheets_manager = sheets_manager
        self.knowledge_manager = knowledge_manager
        self.task_generator = DetailedTaskGenerator(knowledge_manager=knowledge_manager)

        # SafeSheetsWrapper初期化
        if sheets_manager:
            self.sheets = SafeSheetsWrapper(sheets_manager)
            logger.info("✅ SafeSheetsWrapper 初期化完了")
        else:
            self.sheets = None
            logger.warning("⚠️ sheets_managerが未設定。スプレッドシート保存は無効")

        logger.info("✅ PMAgentV32Detailed 初期化完了")

    async def generate_tasks_for_goal(
        self, goal_id: str, goal_description: str, num_tasks: int = 8, use_knowledge: bool = True
    ) -> List[Dict[str, Any]]:
        """ゴールから詳細タスクを生成"""
        return await self.task_generator.generate_tasks_for_goal(
            goal_id=goal_id,
            goal_description=goal_description,
            num_tasks=num_tasks,
            use_knowledge=use_knowledge,
        )

    def convert_to_pm_tasks_format(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """タスクをpm_tasksスキーマ形式に変換"""
        pm_tasks = []
        for task in tasks:
            pm_task = {
                "description": task.get("description", ""),
                "required_role": task.get("required_role", "autonomous_agent"),
                "priority": task.get("priority", "medium"),
                "estimated_time": task.get("estimated_time", "未定"),
                "dependencies": task.get("dependencies", ""),
                "execution_type": task.get("execution_type", "automated"),
                "parent_goal_id": task.get("parent_goal_id", ""),
            }
            pm_tasks.append(pm_task)
        return pm_tasks

    async def write_tasks_to_sheet(self, tasks: List[Dict[str, Any]]):
        """
        タスクをpm_tasksに書き込み

        Args:
            tasks: タスクのリスト
        """
        if not self.sheets:
            logger.error("❌ SafeSheetsWrapperが初期化されていません")
            return

        try:
            logger.info(f"📝 {len(tasks)}個のタスクをpm_tasksに書き込み中...")

            # 既存タスクの最大IDを取得
            existing_tasks_data = self.sheets.safe_read("pm_tasks!A:A")
            max_task_id = 0

            if existing_tasks_data:
                for row in existing_tasks_data[1:]:  # ヘッダーをスキップ
                    if row and len(row) > 0:
                        try:
                            task_id_num = int(row[0])
                            if task_id_num > max_task_id:
                                max_task_id = task_id_num
                        except (ValueError, TypeError):
                            pass

            logger.info(f"✅ 既存タスクの最大ID: {max_task_id}")
            next_task_id = max_task_id + 1

            # 各タスクを書き込み
            for i, task in enumerate(tasks, 1):
                task_id = str(next_task_id)
                parent_goal_id = str(task.get("parent_goal_id", ""))

                # pm_tasksスキーマに従って行データを作成
                task_row = [
                    task_id,  # A: task_id
                    parent_goal_id,  # B: parent_goal_id
                    task.get("description", ""),  # C: description
                    task.get("required_role", "autonomous_agent"),  # D: required_role
                    "pending",  # E: status
                    task.get("priority", "medium"),  # F: priority
                    task.get("estimated_time", "未定"),  # G: estimated_time
                    task.get("dependencies", ""),  # H: dependencies
                    "",  # I: created_at
                    "",  # J: batch_id
                    "",  # K: detail_file_path
                    "",  # L: blank
                    task.get("execution_type", "automated"),  # M: execution_type
                ]

                # 書き込み
                success = self.sheets.safe_append("pm_tasks", [task_row])

                if success:
                    logger.info(f"  ✅ タスク {i}/{len(tasks)} 書き込み完了（ID: {task_id}）")
                    next_task_id += 1
                else:
                    logger.warning(f"  ⚠️ タスク {i}/{len(tasks)} 書き込み失敗")

            logger.info(f"✅ {len(tasks)}個のタスク書き込み完了")

        except Exception as e:
            logger.error(f"❌ タスク書き込みエラー: {e}")
            import traceback

            traceback.print_exc()


# テスト用
async def test_pm_agent_v32():
    """テスト実行"""
    print("=" * 60)
    print("PMAgent v32 Detailed - テスト実行")
    print("=" * 60)

    test_goal = """
既存システムの完全理解と詳細要件定義の作成。

既存のアーキテクチャ、データフロー、テストスイートを徹底的に調査し、
新規開発における制約条件と活用可能な資産を明確化する。
"""

    try:
        # GoogleSheetsManager初期化
        try:
            sheets_manager = GoogleSheetsManager()
            print("✅ GoogleSheetsManager 初期化成功")
        except Exception as e:
            print(f"⚠️ GoogleSheetsManager 初期化失敗: {e}")
            sheets_manager = None

        # PMAgent初期化
        agent = PMAgentV32Detailed(sheets_manager=sheets_manager)

        # タスク生成
        tasks = await agent.generate_tasks_for_goal(
            goal_id="test_001", goal_description=test_goal, num_tasks=8, use_knowledge=False
        )

        print(f"\n✅ タスク生成成功! ({len(tasks)}件)")

        # タスク一覧表示
        for i, task in enumerate(tasks, 1):
            desc = task.get("description", "")
            print(f"\n{i}. {task.get('task_name', 'NO NAME')}")
            print(f"   文字数: {len(desc)}文字")
            print(f"   優先度: {task.get('priority', 'N/A')}")

        # スプレッドシートに保存（sheets_managerが有効な場合）
        if sheets_manager:
            print("\n" + "=" * 60)
            print("📝 スプレッドシートに保存中...")
            print("=" * 60)
            await agent.write_tasks_to_sheet(tasks)
            print("\n✅ スプレッドシート保存完了!")
            print("📊 Google Sheetsで pm_tasks シートを確認してください")

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    import asyncio

    sys.exit(asyncio.run(test_pm_agent_v32()))
