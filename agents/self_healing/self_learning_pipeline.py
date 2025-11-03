#!/usr/bin/env python3
"""
SelfLearningPipeline: AIがAIを進化させる自己学習パイプライン

全てのコンポーネントを統合し、自動学習サイクルを実現。
"""
from datetime import datetime
from typing import Dict, Any, List
from .knowledge_base_manager import KnowledgeBaseManager
from .log_integrator import LogIntegrator
from .pattern_extractor import PatternExtractor
from .context_logger import ContextLogger


class SelfLearningPipeline:
    """自己学習パイプライン"""

    def __init__(self, sheets_manager):
        """
        初期化

        Args:
            sheets_manager: GoogleSheetsManagerインスタンス
        """
        self.sheets_manager = sheets_manager

        # コンポーネント初期化
        self.kb_manager = KnowledgeBaseManager(sheets_manager)
        self.log_integrator = LogIntegrator(sheets_manager)
        self.pattern_extractor = PatternExtractor(self.log_integrator)
        self.context_logger = ContextLogger(sheets_manager)

        print("✅ SelfLearningPipeline初期化完了")

    async def run_learning_cycle(self) -> Dict[str, Any]:
        """
        学習サイクルを実行

        フロー:
        1. ログからパターンを抽出
        2. パターンをナレッジベースに保存
        3. 統計情報を生成

        Returns:
            実行結果の辞書
        """
        print("\n" + "=" * 70)
        print("🧠 自己学習サイクル開始")
        print("=" * 70)
        print(f"⏰ 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        start_time = datetime.now()

        try:
            # ステップ1: パターン抽出
            print("\n" + "=" * 70)
            print("📊 STEP 1: パターンマイニング")
            print("=" * 70)

            patterns = await self.pattern_extractor.extract_all_patterns()

            if not patterns:
                print("\n⚠️ 新しいパターンが見つかりませんでした")
                print("   既存のログから学習可能なパターンを全て抽出済みか、")
                print("   データが不足している可能性があります。")

                return {
                    "success": True,
                    "patterns_found": 0,
                    "patterns_saved": 0,
                    "message": "No new patterns found",
                }

            # ステップ2: ナレッジベースに保存
            print("\n" + "=" * 70)
            print("💾 STEP 2: ナレッジベース保存")
            print("=" * 70)

            saved_count = 0
            failed_count = 0

            for i, pattern in enumerate(patterns, 1):
                print(f"\n[{i}/{len(patterns)}] 保存中: {pattern.description[:50]}...")

                if await self.kb_manager.save_pattern(pattern):
                    saved_count += 1
                    print(f"  ✅ 成功")
                else:
                    failed_count += 1
                    print(f"  ❌ 失敗")

            print(f"\n保存結果: ✅ {saved_count}件成功, ❌ {failed_count}件失敗")

            # ステップ3: 統計情報生成
            print("\n" + "=" * 70)
            print("📈 STEP 3: 統計情報生成")
            print("=" * 70)

            stats = self.kb_manager.get_statistics()

            print(f"\n📊 ナレッジベース統計:")
            print(f"  合計ナレッジ数: {stats.get('total_knowledge', 0)}件")
            print(f"  - 成功パターン: {stats.get('success_patterns', 0)}件")
            print(f"  - 失敗パターン: {stats.get('failure_patterns', 0)}件")
            print(f"  - 修正レシピ: {stats.get('fix_recipes', 0)}件")

            # 実行時間計算
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # 完了メッセージ
            print("\n" + "=" * 70)
            print("✅ 自己学習サイクル完了")
            print("=" * 70)
            print(f"⏰ 終了時刻: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏱️  実行時間: {duration:.2f}秒")
            print(f"📊 抽出パターン: {len(patterns)}件")
            print(f"💾 保存成功: {saved_count}件")

            return {
                "success": True,
                "patterns_found": len(patterns),
                "patterns_saved": saved_count,
                "patterns_failed": failed_count,
                "duration_seconds": duration,
                "statistics": stats,
                "timestamp": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            }

        except Exception as e:
            print(f"\n❌ エラー発生: {e}")
            import traceback

            traceback.print_exc()

            return {"success": False, "error": str(e), "patterns_found": 0, "patterns_saved": 0}

    async def run_incremental_learning(self, since_hours: int = 24) -> Dict[str, Any]:
        """
        増分学習を実行（過去N時間のログのみ）

        Args:
            since_hours: 何時間前からのログを対象にするか

        Returns:
            実行結果
        """
        print(f"\n🔄 増分学習モード: 過去{since_hours}時間のログを分析")

        # TODO: タイムスタンプでフィルタリング
        # 現在は全ログを対象にする
        return await self.run_learning_cycle()

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
