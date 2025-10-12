#!/usr/bin/env python3
"""完全デバッグ版Dashboard"""
from flask import Flask, jsonify, render_template_string, request
from pathlib import Path
import subprocess
import threading
import time
import sys

app = Flask(__name__)

# グローバル実行状態
execution_log = []
current_execution = None

def log_execution(message):
    """実行ログを記録"""
    timestamp = time.strftime('%H:%M:%S')
    log_msg = f"[{timestamp}] {message}"
    execution_log.append(log_msg)
    print(log_msg)
    if len(execution_log) > 100:
        execution_log.pop(0)

def run_agent(instruction=None):
    """エージェント実行"""
    global current_execution
    
    log_execution("=" * 70)
    log_execution("🚀 実行開始")
    
    try:
        # カスタム指示ファイル作成
        if instruction:
            custom_file = Path('CUSTOM_INSTRUCTION.txt')
            custom_file.write_text(instruction, encoding='utf-8')
            log_execution(f"📝 カスタム指示ファイル作成: {custom_file.absolute()}")
            log_execution(f"内容: {instruction[:100]}...")
        
        # Python実行
        cmd = [sys.executable, 'claude_unified_agent_fixed.py']
        log_execution(f"💻 実行コマンド: {' '.join(cmd)}")
        
        current_execution = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        log_execution(f"🔢 プロセスID: {current_execution.pid}")
        
        # 実行完了を待つ
        stdout, stderr = current_execution.communicate(timeout=120)
        
        log_execution(f"✅ 実行完了（終了コード: {current_execution.returncode}）")
        
        if stdout:
            log_execution(f"📤 標準出力（最初の500文字）:\n{stdout[:500]}")
        
        if stderr:
            log_execution(f"⚠️ 標準エラー:\n{stderr[:500]}")
        
        # ログファイル確認
        log_file = Path('logs/unified_conversation.log')
        if log_file.exists():
            mtime = time.strftime('%H:%M:%S', time.localtime(log_file.stat().st_mtime))
            log_execution(f"📋 ログファイル更新時刻: {mtime}")
        
        current_execution = None
        log_execution("🏁 実行終了")
        
    except subprocess.TimeoutExpired:
        log_execution("⏰ タイムアウト（120秒）")
        if current_execution:
            current_execution.kill()
        current_execution = None
    
    except Exception as e:
        log_execution(f"❌ エラー: {type(e).__name__}: {e}")
        import traceback
        log_execution(f"詳細:\n{traceback.format_exc()}")
        current_execution = None
    
    log_execution("=" * 70)

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>🐛 Debug Dashboard</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: monospace; padding: 20px; background: #1e1e1e; color: #d4d4d4; }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { color: #4ec9b0; }
        button { 
            padding: 10px 20px; 
            margin: 5px; 
            font-size: 14px; 
            cursor: pointer;
            background: #007acc;
            color: white;
            border: none;
            border-radius: 5px;
        }
        button:hover { background: #005a9e; }
        textarea { 
            width: 100%; 
            padding: 10px; 
            font-family: monospace; 
            background: #252526;
            color: #d4d4d4;
            border: 1px solid #3e3e42;
        }
        .log-box {
            background: #252526;
            border: 1px solid #3e3e42;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
            max-height: 400px;
            overflow-y: auto;
        }
        pre { margin: 0; white-space: pre-wrap; word-wrap: break-word; }
        .timestamp { color: #858585; }
        .success { color: #4ec9b0; }
        .error { color: #f48771; }
        .warning { color: #ce9178; }
    </style>
    <script>
        function runSystem() {
            fetch('/trigger').then(r => r.json()).then(data => {
                setTimeout(refreshLogs, 2000);
            });
        }
        
        function runWithInstruction() {
            const instruction = document.getElementById('instruction').value;
            if (!instruction.trim()) { alert('指示を入力'); return; }
            
            fetch('/trigger_with_instruction', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({instruction: instruction})
            }).then(r => r.json()).then(data => {
                document.getElementById('instruction').value = '';
                setTimeout(refreshLogs, 2000);
            });
        }
        
        function refreshLogs() {
            fetch('/debug_status').then(r => r.json()).then(data => {
                document.getElementById('execution_log').innerHTML = 
                    '<pre>' + data.execution_log.join('\\n') + '</pre>';
                document.getElementById('file_log').innerHTML = 
                    '<pre>' + data.file_log + '</pre>';
            });
        }
        
        setInterval(refreshLogs, 2000);
        window.onload = refreshLogs;
    </script>
</head>
<body>
    <div class="container">
        <h1>🐛 Claude Agent Debug Dashboard</h1>
        
        <div>
            <button onclick="runSystem()">🚀 実行</button>
            <button onclick="refreshLogs()">🔄 更新</button>
        </div>
        
        <h3>📝 カスタム指示:</h3>
        <textarea id="instruction" rows="3" placeholder="テスト用の簡単な指示を入力"></textarea>
        <button onclick="runWithInstruction()">📤 実行</button>
        
        <h3>🔍 実行ログ（メモリ内）:</h3>
        <div id="execution_log" class="log-box">読み込み中...</div>
        
        <h3>📋 ファイルログ（最新30行）:</h3>
        <div id="file_log" class="log-box">読み込み中...</div>
    </div>
</body>
</html>
    ''')

@app.route('/trigger')
def trigger():
    thread = threading.Thread(target=run_agent)
    thread.start()
    return jsonify({'status': 'success'})

@app.route('/trigger_with_instruction', methods=['POST'])
def trigger_with_instruction():
    data = request.json
    instruction = data.get('instruction', '')
    thread = threading.Thread(target=run_agent, args=(instruction,))
    thread.start()
    return jsonify({'status': 'success'})

@app.route('/debug_status')
def debug_status():
    log_file = Path('logs/unified_conversation.log')
    file_log = ''
    
    if log_file.exists():
        try:
            lines = log_file.read_text(encoding='utf-8').split('\n')
            file_log = '\n'.join(lines[-30:])
        except Exception as e:
            file_log = f"エラー: {e}"
    else:
        file_log = "ログファイルなし"
    
    return jsonify({
        'execution_log': execution_log[-50:],
        'file_log': file_log
    })

if __name__ == '__main__':
    print("=" * 70)
    print("🐛 デバッグダッシュボード起動")
    print("=" * 70)
    print("📍 http://localhost:5001")
    print("=" * 70)
    app.run(host='0.0.0.0', port=5001, debug=False)
