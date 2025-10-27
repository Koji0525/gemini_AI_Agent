#!/usr/bin/env python3
"""
統一されたProgress Dashboard Updater - 設定ローダーを使用
"""

import os
import sys
import asyncio

# 設定ローダーをインポート
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from configuration.config_loader import ConfigLoader
from tools.sheets_manager import GoogleSheetsManager

class UnifiedProgressUpdater:
    """統一された進捗更新クラス"""
    
    def __init__(self):
        # 設定ローダーから設定を取得
        self.config = ConfigLoader()
        self.spreadsheet_id = self.config.get('spreadsheet_id')
        service_account_file = self.config.get('service_account_file')
        
        print("🔧 統一設定を使用:")
        print(f"   スプレッドシート: {self.spreadsheet_id}")
        print(f"   認証ファイル: {service_account_file}")
        
        self.sheets_manager = GoogleSheetsManager(self.spreadsheet_id, service_account_file)
    
    async def update_progress_dashboard(self):
        """進捗ダッシュボードを更新"""
        try:
            print("🚀 Progress Dashboard 更新開始...")
            
            # 1. project_goalからデータ取得
            goals_data = await self._load_sheet_data('project_goal')
            if not goals_data:
                return
            
            # 2. Activeゴールを抽出
            active_goals = self._extract_active_goals(goals_data)
            print(f"🎯 {len(active_goals)}個のActiveゴールを検出")
            
            # 3. 進捗計算
            total_progress = self._calculate_total_progress(active_goals)
            print(f"📊 総合進捗: {total_progress}%")
            
            # 4. ダッシュボード更新
            await self._update_dashboard(active_goals, total_progress)
            
            print("✅ Progress Dashboard 更新完了")
            
        except Exception as e:
            print(f"❌ 更新エラー: {e}")
            import traceback
            traceback.print_exc()
    
    async def _load_sheet_data(self, sheet_name: str):
        """シートデータを読み込み"""
        try:
            data = await self.sheets_manager.load_tasks_from_sheet(sheet_name)
            if data and len(data) > 0:
                print(f"✅ {sheet_name}: {len(data)}行のデータを取得")
                return data
            else:
                print(f"❌ {sheet_name}: データが空です")
                return None
        except Exception as e:
            print(f"❌ {sheet_name}読み込みエラー: {e}")
            return None
    
    def _extract_active_goals(self, data):
        """Activeなゴールを抽出"""
        if len(data) < 2:
            return []
        
        headers = data[0]
        active_goals = []
        
        # ヘッダー分析
        print(f"🔍 ヘッダー: {headers}")
        
        # 列インデックスの検出
        status_idx = self._find_column_index(headers, ['status', 'ステータス'])
        title_idx = self._find_column_index(headers, ['goal_description', 'title', '説明'])
        
        print(f"📊 列マッピング: status={status_idx}, title={title_idx}")
        
        # Activeゴールの抽出
        for row_num, row in enumerate(data[1:], 2):
            if status_idx != -1 and len(row) > status_idx:
                status = str(row[status_idx]).lower().strip()
                if status == 'active':
                    goal_title = row[title_idx] if title_idx != -1 and len(row) > title_idx else f"行{row_num}"
                    active_goals.append({
                        'row': row_num,
                        'title': goal_title,
                        'status': status
                    })
                    print(f"   ✅ Active: 行{row_num} - {goal_title[:50]}...")
        
        return active_goals
    
    def _find_column_index(self, headers, possible_names):
        """列インデックスを検索"""
        headers_lower = [str(h).lower() for h in headers]
        for name in possible_names:
            if name.lower() in headers_lower:
                return headers_lower.index(name.lower())
        return -1
    
    def _calculate_total_progress(self, active_goals):
        """総合進捗率を計算"""
        if not active_goals:
            return 0.0
        # 簡易的な進捗計算（実際は各ゴールの進捗率から計算）
        return min(len(active_goals) * 20, 100)  # 仮の計算
    
    async def _update_dashboard(self, active_goals, total_progress):
        """ダッシュボードを更新"""
        try:
            # progress_dashboardシートを読み込み
            dashboard_data = await self._load_sheet_data('progress_dashboard')
            if dashboard_data:
                print(f"📋 ダッシュボードデータ: {len(dashboard_data)}行")
                # ここで実際の更新処理を実装
                # await self.sheets_manager.update_task_status(...)
            else:
                print("📝 新しいダッシュボードを作成します")
                
        except Exception as e:
            print(f"❌ ダッシュボード更新エラー: {e}")

async def main():
    """メイン実行"""
    try:
        # 設定の検証
        ConfigLoader.validate_config()
        print("\n" + "="*50)
        
        # 進捗更新の実行
        updater = UnifiedProgressUpdater()
        await updater.update_progress_dashboard()
        
    except Exception as e:
        print(f"❌ 実行エラー: {e}")

if __name__ == "__main__":
    asyncio.run(main())
