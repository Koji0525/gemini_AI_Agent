#!/usr/bin/env python3
from pathlib import Path

file = Path('configuration/config_utils.py')
content = file.read_text()

# タイムスタンプ表示頻度を変更: 30 → 50
content = content.replace(
    'SmartLogFormatter._message_count % 30 == 1',
    'SmartLogFormatter._message_count % 50 == 1'
)

# タイムスタンプ間隔も延長: 300秒(5分) → 600秒(10分)
content = content.replace(
    'current_time - SmartLogFormatter._last_timestamp_display > 300',
    'current_time - SmartLogFormatter._last_timestamp_display > 600'
)

file.write_text(content)
print("✅ ログ表示頻度を調整: 30回→50回, 5分→10分")
