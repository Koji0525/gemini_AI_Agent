#!/usr/bin/env python3
"""
ハイブリッドストレージシステム（パス修正版）
"""
import asyncio
import hashlib
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

# WordPressエージェント
try:
    from wordpress.wp_agent import WordPressAgent

    HAS_WP_AGENT = True
except:
    HAS_WP_AGENT = False


class HybridStorageExecutor:
    """ハイブリッドストレージシステム（修正版）"""

    def __init__(self, sheets_manager, browser_controller):
        self.sheets = sheets_manager
        self.browser = browser_controller

        # GitHubストレージ（絶対パス）
        self.github_storage = Path("/workspaces/gemini_AI_Agent/agent_outputs/tasks")
        self.github_storage.mkdir(parents=True, exist_ok=True)

        self.rate_limit = 10

        # エージェント初期化
        self.agents = {}
        self._initialize_agents()

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

    def _generate_file_hash(self, content: str) -> str:
        """ファイルハッシュ生成"""
        return hashlib.sha256(content.encode()).hexdigest()[:8]

    async def save_output_hybrid(
        self, task_id: int, task_description: str, agent_role: str, full_output: str, status: str
    ) -> Dict[str, str]:
        """ハイブリッド保存（修正版）"""

        print(f"\n   💾 ハイブリッド保存開始...")

        result = {
            "github_path": "",
            "sheets_log_id": "",
            "output_hash": "",
            "output_length": len(full_output),
        }

        # [1] GitHub保存
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"task_{task_id}_{agent_role}_{timestamp}.md"
            filepath = self.github_storage / filename

            # ファイル内容
            content = f"""# タスク {task_id}: {agent_role}

**概要**: {task_description}

**ステータス**: {status}

**生成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**文字数**: {len(full_output):,}

---

{full_output}
"""

            # ファイル保存
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            # 相対パス（修正版）
            relative_path = f"agent_outputs/tasks/{filename}"

            result["github_path"] = relative_path
            result["output_hash"] = self._generate_file_hash(full_output)

            print(f"      ✅ GitHub: {filename}")
            print(f"         パス: {relative_path}")
            print(f"         サイズ: {len(full_output):,}文字")

        except Exception as e:
            print(f"      ❌ GitHub保存エラー: {e}")
            import traceback

            traceback.print_exc()

        # [2] Sheets保存
        try:
            spreadsheet = self.sheets.gc.open_by_key(get_spreadsheet_id())
            log_sheet = spreadsheet.worksheet("task_execution_log")

            all_data = log_sheet.get_all_values()
            next_log_id = len(all_data)

            # サマリー生成
            if len(full_output) > 200:
                summary = f"{full_output[:100]}...\n\n[中略 {len(full_output)-200}文字]\n\n...{full_output[-100:]}"
            else:
                summary = full_output

            # output_data列の内容
            output_data_content = f"""📁 GitHub: {result['github_path']}

📊 メタデータ:
- 文字数: {len(full_output):,}
- ハッシュ: {result['output_hash']}
- 生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📝 サマリー:
{summary[:200]}
"""

            row = [
                next_log_id,  # log_id
                task_id,  # task_id
                task_description[:100],  # task_description
                datetime.now().isoformat(),  # timestamp
                agent_role,  # agent_role
                summary[:100],  # output_summary
                output_data_content[:500],  # output_data
                status,  # status
            ]

            log_sheet.append_rows(row)

            result["sheets_log_id"] = str(next_log_id)

            print(f"      ✅ Sheets: log_id {next_log_id}")

        except Exception as e:
            print(f"      ❌ Sheets保存エラー: {e}")
            import traceback

            traceback.print_exc()

        print(f"   ✅ ハイブリッド保存完了")

        return result

    async def get_dependency_output(self, dependency_task_id: int) -> Optional[str]:
        """依存タスクの出力取得（GitHub優先）"""

        try:
            # [1] SheetsからGitHubパスを取得
            spreadsheet = self.sheets.gc.open_by_key(get_spreadsheet_id())
            log_sheet = spreadsheet.worksheet("task_execution_log")

            all_data = log_sheet.get_all_values()

            github_path = None
            for row in reversed(all_data[1:]):
                if len(row) > 1 and str(row[1]) == str(dependency_task_id):
                    output_data = row[6] if len(row) > 6 else ""

                    # GitHubパスを抽出
                    if "GitHub:" in output_data:
                        lines = output_data.split("\n")
                        for line in lines:
                            if "GitHub:" in line:
                                github_path = line.split("GitHub:")[-1].strip()
                                # 📁 などの絵文字を除去
                                github_path = github_path.replace("📁", "").strip()
                                break
                    break

            # [2] GitHubファイルから完全な出力を読み込み
            if github_path:
                full_path = Path("/workspaces/gemini_AI_Agent") / github_path

                if full_path.exists():
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # マークダウンヘッダーを除去して本文のみ取得
                    if "---" in content:
                        parts = content.split("---", 2)
                        if len(parts) > 2:
                            content = parts[2].strip()

                    print(f"   📥 依存タスク{dependency_task_id}の完全な出力取得")
                    print(f"      GitHub: {github_path}")
                    print(f"      文字数: {len(content):,}")

                    return content
                else:
                    print(f"   ⚠️  GitHubファイルが見つかりません: {github_path}")

            # [3] Sheetsフォールバック
            print(f"   📥 依存タスク{dependency_task_id}（Sheetsから取得）")

            for row in reversed(all_data[1:]):
                if len(row) > 1 and str(row[1]) == str(dependency_task_id):
                    output_summary = row[5] if len(row) > 5 else ""
                    output_data = row[6] if len(row) > 6 else ""

                    return f"{output_summary}\n\n{output_data}"

            return None

        except Exception as e:
            print(f"   ❌ 依存タスク取得エラー: {e}")
            import traceback

            traceback.print_exc()
            return None

    async def execute_all_pending(self, max_tasks: Optional[int] = None) -> Dict:
        """タスク実行（ハイブリッドストレージ）"""

        print("\n" + "=" * 70)
        print("🚀 ハイブリッドストレージシステム起動（修正版）")
        print("=" * 70)

        # タスク読み込み
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

        print(f"✅ {len(pending)}件のpendingタスク")

        # Gemini準備
        print("\n[2/5] Gemini接続...")
        if not await self.browser.navigate_to_gemini():
            return {"total": 0, "success": 0, "failed": 0}
        print("✅ 完了")

        # タスク実行
        print("\n[3/5] タスク実行開始...")

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

                # ハイブリッド保存
                save_result = await self.save_output_hybrid(
                    task_id=task_id,
                    task_description=description,
                    agent_role=role,
                    full_output=output if output else "",
                    status="completed" if success else "failed",
                )

                results["details"].append(
                    {
                        "task_id": task_id,
                        "role": role,
                        "success": success,
                        "github_path": save_result.get("github_path", ""),
                        "output_length": save_result.get("output_length", 0),
                    }
                )

                # レート制限
                if i < len(pending):
                    print(f"\n⏳ {self.rate_limit}秒待機...")
                    await asyncio.sleep(self.rate_limit)

            except Exception as e:
                print(f"❌ エラー: {e}")
                import traceback

                traceback.print_exc()
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

        print(f"\n💾 保存詳細:")
        total_chars = sum(d.get("output_length", 0) for d in results["details"])
        print(f"   総文字数: {total_chars:,}文字")
        print(f"   GitHub: /workspaces/gemini_AI_Agent/agent_outputs/tasks/")
        print(f"   Sheets: task_execution_log（サマリー + GitHub参照）")

        print("\n📁 保存されたファイル:")
        for detail in results["details"]:
            if detail.get("github_path"):
                print(f"   - {detail['github_path']} ({detail['output_length']:,}文字)")

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
"""

        if dependency_output:
            prompt += f"""

