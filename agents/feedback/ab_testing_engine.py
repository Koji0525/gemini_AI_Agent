"""
AB Testing Engine v1.0
改善提案の効果をA/Bテストで検証
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import math
from scipy import stats
import numpy as np

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import ConfigLoader


class ABTestingEngine:
    """A/Bテスト実験の設計・実行・分析エンジン"""

    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets = sheets_manager
        self.alpha = 0.05  # 有意水準（5%）
        self.min_sample_size = 30  # 最小サンプルサイズ

    async def create_experiment(
        self, suggestion_id: str, variant_a_description: str, variant_b_description: str, metric: str = "success_rate"
    ) -> Dict[str, Any]:
        """A/Bテスト実験を作成"""

        print(f"🧪 A/Bテスト実験を作成中...")
        print(f"   提案ID: {suggestion_id}")
        print(f"   バリアントA: {variant_a_description[:50]}...")
        print(f"   バリアントB: {variant_b_description[:50]}...")

        experiment = {
            "experiment_id": f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "suggestion_id": suggestion_id,
            "start_date": datetime.now().isoformat(),
            "end_date": None,
            "variant_a_description": variant_a_description,
            "variant_b_description": variant_b_description,
            "metric": metric,
            "variant_a_results": [],
            "variant_b_results": [],
            "status": "running",
        }

        print(f"   ✅ 実験ID: {experiment['experiment_id']}")

        return experiment

    def calculate_sample_size(self, baseline_rate: float, expected_improvement: float, power: float = 0.8) -> int:
        """必要なサンプルサイズを計算"""

        # 効果量の計算
        p1 = baseline_rate
        p2 = baseline_rate * (1 + expected_improvement)

        # Cohen's h（効果量）
        effect_size = 2 * (math.asin(math.sqrt(p2)) - math.asin(math.sqrt(p1)))

        # サンプルサイズ計算（簡易版）
        z_alpha = stats.norm.ppf(1 - self.alpha / 2)
        z_beta = stats.norm.ppf(power)

        n = ((z_alpha + z_beta) ** 2) / (effect_size**2)
        n = math.ceil(n)

        return max(n, self.min_sample_size)

    def add_observation(self, experiment: Dict[str, Any], variant: str, success: bool):
        """観測データを追加"""

        if variant == "A":
            experiment["variant_a_results"].append(1 if success else 0)
        elif variant == "B":
            experiment["variant_b_results"].append(1 if success else 0)
        else:
            raise ValueError(f"Invalid variant: {variant}")

    def analyze_results(self, experiment: Dict[str, Any]) -> Dict[str, Any]:
        """A/Bテスト結果を統計分析"""

        print(f"\n📊 実験結果を分析中: {experiment['experiment_id']}")

        a_results = experiment["variant_a_results"]
        b_results = experiment["variant_b_results"]

        # サンプルサイズチェック
        if len(a_results) < self.min_sample_size or len(b_results) < self.min_sample_size:
            return {
                "status": "insufficient_data",
                "message": f"サンプルサイズ不足（最低{self.min_sample_size}件必要）",
                "variant_a_n": len(a_results),
                "variant_b_n": len(b_results),
            }

        # 成功率の計算
        a_success_rate = sum(a_results) / len(a_results) if a_results else 0
        b_success_rate = sum(b_results) / len(b_results) if b_results else 0

        # 改善率
        improvement = ((b_success_rate - a_success_rate) / a_success_rate * 100) if a_success_rate > 0 else 0

        # 統計的検定（二項検定）
        if len(a_results) > 0 and len(b_results) > 0:
            # カイ二乗検定
            contingency_table = [
                [sum(a_results), len(a_results) - sum(a_results)],
                [sum(b_results), len(b_results) - sum(b_results)],
            ]

            chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

            # 統計的有意性
            is_significant = p_value < self.alpha

            # 信頼区間の計算（簡易版）
            z = stats.norm.ppf(1 - self.alpha / 2)

            # バリアントAの信頼区間
            a_se = math.sqrt(a_success_rate * (1 - a_success_rate) / len(a_results))
            a_ci_lower = max(0, a_success_rate - z * a_se)
            a_ci_upper = min(1, a_success_rate + z * a_se)

            # バリアントBの信頼区間
            b_se = math.sqrt(b_success_rate * (1 - b_success_rate) / len(b_results))
            b_ci_lower = max(0, b_success_rate - z * b_se)
            b_ci_upper = min(1, b_success_rate + z * b_se)

        else:
            p_value = 1.0
            is_significant = False
            a_ci_lower = a_ci_upper = a_success_rate
            b_ci_lower = b_ci_upper = b_success_rate

        # numpy型をPython型に変換（JSON serializable）
        analysis = {
            "status": "complete",
            "variant_a_success_rate": float(round(a_success_rate * 100, 2)),
            "variant_b_success_rate": float(round(b_success_rate * 100, 2)),
            "improvement": float(round(improvement, 2)),
            "sample_size_a": int(len(a_results)),
            "sample_size_b": int(len(b_results)),
            "p_value": float(round(p_value, 4)),
            "is_significant": bool(is_significant),
            "confidence_level": float((1 - self.alpha) * 100),
            "variant_a_ci": (float(round(a_ci_lower * 100, 2)), float(round(a_ci_upper * 100, 2))),
            "variant_b_ci": (float(round(b_ci_lower * 100, 2)), float(round(b_ci_upper * 100, 2))),
        }

        print(f"   バリアントA成功率: {analysis['variant_a_success_rate']}%")
        print(f"   バリアントB成功率: {analysis['variant_b_success_rate']}%")
        print(f"   改善率: {analysis['improvement']}%")
        print(f"   p値: {analysis['p_value']}")
        print(f"   統計的有意性: {'✅ 有意' if is_significant else '❌ 非有意'}")

        return analysis

    def make_decision(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """採用/却下の判定"""

        print(f"\n🎯 判定を実行中...")

        if analysis["status"] == "insufficient_data":
            decision = {
                "decision": "continue_testing",
                "reason": "サンプルサイズが不足しています",
                "recommendation": f"各バリアントあと{self.min_sample_size - analysis['variant_a_n']}件のデータが必要",
            }

        elif not analysis["is_significant"]:
            decision = {
                "decision": "keep_a",
                "reason": "統計的有意差が認められません",
                "recommendation": "現行バージョン（A）を維持",
            }

        elif analysis["improvement"] > 5:  # 5%以上の改善
            decision = {
                "decision": "adopt_b",
                "reason": f"統計的に有意な改善が確認されました（{analysis['improvement']}%向上）",
                "recommendation": "バリアントBを採用",
            }

        elif analysis["improvement"] > 0:
            decision = {
                "decision": "adopt_b_cautiously",
                "reason": f"わずかな改善が確認されました（{analysis['improvement']}%向上）",
                "recommendation": "バリアントBを段階的に導入",
            }

        else:
            decision = {
                "decision": "keep_a",
                "reason": "改善が認められません",
                "recommendation": "現行バージョン（A）を維持",
            }

        # 判定アイコン
        decision_icon = {"adopt_b": "✅", "adopt_b_cautiously": "⚠️", "keep_a": "❌", "continue_testing": "🔄"}

        print(f"   {decision_icon.get(decision['decision'], '❓')} 判定: {decision['decision']}")
        print(f"   理由: {decision['reason']}")
        print(f"   推奨: {decision['recommendation']}")

        return decision

    async def save_experiment_to_sheet(
        self, experiment: Dict[str, Any], analysis: Dict[str, Any], decision: Dict[str, Any]
    ) -> bool:
        """実験結果をGoogle Sheetsに保存"""

        print(f"\n💾 実験結果をGoogle Sheetsに保存中...")

        try:
            spreadsheet = self.sheets.gc.open_by_key(self.sheets.spreadsheet_id)
            worksheet = spreadsheet.worksheet("ab_test_results")

            row = [
                experiment["experiment_id"],
                experiment["suggestion_id"],
                experiment["start_date"],
                datetime.now().isoformat(),  # end_date
                experiment["variant_a_description"][:200],
                experiment["variant_b_description"][:200],
                analysis.get("variant_a_success_rate", 0),
                analysis.get("variant_b_success_rate", 0),
                analysis.get("sample_size_a", 0) + analysis.get("sample_size_b", 0),
                analysis.get("p_value", 1.0),
                "有意" if analysis.get("is_significant", False) else "非有意",
                decision["decision"],
            ]

            worksheet.append_row(row)

            print(f"   ✅ 実験結果を保存しました")
            return True

        except Exception as e:
            print(f"   ❌ 保存エラー: {e}")
            return False

    def simulate_experiment(
        self, baseline_success_rate: float, improvement_rate: float, sample_size: int = 100
    ) -> Tuple[List[int], List[int]]:
        """実験データをシミュレート（テスト用）"""

        # バリアントAの結果
        variant_a = np.random.binomial(1, baseline_success_rate, sample_size).tolist()

        # バリアントBの結果（改善版）
        improved_rate = baseline_success_rate * (1 + improvement_rate)
        improved_rate = min(improved_rate, 1.0)  # 上限1.0
        variant_b = np.random.binomial(1, improved_rate, sample_size).tolist()

        return variant_a, variant_b

    def print_experiment_summary(self, experiment: Dict[str, Any], analysis: Dict[str, Any], decision: Dict[str, Any]):
        """実験結果のサマリーを表示"""

        print("\n" + "=" * 70)
        print("🧪 A/Bテスト実験結果サマリー")
        print("=" * 70)

        print(f"\n実験ID: {experiment['experiment_id']}")
        print(f"提案ID: {experiment['suggestion_id']}")
        print(f"開始: {experiment['start_date']}")

        print(f"\n📊 結果:")
        print(f"  バリアントA（現行）:")
        print(f"    成功率: {analysis['variant_a_success_rate']}%")
        print(f"    95%信頼区間: [{analysis['variant_a_ci'][0]}%, {analysis['variant_a_ci'][1]}%]")
        print(f"    サンプル数: {analysis['sample_size_a']}")

        print(f"\n  バリアントB（改善版）:")
        print(f"    成功率: {analysis['variant_b_success_rate']}%")
        print(f"    95%信頼区間: [{analysis['variant_b_ci'][0]}%, {analysis['variant_b_ci'][1]}%]")
        print(f"    サンプル数: {analysis['sample_size_b']}")

        print(f"\n  改善率: {analysis['improvement']:+.2f}%")
        print(f"  p値: {analysis['p_value']}")
        print(f"  統計的有意性: {'✅ 有意' if analysis['is_significant'] else '❌ 非有意'} (α={self.alpha})")

        print(f"\n🎯 判定:")
        decision_icon = {"adopt_b": "✅", "adopt_b_cautiously": "⚠️", "keep_a": "❌", "continue_testing": "🔄"}
        print(f"  {decision_icon.get(decision['decision'], '❓')} {decision['decision']}")
        print(f"  理由: {decision['reason']}")
        print(f"  推奨: {decision['recommendation']}")

        print("\n" + "=" * 70)


async def main():
    """メイン実行（デモ）"""
    print("🚀 AB Testing Engine を起動\n")

    # 設定読み込み
    config = ConfigLoader()
    sheets = GoogleSheetsManager(
        spreadsheet_id=config.get("SPREADSHEET_ID"), service_account_file=config.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    )

    # ABテストエンジン
    ab_engine = ABTestingEngine(sheets)

    print("=" * 70)
    print("🧪 デモ: A/Bテスト実験のシミュレーション")
    print("=" * 70)

    # === デモ実験1: 有意な改善がある場合 ===
    print("\n【実験1】有意な改善が期待される場合")
    print("-" * 70)

    # 実験作成
    experiment1 = await ab_engine.create_experiment(
        suggestion_id="sug_20251029_001",
        variant_a_description="現行システム（タイムアウト30秒）",
        variant_b_description="改善版（タイムアウト60秒、リトライ追加）",
        metric="success_rate",
    )

    # データシミュレート（現行89.8% → 改善版95%）
    baseline_rate = 0.898
    improvement = 0.06  # 6%改善

    variant_a_data, variant_b_data = ab_engine.simulate_experiment(baseline_rate, improvement, sample_size=100)

    experiment1["variant_a_results"] = variant_a_data
    experiment1["variant_b_results"] = variant_b_data

    # 分析
    analysis1 = ab_engine.analyze_results(experiment1)
    decision1 = ab_engine.make_decision(analysis1)

    # 結果表示
    ab_engine.print_experiment_summary(experiment1, analysis1, decision1)

    # Google Sheetsに保存
    await ab_engine.save_experiment_to_sheet(experiment1, analysis1, decision1)

    # === デモ実験2: 改善が見られない場合 ===
    print("\n\n【実験2】改善が見られない場合")
    print("-" * 70)

    experiment2 = await ab_engine.create_experiment(
        suggestion_id="sug_20251029_002",
        variant_a_description="現行ログ形式",
        variant_b_description="詳細ログ形式",
        metric="success_rate",
    )

    # データシミュレート（ほぼ同じ）
    variant_a_data2, variant_b_data2 = ab_engine.simulate_experiment(
        baseline_rate, 0.01, sample_size=100  # わずか1%改善
    )

    experiment2["variant_a_results"] = variant_a_data2
    experiment2["variant_b_results"] = variant_b_data2

    # 分析
    analysis2 = ab_engine.analyze_results(experiment2)
    decision2 = ab_engine.make_decision(analysis2)

    # 結果表示
    ab_engine.print_experiment_summary(experiment2, analysis2, decision2)

    # Google Sheetsに保存
    await ab_engine.save_experiment_to_sheet(experiment2, analysis2, decision2)

    # JSONで保存（numpy型を除外）
    output_file = Path("agent_outputs/ab_test_results.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # JSON保存用に結果をクリーンアップ（resultsは保存しない）
    results = {
        "experiments": [
            {
                "experiment": {
                    "experiment_id": experiment1["experiment_id"],
                    "suggestion_id": experiment1["suggestion_id"],
                    "start_date": experiment1["start_date"],
                    "variant_a_description": experiment1["variant_a_description"],
                    "variant_b_description": experiment1["variant_b_description"],
                    "metric": experiment1["metric"],
                },
                "analysis": analysis1,
                "decision": decision1,
            },
            {
                "experiment": {
                    "experiment_id": experiment2["experiment_id"],
                    "suggestion_id": experiment2["suggestion_id"],
                    "start_date": experiment2["start_date"],
                    "variant_a_description": experiment2["variant_a_description"],
                    "variant_b_description": experiment2["variant_b_description"],
                    "metric": experiment2["metric"],
                },
                "analysis": analysis2,
                "decision": decision2,
            },
        ]
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 実験結果を保存: {output_file}")

    print("\n" + "=" * 70)
    print("✅ Phase 4-2: ABTestingEngine 完成！")
    print("=" * 70)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
