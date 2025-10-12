#!/usr/bin/env python3
"""継続的にシステムを監視して自動修正"""
import time
import subprocess

while True:
    print("\n🔄 システムチェック開始...")
    result = subprocess.run(
        "python3 autonomous_agent_system_v2.py",
        shell=True
    )
    
    if result.returncode == 0:
        print("✅ すべて正常")
    else:
        print("⚠️ 問題を検出しました")
    
    print("💤 5分待機...")
    time.sleep(300)  # 5分ごと
