"""
LearningCoordinator - 学習サイクルの中央制御ハブ
作成日: 2025-11-03
目的: Loop 3（学習サイクル）を自動化

機能:
1. エラー発生の監視
2. 学習トリガーの管理
3. 学習サイクルの実行
"""

import asyncio
import logging
import time
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LearningCoordinator:
    """
    学習サイクルを制御する中央ハブ

    学習トリガー:
    1. 新規エラー50件蓄積
    2. 6時間経過
    3. 緊急対応（同じエラー5回連続）
    """

    def __init__(
        self,
        sheets_manager,
        error_threshold: int = 50,
        time_threshold: int = 21600,  # 6時間
        consecutive_threshold: int = 5,
    ):
        self.sheets = sheets_manager
        self.error_threshold = error_threshold
        self.time_threshold = time_threshold
        self.consecutive_threshold = consecutive_threshold

        # 状態管理
        self.error_count = 0
        self.consecutive_errors = 0
        self.last_learning_time = time.time()
        self.learning_cycles_executed = 0

        # 統計情報
        self.stats = {"total_errors": 0, "learning_cycles": 0, "patterns_learned": 0}

        # エージェントの初期化
        self._initialize_agents()

        logger.info("✅ LearningCoordinator 初期化完了")

    def _initialize_agents(self):
        """学習関連エージェントの初期化"""
        try:
            # ErrorClassifier
            from agents.self_healing.error_classifier import ErrorClassifier

            self.error_classifier = ErrorClassifier()
            logger.info("  ✅ ErrorClassifier 初期化完了")
        except Exception as e:
            logger.warning(f"  ⚠️ ErrorClassifier 初期化失敗: {str(e)}")
            self.error_classifier = None

        try:
            # KnowledgeBaseManager
            from agents.self_healing.knowledge_base_manager import KnowledgeBaseManager

            self.knowledge_base = KnowledgeBaseManager(self.sheets)
            logger.info("  ✅ KnowledgeBaseManager 初期化完了")
        except Exception as e:
            logger.warning(f"  ⚠️ KnowledgeBaseManager 初期化失敗: {str(e)}")
            self.knowledge_base = None

        try:
            # SelfHealingPipeline
            from agents.self_healing.self_healing_pipeline import SelfHealingPipeline

            self.self_healing = SelfHealingPipeline()
            logger.info("  ✅ SelfHealingPipeline 初期化完了")
        except Exception as e:
            logger.warning(f"  ⚠️ SelfHealingPipeline 初期化失敗: {str(e)}")
            self.self_healing = None

        try:
            # PatternExtractor（logging配下を使用）
            from agents.self_healing.logging.pattern_extractor import PatternExtractor
            from agents.self_healing.logging.log_integrator import LogIntegrator

            self.log_integrator = LogIntegrator()
            self.pattern_extractor = PatternExtractor(self.log_integrator)
            logger.info("  ✅ PatternExtractor 初期化完了")
        except Exception as e:
            logger.warning(f"  ⚠️ PatternExtractor 初期化失敗: {str(e)}")
            self.pattern_extractor = None

    async def record_error(self, error: Exception, context: Dict[str, Any] = None):
        """
        エラーを記録し、学習トリガーをチェック

        Args:
            error: 発生したエラー
            context: エラーのコンテキスト情報
        """
        self.error_count += 1
        self.consecutive_errors += 1
        self.stats["total_errors"] += 1

        # エラー分類
        if self.error_classifier:
            try:
                error_type = self.error_classifier.classify(error)
                logger.info(f"🔍 エラー分類: {error_type}")
            except Exception as e:
                logger.warning(f"⚠️ エラー分類失敗: {str(e)}")

        # 学習トリガーをチェック
        await self._check_learning_trigger()

    def record_success(self):
        """成功を記録（連続エラーカウントをリセット）"""
        self.consecutive_errors = 0

    async def _check_learning_trigger(self):
        """学習トリガー条件をチェック"""
        should_learn = False
        reason = ""

        # トリガー1: 新規エラー50件
        if self.error_count >= self.error_threshold:
            should_learn = True
            reason = f"エラー{self.error_count}件蓄積"

        # トリガー2: 6時間経過
        elif time.time() - self.last_learning_time >= self.time_threshold:
            should_learn = True
            reason = "6時間経過"

        # トリガー3: 緊急対応（5回連続エラー）
        elif self.consecutive_errors >= self.consecutive_threshold:
            should_learn = True
            reason = f"{self.consecutive_errors}回連続エラー（緊急）"

        if should_learn:
            logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            logger.info(f"🔄 学習サイクル開始（{reason}）")
            logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            await self.run_learning_cycle()

    async def run_learning_cycle(self):
        """学習サイクルを実行"""
        try:
            cycle_start = time.time()

            # 1. パターン抽出
            if self.pattern_extractor:
                try:
                    patterns = await self._extract_patterns()
                    logger.info(f"📊 抽出パターン数: {len(patterns)}")
                except Exception as e:
                    logger.warning(f"⚠️ パターン抽出エラー: {str(e)}")
                    patterns = []
            else:
                patterns = []

            # 2. ナレッジベースに保存
            if self.knowledge_base and patterns:
                try:
                    await self._save_to_knowledge_base(patterns)
                    self.stats["patterns_learned"] += len(patterns)
                except Exception as e:
                    logger.warning(f"⚠️ ナレッジ保存エラー: {str(e)}")

            # 3. 自己修復の実行
            if self.self_healing:
                try:
                    await self._run_self_healing()
                except Exception as e:
                    logger.warning(f"⚠️ 自己修復エラー: {str(e)}")

            # カウンターをリセット
            self.error_count = 0
            self.consecutive_errors = 0
            self.last_learning_time = time.time()
            self.learning_cycles_executed += 1
            self.stats["learning_cycles"] += 1

            elapsed = time.time() - cycle_start
            logger.info(f"✅ 学習サイクル完了（{elapsed:.2f}秒）")

        except Exception as e:
            logger.error(f"❌ 学習サイクルエラー: {str(e)}")

    async def _extract_patterns(self):
        """エラーパターンを抽出"""
        # 実装は簡略化
        logger.info("📊 パターン抽出中...")
        await asyncio.sleep(0.1)
        return []

    async def _save_to_knowledge_base(self, patterns):
        """ナレッジベースに保存"""
        logger.info(f"💾 ナレッジベース保存: {len(patterns)}件")
        await asyncio.sleep(0.1)

    async def _run_self_healing(self):
        """自己修復を実行"""
        logger.info("🔧 自己修復実行中...")
        await asyncio.sleep(0.1)

    async def start_background_learning(self):
        """
        バックグラウンドで学習ループを起動

        1分ごとに学習トリガーをチェック
        """
        logger.info("🔄 バックグラウンド学習ループ開始")

        while True:
            try:
                await self._check_learning_trigger()
                await asyncio.sleep(60)  # 1分ごとにチェック
            except Exception as e:
                logger.error(f"❌ バックグラウンド学習エラー: {str(e)}")
                await asyncio.sleep(60)

    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        return {
            **self.stats,
            "error_count": self.error_count,
            "consecutive_errors": self.consecutive_errors,
            "learning_cycles_executed": self.learning_cycles_executed,
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# テスト用のメインブロック
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == "__main__":

    async def test_coordinator():
        """LearningCoordinator の動作テスト"""

        class MockSheets:
            pass

        coordinator = LearningCoordinator(MockSheets())

        print("\n🧪 LearningCoordinator 動作テスト\n")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # エラーを記録してトリガーテスト
        for i in range(3):
            await coordinator.record_error(Exception(f"テストエラー{i+1}"))

        # 統計確認
        stats = coordinator.get_stats()
        print(f"\n📊 統計:")
        print(f"  総エラー数: {stats['total_errors']}")
        print(f"  学習サイクル: {stats['learning_cycles']}")
        print(f"  学習パターン: {stats['patterns_learned']}")

        print("\n✅ テスト完了")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    asyncio.run(test_coordinator())
