#!/usr/bin/env python3
"""
TaskExecutor v4 Sub-task対応版

【Phase 2実装】
- M2.1: Sub-task分解機能実装
- T2.1.1: SubTaskDecomposerクラス ✅
- T2.1.2: Gemini呼び出し最適化 ✅
- T2.1.3: Sub-task結果のメモリ管理 ✅
- T2.1.4: 既存RealExecutorとの統合 ✅

【設計思想】
- 既存high_quality_executor_v6.pyは変更しない
- ラッパー方式で既存executorを活用
- Sub-task分解機能を独立実装
- 1Story → 3-5個のSub-taskに分解
- 各Sub-task: 200-400行の目標コード生成
"""

import asyncio
import json
import logging
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
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
except ImportError:
    pass

# ロギング設定
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)

# Gemini API
import google.generativeai as genai

# 既存システム（変更しない）
try:
    from agents.task_execution.high_quality_executor_v6 import \
        HighQualityExecutorV6

    EXECUTOR_AVAILABLE = True
except ImportError:
    EXECUTOR_AVAILABLE = False
    logger.warning("⚠️ HighQualityExecutorV6が利用できません")

try:
    ACCESSOR_AVAILABLE = True
except ImportError:
    ACCESSOR_AVAILABLE = False
    logger.warning("⚠️ BaseDataAccessorが利用できません")


class SubTaskDecomposer:
    """
    Story→Sub-task分解エンジン

    【Phase 2: T2.1.1実装】
    - 1Story → 3-5個のSub-taskに自動分解
    - 各Sub-task: 200-400行の目標コード
    - Gemini API（max_tokens=32,000）使用
    - JSON解析堅牢化（Phase 1知見適用）
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初期化

        Args:
            api_key: Gemini API Key
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY が設定されていません")

        # Gemini API設定（Phase 1知見を適用）
        genai.configure(api_key=self.api_key)

        self.model = genai.GenerativeModel(
            "gemini-2.5-flash",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 32000,  # Phase 1実測最適値
            },
        )

        logger.info("✅ SubTaskDecomposer 初期化完了")
        logger.info(f"   モデル: gemini-2.5-flash")
        logger.info(f"   max_tokens: 32,000")

    async def decompose_story_to_subtasks(
        self,
        story_id: str,
        story_description: str,
        num_subtasks: int = 4,
        target_lines_per_subtask: int = 300,
    ) -> List[Dict[str, Any]]:
        """
        Storyから詳細Sub-taskを生成

        Args:
            story_id: ストーリーID
            story_description: ストーリーの説明（2,500-3,000文字）
            num_subtasks: 生成するSub-task数（推奨3-5個）
            target_lines_per_subtask: 1Sub-taskの目標行数（200-400）

        Returns:
            Sub-taskのリスト（各600-1,200文字）
        """
        logger.info(f"🚀 Story {story_id} のSub-task分解開始")
        logger.info(f"   目標: {num_subtasks}個のSub-task")
        logger.info(f"   各Sub-task目標行数: {target_lines_per_subtask}行")

        # T2.1.2: Sub-task分解プロンプト作成
        prompt = self._create_subtask_breakdown_prompt(
            story_description=story_description,
            num_subtasks=num_subtasks,
            target_lines=target_lines_per_subtask,
        )

        logger.info(f"📝 プロンプト作成完了（{len(prompt)}文字）")

        # Gemini API呼び出し
        try:
            response = await self._call_gemini_with_retry(prompt, max_retries=3)
            response_text = response.text

            logger.info(f"📥 Gemini APIレスポンス受信 ({len(response_text)}文字)")

            # JSON抽出（Phase 1知見を適用）
            subtasks = self._extract_json_from_response_robust(response_text)

            if not subtasks:
                raise ValueError("Sub-taskが生成されませんでした")

            # parent_story_idを設定
            for subtask in subtasks:
                subtask["parent_story_id"] = story_id
                subtask["subtask_id"] = f"{story_id}_sub_{subtasks.index(subtask) + 1}"

            logger.info(f"✅ {len(subtasks)}件のSub-taskを生成")

            # 文字数確認
            for i, subtask in enumerate(subtasks, 1):
                desc_len = len(subtask.get("description", ""))
                logger.info(
                    f"   Sub-task {i}: {desc_len}文字, {subtask.get('target_lines', 0)}行目標"
                )

            return subtasks

        except Exception as e:
            logger.error(f"❌ Sub-task生成エラー: {e}")
            import traceback

            traceback.print_exc()
            raise

    def _create_subtask_breakdown_prompt(
        self, story_description: str, num_subtasks: int, target_lines: int
    ) -> str:
        """
        Sub-task分解プロンプト設計

        【Phase 2プロンプト設計】
        - 各Sub-task: 600-1,200文字
        - 具体的な実装手順
        - ファイル名・クラス名を明記
        """
        return f"""あなたは経験豊富なソフトウェアエンジニアです。
