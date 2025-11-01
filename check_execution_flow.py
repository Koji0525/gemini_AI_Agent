#!/usr/bin/env python3
"""
実際の実行フロー確認スクリプト
"""

import os
import subprocess
import sys


def check_wordpress_automation_flow():
    """WordPress自動化フローの確認"""
    print("�� WordPress自動化フローの確認...")

    # 主要実行スクリプトの確認
    scripts = [
        "uz-manda-portal/scripts/run_day4_integrated.py",
        "uz-manda-portal/scripts/integration/wordpress_task_definition.py",
        "uz-manda-portal/scripts/agents/ma_auto_poster_day3.py",
    ]

    for script in scripts:
        if os.path.exists(script):
            print(f"  ✅ {script}")

            # スクリプト内のインポートを確認
            try:
                with open(script, "r", encoding="utf-8") as f:
                    content = f.read()

                    # 自己修復関連のインポートをチェック
                    if "self_healing" in content or "RetryManager" in content or "ErrorClassifier" in content:
                        print(f"    🔗 自己修復コンポーネントを参照")
                    else:
                        print(f"    ⚠️  自己修復コンポーネントの参照なし")

            except Exception as e:
                print(f"    ❌ 読み込みエラー: {e}")
        else:
            print(f"  ❌ {script}")


def check_knowledge_base_integration():
    """ナレッジベース連携の確認"""
    print("\n📚 ナレッジベース連携の確認...")

    kb_files = [
        "knowledge_base/wordpress_automation/success_patterns.jsonl",
        "knowledge_base/wordpress_automation/error_patterns.jsonl",
        "knowledge_base/wordpress_automation/statistics.json",
    ]

    for kb_file in kb_files:
        if os.path.exists(kb_file):
            print(f"  ✅ {kb_file}")

            # ファイルサイズを確認
            size = os.path.getsize(kb_file)
            if size > 100:  # 100バイト以上あればデータがあると判断
                print(f"    📊 データ有り ({size} bytes)")
            else:
                print(f"    ⚠️  データ少なめ")
        else:
            print(f"  ❌ {kb_file}")


def check_actual_execution():
    """実際の実行テスト"""
    print("\n🚀 実際の実行テスト...")

    try:
        # 環境変数を設定
        env = os.environ.copy()
        env["PYTHONPATH"] = "/workspaces/gemini_AI_Agent"

        # 単純な実行テスト
        result = subprocess.run(
            [
                "python3",
                "-c",
                """
import sys
sys.path.append("/workspaces/gemini_AI_Agent")
try:
    from uz-manda-portal.scripts.integration.wordpress_task_definition import WordPressTaskExecutor
    print("✅ WordPressTaskExecutor インポート成功")
    
    # 簡単なインスタンス化テスト
    executor = WordPressTaskExecutor()
    print("✅ WordPressTaskExecutor インスタンス化成功")
    
except Exception as e:
    print(f"❌ エラー: {e}")
            """,
            ],
            capture_output=True,
            text=True,
            env=env,
            cwd="/workspaces/gemini_AI_Agent",
        )

        print(f"  実行結果: {result.stdout}")
        if result.stderr:
            print(f"  エラー出力: {result.stderr}")

    except Exception as e:
        print(f"  ❌ 実行テストエラー: {e}")


def main():
    print("=" * 80)
    print("🔧 実際の実行フロー確認")
    print("=" * 80)

    check_wordpress_automation_flow()
    check_knowledge_base_integration()
    check_actual_execution()

    print(f"\n" + "=" * 80)
    print("🎯 分析サマリー")
    print("=" * 80)


if __name__ == "__main__":
    main()
