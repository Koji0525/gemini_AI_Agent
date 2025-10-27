#!/usr/bin/env python3
"""
品質スコア連携確認スクリプト（修正版）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_quality_score_integration():
    """品質スコアの連携状況を確認"""
    print("🔍 品質スコア連携確認")
    print("=" * 50)
    
    try:
        # 正しいインポートパスを使用
        from tools.sheets_manager import GoogleSheetsManager
        
        # 正しいspreadsheet_idで初期化
        SPREADSHEET_ID = '1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s'
        sheets_mgr = GoogleSheetsManager(SPREADSHEET_ID)
        print("✅ GoogleSheetsManager 初期化成功")
        
        # 1. task_execution_log の確認
        print("\n1. 📊 タスク実行ログの確認")
        try:
            logs = sheets_mgr.get_all_records('task_execution_log')
            print(f"   📝 実行ログ総数: {len(logs)}件")
            
            # 品質スコア付きのログを抽出
            scored_logs = [log for log in logs if log.get('quality_score') and str(log.get('quality_score')).strip()]
            print(f"   🎯 品質スコア付き: {len(scored_logs)}件")
            
            if scored_logs:
                print("   📈 直近の品質スコア:")
                for log in scored_logs[-5:]:
                    task_id = log.get('task_id', 'N/A')
                    score = log.get('quality_score', 'N/A')
                    status = log.get('status', 'N/A')
                    agent_type = log.get('agent_type', 'N/A')
                    print(f"      🆔 {task_id}: {agent_type} | 品質 {score}/10 | 状態: {status}")
            else:
                print("   ℹ️ 品質スコア付きログがありません")
                
        except Exception as e:
            print(f"   ❌ 実行ログ取得失敗: {e}")
        
        # 2. pm_tasks と品質スコアの連携確認
        print("\n2. 🔄 タスクと品質スコアの連携確認")
        try:
            tasks = sheets_mgr.get_all_records('pm_tasks')
            completed_tasks = [t for t in tasks if t.get('status') == 'completed']
            print(f"   ✅ 完了タスク: {len(completed_tasks)}件")
            
            # 完了タスクに対応する品質スコアがあるか確認
            completed_with_score = 0
            sample_tasks = completed_tasks[:10] if len(completed_tasks) > 10 else completed_tasks
            
            for task in sample_tasks:
                task_id = task.get('task_id')
                # 対応する実行ログを検索
                corresponding_logs = [log for log in logs if str(log.get('task_id')) == str(task_id) and log.get('quality_score')]
                if corresponding_logs:
                    completed_with_score += 1
                    
            print(f"   📊 品質スコア連携率: {completed_with_score}/{len(sample_tasks)}件")
            
        except Exception as e:
            print(f"   ❌ タスク連携確認失敗: {e}")
        
        # 3. 進捗ダッシュボードの確認
        print("\n3. 📈 進捗ダッシュボード確認")
        try:
            dashboard = sheets_mgr.get_all_records('progress_dashboard')
            print(f"   🎯 ダッシュボード項目: {len(dashboard)}件")
            
            quality_items = [item for item in dashboard if item.get('quality_score')]
            print(f"   📊 品質スコア表示項目: {len(quality_items)}件")
            
            for item in dashboard[:3]:
                goal_id = item.get('goal_id', 'N/A')
                progress = item.get('progress_rate', 'N/A')
                quality = item.get('quality_score', 'N/A')
                print(f"      🎯 {goal_id}: 進捗 {progress}% | 品質 {quality}/10")
                
        except Exception as e:
            print(f"   ❌ ダッシュボード確認失敗: {e}")
        
        # 4. ファイルシステム上の出力確認
        print("\n4. 💾 ファイルシステム出力確認")
        try:
            import subprocess
            # 最近の出力ファイルを確認
            result = subprocess.run(['find', 'agent_outputs', '-name', '*review*', '-type', 'f'], 
                                  capture_output=True, text=True)
            review_files = result.stdout.strip().split('\n') if result.stdout else []
            print(f"   📄 レビュー関連ファイル: {len(review_files)}件")
            
            if review_files:
                for file in review_files[:3]:
                    print(f"      🔍 {os.path.basename(file)}")
                    
        except Exception as e:
            print(f"   ❌ ファイルシステム確認失敗: {e}")
            
        print("=" * 50)
        print("✅ 品質スコア連携確認完了")
        
    except Exception as e:
        print(f"❌ 品質スコア確認失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_quality_score_integration()
