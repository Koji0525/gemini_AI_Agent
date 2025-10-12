#!/usr/bin/env python3
"""
Claude 対話型エージェント（継続対話版）
実行結果をClaudeに送り返して次の指示を受ける
"""
import os
import sys
import subprocess
import anthropic
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import json

load_dotenv()

class InteractiveClaudeAgent:
    def __init__(self, max_iterations=5):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY が設定されていません")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"
        self.max_iterations = max_iterations
        
        # ログファイル
        self.log_dir = Path('logs')
        self.log_dir.mkdir(exist_ok=True)
        self.conv_log = self.log_dir / 'interactive_conversation.log'
        self.session_file = self.log_dir / f'session_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        # 会話履歴
        self.conversation_history = []
        self.execution_results = []
    
    def log(self, message, level="INFO"):
        """ログ出力"""
        timestamp = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
        emoji = {
            "INFO": "📝", "SUCCESS": "✅", "ERROR": "❌",
            "DEBUG": "🐛", "WARN": "⚠️", "CLAUDE": "🤖"
        }.get(level, "📝")
        
        log_msg = f"{timestamp} [{level}] {message}"
        print(f"{emoji} {message}")
        
        with open(self.conv_log, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    
    def send_to_claude(self, user_message: str) -> str:
        """Claude APIに送信"""
        self.log("=" * 70)
        self.log("📤 Claude に送信中...", "CLAUDE")
        self.log(f"メッセージ: {user_message[:200]}...", "DEBUG")
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": user_message}]
            )
            
            response = message.content[0].text
            self.log("📥 Claude からの応答:", "CLAUDE")
            self.log(response)
            self.log("=" * 70)
            
            return response
            
        except Exception as e:
            self.log(f"API エラー: {e}", "ERROR")
            return ""
    
    def extract_commands(self, response: str):
        """コマンド抽出"""
        import re
        commands = []
        
        for match in re.finditer(r'```(?:bash|sh)\n(.*?)```', response, re.DOTALL):
            for line in match.group(1).split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    commands.append(line)
        
        return commands
    
    def execute_command(self, command: str) -> dict:
        """コマンド実行"""
        self.log(f"💻 実行: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = {
                'command': command,
                'returncode': result.returncode,
                'stdout': result.stdout[:2000],  # 最大2000文字
                'stderr': result.stderr[:1000],
                'success': result.returncode == 0
            }
            
            if result.returncode == 0:
                self.log(f"✅ 成功", "SUCCESS")
                if result.stdout:
                    self.log(f"出力:\n{result.stdout[:500]}")
            else:
                self.log(f"❌ エラー（コード: {result.returncode}）", "ERROR")
                if result.stderr:
                    self.log(f"エラー:\n{result.stderr[:300]}", "ERROR")
            
            return output
            
        except subprocess.TimeoutExpired:
            self.log("⏰ タイムアウト", "ERROR")
            return {
                'command': command,
                'returncode': -1,
                'stdout': '',
                'stderr': 'タイムアウト（60秒）',
                'success': False
            }
        except Exception as e:
            self.log(f"実行エラー: {e}", "ERROR")
            return {
                'command': command,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False
            }
    
    def format_execution_results(self, results: list) -> str:
        """実行結果をフォーマット"""
        formatted = "\n=== 前回の実行結果 ===\n"
        
        for i, result in enumerate(results, 1):
            formatted += f"\n[コマンド {i}]\n"
            formatted += f"$ {result['command']}\n"
            formatted += f"終了コード: {result['returncode']}\n"
            
            if result['stdout']:
                formatted += f"\n出力:\n{result['stdout'][:500]}\n"
            
            if result['stderr']:
                formatted += f"\nエラー:\n{result['stderr'][:300]}\n"
            
            formatted += f"\n結果: {'✅ 成功' if result['success'] else '❌ 失敗'}\n"
            formatted += "-" * 50 + "\n"
        
        return formatted
    
    def run_interactive(self, initial_instruction: str):
        """対話型実行"""
        self.log("")
        self.log("=" * 70)
        self.log("🤖 対話型Claudeエージェント 起動", "SUCCESS")
        self.log("=" * 70)
        self.log(f"最大反復回数: {self.max_iterations}")
        self.log(f"初期指示: {initial_instruction}")
        
        current_instruction = initial_instruction
        
        for iteration in range(self.max_iterations):
            self.log("")
            self.log("=" * 70)
            self.log(f"🔄 反復 {iteration + 1}/{self.max_iterations}", "INFO")
            self.log("=" * 70)
            
            # 前回の実行結果がある場合は追加
            if self.execution_results:
                results_summary = self.format_execution_results(self.execution_results)
                current_instruction = f"{current_instruction}\n\n{results_summary}\n\n上記の結果を踏まえて、次に実行すべきことを提案してください。完了した場合は「完了」と明記してください。"
            
            # Claudeに送信
            response = self.send_to_claude(current_instruction)
            
            if not response:
                self.log("応答なし。終了します。", "ERROR")
                break
            
            # 会話履歴に追加
            self.conversation_history.append({
                'iteration': iteration + 1,
                'instruction': current_instruction[:200],
                'response': response,
                'timestamp': datetime.now().isoformat()
            })
            
            # 完了チェック
            if '完了' in response and ('タスク完了' in response or 'すべて完了' in response or '作業完了' in response):
                self.log("🎉 Claudeがタスク完了を報告しました", "SUCCESS")
                break
            
            # コマンド抽出
            commands = self.extract_commands(response)
            
            if not commands:
                self.log("実行可能なコマンドがありません。次の指示を待ちます。", "WARN")
                
                # Claudeの応答にコマンドがない場合は対話を続ける
                current_instruction = f"前回の応答にコマンドがありませんでした。\n\n前回の応答:\n{response[:500]}\n\n具体的なコマンドを含めて、次のステップを提案してください。"
                continue
            
            self.log(f"🔍 {len(commands)}個のコマンドを検出")
            
            # コマンド実行
            self.execution_results = []  # リセット
            for i, cmd in enumerate(commands[:5], 1):  # 最大5個
                self.log(f"\n[{i}/{min(len(commands), 5)}] 実行中...")
                result = self.execute_command(cmd)
                self.execution_results.append(result)
            
            # 次の反復のための指示を準備
            current_instruction = "上記のコマンド実行結果を確認してください。"
        
        # セッション保存
        self.save_session()
        
        self.log("")
        self.log("=" * 70)
        self.log("🏁 対話型エージェント終了", "SUCCESS")
        self.log("=" * 70)
        self.log(f"総反復回数: {len(self.conversation_history)}")
        self.log(f"実行コマンド数: {sum(len(self.extract_commands(h['response'])) for h in self.conversation_history)}")
    
    def save_session(self):
        """セッション保存"""
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'max_iterations': self.max_iterations,
            'actual_iterations': len(self.conversation_history),
            'conversation_history': self.conversation_history,
            'final_results': self.execution_results
        }
        
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        self.log(f"💾 セッション保存: {self.session_file}", "SUCCESS")

if __name__ == "__main__":
    # カスタム指示読み込み
    custom_file = Path('CUSTOM_INSTRUCTION.txt')
    
    if custom_file.exists():
        instruction = custom_file.read_text(encoding='utf-8')
        custom_file.unlink()
    else:
        instruction = "プロジェクトの状態を確認してください"
    
    agent = InteractiveClaudeAgent(max_iterations=5)
    agent.run_interactive(instruction)
