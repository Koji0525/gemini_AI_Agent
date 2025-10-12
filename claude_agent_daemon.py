#!/usr/bin/env python3
"""
Claude エージェント常駐デーモン（即座実行版）
"""
import os
import time
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class ClaudeAgentDaemon:
    def __init__(self, interval=60, check_interval=5):
        self.interval = interval  # 定期実行間隔（秒）
        self.check_interval = check_interval  # トリガーチェック間隔（秒）
        self.running = False
        self.log_file = Path('logs/daemon.log')
        self.log_file.parent.mkdir(exist_ok=True)
    
    def log(self, message):
        """ログ出力"""
        timestamp = datetime.now().strftime('[%H:%M:%S]')
        log_msg = f"{timestamp} {message}"
        print(log_msg)
        with open(self.log_file, 'a') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    
    def check_trigger_file(self):
        """トリガーファイルの確認"""
        trigger = Path('TRIGGER')
        if trigger.exists():
            self.log("🔔 トリガー検出 → 即座に実行！")
            trigger.unlink()
            return True
        return False
    
    def run_autonomous_system(self):
        """自律システムを実行"""
        self.log("🚀 自律システム実行開始")
        start_time = time.time()
        
        try:
            # 1. autonomous_system.py 実行
            result = subprocess.run(
                'python autonomous_system.py',
                shell=True,
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if result.returncode == 0:
                self.log("✅ 自律システム成功")
            else:
                self.log(f"❌ 自律システムエラー: {result.returncode}")
            
            # 2. Claude API で自動対話
            result = subprocess.run(
                'python auto_claude_system.py',
                shell=True,
                capture_output=True,
                text=True,
                input='y\n',
                timeout=60
            )
            
            if result.returncode == 0:
                self.log("✅ Claude自動対話成功")
            else:
                self.log(f"⚠️  Claude自動対話: {result.returncode}")
            
            elapsed = time.time() - start_time
            self.log(f"⏱️  実行時間: {elapsed:.1f}秒")
            
        except subprocess.TimeoutExpired:
            self.log("⏰ タイムアウト")
        except Exception as e:
            self.log(f"❌ 例外: {e}")
    
    def monitor_mode(self):
        """モニターモード（リアルタイム）"""
        self.log("👀 モニターモード開始（リアルタイム）")
        self.log(f"📋 トリガーチェック: {self.check_interval}秒ごと")
        self.log(f"📋 定期実行: {self.interval}秒ごと")
        self.running = True
        
        last_periodic_run = time.time()
        
        try:
            while self.running:
                # トリガーファイルをチェック（即座実行）
                if self.check_trigger_file():
                    self.run_autonomous_system()
                    last_periodic_run = time.time()  # 定期実行タイマーをリセット
                
                # 定期実行のチェック
                elapsed = time.time() - last_periodic_run
                if elapsed >= self.interval:
                    self.log(f"⏰ 定期実行（{self.interval}秒経過）")
                    self.run_autonomous_system()
                    last_periodic_run = time.time()
                
                # 短い間隔でチェック
                time.sleep(self.check_interval)
        
        except KeyboardInterrupt:
            self.log("👋 停止")
            self.running = False
    
    def once_mode(self):
        """1回だけ実行"""
        self.log("🎯 1回実行モード")
        self.run_autonomous_system()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Claude エージェント常駐デーモン')
    parser.add_argument('--monitor', action='store_true', help='モニターモード（常駐）')
    parser.add_argument('--interval', type=int, default=300, help='定期実行間隔（秒）')
    parser.add_argument('--check', type=int, default=5, help='トリガーチェック間隔（秒）')
    parser.add_argument('--once', action='store_true', help='1回だけ実行')
    
    args = parser.parse_args()
    
    daemon = ClaudeAgentDaemon(
        interval=args.interval,
        check_interval=args.check
    )
    
    if args.monitor:
        daemon.monitor_mode()
    elif args.once:
        daemon.once_mode()
    else:
        print("使用方法:")
        print("  python claude_agent_daemon.py --monitor              # リアルタイムモード")
        print("  python claude_agent_daemon.py --monitor --check 2    # 2秒ごとにチェック")
        print("  python claude_agent_daemon.py --once                 # 1回実行")
