"""
品質フィードバックループ（Loop 2の中核）
Quality_Score判定 → 改善案生成 → 自動再実行
要件定義書v3.0 Section 4.1.2準拠
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

from tools.sheets_validator import SheetsValidator


class QualityFeedbackLoop:
    """品質フィードバックループの実装"""

    def __init__(self, sheets_manager, gemini_client=None):
        """
        初期化

        Args:
            sheets_manager: GoogleSheetsManager インスタンス
            gemini_client: Gemini API クライアント（改善案生成用）
        """
        self.sheets = sheets_manager
        self.gemini = gemini_client
        self.validator = SheetsValidator()

        # 品質判定基準（要件定義書 3.2.1）
        self.QUALITY_THRESHOLDS = {
            "excellent": 9,  # 即時採用
            "good": 7,  # 条件付き採用
            "needs_improvement": 5,  # 改善案生成→再実行
            "unacceptable": 0,  # 代替アプローチ
        }

    async def process_task_result(self, task, result):
        """
        タスク結果の品質判定と適切なアクション実行

        Args:
            task: タスクデータ（dict）
            result: 実行結果（dict with 'quality_score'）

        Returns:
            dict: {
                'action': 'accepted' | 'retry_with_improvement' | 'retry_with_alternative',
                'message': str,
                'improvement_plan': dict (if retry)
            }
        """
        quality_score = result.get("quality_score", 0)
        task_id = task.get("task_id", "UNKNOWN")

        print(f"📊 品質判定: {task_id} → スコア {quality_score}/10")

        # CASE 1: 高品質（9-10点）→ 即時採用
        if quality_score >= self.QUALITY_THRESHOLDS["excellent"]:
            await self._mark_as_completed(task, result)
            return {"action": "accepted", "message": f"✅ 高品質（{quality_score}点）- 即時採用"}

        # CASE 2: 合格（7-8点）→ 条件付き採用
        elif quality_score >= self.QUALITY_THRESHOLDS["good"]:
            await self._mark_as_completed(task, result)
            await self._record_improvement_note(task, result)
            return {
                "action": "accepted_with_notes",
                "message": f"✅ 合格（{quality_score}点）- 改善メモ記録",
            }

        # CASE 3: 要改善（5-6点）→ 改善案生成 + 再実行
        elif quality_score >= self.QUALITY_THRESHOLDS["needs_improvement"]:
            improvement_plan = await self._generate_improvement(task, result)
            await self._create_retry_task(task, improvement_plan, reason="quality_improvement")
            return {
                "action": "retry_with_improvement",
                "message": f"⚠️ 要改善（{quality_score}点）- 改善案生成",
                "improvement_plan": improvement_plan,
            }

        # CASE 4: 不合格（4点以下）→ 代替アプローチ
        else:
            alternative = await self._generate_alternative(task, result)
            await self._create_retry_task(task, alternative, reason="alternative_approach")
            return {
                "action": "retry_with_alternative",
                "message": f"❌ 不合格（{quality_score}点）- 代替アプローチ",
                "improvement_plan": alternative,
            }

    async def _mark_as_completed(self, task, result):
        """タスクをcompletedにマーク"""
        task_id = task.get("task_id")

        # pm_tasksのステータス更新
        all_tasks = self.sheets.read_sheet("pm_tasks")
        for i, row in enumerate(all_tasks, start=2):
            if len(row) > 0 and (
                isinstance(row, list)
                and row[0] == task_id
                or isinstance(row, dict)
                and row.get("task_id") == task_id
            ):
                self.sheets.update_cell("pm_tasks", f"E{i}", "completed")
                print(f"  ✅ {task_id}: status → completed")
                break

    async def _record_improvement_note(self, task, result):
        """改善メモをログに記録（7-8点の場合）"""
        note = f"品質スコア{result.get('quality_score')}点: {result.get('quality_description', '要改善点あり')}"

        # task_execution_logに記録
        log_data = {
            "log_id": f"NOTE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "task_id": task.get("task_id"),
            "task_description": f"[改善メモ] {task.get('description', '')}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "agent_role": "QualityFeedbackLoop",
            "output_summary": note,
            "output_data": "",
            "status": "note_recorded",
            "Quality_Score": result.get("quality_score", 0),
            "Quality_description": result.get("quality_description", ""),
            "elapsed_time": 0.0,
            "retry_count": 0,
            "error_type": "",
            "fix_applied": False,
        }

        row = self.validator.create_valid_row("task_execution_log", log_data)
        self.sheets.append_rows("task_execution_log", row)
        print(f"  📝 改善メモ記録: {note}")

    async def _generate_improvement(self, task, result):
        """改善案を生成（5-6点の場合）"""
        # 簡易版: 品質説明から改善案を抽出
        quality_desc = result.get("quality_description", "不明")

        improvement_plan = {
            "original_approach": task.get("description", ""),
            "quality_issue": quality_desc,
            "suggested_improvement": f"品質向上策: {quality_desc}に対処する",
            "retry_count": task.get("retry_count", 0) + 1,
        }

        # Gemini APIが利用可能なら詳細な改善案を生成
        if self.gemini:
            try:
                prompt = f"""
