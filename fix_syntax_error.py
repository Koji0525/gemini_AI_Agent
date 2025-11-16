#!/usr/bin/env python3
"""
構文エラー修正スクリプト
"""


def fix_complete_engine_ultimate():
    """complete_engine_ultimate.pyの構文エラーを修正"""
    file_path = "/workspaces/gemini_AI_Agent/agents/complete_engine_ultimate.py"

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 96行目付近の問題を修正
    fixed_lines = []
    for i, line in enumerate(lines, 1):
        if i == 96 and "def (self):" in line:
            print("🔧 96行目の構文エラーを修正します...")
            # 不正な行を削除（前のメソッド定義が完了しているはず）
            continue
        elif "def integrate_knowledge_system(self):" in line and "def (self):" not in line:
            # 正しいメソッド定義を確認
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    # 修正内容を保存
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(fixed_lines)

    print("✅ 構文エラーを修正しました")


def verify_fix():
    """修正を検証"""
    file_path = "/workspaces/gemini_AI_Agent/agents/complete_engine_ultimate.py"

    # 構文チェック
    import subprocess

    result = subprocess.run(
        ["python", "-m", "py_compile", file_path], capture_output=True, text=True
    )

    if result.returncode == 0:
        print("✅ 構文チェック合格")
        return True
    else:
        print("❌ 構文エラーが残っています:")
        print(result.stderr)
        return False


if __name__ == "__main__":
    print("🔧 構文エラー修正を開始...")
    fix_complete_engine_ultimate()

    if verify_fix():
        print("🎉 修正完了！")
    else:
        print("⚠️ 修正が必要です")
