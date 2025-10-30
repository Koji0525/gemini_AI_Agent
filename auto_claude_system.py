#!/usr/bin/env python3
"""Claude API 自動対話システム（カスタム指示対応）"""
import os
import anthropic
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class AutoClaudeSystem:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"
        self.log_file = Path("logs/claude_conversation.log")
        self.log_file.parent.mkdir(exist_ok=True)

    def log(self, message):
        """ログ出力"""
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        log_msg = f"{timestamp} {message}\n"
        print(message)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_msg)

    def send_prompt(self, prompt: str) -> str:
        """Claudeにプロンプトを送信"""
        self.log("=" * 70)
        self.log("📤 Claude に送信中...")
        self.log("=" * 70)

        # プロンプトの一部を表示
        preview = prompt[:200] + "..." if len(prompt) > 200 else prompt
        self.log(f"プロンプト: {preview}")

        message = self.client.messages.create(
            model=self.model, max_tokens=2000, messages=[{"role": "user", "content": prompt}]
        )

        response = message.content[0].text

        self.log("")
        self.log("=" * 70)
        self.log("📥 Claude からの応答:")
        self.log("=" * 70)
        self.log(response)
        self.log("=" * 70)

        return response

    def extract_commands(self, response: str):
        """応答からコマンドを抽出"""
        import re

        commands = []
        for match in re.finditer(r"```bash\n(.*?)```", response, re.DOTALL):
            for line in match.group(1).split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    commands.append(line)
        return commands

    def run(self):
        """自動実行"""
        self.log("\n\n" + "🤖 Claude自動対話システム 開始".center(70, "="))
        self.log(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 1. カスタム指示をチェック
        custom_instruction_file = Path("CUSTOM_INSTRUCTION.txt")
        custom_instruction = ""
        if custom_instruction_file.exists():
            custom_instruction = custom_instruction_file.read_text(encoding="utf-8")
            self.log("")
            self.log("=" * 70)
            self.log("📝 カスタム指示を検出:")
            self.log("=" * 70)
            self.log(custom_instruction)
            self.log("=" * 70)
            custom_instruction_file.unlink()  # 使用後削除

        # 2. 最新のプロンプトを取得
        prompts = sorted(Path(".").glob("claude_prompt_*.txt"))
        if not prompts:
            self.log("❌ プロンプトファイルが見つかりません")
            return

        latest_prompt = prompts[-1]
        self.log(f"\n📋 プロンプトファイル: {latest_prompt}")

        prompt_text = latest_prompt.read_text()

        # カスタム指示を追加
        if custom_instruction:
            prompt_text += f"\n\n【追加の指示】\n{custom_instruction}"

        # 3. Claudeに送信
        response = self.send_prompt(prompt_text)

        # 4. 応答を保存
        response_file = f"claude_response_{datetime.now().strftime('%H%M%S')}.txt"
        Path(response_file).write_text(response, encoding="utf-8")
        self.log(f"\n💾 応答を保存: {response_file}")

        # 5. コマンドを抽出
        commands = self.extract_commands(response)
        if commands:
            self.log(f"\n🔍 {len(commands)}個のコマンドを検出")
            for i, cmd in enumerate(commands, 1):
                self.log(f"  {i}. {cmd}")

            # 6. 実行確認
            import sys

            if sys.stdin.isatty():  # ターミナルから実行
                confirm = input("\n実行しますか？ (y/n): ")
            else:  # Web経由で実行
                confirm = "y"
                self.log("\n⚙️ 自動実行モード: すべてのコマンドを実行します")

            if confirm.lower() == "y":
                import subprocess

                self.log("\n" + "=" * 70)
                self.log("⚙️ コマンド実行開始")
                self.log("=" * 70)

                for i, cmd in enumerate(commands, 1):
                    self.log(f"\n[{i}/{len(commands)}] $ {cmd}")
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                    if result.stdout:
                        self.log(f"出力:\n{result.stdout[:500]}")
                    if result.returncode != 0:
                        self.log(f"⚠️ エラー: {result.stderr[:200]}")
                    else:
                        self.log("✅ 成功")

                self.log("\n" + "=" * 70)
                self.log("✅ すべてのコマンド実行完了")
                self.log("=" * 70)
        else:
            self.log("\n📝 実行可能なコマンドはありませんでした")

        self.log("\n" + "🏁 Claude自動対話システム 終了".center(70, "=") + "\n")


if __name__ == "__main__":
    system = AutoClaudeSystem()
    system.run()
