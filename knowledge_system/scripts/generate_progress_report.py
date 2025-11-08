# scripts/generate_progress_report.py
import sys
import os
from datetime import datetime

# Add the project root to the Python path to allow importing from 'tools'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.progress_tracker import ProgressTracker

def get_recent_activities(progress):
    """Fetches a summary of recent activities."""
    activities = []
    for phase_id, phase_data in progress['phases'].items():
        for task_id, task_data in phase_data.get('tasks', {}).items():
            if task_data.get('completed'):
                activities.append(
                    (task_data['completed_date'],
                     f"Completed task '{task_id}' in phase '{phase_data['name']}'")
                )

    # Sort activities by date, most recent first
    activities.sort(key=lambda x: x[0], reverse=True)

    # Return the top 5 recent activities
    return "\n".join([f"- {activity[1]}" for activity in activities[:5]])


def generate_progress_report():
    """進捗レポートを生成"""
    tracker = ProgressTracker()
    progress = tracker.load_progress()

    if not progress:
        return "Progress file not found. Please initialize the tracker first."

    report = f"""
# 📊 ナレッジ管理システム 進捗レポート
**生成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**全体進捗**: {progress.get('overall_progress', 0)}%

## フェーズ別進捗状況
"""

    for phase_id, phase_data in progress.get("phases", {}).items():
        progress_percent = phase_data.get('progress', 0)
        status_icon = "✅" if progress_percent == 100 else "🟡" if progress_percent > 0 else "⚪"
        report += f"- {status_icon} {phase_data.get('name', 'N/A')}: {progress_percent}%\n"

    report += f"""
## 主要指標
- 実装コード行数: {progress.get('key_metrics', {}).get('code_lines', 0)}
- テスト合格率: {progress.get('key_metrics', {}).get('tests_passing', 0)}%
- 完了機能数: {progress.get('key_metrics', {}).get('features_completed', 0)}
- 修正バグ数: {progress.get('key_metrics', {}).get('bugs_fixed', 0)}

## 直近の活動
{get_recent_activities(progress)}
"""

    return report

if __name__ == "__main__":
    report = generate_progress_report()
    print(report)
