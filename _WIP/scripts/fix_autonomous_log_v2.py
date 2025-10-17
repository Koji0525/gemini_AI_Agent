#!/usr/bin/env python3
"""autonomous_system.py のログを確実に修正"""
from pathlib import Path

file = Path('autonomous_system.py')
content = file.read_text()

# 現在の log メソッドの場所を特定
import re
log_method_match = re.search(r'def log\(self, message, level="INFO"\):.*?(?=\n    def |\nclass |\Z)', content, re.DOTALL)

if log_method_match:
    old_method = log_method_match.group(0)
    
    new_method = '''def log(self, message, level="INFO"):
        """ログ出力（簡潔版・タイムスタンプ30回に1回）"""
        # カウンター初期化
        if not hasattr(self, '_log_count'):
            self._log_count = 0
            self._last_timestamp = 0
        
        self._log_count += 1
        
        # 30回に1回タイムスタンプ表示
        import time
        current_time = time.time()
        show_timestamp = (
            self._log_count % 30 == 1 or
            current_time - self._last_timestamp > 600  # 10分経過
        )
        
        if show_timestamp:
            from datetime import datetime
            timestamp = datetime.now().strftime('[%H:%M]')
            self._last_timestamp = current_time
            print(f"{timestamp} {message}")
        else:
            print(message)
        
        # ログファイルには完全な情報を記録
        if hasattr(self, 'log_file'):
            from datetime import datetime
            timestamp_full = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"{timestamp_full} [{level}] {message}\\n")'''
    
    content = content.replace(old_method, new_method)
    file.write_text(content)
    print("✅ autonomous_system.py のログメソッドを修正")
else:
    print("⚠️ log メソッドが見つかりません")
