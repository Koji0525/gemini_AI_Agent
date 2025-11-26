"""
Mock環境耐久テスト

認証情報なしで耐久テストを実施し、
統合アダプターの安定性を確認する。

用途:
- 認証設定前の動作確認
- ローカル環境でのテスト
- CI/CD環境での自動テスト
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from agents.integration.complete_engine_adapter import CompleteEngineAdapter


class MockEnduranceTest:
    """Mock環境耐久テスト"""

    def __init__(self, cycles: int = 24, interval_sec: int = 60):
        """
        Args:
            cycles: サイクル数（デフォルト24回）
            interval_sec: 実行間隔（秒、デフォルト60秒）
        """
        self.cycles = cycles
        self.interval_sec = interval_sec
        self.results = []

        # 統合アダプター初期化（Mockモード）
        print("🔧 統合アダプター初期化（Mockモード）...")
        self.adapter = CompleteEngineAdapter(enable_v2=True, mock_mode=True)
        print("✅ 初期化完了")
        print()

    def run_cycle(self, cycle_num: int) -> dict:
        """
        1サイクル実行

        Args:
            cycle_num: サイクル番号

        Returns:
            実行結果
        """
        start_time = datetime.now()

        try:
            # V2方式でゴール実行（Mock）
            result = self.adapter.execute_goal_v2(
                goal_id=f"mock_goal_{cycle_num:03d}", mode="hierarchical", mock=True
            )

            end_time = datetime.now()
            elapsed = (end_time - start_time).total_seconds()

            return {
                "cycle": cycle_num,
                "success": result.get("success", False),
                "elapsed_sec": elapsed,
                "timestamp": start_time.isoformat(),
                "error": None,
            }

        except Exception as e:
            end_time = datetime.now()
            elapsed = (end_time - start_time).total_seconds()

            return {
                "cycle": cycle_num,
                "success": False,
                "elapsed_sec": elapsed,
                "timestamp": start_time.isoformat(),
                "error": str(e),
            }

    def run(self):
        """耐久テスト実行"""
        print("=" * 80)
        print("Mock環境耐久テスト開始")
        print("=" * 80)
        print(f"サイクル数: {self.cycles}")
        print(f"実行間隔: {self.interval_sec}秒")
        print(f"予想所要時間: {self.cycles * self.interval_sec / 60:.1f}分")
        print("=" * 80)
        print()

        for cycle in range(1, self.cycles + 1):
            print(
                f"[サイクル {cycle}/{self.cycles}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            print("-" * 80)

            # 1サイクル実行
            result = self.run_cycle(cycle)
            self.results.append(result)

            # 結果表示
            if result["success"]:
                print(f"✅ 成功 ({result['elapsed_sec']:.2f}秒)")
            else:
                print(f"❌ 失敗: {result['error']}")

            print()

            # 最終サイクル以外は待機
            if cycle < self.cycles:
                print(f"⏳ 次のサイクルまで{self.interval_sec}秒待機...")
                print()
                time.sleep(self.interval_sec)

        # 結果サマリー
        self.print_summary()

        # 結果保存
        self.save_results()

    def print_summary(self):
        """結果サマリー表示"""
        print("=" * 80)
        print("耐久テスト結果サマリー")
        print("=" * 80)

        success_count = sum(1 for r in self.results if r["success"])
        total_count = len(self.results)
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0

        avg_elapsed = sum(r["elapsed_sec"] for r in self.results) / total_count

        print(f"総サイクル数: {total_count}")
        print(f"成功: {success_count}")
        print(f"失敗: {total_count - success_count}")
        print(f"成功率: {success_rate:.1f}%")
        print(f"平均実行時間: {avg_elapsed:.2f}秒")
        print()

        # エラーサマリー
        errors = [r for r in self.results if not r["success"]]
        if errors:
            print("エラー詳細:")
            for err in errors:
                print(f"  サイクル{err['cycle']}: {err['error']}")
        else:
            print("✅ エラーなし")

        print("=" * 80)

    def save_results(self):
        """結果をJSONファイルに保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs/mock_endurance_{timestamp}.json"

        # logsディレクトリ作成
        Path("logs").mkdir(exist_ok=True)

        # 結果保存
        result_data = {
            "test_type": "mock_endurance",
            "cycles": self.cycles,
            "interval_sec": self.interval_sec,
            "start_time": self.results[0]["timestamp"] if self.results else None,
            "end_time": self.results[-1]["timestamp"] if self.results else None,
            "results": self.results,
            "summary": {
                "total": len(self.results),
                "success": sum(1 for r in self.results if r["success"]),
                "failure": sum(1 for r in self.results if not r["success"]),
                "success_rate": (
                    sum(1 for r in self.results if r["success"]) / len(self.results) * 100
                    if self.results
                    else 0
                ),
            },
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)

        print(f"✅ 結果保存: {filename}")


def main():
    """メイン関数"""
    import argparse

    parser = argparse.ArgumentParser(description="Mock環境耐久テスト")
    parser.add_argument("--cycles", type=int, default=24, help="サイクル数（デフォルト: 24）")
    parser.add_argument("--interval", type=int, default=60, help="実行間隔（秒、デフォルト: 60）")

    args = parser.parse_args()

    # テスト実行
    tester = MockEnduranceTest(cycles=args.cycles, interval_sec=args.interval)
    tester.run()


if __name__ == "__main__":
    main()
