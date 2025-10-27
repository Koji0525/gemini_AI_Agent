#!/usr/bin/env python3
"""
Claude 統合エージェント（完全修正版）
- 強化されたエラーハンドリング
- タイムアウト設定
- リアルタイム進捗表示
"""
import os
import sys
import subprocess
import anthropic
import signal
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("API呼び出しがタイムアウトしました")

class ClaudeUnifiedAgent:
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY が設定されていません")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"
        
        # ログファイル
        self.log_dir = Path('logs')
        self.log_dir.mkdir(exist_ok=True)
        self.conv_log = self.log_dir / 'unified_conversation.log'
        self.debug_log = self.log_dir / 'unified_debug.log'
        self.error_log = self.log_dir / 'unified_error.log'
    
    def log(self, message, level="INFO"):
        """ログ出力"""
        timestamp = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
        
        # レベルに応じた絵文字
        emoji = {
            "INFO": "📝",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "DEBUG": "🐛",
            "WARN": "⚠️"
        }.get(level, "📝")
        
        log_msg = f"{timestamp} [{level}] {message}"
        print(f"{emoji} {message}")
        
        # ファイルに記録
        with open(self.conv_log, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
        
        # DEBUGは別ファイルにも
        if level == "DEBUG":
            with open(self.debug_log, 'a', encoding='utf-8') as f:
                f.write(log_msg + '\n')
        
        # ERRORも別ファイルに
        if level == "ERROR":
            with open(self.error_log, 'a', encoding='utf-8') as f:
                f.write(log_msg + '\n')
    
    def run_autonomous_system(self):
        """自律システム実行"""
        self.log("=" * 70)
        self.log("🚀 自律システム実行開始")
        self.log("=" * 70)
        
        try:
            result = subprocess.run(
                'python autonomous_system.py',
                shell=True,
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if result.returncode == 0:
                self.log("✅ 自律システム実行成功", "SUCCESS")
                # 出力の最後の部分を表示
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    self.log(f"出力:\n{''.join(lines[-10:])}", "DEBUG")
            else:
                self.log(f"❌ 自律システムエラー: {result.returncode}", "ERROR")
                if result.stderr:
                    self.log(f"エラー詳細:\n{result.stderr[:500]}", "ERROR")
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            self.log("⏰ 自律システムがタイムアウト", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ 例外発生: {e}", "ERROR")
            return False
    
    def send_to_claude(self, prompt: str) -> str:
        """Claude APIに送信（タイムアウト付き）"""
        self.log("=" * 70)
        self.log("📤 Claude APIに送信中...")
        self.log("=" * 70)
        self.log(f"プロンプト文字数: {len(prompt)}", "DEBUG")
        
        try:
            # タイムアウト設定（60秒）
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(60)
            
            self.log("API呼び出し開始...", "DEBUG")
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            signal.alarm(0)  # タイムアウトキャンセル
            
            self.log("API呼び出し成功！", "SUCCESS")
            
            response = message.content[0].text
            self.log(f"応答文字数: {len(response)}", "DEBUG")
            
            self.log("")
            self.log("=" * 70)
            self.log("📥 Claude からの応答:")
            self.log("=" * 70)
            self.log(response)
            self.log("=" * 70)
            
            return response
            
        except TimeoutError:
            signal.alarm(0)
            self.log("⏰ API呼び出しがタイムアウトしました（60秒）", "ERROR")
            return ""
        
        except anthropic.APIConnectionError as e:
            self.log(f"❌ API接続エラー: {e}", "ERROR")
            return ""
        
        except anthropic.RateLimitError as e:
            self.log(f"❌ レート制限エラー: {e}", "ERROR")
            return ""
        
        except anthropic.APIStatusError as e:
            self.log(f"❌ APIステータスエラー: {e.status_code} - {e.message}", "ERROR")
            return ""
        
        except Exception as e:
            self.log(f"❌ 予期しないエラー: {type(e).__name__} - {e}", "ERROR")
            import traceback
            self.log(f"トレースバック:\n{traceback.format_exc()}", "ERROR")
            return ""
        
        finally:
            signal.alarm(0)
    
    def extract_commands(self, response: str):
        """コマンド抽出"""
        import re
        commands = []
        
        for match in re.finditer(r'```bash\n(.*?)```', response, re.DOTALL):
            for line in match.group(1).split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    commands.append(line)
        
        return commands
    
    def execute_commands(self, commands: list):
        """コマンド実行"""
        if not commands:
            self.log("実行可能なコマンドはありません", "INFO")
            return
        
        self.log(f"🔍 {len(commands)}個のコマンドを検出")
        for i, cmd in enumerate(commands, 1):
            self.log(f"  {i}. {cmd}")
        
        self.log("")
        self.log("=" * 70)
        self.log("⚙️ コマンド実行開始")
        self.log("=" * 70)
        
        for i, cmd in enumerate(commands, 1):
            self.log(f"\n[{i}/{len(commands)}] $ {cmd}")
            
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.stdout:
                    output = result.stdout[:500]
                    self.log(f"出力:\n{output}")
                    if len(result.stdout) > 500:
                        self.log("...(省略)...")
                
                if result.returncode != 0:
                    self.log(f"⚠️ エラー（終了コード: {result.returncode}）", "WARN")
                    if result.stderr:
                        self.log(f"{result.stderr[:200]}", "ERROR")
                else:
                    self.log("✅ 成功", "SUCCESS")
                    
            except subprocess.TimeoutExpired:
                self.log("⏰ コマンドがタイムアウト", "ERROR")
            except Exception as e:
                self.log(f"❌ 実行エラー: {e}", "ERROR")
        
        self.log("")
        self.log("=" * 70)
        self.log("✅ すべてのコマンド実行完了", "SUCCESS")
        self.log("=" * 70)
    
    def run(self):
        """メイン実行"""
        self.log("")
        self.log("=" * 70)
        self.log("🤖 Claude統合エージェント 起動")
        self.log("=" * 70)
        self.log(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. カスタム指示確認
        custom_file = Path('CUSTOM_INSTRUCTION.txt')
        custom_instruction = ""
        
        if custom_file.exists():
            custom_instruction = custom_file.read_text(encoding='utf-8')
            self.log("")
            self.log("=" * 70)
            self.log("📝 カスタム指示を検出しました:")
            self.log("=" * 70)
            self.log(custom_instruction)
            self.log("=" * 70)
            custom_file.unlink()
            self.log("🗑️ カスタム指示ファイルを削除", "DEBUG")
        
        # 2. 自律システム実行
        if not self.run_autonomous_system():
            self.log("自律システムが失敗しましたが続行します", "WARN")
        
        # 3. プロンプト構築
        self.log("")
        self.log("📋 プロンプト構築中...", "DEBUG")
        
        prompts = sorted(Path('.').glob('claude_prompt_*.txt'))
        if not prompts:
            self.log("❌ プロンプトファイルが見つかりません", "ERROR")
            return
        
        latest_prompt = prompts[-1]
        self.log(f"最新プロンプト: {latest_prompt}", "DEBUG")
        
        prompt_text = latest_prompt.read_text(encoding='utf-8')
        self.log(f"プロンプト読み込み: {len(prompt_text)}文字", "DEBUG")
        
        # カスタム指示追加
        if custom_instruction:
            prompt_text += f"\n\n{'='*70}\n🎯 【重要】追加の指示\n{'='*70}\n{custom_instruction}\n{'='*70}\n\n上記の追加指示を最優先で実行してください。"
            self.log(f"カスタム指示を追加: {len(prompt_text)}文字", "DEBUG")
        
        # 4. Claude API送信
        response = self.send_to_claude(prompt_text)
        
        if not response:
            self.log("❌ Claude APIからの応答がありません", "ERROR")
            return
        
        # 5. 応答保存
        response_file = f"claude_response_{datetime.now().strftime('%H%M%S')}.txt"
        Path(response_file).write_text(response, encoding='utf-8')
        self.log(f"💾 応答を保存: {response_file}", "SUCCESS")
        
        # 6. コマンド抽出・実行
        commands = self.extract_commands(response)
        self.execute_commands(commands)
        
        self.log("")
        self.log("=" * 70)
        self.log("🏁 Claude統合エージェント 終了", "SUCCESS")
        self.log("=" * 70)

if __name__ == "__main__":
    try:
        agent = ClaudeUnifiedAgent()
        agent.run()
    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによって中断されました")
    except Exception as e:
        print(f"❌ 致命的エラー: {e}")
        import traceback
        traceback.print_exc()
