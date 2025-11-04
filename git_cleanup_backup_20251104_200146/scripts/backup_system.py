"""
システムバックアップ
重要なデータを定期的にバックアップ
"""

import shutil
from datetime import datetime
from pathlib import Path


def backup_system():
    """システムをバックアップ"""
    print("=" * 70)
    print("💾 システムバックアップ開始")
    print(f"実行時刻: {datetime.now()}")
    print("=" * 70)

    backup_dir = Path("_BACKUP") / datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir.mkdir(parents=True, exist_ok=True)

    # バックアップ対象
    targets = ["agents/", "config/", "scripts/", "logs/"]

    backed_up = []
    for target in targets:
        target_path = Path(target)
        if target_path.exists():
            dest = backup_dir / target
            if target_path.is_dir():
                shutil.copytree(target_path, dest)
            else:
                shutil.copy2(target_path, dest)
            backed_up.append(target)
            print(f"✅ {target} をバックアップ")

    print(f"\n📦 バックアップ先: {backup_dir}")
    print(f"📊 バックアップ項目数: {len(backed_up)}件")
    print("\n" + "=" * 70)
    print("✅ バックアップ完了")
    print("=" * 70)


if __name__ == "__main__":
    backup_system()
