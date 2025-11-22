"""
緊急停止マネージャー
システムの安全な停止・再開を管理
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class EmergencyStopManager:
    """緊急停止マネージャー"""
    
    def __init__(self):
        self.pause_flag = Path("/tmp/system_paused.flag")
        self.emergency_flag = Path("/tmp/system_emergency_stop.flag")
        self.status_file = Path("logs/system_status.json")
        
    def is_paused(self) -> bool:
        """一時停止中かチェック"""
        return self.pause_flag.exists()
    
    def is_emergency_stopped(self) -> bool:
        """緊急停止中かチェック"""
        return self.emergency_flag.exists()
    
    def pause_system(self, reason: str = "manual"):
        """システムを一時停止"""
        print(f"\n⏸️  システム一時停止: {reason}")
        
        self.pause_flag.touch()
        
        self._log_status({
            'action': 'pause',
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
    
    def emergency_stop(self, reason: str):
        """緊急停止"""
        print(f"\n🚨 緊急停止: {reason}")
        
        self.emergency_flag.touch()
        self.pause_flag.touch()
        
        self._log_status({
            'action': 'emergency_stop',
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
    
    def resume_system(self):
        """システムを再開"""
        print(f"\n▶️  システム再開")
        
        if self.pause_flag.exists():
            self.pause_flag.unlink()
        
        if self.emergency_flag.exists():
            self.emergency_flag.unlink()
        
        self._log_status({
            'action': 'resume',
            'timestamp': datetime.now().isoformat()
        })
    
    def get_status(self) -> Dict:
        """システム状態を取得"""
        return {
            'paused': self.is_paused(),
            'emergency_stopped': self.is_emergency_stopped(),
            'running': not (self.is_paused() or self.is_emergency_stopped())
        }
    
    def _log_status(self, status: Dict):
        """状態をログに記録"""
        import json
        
        self.status_file.parent.mkdir(exist_ok=True, parents=True)
        
        # 既存のログを読み込み
        if self.status_file.exists():
            with open(self.status_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(status)
        
        # 最新100件のみ保持
        logs = logs[-100:]
        
        with open(self.status_file, 'w') as f:
            json.dump(logs, f, indent=2)

