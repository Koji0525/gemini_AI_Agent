#!/usr/bin/env python3
"""完全版ダッシュボード - 全機能搭載"""
from flask import Flask, jsonify, render_template_string, request
from pathlib import Path
import subprocess
import threading
import time
import sys
import signal
import os

app = Flask(__name__)
execution_log = []
current_process = None
execution_state = {
    'running': False,
    'pid': None,
    'iteration': 0,
    'max_iterations': 10,
    'commands_executed': [],
    'successful': 0,
    'failed': 0
}

def log_execution(message):
    timestamp = time.strftime('%H:%M:%S')
    log_msg = f"[{timestamp}] {message}"
    execution_log.append(log_msg)
    print(log_msg, flush=True)
    if len(execution_log) > 300:
        execution_log.pop(0)

def run_intelligent_agent(instruction, max_iterations):
    global current_process, execution_state
    
    execution_state['running'] = True
    execution_state['iteration'] = 0
    execution_state['max_iterations'] = max_iterations
    execution_state['commands_executed'] = []
    execution_state['successful'] = 0
    execution_state['failed'] = 0
    
    log_execution("=" * 70)
    log_execution(f"�� インテリジェントエージェント起動（最大{max_iterations}反復）")
    
    try:
        custom_file = Path('CUSTOM_INSTRUCTION.txt')
        custom_file.write_text(instruction, encoding='utf-8')
        log_execution(f"📝 指示: {instruction[:100]}...")
        
        cmd = [sys.executable, 'claude_agent_intelligent.py', str(max_iterations)]
        log_execution(f"💻 実行: {' '.join(cmd)}")
        
        current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            preexec_fn=os.setsid if hasattr(os, 'setsid') else None
        )
        
        execution_state['pid'] = current_process.pid
        log_execution(f"🔢 PID: {current_process.pid}")
        
        # リアルタイム出力
        for line in iter(current_process.stdout.readline, ''):
            if line:
                log_execution(line.rstrip())
                
                # 統計更新
                if '🔄 反復' in line:
                    try:
                        parts = line.split('/')
                        execution_state['iteration'] = int(parts[0].split()[-1])
                    except:
                        pass
                
                if '💻 実行:' in line:
                    cmd_text = line.split('💻 実行:')[1].strip()
                    execution_state['commands_executed'].append(cmd_text)
                
                if '✅ 成功' in line:
                    execution_state['successful'] += 1
                
                if '❌ エラー' in line:
                    execution_state['failed'] += 1
        
        current_process.wait()
        log_execution(f"✅ 完了（終了コード: {current_process.returncode}）")
        
    except Exception as e:
        log_execution(f"❌ エラー: {e}")
    finally:
        current_process = None
        execution_state['running'] = False
        log_execution("=" * 70)

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>🤖 Intelligent Claude Agent</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container { 
            max-width: 1600px; 
            margin: 0 auto; 
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        h1 {
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        
        .progress-section {
            background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 25px;
        }
        
        .progress-bar {
            background: #e0e0e0;
            border-radius: 10px;
            height: 40px;
            overflow: hidden;
            margin: 15px 0;
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
            font-size: 1.1em;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .stat-card {
            padding: 20px;
            background: white;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stat-value { 
            font-size: 2.5em; 
            font-weight: bold; 
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stat-label { color: #666; margin-top: 8px; font-size: 0.9em; }
        
        .controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 12px;
            margin: 25px 0;
        }
        button {
            padding: 14px 20px;
            border: none;
            border-radius: 10px;
            font-size: 15px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        button:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 6px 12px rgba(0,0,0,0.2); 
        }
        button:active { transform: translateY(0); }
        button:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        
        .btn-run { background: linear-gradient(135deg, #4CAF50, #45a049); color: white; }
        .btn-stop { background: linear-gradient(135deg, #f44336, #da190b); color: white; }
        .btn-refresh { background: linear-gradient(135deg, #2196F3, #0b7dda); color: white; }
        
        .input-section {
            background: #f9f9f9;
            padding: 25px;
            border-radius: 15px;
            margin: 25px 0;
        }
        .input-section h3 { 
            color: #333; 
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .input-group {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 15px;
            margin: 15px 0;
        }
        
        input[type="number"] {
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            width: 100%;
        }
        
        textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 15px;
            font-family: 'Segoe UI', sans-serif;
            resize: vertical;
            min-height: 120px;
            transition: border 0.3s;
        }
        textarea:focus, input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .commands-section {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
            max-height: 350px;
            overflow-y: auto;
        }
        .commands-section h3 { color: #667eea; margin-bottom: 15px; }
        
        .command-item {
            padding: 12px 15px;
            background: #e8f5e9;
            border-left: 4px solid #4CAF50;
            margin: 8px 0;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 0.95em;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .log-section {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
            max-height: 600px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.7;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
        }
        .log-section h3 { 
            color: #4ec9b0; 
            margin-bottom: 15px;
            font-family: 'Segoe UI', sans-serif;
        }
        .log-line { margin: 3px 0; }
        
        .status-badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }
        .badge-running { background: #4CAF50; color: white; animation: pulse 1.5s infinite; }
        .badge-idle { background: #2196F3; color: white; }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .alert {
            padding: 15px 20px;
            border-radius: 8px;
            margin: 15px 0;
        }
        .alert-info { background: #e3f2fd; border-left: 4px solid #2196F3; color: #0d47a1; }
        .alert-success { background: #e8f5e9; border-left: 4px solid #4CAF50; color: #1b5e20; }
    </style>
    <script>
        let autoRefresh = null;
        
        function updateUI(data) {
            const state = data.state;
            
            // 進捗バー
            const progress = state.max_iterations > 0 
                ? (state.iteration / state.max_iterations) * 100 
                : 0;
            document.getElementById('progressFill').style.width = progress + '%';
            document.getElementById('progressText').textContent = 
                state.iteration + ' / ' + state.max_iterations + ' 反復';
            
            // 統計
            document.getElementById('statIteration').textContent = state.iteration;
            document.getElementById('statMax').textContent = state.max_iterations;
            document.getElementById('statCommands').textContent = state.commands_executed.length;
            document.getElementById('statSuccess').textContent = state.successful;
            document.getElementById('statFailed').textContent = state.failed;
            
            // ステータスバッジ
            const badge = document.getElementById('statusBadge');
            if (state.running) {
                badge.className = 'status-badge badge-running';
                badge.textContent = '🔄 実行中';
                document.getElementById('runBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
            } else {
                badge.className = 'status-badge badge-idle';
                badge.textContent = '✅ 待機中';
                document.getElementById('runBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
            }
            
            // コマンドリスト
            const cmdsDiv = document.getElementById('commandsList');
            if (state.commands_executed.length > 0) {
                cmdsDiv.innerHTML = state.commands_executed
                    .slice(-15)  // 最新15件
                    .map((cmd, i) => `
                        <div class="command-item">
                            <span>${cmd}</span>
                            <span style="color: #666; font-size: 0.85em;">#${state.commands_executed.length - 14 + i}</span>
                        </div>
                    `).join('');
            } else {
                cmdsDiv.innerHTML = '<div style="color: #999; text-align: center; padding: 20px;">まだコマンドが実行されていません</div>';
            }
            
            // ログ
            const logDiv = document.getElementById('logSection');
            logDiv.innerHTML = data.log
                .slice(-100)  // 最新100行
                .map(line => '<div class="log-line">' + line + '</div>')
                .join('');
            
            // 自動スクロール
            logDiv.scrollTop = logDiv.scrollHeight;
        }
        
        function runAgent() {
            const instruction = document.getElementById('instruction').value.trim();
            const maxIter = parseInt(document.getElementById('maxIterations').value);
            
            if (!instruction) {
                alert('タスク指示を入力してください');
                return;
            }
            
            if (maxIter < 1 || maxIter > 20) {
                alert('最大反復回数は1〜20の範囲で指定してください');
                return;
            }
            
            fetch('/trigger', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    instruction: instruction,
                    max_iterations: maxIter
                })
            }).then(r => r.json()).then(data => {
                if (data.status === 'success') {
                    document.getElementById('instruction').value = '';
                }
            });
        }
        
        function emergencyStop() {
            if (!confirm('実行中のプロセスを強制終了しますか？\\n\\n注意: 実行中のコマンドも中断されます。')) {
                return;
            }
            
            fetch('/emergency_stop').then(r => r.json()).then(data => {
                alert(data.message);
            });
        }
        
        function refresh() {
            fetch('/status').then(r => r.json()).then(updateUI);
        }
        
        function toggleAutoRefresh() {
            const btn = document.getElementById('autoRefreshBtn');
            if (autoRefresh) {
                clearInterval(autoRefresh);
                autoRefresh = null;
                btn.textContent = '▶️ 自動更新';
                btn.style.background = 'linear-gradient(135deg, #2196F3, #0b7dda)';
            } else {
                autoRefresh = setInterval(refresh, 1500);
                btn.textContent = '⏸️ 自動更新中';
                btn.style.background = 'linear-gradient(135deg, #FF9800, #fb8c00)';
            }
        }
        
        // 初期化
        window.onload = function() {
            refresh();
            // デフォルトで自動更新ON
            toggleAutoRefresh();
        };
    </script>
</head>
<body>
    <div class="container">
        <h1>🤖 Intelligent Claude Agent</h1>
        
        <div class="progress-section">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h3 style="margin: 0;">実行進捗</h3>
                <span id="statusBadge" class="status-badge badge-idle">待機中</span>
            </div>
            
            <div class="progress-bar">
                <div id="progressFill" class="progress-fill" style="width: 0%">
                    <span id="progressText">0 / 10 反復</span>
                </div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value" id="statIteration">0</div>
                    <div class="stat-label">現在の反復</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="statMax">10</div>
                    <div class="stat-label">最大反復</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="statCommands">0</div>
                    <div class="stat-label">総コマンド数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="statSuccess">0</div>
                    <div class="stat-label">成功</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="statFailed">0</div>
                    <div class="stat-label">失敗</div>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <button id="runBtn" class="btn-run" onclick="runAgent()">🚀 実行開始</button>
            <button id="stopBtn" class="btn-stop" onclick="emergencyStop()" disabled>🛑 緊急停止</button>
            <button class="btn-refresh" onclick="refresh()">🔄 更新</button>
            <button id="autoRefreshBtn" class="btn-refresh" onclick="toggleAutoRefresh()">▶️ 自動更新</button>
        </div>
        
        <div class="input-section">
            <h3>📝 タスク設定</h3>
            
            <div class="alert alert-info">
                <strong>💡 使い方:</strong> エラーが発生した場合、Claudeが自動的に分析・修正・再実行します。最大反復回数まで繰り返します。
            </div>
            
            <div class="input-group">
                <div>
                    <label style="display: block; margin-bottom: 8px; font-weight: bold; color: #555;">最大反復回数 (1-20)</label>
                    <input type="number" id="maxIterations" min="1" max="20" value="10" 
                           style="width: 150px;" placeholder="10">
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                <label style="display: block; margin-bottom: 8px; font-weight: bold; color: #555;">タスク指示</label>
                <textarea id="instruction" 
                          placeholder="例:&#10;safe_browser_manager.py の機能テストを実行してください。&#10;エラーが発生した場合は原因を特定し、修正して再実行してください。&#10;すべてのテストが成功するまで繰り返してください。"></textarea>
            </div>
        </div>
        
        <div class="commands-section">
            <h3>⚙️ 実行コマンド履歴</h3>
            <div id="commandsList">
                <div style="color: #999; text-align: center; padding: 20px;">まだコマンドが実行されていません</div>
            </div>
        </div>
        
        <div class="log-section">
            <h3>🔍 リアルタイム実行ログ</h3>
            <div id="logSection">読み込み中...</div>
        </div>
    </div>
</body>
</html>
    ''')

@app.route('/trigger', methods=['POST'])
def trigger():
    if execution_state['running']:
        return jsonify({'status': 'error', 'message': '既に実行中です'})
    
    data = request.json
    instruction = data.get('instruction', '')
    max_iterations = int(data.get('max_iterations', 10))
    
    threading.Thread(
        target=run_intelligent_agent,
        args=(instruction, max_iterations)
    ).start()
    
    return jsonify({'status': 'success'})

@app.route('/emergency_stop')
def emergency_stop():
    global current_process
    
    if current_process and current_process.poll() is None:
        try:
            # プロセスグループ全体を終了
            if hasattr(os, 'killpg'):
                os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
            else:
                current_process.terminate()
            
            log_execution("🛑 緊急停止: プロセスを終了しました")
            current_process = None
            execution_state['running'] = False
            
            return jsonify({'status': 'success', 'message': '🛑 プロセスを強制終了しました'})
        except Exception as e:
            log_execution(f"停止エラー: {e}")
            return jsonify({'status': 'error', 'message': f'エラー: {e}'})
    
    return jsonify({'status': 'info', 'message': '実行中のプロセスはありません'})

@app.route('/status')
def status():
    return jsonify({
        'log': execution_log[-150:],
        'state': execution_state
    })

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🤖 Intelligent Claude Agent Dashboard 起動")
    print("=" * 70)
    print("📍 Codespaces: PORTSタブ → 5001")
    print("=" * 70)
    print("✅ エラー自動修正: 有効")
    print("✅ 継続対話: 有効")
    print("✅ 反復回数指定: 1-20回")
    print("✅ 緊急停止: 有効")
    print("=" * 70 + "\n")
    app.run(host='0.0.0.0', port=5001, debug=False)
