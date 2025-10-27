#!/usr/bin/env python3
"""
同期設定変更スクリプト - 対話式で設定を変更
"""

import os
import sys

def change_settings():
    print("⚙️ 同期設定変更ツール")
    print("=" * 50)
    
    settings_file = 'configuration/sync_settings.py'
    
    if not os.path.exists(settings_file):
        print("❌ 設定ファイルが見つかりません")
        return
    
    # 現在の設定を読み込み
    with open(settings_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("📋 現在の設定:")
    auto_sync = 'AUTO_SYNC_ENABLED = True' in content
    interval_line = [line for line in content.split('\n') if 'SYNC_INTERVAL_MINUTES' in line][0]
    interval = int(interval_line.split('=')[1].split('#')[0].strip())
    
    print(f"   自動同期: {'✅ 有効' if auto_sync else '❌ 無効'}")
    print(f"   同期間隔: {interval}分")
    
    print("\n🔧 変更オプション:")
    print("   1. 自動同期を有効化")
    print("   2. 自動同期を無効化")
    print("   3. 同期間隔を変更")
    print("   4. すべてデフォルトに戻す")
    
    choice = input("\n選択してください (1-4): ").strip()
    
    new_content = content
    
    if choice == '1':
        new_content = new_content.replace(
            'AUTO_SYNC_ENABLED = False', 
            'AUTO_SYNC_ENABLED = True'
        )
        print("✅ 自動同期を有効化しました")
        
    elif choice == '2':
        new_content = new_content.replace(
            'AUTO_SYNC_ENABLED = True', 
            'AUTO_SYNC_ENABLED = False'
        )
        print("✅ 自動同期を無効化しました")
        
    elif choice == '3':
        new_interval = input("新しい同期間隔（分）: ").strip()
        try:
            new_interval = int(new_interval)
            new_content = new_content.replace(
                f'SYNC_INTERVAL_MINUTES = {interval}',
                f'SYNC_INTERVAL_MINUTES = {new_interval}'
            )
            print(f"✅ 同期間隔を {new_interval}分に変更しました")
        except ValueError:
            print("❌ 数値を入力してください")
            return
            
    elif choice == '4':
        # デフォルト設定
        new_content = '''"""
同期設定ファイル - 簡単に設定を変更可能
"""

# 自動同期設定
AUTO_SYNC_ENABLED = False  # Trueにすると自動同期が有効
SYNC_INTERVAL_MINUTES = 60  # 同期間隔（分）
MAX_SYNC_ROWS = 100  # 最大保持行数

# 同期対象のシート設定
SYNC_SHEETS = {
    'progress_dashboard': True,
    'project_goal': True, 
    'pm_tasks': True
}

# 通知設定
NOTIFICATIONS = {
    'on_success': True,
    'on_error': True,
    'log_level': 'INFO'  # DEBUG, INFO, WARNING, ERROR
}

# データフィルタ設定
FILTERS = {
    'min_progress_rate': 0,  # 最小進捗率（%）
    'include_completed': False,  # 完了したゴールを含む
    'priority_levels': [1, 2, 3]  # 同期する優先度
}
'''
        print("✅ 設定をデフォルトに戻しました")
    
    else:
        print("❌ 無効な選択です")
        return
    
    # 設定ファイルを保存
    with open(settings_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"\n💡 変更を反映するには:")
    print("   python3 scripts/configurable_sync_manager.py を実行してください")

if __name__ == "__main__":
    change_settings()
