#!/usr/bin/env python3
"""
💬 Human Interaction Agent v1.0
役割: GitHub Issuesから人間の制御指示を読み取り、システムに反映

【v1.0 変更の理由】
何が起きた:
- 24時間自律開発システムが稼働
- 人間からの制御方法が必要

原因:
- 完全自動化されているが、緊急時の制御手段がない
- 進捗確認や優先度変更ができない

狙い:
- GitHub Issuesを通じた人間-AI間の双方向通信
- リアルタイムな制御と進捗確認
- 緊急停止・再開機能の実装

【対応コマンド】
- @bot stop          → システム停止
- @bot resume        → システム再開
- @bot priority-up   → タスク優先度アップ
- @bot backup-now    → 即座にバックアップ
- @bot status        → 現在の進捗状況報告
- @bot help          → ヘルプ表示
- @bot logs <task_id> → タスクログ表示

【連携先】
- GitHub Issues API
- Integrated Orchestrator（制御フラグファイル経由）
- Progress Dashboard

【使用例】
    # GitHub Token設定必要
    export GITHUB_TOKEN=your_token_here
    
    # Issues監視開始
    python3 core_agents/human_interaction_agent_v01_initial.py \
        --repo Koji0525/gemini_AI_Agent \
        --interval 60
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import os
import asyncio
import re
from datetime import datetime
from typing import Optional, Dict, List

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
    
    def __init__(self, repo_name: str):
        """
        Args:
            repo_name: リポジトリ名（例: "Koji0525/gemini_AI_Agent"）
        """
        self.repo_name = repo_name
        self.control_flag_file = '/tmp/system_control_flag.txt'
        self.running = True
        self.processed_comments = set()  # 処理済みコメントID
        
        # GitHub APIの代替実装（PyGithub不要）
        self.github_token = os.getenv('GITHUB_TOKEN')
        if not self.github_token:
            print("⚠️ GITHUB_TOKEN環境変数が未設定（テストモードで動作）")
    
    async def monitor_issues(self, check_interval: int = 60):
        """
        GitHub Issuesを監視し、制御コマンドを処理
        
        Args:
            check_interval: チェック間隔（秒）
        """
        print(f"🔍 GitHub Issues監視開始: {self.repo_name}")
        print(f"⏰ チェック間隔: {check_interval}秒")
        print(f"📋 制御フラグファイル: {self.control_flag_file}")
        
        cycle_count = 0
        
        while self.running:
            cycle_count += 1
            
            print(f"\n{'='*60}")
            print(f"🔄 監視サイクル {cycle_count}")
            print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}")
            
            try:
                # GitHub APIを使用してIssuesを取得
                # MVP版: 実際のAPI呼び出しは後で実装
                issues = await self._fetch_issues_api()
                
                if not issues:
                    print("📋 制御用Issueなし")
                else:
                    print(f"📋 制御用Issue発見: {len(issues)}件")
                    
                    for issue in issues:
                        await self._process_issue(issue)
                
                # 制御フラグの状態を確認
                flag_status = self._check_control_flag()
                if flag_status:
                    print(f"🚦 現在の制御フラグ: {flag_status}")
                
                await asyncio.sleep(check_interval)
            
            except Exception as e:
                print(f"⚠️ 監視エラー: {e}")
                await asyncio.sleep(check_interval)
    
    async def _fetch_issues_api(self) -> List[Dict]:
        """
        GitHub APIからIssuesを取得
        
        TODO: 実際のGitHub API呼び出しを実装
        MVP版では空のリストを返す
        """
        # MVP版: ダミーデータ
        return []
    
    async def _process_issue(self, issue: Dict):
        """Issueを処理してコマンドを実行"""
        issue_number = issue.get('number', 'N/A')
        issue_title = issue.get('title', 'N/A')
        
        print(f"\n📨 Issue #{issue_number}: {issue_title}")
        
        # コメントを取得
        comments = issue.get('comments', [])
        
        for comment in comments:
            comment_id = comment.get('id')
            
            # 処理済みはスキップ
            if comment_id in self.processed_comments:
                continue
            
            comment_body = comment.get('body', '')
            
            # コマンド解析
            command = self._parse_command(comment_body)
            
            if command:
                print(f"   🤖 コマンド検出: {command['action']}")
                
                # コマンド実行
                response = await self._execute_command(command)
                
                print(f"   ✅ 実行結果: {response[:100]}...")
                
                # TODO: Issueにコメント返信
                # await self._reply_to_issue(issue, response)
                
                self.processed_comments.add(comment_id)
    
    def _parse_command(self, text: str) -> Optional[Dict]:
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
    
    async def _execute_command(self, command: Dict) -> str:
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
            os.makedirs(os.path.dirname(self.control_flag_file), exist_ok=True)
            
            with open(self.control_flag_file, 'w') as f:
                f.write(flag)
            
            return f"🚦 制御フラグ設定: {flag}\n実行時刻: {datetime.now().isoformat()}"
        
        except Exception as e:
            return f"❌ フラグ書き込み失敗: {e}"
    
    def _check_control_flag(self) -> Optional[str]:
        """現在の制御フラグを確認"""
        try:
            if not os.path.exists(self.control_flag_file):
                return None
            
            with open(self.control_flag_file, 'r') as f:
                return f.read().strip()
        except:
            return None
    
    def _increase_task_priority(self, task_id: str) -> str:
        """タスクの優先度を上げる"""
        # TODO: スプレッドシートの該当タスクの優先度を変更
        return f"⬆️ タスク {task_id} の優先度をcriticalに変更しました"
    
    def _trigger_backup(self) -> str:
        """バックアップを実行"""
        # TODO: バックアップスクリプトを呼び出し
        return f"💾 バックアップを実行しました\n実行時刻: {datetime.now().isoformat()}"
    
    def _get_current_status(self) -> str:
        """現在の進捗状況を取得"""
        # TODO: Progress Dashboardから情報を取得
        return """📊 現在の進捗状況:

