import ast
import sys
import re
import os

def validate_python_syntax(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source)
        return True, "✅ 構文チェック合格"
    except SyntaxError as e:
        return False, f"❌ 構文エラー: {e}"

def check_for_regex_artifacts(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    regex_patterns = [r'\\[1-9]', r'\(\?P<[^>]+>', r'\\[dws]']
    issues = []
    
    for pattern in regex_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            line_num = content[:match.start()].count(chr(10)) + 1
            issues.append(f"行 {line_num}: {match.group()}")
    
    return issues

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "/workspaces/gemini_AI_Agent"
    
    if os.path.isfile(target) and target.endswith('.py'):
        valid, msg = validate_python_syntax(target)
        print(f"{target}: {msg}")
        issues = check_for_regex_artifacts(target)
        if issues:
            print("⚠️ 正規表現の残骸を検出:")
            for issue in issues: print(f"  - {issue}")
    else:
        for root, dirs, files in os.walk(target):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    valid, msg = validate_python_syntax(full_path)
                    status = "✅" if valid else "❌"
                    print(f"{status} {full_path}")
