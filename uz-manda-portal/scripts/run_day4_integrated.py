#!/usr/bin/env python3
"""
🎯 Day 4: 自律エージェントシステム統合版
Task Executor + Knowledge Base + レポート生成
"""

import sys
import os
import asyncio
from datetime import datetime

# パス設定
sys.path.insert(0, "/workspaces/gemini_AI_Agent")
integration_path = os.path.join(os.path.dirname(__file__), "integration")
sys.path.insert(0, integration_path)

from wordpress_task_definition import WordPressAutoPostTask, WordPressTaskExecutor
from knowledge_base_logger import WordPressKnowledgeLogger
from report_generator import Day4ReportGenerator


def print_day4_header():
    """Day 4ヘッダー表示"""
    print("\n" + "=" * 80)
    print("🚀 Day 4: 自律エージェントシステム統合".center(80))
    print("=" * 80)
    print("\n📋 統合コンポーネント:")
    print("   ✅ Task Executor互換タスク定義")
    print("   ✅ Knowledge Base自動記録")
    print("   ✅ 自動レポート生成")
    print("   ✅ Self Learning Pipeline連携")
    print("\n" + "=" * 80 + "\n")


async def main():
    """Day 4メイン処理"""
    print_day4_header()

    try:
        # Step 1: タスク定義作成
        print("📝 Step 1: Task Executor互換タスク作成...")
        task = WordPressAutoPostTask.create_batch_post_task(companies_count=5)
        print(f"   ✅ タスクID: {task['task_id']}")
        print(f"   ✅ タスク: {task['title']}")
        print(f"   ✅ 優先度: {task['priority']}")

        # Step 2: タスク実行
        print("\n🚀 Step 2: WordPress自動投稿実行...")
        executor = WordPressTaskExecutor()
        result = await executor.execute_batch_post_task(task)

        # Step 3: Knowledge Base記録
        print("\n📚 Step 3: ナレッジベースに記録...")
        kb_logger = WordPressKnowledgeLogger()
        kb_logger.log_execution(result)

        # Step 4: レポート生成
        print("\n📄 Step 4: 実行結果レポート生成...")
        report_gen = Day4ReportGenerator()
        report = report_gen.generate_markdown_report(result)

        # Step 5: 結果サマリー表示
        print("\n" + "=" * 80)
        print("📊 Day 4 実行結果サマリー".center(80))
        print("=" * 80)

        results_data = result["results"]
        print(f"\n🎯 ステータス: {result['status'].upper()}")
        print(f"⏱️  実行時間: {result['execution_time']}")
        print(f"\n📈 投稿結果:")
        print(f"   • 総企業数: {results_data['total_companies']}社")
        print(f"   • 成功: {results_data['successful_posts']}社 ✅")
        print(f"   • 失敗: {results_data['failed_posts']}社 ❌")
        print(f"   • DD項目: {results_data['dd_items_added']}項目")
        print(f"   • 品質スコア: {results_data['quality_score']:.1f}/10")

        print(f"\n📋 作成された投稿:")
        for i, post_id in enumerate(results_data["post_ids"], 1):
            print(f"   {i}. https://uzbek-ma.com/?p={post_id}")

        # Day 4達成判定
        print("\n" + "=" * 80)
        if result["status"] == "completed" and results_data["quality_score"] >= 8.0:
            print("🎉" * 40)
            print("\n🎉🎉🎉 Day 4 完全達成！ 🎉🎉🎉\n")
            print("🎉" * 40)
            print("\n✨ 達成項目:")
            print("   ✅ Task Executor互換タスク作成・実行")
            print("   ✅ WordPress自動投稿（5社完了）")
            print("   ✅ Knowledge Base連携・記録")
            print("   ✅ 実行結果レポート自動生成")
            print("   ✅ 統計情報の自動更新")
            print("\n📌 次のステップ: Day 5")
            print("   • Self Learning Pipeline本格統合")
            print("   • Webダッシュボード実装")
            print("   • GitHub Actions自動実行設定")
        else:
            quality_pct = (results_data["quality_score"] / 10) * 100
            print(f"💪 Day 4 部分達成（品質スコア: {quality_pct:.0f}%）")
            print("\n   推奨アクション:")
            if results_data["failed_posts"] > 0:
                print(f"   • 失敗した{results_data['failed_posts']}社の再投稿")
            print("   • エラーログの詳細分析")
            print("   • 再実行で完全達成を目指す")

        print("\n" + "=" * 80 + "\n")

        return result

    except Exception as e:
        print(f"\n❌ エラー発生: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = asyncio.run(main())

    # 終了コード設定
    if result and result.get("status") == "completed":
        exit(0)
    else:
        exit(1)
