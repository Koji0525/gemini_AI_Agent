#!/usr/bin/env python3
"""
PMAgent v33 Epic - 大規模コード生成対応版（JSON解析修正版）

【Phase 1実装】
- T1.1.1: EpicTaskGeneratorクラス ✅
- T1.1.2: Epicプロンプト設計 ✅
- T1.1.3: ナレッジ連携実装 ✅
- T1.1.4: SafeSheetsWrapper連携 ✅
- 修正: JSON解析エラーの堅牢化 ✅
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
        logger_init_msg = f"✅ .envファイル読み込み成功: {env_path}"
    else:
        logger_init_msg = f"⚠️ .envファイルが見つかりません: {env_path}"
except ImportError:
    logger_init_msg = "⚠️ python-dotenvが未インストール"
except Exception as e:
    logger_init_msg = f"⚠️ .env読み込みエラー: {e}"

# ロギング設定
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)
logger.info(logger_init_msg)

# Gemini API
import google.generativeai as genai

# Sheets連携
try:
    from tools.safe_sheets_wrapper import SafeSheetsWrapper
    from tools.sheets_manager import GoogleSheetsManager

    SHEETS_AVAILABLE = True
except ImportError:
    SHEETS_AVAILABLE = False
    logger.warning("⚠️ Sheets連携モジュールが利用できません")


class EpicTaskGenerator:
    """Epic→Story分解エンジン（JSON解析堅牢化版）"""

    def __init__(self, api_key: Optional[str] = None, knowledge_manager=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY が設定されていません")

        genai.configure(api_key=self.api_key)

        # max_tokens=32,000
        self.model = genai.GenerativeModel(
            "gemini-2.5-flash",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 32000,
            },
        )

        self.knowledge_manager = knowledge_manager

        logger.info("✅ EpicTaskGenerator 初期化完了")
        logger.info(f"   モデル: gemini-2.5-flash")
        logger.info(f"   max_tokens: 32,000")

    async def generate_epic_stories(
        self,
        epic_id: str,
        epic_description: str,
        num_stories: int = 10,
        target_lines_per_story: int = 1000,
        use_knowledge: bool = True,
    ) -> List[Dict[str, Any]]:
        """Epicから詳細Storyを生成"""
        logger.info(f"🚀 Epic {epic_id} のStory生成開始")
        logger.info(f"   目標: {num_stories}個のStory")

        # ナレッジ検索
        knowledge_context = ""
        if use_knowledge and self.knowledge_manager:
            try:
                search_results = await self._search_knowledge(epic_description)
                if search_results:
                    knowledge_context = self._format_knowledge_context(search_results)
                    logger.info(f"✅ {len(search_results)}件のナレッジを取得")
            except Exception as e:
                logger.warning(f"⚠️ ナレッジ検索エラー: {e}")

        # プロンプト作成
        prompt = self._create_epic_breakdown_prompt(
            epic_description=epic_description,
            num_stories=num_stories,
            target_lines=target_lines_per_story,
            knowledge_context=knowledge_context,
        )

        # API呼び出し
        try:
            response = await self._call_gemini_with_retry(prompt, max_retries=3)
            response_text = response.text

            logger.info(f"📥 Gemini APIレスポンス受信 ({len(response_text)}文字)")

            # JSON抽出（堅牢化版）
            stories = self._extract_json_from_response_robust(response_text)

            if not stories:
                raise ValueError("Storyが生成されませんでした")

            # parent_goal_idを設定
            for story in stories:
                story["parent_goal_id"] = epic_id

            logger.info(f"✅ {len(stories)}件のStoryを生成")

            # 文字数確認
            for i, story in enumerate(stories, 1):
                desc_len = len(story.get("description", ""))
                logger.info(f"   Story {i}: {desc_len}文字")
                if desc_len < 2000:
                    logger.warning(f"      ⚠️ 文字数が少ない（目標2,500-3,000）")

            return stories

        except Exception as e:
            logger.error(f"❌ Story生成エラー: {e}")
            import traceback

            traceback.print_exc()
            raise

    def _create_epic_breakdown_prompt(
        self,
        epic_description: str,
        num_stories: int,
        target_lines: int,
        knowledge_context: str = "",
    ) -> str:
        """Epic分解プロンプト（JSON構文エラー防止強化版）"""
        knowledge_section = ""
        if knowledge_context:
            knowledge_section = f"""
【参考情報】過去の成功事例・ナレッジ
{knowledge_context}
"""

        return f"""あなたは経験豊富なソフトウェアアーキテクトです。
