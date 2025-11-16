#!/usr/bin/env python3
"""
タスク実行統合スクリプト（詳細ログ付き）
使用方法:
    python3 scripts/run_task_with_details.py --task_id T001
    python3 scripts/run_task_with_details.py --pending 1
"""
import sys
import argparse
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.sheets_manager import GoogleSheetsManager
from agents.task_execution.enhanced_executor_v2 import EnhancedTaskExecutorV2 as EnhancedTaskExecutor

try:
    from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
    KNOWLEDGE_AVAILABLE = True
except ImportError:
    KNOWLEDGE_AVAILABLE = False
    print("⚠️  KnowledgeManager がインポートできません（ナレッジ機能なしで実行）")


def main():
    parser = argparse.ArgumentParser(description='タスク実行（詳細ログ付き）')
    parser.add_argument('--task_id', type=str, help='実行するタスクID')
    parser.add_argument('--pending', type=int, default=0, help='pendingタスクを指定数実行')
    args = parser.parse_args()
    
    print("=" * 80)
    print("🚀 タスク実行開始（詳細ログ生成モード）")
    print("=" * 80)
    print("")
    
    # シートマネージャー初期化
    print("📊 Google Sheetsに接続中...")
    sheets_manager = GoogleSheetsManager()
    print("   ✅ 接続完了")
    print("")
    
    # ナレッジマネージャー初期化（利用可能な場合）
    knowledge_manager = None
    if KNOWLEDGE_AVAILABLE:
        try:
            print("📚 ナレッジマネージャー初期化中...")
            knowledge_manager = KnowledgeManager()
            print("   ✅ 初期化完了")
        except Exception as e:
            print(f"   ⚠️  初期化エラー: {e}")
    print("")
    
    # タスク実行エグゼキューター初期化
    executor = EnhancedTaskExecutor(knowledge_manager=knowledge_manager)
    
    # タスク取得
    if args.task_id:
        # 特定タスクIDを実行
        print(f"📋 タスク {args.task_id} を検索中...")
        tasks = sheets_manager.read_range('pm_tasks!A2:M1000')
        task = None
        for row in tasks:
            if len(row) > 0 and row[0] == args.task_id:
                task = {
                    'task_id': row[0],
                    'parent_goal_id': row[1] if len(row) > 1 else '',
                    'description': row[2] if len(row) > 2 else '',
                    'required_role': row[3] if len(row) > 3 else 'implementation',
                    'status': row[4] if len(row) > 4 else 'pending'
                }
                break
        
        if not task:
            print(f"   ❌ タスク {args.task_id} が見つかりません")
            return
        
        tasks_to_execute = [task]
    
    elif args.pending > 0:
        # pendingタスクを取得
        print(f"📋 pendingタスクを {args.pending}件 検索中...")
        all_tasks = sheets_manager.read_range('pm_tasks!A2:M1000')
        pending_tasks = []
        
        for row in all_tasks:
            if len(row) >= 5 and row[4] == 'pending':
                pending_tasks.append({
                    'task_id': row[0],
                    'parent_goal_id': row[1] if len(row) > 1 else '',
                    'description': row[2] if len(row) > 2 else '',
                    'required_role': row[3] if len(row) > 3 else 'implementation',
                    'status': row[4]
                })
        
        if not pending_tasks:
            print("   ℹ️  pendingタスクが見つかりません")
            return
        
        tasks_to_execute = pending_tasks[:args.pending]
        print(f"   ✅ {len(tasks_to_execute)}件のタスクを取得")
    
    else:
        print("❌ --task_id または --pending を指定してください")
        parser.print_help()
        return
    
    print("")
    print("=" * 80)
    print(f"📦 実行タスク数: {len(tasks_to_execute)}")
    print("=" * 80)
    print("")
    
    # タスクを実行
    results = []
    for i, task in enumerate(tasks_to_execute, 1):
        print(f"[{i}/{len(tasks_to_execute)}] タスク実行:")
        result = executor.execute_task_with_details(task)
        results.append(result)
        print("")
        
        # task_execution_log に記録
        try:
            log_entry = [
                f"LOG_{task['task_id']}",  # log_id
                task['task_id'],  # task_id
                task['description'],  # task_description
                result.get('elapsed_time', 'N/A'),  # elapsed_time
                'EnhancedExecutor',  # agent_role
                result.get('summary', ''),  # output_summary
                result.get('log_path', ''),  # output_data
                result.get('status', 'unknown'),  # status
                result.get('quality_score', 0),  # quality_score
                result.get('quality_description', '')  # quality_description
            ]
            
            sheets_manager.append_rows('task_execution_log', [log_entry])
            print(f"   📝 task_execution_log に記録しました")
            
            # pm_tasks のステータスを更新
            # TODO: ステータス更新ロジックを実装
            
        except Exception as e:
            print(f"   ⚠️  ログ記録エラー: {e}")
    
    print("")
    print("=" * 80)
    print("✅ 全タスク実行完了")
    print("=" * 80)
    print("")
    print("📊 実行サマリー:")
    print(f"   成功: {sum(1 for r in results if r.get('status') == 'completed')}件")
    print(f"   失敗: {sum(1 for r in results if r.get('status') == 'failed')}件")
    print(f"   平均品質スコア: {sum(r.get('quality_score', 0) for r in results) / len(results):.1f}/10")
    print("")
    print("📁 生成ファイル:")
    for result in results:
        if result.get('log_path'):
            print(f"   - {result['log_path']}")


if __name__ == "__main__":
    main()
