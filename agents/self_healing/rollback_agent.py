"""
RollbackAgent: システム状態のロールバック機能
"""

import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class RollbackAgent:
    """システム状態のロールバック"""

    def __init__(self, checkpoint_dir: str = ".rollback_backup"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)

    def save_checkpoint(self, state: Dict[str, Any]) -> str:
        """チェックポイント保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_id = f"checkpoint_{timestamp}"
        checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.json"

        with open(checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

        print(f"💾 チェックポイント保存: {checkpoint_id}")
        return checkpoint_id

    def restore_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """チェックポイント復元"""
        checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.json"

        if not checkpoint_path.exists():
            raise FileNotFoundError(f"チェックポイント未発見: {checkpoint_id}")

        with open(checkpoint_path, "r", encoding="utf-8") as f:
            state = json.load(f)

        print(f"♻️ チェックポイント復元: {checkpoint_id}")
        return state

    def rollback_to_safe_state(self) -> bool:
        """最新の安全な状態にロールバック"""
        checkpoints = sorted(self.checkpoint_dir.glob("checkpoint_*.json"))

        if not checkpoints:
            print("⚠️ 利用可能なチェックポイントなし")
            return False

        latest_checkpoint = checkpoints[-1]
        checkpoint_id = latest_checkpoint.stem

        try:
            state = self.restore_checkpoint(checkpoint_id)
            print(f"✅ ロールバック成功: {checkpoint_id}")
            return True
        except Exception as e:
            print(f"❌ ロールバック失敗: {e}")
            return False
