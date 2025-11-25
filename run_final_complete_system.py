#!/usr/bin/env python3
"""
最終完全版統合システム
- task_execution_log への正しい記録
- WordPressエージェント正しいインポート
- dependencies活用のフィードバックループ
- aggressive モード（10秒）デフォルト
"""
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

sys.path.insert(0, str(Path(__file__).parent))
os.environ["DISPLAY"] = ":1"

from browser_control.browser_controller import BrowserController
from configuration.config_loader import (get_service_account_file,
                                         get_spreadsheet_id)
from tools.sheets_manager import GoogleSheetsManager

# WordPressエージェント（正しいクラス名でインポート）
try:
    from wordpress.wp_agent import WordPressAgent

    HAS_WP_AGENT = True
    print("✅ WordPressAgent インポート成功")
except Exception as e:
    HAS_WP_AGENT = False
    print(f"⚠️  WordPressAgent インポート失敗: {e}")

try:
    from wordpress.wp_dev.wp_cpt_agent import WordPressCPTAgent

    HAS_WP_CPT_AGENT = True
    print("✅ WordPressCPTAgent インポート成功")
except Exception as e:
    HAS_WP_CPT_AGENT = False
    print(f"⚠️  WordPressCPTAgent インポート失敗: {e}")

try:
    from wordpress.wp_dev.wp_acf_agent import WordPressACFAgent

    HAS_WP_ACF_AGENT = True
    print("✅ WordPressACFAgent インポート成功")
except Exception as e:
    HAS_WP_ACF_AGENT = False
    print(f"⚠️  WordPressACFAgent インポート失敗: {e}")

try:
    from wordpress.wp_dev.wp_requirements_agent import \
        WordPressRequirementsAgent

    HAS_WP_REQ_AGENT = True
    print("✅ WordPressRequirementsAgent インポート成功")
except Exception as e:
    HAS_WP_REQ_AGENT = False
    print(f"⚠️  WordPressRequirementsAgent インポート失敗: {e}")


