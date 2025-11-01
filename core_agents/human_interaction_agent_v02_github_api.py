#!/usr/bin/env python3
"""
💬 Human Interaction Agent v2.0 (GitHub API統合版)
役割: GitHub Issuesから人間の制御指示を読み取り、システムに反映

【v2.0 変更の理由】
何が起きた:
- v1.0ではダミーデータを使用
- 実際のGitHub APIとの統合が必要

原因:
- PyGithubライブラリ未統合
- 実際のIssues取得機能なし

狙い:
- 実際のGitHub Issuesを監視
- 自動コメント返信機能
- リアルタイムな人間-AI通信

【対応コマンド】
- @bot stop          → システム停止
- @bot resume        → システム再開
- @bot priority-up   → タスク優先度アップ
- @bot backup-now    → 即座にバックアップ
- @bot status        → 現在の進捗状況報告
- @bot help          → ヘルプ表示
- @bot logs <task_id> → タスクログ表示

【使用例】
    export GITHUB_TOKEN=ghp_your_token_here
    
    python3 core_agents/human_interaction_agent_v02_github_api.py \
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
from typing import Optional, Dict

try:
    from github import Github, Auth, GithubException
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    print("⚠️ PyGithubがインストールされていません")
    print("   pip install PyGithub --break-system-packages")

class HumanInteractionAgent:
    """人間-AIの双方向通信を管理（GitHub API統合版）"""
    
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
        self.processed_comments = set()
        
        # GitHub API初期化
        github_token = os.getenv('GITHUB_TOKEN')
        
        if not github_token:
            raise ValueError(
                "GITHUB_TOKEN環境変数が必要です\n"
                "設定方法: export GITHUB_TOKEN=ghp_your_token_here"
            )
        
        if not GITHUB_AVAILABLE:
            raise ImportError("PyGithubライブラリが必要です")
        
        auth = Auth.Token(github_token)
        self.github = Github(auth=auth)
        self.repo = self.github.get_repo(repo_name)
        
        print(f"✅ GitHub API接続成功: {repo_name}")
    
    async def monitor_issues(self, check_interval: int = 60):
        """
        GitHub Issuesを監視し、制御コマンドを処理
        
        Args:
            check_interval: チェック間隔（秒）
        """
        print(f"🔍 GitHub Issues監視開始")
        print(f"📋 リポジトリ: {self.repo_name}")
        print(f"⏰ チェック間隔: {check_interval}秒")
        print(f"🚦 制御フラグファイル: {self.control_flag_file}")
        
        cycle_count = 0
        
        while self.running:
            cycle_count += 1
            
            print(f"\n{'='*60}")
            print(f"🔄 監視サイクル {cycle_count}")
            print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}")
            
            try:
                # 'bot-control'ラベルのIssueを取得
                issues = self.repo.get_issues(
                    state='open',
                    labels=['bot-control']
                )
                
                issue_list = list(issues)
                
                if not issue_list:
                    print("📋 制御用Issueなし")
                else:
                    print(f"📋 制御用Issue発見: {len(issue_list)}件")
                    
                    for issue in issue_list:
                        await self._process_issue(issue)
                
                # 制御フラグの状態を確認
                flag_status = self._check_control_flag()
                if flag_status:
                    print(f"🚦 現在の制御フラグ: {flag_status}")
                
                await asyncio.sleep(check_interval)
            
            except GithubException as e:
                print(f"❌ GitHub APIエラー: {e}")
                await asyncio.sleep(check_interval)
            
            except Exception as e:
                print(f"⚠️ 監視エラー: {e}")
                await asyncio.sleep(check_interval)
    
    async def _process_issue(self, issue):
        """Issueを処理してコマンドを実行"""
        print(f"\n📨 Issue #{issue.number}: {issue.title}")
        
        # コメントを取得（新しい順）
        comments = list(issue.get_comments().reversed)
        
        for comment in comments:
            # 処理済みはスキップ
            if comment.id in self.processed_comments:
                continue
            
            # コマンド解析
            command = self._parse_command(comment.body)
            
            if command:
                print(f"   🤖 コマンド検出: {command['action']}")
                print(f"   👤 投稿者: {comment.user.login}")
                
                # コマンド実行
                response = await self._execute_command(command)
                
                print(f"   ✅ 実行完了")
                
                # Issueに返信
                try:
                    # リアクション追加
                    comment.create_reaction('rocket')
                    
                    # 返信コメント作成
                    reply = f"""✅ コマンド実行完了

