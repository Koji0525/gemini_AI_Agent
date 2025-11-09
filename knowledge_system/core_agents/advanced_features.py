"""高度な機能（バックアップ等）"""

import shutil
from datetime import datetime
from pathlib import Path


class AdvancedFeaturesAgent:
    """バックアップなどの高度な機能"""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)

    def create_backup(self) -> str:
        """バックアップ作成"""
        backup_dir = self.db_path.parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)

        # データベースをコピー
        if self.db_path.exists():
            shutil.copy2(self.db_path, backup_path / self.db_path.name)

        # FAISSインデックスもコピー
        index_dir = self.db_path.parent / "faiss_index"
        if index_dir.exists():
            shutil.copytree(index_dir, backup_path / "faiss_index", dirs_exist_ok=True)

        return str(backup_path)
