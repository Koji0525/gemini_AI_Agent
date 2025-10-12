#!/usr/bin/env python3
"""
エラーログから自動修正を起動
"""
import json
import subprocess
from pathlib import Path

# 最新のエラーログを取得
error_logs = sorted(Path("error_logs").glob("errors_*.json"), reverse=True)

if not error_logs:
    print("❌ エラーログが見つかりません")
    exit(1)

latest_log = error_logs[0]
print(f"📋 最新エラーログ: {latest_log}")

with open(latest_log) as f:
    errors = json.load(f)

print(f"🔍 検出エラー数: {len(errors)}")

for err in errors:
    print(f"\n🔧 修正試行: {err['task']}")
    print(f"   エラー内容: {err['error']}")
    
    # main_hybrid_fix.py を起動
    result = subprocess.run(
        ['python', 'main_hybrid_fix.py', '--error', err['error']],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("   ✅ 修正成功")
    else:
        print("   ❌ 修正失敗")

print("\n🔄 修正後に再テスト")
subprocess.run(['python', 'test_tasks_practical.py'])