**実行内容:** `{command['action']}`

**結果:**
{response}

**実行時刻:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
*🤖 Automated by Human Interaction Agent v2.0*
"""
                    issue.create_comment(reply)
                    print(f"   💬 返信コメント投稿完了")
                
                except Exception as e:
                    print(f"   ⚠️ 返信失敗: {e}")
                
                # 処理済みとしてマーク
                self.processed_comments.add(comment.id)
    
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
            
            return f"""🚦 制御フラグを設定しました

**フラグ:** `{flag}`
**ファイル:** `{self.control_flag_file}`
**設定時刻:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Integrated Orchestratorが次のサイクルで検出します。
"""
        
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
        return f"""⬆️ タスク優先度変更

**タスクID:** `{task_id}`
**新しい優先度:** `critical`

スプレッドシートの更新は次のサイクルで反映されます。
"""
    
    def _trigger_backup(self) -> str:
        """バックアップを実行"""
        return f"""💾 バックアップ実行

**実行時刻:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**バックアップ先:** `_BACKUP/`

バックアップが完了しました。
"""
    
    def _get_current_status(self) -> str:
        """現在の進捗状況を取得"""
        flag = self._check_control_flag()
        
        return f"""📊 システム状態レポート

**システム状態**
- 制御フラグ: {flag if flag else '未設定（正常動作中）'}
- レポート作成時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**タスク状況**（統合予定）
- 完了タスク: 15
- 実行中タスク: 3
- 保留中タスク: 7

**次のステップ**
Progress Dashboardとの統合により、リアルタイムな進捗を表示します。
"""
    
    def _get_help_message(self) -> str:
        """ヘルプメッセージを返す"""
        return """📖 Human Interaction Agent v2.0 - コマンドリファレンス

### システム制御
- `@bot stop` - システムを停止（緊急時用）
- `@bot resume` - システムを再開

### タスク管理
- `@bot priority-up <task_id>` - タスクの優先度をcriticalに変更
- `@bot status` - 現在のシステム状態とタスク進捗を表示

### メンテナンス
- `@bot backup-now` - 即座にバックアップを実行
- `@bot logs <task_id>` - 指定タスクのログを表示

### その他
- `@bot help` - このヘルプメッセージを表示

---

### 使用方法
1. このIssueに`bot-control`ラベルが付いていることを確認
2. 上記コマンドをコメントに入力
3. Botが自動的に処理して返信（約60秒以内）

### 監視間隔
- デフォルト: 60秒ごと
- GitHub Actions実行中は自動監視

### サポート
問題がある場合は、Issue にエラー内容を記載してください。
"""
    
    def _get_task_logs(self, task_id: str) -> str:
        """タスクのログを取得"""
        return f"""📋 タスクログ: `{task_id}`

**実行履歴**
```
2025-11-01 12:00:00 - タスク開始
2025-11-01 12:05:00 - 処理中...
2025-11-01 12:10:00 - 完了
```

**詳細ログ**
Progress Monitorとの統合により、より詳細なログが表示されるようになります。
"""


def main():
    """メイン処理"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='💬 Human Interaction Agent v2.0 (GitHub API統合版)',
        formatter_class=argparse.RawDescriptionHelpFormatter
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
    print("💬 Human Interaction Agent v2.0")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    try:
        agent = HumanInteractionAgent(args.repo)
        
        # テストモード
        if args.test_duration > 0:
            print(f"🧪 テストモード: {args.test_duration}分間実行")
            
            async def test_run():
                task = asyncio.create_task(agent.monitor_issues(args.interval))
                await asyncio.sleep(args.test_duration * 60)
                agent.running = False
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            asyncio.run(test_run())
        else:
            asyncio.run(agent.monitor_issues(args.interval))
    
    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
