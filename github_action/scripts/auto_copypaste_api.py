#!/usr/bin/env python3
"""
GitHub Actions用 自動コピペシステム
Gemini API + GitHub Codespaces API使用
"""
import os
import sys
import time
import json
import re
import subprocess
from datetime import datetime
from typing import List, Dict, Optional

try:
    import google.generativeai as genai
    import requests
except ImportError:
    print("❌ 必要なパッケージがインストールされていません")
    print("pip install google-generativeai requests")
    sys.exit(1)


class AutoCopyPasteBot:
    """GitHub Actions用自動コピペロボット"""

    def __init__(self):
        # 環境変数から設定を取得
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.github_pat = os.getenv("GITHUB_PAT")
        self.codespace_name = os.getenv("CODESPACE_NAME")
        self.task = os.getenv("TASK", "プロジェクトの状態を確認してください")
        self.max_iterations = int(os.getenv("MAX_ITERATIONS", "5"))

        # バリデーション
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY が設定されていません")
        if not self.github_pat:
            raise ValueError("GITHUB_PAT が設定されていません")
        if not self.codespace_name:
            raise ValueError("CODESPACE_NAME が設定されていません")

        # Gemini設定
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel("gemini-pro")

        # ログファイル
        self.log_file = "execution.log"

        print("=" * 60)
        print("🤖 自動コピペロボット初期化完了")
        print(f"📝 タスク: {self.task[:80]}...")
        print(f"🔄 最大反復: {self.max_iterations}回")
        print(f"💻 Codespace: {self.codespace_name}")
        print("=" * 60)

    def log(self, message: str):
        """ログ出力"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {message}"
        print(log_line)

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")

    def send_to_gemini(self, message: str) -> str:
        """Gemini APIでメッセージを送信"""
        self.log(f"📤 Geminiに送信: {message[:100]}...")

        try:
            response = self.model.generate_content(message)
            text = response.text

            self.log(f"✅ Gemini応答: {len(text)}文字")
            return text

        except Exception as e:
            self.log(f"❌ Gemini APIエラー: {e}")
            return f"エラー: {e}"

    def execute_in_codespace(self, command: str) -> Dict[str, str]:
        """GitHub Codespaces APIでコマンド実行"""
        self.log(f"💻 Codespacesで実行: {command}")

        try:
            # GitHub CLIを使用
            result = subprocess.run(
                ["gh", "codespace", "ssh", "-c", self.codespace_name, "--", command],
                capture_output=True,
                text=True,
                timeout=120,
                env={**os.environ, "GH_TOKEN": self.github_pat},
            )

            output = {
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
            }

            if output["success"]:
                self.log(f"✅ 実行成功: {len(output['stdout'])}文字出力")
            else:
                self.log(f"⚠️ 実行エラー（終了コード: {result.returncode}）")

            return output

        except subprocess.TimeoutExpired:
            self.log("⏱️ タイムアウト（120秒）")
            return {
                "command": command,
                "returncode": -1,
                "stdout": "",
                "stderr": "Timeout after 120 seconds",
                "success": False,
            }
        except Exception as e:
            self.log(f"❌ 実行エラー: {e}")
            return {"command": command, "returncode": -1, "stdout": "", "stderr": str(e), "success": False}

    def extract_commands(self, text: str) -> List[str]:
        """テキストからbashコマンドを抽出"""
        commands = []

        # ```bash または ```sh ブロックを検索
        patterns = [
            r"```bash\n(.*?)```",
            r"```sh\n(.*?)```",
            r"```shell\n(.*?)```",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                # 各行を処理
                for line in match.strip().split("\n"):
                    line = line.strip()
                    # コメントと空行をスキップ
                    if line and not line.startswith("#"):
                        commands.append(line)

        return commands

    def is_completed(self, text: str) -> bool:
        """完了判定"""
        completion_keywords = [
            "完了",
            "すべて完了",
            "タスク完了",
            "以上で完了",
            "問題なし",
            "全て完了",
            "completed",
            "all done",
            "finished",
        ]

        text_lower = text.lower()
        return any(keyword in text_lower for keyword in completion_keywords)

    def run(self):
        """メインループ実行"""
        self.log("\n" + "=" * 60)
        self.log("🔄 自動コピペループ開始")
        self.log("=" * 60)

        current_message = f"""
{self.task}

各ステップを ```bash ブロックで提示してください。
コマンドは1行ずつ明確に記述してください。
完了したら「完了」と明記してください。
"""

        results_summary = []

        for iteration in range(1, self.max_iterations + 1):
            self.log(f"\n{'='*60}")
            self.log(f"🔁 反復 {iteration}/{self.max_iterations}")
            self.log(f"{'='*60}")

            # 1. Geminiに送信
            gemini_response = self.send_to_gemini(current_message)

            # 完了判定
            if self.is_completed(gemini_response):
                self.log("✅ タスク完了を検出")
                results_summary.append(f"\n【反復{iteration}】タスク完了\n{gemini_response}")
                break

            # 2. コマンド抽出
            commands = self.extract_commands(gemini_response)

            if not commands:
                self.log("ℹ️ コマンドが見つかりません")
                self.log(f"Gemini応答:\n{gemini_response[:500]}")

                current_message = """
前回の回答にbashコマンドがありませんでした。
次のステップを ```bash ブロックで明確に提示してください。
完了している場合は「完了」と答えてください。
"""
                continue

            self.log(f"📋 抽出されたコマンド: {len(commands)}個")
            for idx, cmd in enumerate(commands, 1):
                self.log(f"  {idx}. {cmd}")

            # 3. Codespacesで実行
            execution_results = []
            for cmd in commands:
                result = self.execute_in_codespace(cmd)

                # 結果をフォーマット
                result_text = f"""
コマンド: {result['command']}
終了コード: {result['returncode']}
成功: {'✅ はい' if result['success'] else '❌ いいえ'}

標準出力:
{result['stdout'][:1000]}

標準エラー:
{result['stderr'][:500]}
"""
                execution_results.append(result_text)

                # 少し待機
                time.sleep(1)

            # 4. 結果をGeminiに返す
            all_results = "\n\n---\n\n".join(execution_results)
            results_summary.append(f"\n【反復{iteration}】\nコマンド実行結果:\n{all_results}")

            current_message = f"""
前回のコマンド実行結果:

{all_results}

上記の結果を確認して:
- エラーがあれば修正方法を ```bash で提示
- 次のステップがあれば ```bash で提示
- すべて完了していれば「完了」と答えてください
"""

        # 最終結果を保存
        self.save_results(results_summary)

        self.log("\n" + "=" * 60)
        self.log("🎉 自動コピペループ完了")
        self.log(f"📝 ログ: {self.log_file}")
        self.log("=" * 60)

    def save_results(self, results: List[str]):
        """結果をファイルに保存"""
        with open("results.txt", "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("🤖 自動コピペシステム 実行結果\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"タスク: {self.task}\n")
            f.write(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n" + "=" * 60 + "\n\n")
            f.write("\n".join(results))

        self.log("💾 結果を results.txt に保存しました")


def main():
    """メイン処理"""
    try:
        bot = AutoCopyPasteBot()
        bot.run()

    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによる中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 致命的なエラー: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
