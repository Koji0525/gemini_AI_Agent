#!/usr/bin/env python3
"""
完全統合版（WordPressエージェント対応）
- WordPress専門エージェント統合
- task_execution_log自動記録
- aggressive モード（10秒）デフォルト
- エージェント名明確表示
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent))
os.environ["DISPLAY"] = ":1"

from configuration.config_loader import get_spreadsheet_id, get_service_account_file
from browser_control.browser_controller import BrowserController
from tools.sheets_manager import GoogleSheetsManager

# WordPressエージェントのインポート
try:
    from wordpress.wp_agent import WPAgent

    HAS_WP_AGENT = True
    print("✅ WPAgent インポート成功")
except Exception as e:
    HAS_WP_AGENT = False
    print(f"⚠️  WPAgent インポート失敗: {e}")

try:
    from wordpress.wp_dev.wp_cpt_agent import WPCPTAgent

    HAS_WP_CPT_AGENT = True
    print("✅ WPCPTAgent インポート成功")
except Exception as e:
    HAS_WP_CPT_AGENT = False
    print(f"⚠️  WPCPTAgent インポート失敗: {e}")

try:
    from wordpress.wp_dev.wp_acf_agent import WPACFAgent

    HAS_WP_ACF_AGENT = True
    print("✅ WPACFAgent インポート成功")
except Exception as e:
    HAS_WP_ACF_AGENT = False
    print(f"⚠️  WPACFAgent インポート失敗: {e}")

try:
    from wordpress.wp_dev.wp_requirements_agent import WPRequirementsAgent

    HAS_WP_REQ_AGENT = True
    print("✅ WPRequirementsAgent インポート成功")
except Exception as e:
    HAS_WP_REQ_AGENT = False
    print(f"⚠️  WPRequirementsAgent インポート失敗: {e}")


class CompleteExecutor:
    """完全統合版Executor（WordPress対応）"""

    def __init__(self, sheets_manager, browser_controller):
        self.sheets = sheets_manager
        self.browser = browser_controller
        self.output_dir = Path("agent_outputs/complete")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # レート制限（aggressive: 10秒）
        self.rate_limit = 10

        print(f"\n⏱️  レート制限: {self.rate_limit}秒 (aggressive)")
        print(f"   1時間あたり: 約{3600 // self.rate_limit}タスク")

        # エージェント初期化
        self.agents = {}
        self.agent_display_names = {}
        self._initialize_agents()

    def _initialize_agents(self):
        """エージェント初期化"""

        print(f"\n🤖 エージェント初期化:")

        # WordPressエージェント
        if HAS_WP_AGENT:
            try:
                self.agents["wp"] = WPAgent(self.sheets, self.browser)
                self.agents["wordpress"] = self.agents["wp"]
                self.agent_display_names["wp"] = "🌐 WPAgent"
                self.agent_display_names["wordpress"] = "🌐 WPAgent"
                print("  ✅ WPAgent (wp, wordpress)")
            except Exception as e:
                print(f"  ⚠️  WPAgent初期化失敗: {e}")

        if HAS_WP_CPT_AGENT:
            try:
                self.agents["wp_cpt"] = WPCPTAgent(self.sheets, self.browser)
                self.agents["wp_dev"] = self.agents["wp_cpt"]
                self.agent_display_names["wp_cpt"] = "📝 WPCPTAgent"
                self.agent_display_names["wp_dev"] = "📝 WPCPTAgent"
                print("  ✅ WPCPTAgent (wp_cpt, wp_dev)")
            except Exception as e:
                print(f"  ⚠️  WPCPTAgent初期化失敗: {e}")

        if HAS_WP_ACF_AGENT:
            try:
                self.agents["wp_acf"] = WPACFAgent(self.sheets, self.browser)
                self.agent_display_names["wp_acf"] = "🔧 WPACFAgent"
                print("  ✅ WPACFAgent (wp_acf)")
            except Exception as e:
                print(f"  ⚠️  WPACFAgent初期化失敗: {e}")

        if HAS_WP_REQ_AGENT:
            try:
                self.agents["wp_requirements"] = WPRequirementsAgent(self.sheets, self.browser)
                self.agent_display_names["wp_requirements"] = "📋 WPRequirementsAgent"
                print("  ✅ WPRequirementsAgent (wp_requirements)")
            except Exception as e:
                print(f"  ⚠️  WPRequirementsAgent初期化失敗: {e}")

        # デフォルトエージェント（Gemini統合）
        for role in ["design", "dev", "content", "review", "writer_en"]:
            self.agent_display_names[role] = f"🤖 Gemini ({role})"

        print(f"\n📊 登録済み:")
        print(f"   WordPress専門: {sum(1 for k in self.agents.keys() if 'wp' in k)}種類")
        print(f"   Gemini統合: design, dev, content, review, writer_en")
        print(f"   合計: {len(self.agents) + 5}種類")

    async def execute_all_pending(self, max_tasks: Optional[int] = None) -> Dict:
        """すべてのpendingタスクを実行"""

        print("\n" + "=" * 70)
        print("🚀 完全統合システム起動")
        print("=" * 70)

        # [1] タスク読み込み
        print("\n[1/5] タスク読み込み...")
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

        if max_tasks and len(pending) > max_tasks:
            pending = pending[:max_tasks]

        print(f"✅ {len(pending)}件のpendingタスクを実行")

        # [2] Gemini準備
        print("\n[2/5] Gemini接続...")
        if not await self.browser.navigate_to_gemini():
            return {"total": 0, "success": 0, "failed": 0}
        print("✅ 完了")

        # [3] タスク実行
        print("\n[3/5] タスク実行開始...")

        results = {"total": len(pending), "success": 0, "failed": 0, "details": [], "start_time": datetime.now()}

        for i, task in enumerate(pending, 1):
            task_id = task.get("task_id")
            role = task.get("required_role", "design").strip().lower()
            description = task.get("description", "")

            print(f"\n{'='*70}")
            print(f"[{i}/{len(pending)}] タスク{task_id}: {role}")
            print(f"概要: {description[:60]}...")
            print(f"{'='*70}")

            # エージェント選択
            agent = self.agents.get(role)
            agent_name = self.agent_display_names.get(role, f"🤖 Gemini ({role})")

            print(f"🎯 実行エージェント: {agent_name}")

            try:
                # in_progress
                await self.sheets.update_task_status(task_id=task_id, status="in_progress", sheet_name="pm_tasks")

                # タスク実行
                if agent and hasattr(agent, "execute_task"):
                    # WordPress専門エージェントで実行
                    print(f"   → WordPress専門エージェントで処理")
                    result = await agent.execute_task(task)
                    success = result.get("success", False)
                    output = result.get("output", "")
                    error = result.get("error", "")
                else:
                    # Gemini統合で実行
                    print(f"   → Gemini統合で処理")
                    success, output, error = await self._execute_with_gemini(task, role)

                # ステータス更新
                if success:
                    await self.sheets.update_task_status(task_id=task_id, status="completed", sheet_name="pm_tasks")
                    results["success"] += 1
                    print(f"✅ 完了")
                else:
                    await self.sheets.update_task_status(task_id=task_id, status="failed", sheet_name="pm_tasks")
                    results["failed"] += 1
                    print(f"❌ 失敗")

                # task_execution_log にログ記録
                log_data = {
                    "task_id": task_id,
                    "task_description": description[:100],
                    "timestamp": datetime.now().isoformat(),
                    "agent_role": role,
                    "output_summary": output[:100] if output else "",
                    "output_data": output[:500] if output else "",
                    "status": "completed" if success else "failed",
                    "error": error if error else "",
                }

                await self.sheets.save_task_output(log_data)
                print(f"   📝 task_execution_log に記録")

                results["details"].append({"task_id": task_id, "role": role, "agent": agent_name, "success": success})

                # レート制限
                if i < len(pending):
                    print(f"\n⏳ {self.rate_limit}秒待機...")
                    await asyncio.sleep(self.rate_limit)

            except Exception as e:
                print(f"❌ エラー: {e}")

                await self.sheets.update_task_status(task_id=task_id, status="failed", sheet_name="pm_tasks")

                # エラーログ
                await self.sheets.save_task_output(
                    {
                        "task_id": task_id,
                        "task_description": description[:100],
                        "timestamp": datetime.now().isoformat(),
                        "agent_role": role,
                        "status": "failed",
                        "error": str(e),
                    }
                )

                results["failed"] += 1

        results["end_time"] = datetime.now()
        results["duration"] = (results["end_time"] - results["start_time"]).total_seconds()

        # [4] サマリー
        print("\n" + "=" * 70)
        print("📊 実行結果サマリー")
        print("=" * 70)
        print(f"実行: {results['total']}")
        print(f"✅ 成功: {results['success']}")
        print(f"❌ 失敗: {results['failed']}")
        print(f"⏱️  時間: {results['duration']:.1f}秒")

        if results["total"] > 0:
            print(f"成功率: {results['success']/results['total']*100:.1f}%")

        print(f"\nエージェント別実行:")
        agent_stats = {}
        for detail in results["details"]:
            agent = detail["agent"]
            if agent not in agent_stats:
                agent_stats[agent] = {"success": 0, "failed": 0}

            if detail["success"]:
                agent_stats[agent]["success"] += 1
            else:
                agent_stats[agent]["failed"] += 1

        for agent, stats in sorted(agent_stats.items()):
            total = stats["success"] + stats["failed"]
            print(f"  {agent}: {stats['success']}/{total} 成功")

        print("=" * 70)

        return results

    async def _execute_with_gemini(self, task: Dict, role: str):
        """Gemini統合実行"""

        task_id = task.get("task_id")
        description = task.get("description", "")

        prompt = f"""あなたは{role}の専門家です。

