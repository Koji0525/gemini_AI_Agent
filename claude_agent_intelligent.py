#!/usr/bin/env python3
"""
インテリジェント対話型Claudeエージェント
- エラー自動修正
- 継続対話
- 進捗レポート
"""
import os
import sys
import subprocess
import anthropic
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import json
import re

load_dotenv()

class IntelligentClaudeAgent:
    def __init__(self, max_iterations=10):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY が設定されていません")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"
        self.max_iterations = max_iterations
        
        # ログ
        self.log_dir = Path('logs')
        self.log_dir.mkdir(exist_ok=True)
        self.conv_log = self.log_dir / 'intelligent_conversation.log'
        
        # 状態管理
        self.conversation_history = []
        self.execution_results = []
        self.error_fix_attempts = {}
        self.current_iteration = 0
        self.total_commands = 0
        self.successful_commands = 0
        self.failed_commands = 0
    
    def log(self, message, level="INFO"):
        """ログ出力"""
        timestamp = datetime.now().strftime('[%H:%M:%S]')
        emoji = {
            "INFO": "��", "SUCCESS": "✅", "ERROR": "❌",
            "DEBUG": "🐛", "WARN": "⚠️", "CLAUDE": "🤖",
            "FIX": "🔧", "TEST": "🧪"
        }.get(level, "📝")
        
        log_msg = f"{timestamp} [{level}] {message}"
        print(f"{emoji} {message}", flush=True)
        
        with open(self.conv_log, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    
    def send_to_claude(self, user_message: str) -> str:
        """Claude API送信"""
        self.log("=" * 70, "CLAUDE")
        self.log(f"📤 反復 {self.current_iteration}/{self.max_iterations}", "CLAUDE")
        self.log(f"送信: {user_message[:150]}...", "DEBUG")
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                messages=[{"role": "user", "content": user_message}]
            )
            
            response = message.content[0].text
            self.log("📥 Claude応答受信", "CLAUDE")
            self.log(response[:500] + "..." if len(response) > 500 else response, "CLAUDE")
            self.log("=" * 70, "CLAUDE")
            
            return response
            
        except Exception as e:
            self.log(f"API エラー: {e}", "ERROR")
            return ""
    
    def extract_commands(self, response: str):
        """コマンド抽出"""
        commands = []
        
        # bashブロック
        for match in re.finditer(r'```(?:bash|sh|shell)\n(.*?)```', response, re.DOTALL):
            for line in match.group(1).split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    commands.append(line)
        
        # pythonブロック（ファイル作成など）
        for match in re.finditer(r'```python\n(.*?)```', response, re.DOTALL):
            code = match.group(1)
            # 一時ファイルに保存して実行
            temp_file = Path('temp_fix_script.py')
            temp_file.write_text(code, encoding='utf-8')
            commands.append(f'python {temp_file}')
        
        return commands
    
    def execute_command(self, command: str, context: str = "") -> dict:
        """コマンド実行"""
        self.log(f"💻 実行: {command}")
        self.total_commands += 1
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=os.getcwd()
            )
            
            success = result.returncode == 0
            
            output = {
                'command': command,
                'returncode': result.returncode,
                'stdout': result.stdout[:3000],
                'stderr': result.stderr[:2000],
                'success': success,
                'context': context,
                'timestamp': datetime.now().isoformat()
            }
            
            if success:
                self.log(f"✅ 成功", "SUCCESS")
                self.successful_commands += 1
                if result.stdout:
                    self.log(f"出力:\n{result.stdout[:800]}")
            else:
                self.log(f"❌ エラー（コード: {result.returncode}）", "ERROR")
                self.failed_commands += 1
                if result.stderr:
                    self.log(f"エラー:\n{result.stderr[:500]}", "ERROR")
            
            return output
            
        except subprocess.TimeoutExpired:
            self.log("⏰ タイムアウト（60秒）", "ERROR")
            self.failed_commands += 1
            return {
                'command': command,
                'returncode': -1,
                'stdout': '',
                'stderr': 'タイムアウト',
                'success': False,
                'context': context
            }
        except Exception as e:
            self.log(f"実行エラー: {e}", "ERROR")
            self.failed_commands += 1
            return {
                'command': command,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False,
                'context': context
            }
    
    def analyze_error(self, result: dict) -> str:
        """エラー分析"""
        error_key = result['command']
        
        if error_key not in self.error_fix_attempts:
            self.error_fix_attempts[error_key] = 0
        
        self.error_fix_attempts[error_key] += 1
        attempt_count = self.error_fix_attempts[error_key]
        
        analysis = f"""
エラー分析（修正試行 {attempt_count}回目）

【実行コマンド】
{result['command']}

【終了コード】
{result['returncode']}

【標準出力】
{result['stdout'][:1000]}

【エラー出力】
{result['stderr'][:1000]}

【コンテキスト】
{result.get('context', 'なし')}

このエラーを解決するための具体的な修正方法を提案してください。
- ファイルが存在しない場合は作成方法を
- 構文エラーの場合は修正コードを
- 依存関係の問題の場合はインストールコマンドを

修正後に再実行する完全なコマンドを```bash```ブロックで提示してください。
"""
        return analysis
    
    def format_results_summary(self, results: list) -> str:
        """実行結果サマリー"""
        if not results:
            return ""
        
        summary = "\n【前回の実行結果】\n"
        
        for i, result in enumerate(results[-3:], 1):  # 最新3件
            summary += f"\n[コマンド {i}]\n"
            summary += f"$ {result['command']}\n"
            summary += f"結果: {'✅ 成功' if result['success'] else '❌ 失敗'}\n"
            
            if not result['success']:
                summary += f"エラー: {result['stderr'][:300]}\n"
            elif result['stdout']:
                summary += f"出力: {result['stdout'][:500]}\n"
            
            summary += "-" * 50 + "\n"
        
        return summary
    
    def check_completion(self, response: str) -> bool:
        """完了判定"""
        completion_keywords = [
            'タスク完了', 'すべて完了', '作業完了', '実装完了',
            'テスト成功', 'すべて成功', '問題なし', '全て正常'
        ]
        
        return any(keyword in response for keyword in completion_keywords)
    
    def run_intelligent(self, initial_instruction: str):
        """インテリジェント実行"""
        self.log("")
        self.log("=" * 70)
        self.log("🚀 インテリジェント対話エージェント 起動", "SUCCESS")
        self.log("=" * 70)
        self.log(f"最大反復: {self.max_iterations}回")
        self.log(f"初期指示: {initial_instruction}")
        
        current_instruction = f"""
【タスク】
{initial_instruction}

【重要な指示】
1. まず現状を確認してください
2. 必要なコマンドを順番に実行してください
3. エラーが発生した場合は、原因を分析して修正してください
4. すべて完了したら「タスク完了」と明記してください

各ステップで実行すべきコマンドを```bash```ブロックで提示してください。
"""
        
        for iteration in range(self.max_iterations):
            self.current_iteration = iteration + 1
            
            self.log("")
            self.log("=" * 70)
            self.log(f"🔄 反復 {self.current_iteration}/{self.max_iterations}", "INFO")
            self.log("=" * 70)
            
            # 前回の結果を追加
            if self.execution_results:
                results_summary = self.format_results_summary(self.execution_results)
                
                # エラーがあった場合は詳細分析
                failed_results = [r for r in self.execution_results[-3:] if not r['success']]
                
                if failed_results:
                    self.log(f"🔧 エラー修正モード: {len(failed_results)}件のエラー", "FIX")
                    
                    for failed in failed_results:
                        error_analysis = self.analyze_error(failed)
                        current_instruction = error_analysis
                        break  # 1つずつ修正
                else:
                    current_instruction = f"{results_summary}\n\n上記の結果を踏まえて、次のステップを実行してください。完了していれば「タスク完了」と報告してください。"
            
            # Claude API送信
            response = self.send_to_claude(current_instruction)
            
            if not response:
                self.log("応答なし。終了", "ERROR")
                break
            
            # 会話履歴
            self.conversation_history.append({
                'iteration': self.current_iteration,
                'instruction': current_instruction[:300],
                'response': response[:500],
                'timestamp': datetime.now().isoformat()
            })
            
            # 完了チェック
            if self.check_completion(response):
                self.log("🎉 タスク完了を確認", "SUCCESS")
                break
            
            # コマンド抽出・実行
            commands = self.extract_commands(response)
            
            if not commands:
                self.log("コマンドなし。対話継続", "WARN")
                current_instruction = "コマンドが見つかりませんでした。実行すべき具体的なコマンドを```bash```ブロックで提示してください。"
                continue
            
            self.log(f"🔍 {len(commands)}個のコマンドを検出")
            
            # 実行
            self.execution_results = []
            for i, cmd in enumerate(commands[:10], 1):  # 最大10個
                self.log(f"\n[{i}/{min(len(commands), 10)}]")
                result = self.execute_command(cmd, f"反復{self.current_iteration}")
                self.execution_results.append(result)
                
                # 致命的エラーの場合は即座に次の反復へ
                if not result['success'] and result['returncode'] != 0:
                    self.log("エラー検出。修正を試みます", "FIX")
                    break
        
        # 統計
        self.log("")
        self.log("=" * 70)
        self.log("📊 実行統計", "SUCCESS")
        self.log("=" * 70)
        self.log(f"総反復回数: {self.current_iteration}")
        self.log(f"総コマンド数: {self.total_commands}")
        self.log(f"成功: {self.successful_commands}")
        self.log(f"失敗: {self.failed_commands}")
        self.log(f"成功率: {(self.successful_commands/self.total_commands*100) if self.total_commands > 0 else 0:.1f}%")
        
        # セッション保存
        self.save_session()
    
    def save_session(self):
        """セッション保存"""
        session = {
            'timestamp': datetime.now().isoformat(),
            'max_iterations': self.max_iterations,
            'actual_iterations': self.current_iteration,
            'statistics': {
                'total_commands': self.total_commands,
                'successful': self.successful_commands,
                'failed': self.failed_commands
            },
            'conversation_history': self.conversation_history,
            'execution_results': self.execution_results
        }
        
        session_file = self.log_dir / f'session_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, ensure_ascii=False, indent=2)
        
        self.log(f"💾 セッション保存: {session_file}", "SUCCESS")

if __name__ == "__main__":
    import sys
    
    # 引数: max_iterations
    max_iter = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    # カスタム指示
    custom_file = Path('CUSTOM_INSTRUCTION.txt')
    if custom_file.exists():
        instruction = custom_file.read_text(encoding='utf-8')
        custom_file.unlink()
    else:
        instruction = "プロジェクトの状態を確認"
    
    agent = IntelligentClaudeAgent(max_iterations=max_iter)
    agent.run_intelligent(instruction)
