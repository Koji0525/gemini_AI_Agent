#!/usr/bin/env python3
"""autonomous_system.py の log メソッドを修正"""
from pathlib import Path

file = Path('autonomous_system.py')
content = file.read_text()

# 現在の log メソッドを確認
old_log = '''    def log(self, message, level="INFO"):
        """ログ出力"""
        timestamp = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
        level_str = f"[{level}]"
        log_message = f"{timestamp} {level_str} {message}"
        print(log_message)
        
        # ログファイルにも出力
        if hasattr(self, 'log_file'):
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + '\n')'''

new_log = '''    def log(self, message, level="INFO"):
        """ログ出力（簡潔版）"""
        # メッセージカウンター
        if not hasattr(self, '_log_count'):
            self._log_count = 0
            self._last_timestamp = 0
        
        self._log_count += 1
        import time
        current_time = time.time()
        
        # 50回に1回、または5分経過でタイムスタンプ表示
        show_timestamp = (
            self._log_count % 50 == 1 or
            current_time - self._last_timestamp > 300
        )
        
        if show_timestamp:
            timestamp = datetime.now().strftime('[%H:%M]')
            self._last_timestamp = current_time
            print(f"{timestamp} {message}")
        else:
            print(message)
        
        # ログファイルには常に完全な情報を記録
        if hasattr(self, 'log_file'):
            timestamp_full = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"{timestamp_full} [{level}] {message}\n")'''

if old_log in content:
    content = content.replace(old_log, new_log)
    file.write_text(content)
    print("✅ log メソッドを簡潔版に変更")
else:
    print("⚠️ 既に変更済みまたは該当箇所が異なります")
