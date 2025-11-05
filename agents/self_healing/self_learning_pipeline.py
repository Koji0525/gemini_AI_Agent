#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)
"""
SelfLearningPipeline: AIがAIを進化させる自己学習パイプライン

全てのコンポーネントを統合し、自動学習サイクルを実現。
"""
from typing import List

from agents.self_healing.knowledge_base_manager import KnowledgeBaseManager
from agents.self_healing.logging.log_integrator import LogIntegrator
from agents.self_healing.logging.pattern_extractor import PatternExtractor


class SelfLearningPipeline:
    """自己学習パイプライン"""

    def __init__(self, sheets_manager, knowledge_manager=None):
        """
        初期化

        Args:
            sheets_manager: GoogleSheetsManager インスタンス
            knowledge_manager: KnowledgeBaseManager インスタンス（オプション）
        """
        self.sheets_manager = sheets_manager

        # knowledge_manager が渡されない場合は自己初期化
        if knowledge_manager is None:
            self.knowledge_manager = KnowledgeBaseManager(sheets_manager)
            logger.info("📚 KnowledgeBaseManager を自動初期化")
        else:
            self.knowledge_manager = knowledge_manager
            logger.info("📚 KnowledgeBaseManager を外部から注入")

        # その他のコンポーネント初期化
        self.log_integrator = LogIntegrator(sheets_manager)
        self.pattern_extractor = PatternExtractor(self.log_integrator)

        logger.info("✅ SelfLearningPipeline 初期化完了")

    def get_learning_recommendations(self) -> List[str]:
        """
        学習の推奨事項を生成

        Returns:
            推奨事項のリスト
        """
        recommendations = []

        stats = self.kb_manager.get_statistics()
        total = stats.get("total_knowledge", 0)

        if total < 10:
            recommendations.append(
                "ナレッジが少なすぎます。より多くのタスクを実行してデータを蓄積してください。"
            )

        if stats.get("success_patterns", 0) == 0:
            recommendations.append(
                "成功パターンがありません。品質スコア8以上のタスクを3件以上実行してください。"
            )

        if stats.get("failure_patterns", 0) > stats.get("fix_recipes", 0):
            recommendations.append(
                "失敗パターンに対する修正レシピが不足しています。"
                "エラー発生時に判断プロセスを記録してください。"
            )

        if not recommendations:
            recommendations.append(
                "ナレッジベースは健全です。定期的な学習サイクルを継続してください。"
            )

        return recommendations

    async def run_learning_cycle(self):
        """
        学習サイクルを実行

        Returns:
            dict: 学習結果
                - patterns_found: 抽出されたパターン数
                - knowledge_updated: ナレッジ更新有無
        """
        try:
            # 1. 学習推奨事項を取得
            recommendations = await self.get_learning_recommendations()

            patterns_found = len(recommendations) if recommendations else 0
            knowledge_updated = patterns_found > 0

            # 2. 推奨事項があればナレッジ更新
            if knowledge_updated:
                # ナレッジベースに登録
                for rec in recommendations:
                    try:
                        await self.knowledge_base_manager.add_pattern(rec)
                    except Exception as e:
                        print(f"⚠️ パターン登録エラー: {e}")

            return {
                "patterns_found": patterns_found,
                "knowledge_updated": knowledge_updated,
                "status": "success",
            }

        except Exception as e:
            print(f"❌ 学習サイクルエラー: {e}")
            return {
                "patterns_found": 0,
                "knowledge_updated": False,
                "status": "error",
                "error": str(e),
            }
