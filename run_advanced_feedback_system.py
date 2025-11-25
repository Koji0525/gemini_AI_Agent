#!/usr/bin/env python3
"""
高度なフィードバックシステム
- ゴールベースの優先度制御
- 過去実行データの活用
- 品質評価と再実行
- 進捗レポート
"""
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent))
os.environ["DISPLAY"] = ":1"

from browser_control.browser_controller import BrowserController
from configuration.config_loader import (get_service_account_file,
                                         get_spreadsheet_id)
from tools.sheets_manager import GoogleSheetsManager

# WordPressエージェント（インポートエラー対策）
try:
    from wordpress.wp_agent import WordPressAgent

    HAS_WP_AGENT = True
except:
    HAS_WP_AGENT = False

try:
    from wordpress.wp_dev.wp_requirements_agent import \
        WordPressRequirementsAgent

    HAS_WP_REQ_AGENT = True
except:
    HAS_WP_REQ_AGENT = False


class AdvancedFeedbackExecutor:
    """高度なフィードバックシステム付きExecutor"""

    def __init__(self, sheets_manager, browser_controller):
        self.sheets = sheets_manager
        self.browser = browser_controller
        self.output_dir = Path("agent_outputs/advanced")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.rate_limit = 10

        # エージェント初期化
        self.agents = {}
        self._initialize_agents()

        # プロジェクトゴール
        self.project_goal = None

    def _initialize_agents(self):
        """エージェント初期化"""

        print(f"\n🤖 エージェント初期化:")

        if HAS_WP_AGENT:
            try:
                self.agents["wp"] = WordPressAgent(self.browser)
                self.agents["wordpress"] = self.agents["wp"]
                print("  ✅ WordPressAgent")
            except Exception as e:
                print(f"  ⚠️  初期化失敗: {e}")

        if HAS_WP_REQ_AGENT:
            try:
                self.agents["wp_requirements"] = WordPressRequirementsAgent(self.browser)
                print("  ✅ WordPressRequirementsAgent")
            except Exception as e:
                print(f"  ⚠️  初期化失敗: {e}")

        print(f"\n📊 登録済み: {len(self.agents)}種類")

    async def load_project_goal(self) -> str:
        """プロジェクトゴールを読み込み"""

        try:
            spreadsheet = self.sheets.gc.open_by_key(get_spreadsheet_id())
            goal_sheet = spreadsheet.worksheet("project_goal")

            # ゴール情報を取得
            all_data = goal_sheet.get_all_values()

            if len(all_data) > 1:
                # 最新のゴールを取得（最後の行）
                latest_goal = all_data[-1]
                goal_text = latest_goal[1] if len(latest_goal) > 1 else ""

                print(f"\n🎯 プロジェクトゴール:")
                print(f"   {goal_text[:100]}...")

                self.project_goal = goal_text
                return goal_text

            return ""

        except Exception as e:
            print(f"⚠️  ゴール読み込みエラー: {e}")
            return ""

    async def analyze_execution_history(self) -> Dict:
        """過去の実行履歴を分析"""

        print(f"\n📊 実行履歴分析中...")

        try:
            spreadsheet = self.sheets.gc.open_by_key(get_spreadsheet_id())
            log_sheet = spreadsheet.worksheet("task_execution_log")

            all_data = log_sheet.get_all_values()

            if len(all_data) <= 1:
                return {"total": 0, "completed": 0, "failed": 0}

            # 統計
            stats = {
                "total": len(all_data) - 1,
                "completed": 0,
                "failed": 0,
                "by_agent": {},
                "recent_failures": [],
            }

            for row in all_data[1:]:
                if len(row) > 7:
                    status = row[7]
                    agent = row[4] if len(row) > 4 else "unknown"

                    if status == "completed":
                        stats["completed"] += 1
                    elif status == "failed":
                        stats["failed"] += 1

                        # 最近の失敗を記録
                        if len(stats["recent_failures"]) < 5:
                            stats["recent_failures"].append(
                                {"task_id": row[1], "description": row[2][:50], "agent": agent}
                            )

                    # エージェント別統計
                    if agent not in stats["by_agent"]:
                        stats["by_agent"][agent] = {"completed": 0, "failed": 0}

                    if status == "completed":
                        stats["by_agent"][agent]["completed"] += 1
                    elif status == "failed":
                        stats["by_agent"][agent]["failed"] += 1

            print(f"   全実行: {stats['total']}件")
            print(f"   ✅ 成功: {stats['completed']}件")
            print(f"   ❌ 失敗: {stats['failed']}件")

            if stats["total"] > 0:
                success_rate = stats["completed"] / stats["total"] * 100
                print(f"   成功率: {success_rate:.1f}%")

            if stats["recent_failures"]:
                print(f"\n   最近の失敗タスク:")
                for fail in stats["recent_failures"]:
                    print(f"     - タスク{fail['task_id']}: {fail['description']}...")

            return stats

        except Exception as e:
            print(f"   ❌ 分析エラー: {e}")
            return {"total": 0, "completed": 0, "failed": 0}

    async def prioritize_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """タスクを優先度順にソート（ゴール達成に重要な順）"""

        print(f"\n🎯 タスク優先度付け中...")

        # 優先度の重み付け
        priority_weights = {"high": 3, "medium": 2, "low": 1, "": 1}

        # ソート
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (
                # 1. 優先度（high > medium > low）
                -priority_weights.get(t.get("priority", "").lower(), 1),
                # 2. 依存関係なし優先（依存なし > 依存あり）
                0 if t.get("dependencies") else 1,
                # 3. タスクID（古い順）
                int(t.get("task_id", 999)),
            ),
        )

        print(f"   優先度ソート完了")
        print(f"\n   実行順（最初の5件）:")
        for i, task in enumerate(sorted_tasks[:5], 1):
            priority = task.get("priority", "なし")
            deps = f"(依存: {task.get('dependencies')})" if task.get("dependencies") else ""
            print(f"     {i}. タスク{task.get('task_id')}: {priority} {deps}")

        return sorted_tasks

    async def log_to_execution_log(
        self,
        task_id: int,
        task_description: str,
        agent_role: str,
        status: str,
        output_summary: str = "",
        output_data: str = "",
    ):
        """task_execution_log に記録"""

        try:
            spreadsheet = self.sheets.gc.open_by_key(get_spreadsheet_id())
            log_sheet = spreadsheet.worksheet("task_execution_log")

            all_data = log_sheet.get_all_values()
            next_log_id = len(all_data)

            row = [
                next_log_id,
                task_id,
                task_description[:100],
                datetime.now().isoformat(),
                agent_role,
                output_summary[:100],
                output_data[:500],
                status,
            ]

            log_sheet.append_rows(row)
            print(f"   ✅ task_execution_log 記録 (log_id: {next_log_id})")
            return True

        except Exception as e:
            print(f"   ❌ ログ記録エラー: {e}")
            return False

    async def get_dependency_output(self, dependency_task_id: int) -> Optional[str]:
        """依存タスクの出力を取得"""

        try:
            spreadsheet = self.sheets.gc.open_by_key(get_spreadsheet_id())
            log_sheet = spreadsheet.worksheet("task_execution_log")

            all_data = log_sheet.get_all_values()

            for row in reversed(all_data[1:]):
                if len(row) > 1 and str(row[1]) == str(dependency_task_id):
                    output_summary = row[5] if len(row) > 5 else ""
                    output_data = row[6] if len(row) > 6 else ""

                    print(f"   📥 依存タスク{dependency_task_id}の出力取得")

                    return f"{output_summary}\n\n{output_data}"

            return None

        except Exception as e:
            print(f"   ❌ 依存タスク取得エラー: {e}")
            return None

    async def generate_progress_report(self, results: Dict):
        """進捗レポートを生成"""

        print(f"\n📋 進捗レポート生成中...")

        report = f"""
# プロジェクト進捗レポート

生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 今回の実行結果

- 実行タスク数: {results['total']}
- ✅ 成功: {results['success']}
- ❌ 失敗: {results['failed']}
- 成功率: {results['success']/results['total']*100:.1f}%
- 実行時間: {results['duration']:.1f}秒

## プロジェクトゴール

{self.project_goal if self.project_goal else '（未設定）'}

## 次のステップ

"""

        # 次のステップを提案
        if results["failed"] > 0:
            report += "1. 失敗したタスクを確認・修正\n"

        report += "2. 依存関係のあるタスクを順次実行\n"
        report += "3. 完了タスクの品質確認\n"

        # ファイル保存
        report_path = (
            self.output_dir / f"progress_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"   💾 レポート保存: {report_path}")

        return report

    async def execute_all_pending(self, max_tasks: Optional[int] = None) -> Dict:
        """高度なフィードバック付きタスク実行"""

        print("\n" + "=" * 70)
        print("🚀 高度なフィードバックシステム起動")
        print("=" * 70)

        # [1] プロジェクトゴール読み込み
        await self.load_project_goal()

        # [2] 実行履歴分析
        await self.analyze_execution_history()

        # [3] タスク読み込み
        print("\n[3/7] タスク読み込み...")
        tasks = await self.sheets.load_tasks_from_sheet(sheet_name="pm_tasks")

        if not tasks:
            return {"total": 0, "success": 0, "failed": 0}

        # pending抽出
        pending = []
        for t in tasks:
            status = t.get("status", "").strip().lower()
            if "pending" in status or status == "":
                pending.append(t)

        if not pending:
            print(f"⚠️  pendingタスクなし")
            return {"total": 0, "success": 0, "failed": 0}

        # [4] 優先度付け
        pending = await self.prioritize_tasks(pending)

        if max_tasks and len(pending) > max_tasks:
            pending = pending[:max_tasks]

        print(f"\n✅ {len(pending)}件のpendingタスクを実行（優先度順）")

        # [5] Gemini準備
        print("\n[5/7] Gemini接続...")
        if not await self.browser.navigate_to_gemini():
            return {"total": 0, "success": 0, "failed": 0}
        print("✅ 完了")

        # [6] タスク実行
        print("\n[6/7] タスク実行開始...")

        results = {
            "total": len(pending),
            "success": 0,
            "failed": 0,
            "details": [],
            "start_time": datetime.now(),
        }

        for i, task in enumerate(pending, 1):
            task_id = task.get("task_id")
            role = task.get("required_role", "design").strip().lower()
            description = task.get("description", "")
            dependencies = task.get("dependencies", "")
            priority = task.get("priority", "medium")

            print(f"\n{'='*70}")
            print(f"[{i}/{len(pending)}] タスク{task_id}: {role} (優先度: {priority})")
            print(f"概要: {description[:60]}...")
            if dependencies:
                print(f"📌 依存: タスク{dependencies}")
            print(f"{'='*70}")

            # 依存タスクの出力取得
            dependency_output = None
            if dependencies:
                dependency_output = await self.get_dependency_output(int(dependencies))

            # エージェント選択
            agent = self.agents.get(role)

            try:
                # in_progress
                await self.sheets.update_task_status(
                    task_id=task_id, status="in_progress", sheet_name="pm_tasks"
                )

                # タスク実行
                if agent and hasattr(agent, "execute_task"):
                    print(f"   🤖 WordPress専門エージェント")
                    result = await agent.execute_task(task)
                    success = result.get("success", False)
                    output = result.get("output", "")
                else:
                    print(f"   🤖 Gemini統合 ({role})")
                    success, output, error = await self._execute_with_gemini(
                        task, role, dependency_output
                    )

                # ステータス更新
                if success:
                    await self.sheets.update_task_status(
                        task_id=task_id, status="completed", sheet_name="pm_tasks"
                    )
                    results["success"] += 1
                    print(f"✅ 完了")
                else:
                    await self.sheets.update_task_status(
                        task_id=task_id, status="failed", sheet_name="pm_tasks"
                    )
                    results["failed"] += 1
                    print(f"❌ 失敗")

                # ログ記録
                await self.log_to_execution_log(
                    task_id=task_id,
                    task_description=description,
                    agent_role=role,
                    status="completed" if success else "failed",
                    output_summary=output[:100] if output else "",
                    output_data=output[:500] if output else "",
                )

                results["details"].append({"task_id": task_id, "role": role, "success": success})

                # レート制限
                if i < len(pending):
                    print(f"\n⏳ {self.rate_limit}秒待機...")
                    await asyncio.sleep(self.rate_limit)

            except Exception as e:
                print(f"❌ エラー: {e}")
                results["failed"] += 1

        results["end_time"] = datetime.now()
        results["duration"] = (results["end_time"] - results["start_time"]).total_seconds()

        # [7] 進捗レポート生成
        print("\n[7/7] 進捗レポート生成...")
        await self.generate_progress_report(results)

        # サマリー
        print("\n" + "=" * 70)
        print("📊 実行結果")
        print("=" * 70)
        print(f"実行: {results['total']}")
        print(f"✅ 成功: {results['success']}")
        print(f"❌ 失敗: {results['failed']}")
        print(f"⏱️  時間: {results['duration']:.1f}秒")

        if results["total"] > 0:
            print(f"成功率: {results['success']/results['total']*100:.1f}%")

        print("=" * 70)

        return results

    async def _execute_with_gemini(
        self, task: Dict, role: str, dependency_output: Optional[str] = None
    ):
        """Gemini実行"""

        task_id = task.get("task_id")
        description = task.get("description", "")

        prompt = f"""あなたは{role}の専門家です。

タスクID: {task_id}
内容: {description}

プロジェクトゴール:
{self.project_goal if self.project_goal else '（未設定）'}
"""

        if dependency_output:
            prompt += f"""

【前提情報】
前のタスクの出力:
{dependency_output[:1000]}

上記を踏まえて実行してください。
"""

        prompt += "\n具体的な成果物を作成してください。"

        try:
            await self.browser.send_prompt(prompt)
            await self.browser.wait_for_text_generation(max_wait=120)
            response = await self.browser.extract_latest_text_response()

            if response and len(response) > 100:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = self.output_dir / f"task_{task_id}_{role}_{timestamp}.md"

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# タスク {task_id}: {role}\n\n")
                    f.write(f"**概要**: {description}\n\n")
                    if dependency_output:
                        f.write(f"**前提情報**: 依存タスクの出力を参照\n\n")
                    f.write("---\n\n")
                    f.write(response)

                print(f"   💾 {len(response)}文字")

                return True, response, ""
            else:
                return False, "", "レスポンス不足"

        except Exception as e:
            return False, "", str(e)


async def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--max-tasks", type=int, help="最大タスク数")
    args = parser.parse_args()

    print("=" * 70)
    print("🎯 高度なフィードバックシステム")
    print("=" * 70)
    print("\n機能:")
    print("  ✅ プロジェクトゴール参照")
    print("  ✅ 過去実行履歴分析")
    print("  ✅ ゴールベースの優先度制御")
    print("  ✅ dependencies活用")
    print("  ✅ 進捗レポート自動生成")

    sheets = GoogleSheetsManager(
        spreadsheet_id=get_spreadsheet_id(), service_account_file=get_service_account_file()
    )

    async with BrowserController(download_folder="./downloads") as browser:
        executor = AdvancedFeedbackExecutor(sheets, browser)
        results = await executor.execute_all_pending(max_tasks=args.max_tasks)

    print("\n📋 完了")
    print(f"Google Sheets: https://docs.google.com/spreadsheets/d/{get_spreadsheet_id()}")


if __name__ == "__main__":
    asyncio.run(main())
