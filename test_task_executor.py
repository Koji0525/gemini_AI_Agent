#!/usr/bin/env python3
"""TaskExecutor 動作確認"""

import asyncio
import sys

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from tools.sheets_manager import GoogleSheetsManager
from task_executor import MVPTaskExecutor


async def main():
    print("🧪 TaskExecutor 動作確認")
    print("=" * 60)

    # 初期化
    sheets = GoogleSheetsManager()
    executor = MVPTaskExecutor(sheets)

    # 1回だけテスト実行
    await executor.run_task_loop(max_iterations=1)

    print("✅ Phase 2 完了: TaskExecutor統合")


if __name__ == "__main__":
    asyncio.run(main())
