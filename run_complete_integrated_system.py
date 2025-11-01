#!/usr/bin/env python3
"""
完全統合版システム
- 既存エージェント完全統合
- task_execution_log への自動ログ記録
- aggressive モードデフォルト
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

# 既存エージェントのインポート（存在する場合）
try:
    from agents.design_agent import DesignAgent

    HAS_DESIGN_AGENT = True
except:
    HAS_DESIGN_AGENT = False
    print("⚠️  design_agent.py が見つかりません（Gemini統合を使用）")

try:
    from agents.dev_agent import DevAgent

    HAS_DEV_AGENT = True
except:
    HAS_DEV_AGENT = False

try:
    from agents.review_agent import ReviewAgent

    HAS_REVIEW_AGENT = True
except:
    HAS_REVIEW_AGENT = False

try:
    from wordpress.wp_agent import WPAgent

    HAS_WP_AGENT = True
except:
    HAS_WP_AGENT = False

try:
    from wordpress.wp_dev.wp_cpt_agent import WPCPTAgent

    HAS_WP_CPT_AGENT = True
except:
    HAS_WP_CPT_AGENT = False


class CompleteIntegratedExecutor:
    """完全統合版TaskExecutor"""

    def __init__(self, sheets_manager, browser_controller, rate_limit=10):
        self.sheets = sheets_manager
        self.browser = browser_controller
        self.output_dir = Path("agent_outputs/integrated")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # レート制限（デフォルト: aggressive 10秒）
        self.rate_limit = rate_limit

        print(f"\n⏱️  レート制限: {self.rate_limit}秒（aggressiveモード）")
        print(f"   1時間あたり: 約{3600 // self.rate_limit}タスク")

        # エージェント初期化
        self.agents = {}
        self._initialize_agents()

    def _initialize_agents(self):
        """エージェント初期化"""

        print(f"\n🤖 エージェント初期化:")

        # 既存エージェントを使用
        if HAS_DESIGN_AGENT:
            self.agents["design"] = DesignAgent(self.sheets, self.browser)
            print("  ✅ DesignAgent")

        if HAS_DEV_AGENT:
            self.agents["dev"] = DevAgent(self.sheets, self.browser)
            print("  ✅ DevAgent")

        if HAS_REVIEW_AGENT:
            self.agents["review"] = ReviewAgent(self.sheets, self.browser)
            print("  ✅ ReviewAgent")

        if HAS_WP_AGENT:
            self.agents["wp"] = WPAgent(self.sheets, self.browser)
            print("  ✅ WPAgent")

        if HAS_WP_CPT_AGENT:
            self.agents["wp_cpt"] = WPCPTAgent(self.sheets, self.browser)
            self.agents["wp_dev"] = self.agents["wp_cpt"]  # エイリアス
            print("  ✅ WPCPTAgent (wp_dev)")

        print(f"\n📊 登録済みエージェント: {len(self.agents)}種類")

        if not self.agents:
            print("\n⚠️  既存エージェントが見つかりません")
            print("   Gemini統合モードで動作します")

    async def log_task_execution(self, task_id: int, agent_name: str, status: str, output: str = "", error: str = ""):
        """task_execution_log シートにログ記録"""

        try:
            # save_task_output メソッドを使用（既存機能）
            output_data = {
                "task_id": task_id,
                "agent": agent_name,
                "status": status,
                "output": output[:500] if output else "",  # 500文字まで
                "error": error[:500] if error else "",
                "timestamp": datetime.now().isoformat(),
                "executed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            # sheets_manager の save_task_output を呼び出し
            if hasattr(self.sheets, "save_task_output"):
                await self.sheets.save_task_output(output_data)
                print(f"   📝 ログ記録: task_execution_log")
            else:
                # 直接シートに書き込み
                await self._write_log_directly(output_data)

        except Exception as e:
            print(f"   ⚠️  ログ記録エラー: {e}")

    async def _write_log_directly(self, data: Dict):
        """task_execution_log に直接書き込み"""

        try:
            import gspread

            spreadsheet = self.sheets.gc.open_by_key(get_spreadsheet_id())

            # シート取得または作成
            try:
                log_sheet = spreadsheet.worksheet("task_execution_log")
            except:
                # シートが存在しない場合は作成
                log_sheet = spreadsheet.add_worksheet(title="task_execution_log", rows=1000, cols=10)
                # ヘッダー設定
                log_sheet.update(
                    "A1:G1", [["task_id", "agent", "status", "output", "error", "timestamp", "executed_at"]]
                )

            # データ追加
            row_data = [
                data.get("task_id", ""),
                data.get("agent", ""),
                data.get("status", ""),
                data.get("output", ""),
                data.get("error", ""),
                data.get("timestamp", ""),
                data.get("executed_at", ""),
            ]

            log_sheet.append_row(row_data)
            print(f"   📝 ログ直接書き込み完了")

        except Exception as e:
            print(f"   ⚠️  直接書き込みエラー: {e}")

    async def execute_all_pending(self, max_tasks: Optional[int] = None) -> Dict:
        """すべてのpendingタスクを実行"""

        print("\n" + "=" * 70)
        print("🚀 完全統合システム起動")
        print("=" * 70)

        # タスク読み込み
        print("\n[1/6] タスク読み込み...")
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
            print(f"⚠️  pendingタスクなし（全{len(tasks)}件中）")
            return {"total": 0, "success": 0, "failed": 0}

        # 最大タスク数制限
        if max_tasks and len(pending) > max_tasks:
            pending = pending[:max_tasks]

        print(f"✅ {len(pending)}件のpendingタスクを実行")

        # Gemini準備
        print("\n[2/6] Gemini接続...")
        if not await self.browser.navigate_to_gemini():
            return {"total": 0, "success": 0, "failed": 0}

        print("✅ Gemini準備完了")

        # タスク実行
        print("\n[3/6] タスク実行開始...")

        results = {"total": len(pending), "success": 0, "failed": 0, "details": [], "start_time": datetime.now()}

        for i, task in enumerate(pending, 1):
            task_id = task.get("task_id")
            role = task.get("required_role", "design").strip().lower()

            print(f"\n{'='*70}")
            print(f"[{i}/{len(pending)}] タスク{task_id}: {role}")
            print(f"{'='*70}")

            # エージェント選択
            agent = self.agents.get(role)
            agent_name = f"{role}_agent" if agent else "gemini_fallback"

            if agent:
                print(f"🤖 使用: {agent.__class__.__name__}")
            else:
                print(f"🤖 使用: Gemini統合（{role}用エージェント未登録）")

            try:
                # ステータス更新: in_progress
                await self.sheets.update_task_status(task_id=task_id, status="in_progress", sheet_name="pm_tasks")

                # タスク実行
                if agent and hasattr(agent, "execute_task"):
                    # 既存エージェントで実行
                    result = await agent.execute_task(task)
                    success = result.get("success", False)
                    output = result.get("output", "")
                    error = result.get("error", "")
                else:
                    # Gemini統合で実行
                    success, output, error = await self._execute_with_gemini(task, role)

                # 結果に応じてステータス更新
                if success:
                    await self.sheets.update_task_status(task_id=task_id, status="completed", sheet_name="pm_tasks")
                    results["success"] += 1
                    print(f"✅ 完了")
                else:
                    await self.sheets.update_task_status(task_id=task_id, status="failed", sheet_name="pm_tasks")
                    results["failed"] += 1
                    print(f"❌ 失敗")

                # ログ記録
                await self.log_task_execution(
                    task_id=task_id,
                    agent_name=agent_name,
                    status="completed" if success else "failed",
                    output=output if success else "",
                    error=error if not success else "",
                )

                results["details"].append({"task_id": task_id, "role": role, "agent": agent_name, "success": success})

                # レート制限
                if i < len(pending):
                    print(f"\n⏳ {self.rate_limit}秒待機...")
                    await asyncio.sleep(self.rate_limit)

            except Exception as e:
                print(f"❌ エラー: {e}")

                await self.sheets.update_task_status(task_id=task_id, status="failed", sheet_name="pm_tasks")

                await self.log_task_execution(task_id=task_id, agent_name=agent_name, status="failed", error=str(e))

                results["failed"] += 1

        results["end_time"] = datetime.now()
        results["duration"] = (results["end_time"] - results["start_time"]).total_seconds()

        # サマリー
        print("\n" + "=" * 70)
        print("📊 実行結果")
        print("=" * 70)
        print(f"実行: {results['total']}")
        print(f"✅ 成功: {results['success']}")
        print(f"❌ 失敗: {results['failed']}")
        print(f"⏱️  時間: {results['duration']:.1f}秒")
        print(f"成功率: {results['success']/results['total']*100:.1f}%")
        print("=" * 70)

        return results

    async def _execute_with_gemini(self, task: Dict, role: str):
        """Gemini統合実行"""

        task_id = task.get("task_id")
        description = task.get("description", "")

        prompt = f"""あなたは{role}の専門家です。

