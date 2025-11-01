#!/usr/bin/env python3
"""
Day 7: 24時間監視スクリプト
GitHub Actions実行状況をモニタリング
"""

import json
import os
from datetime import datetime
from typing import List, Dict


class Day7Monitor:
    """24時間テスト監視"""

    def __init__(self):
        self.kb_path = "/workspaces/gemini_AI_Agent/knowledge_base/wordpress_automation"
        self.log_path = "/workspaces/gemini_AI_Agent/uz-manda-portal/logs/day4"

    def get_execution_summary(self) -> Dict:
        """実行サマリーを取得"""

        # 統計読み込み
        stats_file = f"{self.kb_path}/statistics.json"
        if os.path.exists(stats_file):
            with open(stats_file, "r") as f:
                stats = json.load(f)
        else:
            stats = {}

        # 最新ログ読み込み
        latest_logs = []
        if os.path.exists(self.log_path):
            log_files = sorted(os.listdir(self.log_path))[-4:]  # 最新4件
            for log_file in log_files:
                with open(f"{self.log_path}/{log_file}", "r") as f:
                    latest_logs.append(json.load(f))

        return {"stats": stats, "latest_logs": latest_logs, "timestamp": datetime.now().isoformat()}

    def generate_monitoring_report(self) -> str:
        """監視レポート生成"""

        summary = self.get_execution_summary()
        stats = summary["stats"]

        report = f"""# 📊 Day 7: 24時間監視レポート

**生成日時**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

---

## 📈 累計統計

- **総実行回数**: {stats.get('total_executions', 0)}回
- **総投稿数**: {stats.get('total_posts_created', 0)}社
- **平均品質スコア**: {stats.get('average_quality_score', 0):.1f}/10
- **成功率**: {stats.get('success_rate', 0):.1f}%

---

## 🕐 最新実行状況

"""

        for i, log in enumerate(summary["latest_logs"], 1):
            report += f"### 実行 #{i}\n"
            report += f"- **日時**: {log.get('timestamp', 'N/A')}\n"
            report += f"- **ステータス**: {log.get('status', 'N/A').upper()}\n"
            report += f"- **品質スコア**: {log['results'].get('quality_score', 0):.1f}/10\n"
            report += f"- **投稿数**: {log['results'].get('successful_posts', 0)}社\n\n"

        report += """---

## 🎯 Day 7目標の進捗

- [ ] 初回手動実行成功
- [ ] 自動実行4回/日達成
- [ ] 24時間エラーなし
- [ ] 品質スコア8.0以上維持

---

## 📌 次のアクション

1. GitHub Actions実行ログを確認
2. エラーがあれば原因調査
3. 品質スコア推移を監視
4. ナレッジベース蓄積状況を確認

"""

        return report

    def save_report(self):
        """レポート保存"""
        report = self.generate_monitoring_report()

        filename = f'/workspaces/gemini_AI_Agent/uz-manda-portal/reports/day7/monitor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"📄 監視レポート保存: {filename}")
        print("\n" + report)


if __name__ == "__main__":
    monitor = Day7Monitor()
    monitor.save_report()
