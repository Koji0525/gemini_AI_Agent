#!/usr/bin/env python3
"""settingシートのフォーマットを修正"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import get_spreadsheet_id, get_service_account_file

def fix_setting_sheet():
    """settingシートのフォーマットを修正"""
    
    sheets = GoogleSheetsManager(
        spreadsheet_id=get_spreadsheet_id(),
        service_account_file=get_service_account_file()
    )
    
    try:
        spreadsheet = sheets.gc.open_by_key(get_spreadsheet_id())
        setting_sheet = spreadsheet.worksheet('setting')
        
        print("📋 現在のsettingシート構造:")
        
        # 生データを取得
        all_data = setting_sheet.get_all_values()
        
        # ヘッダーを確認
        headers = all_data[0] if all_data else []
        print(f"ヘッダー: {headers}")
        
        # データを表示
        for i, row in enumerate(all_data[:10]):  # 最初の10行のみ
            print(f"行{i+1}: {row}")
        
        # WordPress設定を抽出（現在のフォーマット用）
        wp_config = {}
        for row in all_data:
            if len(row) > 0 and row[0].strip():
                key = row[0].strip().lower()
                if 'wp_url' in key:
                    wp_config['url'] = row[1] if len(row) > 1 else ''
                elif 'wp_user' in key:
                    wp_config['username'] = row[1] if len(row) > 1 else ''
                elif 'wp_pass' in key:
                    wp_config['password'] = row[1] if len(row) > 1 else ''
        
        print(f"\n🎯 抽出したWordPress設定:")
        for key, value in wp_config.items():
            print(f"  {key}: {value[:20]}{'...' if len(value) > 20 else ''}")
        
        # 設定が正しく抽出されているか確認
        if all(wp_config.values()):
            print("✅ WordPress設定は正しく抽出されています")
            return True
        else:
            print("❌ WordPress設定の抽出に問題があります")
            return False
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

if __name__ == "__main__":
    fix_setting_sheet()

