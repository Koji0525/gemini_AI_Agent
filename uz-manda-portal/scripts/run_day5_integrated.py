#!/usr/bin/env python3
"""
Day 5: Self Learning Pipeline統合 + ダッシュボード
軽量学習システム版
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "integration/learning"))

from self_learning_connector import SelfLearningConnector


def print_day5_header():
    """Day 5ヘッダー"""
    print("\n" + "=" * 80)
    print("🧠 Day 5: Self Learning システム統合".center(80))
    print("=" * 80)
    print("\n📋 実装機能:")
    print("   ✅ 軽量パターン分析エンジン")
    print("   ✅ 学習レポート自動生成")
    print("   ✅ Webダッシュボード準備完了")
    print("   ✅ リアルタイム可視化")
    print("\n" + "=" * 80 + "\n")


def main():
    """Day 5メイン処理"""
    print_day5_header()

    try:
        # Step 1: 軽量学習システム初期化
        print("🧠 Step 1: 軽量学習システム初期化...")
        connector = SelfLearningConnector()

        # Step 2: パターン分析実行
        print("\n🔍 Step 2: 実行パターン分析...")
        analysis = connector.analyze_execution_patterns()

        # Step 3: 学習レポート生成
        print("\n📄 Step 3: 学習レポート生成...")
        report = connector.create_learning_report(analysis)

        # Step 4: 結果表示
        print("\n" + "=" * 80)
        print("📊 Day 5 実行結果サマリー".center(80))
        print("=" * 80)

        print(f"\n📈 システムパフォーマンス:")
        print(f"   • 総実行回数: {analysis['total_executions']}回")
        print(f"   • 総投稿数: {analysis['total_posts_created']}社")
        print(f"   • 平均品質スコア: {analysis['average_quality_score']:.1f}/10")

        print(f"\n🔍 パターン分析:")
        print(f"   • 総パターン数: {analysis['total_patterns']}")
        print(f"   • 成功率: {analysis['success_rate']:.1f}%")

        print(f"\n✨ ベストプラクティス: {len(analysis['best_practices'])}件")

        # Day 5達成判定
        print("\n" + "=" * 80)

        if analysis["success_rate"] >= 80 and analysis["average_quality_score"] >= 8.0:
            print("🎉" * 40)
            print("\n🎉🎉🎉 Day 5 完全達成！ 🎉🎉🎉\n")
            print("🎉" * 40)

            print("\n✨ 達成項目:")
            print("   ✅ 軽量学習システム実装")
            print("   ✅ パターン分析自動化")
            print("   ✅ 学習レポート生成")
            print("   ✅ ナレッジベース統合")
            print("   ✅ Webダッシュボード準備完了")

            print("\n📊 Webダッシュボード起動方法:")
            print("   cd /workspaces/gemini_AI_Agent/uz-manda-portal")
            print("   streamlit run dashboard/app.py --server.port 8501")
            print("\n   ※ Codespacesの場合、ポート8501を公開してアクセスしてください")

            print("\n💡 改善提案:")
            for i, rec in enumerate(analysis["recommendations"][:3], 1):
                print(f"   {i}. {rec}")

            print("\n📌 次のステップ: Day 6")
            print("   • GitHub Actions自動実行設定")
            print("   • Slack/Email通知実装")
            print("   • GitHub Issues自動生成")
            print("   • 24時間完全自律運用")

        else:
            print(f"💪 Day 5 部分達成")
            print(f"   成功率: {analysis['success_rate']:.1f}%")
            print(f"   品質スコア: {analysis['average_quality_score']:.1f}/10")

        print("\n" + "=" * 80 + "\n")

        return analysis

    except Exception as e:
        print(f"\n❌ エラー発生: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = main()

    if result and result.get("success_rate", 0) >= 80:
        exit(0)
    else:
        exit(1)
