"""
進捗表示ツール
MASTER_ROADMAP.mdから進捗を読み取り表示
"""


def show_progress():
    """進捗表示"""
    print("=" * 80)
    print("📊 プロジェクト進捗")
    print("=" * 80)

    phases = {
        "Phase 0": {"completed": 3, "total": 3, "weight": 10},
        "Phase 1": {"completed": 0, "total": 6, "weight": 20},
        "Phase 2": {"completed": 0, "total": 6, "weight": 20},
        "Phase 3": {"completed": 0, "total": 4, "weight": 20},
        "Phase 4": {"completed": 0, "total": 3, "weight": 15},
        "Phase 5": {"completed": 0, "total": 3, "weight": 15},
    }

    total_progress = 0
    total_weight = 0

    for phase, data in phases.items():
        progress = (data["completed"] / data["total"]) * 100
        weighted_progress = progress * data["weight"] / 100

        total_progress += weighted_progress
        total_weight += data["weight"]

        bar = "█" * int(progress / 5) + "░" * (20 - int(progress / 5))

        print(f"\n{phase}")
        print(f"  [{bar}] {progress:.1f}%")
        print(f"  完了: {data['completed']}/{data['total']} タスク")

    overall = total_progress / total_weight * 100

    print("\n" + "=" * 80)
    print(f"全体進捗: {overall:.1f}%")
    print("=" * 80)


if __name__ == "__main__":
    show_progress()
