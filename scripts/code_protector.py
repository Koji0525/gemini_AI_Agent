
#!/usr/bin/env python3
import os
import ast
import re

def validate_before_save(file_path, content):
    """保存前の検証"""
    # 禁止パターン
    banned_patterns = [
        (r'def \\[0-9]', "正規表現後方参照"),
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
