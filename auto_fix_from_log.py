#!/usr/bin/env python3
"""
エラーログから自動修正
"""
import json
import subprocess
from pathlib import Path

# 最新のエラーログを取得
error_logs = sorted(Path("error_logs").glob("errors_*.json"), reverse=True)
latest_log = error_logs[0]

print(f"📋 エラーログ: {latest_log}")

with open(latest_log) as f:
    errors = json.load(f)

print(f"🔍 検出エラー数: {len(errors)}")

# エラー情報をmain_hybrid_fix.pyに渡す
for err in errors:
    print(f"\n🔧 修正試行: {err['task']}")
    error_msg = err['error']
    
    # エラーメッセージを解析
    if "WordPressPostEditor.__init__()" in error_msg and "browser_controller" in error_msg:
        print("   📝 WordPress初期化エラーを検出")
        print("   🔧 wp_agent.pyのWordPressPostEditor初期化部分を修正します")
        
        # fix_wp_agent.pyを実行
        result = subprocess.run(['python', 'fix_wp_agent.py'], capture_output=True, text=True)
        print(result.stdout)
        
        if result.returncode == 0:
            print("   ✅ 自動修正完了")
        else:
            print("   ⚠️ 手動確認が必要です")

print("\n🔄 修正後にテスト再実行...")
result = subprocess.run(['python', 'test_tasks_practical.py'])
exit(result.returncode)
