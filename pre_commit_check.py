#!/bin/env python3
import re
import subprocess
import sys

def check_for_fullwidth_chars(filename):
    """全角文字のチェック"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # コメントと文字列リテラルを除外して全角文字を検出
    lines = content.split('\n')
    issues = []
    
    for i, line in enumerate(lines, 1):
        # コード部分のみをチェック（コメントを除去）
        code_part = re.sub(r'#.*$', '', line)
        # 文字列リテラルを一時的にマスク
        code_part = re.sub(r'[\'\"].*?[\'\"]', '', code_part)
        
        fullwidth_matches = re.findall(r'[（）「」【】]', code_part)
        if fullwidth_matches:
            issues.append(f"行 {i}: 全角文字 {set(fullwidth_matches)} - {line.strip()}")
    
    return issues

def main():
    files_to_check = [
        "tools/sheets_manager.py",
        "autonomous_development_orchestrator.py",
        "core_agents/quality_feedback_loop_v02.py"
    ]
    
    has_errors = False
    
    for file in files_to_check:
        try:
            # 構文チェック
            result = subprocess.run(['python3', '-m', 'py_compile', file], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ {file}: 構文エラー")
                print(f"   {result.stderr.splitlines()[-1]}")
                has_errors = True
                continue
            
            # 全角文字チェック
            issues = check_for_fullwidth_chars(file)
            if issues:
                print(f"❌ {file}: 全角文字を検出")
                for issue in issues[:3]:  # 最初の3つだけ表示
                    print(f"   {issue}")
                if len(issues) > 3:
                    print(f"   ... 他 {len(issues) - 3} 個")
                has_errors = True
            else:
                print(f"✅ {file}: OK")
                
        except FileNotFoundError:
            print(f"⚠️  {file}: ファイルが見つかりません")
        except Exception as e:
            print(f"❌  {file}: チェック中にエラー - {e}")
            has_errors = True
    
    if has_errors:
        print("\n🔧 コミットを中止します。問題を修正してください。")
        sys.exit(1)
    else:
        print("\n🎉 すべてのチェックが合格しました！")

if __name__ == "__main__":
    main()
