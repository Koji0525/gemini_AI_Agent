#!/usr/bin/env python3
import subprocess
from pathlib import Path
from datetime import datetime

# 最新のログファイルを取得
log_files = sorted(Path('logs').glob('*.log'), key=lambda x: x.stat().st_mtime, reverse=True)
if log_files:
    latest_log = log_files[0]
    content = latest_log.read_text()
    
    # エラー行を抽出
    error_lines = [line for line in content.split('\n') if 'ERROR' in line or 'Traceback' in line]
    
    prompt = f"""
【エラー検出】
ファイル: {latest_log}

【エラー内容】
{''.join(error_lines[-20:])}

【完全ログ（最後の50行）】
{chr(10).join(content.split(chr(10))[-50:])}

次の修正コマンドを ```bash で提案:
"""
    
    fname = f"claude_error_{datetime.now().strftime('%H%M%S')}.txt"
    Path(fname).write_text(prompt, encoding='utf-8')
    print(f"✅ エラープロンプト生成: {fname}")
    print(prompt)
else:
    print("❌ ログファイルが見つかりません")
