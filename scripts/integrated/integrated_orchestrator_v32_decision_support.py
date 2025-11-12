"""
Integrated Orchestrator v32 - Decision Support Edition
Phase 2 Week 3 Day 3: DecisionSupportSystem統合

既存のv32エラー処理版を継承し、DecisionSupportSystemを追加
既存ファイルは一切変更しない
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# プロジェクトルート追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.integrated.integrated_orchestrator_v32_error_handling import (
    IntegratedOrchestratorV32ErrorHandling,
)


class IntegratedOrchestratorV32DecisionSupport(IntegratedOrchestratorV32ErrorHandling):
    """
    Phase 2 Week 3 Day 3: DecisionSupportSystem統合版

    既存のv32エラー処理版を継承し、DecisionSupportSystemを追加
    既存機能は一切変更せずに新機能を追加
    """

    VERSION = "v32.1.0-decision-support"

    def __init__(self):
        """
        初期化
        既存のv32初期化処理を呼び出し、DecisionSupportSystemを追加
        """
        # 親クラスの初期化（既存機能）
        try:
            super().__init__()
            print(f"✅ v32親クラス初期化完了")
        except Exception as e:
            print(f"⚠️  v32親クラス初期化失敗: {e}")
            # フォールバック初期化
            self._initialize_components_fallback()

        # DecisionSupportSystemの初期化
        self.decision_support = self._initialize_decision_support()

        print(f"✅ IntegratedOrchestrator {self.VERSION} 初期化完了")

    def _initialize_decision_support(self):
        """
        DecisionSupportSystemの初期化
        """
        try:
            # DecisionSupportSystemのインポート試行
            from agents.self_healing.logging.decision_support_system import DecisionSupportSystem

            dss = DecisionSupportSystem()
            print("✅ DecisionSupportSystem 初期化完了")
            return dss
        except ImportError as e:
            print(f"⚠️  DecisionSupportSystem インポート不可: {e}")
            # モック実装で代替
            return self._create_mock_decision_support()
        except Exception as e:
            print(f"⚠️  DecisionSupportSystem 初期化エラー: {e}")
            return self._create_mock_decision_support()

    def _create_mock_decision_support(self):
        """
        DecisionSupportSystemのモック実装
        実際の実装が利用できない場合の代替
        """

        class MockDecisionSupportSystem:
            def __init__(self):
                self.initialized = True
                self.decision_count = 0

            async def analyze_situation(self, context):
                """状況分析のモック"""
                self.decision_count += 1
                return {
                    "decision_id": f"mock_decision_{self.decision_count}",
                    "action": "continue",
                    "confidence": 0.8,
                    "reason": "Mock decision for testing",
                }

            async def get_recommendation(self, error_context):
                """推奨アクションのモック"""
                return {"recommendation": "retry", "wait_time": 5, "message": "Mock recommendation"}

        print("✅ MockDecisionSupportSystem 作成完了")
        return MockDecisionSupportSystem()

    async def run_continuous_cycle(self, duration: int = None, single_cycle: bool = False):
        """
        連続実行サイクル（DecisionSupportSystem統合版）
        """
        self.start_time = datetime.now()

        print("=" * 70)
        print(f"🚀 {self.VERSION} 起動 - DecisionSupportSystem統合")
        print("=" * 70)
        print(f"開始時刻: {self.start_time}")
        print(f"実行モード: {'シングルサイクル' if single_cycle else '連続実行'}")
        if duration:
            print(f"実行時間: {duration}秒")
        print("=" * 70)

        try:
            # 親クラスのメソッドを使用
            await super().run_continuous_cycle(duration, single_cycle)

        except Exception as e:
            print(f"❌ 実行エラー: {e}")
            # DecisionSupportSystemを使用してエラー分析
            await self._analyze_error_with_dss(e)
            raise

        finally:
            self._print_enhanced_final_stats()

    async def _analyze_error_with_dss(self, error):
        """
        DecisionSupportSystemを使用したエラー分析
        """
        try:
            error_context = {
                "error_type": type(error).__name__,
                "error_message": str(error),
                "timestamp": datetime.now().isoformat(),
                "cycle_count": getattr(self, "cycle_count", 0),
            }

            recommendation = await self.decision_support.get_recommendation(error_context)
            print(f"🔍 DecisionSupportSystem 推奨: {recommendation}")

        except Exception as dss_error:
            print(f"⚠️  DecisionSupportSystem 分析エラー: {dss_error}")

    def _print_enhanced_final_stats(self):
        """拡張最終統計表示"""
        if not self.start_time:
            return

        elapsed = (datetime.now() - self.start_time).total_seconds()

        print("\n" + "=" * 70)
        print("📊 拡張最終統計 - DecisionSupportSystem統合")
        print("=" * 70)
        print(f"実行時間: {elapsed:.0f}秒 ({elapsed/3600:.2f}時間)")
        print(f"総サイクル数: {self.cycle_count}")

        # DecisionSupportSystemの統計
        if hasattr(self, "decision_support") and hasattr(self.decision_support, "decision_count"):
            print(f"意思決定回数: {self.decision_support.decision_count}")

        print("=" * 70)

    async def get_decision_support_stats(self):
        """
        DecisionSupportSystemの統計を取得
        """
        stats = {
            "version": self.VERSION,
            "cycle_count": getattr(self, "cycle_count", 0),
            "decision_support_available": hasattr(self, "decision_support")
            and self.decision_support is not None,
        }

        if stats["decision_support_available"]:
            stats["decision_count"] = getattr(self.decision_support, "decision_count", 0)
            stats["initialized"] = getattr(self.decision_support, "initialized", False)

        return stats


async def main():
    """メイン実行"""
    orchestrator = IntegratedOrchestratorV32DecisionSupport()

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
