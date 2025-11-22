"""
APIレート制限管理
Gemini APIのレート制限を監視・制御
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class APIRateLimiter:
    """APIレート制限管理"""
    
    def __init__(self):
        # Gemini API無料枠の制限
        self.requests_per_minute = 15
        self.requests_per_day = 1500
        
        # ログファイル
        self.log_dir = Path("/workspaces/gemini_AI_Agent/logs/api_usage")
        self.log_dir.mkdir(exist_ok=True, parents=True)
        
        self.log_file = self.log_dir / "api_requests.json"
        
        # リクエストログを読み込み
        self._load_log()
    
    def _load_log(self):
        """ログを読み込み"""
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                data = json.load(f)
                # ISO形式の文字列をdatetimeに変換
                self.request_log = [
                    datetime.fromisoformat(ts) 
                    for ts in data.get('requests', [])
                ]
        else:
            self.request_log = []
    
    def _save_log(self):
        """ログを保存"""
        data = {
            'requests': [ts.isoformat() for ts in self.request_log],
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.log_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def can_request(self) -> bool:
        """リクエスト可能かチェック"""
        now = datetime.now()
        
        # 古いログを削除（2日以上前）
        cutoff = now - timedelta(days=2)
        self.request_log = [t for t in self.request_log if t > cutoff]
        
        # 1分以内のリクエスト数
        one_minute_ago = now - timedelta(minutes=1)
        recent_requests = [t for t in self.request_log if t > one_minute_ago]
        
        if len(recent_requests) >= self.requests_per_minute:
            return False
        
        # 1日以内のリクエスト数
        one_day_ago = now - timedelta(days=1)
        today_requests = [t for t in self.request_log if t > one_day_ago]
        
        if len(today_requests) >= self.requests_per_day:
            return False
        
        return True
    
    def wait_if_needed(self) -> int:
        """必要に応じて待機"""
        wait_count = 0
        
        while not self.can_request():
            now = datetime.now()
            
            # 1分以内のリクエスト数をチェック
            one_minute_ago = now - timedelta(minutes=1)
            recent_requests = [t for t in self.request_log if t > one_minute_ago]
            
            if len(recent_requests) >= self.requests_per_minute:
                wait_time = 10
                print(f"⏳ APIレート制限（1分）: {len(recent_requests)}/{self.requests_per_minute}")
                print(f"   {wait_time}秒待機...")
            else:
                # 1日の制限超過
                wait_time = 60
                one_day_ago = now - timedelta(days=1)
                today_requests = [t for t in self.request_log if t > one_day_ago]
                print(f"⏳ APIレート制限（1日）: {len(today_requests)}/{self.requests_per_day}")
                print(f"   {wait_time}秒待機...")
            
            time.sleep(wait_time)
            wait_count += 1
            
            # 10回以上待機した場合は緊急停止
            if wait_count >= 10:
                print("🚨 レート制限待機回数超過 - 緊急停止")
                Path("/tmp/system_paused.flag").touch()
                return wait_count
        
        return wait_count
    
    def record_request(self):
        """リクエストを記録"""
        self.request_log.append(datetime.now())
        self._save_log()
    
    def get_usage_stats(self) -> Dict:
        """使用統計を取得"""
        now = datetime.now()
        
        # 1分以内
        one_minute_ago = now - timedelta(minutes=1)
        minute_count = len([t for t in self.request_log if t > one_minute_ago])
        
        # 1日以内
        one_day_ago = now - timedelta(days=1)
        day_count = len([t for t in self.request_log if t > one_day_ago])
        
        return {
            'minute': {
                'used': minute_count,
                'limit': self.requests_per_minute,
                'available': self.requests_per_minute - minute_count
            },
            'day': {
                'used': day_count,
                'limit': self.requests_per_day,
                'available': self.requests_per_day - day_count
            }
        }

