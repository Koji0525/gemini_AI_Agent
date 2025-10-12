#!/usr/bin/env python3
"""自動修正の無限ループを防ぐ"""
from pathlib import Path

file = Path('autonomous_system.py')
content = file.read_text()

# __init__ に修正カウンターを追加
if 'self.fix_attempt_count = 0' not in content:
    content = content.replace(
        'self.auto_fix_enabled = auto_fix_enabled',
        'self.auto_fix_enabled = auto_fix_enabled\n        self.fix_attempt_count = 0\n        self.max_fix_attempts = 3'
    )
    
    # auto_fix メソッドに制限を追加
    content = content.replace(
        'def auto_fix(self, error_file):',
        'def auto_fix(self, error_file):\n        self.fix_attempt_count += 1\n        if self.fix_attempt_count > self.max_fix_attempts:\n            self.log(f"⚠️ 自動修正の上限（{self.max_fix_attempts}回）に到達。スキップします。", "WARN")\n            return False\n'
    )
    
    file.write_text(content)
    print("✅ 自動修正の無限ループ防止を追加")
else:
    print("ℹ️ 既に設定済み")
