"""
リアルタイムダッシュボード
システム状態をHTML形式で可視化
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class MonitoringDashboard:
    """モニタリングダッシュボード"""
    
    def __init__(self):
        self.dashboard_file = Path("status.html")
        
    def generate_dashboard(self) -> str:
        """ダッシュボードを生成"""
        
        # システム状態を収集
        status = self._collect_status()
        
        # HTMLを生成
        html = self._generate_html(status)
        
        # ファイルに保存
        self.dashboard_file.write_text(html)
        
        return str(self.dashboard_file)
    
    def _collect_status(self) -> Dict:
        """システム状態を収集"""
        
        try:
            from agents.robustness.api_rate_limiter import APIRateLimiter
            rate_limiter = APIRateLimiter()
            api_usage = rate_limiter.get_usage_stats()
        except:
            api_usage = None
        
        try:
            from agents.robustness.resource_cleaner import ResourceCleaner
            cleaner = ResourceCleaner()
            disk_usage = cleaner.get_disk_usage()
            memory_usage = cleaner.get_memory_usage()
        except:
            disk_usage = None
            memory_usage = None
        
        try:
            from agents.robustness.emergency_stop_manager import EmergencyStopManager
            stop_manager = EmergencyStopManager()
            system_status = stop_manager.get_status()
        except:
            system_status = {'running': True}
        
        return {
            'timestamp': datetime.now(),
            'api_usage': api_usage,
            'disk_usage': disk_usage,
            'memory_usage': memory_usage,
            'system_status': system_status
        }
    
    def _generate_html(self, status: Dict) -> str:
        """HTMLを生成"""
        
        timestamp = status['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        
        # システム状態の色
        if status['system_status'].get('emergency_stopped'):
            status_color = 'red'
            status_text = '🚨 緊急停止'
        elif status['system_status'].get('paused'):
            status_color = 'orange'
            status_text = '⏸️ 一時停止'
        else:
            status_color = 'green'
            status_text = '✅ 稼働中'
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="30">
    <title>24時間自律稼働システム - ダッシュボード</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            background: #1a1a1a;
            color: #00ff00;
            padding: 20px;
            margin: 0;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
        }}
        .status-card {{
            background: #2a2a2a;
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 0 20px rgba(0,255,0,0.3);
        }}
        .status-header {{
            font-size: 24px;
            color: {status_color};
            text-align: center;
            margin-bottom: 20px;
            font-weight: bold;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #444;
        }}
        .metric-label {{
            color: #00ff00;
        }}
        .metric-value {{
            color: #ffffff;
            font-weight: bold;
        }}
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: #444;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 5px;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #00ff00, #00aa00);
            transition: width 0.3s;
        }}
        .timestamp {{
            text-align: center;
            color: #888;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 24時間自律稼働システム</h1>
        
        <div class="status-card">
            <div class="status-header">{status_text}</div>
        </div>
'''
        
        # API使用状況
        if status['api_usage']:
            api = status['api_usage']
            minute_percent = (api['minute']['used'] / api['minute']['limit']) * 100
            day_percent = (api['day']['used'] / api['day']['limit']) * 100
            
            html += f'''
        <div class="status-card">
            <h2>📊 API使用状況</h2>
            <div class="metric">
                <span class="metric-label">1分あたり:</span>
                <span class="metric-value">{api['minute']['used']}/{api['minute']['limit']}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {minute_percent}%"></div>
            </div>
            
            <div class="metric" style="margin-top: 15px;">
                <span class="metric-label">1日あたり:</span>
                <span class="metric-value">{api['day']['used']}/{api['day']['limit']}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {day_percent}%"></div>
            </div>
        </div>
'''
        
        # ディスク使用状況
        if status['disk_usage']:
            disk = status['disk_usage']
            html += f'''
        <div class="status-card">
            <h2>💾 ディスク使用状況</h2>
            <div class="metric">
                <span class="metric-label">使用量:</span>
                <span class="metric-value">{disk['used_gb']:.1f}GB / {disk['total_gb']:.1f}GB</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {disk['percent']}%"></div>
            </div>
            <div class="metric" style="margin-top: 15px;">
                <span class="metric-label">使用率:</span>
                <span class="metric-value">{disk['percent']:.1f}%</span>
            </div>
        </div>
'''
        
        # メモリ使用状況
        if status['memory_usage']:
            mem = status['memory_usage']
            html += f'''
        <div class="status-card">
            <h2>🧠 メモリ使用状況</h2>
            <div class="metric">
                <span class="metric-label">使用量:</span>
                <span class="metric-value">{mem['used_gb']:.1f}GB / {mem['total_gb']:.1f}GB</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {mem['percent']}%"></div>
            </div>
            <div class="metric" style="margin-top: 15px;">
                <span class="metric-label">使用率:</span>
                <span class="metric-value">{mem['percent']:.1f}%</span>
            </div>
        </div>
'''
        
        html += f'''
        <div class="timestamp">
            最終更新: {timestamp}<br>
            30秒ごとに自動更新
        </div>
    </div>
</body>
</html>
'''
        
        return html

