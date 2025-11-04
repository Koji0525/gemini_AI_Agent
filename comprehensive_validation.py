#!/bin/env python3
import re
import sys

def validate_python_file(filename):
    """Pythonファイルの完全検証"""
    
    print(f"🔍 {filename} を検証中...")
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    issues = []
    
    # 1. 全角文字チェック
    fullwidth_chars = re.findall(r'[^\x00-\x7F]', content)
    if fullwidth_chars:
        # Pythonで許容される全角文字（コメント、文字列内）を除外
        allowed_fullwidth = re.findall(r'#.*?[^\x00-\x7F]|""".*?[^\x00-\x7F]|\'\'\'.*?[^\x00-\x7F]', content)
        problematic = [char for char in fullwidth_chars if char not in ''.join(allowed_fullwidth)]
        if problematic:
            issues.append(f"❌ 問題のある全角文字: {set(problematic)}")
    
    # 2. 構文チェック
    import subprocess
    result = subprocess.run(['python3', '-m', 'py_compile', filename], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        issues.append(f"❌ 構文エラー: {result.stderr.splitlines()[-1]}")
    
    # 3. 基本的なPython構造チェック
    try:
        with open(filename, 'r') as f:
            source = f.read()
        compile(source, filename, 'exec')
    except SyntaxError as e:
        issues.append(f"❌ コンパイルエラー: {e}")
    
    # 結果表示
    if not issues:
        print("✅ ファイルは正常です")
        return True
    else:
        print("❌ 検出された問題:")
        for issue in issues:
            print(f"   - {issue}")
        return False

def get_file_stats(filename):
    """ファイルの統計情報を表示"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📊 {filename} の統計:")
    print(f"   行数: {len(content.splitlines())}")
    print(f"   ファイルサイズ: {len(content)} バイト")
    print(f"   文字コード: UTF-8")
    
    # メソッド数をカウント
    methods = re.findall(r'def\s+(\w+)', content)
    print(f"   メソッド数: {len(methods)}")
    if methods:
        print(f"   メソッド一覧: {', '.join(methods[:10])}{'...' if len(methods) > 10 else ''}")

# メイン実行
if __name__ == "__main__":
    files_to_check = [
        "tools/sheets_manager.py",
        "autonomous_development_orchestrator.py", 
        "core_agents/quality_feedback_loop_v02.py"
    ]
    
    all_valid = True
    for file in files_to_check:
        try:
            get_file_stats(file)
            if not validate_python_file(file):
                all_valid = False
            print()
        except FileNotFoundError:
            print(f"⚠️  {file} は見つかりません\n")
        except Exception as e:
            print(f"❌  {file} の検証中にエラー: {e}\n")
            all_valid = False
    
    if all_valid:
        print("🎉 すべてのファイルが正常です！")
    else:
        print("🔧 問題のあるファイルがあります - 修正が必要です")
