#!/usr/bin/env python3
"""
setup_optimized_logging に return 文を追加
"""

with open('configuration/config_utils.py', 'r', encoding='utf-8') as f:
    content = f.read()

# logger.addHandler(file_handler) の後に return logger を追加
# ただし、既に return があれば追加しない
if 'def setup_optimized_logging(logger_name=None):' in content:
    # 関数内に return logger がなければ追加
    if 'logger.addHandler(file_handler)' in content and \
       'logger.addHandler(file_handler)\n    return logger' not in content:
        content = content.replace(
            '    logger.addHandler(file_handler)\n',
            '    logger.addHandler(file_handler)\n    return logger\n'
        )
        print("✅ return logger を追加しました")
    else:
        print("ℹ️  return logger は既に存在しています")

with open('configuration/config_utils.py', 'w', encoding='utf-8') as f:
    f.write(content)
