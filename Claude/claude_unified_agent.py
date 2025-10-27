#!/usr/bin/env python3
"""
Claude 統合エージェント（完全版）
- 自律システム実行
- カスタム指示対応
- Claude API自動対話
- 詳細ログ出力
"""
import os
import sys
import subprocess
import anthropic
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class ClaudeUnifiedAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = "claude-sonnet-4-20250514"
        self.log_dir = Path('logs')
        self.log_dir.mkdir(exist_ok=True)
        self.conversation_log = self.log_dir / 'unified_conversation.log'
        self.debug_log = self.log_dir / 'unified_debug.log'
        
    def log(self, message, log_type='info'):
        """統一ログ出力"""
        timestamp = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
        
        # 画面出力
        if log_type == 'debug':
            print(f"🐛 {message}")
        elif log_type == 'error':
            print(f"❌ {message}")
        elif log_type == 'success':
            print(f"✅ {message}")
        else:
            print(f"📝 {message}")
        
        # ファイル出力
        log_msg = f"{timestamp} [{log_type.upper()}] {message}\n"
        with open(self.conversation_log, 'a', encoding='utf-8') as f:
            f.write(log_msg)
        
        if log_type == 'debug':
            with open(self.debug_log, 'a', encoding='utf-8') as f:
                f.write(log_msg)
    
    def run_autonomous_system(self):
        """自律システム実行"""
        self.log("=" * 70)
        self.log("🚀 自律システム実行開始", 'info')
        self.log("=" * 70)
        
        try:
            result = subprocess.run(
                'python autonomous_system.py',
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.log("✅ 自律システム実行成功", 'success')
                if result.stdout:
                    self.log(f"出力:\n{result.stdout[:500]}", 'debug')
                return True
            else:
                self.log(f"⚠️ 自律システム実行エラー: {result.stderr[:300]}", 'error')
                return False
                
        except subprocess.TimeoutExpired:
            self.log("⏱️ 自律システムがタイムアウトしました", 'error')
            return False
        except Exception as e:
            self.log(f"❌ 自律システム例外: {e}", 'error')
            return False
    
    def load_custom_instruction(self):
        """カスタム指示を読み込む"""
        custom_file = Path('CUSTOM_INSTRUCTION.txt')
        
        if custom_file.exists():
            content = custom_file.read_text(encoding='utf-8').strip()
            if content:
                self.log("=" * 70)
                self.log("📝 カスタム指示を検出しました:", 'success')
                self.log("=" * 70)
                self.log(content)
                self.log("=" * 70)
                
                # 使用後削除
                custom_file.unlink()
                self.log("🗑️ カスタム指示ファイルを削除", 'debug')
                
                return content
        
        self.log("カスタム指示なし（通常モード）", 'debug')
        return None
    
    def build_prompt(self, custom_instruction=None):
        """プロンプトを構築"""
        self.log("📋 プロンプト構築中...", 'debug')
        
        # 最新のプロンプトファイルを探す
        prompts = sorted(Path('.').glob('claude_prompt_*.txt'))
        
        if not prompts:
            self.log("⚠️ プロンプトファイルが見つかりません", 'error')
            # 緊急用プロンプトを生成
            self.log("🆘 緊急プロンプトを生成します", 'debug')
            return self._generate_emergency_prompt(custom_instruction)
        
        latest_prompt = prompts[-1]
        self.log(f"最新プロンプト: {latest_prompt}", 'debug')
        
        prompt_text = latest_prompt.read_text(encoding='utf-8')
        self.log(f"プロンプト読み込み: {len(prompt_text)}文字", 'debug')
        
        # カスタム指示を追加
        if custom_instruction:
            self.log("カスタム指示をプロンプトに追加", 'debug')
            prompt_text += f"""

{'='*70}
🎯 【重要】追加の指示
{'='*70}
{custom_instruction}
{'='*70}

上記の追加指示を最優先で実行してください。
"""
            self.log(f"最終プロンプト: {len(prompt_text)}文字", 'debug')
        
        return prompt_text
    
    def _generate_emergency_prompt(self, custom_instruction=None):
        """緊急用プロンプト生成"""
        base = f"""
# システム状態確認

現在時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
作業ディレクトリ: {os.getcwd()}

## ファイル一覧
{self._get_file_list()}

## 最新ログ
{self._get_recent_logs()}
"""
        
        if custom_instruction:
            base += f"""

{'='*70}
🎯 【重要】ユーザーからの指示
{'='*70}
{custom_instruction}
{'='*70}
"""
        
        return base
    
    def _get_file_list(self):
        """ファイル一覧取得"""
        try:
            result = subprocess.run('ls -la', shell=True, capture_output=True, text=True)
            return result.stdout[:1000]
        except:
            return "ファイル一覧取得失敗"
    
    def _get_recent_logs(self):
        """最新ログ取得"""
        try:
            log_files = list(Path('logs').glob('*.log'))
            if log_files:
                latest = sorted(log_files)[-1]
                content = latest.read_text(encoding='utf-8')
                return content[-500:]
            return "ログなし"
        except:
            return "ログ取得失敗"
    
    def send_to_claude(self, prompt):
        """Claudeに送信"""
        self.log("=" * 70)
        self.log("📤 Claude APIに送信中...", 'info')
        self.log("=" * 70)
        
        # プロンプトプレビュー
        preview = prompt[:400] + "\n...\n" + prompt[-400:] if len(prompt) > 800 else prompt
        self.log(f"送信プロンプト:\n{preview}", 'debug')
        
        try:
            self.log("API呼び出し開始", 'debug')
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response = message.content[0].text
            
            self.log("=" * 70)
            self.log("📥 Claude からの応答を受信しました", 'success')
            self.log("=" * 70)
            self.log(response)
            self.log("=" * 70)
            
            # 応答を保存
            response_file = f"claude_response_{datetime.now().strftime('%H%M%S')}.txt"
            Path(response_file).write_text(response, encoding='utf-8')
            self.log(f"💾 応答を保存: {response_file}", 'success')
            
            return response
            
        except Exception as e:
            self.log(f"❌ API呼び出しエラー: {e}", 'error')
            raise
    
    def extract_and_execute_commands(self, response):
        """コマンド抽出と実行"""
        import re
        
        commands = []
        for match in re.finditer(r'```bash\n(.*?)```', response, re.DOTALL):
            for line in match.group(1).split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    commands.append(line)
        
        if not commands:
            self.log("実行可能なコマンドはありませんでした", 'info')
            return
        
        self.log(f"🔍 {len(commands)}個のコマンドを検出", 'success')
        for i, cmd in enumerate(commands, 1):
            self.log(f"  {i}. {cmd}", 'debug')
        
        # 自動実行（Web経由の場合）
        if not sys.stdin.isatty():
            self.log("⚙️ 自動実行モード: コマンドを実行します", 'info')
            self._execute_commands(commands)
        else:
            # ターミナルから実行の場合は確認
            confirm = input("\n実行しますか？ (y/n): ")
            if confirm.lower() == 'y':
                self._execute_commands(commands)
    
    def _execute_commands(self, commands):
        """コマンド実行"""
        self.log("=" * 70)
        self.log("⚙️ コマンド実行開始", 'info')
        self.log("=" * 70)
        
        for i, cmd in enumerate(commands, 1):
            self.log(f"\n[{i}/{len(commands)}] $ {cmd}", 'info')
            
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
                    self.log(f"出力:\n{output}", 'debug')
                    if len(result.stdout) > 500:
                        self.log("...(省略)...", 'debug')
                
                if result.returncode != 0:
                    self.log(f"⚠️ エラー: {result.stderr[:200]}", 'error')
                else:
                    self.log("✅ 成功", 'success')
                    
            except subprocess.TimeoutExpired:
                self.log("⏱️ コマンドがタイムアウトしました", 'error')
            except Exception as e:
                self.log(f"❌ 実行エラー: {e}", 'error')
        
        self.log("=" * 70)
        self.log("✅ すべてのコマンド実行完了", 'success')
        self.log("=" * 70)
    
    def run(self):
        """メイン実行"""
        start_time = datetime.now()
        
        self.log("\n\n" + "🤖 Claude統合エージェント 起動".center(70, "="))
        self.log(f"実行時刻: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("=" * 70)
        
        try:
            # 1. カスタム指示を読み込む
            custom_instruction = self.load_custom_instruction()
            
            # 2. 自律システム実行
            if not self.run_autonomous_system():
                self.log("⚠️ 自律システムに問題がありましたが続行します", 'error')
            
            # 3. プロンプト構築
            prompt = self.build_prompt(custom_instruction)
            
            # 4. Claudeに送信
            response = self.send_to_claude(prompt)
            
            # 5. コマンド実行
            self.extract_and_execute_commands(response)
            
            # 実行時間
            elapsed = (datetime.now() - start_time).total_seconds()
            self.log(f"\n⏱️ 総実行時間: {elapsed:.1f}秒", 'success')
            
        except Exception as e:
            self.log(f"❌ システムエラー: {e}", 'error')
            import traceback
            self.log(traceback.format_exc(), 'debug')
        
        self.log("=" * 70)
        self.log("🏁 Claude統合エージェント 終了")
        self.log("=" * 70 + "\n")

if __name__ == "__main__":
    print("🤖 Claude統合エージェント 起動")
    agent = ClaudeUnifiedAgent()
    agent.run()
