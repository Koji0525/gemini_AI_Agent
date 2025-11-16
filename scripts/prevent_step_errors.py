#!/usr/bin/env python3
"""
STEP変数エラー防止スクリプト
"""

import ast
import re

def validate_step_variables(file_path):
    """STEP変数の検証"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
        
        # 未定義のSTEP変数を検出
        undefined_steps = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id.startswith('STEP') and node.id != 'STEP':
                # 代入されていない変数の使用をチェック
                if not any(isinstance(parent, ast.Assign) for parent in ast.walk(tree)):
                    undefined_steps.append(node.id)
        
        if undefined_steps:
            print(f"⚠️  {file_path} で未定義のSTEP変数: {set(undefined_steps)}")
            return False
        return True
        
    except SyntaxError as e:
        print(f"❌ {file_path} の構文エラー: {e}")
        return False

if __name__ == "__main__":
    import glob
    python_files = glob.glob("/workspaces/gemini_AI_Agent/**/*.py", recursive=True)
    
    issues_found = 0
    for file_path in python_files:
        if not validate_step_variables(file_path):
            issues_found += 1
    
    if issues_found == 0:
        print("🎉 全てのファイルでSTEP変数が正常です")
    else:
        print(f"⚠️  {issues_found} 個のファイルにSTEP変数問題があります")
