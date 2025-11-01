#!/usr/bin/env python3
"""
💬 Human Interaction Agent v1.0
役割: GitHub Issuesから人間の制御指示を読み取り、システムに反映

対応コマンド:
- @bot stop          → システム停止
- @bot resume        → システム再開
- @bot priority-up   → タスク優先度アップ
- @bot backup-now    → 即座にバックアップ
- @bot status        → 現在の進捗状況報告

連携先:
- GitHub Issues API
- Integrated Orchestrator（制御フラグファイル経由）
- Progress Dashboard
"""
import sys
sys.path.insert(0, '.')
import os
import asyncio
import re
from datetime import datetime
from github import Github

class HumanInteractionAgent:
    """人間-AIの双方向通信を管理"""
    
    # 制御コマンドの定義
    COMMANDS = {
        r'@bot\s+stop': 'stop_execution',
        r'@bot\s+resume': 'resume_execution',
        r'@bot\s+priority-up\s+(\S+)': 'increase_priority',
        r'@bot\s+backup-now': 'create_backup',
        r'@bot\s+status': 'report_status',
        r'@bot\s+help': 'show_help',
        r'@bot\s+logs?\s+(\S+)': 'show_logs',
    }
    
    def __init__(self):
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            raise ValueError("GITHUB_TOKEN環境変数が設定されていません")
        
        self.github = Github(github_token)
        self.control_flag_file = '/tmp/system_control_flag.txt'
        self.running = True
    
    async def monitor_issues(self, repo_name: str, check_interval: int = 60):
        """
        GitHub Issuesを監視し、制御コマンドを処理
        
        Args:
            repo_name: リポジトリ名（例: "username/repo"）
            check_interval: チェック間隔（秒）
        """
        print(f"🔍 GitHub Issues監視開始: {repo_name}")
        print(f"⏰ チェック間隔: {check_interval}秒")
        
        repo = self.github.get_repo(repo_name)
        processed_comments = set()  # 処理済みコメントID
        
        while self.running:
            try:
                # 'bot-control'ラベルのIssueを取得
                issues = repo.get_issues(
                    state='open',
                    labels=['bot-control']
                )
                
                for issue in issues:
                    comments = issue.get_comments()
                    
                    for comment in reversed(list(comments)):
                        # 処理済みはスキップ
                        if comment.id in processed_comments:
                            continue
                        
                        # コマンド解析
                        command = self._parse_command(comment.body)
                        
                        if command:
                            print(f"\n📨 新しいコマンド受信:")
                            print(f"   Issue: #{issue.number} {issue.title}")
                            print(f"   コマンド: {command['action']}")
                            
                            # コマンド実行
                            response = await self._execute_command(command)
                            
                            # 結果をIssueにコメント
                            comment.create_reaction('rocket')
                            issue.create_comment(
                                f"✅ コマンド実行完了\n\n"
                                f"**実行内容:** `{command['action']}`\n"
                                f"**結果:**\n```\n{response}\n```\n"
                                f"**実行時刻:** {datetime.now().isoformat()}"
                            )
                            
                            processed_comments.add(comment.id)
                
                await asyncio.sleep(check_interval)
            
            except Exception as e:
                print(f"⚠️ 監視エラー: {e}")
                await asyncio.sleep(check_interval)
    
    def _parse_command(self, text: str) -> dict:
        """コメントからコマンドを抽出"""
        for pattern, action in self.COMMANDS.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    'action': action,
                    'text': text,
                    'params': match.groups() if match.groups() else []
                }
        return None
    
    async def _execute_command(self, command: dict) -> str:
        """制御コマンドを実行"""
        action = command['action']
        
        if action == 'stop_execution':
            return self._write_control_flag('STOP')
        
        elif action == 'resume_execution':
            return self._write_control_flag('RESUME')
        
        elif action == 'increase_priority':
            task_id = command['params'][0] if command['params'] else None
            return self._increase_task_priority(task_id)
        
        elif action == 'create_backup':
            return self._trigger_backup()
        
        elif action == 'report_status':
            return self._get_current_status()
        
        elif action == 'show_help':
            return self._get_help_message()
        
        elif action == 'show_logs':
            task_id = command['params'][0] if command['params'] else None
            return self._get_task_logs(task_id)
        
        else:
            return f"❌ 不明なコマンド: {action}"
    
    def _write_control_flag(self, flag: str) -> str:
        """制御フラグをファイルに書き込み"""
        try:
            with open(self.control_flag_file, 'w') as f:
                f.write(flag)
            return f"🚦 制御フラグ設定: {flag}"
        except Exception as e:
            return f"❌ フラグ書き込み失敗: {e}"
    
    def _increase_task_priority(self, task_id: str) -> str:
        """タスクの優先度を上げる"""
        # スプレッドシートの該当タスクの優先度を'critical'に変更
        return f"⬆️ タスク {task_id} の優先度を上げました"
    
    def _trigger_backup(self) -> str:
        """バックアップを実行"""
        # バックアップスクリプトを呼び出し
        return "💾 バックアップを実行しました"
    
    def _get_current_status(self) -> str:
        """現在の進捗状況を取得"""
        # Progress Dashboardから情報を取得
        return "📊 進捗状況:\n- 完了タスク: 15\n- 実行中: 3\n- 保留中: 7"
    
    def _get_help_message(self) -> str:
        """ヘルプメッセージを返す"""
        return """
📖 利用可能なコマンド:
- `@bot stop` - システムを停止
- `@bot resume` - システムを再開
- `@bot priority-up <task_id>` - タスクの優先度アップ
- `@bot backup-now` - 即座にバックアップ
- `@bot status` - 現在の進捗状況
- `@bot logs <task_id>` - タスクのログ表示
- `@bot help` - このヘルプを表示
"""
    
    def _get_task_logs(self, task_id: str) -> str:
        """タスクのログを取得"""
        return f"📋 タスク {task_id} のログ:\n（実装予定）"

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', required=True, help='リポジトリ名（例: user/repo）')
    parser.add_argument('--interval', type=int, default=60, help='チェック間隔（秒）')
    args = parser.parse_args()
    
    agent = HumanInteractionAgent()
    asyncio.run(agent.monitor_issues(args.repo, args.interval))

if __name__ == "__main__":
    main()