以下のEpicを{num_stories}個の実行可能なStoryに分解してください。

【Epic】
{epic_description}

{knowledge_section}

【Story設計の原則】
1. 実行可能性: AIエージェントが自律的に実行できる
2. 具体性: 曖昧さゼロ、実装内容が完全に明確
3. 完結性: 各Storyが独立して完結できる

【各Storyに含める情報】（2,500-3,000文字）

1. **目的** (200文字)
2. **詳細な作業手順** (800文字)
3. **入力情報** (250文字)
4. **期待される成果物** (500文字)
5. **完了条件** (300文字)
6. **統合要件** (400文字)
7. **依存関係** (200文字)
8. **テスト要件** (400文字)
9. **サブタスク分解指針** (300文字)
10. **注意事項** (250文字)

【重要なJSON構文ルール】
⚠️ 以下の点に特に注意してください：

1. **ダブルクォートのエスケープ**
   - description内のダブルクォート（"）は必ず \\" にエスケープ
   - 例: "クラス名は \\"DataCollector\\" です"

2. **改行のエスケープ**
   - description内の改行は必ず \\n にエスケープ
   - 例: "目的\\n1. データ収集\\n2. 分析"

3. **バックスラッシュのエスケープ**
   - パス区切りなどは \\\\ にエスケープ
   - 例: "path\\\\to\\\\file.py"

4. **特殊文字の回避**
   - タブ文字、制御文字は使用しない
   - 単一引用符（'）を優先的に使用

5. **JSON配列の完全性**
   - 必ず [ で開始、] で終了
   - 各オブジェクトは {{ で開始、}} で終了
   - 最後のオブジェクト以外はカンマ（,）で区切る

【出力形式】
以下のJSON形式で出力してください（説明文・コードブロック一切不要）:

[
  {{
    "story_name": "ストーリー名（70文字以内・ダブルクォート不使用）",
    "description": "【目的】\\n...\\n\\n【詳細な作業手順】\\n...\\n\\n【入力情報】\\n...\\n\\n【期待される成果物】\\n...\\n\\n【完了条件】\\n...\\n\\n【統合要件】\\n...\\n\\n【依存関係】\\n...\\n\\n【テスト要件】\\n...\\n\\n【サブタスク分解指針】\\n...\\n\\n【注意事項】\\n...",
    "priority": "high",
    "estimated_time": "{target_lines}行: 2-4時間",
    "target_lines": {target_lines},
    "required_role": "autonomous_agent",
    "execution_type": "automated",
    "dependencies": "",
    "integration_ready": false
  }}
]

【JSON出力時の確認事項】
□ description内のダブルクォートはすべて \\" にエスケープ済み
□ 改行はすべて \\n にエスケープ済み
□ 配列は正しく閉じられている（]）
□ 最後のオブジェクトの後にカンマはない
□ すべての {{}} が対応している

