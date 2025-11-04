#!/bin/env python3
import re
import shutil
from datetime import datetime

def safe_fix_fullwidth_chars(filename):
    """全角文字を安全に修正"""
    
    # バックアップ作成
    backup_name = f"{filename}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filename, backup_name)
    print(f"✅ バックアップ作成: {backup_name}")
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 全角文字の検出
    fullwidth_pattern = re.compile(r'[（）「」【】]')
    matches = list(fullwidth_pattern.finditer(content))
    
    if not matches:
        print("✅ 全角文字は見つかりませんでした")
        return True
    
    print(f"🔍 全角文字を {len(matches)} 個発見:")
    
    # 問題箇所を表示
    for i, match in enumerate(matches[:5]):  # 最初の5つだけ表示
        start = max(0, match.start() - 20)
        end = min(len(content), match.end() + 20)
        context = content[start:end].replace('\n', ' ')
        print(f"   {i+1}. 位置 {match.start()}: ...{context}...")
    
    if len(matches) > 5:
        print(f"   ... 他 {len(matches) - 5} 個")
    
    # 安全な置換
    replacement_map = {
        '（': '(',  # 全角括弧 → 半角括弧
        '）': ')',  # 全角括弧 → 半角括弧  
        '「': '"',  # 全角鉤括弧 → 半角引用符
        '」': '"',  # 全角鉤括弧 → 半角引用符
        '【': '[',  # 全角角括弧 → 半角角括弧
        '】': ']'   # 全角角括弧 → 半角角括弧
    }
    
    fixed_content = content
    for fullwidth, halfwidth in replacement_map.items():
        fixed_content = fixed_content.replace(fullwidth, halfwidth)
    
    # 修正内容を保存
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("✅ 全角文字を半角文字に置換しました")
    
    # 構文チェック
    import subprocess
    result = subprocess.run(['python3', '-m', 'py_compile', filename], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("🎉 構文チェック合格！")
        return True
    else:
        print("❌ 構文チェック失敗 - バックアップから復元します")
        print(f"エラー内容: {result.stderr}")
        # バックアップから復元
        shutil.copy2(backup_name, filename)
        return False

# メイン実行
if __name__ == "__main__":
    target_file = "tools/sheets_manager.py"
    print(f"🔧 {target_file} の全角文字を修正します...")
    
    if safe_fix_fullwidth_chars(target_file):
        print("🎯 修正完了！")
    else:
        print("💥 修正に失敗しました - 手動での修正が必要です")
