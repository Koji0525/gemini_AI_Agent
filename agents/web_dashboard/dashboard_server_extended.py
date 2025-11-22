"""
Webダッシュボードサーバー（システム制御拡張版）
既存機能 + システム起動/停止制御
"""

import sys
import os
import subprocess
import signal
from pathlib import Path

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

# 既存のdashboard_server.pyをインポート
from agents.web_dashboard.dashboard_server import app, sheets_manager, f9_interface

from fastapi import HTTPException

# ステート管理ファイル
STATE_FILE = '/tmp/system_control.state'
PID_FILE = '/tmp/system_executor.pid'

def get_system_state():
    """システム状態を取得"""
    if not os.path.exists(STATE_FILE):
        return 'stopped'
    
    with open(STATE_FILE, 'r') as f:
        state = f.read().strip()
    
    # PIDファイルでプロセスの実存を確認
    if state == 'running' and os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        try:
            os.kill(pid, 0)  # プロセスが存在するかチェック
            return 'running'
        except OSError:
            return 'stopped'
    
    return state

def set_system_state(state: str):
    """システム状態を設定"""
    with open(STATE_FILE, 'w') as f:
        f.write(state)

@app.get("/api/system/status")
async def get_system_status():
    """システム状態を取得"""
    state = get_system_state()
    
    pid = None
    if state == 'running' and os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
    
    return {
        'state': state,
        'pid': pid,
        'is_running': state == 'running'
    }

@app.post("/api/system/start")
async def start_system():
    """システムを起動"""
    try:
        print("\n" + "=" * 80)
        print("🚀 システム起動リクエスト")
        print("=" * 80)
        
        current_state = get_system_state()
        
        if current_state == 'running':
            print("⚠️  システムは既に起動中です")
            return {
                'success': False,
                'message': 'システムは既に起動中です'
            }
        
        # 起動スクリプトをバックグラウンドで実行
        print("🔄 24時間稼働システムを起動中...")
        
        process = subprocess.Popen(
            ['bash', 'sh/run_autonomous_24h_v6_final.sh'],
            stdout=open('logs/executor_stdout.log', 'w'),
            stderr=open('logs/executor_stderr.log', 'w'),
            cwd='/workspaces/gemini_AI_Agent'
        )
        
        # PIDを保存
        with open(PID_FILE, 'w') as f:
            f.write(str(process.pid))
        
        # 状態を更新
        set_system_state('running')
        
        print(f"✅ システム起動完了 (PID: {process.pid})")
        print("=" * 80)
        
        return {
            'success': True,
            'message': 'システムを起動しました',
            'pid': process.pid
        }
        
    except Exception as e:
        print(f"❌ システム起動エラー: {e}")
        return {
            'success': False,
            'message': f'起動エラー: {str(e)}'
        }

@app.post("/api/system/stop")
async def stop_system():
    """システムを停止"""
    try:
        print("\n" + "=" * 80)
        print("⏹️  システム停止リクエスト")
        print("=" * 80)
        
        current_state = get_system_state()
        
        if current_state != 'running':
            print("⚠️  システムは起動していません")
            return {
                'success': False,
                'message': 'システムは起動していません'
            }
        
        # PIDを取得
        if not os.path.exists(PID_FILE):
            print("⚠️  PIDファイルが見つかりません")
            set_system_state('stopped')
            return {
                'success': False,
                'message': 'PIDファイルが見つかりません'
            }
        
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        print(f"🔄 プロセス(PID: {pid})を停止中...")
        
        # プロセスを停止
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"✅ プロセス停止シグナル送信")
        except OSError:
            print(f"⚠️  プロセスが既に終了しています")
        
        # ファイルを削除
        os.remove(PID_FILE)
        set_system_state('stopped')
        
        print("✅ システム停止完了")
        print("=" * 80)
        
        return {
            'success': True,
            'message': 'システムを停止しました'
        }
        
    except Exception as e:
        print(f"❌ システム停止エラー: {e}")
        return {
            'success': False,
            'message': f'停止エラー: {str(e)}'
        }

# 既存の start_server 関数を使用
from agents.web_dashboard.dashboard_server import start_server

