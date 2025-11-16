#!/usr/bin/env python3
"""
実用タスク管理CLIツール
タスクID: 469
生成日時: 自動生成

このツールは実際にプロジェクトで使用できます！
"""
import click
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.sheets_manager import GoogleSheetsManager
from agents.task_execution.enhanced_executor_v2 import EnhancedTaskExecutorV2

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    実用タスク管理CLIツール
    
    このツールを使って実際の開発タスクを効率的に管理できます！
    """
    pass

@cli.command()
@click.option('--status', type=click.Choice(['pending', 'completed', 'failed', 'all']), 
              default='pending', help='タスクステータスでフィルタ')
@click.option('--limit', '-n', default=10, help='表示件数')
def list_tasks(status: str, limit: int):
    """
    📋 タスク一覧を表示
    
    例:
        python task_cli.py list-tasks --status pending
        python task_cli.py list-tasks --status all --limit 20
    """
    click.echo(f"\n📋 タスク一覧（ステータス: {status}）")
    click.echo("=" * 80)
    
    try:
        sheets = GoogleSheetsManager()
        tasks = sheets.read_range('pm_tasks!A2:M1000')
        
        # フィルタリング
        filtered_tasks = []
        for row in tasks:
            if len(row) >= 5:
                task_status = row[4] if row[4] else 'unknown'
                if status == 'all' or task_status == status:
                    filtered_tasks.append(row)
        
        # 表示
        count = 0
        for row in filtered_tasks[:limit]:
            task_id = row[0]
            description = row[2] if len(row) > 2 else 'N/A'
            task_status = row[4] if len(row) > 4 else 'unknown'
            
            status_emoji = {
                'pending': '⏳',
                'completed': '✅',
                'failed': '❌',
                'cancelled': '🚫'
            }.get(task_status, '❓')
            
            click.echo(f"{status_emoji} [{task_id}] {description[:60]}")
            count += 1
        
        click.echo(f"\n表示: {count}件 / 全{len(filtered_tasks)}件")
        
    except Exception as e:
        click.echo(f"❌ エラー: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('task_id')
@click.option('--dry-run', is_flag=True, help='実際には実行せず、実行内容を表示')
def run_task(task_id: str, dry_run: bool):
    """
    🚀 指定したタスクを実行
    
    例:
        python task_cli.py run-task 469
        python task_cli.py run-task 469 --dry-run
    """
    if dry_run:
        click.echo(f"\n[DRY RUN] タスク {task_id} の実行内容を表示")
    else:
        click.echo(f"\n🚀 タスク {task_id} を実行中...")
    
    try:
        sheets = GoogleSheetsManager()
        tasks = sheets.read_range('pm_tasks!A2:M1000')
        
        # タスクを検索
        target_task = None
        for row in tasks:
            if row[0] == task_id:
                target_task = {
                    'task_id': row[0],
                    'parent_goal_id': row[1] if len(row) > 1 else '',
                    'description': row[2] if len(row) > 2 else '',
                    'required_role': row[3] if len(row) > 3 else 'implementation',
                    'status': row[4] if len(row) > 4 else 'pending'
                }
                break
        
        if not target_task:
            click.echo(f"❌ タスク {task_id} が見つかりません")
            sys.exit(1)
        
        click.echo(f"\n📝 タスク情報:")
        click.echo(f"  ID: {target_task['task_id']}")
        click.echo(f"  説明: {target_task['description']}")
        click.echo(f"  ステータス: {target_task['status']}")
        
        if dry_run:
            click.echo(f"\n[DRY RUN] 実際には実行しません")
            return
        
        # 実行確認
        if not click.confirm('\n本当に実行しますか？'):
            click.echo("キャンセルしました")
            return
        
        # 実行
        executor = EnhancedTaskExecutorV2()
        result = executor.execute_task_with_details(target_task)
        
        if result['status'] == 'completed':
            click.echo(f"\n✅ 実行完了！")
            click.echo(f"品質スコア: {result.get('quality_score', 'N/A')}/10")
            click.echo(f"保存先: {result.get('task_dir', 'N/A')}")
        else:
            click.echo(f"\n❌ 実行失敗: {result.get('error', 'Unknown error')}")
            sys.exit(1)
        
    except Exception as e:
        click.echo(f"❌ エラー: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('task_id')
@click.argument('new_status', type=click.Choice(['pending', 'completed', 'failed', 'cancelled']))
def update_status(task_id: str, new_status: str):
    """
    🔄 タスクステータスを変更
    
    例:
        python task_cli.py update-status 469 completed
    """
    click.echo(f"\n🔄 タスク {task_id} のステータスを '{new_status}' に変更中...")
    
    try:
        sheets = GoogleSheetsManager()
        tasks = sheets.read_range('pm_tasks!A2:M1000')
        
        # タスクの行番号を検索
        row_number = None
        for i, row in enumerate(tasks):
            if row[0] == task_id:
                row_number = i + 2  # ヘッダー行を考慮
                break
        
        if row_number is None:
            click.echo(f"❌ タスク {task_id} が見つかりません")
            sys.exit(1)
        
        # ステータス更新（E列 = 5列目）
        sheets.update_cell('pm_tasks', row=row_number, col=5, value=new_status)
        
        click.echo(f"✅ ステータスを更新しました")
        
    except Exception as e:
        click.echo(f"❌ エラー: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--tail', '-n', default=20, help='表示行数')
def show_logs(tail: int):
    """
    📄 最新の実行ログを表示
    
    例:
        python task_cli.py show-logs
        python task_cli.py show-logs --tail 50
    """
    click.echo(f"\n📄 最新ログ（最後の{tail}行）")
    click.echo("=" * 80)
    
    try:
        log_dir = Path('/workspaces/gemini_AI_Agent/agent_outputs/tasks')
        
        # 最新のタスクディレクトリを検索
        task_dirs = sorted(log_dir.glob('task_*'), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not task_dirs:
            click.echo("ログが見つかりません")
            return
        
        latest_dir = task_dirs[0]
        log_file = latest_dir / 'EXECUTION_LOG.md'
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                lines = f.readlines()
                for line in lines[-tail:]:
                    click.echo(line.rstrip())
        else:
            click.echo(f"ログファイルが見つかりません: {log_file}")
        
    except Exception as e:
        click.echo(f"❌ エラー: {e}", err=True)
        sys.exit(1)

@cli.command()
def stats():
    """
    📊 タスク統計を表示
    
    例:
        python task_cli.py stats
    """
    click.echo("\n📊 タスク統計")
    click.echo("=" * 80)
    
    try:
        sheets = GoogleSheetsManager()
        tasks = sheets.read_range('pm_tasks!A2:M1000')
        
        # 統計集計
        status_count = {}
        for row in tasks:
            if len(row) >= 5:
                status = row[4] if row[4] else 'unknown'
                status_count[status] = status_count.get(status, 0) + 1
        
        total = len(tasks)
        
        click.echo(f"\n総タスク数: {total}件\n")
        
        for status, count in sorted(status_count.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            bar_length = int(percentage / 2)
            bar = '█' * bar_length
            
            emoji = {
                'pending': '⏳',
                'completed': '✅',
                'failed': '❌',
                'cancelled': '🚫'
            }.get(status, '❓')
            
            click.echo(f"{emoji} {status:12s}: {count:3d}件 ({percentage:5.1f}%) {bar}")
        
    except Exception as e:
        click.echo(f"❌ エラー: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()