タスクID: {task_id}
内容: {description}

具体的な成果物を日本語で作成してください。"""

        try:
            await self.browser.send_prompt(prompt)
            await self.browser.wait_for_text_generation(max_wait=120)
            response = await self.browser.extract_latest_text_response()

            if response and len(response) > 100:
                # ファイル保存
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = self.output_dir / f"task_{task_id}_{role}_{timestamp}.md"

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# タスク {task_id}: {role}\n\n")
                    f.write(f"**概要**: {description}\n\n")
                    f.write("---\n\n")
                    f.write(response)

                print(f"   💾 {len(response)}文字 → {filepath.name}")

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
    print("🎯 完全統合システム（WordPress専門エージェント対応）")
    print("=" * 70)

    sheets = GoogleSheetsManager(spreadsheet_id=get_spreadsheet_id(), service_account_file=get_service_account_file())

    async with BrowserController(download_folder="./downloads") as browser:
        executor = CompleteExecutor(sheets, browser)
        results = await executor.execute_all_pending(max_tasks=args.max_tasks)

    print("\n📋 完了")
    print(f"Google Sheets: https://docs.google.com/spreadsheets/d/{get_spreadsheet_id()}")
    print(f"task_execution_log シートでログ確認可能")


if __name__ == "__main__":
    asyncio.run(main())
