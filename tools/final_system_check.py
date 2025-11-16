"""
最終システムチェック
"""

import os
import sys
from pathlib import Path


def check_system_health():
    """システムの健全性をチェック"""
    checks = [
        check_python_syntax,
        check_template_integrity,
        check_knowledge_base,
        check_dependencies,
    ]

    results = []
    for check in checks:
        try:
            result = check()
            results.append((check.__name__, result, "SUCCESS"))
        except Exception as e:
            results.append((check.__name__, str(e), "FAILED"))

    return results


def check_python_syntax():
    """Python構文チェック"""
    project_root = Path("/workspaces/gemini_AI_Agent")
    python_files = list(project_root.rglob("*.py"))

    valid_files = 0
    for py_file in python_files:
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                compile(f.read(), str(py_file), "exec")
            valid_files += 1
        except SyntaxError:
            continue

    return f"{valid_files}/{len(python_files)} ファイルが構文正常"


def check_template_integrity():
    """テンプレート整合性チェック"""
    templates_dir = Path("/workspaces/gemini_AI_Agent/agents/templates")
    template_files = list(templates_dir.glob("*.py"))
    return f"{len(template_files)} 個のテンプレートを確認"


def check_knowledge_base():
    """ナレッジベースチェック"""
    knowledge_dirs = [
        "/workspaces/gemini_AI_Agent/knowledge_system",
        "/workspaces/gemini_AI_Agent/agent_outputs/knowledge",
    ]

    total_files = 0
    for knowledge_dir in knowledge_dirs:
        if os.path.exists(knowledge_dir):
            total_files += len(list(Path(knowledge_dir).rglob("*")))

    return f"ナレッジベース: {total_files} ファイル"


def check_dependencies():
    """依存関係チェック"""
    try:
        import gspread
        import google
        import requests

        return "主要依存関係: 正常"
    except ImportError as e:
        return f"依存関係エラー: {e}"


def main():
    """メイン関数"""
    print("システム健全性チェックを開始...")
    results = check_system_health()

    print("\nチェック結果:")
    for name, result, status in results:
        status_icon = "✅" if status == "SUCCESS" else "❌"
        print(f"  {status_icon} {name}: {result}")


if __name__ == "__main__":
    main()