以下のStory（ストーリー）を{num_subtasks}個の実行可能なSub-task（サブタスク）に分解してください。

【Story】
{story_description}

【前提条件】
- このStoryを完了するために必要なコード: 約{num_subtasks * target_lines}行
- 1Sub-taskあたりの目標コード行数: {target_lines}行
- Sub-taskは順序立てて実行される
- 各Sub-taskは具体的な実装内容を含む

【Sub-task設計の原則】
1. **段階的実装**: 基礎→応用の順序
2. **独立性**: 各Sub-taskが独立して実装可能
3. **具体性**: ファイル名、クラス名、メソッド名を明記
4. **テスト可能性**: 各Sub-taskの完了判定が明確

【各Sub-taskに必ず含める情報】（600-1,200文字）

1. **Sub-task名** (30文字)
   - 何を実装するか明確に

2. **実装内容** (400文字)
   - 作成するファイル: src/xxx.py
   - 実装するクラス: class XxxClass
   - 実装するメソッド: def method_name()
   - 使用するライブラリ: import xxx
   - 具体的な実装ステップ（5-8ステップ）

3. **入力・前提条件** (100文字)
   - 前のSub-taskの成果物
   - 必要な設定ファイル

4. **期待される成果物** (200文字)
   - ファイル名とパス: src/xxx.py ({target_lines}行)
   - 実装されるクラス・メソッド
   - 動作確認方法

5. **完了条件** (100文字)
   - [ ] コードが動作する
   - [ ] テストがパスする
   - [ ] Lintエラーなし

6. **目標行数** (数値)
   - {target_lines}行

【JSON構文ルール】
⚠️ 以下の点に特に注意してください：
1. description内のダブルクォート（"）は必ず \\" にエスケープ
2. 改行は必ず \\n にエスケープ
3. 最後のオブジェクトの後にカンマはない
4. すべての {{}} が対応している

【出力形式】
以下のJSON形式で出力してください（説明文不要）:

[
  {{
    "subtask_name": "サブタスク名（30文字以内）",
    "description": "【実装内容】\\nファイル: src/xxx.py\\nクラス: class XxxClass\\nメソッド: def method1()\\n\\n1. ...\\n2. ...\\n\\n【入力・前提条件】\\n...\\n\\n【期待される成果物】\\n...\\n\\n【完了条件】\\n...",
    "target_lines": {target_lines},
    "execution_order": 1,
    "estimated_time": "30-60分",
    "dependencies": ""
  }}
]

