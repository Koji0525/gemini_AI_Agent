#!/usr/bin/env python3
import os
import subprocess
import sys

def final_syntax_check():
    """最終構文チェック"""
    print("🔍 最終構文チェックを実行...")
    result = subprocess.run(
        ["find", "/workspaces/gemini_AI_Agent", "-name", "*.py", "-exec", 
         "python", "-m", "py_compile", "{}", ";"],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        print("🎉 全Pythonファイルの構文チェック合格！")
        return True
    else:
        print("❌ 構文エラーが検出されました:")
        print(result.stderr)
        return False

def create_protection_system():
    """恒久保護システムの作成"""
    protection_script = '''
#!/usr/bin/env python3
import os
import ast
import re

def validate_before_save(file_path, content):
    """保存前の検証"""
    # 禁止パターン
    banned_patterns = [
        (r'def \\\\[0-9]', "正規表現後方参照"),
        (r'[🤖🚀🔍📊📋✅❌⚠️🔧🎯🎉]', "絵文字"),
        (r'""".*?""",', "三重引用符後のカンマ"),
        (r'from, import,', "不正なimport構文"),
    ]
    
    for pattern, description in banned_patterns:
        if re.search(pattern, content):
            return False, f"禁止パターン検出: {description}"
    
    # 構文チェック
    try:
        ast.parse(content)
        return True, "有効なPythonコード"
    except SyntaxError as e:
        return False, f"構文エラー: {e}"
    
    return True, "OK"

if __name__ == "__main__":
    # テスト実行
    test_code = "print('Hello World')"
    valid, msg = validate_before_save("test.py", test_code)
    print(f"テスト: {msg}")
'''
    
    with open("/workspaces/gemini_AI_Agent/scripts/code_protector.py", "w", encoding="utf-8") as f:
        f.write(protection_script)
    print("🛡️ コード保護システムを設置")

def setup_git_hooks():
    """Gitフックの設定"""
    git_hook = '''#!/bin/bash
# pre-commit hook: コード検証

echo "🔍 コミット前チェック..."

# 変更されたPythonファイルをチェック
git diff --cached --name-only --diff-filter=ACM | grep '\.py$' | while read file; do
    if [ -f "$file" ]; then
        if ! python -m py_compile "$file"; then
            echo "❌ 構文エラー: $file"
            exit 1
        fi
        echo "✅ $file"
    fi
done

# コード保護システムの実行
python /workspaces/gemini_AI_Agent/scripts/code_protector.py

echo "🎉 コミット前チェック完了"
'''
    
    hook_path = "/workspaces/gemini_AI_Agent/.git/hooks/pre-commit"
    os.makedirs(os.path.dirname(hook_path), exist_ok=True)
    
    with open(hook_path, "w") as f:
        f.write(git_hook)
    
    # 実行権限付与
    os.chmod(hook_path, 0o755)
    print("🔧 Git pre-commit hookを設定")

def main():
    print("🚀 最終クリーンアップを開始...")
    
    # 構文チェック
    if not final_syntax_check():
        print("⚠️ 構文エラーが残っています。詳細を確認してください。")
        return
    
    # 保護システム設置
    create_protection_system()
    
    # Gitフック設定
    setup_git_hooks()
    
    # 最終システムテスト
    print("🔧 最終システムテスト...")
    os.chdir("/workspaces/gemini_AI_Agent")
    result = subprocess.run([sys.executable, "tools/startup_validator.py"], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("🎉 システムは完全に正常です！")
        print("📊 起動検証結果:")
        print(result.stdout)
    else:
        print("❌ システム検証で問題が発生しました:")
        print(result.stderr)

if __name__ == "__main__":
    main()
