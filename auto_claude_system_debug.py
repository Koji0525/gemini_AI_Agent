#!/usr/bin/env python3
"""Claude API 自動対話システム（完全デバッグ版）"""
import os
import sys
import anthropic
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class AutoClaudeSystemDebug:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"
        self.log_file = Path("logs/claude_conversation.log")
        self.log_file.parent.mkdir(exist_ok=True)
        self.debug_file = Path("logs/debug.log")

    def debug(self, message):
        """デバッグログ"""
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        log_msg = f"{timestamp} DEBUG: {message}\n"
        print(f"🐛 DEBUG: {message}")
        with open(self.debug_file, "a", encoding="utf-8") as f:
            f.write(log_msg)

    def log(self, message):
        """ログ出力"""
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        log_msg = f"{timestamp} {message}\n"
        print(message)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_msg)

    def send_prompt(self, prompt: str) -> str:
        """Claudeにプロンプトを送信"""
        self.debug(f"プロンプト文字数: {len(prompt)}")
        self.log("=" * 70)
        self.log("📤 Claude に送信中...")
        self.log("=" * 70)

        # プロンプトの最初と最後を表示
        preview = prompt[:300] + "\n...\n" + prompt[-300:] if len(prompt) > 600 else prompt
        self.log(f"プロンプトプレビュー:\n{preview}")

        try:
            self.debug("Anthropic API呼び出し開始")
            message = self.client.messages.create(
                model=self.model, max_tokens=2000, messages=[{"role": "user", "content": prompt}]
            )
            self.debug("Anthropic API呼び出し成功")

            response = message.content[0].text
            self.debug(f"応答文字数: {len(response)}")

            self.log("")
            self.log("=" * 70)
            self.log("📥 Claude からの応答:")
            self.log("=" * 70)
            self.log(response)
            self.log("=" * 70)

            return response

        except Exception as e:
            self.debug(f"APIエラー: {e}")
            self.log(f"❌ APIエラー: {e}")
            raise

    def run(self):
        """自動実行"""
        self.debug("=" * 70)
        self.debug("システム起動")
        self.debug(f"実行時刻: {datetime.now()}")
        self.debug(f"カレントディレクトリ: {os.getcwd()}")

        self.log("\n" + "🤖 Claude自動対話システム 開始".center(70, "="))

        # 1. カスタム指示をチェック
        custom_instruction_file = Path("CUSTOM_INSTRUCTION.txt")
        custom_instruction = ""

        self.debug(f"カスタム指示ファイル確認: {custom_instruction_file.absolute()}")

        if custom_instruction_file.exists():
            custom_instruction = custom_instruction_file.read_text(encoding="utf-8")
            self.debug(f"カスタム指示を読み込み: {len(custom_instruction)}文字")
            self.log("")
            self.log("=" * 70)
            self.log("�� カスタム指示を検出:")
            self.log("=" * 70)
            self.log(custom_instruction)
            self.log("=" * 70)

            # ファイルを削除
            custom_instruction_file.unlink()
            self.debug("カスタム指示ファイルを削除")
        else:
            self.debug("カスタム指示ファイルなし")

        # 2. 最新のプロンプトを取得
        prompts = sorted(Path(".").glob("claude_prompt_*.txt"))
        self.debug(f"プロンプトファイル数: {len(prompts)}")

        if not prompts:
            self.log("❌ プロンプトファイルが見つかりません")
            self.debug("プロンプトファイルが見つからないため終了")
            return

        latest_prompt = prompts[-1]
        self.debug(f"最新プロンプト: {latest_prompt}")
        self.log(f"\n📋 プロンプトファイル: {latest_prompt}")

        prompt_text = latest_prompt.read_text(encoding="utf-8")
        self.debug(f"プロンプト読み込み: {len(prompt_text)}文字")

        # カスタム指示を追加
        if custom_instruction:
            original_length = len(prompt_text)
            prompt_text += f"\n\n{'='*70}\n【🎯 追加の重要な指示】\n{'='*70}\n{custom_instruction}\n{'='*70}\n"
            self.debug(f"カスタム指示追加: {original_length} → {len(prompt_text)}文字")
            self.log(f"\n✅ カスタム指示を追加しました")

        # 3. Claudeに送信
        self.debug("Claude API送信開始")
        response = self.send_prompt(prompt_text)
        self.debug("Claude API送信完了")

        # 4. 応答を保存
        response_file = f"claude_response_{datetime.now().strftime('%H%M%S')}.txt"
        Path(response_file).write_text(response, encoding="utf-8")
        self.log(f"\n💾 応答を保存: {response_file}")
        self.debug(f"応答ファイル作成: {response_file}")

        # 5. コマンドを抽出
        import re

        commands = []
        for match in re.finditer(r"```bash\n(.*?)```", response, re.DOTALL):
            for line in match.group(1).split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    commands.append(line)

        self.debug(f"コマンド抽出: {len(commands)}個")

        if commands:
            self.log(f"\n🔍 {len(commands)}個のコマンドを検出")
            for i, cmd in enumerate(commands, 1):
                self.log(f"  {i}. {cmd}")

            # 自動実行（Webからの場合）
            if not sys.stdin.isatty():
                self.log("\n⚙️ 自動実行モード")
                self.debug("自動実行モード開始")

                import subprocess

                self.log("\n" + "=" * 70)
                self.log("⚙️ コマンド実行開始")
                self.log("=" * 70)

                for i, cmd in enumerate(commands, 1):
                    self.log(f"\n[{i}/{len(commands)}] $ {cmd}")
                    self.debug(f"コマンド実行: {cmd}")

                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                    if result.stdout:
                        output = result.stdout[:500]
                        self.log(f"出力:\n{output}")
                        if len(result.stdout) > 500:
                            self.log("...(省略)...")

                    if result.returncode != 0:
                        self.log(f"⚠️ エラー: {result.stderr[:200]}")
                        self.debug(f"コマンドエラー: {result.returncode}")
                    else:
                        self.log("✅ 成功")
                        self.debug("コマンド成功")

                self.log("\n" + "=" * 70)
                self.log("✅ すべてのコマンド実行完了")
                self.log("=" * 70)
            else:
                # ターミナルから実行の場合は確認
                confirm = input("\n実行しますか？ (y/n): ")
                if confirm.lower() == "y":
                    # 同じ実行ロジック
                    pass
        else:
            self.log("\n📝 実行可能なコマンドはありませんでした")
            self.debug("コマンドなし")

        self.log("\n" + "🏁 Claude自動対話システム 終了".center(70, "=") + "\n")
        self.debug("システム終了")


if __name__ == "__main__":
    print("🐛 デバッグモードで起動")
    system = AutoClaudeSystemDebug()
    system.run()
    print("\n📋 デバッグログ: logs/debug.log")
