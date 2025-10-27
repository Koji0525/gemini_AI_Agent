#!/usr/bin/env python3
"""
他のスクリプトでの設定ローダー使用例
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configuration.config_loader import ConfigLoader

def example_script():
    """設定ローダー使用例"""
    print("🔧 設定ローダー使用例")
    
    # 設定の検証
    ConfigLoader.validate_config()
    
    # 個別の設定取得
    spreadsheet_id = ConfigLoader.get('spreadsheet_id')
    service_account = ConfigLoader.get('service_account_file')
    
    print(f"\n📊 個別設定:")
    print(f"   スプレッドシートID: {spreadsheet_id}")
    print(f"   認証ファイル: {service_account}")
    
    # 全設定取得
    all_config = ConfigLoader.get_all()
    print(f"\n�� 全設定 ({len(all_config)}項目):")
    for key, value in all_config.items():
        if value:  # 設定されているもののみ表示
            masked_value = "******" if 'pass' in key.lower() else value
            print(f"   {key}: {masked_value}")

if __name__ == "__main__":
    example_script()
