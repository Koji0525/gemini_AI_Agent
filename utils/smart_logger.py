#!/usr/bin/env python3
"""
SmartLogger - 簡潔なログ出力システム
30回に1回タイムスタンプを表示
"""
import logging
from datetime import datetime
from typing import Optional

class SmartLogFormatter(logging.Formatter):
    """SmartLog形式のフォーマッター"""
    
    def __init__(self):
        super().__init__()
        self._log_count = 0
        self._last_timestamp = 0
        self._last_date = None
        
        # レベル別絵文字
        self.level_emoji = {
            'DEBUG': '🔍',
            'INFO': '📋',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🚨'
        }
    
    def format(self, record):
        """ログレコードをフォーマット"""
        self._log_count += 1
        current_time = datetime.now()
        current_date = current_time.strftime('%Y-%m-%d')
        
        # タイムスタンプ表示判定
        show_timestamp = False
        
        # 条件1: 30回に1回
        if self._log_count % 30 == 1:
            show_timestamp = True
        
        # 条件2: 10分経過
        elif (current_time.timestamp() - self._last_timestamp) > 600:
            show_timestamp = True
        
        # 条件3: 日付変更
        elif self._last_date != current_date:
            show_timestamp = True
        
        # タイムスタンプ構築
        if show_timestamp:
            timestamp = current_time.strftime('🕒 %Y-%m-%d %H:%M')
            self._last_timestamp = current_time.timestamp()
            self._last_date = current_date
        else:
            timestamp = ''
        
        # レベル絵文字
        emoji = self.level_emoji.get(record.levelname, '📋')
        
        # メッセージ構築
        if timestamp:
            return f"{timestamp} {emoji} {record.name} 💬 {record.getMessage()}"
        else:
            return f"{emoji} {record.name} 💬 {record.getMessage()}"

def setup_smart_logging(level=logging.INFO):
    """SmartLogを設定"""
    # ルートロガー取得
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 既存のハンドラーをクリア
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # コンソールハンドラー（SmartLog形式）
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(SmartLogFormatter())
    root_logger.addHandler(console_handler)
    
    # ファイルハンドラー（完全なログ）
    try:
        import os
        os.makedirs('logs', exist_ok=True)
        
        file_handler = logging.FileHandler(
            'logs/autonomous_system.log',
            encoding='utf-8'
        )
        file_handler.setFormatter(
            logging.Formatter(
                '[%(asctime)s] %(levelname)s %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        )
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"⚠️  ファイルハンドラー設定失敗: {e}")
    
    return root_logger

class SmartLogger:
    """SmartLogger - シンプルなインターフェース"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def critical(self, message: str):
        self.logger.critical(message)
