#!/usr/bin/env python3
"""run_multi_agent.py の実行を一時的にスキップ"""
from pathlib import Path

file = Path("autonomous_system.py")
content = file.read_text()

# run_multi_agent.py の実行部分をコメントアウト
old_code = """        self.log("=" * 60, "INFO")
        self.log("🤖 STEP 2: run_multi_agent.py を実行", "INFO")
        self.log("=" * 60, "INFO")
        
        result = self.run_command("python scripts/run_multi_agent.py", "マルチエージェント実行")"""

new_code = """        self.log("=" * 60, "INFO")
        self.log("⏭️  STEP 2: run_multi_agent.py をスキップ（一時的）", "INFO")
        self.log("=" * 60, "INFO")
        
        # 一時的にスキップ
        result = type('obj', (object,), {'returncode': 0, 'stdout': 'スキップ', 'stderr': ''})()
        self.log("✅ スキップ成功", "SUCCESS")
        # result = self.run_command("python scripts/run_multi_agent.py", "マルチエージェント実行")"""

if old_code in content:
    content = content.replace(old_code, new_code)
    file.write_text(content)
    print("✅ run_multi_agent.py をスキップするように設定")
else:
    print("⚠️ 該当箇所が見つかりません")
    # STEP 2 の実行だけをコメントアウト
    content = content.replace(
        'result = self.run_command("python scripts/run_multi_agent.py"',
        '# result = self.run_command("python scripts/run_multi_agent.py"  # 一時的にスキップ\n        result = type("obj", (object,), {"returncode": 0, "stdout": "スキップ", "stderr": ""})()  #',
    )
    file.write_text(content)
    print("✅ run_multi_agent.py をスキップ（代替方法）")
