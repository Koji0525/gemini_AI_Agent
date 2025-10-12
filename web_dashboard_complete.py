#!/usr/bin/env python3
"""完全版Dashboard（緊急停止・実行詳細表示）"""
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
execution_details = {
    'running': False,
    'pid': None,
    'start_time': None,
    'commands_executed': []
}

def log_execution(message):
    timestamp = time.strftime('%H:%M:%S')
    log_msg = f"[{timestamp}] {message}"
    execution_log.append(log_msg)
    print(log_msg, flush=True)
    if len(execution_log) > 150:
        execution_log.pop(0)

def run_agent(instruction=None):
    global current_process, execution_details
    
    execution_details['running'] = True
    execution_details['start_time'] = time.strftime('%H:%M:%S')
    execution_details['commands_executed'] = []
    
    log_execution("=" * 70)
    log_execution("🚀 実行開始")
    
    try:
        if instruction:
            custom_file = Path('CUSTOM_INSTRUCTION.txt')
            custom_file.write_text(instruction, encoding='utf-8')
            log_execution(f"📝 カスタム指示: {instruction[:100]}...")
        
        cmd = [sys.executable, 'claude_unified_agent_fixed.py']
        log_execution(f"💻 コマンド: {' '.join(cmd)}")
        
        current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        execution_details['pid'] = current_process.pid
        log_execution(f"🔢 プロセスID: {current_process.pid}")
        
        stdout, stderr = current_process.communicate(timeout=120)
        
        log_execution(f"✅ 完了（終了コード: {current_process.returncode}）")
        
        # 実行されたコマンドをログから抽出
        if '$ ' in stdout:
            commands = [line.split('$ ')[1] for line in stdout.split('\n') if '$ ' in line]
            execution_details['commands_executed'] = commands[:10]  # 最大10個
            log_execution(f"📋 実行コマンド数: {len(commands)}")
        
        if stdout:
            log_execution(f"📤 出力: {stdout[:500]}")
        
        if stderr:
            log_execution(f"⚠️ エラー: {stderr[:500]}")
        
        current_process = None
        execution_details['running'] = False
        log_execution("�� 実行終了")
        
    except subprocess.TimeoutExpired:
        log_execution("⏰ タイムアウト（120秒）")
        if current_process:
            current_process.kill()
        current_process = None
        execution_details['running'] = False
    
    except Exception as e:
        log_execution(f"❌ エラー: {e}")
        current_process = None
        execution_details['running'] = False
    
    log_execution("=" * 70)

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>🤖 Claude Agent Dashboard</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; padding: 20px; background: linear-gradient(135deg, #667eea, #764ba2); min-height: 100vh; }
        .container { max-width: 1400px; margin: 0 auto; background: white; border-radius: 20px; padding: 30px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
        h1 { color: #667eea; text-align: center; margin-bottom: 30px; }
        
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .status-badge {
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }
        .status-running { background: #4CAF50; color: white; animation: pulse 1.5s infinite; }
        .status-idle { background: #2196F3; color: white; }
        
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
        
        .controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-bottom: 20px;
        }
        button {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
        button:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        
        .btn-run { background: linear-gradient(135deg, #4CAF50, #45a049); color: white; }
        .btn-stop { background: linear-gradient(135deg, #f44336, #da190b); color: white; }
        .btn-refresh { background: linear-gradient(135deg, #2196F3, #0b7dda); color: white; }
        
        .instruction-box {
            margin: 20px 0;
            padding: 20px;
            background: #f5f7fa;
            border-radius: 10px;
        }
        .instruction-box h3 { margin-bottom: 10px; color: #333; }
        textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            font-family: 'Segoe UI', sans-serif;
            resize: vertical;
            min-height: 80px;
        }
        textarea:focus { outline: none; border-color: #667eea; }
        
        .execution-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .detail-card {
            padding: 15px;
            background: white;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .detail-label { font-size: 0.85em; color: #666; margin-bottom: 5px; }
        .detail-value { font-size: 1.2em; font-weight: bold; color: #667eea; }
        
        .log-section {
            background: #f9f9f9;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            max-height: 500px;
            overflow-y: auto;
        }
        .log-section h3 { color: #667eea; margin-bottom: 15px; }
        pre {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 13px;
            line-height: 1.6;
        }
        
        .commands-list {
            list-style: none;
            padding: 0;
        }
        .commands-list li {
            padding: 8px 12px;
            background: #e8f5e9;
            border-left: 4px solid #4CAF50;
            margin: 5px 0;
            border-radius: 4px;
            font-family: monospace;
            font-size: 0.9em;
        }
    </style>
    <script>
        let autoRefresh = null;
        
        function updateStatus(data) {
            const badge = document.getElementById('statusBadge');
            const pid = document.getElementById('pidValue');
            const startTime = document.getElementById('startTimeValue');
            const commandsCount = document.getElementById('commandsValue');
            
            if (data.execution_details.running) {
                badge.className = 'status-badge status-running';
                badge.textContent = '🔄 実行中';
            } else {
                badge.className = 'status-badge status-idle';
                badge.textContent = '✅ 待機中';
            }
            
            pid.textContent = data.execution_details.pid || '-';
            startTime.textContent = data.execution_details.start_time || '-';
            commandsCount.textContent = data.execution_details.commands_executed.length;
            
            // 実行コマンドリスト
            const commandsList = document.getElementById('commandsList');
            if (data.execution_details.commands_executed.length > 0) {
                commandsList.innerHTML = data.execution_details.commands_executed
                    .map(cmd => '<li>' + cmd + '</li>')
                    .join('');
            } else {
                commandsList.innerHTML = '<li style="background:#f5f5f5; border-color:#ddd;">コマンドなし</li>';
            }
        }
        
        function runSystem() {
            document.getElementById('runBtn').disabled = true;
            fetch('/trigger').then(r => r.json()).then(() => {
                setTimeout(() => {
                    refresh();
                    document.getElementById('runBtn').disabled = false;
                }, 3000);
            });
        }
        
        function runCustom() {
            const text = document.getElementById('instruction').value;
            if (!text.trim()) { alert('指示を入力してください'); return; }
            
            document.getElementById('runBtn').disabled = true;
            fetch('/trigger_custom', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({instruction: text})
            }).then(r => r.json()).then(() => {
                document.getElementById('instruction').value = '';
                setTimeout(() => {
                    refresh();
                    document.getElementById('runBtn').disabled = false;
                }, 3000);
            });
        }
        
        function emergencyStop() {
            if (!confirm('実行中のプロセスを強制終了しますか？')) return;
            
            fetch('/emergency_stop').then(r => r.json()).then(data => {
                alert(data.message);
                refresh();
            });
        }
        
        function refresh() {
            fetch('/status').then(r => r.json()).then(data => {
                updateStatus(data);
                
                document.getElementById('executionLog').innerHTML = 
                    '<pre>' + data.execution_log.join('\\n') + '</pre>';
                
                if (data.file_log) {
                    document.getElementById('fileLog').innerHTML = 
                        '<pre>' + data.file_log + '</pre>';
                }
            });
        }
        
        function toggleAutoRefresh() {
            const btn = document.getElementById('autoRefreshBtn');
            if (autoRefresh) {
                clearInterval(autoRefresh);
                autoRefresh = null;
                btn.textContent = '▶️ 自動更新';
            } else {
                autoRefresh = setInterval(refresh, 2000);
                btn.textContent = '⏸️ 自動更新中';
            }
        }
        
        window.onload = refresh;
    </script>
</head>
<body>
    <div class="container">
        <h1>🤖 Claude Agent Dashboard</h1>
        
        <div class="status-bar">
            <span id="statusBadge" class="status-badge status-idle">待機中</span>
            <span style="color: #666;">ポート: 5001 | 統合エージェント</span>
        </div>
        
        <div class="execution-details">
            <div class="detail-card">
                <div class="detail-label">プロセスID</div>
                <div class="detail-value" id="pidValue">-</div>
            </div>
            <div class="detail-card">
                <div class="detail-label">開始時刻</div>
                <div class="detail-value" id="startTimeValue">-</div>
            </div>
            <div class="detail-card">
                <div class="detail-label">実行コマンド数</div>
                <div class="detail-value" id="commandsValue">0</div>
            </div>
        </div>
        
        <div class="controls">
            <button id="runBtn" class="btn-run" onclick="runSystem()">🚀 実行</button>
            <button class="btn-stop" onclick="emergencyStop()">🛑 緊急停止</button>
            <button class="btn-refresh" onclick="refresh()">🔄 更新</button>
            <button id="autoRefreshBtn" class="btn-refresh" onclick="toggleAutoRefresh()">▶️ 自動更新</button>
        </div>
        
        <div class="instruction-box">
            <h3>📝 カスタム指示</h3>
            <textarea id="instruction" placeholder="例: safe_browser_manager.py の機能テストを実行してください"></textarea>
            <button class="btn-run" onclick="runCustom()" style="width: 100%; margin-top: 10px;">📤 指示付きで実行</button>
        </div>
        
        <div class="log-section">
            <h3>⚙️ 実行されたコマンド</h3>
            <ul id="commandsList" class="commands-list">
                <li style="background:#f5f5f5; border-color:#ddd;">まだ実行されていません</li>
            </ul>
        </div>
        
        <div class="log-section">
            <h3>🔍 実行ログ（メモリ内）</h3>
            <div id="executionLog">読み込み中...</div>
        </div>
        
        <div class="log-section">
            <h3>📋 ファイルログ（最新30行）</h3>
            <div id="fileLog">読み込み中...</div>
        </div>
    </div>
</body>
</html>
    ''')

@app.route('/trigger')
def trigger():
    if execution_details['running']:
        return jsonify({'status': 'error', 'message': '既に実行中です'})
    threading.Thread(target=run_agent).start()
    return jsonify({'status': 'success'})

@app.route('/trigger_custom', methods=['POST'])
def trigger_custom():
    if execution_details['running']:
        return jsonify({'status': 'error', 'message': '既に実行中です'})
    data = request.json
    threading.Thread(target=run_agent, args=(data.get('instruction'),)).start()
    return jsonify({'status': 'success'})

@app.route('/emergency_stop')
def emergency_stop():
    global current_process
    if current_process and current_process.poll() is None:
        try:
            # プロセスグループ全体を終了
            os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
            log_execution("🛑 緊急停止: プロセスを終了しました")
            current_process = None
            execution_details['running'] = False
            return jsonify({'status': 'success', 'message': '🛑 プロセスを強制終了しました'})
        except Exception as e:
            log_execution(f"⚠️ 停止エラー: {e}")
            return jsonify({'status': 'error', 'message': f'エラー: {e}'})
    return jsonify({'status': 'info', 'message': '実行中のプロセスはありません'})

@app.route('/status')
def status():
    log_file = Path('logs/unified_conversation.log')
    file_log = ''
    
    if log_file.exists():
        try:
            lines = log_file.read_text(encoding='utf-8').split('\n')
            file_log = '\n'.join(lines[-30:])
        except Exception as e:
            file_log = f"エラー: {e}"
    
    return jsonify({
        'execution_log': execution_log[-80:],
        'file_log': file_log,
        'execution_details': execution_details
    })

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🤖 Claude Agent Dashboard（完全版）起動")
    print("=" * 70)
    print("📍 Codespaces: PORTSタブ → 5001")
    print("=" * 70)
    print("✅ 緊急停止ボタン: 追加済み")
    print("✅ 実行コマンド表示: 追加済み")
    print("✅ プロセスID表示: 追加済み")
    print("=" * 70 + "\n")
    app.run(host='0.0.0.0', port=5001, debug=False)
