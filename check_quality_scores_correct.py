#!/usr/bin/env python3
"""
品質スコア連携確認スクリプト（正しいメソッド版）
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_quality_score_integration():
    """品質スコアの連携状況を確認"""
    print("🔍 品質スコア連携確認")
    print("=" * 50)

    try:
        from tools.sheets_manager import GoogleSheetsManager

        # 正しいspreadsheet_idで初期化
        SPREADSHEET_ID = "1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s"
        sheets_mgr = GoogleSheetsManager(SPREADSHEET_ID)
        print("✅ GoogleSheetsManager 初期化成功")

        # 1. タスク実行ログの確認（正しいメソッドを使用）
        print("\n1. 📊 タスク実行ログの確認")
        try:
            # get_tasksメソッドでデータ取得を試みる
            if hasattr(sheets_mgr, "get_tasks"):
                tasks_data = sheets_mgr.get_tasks()
                print(f"   📝 get_tasks() 戻り値タイプ: {type(tasks_data)}")
                if isinstance(tasks_data, list):
                    print(f"   📋 タスクデータ数: {len(tasks_data)}件")
                else:
                    print(f"   ℹ️ タスクデータ: {tasks_data}")
            else:
                print("   ❌ get_tasksメソッドが利用できません")

        except Exception as e:
            print(f"   ❌ 実行ログ取得失敗: {e}")

        # 2. 代替方法での確認
        print("\n2. �� 代替方法での確認")
        try:
            # シート名を直接指定して試す
            sheet_names = ["task_execution_log", "pm_tasks", "progress_dashboard"]
            for sheet_name in sheet_names:
                try:
                    # メソッド名を動的に生成して試す
                    method_name = f"get_{sheet_name}"
                    if hasattr(sheets_mgr, method_name):
                        method = getattr(sheets_mgr, method_name)
                        data = method()
                        print(f"   ✅ {sheet_name}: {len(data) if isinstance(data, list) else 'データ取得'}件")
                    else:
                        print(f"   ❌ {method_name}メソッドなし")
                except Exception as e:
                    print(f"   ❌ {sheet_name}取得失敗: {e}")

        except Exception as e:
            print(f"   ❌ 代替方法確認失敗: {e}")

        # 3. ファイルシステム上のレビュー結果確認
        print("\n3. 💾 ファイルシステム上のレビュー結果")
        try:
            import glob

            review_files = glob.glob("agent_outputs/**/*review*", recursive=True)
            print(f"   📄 レビュー関連ファイル: {len(review_files)}件")

            # 品質スコアを含むファイルを検索
            quality_files = []
            for file_path in review_files[:10]:  # 最初の10件のみ確認
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if any(keyword in content for keyword in ["品質スコア", "quality_score", "品質評価", "score"]):
                            quality_files.append(file_path)
                except:
                    pass

            print(f"   🎯 品質スコア関連ファイル: {len(quality_files)}件")
            for qfile in quality_files[:3]:
                print(f"      🔍 {os.path.basename(qfile)}")

        except Exception as e:
            print(f"   ❌ ファイルシステム確認失敗: {e}")

        # 4. 品質スコア連携の重要性を再確認
        print("\n4. 🎯 品質スコア連携の重要性")
        print("   📊 現在の状態: ファイルシステム上にはレビュー結果がある")
        print("   🔄 必要な連携: ファイル → Google Sheets → 進捗ダッシュボード")
        print("   🎯 目標: 自動的な品質ベースの意思決定")

        print("=" * 50)
        print("✅ 品質スコア連携確認完了")

    except Exception as e:
        print(f"❌ 品質スコア確認失敗: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    check_quality_score_integration()