タスクID: {task_id}
内容: {description}

具体的な成果物を作成してください。"""

        try:
            await self.browser.send_prompt(prompt)
            await self.browser.wait_for_text_generation(max_wait=120)
            response = await self.browser.extract_latest_text_response()

            if response and len(response) > 100:
                # ファイル保存
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = self.output_dir / f"task_{task_id}_{role}_{timestamp}.md"

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# タスク {task_id}\n\n{response}")

                print(f"   💾 {len(response)}文字 → {filepath.name}")

                return True, response, ""
            else:
                return False, "", "レスポンス不足"

        except Exception as e:
            return False, "", str(e)


async def main():
    print("=" * 70)
    print("🎯 完全統合システム（既存エージェント対応）")
    print("=" * 70)

    sheets = GoogleSheetsManager(spreadsheet_id=get_spreadsheet_id(), service_account_file=get_service_account_file())

    async with BrowserController(download_folder="./downloads") as browser:
        executor = CompleteIntegratedExecutor(sheets, browser, rate_limit=10)  # aggressive モード

        results = await executor.execute_all_pending()

    print("\n📋 完了")
    print(f"Google Sheets: https://docs.google.com/spreadsheets/d/{get_spreadsheet_id()}")


if __name__ == "__main__":
    asyncio.run(main())
