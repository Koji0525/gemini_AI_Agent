#!/usr/bin/env python3
"""
修正版Progress Dashboard Updater - データ取得問題を解決
"""

import os
import sys
import asyncio
import gspread
from google.oauth2.service_account import Credentials

# 設定ローダーをインポート
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from configuration.config_loader import ConfigLoader

class FixedProgressUpdater:
    """データ取得問題を解決した進捗更新クラス"""
    
    def __init__(self):
        # 設定ローダーから設定を取得
        self.config = ConfigLoader()
        self.spreadsheet_id = self.config.get('spreadsheet_id')
        self.service_account_file = self.config.get('service_account_file')
        
        print("🔧 設定を使用:")
        print(f"   スプレッドシート: {self.spreadsheet_id}")
        print(f"   認証ファイル: {self.service_account_file}")
        
        # 直接gspreadを使用
        self.setup_gspread()
    
    def setup_gspread(self):
        """直接gspreadをセットアップ"""
        try:
            scopes = ['https://www.googleapis.com/auth/spreadsheets']
            credentials = Credentials.from_service_account_file(
                self.service_account_file, 
                scopes=scopes
            )
            self.gc = gspread.authorize(credentials)
            self.spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
            print("✅ 直接gspreadで接続成功")
        except Exception as e:
            print(f"❌ gspreadセットアップエラー: {e}")
            raise
    
    async def update_progress_dashboard(self):
        """進捗ダッシュボードを更新"""
        try:
            print("🚀 Progress Dashboard 更新開始...")
            
            # 1. project_goalからデータ取得（直接方法）
            goals_data = await self.load_sheet_data_direct('project_goal')
            if not goals_data:
                return
            
            # 2. Activeゴールを抽出
            active_goals = self.extract_active_goals(goals_data)
            print(f"🎯 {len(active_goals)}個のActiveゴールを検出")
            
            # 3. 進捗計算
            total_progress = self.calculate_total_progress(active_goals)
            print(f"📊 総合進捗: {total_progress}%")
            
            # 4. 結果表示
            self.display_results(active_goals, total_progress)
            
            print("✅ Progress Dashboard 更新完了")
            
        except Exception as e:
            print(f"❌ 更新エラー: {e}")
            import traceback
            traceback.print_exc()
    
    async def load_sheet_data_direct(self, sheet_name: str):
        """直接方法でシートデータを読み込み"""
        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
            
            # 複数の方法でデータ取得を試す
            print(f"📥 {sheet_name}からデータ取得中...")
            
            # 方法1: get_all_values
            all_values = worksheet.get_all_values()
            print(f"✅ get_all_values: {len(all_values)}行")
            
            if all_values and len(all_values) > 1:
                print(f"   ヘッダー: {all_values[0]}")
                print(f"   データ行: {len(all_values)-1}行")
                return all_values
            
            # 方法2: get_all_records
            try:
                all_records = worksheet.get_all_records()
                print(f"✅ get_all_records: {len(all_records)}件")
                if all_records:
                    # レコードを値のリストに変換
                    headers = list(all_records[0].keys())
                    values = [headers] + [list(record.values()) for record in all_records]
                    return values
            except Exception as e:
                print(f"⚠️ get_all_recordsエラー: {e}")
            
            print(f"❌ {sheet_name}: 有効なデータが見つかりません")
            return None
            
        except Exception as e:
            print(f"❌ {sheet_name}読み込みエラー: {e}")
            return None
    
    def extract_active_goals(self, data):
        """Activeなゴールを抽出"""
        if len(data) < 2:
            return []
        
        headers = data[0]
        active_goals = []
        
        print(f"🔍 ヘッダー分析: {headers}")
        
        # 列インデックスの検出
        status_idx = self.find_column_index(headers, ['status', 'ステータス'])
        title_idx = self.find_column_index(headers, ['goal_description', 'title', '説明', 'goal_id'])
        
        print(f"📊 検出された列: status={status_idx}, title={title_idx}")
        
        # Activeゴールの抽出
        for row_num, row in enumerate(data[1:], 2):
            if status_idx != -1 and len(row) > status_idx:
                status = str(row[status_idx]).lower().strip()
                if status == 'active':
                    # タイトルを取得
                    if title_idx != -1 and len(row) > title_idx:
                        title = str(row[title_idx])
                    else:
                        title = f"行{row_num}"
                    
                    # 進捗率を探す
                    progress_idx = self.find_column_index(headers, ['progress', '進捗', 'progress_rate'])
                    progress = row[progress_idx] if progress_idx != -1 and len(row) > progress_idx else '0'
                    
                    goal_data = {
                        'row': row_num,
                        'title': title,
                        'status': status,
                        'progress': progress,
                        'raw_data': row
                    }
                    active_goals.append(goal_data)
                    
                    title_preview = title[:50] + "..." if len(title) > 50 else title
                    print(f"   ✅ Active: 行{row_num} - {title_preview}")
        
        return active_goals
    
    def find_column_index(self, headers, possible_names):
        """列インデックスを検索"""
        headers_lower = [str(h).lower() for h in headers]
        for name in possible_names:
            name_lower = name.lower()
            if name_lower in headers_lower:
                return headers_lower.index(name_lower)
        return -1
    
    def calculate_total_progress(self, active_goals):
        """総合進捗率を計算"""
        if not active_goals:
            return 0.0
        
        total = 0.0
        count = 0
        
        for goal in active_goals:
            try:
                progress_str = str(goal['progress']).replace('%', '').strip()
                progress_value = float(progress_str) if progress_str.replace('.', '').isdigit() else 0.0
                total += progress_value
                count += 1
            except (ValueError, TypeError):
                continue
        
        return round(total / count, 2) if count > 0 else 0.0
    
    def display_results(self, active_goals, total_progress):
        """結果を表示"""
        print(f"\n📋 検出結果: {len(active_goals)}個のActiveゴール")
        print(f"📊 総合進捗率: {total_progress}%")
        
        for i, goal in enumerate(active_goals, 1):
            print(f"  {i}. 行{goal['row']}: {goal['title']}")
            print(f"     進捗: {goal['progress']}%, ステータス: {goal['status']}")

async def main():
    """メイン実行"""
    try:
        # 設定の検証
        ConfigLoader.validate_config()
        print("\n" + "="*50)
        
        # 進捗更新の実行
        updater = FixedProgressUpdater()
        await updater.update_progress_dashboard()
        
    except Exception as e:
        print(f"❌ 実行エラー: {e}")

if __name__ == "__main__":
    asyncio.run(main())
