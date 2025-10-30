#!/usr/bin/env python3
"""
データ統合パイプライン実行スクリプト

全てのログソースからナレッジを抽出し、
knowledge_baseに統合する
"""

import sys
import os
import yaml
from pathlib import Path

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from dotenv import load_dotenv
load_dotenv('.env')

from tools.data_integration.pipeline import DataIntegrationPipeline
from tools.sheets_manager import GoogleSheetsManager

def load_config() -> dict:
    """設定ファイル読み込み"""
    
    config_path = Path('/workspaces/gemini_AI_Agent/config/data_integration.yaml')
    
    if not config_path.exists():
        print(f"❌ 設定ファイルが見つかりません: {config_path}")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    """メイン処理"""
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 データ統合パイプライン")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    
    # 設定読み込み
    print("⚙️  設定ファイル読み込み中...")
    config = load_config()
    print("   ✅ 読み込み完了")
    print()
    
    # Google Sheets接続
    print("📊 Google Sheets接続中...")
    sheets = GoogleSheetsManager(
        spreadsheet_id=os.getenv("SPREADSHEET_ID"),
        service_account_file="configuration/service_account.json"
    )
    print("   ✅ 接続完了")
    print()
    
    # パイプライン実行
    pipeline = DataIntegrationPipeline(config, sheets)
    metrics = pipeline.run()
    
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎉 完了！")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print(f"処理件数: {metrics.total_entries}件")
    print(f"抽出パターン: {sum(metrics.patterns_extracted.values())}件")
    print(f"実行時間: {metrics.execution_time:.2f}秒")
    print()
    print("スプレッドシートを確認してください:")
    print(f"https://docs.google.com/spreadsheets/d/{os.getenv('SPREADSHEET_ID')}")

if __name__ == "__main__":
    main()
