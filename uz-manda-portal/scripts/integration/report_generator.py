"""
Day 4: 実行結果レポート自動生成
"""

from datetime import datetime
from typing import Dict
import json
import os


class Day4ReportGenerator:
    """Day 4実行結果のレポート生成"""

    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = "/workspaces/gemini_AI_Agent/uz-manda-portal/reports/day4"

        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_markdown_report(self, task_result: Dict) -> str:
        """Markdown形式のレポート生成"""

        timestamp = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")

        report = f"""# 🎯 Day 4 実行結果レポート

**実行日時**: {timestamp}  
**タスクID**: {task_result['task_id']}  
**ステータス**: {task_result['status'].upper()}  

---

## 📊 実行サマリー

| 項目 | 結果 |
|------|------|
| 総企業数 | {task_result['results']['total_companies']}社 |
| 成功 | {task_result['results']['successful_posts']}社 |
| 失敗 | {task_result['results']['failed_posts']}社 |
| DD項目追加 | {task_result['results']['dd_items_added']}項目 |
| 品質スコア | {task_result['results']['quality_score']:.1f}/10 |
| 実行時間 | {task_result['execution_time']} |

---

## 📋 作成された投稿

"""

        for i, post_id in enumerate(task_result["results"]["post_ids"], 1):
            report += f"{i}. [投稿 #{post_id}](https://uzbek-ma.com/?p={post_id})\n"

        report += "\n---\n\n"

        # 詳細結果
        report += "## 📝 詳細結果\n\n"
        for detail in task_result["results"].get("details", []):
            icon = "✅" if detail["status"] == "success" else "❌"
            report += f"### {icon} {detail['title']}\n"
            report += f"- ステータス: {detail['status']}\n"
            report += f"- 投稿ID: {detail.get('post_id', 'N/A')}\n"
            report += f"- 業種: {detail.get('industry', 'N/A')}\n"
            report += f"- DD項目: {detail.get('dd_items', 0)}件\n\n"

        # 次のアクション
        report += "---\n\n## 🚀 次のアクション\n\n"

        if task_result["status"] == "completed":
            report += "✨ **Day 4 完全達成！**\n\n"
            report += "次のステップ:\n"
            report += "- [ ] Day 5: Self Learning Pipeline統合\n"
            report += "- [ ] Webダッシュボード実装\n"
            report += "- [ ] リアルタイム可視化\n"
        else:
            report += "💪 **改善の余地あり**\n\n"
            report += "推奨アクション:\n"
            report += "- [ ] 失敗した企業の再投稿\n"
            report += "- [ ] エラーログの詳細分析\n"
            report += "- [ ] リトライ設定の調整\n"

        # ファイル保存
        filename = f'{self.output_dir}/report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"📄 レポート生成: {filename}")

        return report
