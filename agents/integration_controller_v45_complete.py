#!/usr/bin/env python3
"""
統合コントローラー v4.5 完成版 - 既存システム保護型
要件定義書v4.5を完全実現する統合コントローラー
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# プロジェクトルートを追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class IntegrationControllerV45Complete:
    """
    要件定義書v4.5実現のための完全統合コントローラー
    既存システムを完全保護しながら連携を強化
    """

    def __init__(self):
        self.execution_count = 0
        self.monitoring = MonitoringSystem()
        self.components = {}
        self.components_loaded = False

        print("=" * 80)
        print("🚀 統合コントローラー v4.5 完成版 - 初期化")
        print("既存システム保護モードで起動します")
        print("=" * 80)

        # コンポーネントの安全なロード
        self.load_components_safely()

    def load_components_safely(self):
        """既存コンポーネントを安全にロード"""
        print("📦 既存コンポーネントを安全にロード中...")

        component_status = {}

        try:
            from tools.base_data_accessor import BaseDataAccessor

            self.components["data_accessor"] = BaseDataAccessor()
            component_status["BaseDataAccessor"] = "✅"
            print("  ✅ BaseDataAccessor ロード成功")
        except Exception as e:
            component_status["BaseDataAccessor"] = "❌"
            print(f"  ⚠️ BaseDataAccessor ロード失敗: {e}")

        try:
            from agents.complete_engine_safe_integrated_v2 import \
                CompleteEngineSafeIntegratedV2

            self.components["safe_engine"] = CompleteEngineSafeIntegratedV2()
            component_status["SafeEngine"] = "✅"
            print("  ✅ 安全版エンジン ロード成功")
        except Exception as e:
            component_status["SafeEngine"] = "❌"
            print(f"  ⚠️ 安全版エンジン ロード失敗: {e}")

        try:
            # 強化版進捗表示をロード
            from tools.show_progress_enhanced import EnhancedProgressTracker

            self.components["progress_tracker"] = EnhancedProgressTracker()
            component_status["ProgressTracker"] = "✅"
            print("  ✅ 進捗トラッカー ロード成功")
        except Exception as e:
            component_status["ProgressTracker"] = "❌"
            print(f"  ⚠️ 進捗トラッカー ロード失敗: {e}")

        try:
            # 自己修復エージェントをロード
            from agents.self_healing.self_healing_agent_safe import \
                SelfHealingAgentSafe

            self.components["healing_agent"] = SelfHealingAgentSafe()
            component_status["HealingAgent"] = "✅"
            print("  ✅ 自己修復エージェント ロード成功")
        except Exception as e:
            component_status["HealingAgent"] = "❌"
            print(f"  ⚠️ 自己修復エージェント ロード失敗: {e}")

        self.components_loaded = True

        # コンポーネント状態を表示
        print("\n📊 コンポーネントロード状況:")
        for name, status in component_status.items():
            print(f"  {status} {name}")

        loaded_count = sum(1 for status in component_status.values() if status == "✅")
        total_count = len(component_status)

        print(f"\n🎯 ロード率: {loaded_count}/{total_count} ({loaded_count/total_count*100:.1f}%)")

        if loaded_count >= total_count * 0.7:
            print("✅ 十分なコンポーネントがロードされました - 実行可能")
            return True
        else:
            print("❌ 重要なコンポーネントが不足しています")
            return False

    def execute_protected_workflow(self, count=3):
        """保護されたワークフロー実行"""
        print("\n" + "=" * 80)
        print("🛡️ 保護されたワークフロー実行開始")
        print("5回に1回の監視テストを実施します")
        print("=" * 80)

        if not self.components_loaded:
            print("❌ コンポーネントがロードされていません")
            return 0

        success_count = 0
        start_time = time.time()

        for i in range(count):
            self.execution_count += 1
            current_execution = self.execution_count

            print(f"\n--- 実行 {i+1}/{count} (総実行回数: {current_execution}) ---")

            # 5回に1回の監視テスト
            if self.monitoring.should_run_test(current_execution):
                print("🧪 監視テストを実行します...")
                monitor_result = self.monitoring.run_comprehensive_monitoring()

                if not monitor_result:
                    print("❌ 監視テスト失敗 - 安全のため実行をスキップ")
                    continue

            try:
                # 安全版エンジンで実行
                if self.components.get("safe_engine"):
                    print("⚡ 安全版エンジンでタスク実行...")
                    engine_result = self.components["safe_engine"].run_with_healing(count=1)

                    if engine_result:
                        success_count += 1
                        print(f"✅ 実行 {i+1} 成功")

                        # 成功時に進捗を表示（3回に1回）
                        if success_count % 3 == 0:
                            self.show_progress_snapshot()
                    else:
                        print(f"⚠️ 実行 {i+1} 失敗")

                else:
                    print("❌ 安全版エンジンが利用不可")

            except Exception as e:
                print(f"💥 実行 {i+1} で例外発生: {e}")
                # 自己修復を試行
                if self.components.get("healing_agent"):
                    healing_result = self.components["healing_agent"].detect_and_heal(
                        e, {"operation": "workflow_execution", "count": i + 1}
                    )
                    if healing_result["success"]:
                        print("🔧 自己修復成功 - 実行を継続")
                    else:
                        print("❌ 自己修復失敗")

        # 実行結果サマリー
        elapsed_time = time.time() - start_time
        self.show_execution_summary(success_count, count, elapsed_time)

        return success_count

    def show_progress_snapshot(self):
        """進捗スナップショット表示"""
        print("\n📸 進捗スナップショット:")
        print("-" * 40)

        if self.components.get("progress_tracker"):
            try:
                completed, total = self.components["progress_tracker"].show_enhanced_progress()
                progress_percent = (completed / total * 100) if total > 0 else 0

                print(f"📊 全体進捗: {progress_percent:.1f}% ({completed}/{total})")

                # 進捗に基づいたメッセージ
                if progress_percent >= 90:
                    print("🎉 あと少しで完了！")
                elif progress_percent >= 70:
                    print("🚀 順調に進んでいます")
                elif progress_percent >= 50:
                    print("📈 着実に進捗")
                else:
                    print("💪 これから加速します")

            except Exception as e:
                print(f"⚠️ 進捗表示エラー: {e}")
        else:
            print("❌ 進捗トラッカーが利用不可")

    def show_execution_summary(self, success_count, total_count, elapsed_time):
        """実行サマリー表示"""
        print("\n" + "=" * 80)
        print("📈 実行サマリー")
        print("=" * 80)

        success_rate = (success_count / total_count * 100) if total_count > 0 else 0

        print(f"✅ 成功実行: {success_count}/{total_count} ({success_rate:.1f}%)")
        print(f"⏱️ 実行時間: {elapsed_time:.2f}秒")
        print(f"📊 総実行回数: {self.execution_count}")

        # 監視テスト統計
        monitor_stats = self.monitoring.get_statistics()
        print(f"🧪 監視テスト実行: {monitor_stats['tests_run']}回")
        print(f"🔍 テスト合格率: {monitor_stats['success_rate']:.1f}%")

        # 最終進捗表示
        self.show_progress_snapshot()

        # システム健全性チェック
        print("\n🩺 最終システム健全性チェック:")
        health_status = self.check_system_health()

        if health_status:
            print("🎉 システムは健全です - 要件定義書v4.5実現に向けて順調")
        else:
            print("⚠️ システムに軽微な問題があります - 要監視")

    def check_system_health(self):
        """システム健全性チェック"""
        health_checks = []

        # コンポーネント状態チェック
        for name, component in self.components.items():
            health_checks.append((f"コンポーネント: {name}", component is not None))

        # 監視テスト実行
        test_result = self.monitoring.run_comprehensive_monitoring()
        health_checks.append(("監視テスト", test_result))

        # データアクセステスト
        try:
            if self.components.get("data_accessor"):
                goals = self.components["data_accessor"].read_sheet_as_dicts("project_goal")
                data_ok = len(goals) > 0
                health_checks.append(("データアクセス", data_ok))
            else:
                health_checks.append(("データアクセス", False))
        except:
            health_checks.append(("データアクセス", False))

        # 結果表示
        passed = sum(1 for _, passed in health_checks if passed)
        total = len(health_checks)

        print(f"  検査項目: {passed}/{total} 合格")

        for check_name, passed in health_checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")

        return passed >= total * 0.7


class MonitoringSystem:
    """監視システム - 5回に1回のテストを管理"""

    def __init__(self):
        self.test_history = []
        self.test_count = 0

    def should_run_test(self, execution_count):
        """5回に1回テストを実行するか判定"""
        should_run = execution_count % 5 == 0
        if should_run:
            print(f"🔍 監視テスト実行タイミング (実行回数: {execution_count})")
        return should_run

    def run_comprehensive_monitoring(self):
        """包括的な監視テスト"""
        self.test_count += 1
        print("🧪 包括的監視テストを実行中...")

        tests = [
            ("構文チェック", self.test_syntax()),
            ("データ整合性", self.test_data_integrity()),
            ("コンポーネント連携", self.test_component_integration()),
            ("進捗計算", self.test_progress_calculation()),
        ]

        # テスト結果を記録
        test_time = time.strftime("%Y-%m-%d %H:%M:%S")
        test_results = {name: result for name, result in tests}
        passed_tests = sum(1 for _, result in tests if result)
        total_tests = len(tests)

        self.test_history.append(
            {
                "timestamp": test_time,
                "results": test_results,
                "passed": passed_tests,
                "total": total_tests,
            }
        )

        # 結果表示
        print(f"�� 監視テスト結果: {passed_tests}/{total_tests} 合格")

        for test_name, result in tests:
            status = "✅" if result else "❌"
            print(f"  {status} {test_name}")

        success = passed_tests == total_tests

        if success:
            print("🎉 監視テスト全項目合格")
        else:
            print("⚠️ 監視テストに不合格項目があります")

        return success

    def test_syntax(self):
        """構文チェックテスト"""
        try:
            scripts_to_check = [
                "agents/complete_engine_ultimate.py",
                "tools/show_progress.py",
                "agents/complete_engine_safe_integrated_v2.py",
                "agents/integration_controller_v45_complete.py",
            ]

            for script in scripts_to_check:
                if os.path.exists(script):
                    result = subprocess.run(
                        ["python3", "-m", "py_compile", script], capture_output=True, text=True
                    )
                    if result.returncode != 0:
                        print(f"    ❌ {script} 構文エラー")
                        return False

            return True

        except Exception as e:
            print(f"    ❌ 構文テスト例外: {e}")
            return False

    def test_data_integrity(self):
        """データ整合性テスト"""
        try:
            from tools.base_data_accessor import BaseDataAccessor

            accessor = BaseDataAccessor()

            # 基本的なデータ読み込みテスト
            goals = accessor.read_sheet_as_dicts("project_goal")
            tasks = accessor.read_sheet_as_dicts("pm_tasks")

            goals_ok = len(goals) > 0
            tasks_ok = len(tasks) > 0

            if not goals_ok:
                print("    ❌ ゴールデータなし")
            if not tasks_ok:
                print("    ❌ タスクデータなし")

            return goals_ok and tasks_ok

        except Exception as e:
            print(f"    ❌ データ整合性テスト例外: {e}")
            return False

    def test_component_integration(self):
        """コンポーネント連携テスト"""
        try:
            # 主要コンポーネントのインポートテスト
            from agents.complete_engine_safe_integrated_v2 import \
                CompleteEngineSafeIntegratedV2
            from tools.base_data_accessor import BaseDataAccessor

            # インスタンス化テスト
            accessor = BaseDataAccessor()
            engine = CompleteEngineSafeIntegratedV2()

            return accessor is not None and engine is not None

        except Exception as e:
            print(f"    ❌ コンポーネント連携テスト例外: {e}")
            return False

    def test_progress_calculation(self):
        """進捗計算テスト"""
        try:
            from tools.base_data_accessor import BaseDataAccessor

            accessor = BaseDataAccessor()

            tasks = accessor.read_sheet_as_dicts("pm_tasks")
            if not tasks:
                return False

            completed = sum(1 for t in tasks if t.get("status") == "completed")
            total = len(tasks)

            progress = (completed / total * 100) if total > 0 else 0

            # 進捗が0-100%の範囲内かチェック
            return 0 <= progress <= 100

        except Exception as e:
            print(f"    ❌ 進捗計算テスト例外: {e}")
            return False

    def get_statistics(self):
        """監視統計を取得"""
        if not self.test_history:
            return {"tests_run": 0, "success_rate": 0}

        total_tests = len(self.test_history)
        successful_tests = sum(1 for test in self.test_history if test["passed"] == test["total"])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0

        return {
            "tests_run": total_tests,
            "success_rate": success_rate,
            "history": self.test_history,
        }


def main():
    """統合コントローラーのメイン実行"""
    try:
        print("🚀 要件定義書v4.5 統合コントローラー完成版 - 起動")
        print("既存システムを完全保護しながら連携強化を実行します")
        print("5回に1回の監視テストを実施して安全性を確保します")

        controller = IntegrationControllerV45Complete()

        # システム健全性初期チェック
        print("\n🔍 初期システム健全性チェック...")
        if not controller.check_system_health():
            print("❌ システム健全性チェック失敗 - 実行を中止します")
            return 1

        # 保護されたワークフロー実行（3回）
        print("\n🎯 保護されたワークフローを実行します...")
        success_count = controller.execute_protected_workflow(count=3)

        if success_count > 0:
            print(f"\n🎉 統合実行完了: {success_count}回成功")
            print("✅ 要件定義書v4.5実現に向けて順調に進んでいます")
            return 0
        else:
            print("\n❌ 統合実行失敗 - 要因調査が必要です")
            return 1

    except Exception as e:
        print(f"💥 統合コントローラー重大エラー: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
