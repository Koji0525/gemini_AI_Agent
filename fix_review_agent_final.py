#!/usr/bin/env python3
"""ReviewAgent.__init__から古いコード（26-27行目）を削除"""

from pathlib import Path

def fix_review_agent_final():
    print("🔧 ReviewAgent最終修正")
    print("=" * 70)
    
    file_path = Path("core_agents/review_agent.py")
    
    # 読み込み
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # バックアップ
    backup_path = Path("core_agents/review_agent.py.backup_final")
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"✅ バックアップ: {backup_path}")
    
    # 修正: __init__内の古いコードを削除
    new_lines = []
    in_init = False
    skip_next_lines = 0
    
    for i, line in enumerate(lines):
        # __init__の開始を検出
        if 'def __init__(self, browser_controller' in line:
            in_init = True
            new_lines.append(line)
            continue
        
        # __init__内で問題のコードを検出
        if in_init:
            # 次のdefまたはclassで__init__終了
            if (line.strip().startswith('def ') and '__init__' not in line) or \
               (line.strip().startswith('class ')):
                in_init = False
            
            # 削除すべき行をスキップ
            if '"""コンストラクタ - 後でプロパティを設定する"""' in line:
                print(f"❌ 削除: {i+1}行目: {line.strip()}")
                continue
            
            if in_init and 'self.browser = None' in line and i > 20:  # 26行目付近
                print(f"❌ 削除: {i+1}行目: {line.strip()}")
                continue
            
            if in_init and 'self.sheets_manager = None' in line and i > 20:  # 27行目付近
                print(f"❌ 削除: {i+1}行目: {line.strip()}")
                continue
        
        new_lines.append(line)
    
    # 保存
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ ReviewAgent修正完了")
    print()
    print("修正内容:")
    print("  - 26行目: self.browser = None を削除")
    print("  - 27行目: self.sheets_manager = None を削除")
    print("  - 25行目: 古いコメントを削除")
    print()
    print("=" * 70)

if __name__ == "__main__":
    fix_review_agent_final()
