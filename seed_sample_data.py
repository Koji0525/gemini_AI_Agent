#!/usr/bin/env python3
"""
🌱 サンプルデータ投入
目的: テスト用の目標とタスクを作成
"""

import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.sheets_manager import GoogleSheetsManager
from tools.safe_sheets_wrapper import SafeSheetsWrapper
import os
from datetime import datetime
from dotenv import load_dotenv

def seed_data():
    load_dotenv()
    
    sheets = GoogleSheetsManager()
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    sheets.open_spreadsheet(spreadsheet_id)
    
    safe_sheets = SafeSheetsWrapper(sheets)
    
    # サンプル目標
    sample_goals = [
        ["G001", "APIドキュメント自動生成機能の実装", "high", "pending", datetime.now().isoformat()],
        ["G002", "ログ分析ダッシュボードの作成", "medium", "pending", datetime.now().isoformat()],
        ["G003", "テストカバレッジを80%以上に向上", "high", "pending", datetime.now().isoformat()]
    ]
    
    # サンプルタスク
    sample_tasks = [
        ["T001", "G001", "API仕様書のMarkdown化", "developer", "pending", "high", "2h", "", datetime.now().isoformat(), ""],
        ["T002", "G001", "自動生成スクリプトの作成", "developer", "pending", "high", "3h", "T001", datetime.now().isoformat(), ""],
        ["T003", "G002", "Plotlyダッシュボードのプロトタイプ作成", "developer", "pending", "medium", "4h", "", datetime.now().isoformat(), ""]
    ]
    
    print("=" * 60)
    print("🌱 サンプルデータ投入")
    print("=" * 60)
    
    # 目標を投入
    if safe_sheets.safe_append('project_goal', sample_goals):
        print(f"✅ 目標: {len(sample_goals)}件追加")
    
    # タスクを投入
    if safe_sheets.safe_append('pm_tasks', sample_tasks):
        print(f"✅ タスク: {len(sample_tasks)}件追加")
    
    print("=" * 60)
    print("✅ サンプルデータ投入完了")
    print("\n📝 次のステップ:")
    print("  python3 test_orchestrator_5min.py")

if __name__ == '__main__':
    seed_data()
