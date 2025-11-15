"""pendingタスク実行スクリプト - 詳細出力版"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import argparse
from datetime import datetime, timezone, timedelta
from tools.base_data_accessor import BaseDataAccessor

JST = timezone(timedelta(hours=9))


def get_pending_tasks(goal_id: str = None, limit: int = None):
    """pendingタスク取得"""
    
    accessor = BaseDataAccessor()
    
    # フィルター条件
    def filter_func(task):
        status = task.get('status', '').lower()
        
        # pending以外はスキップ
        if status != 'pending':
            return False
        
        # ゴールIDフィルター
        if goal_id and str(task.get('parent_goal_id')) != str(goal_id):
            return False
        
        return True
    
    # タスク取得
    tasks = accessor.read_sheet_as_dicts('pm_tasks', filter_func=filter_func)
    
    # 優先度でソート（high → medium → low）
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    tasks.sort(key=lambda t: priority_order.get(t.get('priority', 'medium').lower(), 1))
    
    # 件数制限
    if limit:
        tasks = tasks[:limit]
    
    return tasks


def main():
    parser = argparse.ArgumentParser(description='pendingタスク実行')
    parser.add_argument('--goal-id', type=str, help='特定ゴールのタスクのみ実行')
    parser.add_argument('--limit', type=int, help='実行タスク数上限')
    parser.add_argument('--dry-run', action='store_true', help='実行せず表示のみ')
    
    args = parser.parse_args()
    
    print("="*80)
    print("📋 pendingタスク実行")
    print("="*80)
    
    # pendingタスク取得
    tasks = get_pending_tasks(goal_id=args.goal_id, limit=args.limit)
    
    if not tasks:
        print("\n✅ 実行すべきpendingタスクはありません")
        return
    
    print(f"\n実行対象: {len(tasks)}個のタスク")
    print("\n【タスク一覧】")
    
    for i, task in enumerate(tasks, 1):
        task_id = task.get('task_id', '?')
        description = task.get('description', '?')
        priority = task.get('priority', 'medium')
        goal_id = task.get('parent_goal_id', '?')
        
        print(f"{i:2d}. [{priority:6s}] Goal{goal_id} - {task_id}")
        print(f"     {description[:70]}")
    
    # Dry-run チェック
    if args.dry_run:
        print("\n✅ Dry-run モード: 実行せず終了")
        return
    
    # 実行確認
    print("\n" + "="*80)
    print("これらのタスクを実行しますか？")
    print("  [y] はい、実行")
    print("  [n] いいえ、キャンセル")
    
    choice = input("\n選択 > ").strip().lower()
    
    if choice != 'y':
        print("❌ キャンセルしました")
        return
    
    # 実行（詳細出力をリアルタイム表示）
    print("\n" + "="*80)
    print("🚀 タスク実行開始")
    print("="*80)
    print("")
    
    # run_3_cycles.pyを呼び出し（出力をリアルタイム表示）
    import subprocess
    
    # capture_output=False で標準出力をそのまま表示
    result = subprocess.run(
        ['python3', '/workspaces/gemini_AI_Agent/run_3_cycles.py'],
        capture_output=False  # 重要: リアルタイム表示
    )
    
    print("\n" + "="*80)
    
    if result.returncode == 0:
        print("✅ タスク実行完了")
        
        # 実行後サマリー
        print("\n【実行サマリー】")
        print(f"  実行タスク数: {len(tasks)}個")
        
        # 最新の実行結果を確認
        from pathlib import Path
        auto_logs = Path('/workspaces/gemini_AI_Agent/agent_outputs/auto_logs')
        
        if auto_logs.exists():
            latest_logs = sorted(auto_logs.glob('*.txt'), key=lambda f: f.stat().st_mtime, reverse=True)
            
            if latest_logs:
                print(f"\n  📄 最新実行ログ:")
                for log in latest_logs[:len(tasks)]:
                    print(f"    - {log.name}")
        
        # 成果物確認
        setup_dir = Path('/workspaces/gemini_AI_Agent/agent_outputs/setup')
        impl_dir = Path('/workspaces/gemini_AI_Agent/agent_outputs/implementation')
        
        print(f"\n  📂 成果物:")
        
        if setup_dir.exists():
            recent_setup = sorted(setup_dir.iterdir(), key=lambda d: d.stat().st_mtime, reverse=True)
            for d in recent_setup[:2]:
                if d.is_dir():
                    file_count = len(list(d.rglob('*')))
                    print(f"    - {d.name}/ ({file_count}個のファイル)")
        
        if impl_dir.exists():
            recent_impl = sorted(impl_dir.iterdir(), key=lambda d: d.stat().st_mtime, reverse=True)
            for d in recent_impl[:2]:
                if d.is_dir():
                    file_count = len(list(d.rglob('*')))
                    print(f"    - {d.name}/ ({file_count}個のファイル)")
    else:
        print("❌ タスク実行エラー")
        sys.exit(1)


if __name__ == "__main__":
    main()