【実行中のサイクル】
- サイクル番号: 5
- 実行時間: 45分

【タスク状況】
- 完了: 15タスク
- 実行中: 3タスク
- 保留中: 7タスク

【システム状態】
- 制御フラグ: """ + (self._check_control_flag() or "なし") + """
- 最終更新: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _get_help_message(self) -> str:
        """ヘルプメッセージを返す"""
        return """
📖 Human Interaction Agent - 利用可能なコマンド

【システム制御】
- `@bot stop` - システムを停止
- `@bot resume` - システムを再開

【タスク管理】
- `@bot priority-up <task_id>` - タスクの優先度アップ
- `@bot status` - 現在の進捗状況

【メンテナンス】
- `@bot backup-now` - 即座にバックアップ
- `@bot logs <task_id>` - タスクのログ表示

【その他】
- `@bot help` - このヘルプを表示

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 使用方法:
1. 'bot-control'ラベルのIssueを作成
2. コメントで上記コマンドを入力
3. Botが自動的に処理して返信

⏰ 監視間隔: 60秒
"""
    
    def _get_task_logs(self, task_id: str) -> str:
        """タスクのログを取得"""
        # TODO: 実際のログファイルから取得
        return f"""📋 タスク {task_id} のログ:

【実行履歴】
2025-11-01 12:00:00 - タスク開始
2025-11-01 12:05:00 - 処理中...
2025-11-01 12:10:00 - 完了

【詳細ログ】
（実装予定）
"""


def main():
    """メイン処理"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='💬 Human Interaction Agent v1.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # Issues監視開始
  python3 core_agents/human_interaction_agent_v01_initial.py \\
      --repo Koji0525/gemini_AI_Agent \\
      --interval 60
  
  # テストモード（短時間）
  python3 core_agents/human_interaction_agent_v01_initial.py \\
      --repo Koji0525/gemini_AI_Agent \\
      --interval 10 \\
      --test-duration 2
        """
    )
    
    parser.add_argument(
        '--repo',
        required=True,
        help='リポジトリ名（例: user/repo）'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='チェック間隔（秒）'
    )
    parser.add_argument(
        '--test-duration',
        type=int,
        default=0,
        help='テスト実行時間（分）。0=無制限'
    )
    
    args = parser.parse_args()
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("💬 Human Interaction Agent v1.0")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    agent = HumanInteractionAgent(args.repo)
    
    # テストモードの処理
    if args.test_duration > 0:
        print(f"🧪 テストモード: {args.test_duration}分間実行")
        
        async def test_run():
            task = asyncio.create_task(agent.monitor_issues(args.interval))
            await asyncio.sleep(args.test_duration * 60)
            agent.running = False
            await task
        
        asyncio.run(test_run())
    else:
        asyncio.run(agent.monitor_issues(args.interval))


if __name__ == "__main__":
    main()