それでは、{num_stories}個の実行可能な詳細StoryをJSON形式のみで出力してください（説明文・コードブロック不要）:
"""

    async def _search_knowledge(self, query: str) -> List[Dict]:
        """ナレッジベース検索"""
        if not self.knowledge_manager:
            return []

        try:
            if hasattr(self.knowledge_manager, "search_knowledge"):
                results = self.knowledge_manager.search_knowledge(query=query, top_k=5)
            elif hasattr(self.knowledge_manager, "search_async"):
                results = await self.knowledge_manager.search_async(query=query, top_k=5)
            else:
                return []
            return results if results else []
        except Exception as e:
            logger.warning(f"⚠️ ナレッジ検索エラー: {e}")
            return []

    def _format_knowledge_context(self, search_results: List[Dict]) -> str:
        """ナレッジ検索結果をプロンプト用に整形"""
        context = []
        for i, result in enumerate(search_results[:5], 1):
            title = result.get("title", "無題")
            content = result.get("content", "")[:400]
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
                await asyncio.sleep(2**attempt)
        raise Exception("Gemini API呼び出しに失敗しました")

    def _extract_json_from_response_robust(self, response_text: str) -> List[Dict[str, Any]]:
        """
        レスポンスからJSON抽出（堅牢化版）

        【修正内容】
        1. マークダウンブロック除去の強化
        2. 不正なエスケープシーケンスの修正
        3. 段階的パース試行
        """
        logger.info("🔍 JSON抽出開始（堅牢化版）...")

        # ステップ1: マークダウンコードブロック除去
        cleaned = re.sub(r"```json\s*", "", response_text)
        cleaned = re.sub(r"```\s*", "", cleaned)
        cleaned = cleaned.strip()

        # ステップ2: JSON配列の抽出
        match = re.search(r"\[\s*\{.*\}\s*\]", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(0)
            logger.info(f"✅ JSON配列を抽出 ({len(cleaned)}文字)")
        else:
            logger.warning("⚠️ JSON配列が見つかりませんでした。全文をパースします。")

        # ステップ3: 不正なエスケープシーケンスを修正
        # description内の不正なエスケープを検出・修正
        def fix_escapes(text):
            # \"\" の連続を \" に修正
            text = re.sub(r'\\"\\"+', r'\\"', text)
            # 不正な改行エスケープを修正
            text = re.sub(r"\\n\s*\\n", r"\\n", text)
            return text

        cleaned = fix_escapes(cleaned)

        # ステップ4: JSONパース試行
        try:
            stories = json.loads(cleaned)
            logger.info(f"✅ JSON解析成功 ({len(stories)}件のStory)")
            return stories
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON解析エラー: {e}")
            logger.error(f"エラー位置: 行{e.lineno} 列{e.colno}")

            # エラー箇所を表示
            lines = cleaned.split("\n")
            if e.lineno <= len(lines):
                error_line = lines[e.lineno - 1]
                logger.error(f"エラー行: {error_line}")

            # ステップ5: 部分的にパース試行
            logger.info("🔄 部分的パースを試行...")
            partial_stories = self._parse_partial_json(cleaned)
            if partial_stories:
                logger.info(f"✅ 部分的パース成功 ({len(partial_stories)}件のStory)")
                return partial_stories

            raise

    def _parse_partial_json(self, text: str) -> List[Dict[str, Any]]:
        """
        部分的JSON解析（フォールバック）

        完全なJSONがパースできない場合、個別のオブジェクトを抽出
        """
        stories = []

        # 各オブジェクトを個別に抽出
        pattern = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
        matches = re.finditer(pattern, text)

        for match in matches:
            obj_text = match.group(0)
            try:
                story = json.loads(obj_text)
                # 必須フィールドの確認
                if "story_name" in story and "description" in story:
                    stories.append(story)
            except json.JSONDecodeError:
                continue

        return stories


class PMAgentV33Epic:
    """PMAgent v33 Epic - 大規模コード生成対応"""

    def __init__(self, sheets_manager=None, knowledge_manager=None):
        self.sheets_manager = sheets_manager
        self.knowledge_manager = knowledge_manager
        self.epic_generator = EpicTaskGenerator(knowledge_manager=knowledge_manager)

        # SafeSheetsWrapper初期化
        if sheets_manager and SHEETS_AVAILABLE:
            self.sheets = SafeSheetsWrapper(sheets_manager)
            logger.info("✅ SafeSheetsWrapper 初期化完了")
        else:
            self.sheets = None

        logger.info("✅ PMAgentV33Epic 初期化完了")

    async def generate_epic_stories(
        self,
        epic_id: str,
        epic_description: str,
        num_stories: int = 10,
        target_lines_per_story: int = 1000,
        use_knowledge: bool = True,
    ) -> List[Dict[str, Any]]:
        """Epicからストーリーを生成"""
        return await self.epic_generator.generate_epic_stories(
            epic_id=epic_id,
            epic_description=epic_description,
            num_stories=num_stories,
            target_lines_per_story=target_lines_per_story,
            use_knowledge=use_knowledge,
        )

    def convert_to_pm_tasks_format(self, stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """StoryをPM_TASKSスキーマ形式に変換"""
        pm_tasks = []
        for story in stories:
            pm_task = {
                "description": story.get("description", ""),
                "required_role": story.get("required_role", "autonomous_agent"),
                "priority": story.get("priority", "medium"),
                "estimated_time": story.get("estimated_time", "未定"),
                "dependencies": story.get("dependencies", ""),
                "execution_type": story.get("execution_type", "automated"),
                "parent_goal_id": story.get("parent_goal_id", ""),
                "target_lines": story.get("target_lines", 1000),
            }
            pm_tasks.append(pm_task)
        return pm_tasks

    async def write_stories_to_sheet(self, stories: List[Dict[str, Any]]):
        """StoryをPM_TASKSに書き込み"""
        if not self.sheets:
            logger.error("❌ SafeSheetsWrapperが初期化されていません")
            return

        try:
            logger.info(f"📝 {len(stories)}個のStoryをpm_tasksに書き込み中...")

            # 既存タスクの最大ID取得
            existing_tasks_data = self.sheets.safe_read("pm_tasks!A:A")
            max_task_id = 0

            if existing_tasks_data:
                for row in existing_tasks_data[1:]:
                    if row and len(row) > 0:
                        try:
                            task_id_num = int(row[0])
                            if task_id_num > max_task_id:
                                max_task_id = task_id_num
                        except (ValueError, TypeError):
                            pass

            logger.info(f"✅ 既存タスクの最大ID: {max_task_id}")
            next_task_id = max_task_id + 1

            # 各Story書き込み
            for i, story in enumerate(stories, 1):
                task_id = str(next_task_id)
                parent_goal_id = str(story.get("parent_goal_id", ""))

                task_row = [
                    task_id,
                    parent_goal_id,
                    story.get("description", ""),
                    story.get("required_role", "autonomous_agent"),
                    "pending",
                    story.get("priority", "medium"),
                    story.get("estimated_time", "未定"),
                    story.get("dependencies", ""),
                    "",  # created_at
                    "",  # batch_id
                    "",  # detail_file_path
                    "",  # blank
                    story.get("execution_type", "automated"),
                ]

                success = self.sheets.safe_append("pm_tasks", [task_row])

                if success:
                    logger.info(f"  ✅ Story {i}/{len(stories)} 書き込み完了（ID: {task_id}）")
                    next_task_id += 1
                else:
                    logger.warning(f"  ⚠️ Story {i}/{len(stories)} 書き込み失敗")

            logger.info(f"✅ {len(stories)}個のStory書き込み完了")

        except Exception as e:
            logger.error(f"❌ Story書き込みエラー: {e}")
            import traceback

            traceback.print_exc()


# テスト用
async def test_pm_agent_v33():
    """Phase 1 テスト実行"""
    print("=" * 60)
    print("Phase 1: PMAgent v33 Epic テスト実行（JSON修正版）")
    print("=" * 60)
    print()

    test_epic = """
