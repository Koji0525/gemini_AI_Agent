"""
簡易版Loop 3: 定期的に学習サイクルを実行

【何が起きた】
v26にLoop 3を統合するには6箇所以上の修正が必要

【原因】
複雑な統合作業で手動ミスのリスクが高い

【狙い】
- 別プロセスとして学習サイクルを実行
- v26への変更を最小限に抑える
- 動作確認が容易
"""

import asyncio
import time
import os
from dotenv import load_dotenv

load_dotenv()

from tools.sheets_manager import GoogleSheetsManager
from agents.self_healing.self_learning_pipeline import SelfLearningPipeline


class LearningTrigger:
    def __init__(self):
        self.sheets = GoogleSheetsManager(spreadsheet_id=os.getenv("SPREADSHEET_ID"))
        self.self_learning = SelfLearningPipeline(sheets_manager=self.sheets)
        self.last_learning_time = time.time()

    async def run(self):
        """6時間ごとに学習サイクルを実行"""
        print("🎓 Learning Trigger 起動\n")

        cycle_count = 0

        while True:
            cycle_count += 1
            elapsed = time.time() - self.last_learning_time

            print(f"\n{'='*60}")
            print(f"🔄 学習チェック #{cycle_count}")
            print(f"   前回実行から: {elapsed/3600:.1f}時間")
            print(f"{'='*60}")

            # 6時間経過したら学習実行
            if elapsed >= 21600:  # 6時間 = 21600秒
                print("\n🎓 学習サイクル実行中...")
                try:
                    await self.self_learning.run_learning_cycle()
                    print("✅ 学習サイクル完了")
                    self.last_learning_time = time.time()
                except Exception as e:
                    print(f"❌ 学習エラー: {e}")
            else:
                remaining = (21600 - elapsed) / 3600
                print(f"   次回実行まで: {remaining:.1f}時間")

            # 30分ごとにチェック

            # 標準環境変数ローダー（自動追加）import sysfrom pathlib import Pathsys.path.insert(0, str(Path(__file__).parent.parent))from tools.env_loader import StandardEnvLoaderif not StandardEnvLoader.load_and_verify():    print("環境変数の読み込みに失敗しました")    sys.exit(1)
            print("   30分後に再チェック...\n")
            await asyncio.sleep(1800)


async def main():
    trigger = LearningTrigger()
    await trigger.run()


if __name__ == "__main__":
    asyncio.run(main())
