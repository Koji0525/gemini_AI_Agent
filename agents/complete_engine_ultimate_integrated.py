#!/usr/bin/env python3
"""
CompleteEngineUltimate + SelfHealingAgent 統合版（修正版）
既存のCompleteEngineUltimateを継承して自己修復機能を追加
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 既存のCompleteEngineUltimateをインポート
try:
    from agents.complete_engine_ultimate import CompleteEngineUltimate
except ImportError:
    print("❌ CompleteEngineUltimate が見つかりません。既存の実装を確認してください。")
    sys.exit(1)

from agents.self_healing.self_healing_agent import SelfHealingAgent


class CompleteEngineUltimateIntegrated(CompleteEngineUltimate):
    """
    CompleteEngineUltimate + SelfHealingAgent 統合クラス
    既存のCompleteEngineUltimateを継承し、自己修復機能を追加
    """

    def __init__(self, sheets_manager=None):
        # 既存のCompleteEngineUltimateの初期化を実行
        super().__init__(sheets_manager)

        # 🆕 新規: 自己修復エージェントの統合
        self.self_healing_agent = SelfHealingAgent()

        print("✅ CompleteEngineUltimate + SelfHealingAgent 統合完了")

    def execute_task_with_healing(self, task):
        """
        タスク実行（自己修復機能付き）
        既存のexecute_taskをラップして修復機能を追加
        """
        print(f"\n🔧 タスク実行開始（自己修復モード）: {task.get('description', 'N/A')}")

        try:
            # 既存のexecute_taskを呼び出し（既存機能を維持）
            result = self.execute_task(task)

            print("✅ タスク正常完了")
            return result

        except Exception as e:
            print(f"⚠️ タスク実行エラー: {type(e).__name__}: {e}")

            # 🆕 新規: 自己修復の実行
            healing_context = {
                "task": task,
                "func": self.execute_task,  # 再実行する関数
                "args": [task],  # 関数の引数
                "kwargs": {},  # キーワード引数
            }

            healing_result = self.self_healing_agent.detect_and_heal(e, healing_context)

            if healing_result["success"]:
                print("🎉 自己修復成功！タスクを完了しました")
                return healing_result.get("result", {"status": "healed"})
            else:
                print("💥 自己修復失敗。タスクを中断します")
                # 既存のエラーハンドリングに委譲
                raise

    def run_with_healing(self, count=1):
        """
        メイン実行ループ（自己修復機能付き）
        既存のrunメソッドを拡張
        """
        print("=" * 80)
        print("🚀 CompleteEngine Ultimate - 自己修復モード起動")
        print("=" * 80)

        try:
            # 既存のゴール選択ロジックを使用
            goal_id = self.select_goal()
            if not goal_id:
                print("❌ 実行対象のゴールが見つかりません")
                return

            print(f"🎯 対象ゴール: {goal_id}")

            # タスク実行ループ
            for i in range(count):
                print(f"\n--- 実行 {i+1}/{count} ---")

                # タスク取得（既存ロジック）
                task = self.get_next_pending_task(goal_id)
                if not task:
                    print("⏸️ 実行対象のタスクがありません")
                    break

                # 🆕 新規: 自己修復付きタスク実行
                result = self.execute_task_with_healing(task)

                # 既存の結果処理ロジック
                self.process_execution_result(task, result)

            # 🆕 新規: 修復統計の表示
            self.show_healing_stats()

        except Exception as e:
            print(f"💥 システムエラー: {e}")
            # 🆕 新規: システムレベルの自己修復を試行
            self.try_system_level_healing(e)

    def show_healing_stats(self):
        """修復統計の表示"""
        stats = self.self_healing_agent.get_statistics()

        print("\n" + "=" * 80)
        print("📊 自己修復統計")
        print("=" * 80)
        print(f"総エラー数: {stats['total_errors']}")
        print(f"修復成功: {stats['healed_errors']}")
        print(f"修復失敗: {stats['failed_heals']}")
        print(f"修復成功率: {stats['healing_rate']:.1f}%")

        if stats["by_type"]:
            print("\nエラータイプ別:")
            for error_type, count in stats["by_type"].items():
                print(f"  {error_type}: {count}件")

    def try_system_level_healing(self, error):
        """システムレベルの修復試行"""
        print(f"\n🛠️ システムレベル修復を試行: {error}")

        # 簡易的なシステム修復ロジック
        system_context = {"error": str(error), "component": "CompleteEngine", "timestamp": "now"}

        # システムエラーとして修復試行
        healing_result = self.self_healing_agent.detect_and_heal(error, system_context)

        if healing_result["success"]:
            print("✅ システムレベル修復成功")
        else:
            print("❌ システムレベル修復失敗 - 要人間介入")


def main():
    """統合版のメイン実行"""
    try:
        engine = CompleteEngineUltimateIntegrated()

        # テスト実行
        print("🧪 統合テスト実行")
        engine.run_with_healing(count=1)

    except Exception as e:
        print(f"❌ 統合テスト失敗: {e}")
        print("\n💡 トラブルシューティング:")
        print("1. 既存のCompleteEngineUltimateが動作するか確認:")
        print("   python3 agents/complete_engine_ultimate.py --count 1")
        print("2. SelfHealingAgent単体テスト:")
        print("   python3 agents/self_healing/self_healing_agent.py")


if __name__ == "__main__":
    main()
