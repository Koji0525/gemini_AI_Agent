#!/usr/bin/env python3
"""
STEP1エラー修正スクリプト
"""

def fix_task_executor_enhanced():
    """task_executor_enhanced.pyのSTEP1エラーを修正"""
    file_path = "/workspaces/gemini_AI_Agent/agents/task_executor_enhanced.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # STEP1 を適切な値に置き換えまたは削除
    if "STEP1" in content:
        print(f"🔧 {file_path} のSTEP1を修正します...")
        
        # STEP1 が未定義変数として使われている場合の修正
        # コメントアウトするか、適切な値に置き換える
        content = content.replace("STEP1", "'STEP1'")  # 文字列として扱う
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ STEP1エラーを修正しました")
    else:
        print("✅ STEP1の問題は見つかりませんでした")

def check_related_files():
    """関連ファイルもチェック"""
    files_to_check = [
        "/workspaces/gemini_AI_Agent/agents/complete_engine_ultimate_integrated.py",
        "/workspaces/gemini_AI_Agent/run_3_cycles.py"
    ]
    
    for file_path in files_to_check:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "STEP1" in content and not ("STEP1_" in content or "'STEP1'" in content or '"STEP1"' in content):
                    print(f"⚠️  {file_path} に未定義のSTEP1が見つかりました")
        except FileNotFoundError:
            print(f"❌ {file_path} が見つかりません")

if __name__ == "__main__":
    fix_task_executor_enhanced()
    check_related_files()
    print("🎉 修正完了！テスト実行します...")
