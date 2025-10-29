#!/usr/bin/env python3
"""
run_pm_tasks_adaptive.py - 統合版タスク実行システム（修正版）

Phase 1-8の全コンポーネントを統合した、完全自動化タスク実行システム。
"""
import asyncio
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# プロジェクトルート設定
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# 基盤コンポーネント
from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import get_config

# Phase 7: 自己修復システム
try:
    from agents.self_healing.retry_manager import RetryManager
    from agents.self_healing.utils.error_classifier import ErrorClassifier

    PHASE7_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Phase 7コンポーネント利用不可: {e}")
    PHASE7_AVAILABLE = False

# Phase 8: ナレッジベース & 自己学習
try:
    from agents.self_healing.logging import KnowledgeBaseManager, ContextLogger, DecisionContext, SelfLearningPipeline

    PHASE8_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Phase 8コンポーネント利用不可: {e}")
    PHASE8_AVAILABLE = False


class IntegratedTaskExecutor:
    """統合タスク実行システム"""

    def __init__(self):
        """初期化"""
        self.sheets_manager = None
        self.retry_manager = None
        self.error_classifier = None
        self.kb_manager = None
        self.context_logger = None
        self.learning_pipeline = None

        print("=" * 70)
        print("🚀 統合タスク実行システム初期化")
        print("=" * 70)
        print()

    async def initialize(self):
        """全コンポーネントの初期化"""
        try:
            print("📊 Phase 1-6: 基盤システム初期化")
            print("-" * 70)

            # GoogleSheetsManager初期化
            spreadsheet_id = get_config("SPREADSHEET_ID")
            service_account_file = get_config("SERVICE_ACCOUNT_FILE")

            self.sheets_manager = GoogleSheetsManager(
                spreadsheet_id=spreadsheet_id, service_account_file=service_account_file
            )
            print("✅ GoogleSheetsManager初期化完了")

            # Phase 7初期化
            if PHASE7_AVAILABLE:
                print()
                print("🛡️ Phase 7: 自己修復システム初期化")
                print("-" * 70)

                try:
                    # RetryManager初期化（引数なしで初期化）
                    self.retry_manager = RetryManager(sheets_manager=self.sheets_manager)
                    print("✅ RetryManager初期化完了")
                except Exception as e:
                    print(f"⚠️ RetryManager初期化失敗: {e}")
                    print("   → デフォルト設定で続行")

                try:
                    # ErrorClassifier初期化
                    self.error_classifier = ErrorClassifier()
                    print("✅ ErrorClassifier初期化完了")
                except Exception as e:
                    print(f"⚠️ ErrorClassifier初期化失敗: {e}")
            else:
                print()
                print("⚠️ Phase 7: コンポーネント利用不可（スキップ）")

            # Phase 8初期化
            if PHASE8_AVAILABLE:
                print()
                print("🧠 Phase 8: ナレッジベース & 自己学習初期化")
                print("-" * 70)

                try:
                    # KnowledgeBaseManager初期化
                    self.kb_manager = KnowledgeBaseManager(self.sheets_manager)
                    print("✅ KnowledgeBaseManager初期化完了")
                except Exception as e:
                    print(f"⚠️ KnowledgeBaseManager初期化失敗: {e}")

                try:
                    # ContextLogger初期化
                    self.context_logger = ContextLogger(self.sheets_manager)
                    print("✅ ContextLogger初期化完了")
                except Exception as e:
                    print(f"⚠️ ContextLogger初期化失敗: {e}")

                try:
                    # SelfLearningPipeline初期化
                    self.learning_pipeline = SelfLearningPipeline(self.sheets_manager)
                    print("✅ SelfLearningPipeline初期化完了")
                except Exception as e:
                    print(f"⚠️ SelfLearningPipeline初期化失敗: {e}")
                    self.learning_pipeline = None
            else:
                print()
                print("⚠️ Phase 8: コンポーネント利用不可（スキップ）")

            print()
            print("=" * 70)
            print("✅ 初期化完了（利用可能なコンポーネントのみ）")
            print("=" * 70)
            print()

            return True

        except Exception as e:
            print(f"❌ 初期化エラー: {e}")
            import traceback

            traceback.print_exc()
            return False

    async def load_tasks(self, limit: int = None) -> List[Dict[str, Any]]:
        """タスクを読み込み"""
        try:
            print("📋 タスク読み込み中...")

            tasks = await self.sheets_manager.load_tasks_from_sheet("pm_tasks")

            # ステータスが'pending'のタスクのみ
            pending_tasks = [task for task in tasks if task.get("status") == "pending"]

            if limit:
                pending_tasks = pending_tasks[:limit]

            print(f"✅ {len(pending_tasks)}件のタスクを読み込みました")

            return pending_tasks

        except Exception as e:
            print(f"❌ タスク読み込みエラー: {e}")
            return []

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """タスクを実行"""
        task_id = task.get("task_id", "unknown")

        print()
        print("=" * 70)
        print(f"🎯 タスク実行開始: {task_id}")
        print("=" * 70)

        try:
            # TODO: 実際のタスク実行ロジックを実装
            # 現在はモック
            result = {
                "task_id": task_id,
                "status": "completed",
                "message": "タスク実行成功（モック）",
                "quality_score": 8.5,
            }

            print(f"✅ タスク {task_id} 完了")

            return result

        except Exception as e:
            print(f"❌ タスク {task_id} エラー: {e}")

            # エラー分類
            if self.error_classifier:
                error_class = self.error_classifier.classify(e)
                print(f"   エラー分類: {error_class}")
            else:
                error_class = "UnknownError"

            # コンテキスト記録
            if self.context_logger:
                await self._log_error_context(task, e, error_class)

            # 類似ケース検索
            if self.kb_manager:
                similar_cases = self.kb_manager.search_similar_knowledge(
                    {"error_type": error_class, "task_type": task.get("type", "unknown")}, limit=3
                )

                if similar_cases:
                    print(f"   💡 類似ケース発見: {len(similar_cases)}件")
                    print(f"      → {similar_cases[0].get('pattern_description', 'N/A')}")

            return {"task_id": task_id, "status": "failed", "error": str(e)}

    async def _log_error_context(self, task: Dict, error: Exception, error_class: str):
        """エラーコンテキストを記録"""
        try:
            context = DecisionContext(
                task_id=str(task.get("task_id", "unknown")),
                error_type=error_class,
                error_message=str(error),
                modification_reason=f"{error_class}エラーが発生",
                decision_process="エラー分類 → 類似ケース検索 → 対応",
                modification_purpose="タスクの成功",
                expected_result="エラー解決",
            )

            context.add_learning_tag(error_class)
            context.add_learning_tag("auto_recovery")

            await self.context_logger.log_decision(context)

        except Exception as e:
            print(f"⚠️ コンテキスト記録エラー: {e}")

    async def run_learning_cycle(self):
        """学習サイクルを実行"""
        if not self.learning_pipeline:
            print()
            print("⚠️ SelfLearningPipelineが利用不可のため学習サイクルをスキップ")
            return

        print()
        print("=" * 70)
        print("🧠 自己学習サイクル実行")
        print("=" * 70)

        try:
            result = await self.learning_pipeline.run_learning_cycle()

            if result["success"]:
                print(f"✅ 学習サイクル完了")
                print(f"   抽出: {result['patterns_found']}件")
                print(f"   保存: {result['patterns_saved']}件")
            else:
                print(f"❌ 学習サイクル失敗: {result.get('error', 'Unknown')}")
        except Exception as e:
            print(f"❌ 学習サイクルエラー: {e}")

    async def run(self, max_tasks: int = None, run_learning: bool = True):
        """メイン実行"""
        print()
        print("=" * 70)
        print("�� 統合タスク実行システム開始")
        print("=" * 70)
        print(f"⏰ 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # 初期化
        if not await self.initialize():
            print("❌ 初期化失敗")
            return

        # タスク読み込み
        tasks = await self.load_tasks(limit=max_tasks)

        if not tasks:
            print("⚠️ 実行可能なタスクがありません")

            if run_learning:
                await self.run_learning_cycle()

            return

        # タスク実行
        print()
        print("=" * 70)
        print(f"📊 {len(tasks)}件のタスクを実行します")
        print("=" * 70)

        results = []
        for i, task in enumerate(tasks, 1):
            print(f"\n[{i}/{len(tasks)}]")
            result = await self.execute_task(task)
            results.append(result)

        # 結果サマリー
        print()
        print("=" * 70)
        print("📊 実行結果サマリー")
        print("=" * 70)

        completed = sum(1 for r in results if r["status"] == "completed")
        failed = len(results) - completed

        print(f"✅ 成功: {completed}件")
        print(f"❌ 失敗: {failed}件")
        print(f"📈 成功率: {completed/len(results)*100:.1f}%")

        # 学習サイクル実行
        if run_learning:
            await self.run_learning_cycle()

        print()
        print("=" * 70)
        print("✅ 統合タスク実行システム完了")
        print("=" * 70)
        print(f"⏰ 終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


async def main():
    """メインエントリポイント"""
    parser = argparse.ArgumentParser(description="統合タスク実行システム（Phase 1-8完全統合版）")
    parser.add_argument("--max-tasks", type=int, default=None, help="実行するタスクの最大数（デフォルト: 全て）")
    parser.add_argument("--no-learning", action="store_true", help="学習サイクルをスキップ")
    parser.add_argument("--learning-only", action="store_true", help="学習サイクルのみ実行（タスク実行なし）")

    args = parser.parse_args()

    executor = IntegratedTaskExecutor()

    if args.learning_only:
        # 学習サイクルのみ
        if await executor.initialize():
            await executor.run_learning_cycle()
    else:
        # 通常実行
        await executor.run(max_tasks=args.max_tasks, run_learning=not args.no_learning)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによる中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 致命的エラー: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
