#!/usr/bin/env python3
"""sheets_managerの状況確認"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from tools.sheets_manager import GoogleSheetsManager
    print("✅ tools.sheets_manager インポート成功")
    
    # 設定を確認
    from configuration.config_loader import get_spreadsheet_id, get_service_account_file
    
    sheets = GoogleSheetsManager(
        spreadsheet_id=get_spreadsheet_id(),
        service_account_file=get_service_account_file()
    )
    
    print("✅ GoogleSheetsManager 初期化成功")
    
    # settingシートを確認
    try:
        spreadsheet = sheets.gc.open_by_key(get_spreadsheet_id())
        setting_sheet = spreadsheet.worksheet('setting')
        settings_data = setting_sheet.get_all_records()
        
        print('📋 settingシートの内容:')
        for row in settings_data:
            print(f'  {row}')
            
        # WordPress関連の設定を探す
        wp_settings = {}
        for row in settings_data:
            key = row.get('key', '').lower()
            value = row.get('value', '')
            if 'wordpress' in key or 'wp' in key or 'url' in key:
                wp_settings[key] = value
                print(f'🎯 関連設定: {key} = {value}')
        
        if not wp_settings:
            print('❌ WordPress関連設定が見つかりません')
        else:
            print(f'✅ WordPress関連設定: {len(wp_settings)}件見つかりました')
            
    except Exception as e:
        print(f'❌ settingシート読み込みエラー: {e}')
    
except Exception as e:
    print(f'❌ インポートエラー: {e}')
    print("💡 代替手段を試します...")

