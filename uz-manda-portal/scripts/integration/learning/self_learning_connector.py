"""
軽量Self Learning システム
依存関係を最小化した独自学習機能
"""

import json
from typing import Dict, List
from datetime import datetime
import os


class SelfLearningConnector:
    """軽量自己学習システム"""

    def __init__(self):
        self.kb_path = "/workspaces/gemini_AI_Agent/knowledge_base/wordpress_automation"
        self.learning_log_path = "/workspaces/gemini_AI_Agent/uz-manda-portal/logs/learning"
        os.makedirs(self.learning_log_path, exist_ok=True)
        os.makedirs(self.kb_path, exist_ok=True)

        print("✅ 軽量学習システム初期化完了")

    def analyze_execution_patterns(self) -> Dict:
        """実行パターンを分析（独自実装）"""
        print("\n🔍 実行パターン分析中...")

        # 各パターンファイルを読み込み
        success_patterns = self._load_patterns("success_patterns.jsonl")
        partial_patterns = self._load_patterns("partial_success_patterns.jsonl")
        failure_patterns = self._load_patterns("failure_patterns.jsonl")

        # 統計情報を読み込み
        stats = self._load_statistics()

        # 分析結果を作成
        analysis = {
            "total_patterns": len(success_patterns) + len(partial_patterns) + len(failure_patterns),
            "success_count": len(success_patterns),
            "partial_count": len(partial_patterns),
            "failure_count": len(failure_patterns),
            "success_rate": self._calculate_success_rate(success_patterns, failure_patterns),
            "average_quality_score": stats.get("average_quality_score", 0),
            "total_posts_created": stats.get("total_posts_created", 0),
            "total_executions": stats.get("total_executions", 0),
            "common_success_conditions": self._extract_common_conditions(success_patterns),
            "common_failure_causes": self._extract_failure_causes(failure_patterns),
            "best_practices": self._extract_best_practices(success_patterns),
            "recommendations": self._generate_recommendations(success_patterns, failure_patterns, stats),
        }

        print(f"  ✅ 総パターン数: {analysis['total_patterns']}")
        print(f"  ✅ 成功率: {analysis['success_rate']:.1f}%")
        print(f"  ✅ 平均品質スコア: {analysis['average_quality_score']:.1f}/10")

        return analysis

    def _load_patterns(self, filename: str) -> List[Dict]:
        """パターンファイルを読み込み"""
        filepath = f"{self.kb_path}/{filename}"
        patterns = []

        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        patterns.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue

        return patterns

    def _load_statistics(self) -> Dict:
        """統計情報を読み込み"""
        stats_file = f"{self.kb_path}/statistics.json"

        if os.path.exists(stats_file):
            with open(stats_file, "r", encoding="utf-8") as f:
                return json.load(f)

        return {}

    def _calculate_success_rate(self, success: List, failure: List) -> float:
        """成功率を計算"""
        total = len(success) + len(failure)
        if total == 0:
            return 100.0  # デフォルトで100%
        return (len(success) / total) * 100

    def _extract_common_conditions(self, patterns: List[Dict]) -> List[str]:
        """共通する成功条件を抽出"""
        if not patterns:
            return ["初回実行のため、まだデータがありません"]

        conditions = []
        for pattern in patterns[-3:]:  # 最新3件
            if "conditions" in pattern:
                for key, value in pattern["conditions"].items():
                    condition = f"{key}: {value}"
                    if condition not in conditions:
                        conditions.append(condition)

        return conditions

    def _extract_failure_causes(self, patterns: List[Dict]) -> List[str]:
        """失敗原因を抽出"""
        if not patterns:
            return []

        causes = []
        for pattern in patterns:
            if "error_type" in pattern:
                causes.append(pattern["error_type"])

        return list(set(causes))

    def _extract_best_practices(self, patterns: List[Dict]) -> List[str]:
        """ベストプラクティスを抽出"""
        if not patterns:
            return []

        practices = []
        for pattern in patterns:
            if "best_practices" in pattern:
                practices.extend(pattern["best_practices"])

        return list(set(practices))

    def _generate_recommendations(self, success: List, failure: List, stats: Dict) -> List[str]:
        """改善提案を生成"""
        recommendations = []

        # 統計ベースの提案
        if stats.get("total_executions", 0) > 0:
            avg_quality = stats.get("average_quality_score", 0)

            if avg_quality >= 9.0:
                recommendations.append("🎉 品質スコアが非常に高い水準を維持しています！")
            elif avg_quality >= 8.0:
                recommendations.append("✨ 良好な品質を維持しています")
            else:
                recommendations.append("💪 品質スコア向上の余地があります")

        # 成功パターンからの提案
        if success:
            latest_success = success[-1]
            if "best_practices" in latest_success:
                recommendations.append("✅ 最新の成功パターンのベストプラクティスを継続してください")

        # 失敗パターンからの提案
        if failure:
            recommendations.append("⚠️ 失敗パターンが検出されました。リトライ戦略の見直しを推奨します")
        else:
            recommendations.append("🎯 失敗パターンなし - 安定稼働中です！")

        # 次のアクション
        recommendations.append("📌 Day 6: GitHub Actions自動実行設定に進みましょう")

        return recommendations

    def create_learning_report(self, analysis: Dict) -> str:
        """学習レポートを作成"""
        report = f"""# 🧠 Self Learning Report - Day 5

**生成日時**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

---

## 📊 システムパフォーマンス

### 実行統計
- **総実行回数**: {analysis['total_executions']}回
- **総投稿数**: {analysis['total_posts_created']}社
- **平均品質スコア**: {analysis['average_quality_score']:.1f}/10

### パターン分析
- **総パターン数**: {analysis['total_patterns']}
- **成功パターン**: {analysis['success_count']}
- **部分成功**: {analysis['partial_count']}
- **失敗パターン**: {analysis['failure_count']}
- **成功率**: {analysis['success_rate']:.1f}%

---

## ✅ 共通成功条件

"""
        for condition in analysis["common_success_conditions"]:
            report += f"- {condition}\n"

        if analysis["best_practices"]:
            report += "\n---\n\n## 🎯 ベストプラクティス\n\n"
            for practice in analysis["best_practices"]:
                report += f"- {practice}\n"

        if analysis["common_failure_causes"]:
            report += "\n---\n\n## ❌ 失敗原因（過去）\n\n"
            for cause in analysis["common_failure_causes"]:
                report += f"- {cause}\n"

        report += "\n---\n\n## 💡 改善提案\n\n"
        for rec in analysis["recommendations"]:
            report += f"{rec}\n\n"

        report += f"""---

## 📈 学習効果

このシステムは実行ごとに学習し、以下の情報を蓄積しています：

1. **成功パターン**: 品質スコア9.0以上の実行条件を記録
2. **失敗パターン**: エラー発生時の状況を分析
3. **ベストプラクティス**: 高品質な結果を生み出す方法論

### 次回実行時の改善
- 過去の成功パターンを自動適用
- 失敗パターンを回避する戦略を自動選択
- 品質スコアの継続的向上

---

**生成元**: WordPress自動化 Self Learning System v1.0
"""

        # ファイル保存
        filename = f'{self.learning_log_path}/learning_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"📄 学習レポート保存: {filename}")

        return report
