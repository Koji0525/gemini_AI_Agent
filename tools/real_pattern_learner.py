#!/usr/bin/env python3
"""
実データパターン学習エンジン（実データ適応版）
変更理由: status='completed'/'failed' に対応、knowledge_baseのsuccess_rateも活用
"""

import sys
from pathlib import Path
from collections import Counter
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.sheets_manager import GoogleSheetsManager


class RealPatternLearner:
    def __init__(self):
        self.sheets_manager = GoogleSheetsManager()
        self.patterns = []

    def analyze_all_data(self):
        print("🔍 実データ分析開始")
        print("=" * 60)

        task_patterns = self._analyze_task_patterns()
        knowledge_patterns = self._analyze_knowledge_patterns()

        self.patterns = sorted(task_patterns + knowledge_patterns, key=lambda x: x["confidence"], reverse=True)

        return self.patterns

    def _analyze_task_patterns(self):
        print("\n📊 タスク実行ログを分析中...")
        patterns = []

        try:
            data = self.sheets_manager.read_range("task_execution_log")
            if not data or len(data) <= 1:
                return patterns

            headers = data[0]
            rows = data[1:]

            status_idx = headers.index("status") if "status" in headers else -1

            if status_idx != -1:
                # 実データ構造に適応: 'completed'/'failed'
                statuses = [row[status_idx] for row in rows if len(row) > status_idx]

                total = len(statuses)
                completed = sum(1 for s in statuses if s.lower() == "completed")
                failed = sum(1 for s in statuses if s.lower() == "failed")

                print(f"✅ 総タスク数: {total}件")
                print(f"   完了: {completed}件 ({completed/total*100:.1f}%)")
                print(f"   失敗: {failed}件 ({failed/total*100:.1f}%)")

                # 成功率を計算
                success_rate = completed / total if total > 0 else 0

                # パターン1: 高成功率タスク
                if success_rate >= 0.90:
                    patterns.append(
                        {
                            "name": "高成功率タスク実行パターン",
                            "type": "success_pattern",
                            "confidence": success_rate,
                            "applicable_count": completed,
                            "description": f"現在の成功率{success_rate*100:.1f}%を維持する実行パターン",
                        }
                    )

                # パターン2: 失敗タスクの再試行
                if failed > 0:
                    # 再試行成功率を推定（一般的に70-85%）
                    retry_success_rate = 0.80
                    patterns.append(
                        {
                            "name": "失敗タスクの自動再試行",
                            "type": "retry_pattern",
                            "confidence": retry_success_rate,
                            "applicable_count": failed,
                            "description": f"{failed}件の失敗タスクに再試行を適用（推定成功率80%）",
                        }
                    )

                # パターン3: エージェント別分析
                agent_idx = headers.index("agent_role") if "agent_role" in headers else -1
                if agent_idx != -1:
                    agents = [row[agent_idx] for row in rows if len(row) > agent_idx and row[agent_idx]]
                    agent_counter = Counter(agents)

                    print(f"\n👥 エージェント別実行数:")
                    for agent, count in agent_counter.most_common():
                        print(f"   • {agent}: {count}件")

                        if count >= 20:
                            patterns.append(
                                {
                                    "name": f"{agent}エージェントの専門化",
                                    "type": "optimization",
                                    "confidence": min(0.75, count / total),
                                    "applicable_count": count,
                                    "description": f"{agent}エージェント向けの最適化が効果的",
                                }
                            )

        except Exception as e:
            print(f"❌ タスク分析エラー: {e}")

        return patterns

    def _analyze_knowledge_patterns(self):
        print("\n📚 ナレッジベースを分析中...")
        patterns = []

        try:
            data = self.sheets_manager.read_range("knowledge_base")
            if not data or len(data) <= 1:
                return patterns

            headers = data[0]
            rows = data[1:]

            print(f"✅ ナレッジエントリ: {len(rows)}件")

            # success_rate列を活用
            success_rate_idx = headers.index("success_rate") if "success_rate" in headers else -1
            knowledge_type_idx = headers.index("knowledge_type") if "knowledge_type" in headers else -1

            if success_rate_idx != -1:
                success_rates = []
                for row in rows:
                    if len(row) > success_rate_idx:
                        try:
                            rate = float(row[success_rate_idx])
                            if rate > 0:
                                success_rates.append(rate)
                        except (ValueError, TypeError):
                            pass

                if success_rates:
                    avg_success_rate = sum(success_rates) / len(success_rates)
                    print(f"   平均成功率: {avg_success_rate:.1f}%")

                    # 高成功率パターンを抽出
                    high_success = [r for r in success_rates if r >= 90]
                    if high_success:
                        patterns.append(
                            {
                                "name": "高成功率ナレッジの活用",
                                "type": "knowledge_application",
                                "confidence": avg_success_rate / 100,
                                "applicable_count": len(high_success),
                                "description": f"{len(high_success)}件の高成功率パターンを活用可能",
                            }
                        )

            # knowledge_type別の分析
            if knowledge_type_idx != -1:
                types = [row[knowledge_type_idx] for row in rows if len(row) > knowledge_type_idx]
                type_counter = Counter(types)

                print(f"\n📊 ナレッジタイプ別分布:")
                for ktype, count in type_counter.most_common():
                    print(f"   • {ktype}: {count}件 ({count/len(rows)*100:.1f}%)")

                    if count >= 50:
                        patterns.append(
                            {
                                "name": f"{ktype}パターンの体系化",
                                "type": "knowledge_organization",
                                "confidence": 0.70,
                                "applicable_count": count,
                                "description": f"{ktype}タイプの{count}件を体系的に活用",
                            }
                        )

        except Exception as e:
            print(f"❌ ナレッジ分析エラー: {e}")

        return patterns

    def save_patterns(self):
        print("\n💾 学習パターンを保存中...")

        try:
            values = [["timestamp", "pattern_name", "confidence", "applicable_count", "description"]]

            timestamp = datetime.now().isoformat()
            for pattern in self.patterns:
                values.append(
                    [
                        timestamp,
                        pattern["name"],
                        f"{pattern['confidence']:.2f}",
                        str(pattern["applicable_count"]),
                        pattern["description"],
                    ]
                )

            self.sheets_manager.write_range("learning_patterns", values)
            print(f"✅ {len(self.patterns)}件のパターンを保存")

        except Exception as e:
            print(f"❌ 保存エラー: {e}")

    def generate_report(self):
        print("\n" + "=" * 60)
        print("📈 パターン学習レポート")
        print("=" * 60)

        if not self.patterns:
            print("⚠️ パターンが見つかりませんでした")
            return

        print(f"\n🎯 発見されたパターン: {len(self.patterns)}件\n")

        for i, pattern in enumerate(self.patterns, 1):
            print(f"{i}. {pattern['name']}")
            print(f"   信頼度: {pattern['confidence']:.0%}")
            print(f"   適用可能: {pattern['applicable_count']}件")
            print(f"   説明: {pattern['description']}")
            print()

        # 推奨アクション
        print("💡 推奨アクション（上位3件）:")
        high_confidence = [p for p in self.patterns if p["confidence"] >= 0.70]
        for i, pattern in enumerate(high_confidence[:3], 1):
            print(f"   {i}. {pattern['name']} (信頼度{pattern['confidence']:.0%})")


def main():
    print("🚀 実データパターン学習エンジン起動")
    learner = RealPatternLearner()

    patterns = learner.analyze_all_data()
    learner.save_patterns()
    learner.generate_report()

    print("\n🎉 パターン学習完了")
    return len(patterns)


if __name__ == "__main__":
    sys.exit(0 if main() > 0 else 1)
