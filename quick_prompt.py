#!/usr/bin/env python3
import subprocess
from datetime import datetime

# 直近のコマンドを実行
result = subprocess.run(
    "python autonomous_system.py --test-only",
    shell=True,
    capture_output=True,
    text=True
)

# 簡潔なプロンプトを生成
prompt = f"""
【{datetime.now().strftime('%H:%M')}】実行結果

{result.stdout[-500:]}

{'✅ 成功' if result.returncode == 0 else '❌ エラー'}

次のコマンドを提案:
"""

print(prompt)

with open(f"quick_{datetime.now().strftime('%H%M')}.txt", 'w') as f:
    f.write(prompt)
