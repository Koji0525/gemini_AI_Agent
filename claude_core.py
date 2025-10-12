#!/usr/bin/env python3
import subprocess, sys, re
from pathlib import Path
from datetime import datetime

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"$ {cmd}\n{r.stdout}")
    return r.stdout, r.returncode == 0

def save(text, name="output"):
    f = f"{name}_{datetime.now().strftime('%H%M%S')}.txt"
    Path(f).write_text(text, encoding='utf-8')
    print(f"✅ 保存: {f}")
    return f

def extract_commands(text):
    cmds = []
    for m in re.finditer(r'```bash\n(.*?)```', text, re.DOTALL):
        for line in m.group(1).split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                cmds.append(line)
    return cmds

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmds = extract_commands(Path(sys.argv[1]).read_text())
        print(f"🔍 {len(cmds)}個")
        for i, c in enumerate(cmds, 1):
            print(f"{i}. {c}")
        if input("実行? (y/n): ").lower() == 'y':
            for c in cmds:
                run(c)
    else:
        out, _ = run("ls -la | head -20")
        prompt = f"【結果】\n{out}\n\n次のコマンドを ```bash で:"
        save(prompt, "claude_prompt")
