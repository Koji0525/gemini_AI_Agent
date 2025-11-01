#!/usr/bin/env python3
"""
Day 6: 完全自律運用システム
GitHub Actions + Slack + Issues統合
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "integration"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "notifications"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "github_integration"))

from wordpress_task_definition import WordPressAutoPostTask, WordPressTaskExecutor
from knowledge_base_logger import WordPressKnowledgeLogger
from report_generator import Day4ReportGenerator

# 通知・連携機能（オプション）
try:
    from slack_notifier import SlackNotifier
    from issue_creator import GitHubIssueCreator

    HAS_INTEGRATIONS = True
except ImportError:
    HAS_INTEGRATIONS = False
    print("⚠️ 通知機能はオプションです")


def print_day6_header():
    """Day 6ヘッダー"""
    print("\n" + "=" * 80)
    print("🎯 Day 6: 完全自律運用システム".center(80))
    print("=" * 80)
    print("\n📋 機能:")
    print("   ✅ GitHub Actions 6時間ごと自動実行")
    print("   ✅ Slack通知（成功/失敗）")
    print("   ✅ GitHub Issues自動生成")
    print("   ✅ ナレッジベース自動更新")
    print("   ✅ 完全自律運用")
    print("\n" + "=" * 80 + "\n")


async def main():
    """Day 6メイン処理"""
    print_day6_header()

    try:
        # Step 1: タスク実行
        print("🚀 Step 1: WordPress自動投稿実行...")
        task = WordPressAutoPostTask.create_batch_post_task(5)
        executor = WordPressTaskExecutor()
        result = await executor.execute_batch_post_task(task)

        # Step 2: ナレッジベース記録
        print("\n📚 Step 2: ナレッジベース記録...")
        kb_logger = WordPressKnowledgeLogger()
        kb_logger.log_execution(result)

        # Step 3: レポート生成
        print("\n📄 Step 3: レポート生成...")
        report_gen = Day4ReportGenerator()
        report_gen.generate_markdown_report(result)

        # Step 4: Slack通知（オプション）
        if HAS_INTEGRATIONS:
            print("\n📱 Step 4: Slack通知...")
            slack = SlackNotifier()
            slack.send_success_notification(result)

        # Step 5: GitHub Issue作成（品質スコアが低い場合）
        if HAS_INTEGRATIONS:
            print("\n📝 Step 5: GitHub Issue確認...")
            issue_creator = GitHubIssueCreator()
            issue_creator.create_improvement_issue(result)

        # 結果表示
        print("\n" + "=" * 80)
        print("📊 Day 6 実行結果".center(80))
        print("=" * 80)

        results_data = result["results"]
        print(f"\n✅ ステータス: {result['status'].upper()}")
        print(f"⏱️  実行時間: {result['execution_time']}")
        print(f"📈 品質スコア: {results_data['quality_score']:.1f}/10")
        print(f"🎯 成功: {results_data['successful_posts']}/{results_data['total_companies']}社")

        # Day 6達成判定
        if results_data["quality_score"] >= 8.0:
            print("\n" + "🎉" * 40)
            print("\n🎉🎉🎉 Day 6 完全達成！ 🎉🎉🎉\n")
            print("🎉" * 40)

            print("\n✨ 達成項目:")
            print("   ✅ GitHub Actions自動実行設定完了")
            print("   ✅ WordPress自動投稿（品質スコア8.0以上）")
            print("   ✅ ナレッジベース自動更新")
            print("   ✅ Slack通知機能実装")
            print("   ✅ GitHub Issues自動生成機能実装")

            print("\n🚀 完全自律運用システム完成！")
            print("\n📌 次のアクション:")
            print("   1. GitHub Secretsに以下を設定:")
            print("      • WP_URL")
            print("      • WP_USERNAME")
            print("      • WP_PASSWORD")
            print("      • SLACK_WEBHOOK_URL（オプション）")
            print("      • GITHUB_TOKEN（オプション）")
            print("\n   2. GitHub Actionsを有効化")
            print("\n   3. 6時間ごとに自動実行開始 🎯")
        else:
            print(f"\n💪 品質スコア向上中 ({results_data['quality_score']:.1f}/10)")

        print("\n" + "=" * 80 + "\n")

        return result

    except Exception as e:
        print(f"\n❌ エラー: {e}")

        # エラー通知
        if HAS_INTEGRATIONS:
            slack = SlackNotifier()
            slack.send_error_notification(str(e))

        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = asyncio.run(main())

    if result and result["results"]["quality_score"] >= 8.0:
        exit(0)
    else:
        exit(1)
