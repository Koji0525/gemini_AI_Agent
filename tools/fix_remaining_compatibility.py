"""
残りのAPI互換性問題を修正
"""

import os
import re


def fix_file(file_path):
    """単一ファイルを修正"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 置換パターン
        replacements = {
            r"self\.sheets_manager\.append_row\(": "self.sheets_manager.append_rows(",
            r"sheets_manager\.append_row\(": "sheets_manager.append_rows(",
        }

        original_content = content
        for pattern, replacement in replacements.items():
            content = re.sub(pattern, replacement, content)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ 修正完了: {file_path}")
            return True
        else:
            print(f"ℹ️  変更なし: {file_path}")
            return False
    except Exception as e:
        print(f"❌ エラー: {file_path} - {e}")
        return False


# 修正対象ファイル
files_to_fix = ["agent_registry.py", "setup_agent_registry.py", "pm_tasks_loader_enhanced.py"]

fixed_count = 0
for file_path in files_to_fix:
    if os.path.exists(file_path):
        if fix_file(file_path):
            fixed_count += 1
    else:
        print(f"⚠️  ファイルが見つかりません: {file_path}")

print(f"🎉 残りのAPI互換性問題の修正完了: {fixed_count}/{len(files_to_fix)}件")
