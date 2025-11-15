#!/usr/bin/env python3
"""
complete_engine_ultimate.py の409行目構文エラー修正
"""

# ファイル読み込み
with open("agents/complete_engine_ultimate.py", "r", encoding="utf-8") as f:
    content = f.read()

# 409行目付近の問題を修正
# 未終了の文字列リテラルを修正
old_line = '    output = "タスク実行完了: " + task_id + "'
new_line = '    output = "タスク実行完了: " + task_id'

# 置換実行
if old_line in content:
    content = content.replace(old_line, new_line)
    print("✅ 409行目を修正しました")
else:
    print("⚠️ 409行目のパターンが見つかりませんでした。現在の状態を確認:")
    lines = content.split("\n")
    for i in range(405, 415):
        if i < len(lines):
            print(f"{i+1}: {lines[i]}")

# 修正内容を保存
with open("agents/complete_engine_ultimate.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 構文エラー修正完了")

# 構文チェック
import subprocess

result = subprocess.run(
    ["python3", "-m", "py_compile", "agents/complete_engine_ultimate.py"],
    capture_output=True,
    text=True,
)
if result.returncode == 0:
    print("✅ 構文チェック合格")
else:
    print("❌ 構文チェック不合格")
    print("エラー詳細:")
    print(result.stderr)
