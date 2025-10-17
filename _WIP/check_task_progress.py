#!/usr/bin/env python3
"""
タスク進捗確認スクリプト
"""
import sys
from google_sheets.sheets_manager import GoogleSheetsManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_progress():
    try:
        sheets = GoogleSheetsManager()
        logger.info("✅ Google Sheets接続成功")
        
        # タスク実行履歴を確認（実際のシート名に応じて変更）
        # sheets.get_data() などのメソッドがあれば使用
        logger.info("📊 タスク履歴を取得中...")
        
        # TODO: 実際のシート構造に応じて実装
        logger.info("💡 Google Sheetsの構造を確認してください")
        
    except Exception as e:
        logger.error(f"❌ エラー: {e}")

if __name__ == "__main__":
    check_progress()
