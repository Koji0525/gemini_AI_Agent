#!/usr/bin/env python3
"""対話型ダッシュボード"""
from flask import Flask, jsonify, render_template_string, request
from pathlib import Path
import subprocess
import threading
import time
import sys
import json

app = Flask(__name__)
execution_log = []
current_process = None
execution_state = {
    'running': False,
    'pid': None,
    'iteration': 0,
    'max_iterations': 5,
    'commands_executed': []
}

def log_execution(message):
    timestamp = time.strftime('%H:%M:%S')
    log_msg = f"[{timestamp}] {message}"
    execution_log.append(log_msg)
    print(log_msg, flush=True)
    if len(execution_log) > 200:
        execution_log.pop(0)

def run_interactive_agent(instruction=None):
    global current_process, execution_state
    
    execution_state['running'] = True
    execution_state['iteration'] = 0
    execution_state['commands_executed'] = []
    
    log_execution("=" * 70)
    log_execution("🚀 対話型エージェント起動")
    
    try:
        if instruction:
            custom_file = Path('CUSTOM_INSTRUCTION.txt')
            custom_file.write_text(instruction, encoding='utf-8')
            log_execution(f"📝 初期指示: {instruction[:100]}...")
        
        cmd = [sys.executable, 'claude_agent_interactive.py']
        log_execution(f"💻 実行: {' '.join(cmd)}")
        
        current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        execution_state['pid'] = current_process.pid
        log_execution(f"🔢 PID: {current_process.pid}")
        
        # リアルタイム出力読み取り
        for line in iter(current_process.stdout.readline, ''):
            if line:
                log_execution(line.rstrip())
                
                # 反復回数を抽出
                if '🔄 反復' in line:
                    try:
                        execution_state['iteration'] = int(line.split('/')[0].split()[-1])
                    except:
                        pass
                
                # 実行コマンドを記録
                if '💻 実行:' in line:
                    cmd_text = line.split('💻 実行:')[1].strip()
                    execution_state['commands_executed'].append(cmd_text)
        
        current_process.wait()
        
        log_execution(f"✅ 完了（終了コード: {current_process.returncode}）")
        
        current_process = None
        execution_state['running'] = False
        log_execution("🏁 対話型エージェント終了")
        
    except Exception as e:
        log_execution(f"❌ エラー: {e}")
        current_process = None
        execution_state['running'] = False
    
    log_execution("=" * 70)

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>🤖 対話型 Claude Agent</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; padding: 20px; background: linear-gradient(135deg, #667eea, #764ba2); min-height: 100vh; }
        .container { max-width: 1600px; margin: 0 auto; background: white; border-radius: 20px; padding: 30px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
        h1 { color: #667eea; text-align: center; margin-bottom: 30px; }
        
        .progress-bar {
            background: #f0f0f0;
            border-radius: 10px;
            height: 30px;
            margin: 20px 0;
            overflow: hidden;
        }
        .progress-fill {
            background: linear-gradient(90deg, #4CAF50, #45a049);
            height: 100%;
            transition: width 0.5s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
            border-radius: 10px;
            text-align: center;
        }
        .stat-value { font-size: 2em; font-weight: bold; color: #667eea; }
        .stat-label { color: #666; margin-top: 5px; }
        
        button {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            margin: 5px;
            transition: all 0.3s;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
        .btn-run { background: linear-gradient(135deg, #4CAF50, #45a049); color: white; }
        .btn-stop { background: linear-gradient(135deg, #f44336, #da190b); color: white; }
        
        textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 14px;
            min-height: 100px;
            font-family: 'Segoe UI', sans-serif;
        }
        
        .log-section {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            max-height: 600px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
        }
        .log-line { margin: 2px 0; }
        
        .commands-list {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            max-height: 300px;
            overflow-y: auto;
        }
        .command-item {
            padding: 10px;
            background: #e8f5e9;
            border-left: 4px solid #4CAF50;
            margin: 5px 0;
            border-radius: 4px;
            font-family: monospace;
        }
    </style>
    <script>
        function updateUI(data) {
            // 進捗バー
            const progress = (data.state.iteration / data.state.max_iterations) * 100;
            document.getElementById('progressFill').style.width = progress + '%';
            document.getElementById('progressText').textContent = 
                data.state.iteration + '/' + data.state.max_iterations + ' 反復';
            
            // 統計
            document.getElementById('statIteration').textContent = data.state.iteration;
            document.getElementById('statCommands').textContent = data.state.commands_executed.length;
            document.getElementById('statStatus').textContent = data.state.running ? '🔄 実行中' : '✅ 待機中';
            
            // ログ
            const logHtml = data.log.map(line => '<div class="log-line">' + line + '</div>').join('');
            document.getElementById('logSection').innerHTML = logHtml;
            
            // コマンドリスト
            if (data.state.commands_executed.length > 0) {
                const cmdsHtml = data.state.commands_executed.map(cmd => 
                    '<div class="command-item">' + cmd + '</div>'
                ).join('');
                document.getElementById('commandsList').innerHTML = cmdsHtml;
            }
            
            // 自動スクロール
            const logDiv = document.getElementById('logSection');
            logDiv.scrollTop = logDiv.scrollHeight;
        }
        
        function runAgent() {
            const instruction = document.getElementById('instruction').value;
            if (!instruction.trim()) { alert('指示を入力してください'); return; }
            
            fetch('/trigger', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({instruction: instruction})
            }).then(r => r.json()).then(() => {
                document.getElementById('instruction').value = '';
            });
        }
        
        function refresh() {
            fetch('/status').then(r => r.json()).then(updateUI);
        }
        
        setInterval(refresh, 1000);
        window.onload = refresh;
    </script>
</head>
<body>
    <div class="container">
        <h1>🤖 対話型 Claude Agent Dashboard</h1>
        
        <div class="progress-bar">
            <div id="progressFill" class="progress-fill" style="width: 0%">
                <span id="progressText">0/5 反復</span>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="statIteration">0</div>
                <div class="stat-label">現在の反復</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="statCommands">0</div>
                <div class="stat-label">実行コマンド数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="statStatus">✅ 待機中</div>
                <div class="stat-label">ステータス</div>
            </div>
        </div>
        
        <h3>📝 タスク指示（対話型実行）</h3>
        <textarea id="instruction" placeholder="例: safe_browser_manager.py の機能テストを実行して、結果を分析し、改善提案を3つ出してください"></textarea>
        <button class="btn-run" onclick="runAgent()">🚀 対話型実行（最大5反復）</button>
        <button class="btn-stop" onclick="location.reload()">🔄 リセット</button>
        
        <h3>⚙️ 実行されたコマンド</h3>
        <div id="commandsList" class="commands-list">
            <div style="color: #999;">まだ実行されていません</div>
        </div>
        
        <h3>🔍 リアルタイムログ</h3>
        <div id="logSection" class="log-section">読み込み中...</div>
    </div>
</body>
</html>
    ''')

@app.route('/trigger', methods=['POST'])
def trigger():
    if execution_state['running']:
        return jsonify({'status': 'error', 'message': '既に実行中'})
    data = request.json
    threading.Thread(target=run_interactive_agent, args=(data.get('instruction'),)).start()
    return jsonify({'status': 'success'})

@app.route('/status')
def status():
    return jsonify({
        'log': execution_log[-100:],
        'state': execution_state
    })

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🤖 対話型Claudeエージェント Dashboard 起動")
    print("=" * 70)
    print("📍 Codespaces: PORTSタブ → 5001")
    print("=" * 70)
    print("✅ 継続対話: 最大5反復")
    print("✅ リアルタイムログ: 有効")
    print("✅ 進捗表示: 有効")
    print("=" * 70 + "\n")
    app.run(host='0.0.0.0', port=5001, debug=False)
