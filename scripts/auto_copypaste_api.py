#!/usr/bin/env python3
import os, sys, subprocess, time, re
from datetime import datetime

try:
    import google.generativeai as genai
except:
    print("ERROR: google-generativeai not installed")
    sys.exit(1)

class Bot:
    def __init__(self):
        self.key = os.getenv('GEMINI_API_KEY')
        self.pat = os.getenv('GITHUB_PAT')
        self.cs = os.getenv('CODESPACE_NAME')
        self.task = os.getenv('TASK', 'echo hello')
        self.max = int(os.getenv('MAX_ITERATIONS', '3'))
        if not all([self.key, self.pat, self.cs]):
            raise ValueError("Missing env vars")
        genai.configure(api_key=self.key)
        self.model = genai.GenerativeModel('gemini-pro')
        print(f"Task: {self.task}")
    
    def ask(self, msg):
        try:
            return self.model.generate_content(msg).text
        except Exception as e:
            return f"Error: {e}"
    
    def exec(self, cmd):
        try:
            r = subprocess.run(['gh', 'codespace', 'ssh', '-c', self.cs, '--', cmd],
                             capture_output=True, text=True, timeout=120,
                             env={**os.environ, 'GH_TOKEN': self.pat})
            return {'cmd': cmd, 'code': r.returncode, 'out': r.stdout, 'err': r.stderr}
        except Exception as e:
            return {'cmd': cmd, 'code': -1, 'out': '', 'err': str(e)}
    
    def cmds(self, txt):
        cs = []
        for m in re.findall(r'```(?:bash|sh)\n(.*?)```', txt, re.S|re.I):
            for l in m.strip().split('\n'):
                l = l.strip()
                if l and not l.startswith('#'):
                    cs.append(l)
        return cs
    
    def run(self):
        msg = f"{self.task}\n\nProvide bash commands in ```bash blocks."
        for i in range(1, self.max + 1):
            print(f"\n=== Iteration {i}/{self.max} ===")
            resp = self.ask(msg)
            cmds = self.cmds(resp)
            if not cmds:
                print("No commands found")
                break
            print(f"Commands: {len(cmds)}")
            res = []
            for c in cmds:
                r = self.exec(c)
                res.append(f"Cmd: {c}\nCode: {r['code']}\nOut: {r['out'][:500]}")
                time.sleep(1)
            msg = f"Results:\n{chr(10).join(res)}\n\nNext steps in ```bash or say done."
        print("\n=== Completed ===")
        with open('results.txt', 'w') as f:
            f.write("Task completed\n")

if __name__ == "__main__":
    Bot().run()
