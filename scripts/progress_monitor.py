#!/usr/bin/env python3
"""
進捗モニター - 定期的な進捗確認とレポート
"""

import os
import sys
import asyncio
import time
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from configuration.config_loader import ConfigLoader
from scripts.enhanced_progress_updater import EnhancedProgressUpdater

class ProgressMonitor:
    """進捗モニター - 定期的な進捗確認"""
    
    def __init__(self):
        self.config = ConfigLoader()
        self.updater = EnhancedProgressUpdater()
    
    async def monitor_progress(self, interval_minutes=60):
        """定期的な進捗監視"""
        print(f"🔍 進捗モニター開始 (間隔: {interval_minutes}分)")
        print("=" * 50)
        
        iteration = 0
        try:
            while True:
                iteration += 1
                print(f"\n🕒 監視実行 #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("-" * 40)
                
                # 進捗更新を実行
                await self.updater.update_progress_dashboard()
                
                # 進捗サマリーを表示
                await self.show_progress_summary()
                
                print(f"\n⏰ 次の更新まで {interval_minutes}分待機...")
                print("=" * 50)
                
                # 待機（テスト用に短く設定）
                test_interval = 10  # テスト用に10秒
                if interval_minutes == 60:  # 本番モード
                    await asyncio.sleep(interval_minutes * 60)
                else:  # テストモード
                    await asyncio.sleep(test_interval)
                    
        except KeyboardInterrupt:
            print("\n🛑 進捗モニターを停止しました")
        except Exception as e:
            print(f"❌ モニターエラー: {e}")
    
    async def show_progress_summary(self):
        """進捗サマリーを表示"""
        try:
            # 簡易的な進捗分析
            config = ConfigLoader()
            sheets_config = config.get_sheets_config()
            
            scopes = ['https://www.googleapis.com/auth/spreadsheets']
            from google.oauth2.service_account import Credentials
            import gspread
            
            credentials = Credentials.from_service_account_file(
                sheets_config['service_account_file'], 
                scopes=scopes
            )
            gc = gspread.authorize(credentials)
            spreadsheet = gc.open_by_key(sheets_config['spreadsheet_id'])
            
            # 最新の進捗データを取得
            worksheet = spreadsheet.worksheet('progress_dashboard')
            data = worksheet.get_all_values()
            
            if len(data) > 1:
                latest = data[1]  # 最新の行
                print(f"\n📈 最新進捗サマリー:")
                print(f"   🕒 更新時刻: {latest[0]}")
                print(f"   📊 総合進捗: {latest[1]}%")
                print(f"   🎯 Activeゴール: {latest[2]}個")
                print(f"   ✅ 完了タスク: {latest[3]}/{latest[4]} ({latest[5]}%)")
                
                # 進捗トレンド分析
                if len(data) > 2:
                    previous = data[2]  # 前回のデータ
                    current_progress = float(latest[1])
                    previous_progress = float(previous[1])
                    progress_change = current_progress - previous_progress
                    
                    trend = "↑増加" if progress_change > 0 else "↓減少" if progress_change < 0 else "→横ばい"
                    print(f"   📈 進捗変化: {progress_change:+.2f}% ({trend})")
            
        except Exception as e:
            print(f"❌ サマリー取得エラー: {e}")

async def main():
    """メイン実行"""
    try:
        print("🚀 進捗モニター起動")
        ConfigLoader.validate_config()
        
        monitor = ProgressMonitor()
        
        # テストモード（10秒間隔）で実行
        print("🧪 テストモード（10秒間隔）で実行します")
        await monitor.monitor_progress(interval_minutes=0.1)  # 10秒
        
    except Exception as e:
        print(f"❌ モニター起動エラー: {e}")

if __name__ == "__main__":
    asyncio.run(main())
