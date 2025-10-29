"""
Week 5: エラー分類システム

エラーを種別に自動分類
"""
import re
from typing import Dict, List, Optional


class ErrorClassifier:
    """
    エラーを種別に分類するクラス
    
    エラー種別:
    - network: ネットワーク関連エラー
    - timeout: タイムアウト
    - rate_limit: APIレート制限
    - auth: 認証エラー
    - selector: セレクタエラー (Playwright等)
    - unknown: 分類不能
    """
    
    # エラーパターン定義
    ERROR_PATTERNS: Dict[str, List[str]] = {
        'network': [
            'ConnectionError',
            'NetworkError',
            'ConnectionRefusedError',
            'ConnectionResetError',
            'socket.gaierror',
            'requests.exceptions.ConnectionError',
            'urllib3.exceptions.NewConnectionError',
        ],
        'timeout': [
            'TimeoutError',
            'asyncio.TimeoutError',
            'ReadTimeout',
            'ConnectTimeout',
            'requests.exceptions.Timeout',
            'playwright._impl._api_types.TimeoutError',
        ],
        'rate_limit': [
            '429',
            'Too Many Requests',
            'Rate limit exceeded',
            'quota exceeded',
            'ResourceExhausted',
        ],
        'auth': [
            '401',
            '403',
            'Unauthorized',
            'Forbidden',
            'Authentication failed',
            'Invalid credentials',
            'Token expired',
        ],
        'selector': [
            'NoSuchElementException',
            'ElementNotFound',
            'Selector not found',
            'Element is not attached',
            'playwright._impl._api_types.Error: Timeout',
        ]
    }
    
    def classify(self, error: Exception) -> str:
        """
        エラーを分類
        
        Args:
            error: 分類するException
            
        Returns:
            エラー種別 ('network', 'timeout', 'rate_limit', 
                       'auth', 'selector', 'unknown')
        """
        error_str = str(error)
        error_type_name = type(error).__name__
        
        # エラー種別ごとにパターンマッチング
        for category, patterns in self.ERROR_PATTERNS.items():
            for pattern in patterns:
                # エラーメッセージまたは型名に一致
                if pattern.lower() in error_str.lower() or \
                   pattern.lower() in error_type_name.lower():
                    return category
        
        return 'unknown'
    
    def get_error_details(self, error: Exception) -> Dict[str, str]:
        """
        エラーの詳細情報を取得
        
        Args:
            error: Exception
            
        Returns:
            {
                'type': エラー種別,
                'message': エラーメッセージ,
                'class': エラークラス名
            }
        """
        return {
            'type': self.classify(error),
            'message': str(error)[:200],  # 最初の200文字
            'class': type(error).__name__
        }


# TODO: Day 2で実装予定
# - classify() のテスト
# - パターンの追加・調整
# - 複雑なエラーケースの対応
