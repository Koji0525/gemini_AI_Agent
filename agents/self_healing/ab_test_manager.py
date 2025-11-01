#!/usr/bin/env python3
"""
ABTestManager: 自動A/Bテストマネージャー

複数の修正案を自動的にテストし、
統計的に最も効果的な方法を選定する。
"""
from typing import Dict, Any, List, Optional, Callable, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import json
import statistics


@dataclass
class TestVariant:
    """テストバリアント（修正案）"""

    variant_id: str
    name: str
    description: str
    implementation: Callable  # 実行する関数
    parameters: Dict[str, Any] = field(default_factory=dict)

    # テスト結果
    executions: List[Dict[str, Any]] = field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0
    total_duration: float = 0.0
    quality_scores: List[float] = field(default_factory=list)

    def add_result(self, success: bool, duration: float, quality_score: float = 0.0):
        """結果を追加"""
        self.executions.append(
            {
                "success": success,
                "duration": duration,
                "quality_score": quality_score,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

        self.total_duration += duration

        if quality_score > 0:
            self.quality_scores.append(quality_score)

    @property
    def success_rate(self) -> float:
        """成功率"""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0

    @property
    def average_duration(self) -> float:
        """平均実行時間"""
        total = self.success_count + self.failure_count
        return self.total_duration / total if total > 0 else 0.0

    @property
    def average_quality(self) -> float:
        """平均品質スコア"""
        return statistics.mean(self.quality_scores) if self.quality_scores else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "variant_id": self.variant_id,
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_rate,
            "average_duration": self.average_duration,
            "average_quality": self.average_quality,
            "execution_count": len(self.executions),
        }


@dataclass
class ABTestResult:
    """A/Bテスト結果"""

    test_id: str
    test_name: str
    variants: List[TestVariant]
    winner: Optional[TestVariant] = None
    confidence_level: float = 0.0
    total_executions: int = 0
    test_duration: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "variants": [v.to_dict() for v in self.variants],
            "winner": self.winner.to_dict() if self.winner else None,
            "confidence_level": self.confidence_level,
            "total_executions": self.total_executions,
            "test_duration": self.test_duration,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


class ABTestManager:
    """自動A/Bテストマネージャー"""

    def __init__(self, kb_manager=None):
        """
        初期化

        Args:
            kb_manager: KnowledgeBaseManager（結果保存用）
        """
        self.kb_manager = kb_manager
        self.active_tests: Dict[str, ABTestResult] = {}

        print("✅ ABTestManager初期化完了")

    async def create_test(self, test_name: str, variants: List[TestVariant], min_executions: int = 10) -> str:
        """
        A/Bテストを作成

        Args:
            test_name: テスト名
            variants: テストバリアントのリスト
            min_executions: 最小実行回数

        Returns:
            テストID
        """
        test_id = f"ABT_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        test_result = ABTestResult(test_id=test_id, test_name=test_name, variants=variants)

        self.active_tests[test_id] = test_result

        print(f"\n✅ A/Bテスト作成: {test_id}")
        print(f"   テスト名: {test_name}")
        print(f"   バリアント数: {len(variants)}")
        print(f"   最小実行回数: {min_executions}")

        return test_id

    async def run_test(
        self,
        test_id: str,
        test_data: Any,
        min_executions: int = 10,
        max_executions: int = 50,
        early_stopping: bool = True,
    ) -> ABTestResult:
        """
        A/Bテストを実行

        Args:
            test_id: テストID
            test_data: テストデータ
            min_executions: 最小実行回数
            max_executions: 最大実行回数
            early_stopping: 早期終了を有効にするか

        Returns:
            テスト結果
        """
        if test_id not in self.active_tests:
            raise ValueError(f"Test {test_id} not found")

        test_result = self.active_tests[test_id]

        print("\n" + "=" * 70)
        print(f"🧪 A/Bテスト実行: {test_result.test_name}")
        print("=" * 70)

        start_time = datetime.now()
        total_executions = 0

        # ラウンドロビンで各バリアントをテスト
        while total_executions < max_executions:
            for variant in test_result.variants:
                print(f"\n[{total_executions + 1}/{max_executions}] テスト: {variant.name}")

                # バリアント実行
                success, duration, quality = await self._execute_variant(variant, test_data)

                # 結果を記録
                variant.add_result(success, duration, quality)
                total_executions += 1

                print(f"   結果: {'✅ 成功' if success else '❌ 失敗'}")
                print(f"   実行時間: {duration:.2f}秒")
                if quality > 0:
                    print(f"   品質スコア: {quality:.1f}")

                # 最小実行回数に達したかチェック
                if total_executions >= min_executions:
                    # 早期終了チェック
                    if early_stopping and self._should_stop_early(test_result):
                        print(f"\n⚡ 早期終了: 明確な勝者が確定")
                        break

            # 早期終了した場合
            if total_executions >= min_executions and early_stopping:
                if self._should_stop_early(test_result):
                    break

        # テスト終了
        end_time = datetime.now()
        test_result.test_duration = (end_time - start_time).total_seconds()
        test_result.total_executions = total_executions

        # 勝者を判定
        test_result.winner, test_result.confidence_level = self._determine_winner(test_result)

        # 結果を表示
        self._print_test_results(test_result)

        # ナレッジベースに保存
        if self.kb_manager:
            await self._save_to_knowledge_base(test_result)

        return test_result

    async def _execute_variant(self, variant: TestVariant, test_data: Any) -> Tuple[bool, float, float]:
        """
        バリアントを実行

        Args:
            variant: テストバリアント
            test_data: テストデータ

        Returns:
            (成功フラグ, 実行時間, 品質スコア)
        """
        start_time = datetime.now()

        try:
            # バリアントの実装を実行
            result = await variant.implementation(test_data, **variant.parameters)

            # 結果を評価
            if isinstance(result, dict):
                success = result.get("success", True)
                quality = result.get("quality_score", 0.0)
            else:
                success = True
                quality = 0.0

        except Exception as e:
            print(f"      ⚠️ エラー: {e}")
            success = False
            quality = 0.0

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        return success, duration, quality

    def _should_stop_early(self, test_result: ABTestResult) -> bool:
        """
        早期終了すべきか判定

        Args:
            test_result: テスト結果

        Returns:
            早期終了すべきか
        """
        # 最低10回は実行
        if test_result.total_executions < 10:
            return False

        # 各バリアントの成功率を比較
        success_rates = [v.success_rate for v in test_result.variants]

        if not success_rates:
            return False

        max_rate = max(success_rates)
        min_rate = min(success_rates)

        # 成功率の差が30%以上なら早期終了
        if max_rate - min_rate >= 0.3:
            return True

        return False

    def _determine_winner(self, test_result: ABTestResult) -> Tuple[Optional[TestVariant], float]:
        """
        勝者を判定

        Args:
            test_result: テスト結果

        Returns:
            (勝者バリアント, 信頼度)
        """
        if not test_result.variants:
            return None, 0.0

        # 総合スコアを計算
        scored_variants = []

        for variant in test_result.variants:
            # 成功率、速度、品質の重み付け平均
            score = (
                variant.success_rate * 0.5  # 成功率: 50%
                + (1 / (variant.average_duration + 1)) * 0.2  # 速度: 20%
                + (variant.average_quality / 10) * 0.3  # 品質: 30%
            )

            scored_variants.append((variant, score))

        # スコア順にソート
        scored_variants.sort(key=lambda x: x[1], reverse=True)

        winner, winner_score = scored_variants[0]

        # 信頼度を計算
        if len(scored_variants) > 1:
            runner_up_score = scored_variants[1][1]

            # スコア差が大きいほど信頼度が高い
            if winner_score > 0:
                confidence = min((winner_score - runner_up_score) / winner_score, 1.0)
            else:
                confidence = 0.0
        else:
            confidence = 1.0

        # 最低実行回数による信頼度調整
        execution_factor = min(len(winner.executions) / 20, 1.0)
        confidence *= execution_factor

        return winner, confidence

    def _print_test_results(self, test_result: ABTestResult):
        """テスト結果を表示"""
        print("\n" + "=" * 70)
        print("📊 A/Bテスト結果")
        print("=" * 70)
        print(f"テスト名: {test_result.test_name}")
        print(f"総実行回数: {test_result.total_executions}")
        print(f"実行時間: {test_result.test_duration:.2f}秒")
        print()

        # 各バリアントの結果
        print("バリアント別結果:")
        print("-" * 70)

        for i, variant in enumerate(test_result.variants, 1):
            print(f"\n{i}. {variant.name}")
            print(f"   説明: {variant.description}")
            print(f"   実行回数: {len(variant.executions)}")
            print(f"   成功率: {variant.success_rate:.1%}")
            print(f"   平均実行時間: {variant.average_duration:.2f}秒")
            if variant.quality_scores:
                print(f"   平均品質: {variant.average_quality:.2f}")

        # 勝者
        if test_result.winner:
            print("\n" + "=" * 70)
            print("🏆 勝者")
            print("=" * 70)
            print(f"バリアント: {test_result.winner.name}")
            print(f"信頼度: {test_result.confidence_level:.1%}")
            print(f"成功率: {test_result.winner.success_rate:.1%}")
            print(f"平均実行時間: {test_result.winner.average_duration:.2f}秒")

            if test_result.confidence_level >= 0.8:
                print("\n✅ 高信頼度で勝者が確定しました")
            elif test_result.confidence_level >= 0.6:
                print("\n⚠️ 中程度の信頼度です。追加テストを推奨")
            else:
                print("\n⚠️ 信頼度が低いです。より多くのテストが必要")

    async def _save_to_knowledge_base(self, test_result: ABTestResult):
        """テスト結果をナレッジベースに保存"""
        if not self.kb_manager:
            return

        try:
            from .knowledge_base_manager import KnowledgePattern

            # 勝者のパターンを保存
            if test_result.winner:
                pattern = KnowledgePattern(
                    pattern_type="success_pattern",
                    description=f"A/Bテスト勝者: {test_result.winner.name}",
                    context={
                        "test_id": test_result.test_id,
                        "test_name": test_result.test_name,
                        "variant_name": test_result.winner.name,
                        "success_rate": test_result.winner.success_rate,
                        "confidence_level": test_result.confidence_level,
                        "parameters": test_result.winner.parameters,
                    },
                    source_logs=[test_result.test_id],
                )

                pattern.success_rate = test_result.winner.success_rate * 100
                pattern.usage_count = len(test_result.winner.executions)
                pattern.effectiveness_score = int(test_result.confidence_level * 100)
                pattern.learning_tags = ["ab_test", "winner", test_result.test_name]

                await self.kb_manager.save_pattern(pattern)

                print(f"\n✅ テスト結果をナレッジベースに保存")

        except Exception as e:
            print(f"\n⚠️ ナレッジベース保存エラー: {e}")

    def get_test_summary(self, test_id: str) -> Optional[Dict[str, Any]]:
        """テストサマリーを取得"""
        if test_id not in self.active_tests:
            return None

        test_result = self.active_tests[test_id]
        return test_result.to_dict()


if __name__ == "__main__":
    # 簡易テスト
    manager = ABTestManager()
    print("ABTestManager初期化成功")
