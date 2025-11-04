# update_cellの呼び出し方を修正
import re

# QualityFeedbackLoopの修正
files_to_fix = [
    'core_agents/quality_feedback_loop_v02.py'
]

for file_path in files_to_fix:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # cell_address → cell_range に修正
        old_pattern = r"await self\.sheets\.update_cell\([^,]+,\s*cell_address=([^,]+),\s*value=([^)]+)\)"
        new_pattern = r"await self.sheets.update_cell(\1, \2)"
        
        # 非同期呼び出しの修正
        content = re.sub(
            r"await self\.sheets\.update_cell\(([^,]+),\s*cell_address=([^,]+),\s*value=([^)]+)\)",
            r"await self.sheets.update_cell(\1, \2, \3)",
            content
        )
        
        # 同期呼び出しの修正
        content = re.sub(
            r"self\.sheets\.update_cell\(([^,]+),\s*cell_address=([^,]+),\s*value=([^)]+)\)",
            r"self.sheets.update_cell(\1, \2, \3)",
            content
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ {file_path} のupdate_cell呼び出しを修正しました")
        
    except Exception as e:
        print(f"❌ {file_path} の修正に失敗: {e}")

print("🎯 update_cell呼び出しの修正完了")
