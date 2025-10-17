#!/usr/bin/env python3
"""task_executor.pyにPathインポートを追加"""

from pathlib import Path as PathLib

def fix_path_import():
    print("🔧 Pathインポート追加")
    print("=" * 70)
    
    file_path = PathLib("scripts/task_executor.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # バックアップ
    backup_path = PathLib("scripts/task_executor.py.backup_path_import")
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"✅ バックアップ: {backup_path}")
    
    # Pathがインポートされているか確認
    has_path_import = False
    for line in lines:
        if 'from pathlib import Path' in line:
            has_path_import = True
            print("✅ Pathは既にインポート済み")
            break
    
    if not has_path_import:
        # import文を探して追加
        import_section_end = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_section_end = i + 1
            elif import_section_end > 0 and line.strip() == '':
                break
        
        # Pathインポートを追加
        new_import = 'from pathlib import Path\n'
        lines.insert(import_section_end, new_import)
        
        # 保存
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"✅ Pathインポートを追加しました（{import_section_end + 1}行目）")
    
    print("=" * 70)
    return True

if __name__ == "__main__":
    fix_path_import()
