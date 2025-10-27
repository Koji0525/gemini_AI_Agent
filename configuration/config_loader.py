#!/usr/bin/env python3
"""
プロジェクト全体の設定ローダー - 一元管理
v1.1 - 属性アクセス対応版
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any

class ConfigLoader:
    """プロジェクト全体の設定を一元管理"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._load_config()
        return cls._instance
    
    @classmethod
    def _load_config(cls):
        """設定を読み込み"""
        # .envファイルを明示的に読み込み
        env_path = '/workspaces/gemini_AI_Agent/.env'
        load_dotenv(env_path)
        
        cls._config = {
            # Google Sheets設定
            'spreadsheet_id': os.getenv('SPREADSHEET_ID'),
            'service_account_file': os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            'pm_sheet_name': os.getenv('PM_SHEET_NAME', 'pm_tasks'),
            'settings_sheet_name': os.getenv('SETTINGS_SHEET_NAME', 'setting'),
            'progress_sheet_name': 'progress_dashboard',
            'goals_sheet_name': 'project_goal',
            
            # WordPress設定
            'wp_url': os.getenv('WP_URL'),
            'wp_user': os.getenv('WP_USER'),
            'wp_pass': os.getenv('WP_PASS'),
            
            # プロジェクト設定
            'project_root': os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'debug_mode': os.getenv('DEBUG_MODE', 'False').lower() == 'true',
            'max_retries': int(os.getenv('MAX_RETRIES', '3')),
            'timeout': int(os.getenv('TIMEOUT', '300'))
        }
        
        # 必須設定の検証
        required = ['spreadsheet_id', 'service_account_file']
        for key in required:
            if not cls._config.get(key):
                raise ValueError(f"❌ 必須環境変数が設定されていません: {key}")
    
    def __getattr__(self, name: str) -> Any:
        """属性アクセスをサポート（config.wp_url のような形式）"""
        if self._config and name in self._config:
            return self._config[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """設定値を取得"""
        if cls._config is None:
            cls._load_config()
        return cls._config.get(key, default)
    
    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """全ての設定を取得"""
        if cls._config is None:
            cls._load_config()
        return cls._config.copy()
    
    @classmethod
    def get_sheets_config(cls) -> Dict[str, str]:
        """Sheets関連の設定を取得"""
        return {
            'spreadsheet_id': cls.get('spreadsheet_id'),
            'service_account_file': cls.get('service_account_file'),
            'pm_sheet_name': cls.get('pm_sheet_name', 'pm_tasks'),
            'settings_sheet_name': cls.get('settings_sheet_name', 'setting'),
            'progress_sheet_name': cls.get('progress_sheet_name', 'progress_dashboard'),
            'goals_sheet_name': cls.get('goals_sheet_name', 'project_goal')
        }
    
    @classmethod
    def get_wordpress_config(cls) -> Dict[str, str]:
        """WordPress関連の設定を取得"""
        return {
            'url': cls.get('wp_url'),
            'username': cls.get('wp_user'),
            'password': cls.get('wp_pass')
        }
    
    @classmethod
    def validate_config(cls):
        """設定の検証"""
        print("🔧 設定検証:")
        config = cls.get_all()
        for key, value in config.items():
            status = "✅" if value else "❌"
            # パスワードはマスク表示
            display_value = value
            if 'pass' in key.lower() and value:
                display_value = "******"
            print(f"   {status} {key}: {display_value}")
        
        # 必須設定の確認
        required_ok = all([config['spreadsheet_id'], config['service_account_file']])
        if required_ok:
            print("✅ 必須設定が正しく設定されています")
        else:
            print("❌ 必須設定が不足しています")

# シングルトンインスタンス
config = ConfigLoader()

if __name__ == "__main__":
    ConfigLoader.validate_config()
    
    # 属性アクセスのテスト
    print("\n🧪 属性アクセステスト:")
    print(f"WP_URL: {config.wp_url}")
    print(f"WP_USER: {config.wp_user}")
    print(f"WP_PASS: {'設定済み' if config.wp_pass else '未設定'}")