【Epic】AIデューデリジェンスエージェント開発

【概要】
企業のデューデリジェンスプロセスを自動化するAIエージェントシステム。
財務分析、リスク評価、市場調査、法務チェックを自動実行し、
包括的なデューデリジェンスレポートを生成する。

【目標コード規模】約10,000行

【主要機能】
- データ収集モジュール (2,000行)
- リスク評価エンジン (1,500行)
- 財務分析モジュール (1,500行)
- レポート生成システム (1,500行)
- API統合レイヤー (1,000行)
- テストスイート (2,500行)

【技術スタック】
- Python 3.10+
- FastAPI
- PostgreSQL
- Redis
"""

    try:
        # Sheets初期化
        sheets_manager = None
        if SHEETS_AVAILABLE:
            try:
                sheets_manager = GoogleSheetsManager()
                print("✅ GoogleSheetsManager 初期化成功")
            except Exception as e:
                print(f"⚠️ GoogleSheetsManager 初期化失敗: {e}")

        agent = PMAgentV33Epic(sheets_manager=sheets_manager)
        print()

        print("🚀 Story生成中...")
        print()
        stories = await agent.generate_epic_stories(
            epic_id="epic_dd_001",
            epic_description=test_epic,
            num_stories=10,
            target_lines_per_story=1000,
            use_knowledge=False,
        )

        print()
        print(f"✅ Story生成成功! ({len(stories)}件)")
        print()
        print("【生成されたStory】")
        print()

        total_chars = 0
        for i, story in enumerate(stories, 1):
            desc = story.get("description", "")
            desc_len = len(desc)
            total_chars += desc_len

            print(f"{i}. {story.get('story_name', 'NO NAME')}")
            print(f"   文字数: {desc_len}文字 {'✅' if desc_len >= 2500 else '⚠️'}")
            print(f"   目標行数: {story.get('target_lines', 0)}行")
            print()

        avg_chars = total_chars / len(stories) if stories else 0
        print("【統計】")
        print(f"平均文字数: {avg_chars:.0f}文字 {'✅' if avg_chars >= 2500 else '⚠️'}")
        print(f"合計文字数: {total_chars}文字")
        print()

        # Sheets書き込み
        if sheets_manager:
            print("=" * 60)
            print("📝 Google Sheetsに保存中...")
            await agent.write_stories_to_sheet(stories)
            print("✅ Google Sheets保存完了!")

        print()
        print("=" * 60)
        print("Phase 1 テスト完了")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    import asyncio

    sys.exit(asyncio.run(test_pm_agent_v33()))