以下のタスクが品質スコア{result.get('quality_score')}点でした。
タスク: {task.get('description')}
品質問題: {quality_desc}

具体的な改善策を3つ提案してください。
"""
                # Gemini API呼び出し（実装は省略、ここでは簡易版）
                improvement_plan["suggested_improvement"] = "Gemini API改善案（未実装）"
            except Exception as e:
                print(f"  ⚠️ Gemini API呼び出し失敗: {e}")

        print(f"  💡 改善案生成: {improvement_plan['suggested_improvement']}")
        return improvement_plan

    async def _generate_alternative(self, task, result):
        """代替アプローチを生成（4点以下の場合）"""
        alternative = {
            "original_approach": task.get("description", ""),
            "failure_reason": result.get("quality_description", "不明"),
            "alternative_approach": f"代替案: 別の方法で実装を試みる",
            "retry_count": task.get("retry_count", 0) + 1,
        }

        print(f"  🔄 代替案生成: {alternative['alternative_approach']}")
        return alternative

    async def _create_retry_task(self, task, improvement_plan, reason):
        """再実行タスクをpm_tasksに追加"""
        retry_task_data = {
            "task_id": f"{task.get('task_id')}-RETRY{improvement_plan['retry_count']}",
            "parent_goal_id": task.get("parent_goal_id", ""),
            "description": f"[再実行] {improvement_plan.get('suggested_improvement', improvement_plan.get('alternative_approach', ''))}",
            "required_role": task.get("required_role", "developer"),
            "status": "pending",
            "priority": "high",  # 再実行は高優先度
            "estimated_time": task.get("estimated_time", 30),
            "dependencies": task.get("task_id", ""),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "batch_id": f"RETRY-{task.get('batch_id', '')}",
        }

        row = self.validator.create_valid_row("pm_tasks", retry_task_data)
        is_valid, message = self.validator.validate_before_write("pm_tasks", row)

        if is_valid:
            self.sheets.append_rows("pm_tasks", row)
            print(f"  ✅ 再実行タスク作成: {retry_task_data['task_id']}")
        else:
            print(f"  ❌ 再実行タスク作成失敗: {message}")


# テスト用コード
if __name__ == "__main__":
    import asyncio

    from tools.sheets_manager import GoogleSheetsManager

    async def test_quality_feedback():
        """品質フィードバックループのテスト"""
        print("🧪 QualityFeedbackLoopテスト開始")

        sheets = GoogleSheetsManager()
        qfl = QualityFeedbackLoop(sheets)

        # テストケース1: 高品質（9点）
        task1 = {
            "task_id": "TEST-001",
            "description": "テストタスク1",
            "required_role": "developer",
        }
        result1 = {"quality_score": 9, "quality_description": "優秀"}

        response1 = await qfl.process_task_result(task1, result1)
        print(f"  テスト1: {response1['message']}")
        assert response1["action"] == "accepted", "高品質タスクが即時採用されていない"

        # テストケース2: 要改善（6点）
        task2 = {
            "task_id": "TEST-002",
            "description": "テストタスク2",
            "required_role": "developer",
            "retry_count": 0,
        }
        result2 = {"quality_score": 6, "quality_description": "コードの可読性に問題"}

        response2 = await qfl.process_task_result(task2, result2)
        print(f"  テスト2: {response2['message']}")
        assert response2["action"] == "retry_with_improvement", "要改善タスクが再実行されていない"

        # テストケース3: 不合格（3点）
        task3 = {
            "task_id": "TEST-003",
            "description": "テストタスク3",
            "required_role": "developer",
        }
        result3 = {"quality_score": 3, "quality_description": "機能要件を満たしていない"}

        response3 = await qfl.process_task_result(task3, result3)
        print(f"  テスト3: {response3['message']}")
        assert (
            response3["action"] == "retry_with_alternative"
        ), "不合格タスクが代替アプローチされていない"

        print("\n✅ 全テスト合格")

    asyncio.run(test_quality_feedback())
