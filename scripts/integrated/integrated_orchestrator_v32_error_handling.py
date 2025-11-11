"""
Integrated Orchestrator v32 - Error Handling Edition
Phase 2 Week 3 Day 1-2: ErrorClassifier統合

【追加機能】
- ErrorClassifier統合
- エラー自動分類（9カテゴリ63パターン）
- エラー重要度判定
- エラーコンテキスト記録

【継承元】
- IntegratedOrchestratorV31Core（Phase 1完成版）
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# プロジェクトルート追加
sys.path.insert(0, str(Path(__file__).parent.parent))

# v31継承
from scripts.integrated.integrated_orchestrator_v31_core import IntegratedOrchestratorV31Core

# ErrorClassifier追加
try:
    from agents.self_healing.utils.error_classifier import ErrorClassifier

    ERROR_CLASSIFIER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  ErrorClassifierインポート失敗: {e}")
    ERROR_CLASSIFIER_AVAILABLE = False
    ErrorClassifier = None


class IntegratedOrchestratorV32ErrorHandling(IntegratedOrchestratorV31Core):
    """
    Phase 2 Week 3: ErrorClassifier統合版

    v31の全機能を継承し、エラー処理機能を追加
    """

    VERSION = "v32.0.0-error-handling"

    def __init__(self):
        """
        初期化
        v31の初期化 + ErrorClassifier追加
        """
        # 親クラス初期化（v31）
        super().__init__()

        # ErrorClassifier初期化
        self.error_classifier = None
        self.error_stats = {
            "total_errors": 0,
            "classified_errors": 0,
            "by_category": {},
            "by_severity": {},
        }

        if ERROR_CLASSIFIER_AVAILABLE and ErrorClassifier:
            try:
                self.error_classifier = ErrorClassifier()
                print(f"   ✅ ErrorClassifier初期化成功")
            except Exception as e:
                print(f"   ⚠️  ErrorClassifier初期化失敗: {e}")
        else:
            print(f"   ⚠️  ErrorClassifier利用不可")

        print(f"✅ IntegratedOrchestrator {self.VERSION} 初期化完了")

    async def classify_error(
        self, error: Exception, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        エラー分類

        Args:
            error: 発生したエラー
            context: エラーコンテキスト

        Returns:
            分類結果 {category, severity, message, context}
        """
        if not self.error_classifier:
            return {
                "category": "unknown",
                "severity": "medium",
                "message": str(error),
                "context": context or {},
                "classified": False,
            }

        try:
            # ErrorClassifierで分類
            result = self.error_classifier.classify(error)

            # 統計更新
            self.error_stats["total_errors"] += 1
            self.error_stats["classified_errors"] += 1

            category = result.get("category", "unknown")
            severity = result.get("severity", "medium")

            self.error_stats["by_category"][category] = (
                self.error_stats["by_category"].get(category, 0) + 1
            )
            self.error_stats["by_severity"][severity] = (
                self.error_stats["by_severity"].get(severity, 0) + 1
            )

            return {
                "category": category,
                "severity": severity,
                "message": str(error),
                "context": context or {},
                "classified": True,
                "details": result,
            }

        except Exception as e:
            print(f"⚠️  エラー分類失敗: {e}")
            self.error_stats["total_errors"] += 1

            return {
                "category": "unknown",
                "severity": "medium",
                "message": str(error),
                "context": context or {},
                "classified": False,
                "classification_error": str(e),
            }

    async def _execute_single_cycle(self):
        """
        1サイクル実行（エラーハンドリング強化版）
        """
        print(f"\n{'='*70}")
        print(f"🔄 サイクル {self.cycle_count + 1}")
        print(f"{'='*70}")

        try:
            # 親クラスのサイクル実行
            if hasattr(super(), "_execute_single_cycle"):
                await super()._execute_single_cycle()
            else:
                print("⚠️  親クラスのメソッドなし - スキップ")

        except Exception as e:
            # エラー発生時: ErrorClassifierで分類
            print(f"\n❌ サイクルエラー発生")

            classification = await self.classify_error(
                e, {"cycle": self.cycle_count + 1, "timestamp": datetime.now().isoformat()}
            )

            print(f"   カテゴリ: {classification['category']}")
            print(f"   重要度: {classification['severity']}")
            print(f"   メッセージ: {classification['message']}")

            # 重要度に応じた処理
            if classification["severity"] in ["critical", "high"]:
                print(f"   ⚠️  重大エラー - 記録して継続")
            else:
                print(f"   ℹ️  軽微なエラー - 継続")

    def get_error_stats(self) -> Dict[str, Any]:
        """エラー統計取得"""
        return {
            "version": self.VERSION,
            "stats": self.error_stats,
            "classifier_available": self.error_classifier is not None,
        }

    def _print_final_stats(self):
        """最終統計表示（エラー統計追加）"""
        super()._print_final_stats()

        # エラー統計表示
        if self.error_stats["total_errors"] > 0:
            print("\n" + "=" * 70)
            print("🚨 エラー統計")
            print("=" * 70)
            print(f"総エラー数: {self.error_stats['total_errors']}")
            print(f"分類成功: {self.error_stats['classified_errors']}")

            if self.error_stats["by_category"]:
                print("\nカテゴリ別:")
                for category, count in self.error_stats["by_category"].items():
                    print(f"  {category}: {count}")

            if self.error_stats["by_severity"]:
                print("\n重要度別:")
                for severity, count in self.error_stats["by_severity"].items():
                    print(f"  {severity}: {count}")

            print("=" * 70)


async def main():
    """メイン実行"""
    orchestrator = IntegratedOrchestratorV32ErrorHandling()

    # 引数処理
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--single":
            await orchestrator.run_continuous_cycle(single_cycle=True)
        elif sys.argv[1] == "--stats":
            # エラー統計表示のみ
            stats = orchestrator.get_error_stats()
            print("\n" + "=" * 70)
            print("📊 エラー統計")
            print("=" * 70)
            import json

            print(json.dumps(stats, indent=2, ensure_ascii=False))
        else:
            duration = int(sys.argv[1])
            await orchestrator.run_continuous_cycle(duration=duration)
    else:
        await orchestrator.run_continuous_cycle()


if __name__ == "__main__":
    asyncio.run(main())