class FinalCompleteExecutor:
    """最終完全版Executor"""

    def __init__(self, sheets_manager, browser_controller):
        self.sheets = sheets_manager
        self.browser = browser_controller
        self.output_dir = Path("agent_outputs/final")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # レート制限
        self.rate_limit = 10

        print(f"\n⏱️  レート制限: {self.rate_limit}秒 (aggressive)")

        # エージェント初期化
        self.agents = {}
        self.agent_display_names = {}
        self._initialize_agents()

    def _initialize_agents(self):
        """エージェント初期化（正しい引数で）"""

        print(f"\n🤖 エージェント初期化:")

        # WordPressエージェント（browser_controllerのみ渡す）
        if HAS_WP_AGENT:
            try:
                self.agents["wp"] = WordPressAgent(self.browser)
                self.agents["wordpress"] = self.agents["wp"]
                self.agent_display_names["wp"] = "🌐 WordPressAgent"
                self.agent_display_names["wordpress"] = "🌐 WordPressAgent"
                print("  ✅ WordPressAgent")
            except Exception as e:
                print(f"  ⚠️  WordPressAgent初期化失敗: {e}")

        if HAS_WP_CPT_AGENT:
            try:
                self.agents["wp_cpt"] = WordPressCPTAgent(self.browser)
                self.agents["wp_dev"] = self.agents["wp_cpt"]
                self.agent_display_names["wp_cpt"] = "📝 WordPressCPTAgent"
                self.agent_display_names["wp_dev"] = "📝 WordPressCPTAgent"
                print("  ✅ WordPressCPTAgent (wp_cpt, wp_dev)")
            except Exception as e:
                print(f"  ⚠️  WordPressCPTAgent初期化失敗: {e}")

        if HAS_WP_ACF_AGENT:
            try:
                self.agents["wp_acf"] = WordPressACFAgent(self.browser)
                self.agent_display_names["wp_acf"] = "🔧 WordPressACFAgent"
                print("  ✅ WordPressACFAgent")
            except Exception as e:
                print(f"  ⚠️  WordPressACFAgent初期化失敗: {e}")

        if HAS_WP_REQ_AGENT:
            try:
                self.agents["wp_requirements"] = WordPressRequirementsAgent(self.browser)
                self.agent_display_names["wp_requirements"] = "📋 WordPressRequirementsAgent"
                print("  ✅ WordPressRequirementsAgent")
            except Exception as e:
                print(f"  ⚠️  WordPressRequirementsAgent初期化失敗: {e}")

        # デフォルトエージェント
        for role in ["design", "dev", "content", "review", "writer_en"]:
            self.agent_display_names[role] = f"🤖 Gemini ({role})"

        print(f"\n📊 登録済み: WordPress={len([k for k in self.agents.keys() if 'wp' in k])}種類")

    async def log_to_execution_log(
        self,
        task_id: int,
        task_description: str,
        agent_role: str,
        status: str,
        output_summary: str = "",
        output_data: str = "",
    ):
        """task_execution_log シートに正しく記録"""

        try:
            # スプレッドシート取得
            spreadsheet = self.sheets.gc.open_by_key(get_spreadsheet_id())

            # task_execution_log シート取得
            try:
                log_sheet = spreadsheet.worksheet("task_execution_log")
            except:
                print("   ⚠️  task_execution_log シートが見つかりません")
                return False

            # 次のlog_idを取得
            all_data = log_sheet.get_all_values()
            next_log_id = len(all_data)  # ヘッダー含むので、次の行番号

            # データ行作成（既存の列構造に合わせる）
            row = [
                next_log_id,  # log_id
                task_id,  # task_id
                task_description[:100],  # task_description
                datetime.now().isoformat(),  # timestamp
                agent_role,  # agent_role
                output_summary[:100],  # output_summary
                output_data[:500],  # output_data
                status,  # status
            ]

            # 追加
            log_sheet.append_rows(row)

            print(f"   ✅ task_execution_log に記録 (log_id: {next_log_id})")
            return True

        except Exception as e:
            print(f"   ❌ ログ記録エラー: {e}")
            return False

    async def get_dependency_output(self, dependency_task_id: int) -> Optional[str]:
        """依存タスクの出力を取得（フィードバックループ）"""

        try:
            spreadsheet = self.sheets.gc.open_by_key(get_spreadsheet_id())
            log_sheet = spreadsheet.worksheet("task_execution_log")

            # 該当タスクのログを検索
            all_data = log_sheet.get_all_values()
            all_data[0]

            # task_idでフィルター
            for row in reversed(all_data[1:]):  # 最新から検索
                if len(row) > 1 and str(row[1]) == str(dependency_task_id):
                    # output_summaryとoutput_dataを取得
                    output_summary = row[5] if len(row) > 5 else ""
                    output_data = row[6] if len(row) > 6 else ""

                    print(f"   📥 依存タスク{dependency_task_id}の出力を取得")
                    print(f"      {output_summary[:80]}...")

                    return f"{output_summary}\n\n{output_data}"

            print(f"   ⚠️  依存タスク{dependency_task_id}の出力が見つかりません")
            return None

        except Exception as e:
            print(f"   ❌ 依存タスク取得エラー: {e}")
            return None

    async def execute_all_pending(self, max_tasks: Optional[int] = None) -> Dict:
        """すべてのpendingタスクを実行（依存関係を考慮）"""

        print("\n" + "=" * 70)
        print("🚀 最終完全版システム起動")
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
            print(f"⚠️  pendingタスクなし")
            return {"total": 0, "success": 0, "failed": 0}

        if max_tasks and len(pending) > max_tasks:
            pending = pending[:max_tasks]

        print(f"✅ {len(pending)}件のpendingタスクを実行")

        # 依存関係の確認
        deps_count = sum(1 for t in pending if t.get("dependencies"))
        print(f"   うち依存関係あり: {deps_count}件")

        # Gemini準備
        print("\n[2/6] Gemini接続...")
        if not await self.browser.navigate_to_gemini():
            return {"total": 0, "success": 0, "failed": 0}
        print("✅ 完了")

        # タスク実行
        print("\n[3/6] タスク実行開始...")

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

            print(f"\n{'='*70}")
            print(f"[{i}/{len(pending)}] タスク{task_id}: {role}")
            print(f"概要: {description[:60]}...")
            if dependencies:
                print(f"📌 依存: タスク{dependencies}")
            print(f"{'='*70}")

            # 依存タスクの出力を取得
            dependency_output = None
            if dependencies:
                dependency_output = await self.get_dependency_output(int(dependencies))

            # エージェント選択
            agent = self.agents.get(role)
            agent_name = self.agent_display_names.get(role, f"🤖 Gemini ({role})")

            print(f"🎯 実行: {agent_name}")

            try:
                # in_progress
                await self.sheets.update_task_status(
                    task_id=task_id, status="in_progress", sheet_name="pm_tasks"
                )

                # タスク実行（依存タスクの出力を含む）
                if agent and hasattr(agent, "execute_task"):
                    print(f"   → WordPress専門エージェント")
                    result = await agent.execute_task(task)
                    success = result.get("success", False)
                    output = result.get("output", "")
                    error = result.get("error", "")
                else:
                    print(f"   → Gemini統合")
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

                # task_execution_log に記録（正しい方法）
                await self.log_to_execution_log(
                    task_id=task_id,
                    task_description=description,
                    agent_role=role,
                    status="completed" if success else "failed",
                    output_summary=output[:100] if output else "",
                    output_data=output[:500] if output else "",
                )

                results["details"].append(
                    {"task_id": task_id, "role": role, "agent": agent_name, "success": success}
                )

                # レート制限
                if i < len(pending):
                    print(f"\n⏳ {self.rate_limit}秒待機...")
                    await asyncio.sleep(self.rate_limit)

            except Exception as e:
                print(f"❌ エラー: {e}")

                await self.sheets.update_task_status(
                    task_id=task_id, status="failed", sheet_name="pm_tasks"
                )

                await self.log_to_execution_log(
                    task_id=task_id,
                    task_description=description,
                    agent_role=role,
                    status="failed",
                    output_summary="",
                    output_data=f"エラー: {str(e)}",
                )

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

        if results["total"] > 0:
            print(f"成功率: {results['success']/results['total']*100:.1f}%")

        print("\nエージェント別:")
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
            print(f"  {agent}: {stats['success']}/{total}")

        print("=" * 70)

        return results

    async def _execute_with_gemini(
        self, task: Dict, role: str, dependency_output: Optional[str] = None
    ):
        """Gemini統合実行（依存タスクの出力を含む）"""

        task_id = task.get("task_id")
        description = task.get("description", "")

        # プロンプトに依存タスクの出力を含める
        prompt = f"""あなたは{role}の専門家です。

タスクID: {task_id}
内容: {description}
"""

        if dependency_output:
            prompt += f"""

【前提情報】
このタスクは以前のタスクの結果を元に進めます。
以下が前のタスクの出力です：

{dependency_output[:1000]}

上記の内容を踏まえて、このタスクを実行してください。
"""

        prompt += "\n具体的な成果物を日本語で作成してください。"

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
                    if dependency_output:
                        f.write(f"**前提情報あり**: 依存タスクの出力を参照\n\n")
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
    print("🎯 最終完全版統合システム")
    print("=" * 70)
    print("\n特徴:")
    print("  ✅ task_execution_log への正しい記録")
    print("  ✅ WordPressエージェント正しい統合")
    print("  ✅ dependencies活用のフィードバックループ")
    print("  ✅ aggressive モード（10秒）")

    sheets = GoogleSheetsManager(
        spreadsheet_id=get_spreadsheet_id(), service_account_file=get_service_account_file()
    )

    async with BrowserController(download_folder="./downloads") as browser:
        executor = FinalCompleteExecutor(sheets, browser)
        results = await executor.execute_all_pending(max_tasks=args.max_tasks)

    print("\n📋 完了")
    print(f"Google Sheets: https://docs.google.com/spreadsheets/d/{get_spreadsheet_id()}")
    print(f"task_execution_log シートでログ確認可能")


if __name__ == "__main__":
    asyncio.run(main())
