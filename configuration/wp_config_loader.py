"""
WordPress設定ローダー - 修正版
"""
import os
import sys
from pathlib import Path
from typing import Dict, Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.sheets_manager import GoogleSheetsManager
    from configuration.config_loader import get_spreadsheet_id, get_service_account_file
    HAS_SHEETS = True
except ImportError as e:
    print(f"⚠️  モジュールインポートエラー: {e}")
    HAS_SHEETS = False

class WordPressConfigLoader:
    """WordPress設定を管理"""
    
    def __init__(self):
        self.wp_config = {}
        if HAS_SHEETS:
            self._load_config()
        else:
            print("❌ Sheetsマネージャーが利用できません")
    
    def _load_config(self):
        """設定をシートから読み込み"""
        try:
            sheets = GoogleSheetsManager(
                spreadsheet_id=get_spreadsheet_id(),
                service_account_file=get_service_account_file()
            )
            
            spreadsheet = sheets.gc.open_by_key(get_spreadsheet_id())
            setting_sheet = spreadsheet.worksheet('setting')
            settings_data = setting_sheet.get_all_records()
            
            print('📋 settingシートから設定を読み込み中...')
            
            # すべての設定を表示（デバッグ用）
            for row in settings_data:
                key = row.get('key', '').strip()
                value = row.get('value', '').strip()
                print(f'  📝 {key} = {value[:20]}{"..." if len(value) > 20 else ""}')
            
            # WordPress関連設定を抽出
            for row in settings_data:
                key = row.get('key', '').strip().lower()
                value = row.get('value', '').strip()
                
                # WordPress関連のキーを検出
                if any(wp_key in key for wp_key in ['wordpress', 'wp', 'url', 'user', 'pass']):
                    # キー名を正規化
                    clean_key = self._normalize_key(key)
                    self.wp_config[clean_key] = value
                    print(f'🎯 WordPress設定: {clean_key} = {value[:10]}{"..." if len(value) > 10 else ""}')
            
            print(f"📋 読み込んだWordPress設定: {len(self.wp_config)}件")
            
        except Exception as e:
            print(f"❌ WordPress設定読み込みエラー: {e}")
    
    def _normalize_key(self, key: str) -> str:
        """キー名を正規化"""
        key = key.lower()
        replacements = {
            'wordpress_': '',
            'wp_': '',
            'wordpress': '',
            'url': 'url',
            'username': 'username', 
            'password': 'password',
            'user': 'username',
            'pass': 'password'
        }
        
        for old, new in replacements.items():
            key = key.replace(old, new)
        
        return key.strip('_')
    
    def get_wp_url(self) -> Optional[str]:
        """WordPress URLを取得"""
        return self.wp_config.get('url')
    
    def get_wp_username(self) -> Optional[str]:
        """ユーザー名を取得"""
        return self.wp_config.get('username') or self.wp_config.get('user')
    
    def get_wp_password(self) -> Optional[str]:
        """パスワードを取得"""
        return self.wp_config.get('password') or self.wp_config.get('pass')
    
    def has_valid_config(self) -> bool:
        """有効な設定があるか確認"""
        url = self.get_wp_url()
        username = self.get_wp_username()
        password = self.get_wp_password()
        
        has_config = all([url, username, password])
        
        if has_config:
            print(f"✅ WordPress設定: 有効 (URL: {url}, ユーザー: {username})")
        else:
            print(f"❌ WordPress設定: 不完全 (URL: {bool(url)}, ユーザー: {bool(username)}, パスワード: {bool(password)})")
        
        return has_config
    
    def get_config_summary(self) -> Dict:
        """設定のサマリーを取得（デバッグ用）"""
        return {
            'url': self.get_wp_url(),
            'username': self.get_wp_username(),
            'password_set': bool(self.get_wp_password()),
            'is_valid': self.has_valid_config(),
            'all_config': self.wp_config
        }

# シングルトンインスタンス
wp_config_loader = WordPressConfigLoader()

