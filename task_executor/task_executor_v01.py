#!/usr/bin/env python3
"""
TaskExecutor v01 - タスク実行のオーケストレーター

P0-1: タスク実行時間の計測機能追加
- elapsed_time: タスク実行時間（秒）
- retry_count: リトライ回数
- error_type: エラー分類
- fix_applied: 自動修復フラグ

Google Sheets → Gemini → 結果保存 → Sheets更新
の全フローを管理
"""
import asyncio
import sys
import time  # ← 追加
from pathlib import Path
from typing import Dict
from datetime import datetime

# パス設定
sys.path.insert(0, str(Path(__file__).parent.parent))

from browser_control.browser_controller import BrowserController
from browser_control.rate_limiter import RateLimiter
from browser_control.error_recovery import ErrorRecovery
from tools.sheets_manager import GoogleSheetsManager


class TaskExecutor:
    """
    タスク実行を統括するクラス
    """

    def __init__(self, sheets_manager: GoogleSheetsManager, output_dir: str = "agent_outputs"):
        self.sheets_manager = sheets_manager
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # レート制限
        self.rate_limiter = RateLimiter(max_requests_per_hour=50, min_interval_seconds=30)

        # エラーリカバリー
        self.error_recovery = ErrorRecovery(max_retries=3)

    async def execute_single_task(self, browser: BrowserController, task: Dict) -> bool:
        """
        単一タスクを実行

        Args:
            browser: BrowserController インスタンス
            task: タスク情報

        Returns:
            bool: 成功したかどうか
        """
        task_id = task.get("id", "unknown")
        title = task.get("title", "No Title")
        prompt = task.get("prompt", "")

        # ✅ P0-1: 実行時間計測開始
        task_start = time.time()
        retry_count = task.get("retry_count", 0)  # リトライ回数を引き継ぐ

        print(f"\n🎯 タスク: {title}")
        print(f"   ID: {task_id}")
        print(f"   プロンプト: {prompt[:100]}...")

        try:
            # ステータスを「実行中」に更新
            self.sheets_manager.update_task_status(task_id=task_id, status="in_progress")

            # プロンプト送信
            print("\n📤 プロンプト送信中...")
            await browser.send_prompt(prompt)

            # レスポンス待機
            print("⏳ レスポンス生成待機中...")
            await browser.wait_for_text_generation(max_wait=120)

            # レスポンス取得
            print("📥 レスポンス取得中...")
            response = await browser.extract_latest_text_response()

            if not response or len(response) < 50:
                raise Exception(f"レスポンスが短すぎます: {len(response) if response else 0} 文字")

            print(f"✅ レスポンス取得成功: {len(response)} 文字")

            # ✅ P0-1: 実行時間計算
            elapsed_time = round(time.time() - task_start, 2)

            # ファイル保存
            output_file = self.save_result(task_id, title, response)
            print(f"💾 保存: {output_file}")

            # 成功ステータスに更新（✅ 計測データを追加）
            self.sheets_manager.update_task_status(
                task_id=task_id,
                status="completed",
                result={
                    "summary": f"{len(response)}文字のレスポンスを取得",
                    "length": len(response),
                },
                output_file=str(output_file),
                # ✅ P0-1: 計測データ
                elapsed_time=elapsed_time,
                retry_count=retry_count,
                error_type=None,
                fix_applied=False,
            )

            print(f"✅ タスク完了: {title} (実行時間: {elapsed_time}秒)")
            return True

        except Exception as e:
            # ✅ P0-1: 失敗時も実行時間を記録
            elapsed_time = round(time.time() - task_start, 2)
            error_type = type(e).__name__

            print(f"❌ タスク失敗: {e}")

            # 失敗ステータスに更新（✅ 計測データを追加）
            self.sheets_manager.update_task_status(
                task_id=task_id,
                status="failed",
                error_message=str(e),
                # ✅ P0-1: 計測データ
                elapsed_time=elapsed_time,
                retry_count=retry_count,
                error_type=error_type,
                fix_applied=False,
            )

            return False

    def save_result(self, task_id: str, title: str, content: str) -> Path:
        """
        結果をファイルに保存

        Args:
            task_id: タスクID
            title: タイトル
            content: 内容

        Returns:
            保存先のPath
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{task_id}_{timestamp}.md"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write(f"**タスクID**: {task_id}\n")
            f.write(f"**生成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**文字数**: {len(content)}\n\n")
            f.write("---\n\n")
            f.write(content)

        return filepath


async def main():
    """
    メイン実行関数
    """
    print("\n🚀 TaskExecutor v01 起動")

    # SheetsManager初期化
    sheets_manager = GoogleSheetsManager(
        service_account_file="configuration/service_account.json",
        spreadsheet_id="YOUR_SPREADSHEET_ID",  # 環境変数または設定ファイルから読み込む
    )

    # TaskExecutor初期化
    executor = TaskExecutor(sheets_manager=sheets_manager, output_dir="agent_outputs")

    # すべての未実行タスクを実行
    await executor.execute_all_pending_tasks()

    print("\n✅ すべての処理が完了しました")


if __name__ == "__main__":
    asyncio.run(main())
