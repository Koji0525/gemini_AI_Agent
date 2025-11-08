# tools/progress_tracker.py
import json
from datetime import datetime
from pathlib import Path

class ProgressTracker:
    def __init__(self):
        project_root = Path(__file__).resolve().parent.parent
        self.progress_file = project_root / "docs" / "progress_status.json"
        self.setup_progress_tracking()

    def setup_progress_tracking(self):
        """進捗追跡の初期設定"""
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.progress_file.exists():
            initial_status = {
                "project_start_date": "2025-11-08",
                "last_updated": "2025-11-08",
                "current_phase": "Phase 0",
                "overall_progress": 0,
                "phases": {
                    "phase_0": {"name": "環境設定", "progress": 0, "tasks": {}},
                    "phase_1": {"name": "コア基盤構築", "progress": 0, "tasks": {}},
                    "phase_2": {"name": "機能統合", "progress": 0, "tasks": {}},
                    "phase_3": {"name": "最適化", "progress": 0, "tasks": {}},
                    "phase_4": {"name": "本番導入", "progress": 0, "tasks": {}}
                },
                "key_metrics": {
                    "code_lines": 0,
                    "tests_passing": 0,
                    "features_completed": 0,
                    "bugs_fixed": 0
                }
            }
            self.save_progress(initial_status)

    def load_progress(self):
        """進捗データを読み込む"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def save_progress(self, progress_data):
        """進捗データを保存"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, indent=4, ensure_ascii=False)

    def update_task_status(self, phase: str, task_id: str, completed: bool = True):
        """タスクの進捗状況を更新"""
        progress = self.load_progress()

        # Phase key mapping
        phase_map = {
            "Phase 0": "phase_0", "Phase 1": "phase_1", "Phase 2": "phase_2",
            "Phase 3": "phase_3", "Phase 4": "phase_4"
        }
        phase_key = phase_map.get(phase, phase)

        if phase_key in progress["phases"]:
            if task_id not in progress["phases"][phase_key]["tasks"]:
                progress["phases"][phase_key]["tasks"][task_id] = {
                    "completed": completed,
                    "completed_date": datetime.now().isoformat() if completed else None
                }
            else:
                task = progress["phases"][phase_key]["tasks"][task_id]
                task["completed"] = completed
                task["completed_date"] = datetime.now().isoformat() if completed else None


            # 進捗率を再計算
            total_tasks = len(progress["phases"][phase_key]["tasks"])
            completed_tasks = sum(1 for t in progress["phases"][phase_key]["tasks"].values() if t["completed"])
            progress["phases"][phase_key]["progress"] = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            # 全体進捗を更新
            self.update_overall_progress(progress)
            self.save_progress(progress)

    def update_overall_progress(self, progress):
        """全体進捗率を計算"""
        phase_weights = {
            "phase_0": 0.1, # 10%
            "phase_1": 0.3, # 30%
            "phase_2": 0.3, # 30%
            "phase_3": 0.2, # 20%
            "phase_4": 0.1 # 10%
        }

        total_progress = 0
        for phase, weight in phase_weights.items():
            total_progress += progress["phases"][phase]["progress"] * weight

        progress["overall_progress"] = round(total_progress, 2)
        progress["last_updated"] = datetime.now().isoformat()
