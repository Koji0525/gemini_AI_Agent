#!/usr/bin/env python3
"""
ProgressAnalyzer v2 - 進捗可視化＆ギャップ分析（修正版）

【Phase 3: M3.1実装】
- F11: 進捗可視化＆ギャップ分析
- KeyError修正: すべての返り値で統一されたキーを保証
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# プロジェクトルート設定
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# ロギング設定
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)

# 既存システム（読み取り専用）
try:
    from tools.base_data_accessor import BaseDataAccessor

    ACCESSOR_AVAILABLE = True
except ImportError:
    ACCESSOR_AVAILABLE = False
    logger.warning("⚠️ BaseDataAccessorが利用できません")


class ProgressAnalyzer:
    """進捗可視化＆ギャップ分析エンジン"""

    def __init__(self):
        """初期化"""
        if ACCESSOR_AVAILABLE:
            self.accessor = BaseDataAccessor()
            logger.info("✅ BaseDataAccessor ロード完了")
        else:
            self.accessor = None
            logger.warning("⚠️ BaseDataAccessor 利用不可")

        logger.info("✅ ProgressAnalyzer 初期化完了")

    def analyze_story_progress(self, story_id: str) -> Dict[str, Any]:
        """
        Story完了度を計算

        【修正内容】
        - すべての返り値で統一されたキーを保証
        - integration_ready を必ず含める
        - failed_subtasks を必ず含める
        """
        logger.info(f"📊 Story進捗分析開始: {story_id}")

        try:
            # Sub-task一覧を取得
            subtasks = self._get_story_subtasks(story_id)

            # Sub-taskが見つからない場合（修正: すべてのキーを含める）
            if not subtasks:
                logger.warning(f"⚠️ Story {story_id} のSub-taskが見つかりません")
                return {
                    "story_id": story_id,
                    "completion_rate": 0.0,
                    "total_subtasks": 0,
                    "completed_subtasks": 0,
                    "pending_subtasks": 0,
                    "failed_subtasks": 0,  # ★追加
                    "integration_ready": False,  # ★追加
                    "status": "no_subtasks",
                    "timestamp": datetime.now().isoformat(),
                    "subtasks": [],  # ★追加
                }

            # 完了度を計算
            total = len(subtasks)
            completed = sum(1 for st in subtasks if st.get("status") in ["completed", "success"])
            pending = sum(1 for st in subtasks if st.get("status") == "pending")
            failed = sum(1 for st in subtasks if st.get("status") == "failed")

            completion_rate = completed / total if total > 0 else 0.0

            # 統合準備状況を判定
            integration_ready = completion_rate >= 0.8  # 80%以上で統合可能

            result = {
                "story_id": story_id,
                "completion_rate": completion_rate,
                "total_subtasks": total,
                "completed_subtasks": completed,
                "pending_subtasks": pending,
                "failed_subtasks": failed,
                "integration_ready": integration_ready,
                "status": self._determine_status(completion_rate),
                "timestamp": datetime.now().isoformat(),
                "subtasks": subtasks,
            }

            logger.info(f"✅ 完了度: {completion_rate:.1%} ({completed}/{total})")
            logger.info(f"   統合準備: {'✅ 可能' if integration_ready else '⏳ 未完'}")

            return result

        except Exception as e:
            logger.error(f"❌ 進捗分析エラー: {e}")
            import traceback

            traceback.print_exc()
            raise

    def detect_missing_subtasks(self, story: Dict[str, Any]) -> List[Dict[str, Any]]:
        """不足Sub-taskを検出"""
        logger.info(f"🔍 不足Sub-task検出: {story.get('story_id', 'unknown')}")

        missing_subtasks = []

        try:
            # Storyの目標行数を取得
            target_lines = story.get("target_lines", 1000)

            # 既存Sub-taskの合計行数を計算
            existing_subtasks = self._get_story_subtasks(story.get("story_id", ""))
            total_existing_lines = sum(st.get("target_lines", 0) for st in existing_subtasks)

            # 不足行数を計算
            missing_lines = target_lines - total_existing_lines

            if missing_lines > 200:  # 200行以上不足している場合
                # 不足Sub-taskを提案
                num_missing = (missing_lines + 299) // 300  # 300行単位で切り上げ

                for i in range(num_missing):
                    missing_subtask = {
                        "subtask_name": f"追加Sub-task {i+1}",
                        "description": f"不足機能の実装（推定{min(300, missing_lines - i*300)}行）",
                        "target_lines": min(300, missing_lines - i * 300),
                        "status": "missing",
                        "reason": f"目標{target_lines}行に対して{missing_lines}行不足",
                    }
                    missing_subtasks.append(missing_subtask)

                logger.info(f"⚠️ {len(missing_subtasks)}個の不足Sub-taskを検出")
            else:
                logger.info(f"✅ Sub-taskは十分です（不足: {missing_lines}行）")

            return missing_subtasks

        except Exception as e:
            logger.error(f"❌ 不足Sub-task検出エラー: {e}")
            return []

    def get_integration_readiness(self, story_id: str) -> Dict[str, Any]:
        """統合準備状況を判定"""
        logger.info(f"🔍 統合準備状況確認: {story_id}")

        try:
            # 進捗分析
            progress = self.analyze_story_progress(story_id)

            # 統合可能条件のチェック
            checks = {
                "completion_rate_ok": progress["completion_rate"] >= 0.8,
                "no_failed_subtasks": progress["failed_subtasks"] == 0,
                "all_tests_passed": self._check_tests_passed(story_id),
                "no_lint_errors": self._check_lint_status(story_id),
            }

            # 総合判定
            all_ready = all(checks.values())

            readiness = {
                "story_id": story_id,
                "ready_for_integration": all_ready,
                "checks": checks,
                "progress": progress,
                "recommendation": self._get_recommendation(checks),
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"   統合準備: {'✅ 完了' if all_ready else '⏳ 未完'}")

            return readiness

        except Exception as e:
            logger.error(f"❌ 統合準備状況確認エラー: {e}")
            raise

    def _get_story_subtasks(self, story_id: str) -> List[Dict[str, Any]]:
        """Story配下のSub-taskを取得（既存システムから）"""
        if not self.accessor:
            return []

        try:
            # pm_tasksからSub-taskを取得
            tasks = self.accessor.read_sheet_as_dicts(
                "pm_tasks",
                filter_func=lambda t: str(t.get("parent_goal_id", "")).startswith(story_id),
            )
            return tasks
        except Exception as e:
            logger.warning(f"⚠️ Sub-task取得エラー: {e}")
            return []

    def _determine_status(self, completion_rate: float) -> str:
        """完了度から状態を判定"""
        if completion_rate >= 1.0:
            return "completed"
        elif completion_rate >= 0.8:
            return "almost_done"
        elif completion_rate >= 0.5:
            return "in_progress"
        elif completion_rate > 0:
            return "started"
        else:
            return "not_started"

    def _check_tests_passed(self, story_id: str) -> bool:
        """テスト通過状況を確認（モック実装）"""
        return True

    def _check_lint_status(self, story_id: str) -> bool:
        """Lintエラー状況を確認（モック実装）"""
        return True

    def _get_recommendation(self, checks: Dict[str, bool]) -> str:
        """統合に向けた推奨アクションを生成"""
        if all(checks.values()):
            return "統合準備完了。F12（CodeIntegrator）で統合を開始できます。"

        recommendations = []
        if not checks["completion_rate_ok"]:
            recommendations.append("Sub-taskの完了率を80%以上にしてください。")
        if not checks["no_failed_subtasks"]:
            recommendations.append("失敗したSub-taskを修正してください。")
        if not checks["all_tests_passed"]:
            recommendations.append("すべてのテストを通過させてください。")
        if not checks["no_lint_errors"]:
            recommendations.append("Lintエラーを修正してください。")

        return " ".join(recommendations)


# テスト用
def test_progress_analyzer():
    """Phase 3 M3.1 テスト実行"""
    print("=" * 60)
    print("Phase 3: ProgressAnalyzer (F11) テスト実行（修正版）")
    print("=" * 60)
    print()

    try:
        analyzer = ProgressAnalyzer()
        print()

        # テスト1: Story進捗分析
        print("🧪 テスト1: Story進捗分析")
        progress = analyzer.analyze_story_progress("story_001")
        print(f"   Story ID: {progress['story_id']}")
        print(f"   完了度: {progress['completion_rate']:.1%}")
        print(f"   統合準備: {progress['integration_ready']}")
        print(f"   ステータス: {progress['status']}")
        print()

        # テスト2: 不足Sub-task検出
        print("🧪 テスト2: 不足Sub-task検出")
        test_story = {
            "story_id": "story_001",
            "target_lines": 1200,
            "description": "テストストーリー",
        }
        missing = analyzer.detect_missing_subtasks(test_story)
        print(f"   不足Sub-task: {len(missing)}個")
        for i, m in enumerate(missing, 1):
            print(f"     {i}. {m['subtask_name']} ({m['target_lines']}行)")
        print()

        # テスト3: 統合準備状況
        print("🧪 テスト3: 統合準備状況")
        readiness = analyzer.get_integration_readiness("story_001")
        print(f"   統合可能: {readiness['ready_for_integration']}")
        print(f"   チェック:")
        for check, passed in readiness["checks"].items():
            print(f"     - {check}: {'✅' if passed else '❌'}")
        print(f"   推奨: {readiness['recommendation']}")
        print()

        print("=" * 60)
        print("Phase 3 M3.1 テスト完了 ✅")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(test_progress_analyzer())