【前提情報】
前のタスクの出力（最初の2000文字）:
{dependency_output[:2000]}

上記を踏まえて実行してください。
"""

        prompt += "\n具体的な成果物を作成してください。"

        try:
            await self.browser.send_prompt(prompt)
            await self.browser.wait_for_text_generation(max_wait=120)
            response = await self.browser.extract_latest_text_response()

            if response and len(response) > 100:
                print(f"   ✅ {len(response):,}文字生成")

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
    print("🎯 ハイブリッドストレージシステム（修正版）")
    print("=" * 70)
    print("\n保存戦略:")
    print("  📁 GitHub: 完全な出力（制限なし）")
    print("  📊 Sheets: サマリー + GitHub参照リンク")

    sheets = GoogleSheetsManager(
        spreadsheet_id=get_spreadsheet_id(), service_account_file=get_service_account_file()
    )

    async with BrowserController(download_folder="./downloads") as browser:
        executor = HybridStorageExecutor(sheets, browser)
        results = await executor.execute_all_pending(max_tasks=args.max_tasks)

    print("\n📋 完了")
    print(f"Google Sheets: https://docs.google.com/spreadsheets/d/{get_spreadsheet_id()}")
    print(f"GitHub出力: agent_outputs/tasks/")


if __name__ == "__main__":
    asyncio.run(main())
