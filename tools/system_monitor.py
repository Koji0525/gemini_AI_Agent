import logging
from datetime import datetime, timedelta
from typing import Dict, List
import sys
from pathlib import Path
from tools.sheets_manager import GoogleSheetsManager

"""
system_monitor.py

システム動作状況の監視ツール

【変更の理由】
- 1週間後のシステム動作状況確認用
- エラー率、ナレッジベース成長率の自動算出
- 最適化ポイントの自動検出
"""


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


logger = logging.getLogger(__name__)


class SystemMonitor:
    """システム監視ツール"""

    def __init__(self):
        self.sheets_manager = GoogleSheetsManager()

    def get_system_status(self) -> Dict:
        """システム動作状況を取得"""
        print("=" * 60)
        print("📊 システム動作状況レポート")
        print(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        status = {}

        # 1. タスク実行状況
        print("\n【1. タスク実行状況】")
        task_stats = self._get_task_statistics()
        status["tasks"] = task_stats

        # 2. エラー率分析
        print("\n【2. エラー率分析】")
        error_stats = self._get_error_statistics()
        status["errors"] = error_stats

        # 3. ナレッジベース成長率
        print("\n【3. ナレッジベース成長】")
        kb_stats = self._get_knowledge_base_growth()
        status["knowledge_base"] = kb_stats

        # 4. 品質トレンド
        print("\n【4. 品質トレンド】")
        quality_stats = self._get_quality_trend()
        status["quality"] = quality_stats

        # 5. ボトルネック検出
        print("\n【5. ボトルネック検出】")
        bottlenecks = self._detect_bottlenecks()
        status["bottlenecks"] = bottlenecks

        return status

    def _get_task_statistics(self) -> Dict:
        """タスク統計"""
        try:
            data = self.sheets_manager.read_range("pm_tasks!A2:K100")

            if not data:
                print("  ⚠️ タスクデータなし")
                return {}

            total = len(data)
            pending = sum(1 for row in data if len(row) > 3 and row[3] == "pending")
            in_progress = sum(1 for row in data if len(row) > 3 and row[3] == "in_progress")
            completed = sum(1 for row in data if len(row) > 3 and row[3] == "completed")
            failed = sum(1 for row in data if len(row) > 3 and row[3] == "failed")

            completion_rate = (completed / total * 100) if total > 0 else 0
            failure_rate = (failed / total * 100) if total > 0 else 0

            print(f"  総タスク数: {total}")
            print(f"  保留中: {pending} ({pending / total * 100:.1f}%)")
            print(f"  実行中: {in_progress} ({in_progress / total * 100:.1f}%)")
            print(f"  完了: {completed} ({completion_rate:.1f}%)")
            print(f"  失敗: {failed} ({failure_rate:.1f}%)")

            return {
                "total": total,
                "pending": pending,
                "in_progress": in_progress,
                "completed": completed,
                "failed": failed,
                "completion_rate": completion_rate,
                "failure_rate": failure_rate,
            }

        except Exception as e:
            print(f"  ❌ エラー: {e}")
            return {}

    def _get_error_statistics(self) -> Dict:
        """エラー統計"""
        try:
            data = self.sheets_manager.read_range("error_log!A2:E100")

            if not data:
                print("  ℹ️ エラーログなし")
                return {"total_errors": 0, "error_rate": 0}

            total_errors = len(data)
            resolved = sum(1 for row in data if len(row) > 3 and row[3] == "resolved")
            unresolved = total_errors - resolved

            resolution_rate = (resolved / total_errors * 100) if total_errors > 0 else 0

            print(f"  総エラー数: {total_errors}")
            print(f"  解決済み: {resolved} ({resolution_rate:.1f}%)")
            print(f"  未解決: {unresolved}")

            # エラータイプ別集計
            error_types = {}
            for row in data:
                if len(row) > 1:
                    error_type = row[1]
                    error_types[error_type] = error_types.get(error_type, 0) + 1

            if error_types:
                print("\n  【エラータイプ別】")
                for error_type, count in sorted(
                    error_types.items(), key=lambda x: x[1], reverse=True
                ):
                    print(f"    - {error_type}: {count}回")

            return {
                "total_errors": total_errors,
                "resolved": resolved,
                "unresolved": unresolved,
                "resolution_rate": resolution_rate,
                "error_types": error_types,
            }

        except Exception as e:
            print(f"  ⚠️ エラーログ取得失敗: {e}")
            return {}

    def _get_knowledge_base_growth(self) -> Dict:
        """ナレッジベース成長率"""
        try:
            data = self.sheets_manager.read_range("knowledge_base!A2:F100")

            if not data:
                print("  ℹ️ ナレッジベースなし")
                return {"total_recipes": 0, "growth_rate": 0}

            total_recipes = len(data)

            # 直近7日間の追加数
            week_ago = datetime.now() - timedelta(days=7)
            recent_recipes = 0

            for row in data:
                if len(row) > 5:  # created_atがある場合
                    try:
                        created_at = datetime.fromisoformat(row[5].replace("Z", "+00:00"))
                        if created_at >= week_ago:
                            recent_recipes += 1
                    except Exception:
                        pass

            growth_rate = (recent_recipes / 7) if recent_recipes > 0 else 0  # 1日あたり

            print(f"  総レシピ数: {total_recipes}")
            print(f"  直近7日間の追加: {recent_recipes}件")
            print(f"  成長率: {growth_rate:.1f}件/日")

            return {
                "total_recipes": total_recipes,
                "recent_additions": recent_recipes,
                "growth_rate": growth_rate,
            }

        except Exception as e:
            print(f"  ⚠️ ナレッジベース取得失敗: {e}")
            return {}

    def _get_quality_trend(self) -> Dict:
        """品質トレンド"""
        try:
            data = self.sheets_manager.read_range("task_execution_log!A2:J100")

            if not data:
                print("  ℹ️ 実行ログなし")
                return {}

            # 品質スコアを抽出（H列: Quality_Score）
            quality_scores = []
            for row in data:
                if len(row) > 7:
                    try:
                        score = float(row[7])
                        quality_scores.append(score)
                    except Exception:
                        pass

            if not quality_scores:
                print("  ⚠️ 品質スコアなし")
                return {}

            avg_quality = sum(quality_scores) / len(quality_scores)
            max_quality = max(quality_scores)
            min_quality = min(quality_scores)

            print(f"  平均品質スコア: {avg_quality:.2f}/10")
            print(f"  最高: {max_quality:.1f} / 最低: {min_quality:.1f}")
            print(f"  サンプル数: {len(quality_scores)}")

            return {
                "average": avg_quality,
                "max": max_quality,
                "min": min_quality,
                "count": len(quality_scores),
            }

        except Exception as e:
            print(f"  ⚠️ 品質データ取得失敗: {e}")
            return {}

    def _detect_bottlenecks(self) -> List[str]:
        """ボトルネック検出"""
        bottlenecks = []

        try:
            # 長時間in_progressのタスク
            data = self.sheets_manager.read_range("pm_tasks!A2:K100")

            for row in data:
                if len(row) > 3 and row[3] == "in_progress":
                    task_id = row[0] if len(row) > 0 else "unknown"
                    bottlenecks.append(f"長期実行中タスク: {task_id}")

            # 高頻度エラー
            error_data = self.sheets_manager.read_range("error_log!A2:E100")
            error_types = {}

            for row in error_data:
                if len(row) > 1:
                    error_type = row[1]
                    error_types[error_type] = error_types.get(error_type, 0) + 1

            for error_type, count in error_types.items():
                if count >= 5:
                    bottlenecks.append(f"高頻度エラー: {error_type} ({count}回)")

            if bottlenecks:
                for bottleneck in bottlenecks:
                    print(f"  ⚠️ {bottleneck}")
            else:
                print("  ✅ ボトルネックなし")

            return bottlenecks

        except Exception as e:
            print(f"  ⚠️ ボトルネック検出エラー: {e}")
            return []

    def generate_report(self) -> str:
        """レポート生成"""
        status = self.get_system_status()

        print("\n" + "=" * 60)
        print("📋 推奨アクション")
        print("=" * 60)

        # エラー率が高い場合
        if status.get("tasks", {}).get("failure_rate", 0) > 20:
            print("  ⚠️ エラー率が20%を超えています")
            print("     → error_analysisシートでエラー原因を確認")
            print("     → knowledge_baseに修正レシピを追加")

        # ボトルネックがある場合
        if status.get("bottlenecks"):
            print("  ⚠️ ボトルネックが検出されました")
            print("     → 長期実行中のタスクを手動確認")
            print("     → タイムアウト設定の見直し")

        # ナレッジベースの成長が遅い場合
        if status.get("knowledge_base", {}).get("growth_rate", 0) < 0.5:
            print("  ℹ️ ナレッジベースの成長が遅いです")
            print("     → 手動でレシピを追加")
            print("     → エラー分析から学習パターンを抽出")

        # 品質スコアが低い場合
        if status.get("quality", {}).get("average", 10) < 7.0:
            print("  ⚠️ 品質スコアが低下しています")
            print("     → タスク定義の見直し")
            print("     → エージェントのプロンプト改善")

        print("=" * 60)

        return "レポート生成完了"


def main():
    """メイン実行"""
    monitor = SystemMonitor()
    monitor.generate_report()
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    exit(main())
