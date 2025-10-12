#!/usr/bin/env python3
import subprocess
from pathlib import Path
from datetime import datetime

results = []
for cmd in Path('commands.txt').read_text().strip().split('\n'):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    results.append(f"$ {cmd}\n{r.stdout}\n")

prompt = f"【実行結果】\n" + "\n".join(results) + "\n次のコマンドを提案:"
fname = f"claude_prompt_{datetime.now().strftime('%H%M%S')}.txt"
Path(fname).write_text(prompt, encoding='utf-8')
print(f"✅ {fname}")
print(prompt)
