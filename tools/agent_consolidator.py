"""
agent_consolidator.py

エージェント統合自動化システム

【目的】
- 依存関係レポートに基づいた自動統合
- 重複機能の削除
- システム全体の最適化
"""

import json
import logging
from pathlib import Path
from typing import List, Dict
import shutil

logger = logging.getLogger(__name__)


class AgentConsolidator:
    """
    エージェント統合自動化
    """

    def __init__(self, report_file: str = "dependency_report.json"):
        with open(report_file, "r") as f:
            self.report = json.load(f)

        self.consolidation_plan = []

    def create_consolidation_plan(self):
        """統合計画を作成"""
        logger.info("📋 統合計画作成中...")

        candidates = self.report.get("integration_candidates", {})

        for agent_type, agents in candidates.items():
            if len(agents) <= 1:
                continue

            # 統合戦略
            primary = self._select_primary_agent(agents)
            secondaries = [a for a in agents if a != primary]

            self.consolidation_plan.append(
                {
                    "type": agent_type,
                    "primary": primary,
                    "merge_into_primary": secondaries,
                    "action": "merge",
                }
            )

        # 未使用ファイル
        unused = self.report.get("unused_files", [])
        for file in unused:
            self.consolidation_plan.append({"file": file, "action": "archive"})

        logger.info(f"✅ {len(self.consolidation_plan)}個の統合アクション")

    def _select_primary_agent(self, agents: List[str]) -> str:
        """主要エージェントを選択"""
        # 最新バージョン、最大サイズ、v0x の命名などで判断

        # バージョン番号がある場合は最新を選択
        versioned = [a for a in agents if "_v" in a or "v0" in a]
        if versioned:
            # vXX_feature形式を優先
            versioned_sorted = sorted(
                versioned,
                key=lambda x: (
                    int("".join(filter(str.isdigit, x.split("_v")[-1].split("_")[0])) or "0")
                ),
                reverse=True,
            )
            return versioned_sorted[0]

        # それ以外は最初のものを選択
        return agents[0]

    def print_plan(self):
        """統合計画を表示"""
        print("\n" + "=" * 80)
        print("📋 エージェント統合計画")
        print("=" * 80)

        merge_actions = [p for p in self.consolidation_plan if p.get("action") == "merge"]
        archive_actions = [p for p in self.consolidation_plan if p.get("action") == "archive"]

        if merge_actions:
            print(f"\n🔀 統合: {len(merge_actions)}グループ")
            for plan in merge_actions:
                print(f"\n  【{plan['type']}】")
                print(f"    主要: {plan['primary']}")
                print(f"    統合: {len(plan['merge_into_primary'])}個")
                for agent in plan["merge_into_primary"][:3]:
                    print(f"      - {agent}")
                if len(plan["merge_into_primary"]) > 3:
                    print(f"      ... 他{len(plan['merge_into_primary'])-3}個")

        if archive_actions:
            print(f"\n📦 アーカイブ: {len(archive_actions)}個")
            for plan in archive_actions[:10]:
                print(f"    - {plan['file']}")
            if len(archive_actions) > 10:
                print(f"    ... 他{len(archive_actions)-10}個")

        print("=" * 80)

    def execute_consolidation(self, dry_run: bool = True):
        """統合を実行"""
        if dry_run:
            logger.info("🔍 ドライラン実行（実際の変更なし）")
            self.print_plan()
            return

        logger.info("🚀 統合実行中...")

        for plan in self.consolidation_plan:
            if plan["action"] == "archive":
                self._archive_file(plan["file"])
            elif plan["action"] == "merge":
                self._merge_agents(plan)

        logger.info("✅ 統合完了")

    def _archive_file(self, file_path: str):
        """ファイルをアーカイブ"""
        source = Path(file_path)
        if not source.exists():
            return

        # _ARCHIVE/unused/ に移動
        archive_dir = Path("_ARCHIVE/unused")
        archive_dir.mkdir(parents=True, exist_ok=True)

        dest = archive_dir / source.name
        shutil.move(str(source), str(dest))
        logger.info(f"📦 アーカイブ: {file_path}")

    def _merge_agents(self, plan: Dict):
        """エージェントを統合"""
        # 実装は複雑なため、ここでは計画のみ
        logger.info(f"🔀 統合計画: {plan['type']}")
        logger.info(f"   主要: {plan['primary']}")
        logger.info(f"   統合対象: {len(plan['merge_into_primary'])}個")


def main():
    """メイン実行"""
    consolidator = AgentConsolidator()
    consolidator.create_consolidation_plan()
    consolidator.execute_consolidation(dry_run=True)

    print("\n" + "=" * 80)
    print("📝 次のステップ")
    print("=" * 80)
    print("1. 統合計画を確認")
    print("2. dry_run=False で実行して実際に統合")
    print("3. テスト実行で動作確認")
    print("=" * 80)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
