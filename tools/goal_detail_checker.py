"""ゴール詳細度チェッカー"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse

from tools.base_data_accessor import BaseDataAccessor


def check_goal_detail(goal_description: str) -> float:
    """
    ゴール詳細度スコア算出 (0.0 - 1.0)

    評価項目:
    - 具体的な技術スタック記載: 20%
    - 機能一覧の明確さ: 20%
    - 成果物の定義: 20%
    - 期限/スケジュール: 20%
    - 制約条件の明示: 20%
    """
    score = 0.0
    desc_lower = goal_description.lower()

    # 技術スタック
    tech_keywords = ["python", "cli", "api", "react", "vue", "node", "django", "flask"]
    if any(tech in desc_lower for tech in tech_keywords):
        score += 0.2

    # 機能一覧（複数の項目がカンマ/句点で区切られている）
    if len(goal_description.split("、")) >= 3 or len(goal_description.split("。")) >= 3:
        score += 0.2

    # 成果物
    deliverable_keywords = ["ツール", "システム", "アプリ", "サイト", "プラットフォーム"]
    if any(word in goal_description for word in deliverable_keywords):
        score += 0.2

    # 期限/スケジュール
    schedule_keywords = ["日", "週間", "ヶ月", "月", "phase", "フェーズ"]
    if any(word in desc_lower for word in schedule_keywords):
        score += 0.2

    # 制約条件
    constraint_keywords = ["mvp", "最小", "段階", "優先", "v1", "v2"]
    if any(word in desc_lower for word in constraint_keywords):
        score += 0.2

    return score


def main():
    parser = argparse.ArgumentParser(description="ゴール詳細度チェック")
    parser.add_argument("--goal-id", type=str, required=True, help="ゴールID")

    args = parser.parse_args()

    # ゴール取得
    accessor = BaseDataAccessor()
    goals = accessor.read_sheet_as_dicts("project_goal")

    goal = None
    for g in goals:
        if str(g.get("goal_id")) == str(args.goal_id):
            goal = g
            break

    if not goal:
        print(f"❌ ゴール{args.goal_id}が見つかりません")
        sys.exit(1)

    # 詳細度チェック
    description = goal.get("goal_description", "")
    score = check_goal_detail(description)

    print("=" * 80)
    print(f"📊 ゴール{args.goal_id}詳細度チェック")
    print("=" * 80)
    print(f"\nゴール: {description[:60]}...")
    print(f"\n詳細度スコア: {score:.1%}")
    print("\n評価:")

    if score >= 0.8:
        print("  ✅ 非常に詳細（すぐにタスク生成可能）")
        sys.exit(0)
    elif score >= 0.5:
        print("  ✅ 十分に詳細（タスク生成可能）")
        sys.exit(0)
    elif score >= 0.3:
        print("  ⚠️ やや不足（要件定義推奨）")
        sys.exit(1)
    else:
        print("  ❌ 不十分（要件定義必須）")
        sys.exit(1)


if __name__ == "__main__":
    main()
