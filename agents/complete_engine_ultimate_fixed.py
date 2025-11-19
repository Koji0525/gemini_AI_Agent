"""
CompleteEngine修正版
RobustTaskSelectorとAutoTaskGeneratorV2を統合
"""

import sys

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from agents.auto_task_generator import AutoTaskGeneratorV2
# 既存のCompleteEngineをインポート
from agents.complete_engine_ultimate import CompleteEngineUltimate
from agents.robust_task_selector import RobustTaskSelector


class CompleteEngineUltimateFixed(CompleteEngineUltimate):
    """CompleteEngine修正版"""

    def __init__(self):
        super().__init__()
        self.task_selector = RobustTaskSelector(self.sheets)
        self.task_generator = AutoTaskGeneratorV2(self.sheets)

    def run_full_integration_cycle_fixed(self, goal_id=None, limit=1):
        """統合フロー（修正版）"""
        print("\n" + "=" * 80)
        print("🚀 完全統合フロー開始（修正版）")
        print("=" * 80)

        # F1: タスク可用性チェック
        print("\n🔄 F1: タスク可用性チェック")
        pending_tasks = self.task_selector.get_pending_tasks()

        if len(pending_tasks) == 0:
            print("⚠️  pendingタスクが0個です")
            print("🔧 F1: 自動タスク生成を起動...")

            result = self.task_generator.auto_generate_if_needed()

            if result.get("generated"):
                print("✅ F1: 高品質タスクを生成しました")
                # 再度タスクを取得
                pending_tasks = self.task_selector.get_pending_tasks()
            else:
                print("⚠️  F1: タスク生成できませんでした")

        # F2: タスク選択（スマート選択）
        print(f"\n🎯 F2: タスク選択（{limit}個）")
        selected_tasks = self.task_selector.select_executable_task(limit=limit)

        if not selected_tasks:
            print("⚠️  実行可能なタスクがありません")
            return {"success": False, "message": "タスクなし"}

        # タスク実行
        success_count = 0
        for task in selected_tasks:
            print(f"\n{'=' * 80}")
            print(f"🚀 タスク実行: {task['task_id']}")
            print(f"   説明: {task['description'][:80]}...")
            print("=" * 80)

            try:
                # 詳細タスク定義のチェック
                if not task.get("detail_file_path"):
                    print("⚠️  詳細タスク定義がありません")
                    print("🔧 F6: 動的に詳細定義を生成します...")

                    # 詳細定義を動的生成
                    task["description"] = self._enhance_task_description(task)

                # タスク実行
                result = self.execute_task(task)

                # F3: 品質評価
                quality_score = result.get("quality_score", 0)
                print(f"\n📊 F3: 品質評価 = {quality_score}/100")

                # フォールバック実行を不合格とする
                if result.get("fallback", False):
                    print("❌ フォールバック実行のため不合格")
                    quality_score = 0

                # 品質評価に基づく判定
                if quality_score >= 70:
                    # ステータス更新
                    row_index = task["row_index"]
                    self.sheets.service.spreadsheets().values().update(
                        spreadsheetId=self.sheets.spreadsheet_id,
                        range=f"pm_tasks!E{row_index}",
                        valueInputOption="RAW",
                        body={"values": [["completed"]]},
                    ).execute()

                    print(f"✅ タスク完了: {task['task_id']}")
                    success_count += 1
                else:
                    print(f"⚠️  品質不足（{quality_score}/100）")
                    print("🔧 F7: 自己修復が必要です")
                    # TODO: F7統合

            except Exception as e:
                print(f"❌ タスク実行エラー: {e}")

        print(f"\n{'=' * 80}")
        print(f"✅ フロー完了: {success_count}/{len(selected_tasks)}件成功")
        print("=" * 80)

        return {
            "success": success_count > 0,
            "executed": len(selected_tasks),
            "succeeded": success_count,
        }

    def _enhance_task_description(self, task):
        """タスク説明を拡張"""
        description = task.get("description", "")

        # 既に詳細な説明の場合はそのまま
        if "【目的】" in description:
            return description

        # 簡易的な拡張
        enhanced = f"""
{description}

【目的】{description.split('：')[0] if '：' in description else description}を完了させる

【作業内容】
1. 要件を確認
2. 実装または調査を実施
3. 成果物を作成
4. テストと検証

【成功基準】
・{task['task_id']}の成果物が生成されている
・実行ログにエラーがない
・品質スコアが70以上

【コンテキスト】
既存システムとの統合を考慮し、実用的な成果物を作成する。
"""
        return enhanced.strip()