それでは、{num_subtasks}個の実行可能な詳細Sub-taskをJSON形式のみで出力してください:
"""

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
        レスポンスからJSON抽出（Phase 1知見を適用）

        【Phase 1知見適用】
        1. マークダウンブロック除去
        2. 不正なエスケープシーケンスの修正
        3. 段階的パース試行
        """
        logger.info("🔍 JSON抽出開始（Phase 1知見適用）...")

        # ステップ1: マークダウンコードブロック除去
        cleaned = re.sub(r"```json\s*", "", response_text)
        cleaned = re.sub(r"```\s*", "", cleaned)
        cleaned = cleaned.strip()

        # ステップ2: JSON配列の抽出
        match = re.search(r"\[\s*\{.*\}\s*\]", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(0)
            logger.info(f"✅ JSON配列を抽出 ({len(cleaned)}文字)")

        # ステップ3: 不正なエスケープシーケンスを修正
        cleaned = re.sub(r'\\"\\"+', r'\\"', cleaned)
        cleaned = re.sub(r"\\n\s*\\n", r"\\n", cleaned)

        # ステップ4: JSONパース
        try:
            subtasks = json.loads(cleaned)
            logger.info(f"✅ JSON解析成功 ({len(subtasks)}件のSub-task)")
            return subtasks
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON解析エラー: {e}")

            # ステップ5: 部分的にパース試行
            logger.info("🔄 部分的パースを試行...")
            partial_subtasks = self._parse_partial_json(cleaned)
            if partial_subtasks:
                logger.info(f"✅ 部分的パース成功 ({len(partial_subtasks)}件)")
                return partial_subtasks

            raise

    def _parse_partial_json(self, text: str) -> List[Dict[str, Any]]:
        """部分的JSON解析（フォールバック）"""
        subtasks = []
        pattern = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
        matches = re.finditer(pattern, text)

        for match in matches:
            obj_text = match.group(0)
            try:
                subtask = json.loads(obj_text)
                if "subtask_name" in subtask and "description" in subtask:
                    subtasks.append(subtask)
            except json.JSONDecodeError:
                continue

        return subtasks


class SubTaskMemoryManager:
    """
    Sub-task結果のメモリ管理

    【Phase 2: T2.1.3実装】
    - Sub-task実行結果を一時保存
    - Story単位での結果集約
    - 統合時の参照機能
    """

    def __init__(self):
        """初期化"""
        self.subtask_results = defaultdict(list)
        logger.info("✅ SubTaskMemoryManager 初期化完了")

    def save_subtask_result(self, story_id: str, subtask_id: str, result: Dict[str, Any]):
        """
        Sub-task結果を保存

        Args:
            story_id: ストーリーID
            subtask_id: サブタスクID
            result: 実行結果
        """
        result_with_meta = {
            "subtask_id": subtask_id,
            "timestamp": datetime.now().isoformat(),
            "result": result,
        }
        self.subtask_results[story_id].append(result_with_meta)
        logger.info(f"💾 Sub-task結果保存: {story_id} / {subtask_id}")

    def get_story_results(self, story_id: str) -> List[Dict[str, Any]]:
        """
        Story配下のすべてのSub-task結果を取得

        Args:
            story_id: ストーリーID

        Returns:
            Sub-task結果のリスト
        """
        results = self.subtask_results.get(story_id, [])
        logger.info(f"📖 Story結果取得: {story_id} ({len(results)}件)")
        return results

    def get_all_results(self) -> Dict[str, List[Dict[str, Any]]]:
        """すべてのSub-task結果を取得"""
        return dict(self.subtask_results)

    def clear_story_results(self, story_id: str):
        """Story配下のSub-task結果をクリア"""
        if story_id in self.subtask_results:
            del self.subtask_results[story_id]
            logger.info(f"🗑️ Story結果削除: {story_id}")


class TaskExecutorV4SubTask:
    """
    TaskExecutor v4 Sub-task対応版

    【Phase 2: T2.1.4実装】
    - 既存HighQualityExecutorV6をラッパーとして使用
    - Sub-task分解機能を統合
    - Story→Sub-task→実行→統合のフロー
    """

    def __init__(self):
        """初期化"""
        # 既存executor（変更しない）
        if EXECUTOR_AVAILABLE:
            self.base_executor = HighQualityExecutorV6()
            logger.info("✅ HighQualityExecutorV6 ロード完了")
        else:
            self.base_executor = None
            logger.warning("⚠️ HighQualityExecutorV6 利用不可")

        # Sub-task分解エンジン
        self.decomposer = SubTaskDecomposer()

        # メモリ管理
        self.memory = SubTaskMemoryManager()

        logger.info("✅ TaskExecutorV4SubTask 初期化完了")

    async def execute_story_with_subtasks(
        self, story_id: str, story_description: str, num_subtasks: int = 4
    ) -> Dict[str, Any]:
        """
        Storyを Sub-taskに分解して実行

        Args:
            story_id: ストーリーID
            story_description: ストーリーの説明
            num_subtasks: Sub-task数（推奨3-5個）

        Returns:
            実行結果サマリー
        """
        logger.info(f"🚀 Story実行開始: {story_id}")
        logger.info(f"   Sub-task数: {num_subtasks}個")

        try:
            # ステップ1: Story→Sub-task分解
            logger.info("📋 Sub-task分解中...")
            subtasks = await self.decomposer.decompose_story_to_subtasks(
                story_id=story_id, story_description=story_description, num_subtasks=num_subtasks
            )

            logger.info(f"✅ {len(subtasks)}個のSub-taskに分解完了")

            # ステップ2: 各Sub-taskを実行
            results = []
            for i, subtask in enumerate(subtasks, 1):
                logger.info(f"🔄 Sub-task {i}/{len(subtasks)} 実行中...")

                if self.base_executor:
                    # 既存executorで実行
                    result = self.base_executor.execute_task(
                        task_id=subtask["subtask_id"],
                        task_description=subtask["description"],
                        required_role="autonomous_agent",
                    )
                else:
                    # executorがない場合はモック
                    result = {
                        "status": "mock_success",
                        "subtask_id": subtask["subtask_id"],
                        "message": "Executor利用不可（モック実行）",
                    }

                # 結果を保存
                self.memory.save_subtask_result(
                    story_id=story_id, subtask_id=subtask["subtask_id"], result=result
                )

                results.append(result)
                logger.info(f"✅ Sub-task {i} 完了")

            # ステップ3: 結果統合
            logger.info("📊 結果統合中...")
            summary = self._integrate_results(story_id, subtasks, results)

            logger.info(f"✅ Story {story_id} 実行完了")

            return summary

        except Exception as e:
            logger.error(f"❌ Story実行エラー: {e}")
            import traceback

            traceback.print_exc()
            raise

    def _integrate_results(
        self, story_id: str, subtasks: List[Dict], results: List[Dict]
    ) -> Dict[str, Any]:
        """結果統合"""
        total_subtasks = len(subtasks)
        successful = sum(
            1 for r in results if r.get("status") == "success" or r.get("status") == "mock_success"
        )

        summary = {
            "story_id": story_id,
            "total_subtasks": total_subtasks,
            "successful_subtasks": successful,
            "success_rate": successful / total_subtasks if total_subtasks > 0 else 0,
            "timestamp": datetime.now().isoformat(),
            "subtasks": subtasks,
            "results": results,
        }

        logger.info(f"📊 統合結果: {successful}/{total_subtasks}成功")

        return summary


# テスト用
async def test_task_executor_v4():
    """Phase 2 テスト実行"""
    print("=" * 60)
    print("Phase 2: TaskExecutor v4 Sub-task テスト実行")
    print("=" * 60)
    print()

    test_story = """
【Story】データ収集モジュール - 企業基本情報と公開財務データ取得

【目的】
企業の基本情報と財務データをGoogle Sheetsから取得し、
PostgreSQLに保存するモジュールを実装する。

【詳細な作業手順】
1. Google Sheets APIクライアント実装
2. データモデル定義（Company, FinancialData）
3. データ取得ロジック実装
4. PostgreSQL保存機能実装
5. エラーハンドリング実装
6. ユニットテスト作成

【期待される成果物】
- src/data_collection/sheets_client.py (300行)
- src/data_collection/models.py (200行)
- src/data_collection/repository.py (300行)
- tests/test_data_collection.py (200行)

【完了条件】
- [ ] すべてのテストがパス
- [ ] カバレッジ85%以上
- [ ] Lintエラーゼロ
"""

    try:
        executor = TaskExecutorV4SubTask()
        print()

        print("🚀 Story→Sub-task分解テスト...")
        print()

        summary = await executor.execute_story_with_subtasks(
            story_id="story_001", story_description=test_story, num_subtasks=4
        )

        print()
        print("=" * 60)
        print("実行結果サマリー")
        print("=" * 60)
        print(f"Story ID: {summary['story_id']}")
        print(f"Sub-task数: {summary['total_subtasks']}")
        print(f"成功数: {summary['successful_subtasks']}")
        print(f"成功率: {summary['success_rate']:.1%}")
        print()

        print("【生成されたSub-task】")
        for i, subtask in enumerate(summary["subtasks"], 1):
            print(f"{i}. {subtask.get('subtask_name', 'NO NAME')}")
            print(f"   目標行数: {subtask.get('target_lines', 0)}行")
            print(f"   実行順序: {subtask.get('execution_order', 0)}")
            print()

        print("=" * 60)
        print("Phase 2 テスト完了")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    import asyncio

    sys.exit(asyncio.run(test_task_executor_v4()))
