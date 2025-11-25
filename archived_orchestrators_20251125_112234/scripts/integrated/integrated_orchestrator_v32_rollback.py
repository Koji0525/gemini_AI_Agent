"""
Integrated Orchestrator v32 - Rollback Edition
Phase 2 Week 3 Day 4: ロールバック機能統合

既存のv32 Decision Support版を継承し、ロールバック機能を追加
既存ファイルは一切変更しない
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# プロジェクトルート追加
sys.path.insert(0, str(Path(__file__).parent.parent))

# 相対インポートを使用して修正
try:
    from integrated_orchestrator_v32_decision_support import \
        IntegratedOrchestratorV32DecisionSupport
except ImportError:
    # フォールバック: 直接インポート
    try:
        from scripts.integrated.integrated_orchestrator_v32_decision_support import \
            IntegratedOrchestratorV32DecisionSupport
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        sys.exit(1)


class IntegratedOrchestratorV32Rollback(IntegratedOrchestratorV32DecisionSupport):
    """
    Phase 2 Week 3 Day 4: ロールバック機能統合版

    既存のv32 Decision Support版を継承し、ロールバック機能を追加
    既存機能は一切変更せずに新機能を追加
    """

    VERSION = "v32.2.0-rollback"

    def __init__(self):
        """
        初期化
        既存のv32 Decision Support初期化処理を呼び出し、ロールバック機能を追加
        """
        # 親クラスの初期化（既存機能）
        try:
            super().__init__()
            print(f"✅ v32 Decision Support親クラス初期化完了")
        except Exception as e:
            print(f"⚠️  v32 Decision Support親クラス初期化失敗: {e}")
            # フォールバック初期化
            self._initialize_components_fallback()

        # ロールバック機能の初期化
        self.rollback_manager = self._initialize_rollback_manager()
        self.backup_states = []
        self.max_backups = 5  # 保持するバックアップ数

        print(f"✅ IntegratedOrchestrator {self.VERSION} 初期化完了")

    def _initialize_rollback_manager(self):
        """
        ロールバックマネージャーの初期化
        """
        try:
            # ロールバックエージェントのインポート試行
            from agents.rollback_agent import RollbackAgent

            rollback_manager = RollbackAgent()
            print("✅ RollbackAgent 初期化完了")
            return rollback_manager
        except ImportError as e:
            print(f"⚠️  RollbackAgent インポート不可: {e}")
            # モック実装で代替
            return self._create_mock_rollback_manager()
        except Exception as e:
            print(f"⚠️  RollbackAgent 初期化エラー: {e}")
            return self._create_mock_rollback_manager()

    def _create_mock_rollback_manager(self):
        """
        ロールバックマネージャーのモック実装
        """

        class MockRollbackManager:
            def __init__(self):
                self.rollback_count = 0
                self.backups = []

            async def create_backup(self, state_data):
                """バックアップ作成のモック"""
                backup_id = f"backup_{len(self.backups) + 1}"
                self.backups.append(
                    {"id": backup_id, "timestamp": datetime.now().isoformat(), "data": state_data}
                )
                return backup_id

            async def perform_rollback(self, backup_id):
                """ロールバック実行のモック"""
                self.rollback_count += 1
                backup = next((b for b in self.backups if b["id"] == backup_id), None)
                if backup:
                    return {
                        "success": True,
                        "backup_id": backup_id,
                        "rollback_count": self.rollback_count,
                    }
                return {"success": False, "error": "Backup not found"}

            async def get_available_backups(self):
                """利用可能なバックアップ一覧のモック"""
                return self.backups

        print("✅ MockRollbackManager 作成完了")
        return MockRollbackManager()

    async def run_continuous_cycle(self, duration: int = None, single_cycle: bool = False):
        """
        連続実行サイクル（ロールバック機能統合版）
        """
        self.start_time = datetime.now()

        print("=" * 70)
        print(f"🚀 {self.VERSION} 起動 - ロールバック機能統合")
        print("=" * 70)
        print(f"開始時刻: {self.start_time}")
        print(f"実行モード: {'シングルサイクル' if single_cycle else '連続実行'}")
        if duration:
            print(f"実行時間: {duration}秒")
        print("=" * 70)

        try:
            # サイクル開始前に状態をバックアップ
            await self._create_state_backup()

            # 親クラスのメソッドを使用
            await super().run_continuous_cycle(duration, single_cycle)

        except Exception as e:
            print(f"❌ 実行エラー: {e}")
            # ロールバック機能を使用して復旧試行
            recovery_success = await self._attempt_recovery(e)
            if not recovery_success:
                print("❌ 自動復旧失敗 - 手動介入が必要です")
            raise

        finally:
            self._print_rollback_stats()

    async def _create_state_backup(self):
        """
        現在の状態をバックアップ
        """
        try:
            state_data = {
                "cycle_count": getattr(self, "cycle_count", 0),
                "timestamp": datetime.now().isoformat(),
                "version": self.VERSION,
            }

            backup_id = await self.rollback_manager.create_backup(state_data)

            # バックアップリストを管理（古いものは削除）
            self.backup_states.append(backup_id)
            if len(self.backup_states) > self.max_backups:
                removed = self.backup_states.pop(0)
                print(f"🔄 古いバックアップを削除: {removed}")

            print(f"✅ 状態バックアップ作成: {backup_id}")

        except Exception as e:
            print(f"⚠️  バックアップ作成エラー: {e}")

    async def _attempt_recovery(self, error):
        """
        エラー発生時の復旧試行
        """
        try:
            print("🔄 自動復旧を試行中...")

            # DecisionSupportSystemを使用して復旧方法を決定
            error_context = {
                "error_type": type(error).__name__,
                "error_message": str(error),
                "timestamp": datetime.now().isoformat(),
                "recovery_attempt": True,
            }

            if hasattr(self, "decision_support"):
                recommendation = await self.decision_support.get_recommendation(error_context)
                print(f"🔍 復旧推奨: {recommendation}")

                if recommendation.get("recommendation") == "rollback" and self.backup_states:
                    # 最新のバックアップにロールバック
                    latest_backup = self.backup_states[-1]
                    rollback_result = await self.rollback_manager.perform_rollback(latest_backup)

                    if rollback_result.get("success"):
                        print(f"✅ ロールバック成功: {latest_backup}")
                        return True

            print("⚠️  ロールバック不要またはバックアップなし")
            return False

        except Exception as recovery_error:
            print(f"❌ 復旧試行エラー: {recovery_error}")
            return False

    def _print_rollback_stats(self):
        """ロールバック統計表示"""
        if not self.start_time:
            return

        elapsed = (datetime.now() - self.start_time).total_seconds()

        print("\n" + "=" * 70)
        print("📊 ロールバック統計")
        print("=" * 70)
        print(f"実行時間: {elapsed:.0f}秒 ({elapsed/3600:.2f}時間)")
        print(f"総サイクル数: {self.cycle_count}")

        # ロールバック統計
        if hasattr(self, "rollback_manager"):
            rollback_count = getattr(self.rollback_manager, "rollback_count", 0)
            backup_count = len(getattr(self.rollback_manager, "backups", []))
            print(f"ロールバック回数: {rollback_count}")
            print(f"バックアップ数: {backup_count}")

        print("=" * 70)

    async def get_rollback_stats(self):
        """
        ロールバック統計を取得
        """
        stats = {
            "version": self.VERSION,
            "cycle_count": getattr(self, "cycle_count", 0),
            "rollback_available": hasattr(self, "rollback_manager")
            and self.rollback_manager is not None,
            "backup_count": len(self.backup_states),
        }

        if stats["rollback_available"]:
            stats["rollback_count"] = getattr(self.rollback_manager, "rollback_count", 0)
            stats["total_backups"] = len(getattr(self.rollback_manager, "backups", []))

        return stats


async def main():
    """メイン実行"""
    orchestrator = IntegratedOrchestratorV32Rollback()

    # 引数処理
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--single":
            await orchestrator.run_continuous_cycle(single_cycle=True)
        else:
            duration = int(sys.argv[1])
            await orchestrator.run_continuous_cycle(duration=duration)
    else:
        await orchestrator.run_continuous_cycle()


if __name__ == "__main__":
    asyncio.run(main())
