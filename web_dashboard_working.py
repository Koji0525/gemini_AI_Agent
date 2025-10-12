#!/usr/bin/env python3
"""Claude Agent Dashboard（完全動作版）"""
from flask import Flask, jsonify, render_template_string, request
from pathlib import Path
import subprocess
import threading
import time
import os

app = Flask(__name__)
current_process = None
execution_status = {
    'running': False,
    'last_execution': None,
    'error': None
}

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>🤖 Claude Agent Dashboard</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { 
            color: #667eea;
            margin-bottom: 30px; 
            text-align: center;
            font-size: 2.5em;
        }
        
        .status-badge {
            display: inline-block;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin-left: 10px;
        }
        .status-running { background: #4CAF50; color: white; }
        .status-idle { background: #2196F3; color: white; }
        .status-error { background: #f44336; color: white; }
        
        .control-panel {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        button { 
            padding: 15px 20px; 
            font-size: 15px; 
            cursor: pointer; 
            border: none;
            border-radius: 10px;
            transition: all 0.3s;
            font-weight: bold;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        
        .btn-run { background: linear-gradient(135deg, #4CAF50, #45a049); color: white; }
        .btn-stop { background: linear-gradient(135deg, #f44336, #da190b); color: white; }
        .btn-status { background: linear-gradient(135deg, #2196F3, #0b7dda); color: white; }
        .btn-clear { background: linear-gradient(135deg, #FF9800, #fb8c00); color: white; }
        
        .instruction-box {
            margin: 20px 0;
            padding: 25px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
        }
        .instruction-box h2 { margin-bottom: 15px; color: #333; }
        .instruction-box textarea {
            width: 100%;
            min-height: 100px;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 14px;
            resize: vertical;
        }
        
        .debug-info {
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            font-family: monospace;
            font-size: 0.9em;
        }
        
        .status-container {
            margin-top: 30px;
            padding: 25px;
            background: #f9f9f9;
            border-radius: 15px;
            min-height: 400px;
            max-height: 70vh;
            overflow-y: auto;
        }
        
        pre { 
            background: #2d2d2d; 
            color: #f8f8f2; 
            padding: 20px; 
            border-radius: 10px;
            overflow-x: auto;
            font-size: 13px;
            line-height: 1.6;
        }
        
        .loading { 
            text-align: center;
            padding: 50px;
            color: #FF9800;
            font-size: 1.5em;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
    <script>
        let autoRefresh = null;
        
        function updateStatusBadge(data) {
            const badge = document.getElementById('statusBadge');
            if (data.execution_status.running) {
                badge.className = 'status-badge status-running';
                badge.textContent = '🔄 実行中';
            } else if (data.execution_status.error) {
                badge.className = 'status-badge status-error';
                badge.textContent = '❌ エラー';
            } else {
                badge.className = 'status-badge status-idle';
                badge.textContent = '✅ 待機中';
            }
        }
        
        function runSystem() {
            document.getElementById('status').innerHTML = '<div class="loading">⏳ 実行中...</div>';
            document.getElementById('runBtn').disabled = true;
            
            fetch('/trigger')
                .then(r => r.json())
                .then(data => {
                    setTimeout(() => {
                        checkStatus();
                        document.getElementById('runBtn').disabled = false;
                    }, 3000);
                })
                .catch(err => {
                    document.getElementById('status').innerHTML = '<div style="color: red;">❌ エラー: ' + err + '</div>';
                    document.getElementById('runBtn').disabled = false;
                });
        }
        
        function runWithInstruction() {
            const instruction = document.getElementById('instruction').value;
            if (!instruction.trim()) {
                alert('指示を入力してください');
                return;
            }
            
            document.getElementById('status').innerHTML = '<div class="loading">⏳ カスタム指示付きで実行中...</div>';
            document.getElementById('runBtn').disabled = true;
            
            fetch('/trigger_with_instruction', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({instruction: instruction})
            })
                .then(r => r.json())
                .then(data => {
                    document.getElementById('instruction').value = '';
                    setTimeout(() => {
                        checkStatus();
                        document.getElementById('runBtn').disabled = false;
                    }, 5000);
                })
                .catch(err => {
                    document.getElementById('status').innerHTML = '<div style="color: red;">❌ エラー: ' + err + '</div>';
                    document.getElementById('runBtn').disabled = false;
                });
        }
        
        function checkStatus() {
            fetch('/status')
                .then(r => r.json())
                .then(data => {
                    updateStatusBadge(data);
                    
                    let html = '';
                    
                    // デバッグ情報
                    html += '<div class="debug-info">';
                    html += '<strong>🔍 デバッグ情報</strong><br>';
                    html += '実行状態: ' + (data.execution_status.running ? '実行中' : '待機中') + '<br>';
                    html += '最終実行: ' + data.execution_status.last_execution + '<br>';
                    html += 'ログファイル: ' + data.debug.log_file_exists + '<br>';
                    html += 'ログ更新: ' + data.debug.log_last_modified + '<br>';
                    html += 'プロセス数: ' + data.debug.process_count;
                    if (data.execution_status.error) {
                        html += '<br><span style="color: red;">エラー: ' + data.execution_status.error + '</span>';
                    }
                    html += '</div>';
                    
                    // Claude応答
                    if (data.claude_response) {
                        html += '<h3>🤖 Claude の最新応答</h3>';
                        html += '<pre>' + data.claude_response + '</pre>';
                    }
                    
                    // ログ
                    if (data.logs) {
                        html += '<h3>📋 実行ログ（最新30行）</h3>';
                        html += '<pre>' + data.logs + '</pre>';
                    } else {
                        html += '<p>ログがありません</p>';
                    }
                    
                    document.getElementById('status').innerHTML = html;
                });
        }
        
        function toggleAutoRefresh() {
            if (autoRefresh) {
                clearInterval(autoRefresh);
                autoRefresh = null;
                document.getElementById('autoRefreshBtn').textContent = '▶️ 自動更新';
            } else {
                autoRefresh = setInterval(checkStatus, 2000);
                document.getElementById('autoRefreshBtn').textContent = '⏸️ 自動更新中';
            }
        }
        
        window.onload = function() {
            checkStatus();
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>🤖 Claude Agent Dashboard <span id="statusBadge" class="status-badge status-idle">待機中</span></h1>
        
        <div class="control-panel">
            <button id="runBtn" class="btn-run" onclick="runSystem()">🚀 今すぐ実行</button>
            <button class="btn-status" onclick="checkStatus()">🔄 ステータス更新</button>
            <button class="btn-status" id="autoRefreshBtn" onclick="toggleAutoRefresh()">▶️ 自動更新</button>
            <button class="btn-clear" onclick="location.reload()">🔄 ページ更新</button>
        </div>
        
        <div class="instruction-box">
            <h2>📝 カスタム指示</h2>
            <textarea id="instruction" placeholder="例: プロジェクトのtest/ディレクトリを確認して改善提案を3つしてください"></textarea>
            <button class="btn-run" onclick="runWithInstruction()" style="width: 100%; margin-top: 15px;">
                📤 指示付きで実行
            </button>
        </div>
        
        <div id="status" class="status-container">
            <div class="loading">読み込み中...</div>
        </div>
    </div>
</body>
</html>
'''

def run_system_sync(instruction=None):
    """同期実行（デバッグ用）"""
    global execution_status
    
    execution_status['running'] = True
    execution_status['last_execution'] = time.strftime('%H:%M:%S')
    execution_status['error'] = None
    
    try:
        # カスタム指示ファイル作成
        if instruction:
            custom_file = Path('CUSTOM_INSTRUCTION.txt')
            custom_file.write_text(instruction, encoding='utf-8')
            print(f"📝 カスタム指示ファイル作成: {custom_file.absolute()}")
        
        # 実行
        print("🚀 claude_unified_agent_fixed.py 実行開始")
        result = subprocess.run(
            ['python', 'claude_unified_agent_fixed.py'],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        print(f"✅ 実行完了（終了コード: {result.returncode}）")
        
        if result.returncode != 0:
            execution_status['error'] = f"終了コード: {result.returncode}"
            print(f"❌ エラー出力:\n{result.stderr}")
        
    except subprocess.TimeoutExpired:
        execution_status['error'] = "タイムアウト（120秒）"
        print("⏰ タイムアウト")
    except Exception as e:
        execution_status['error'] = str(e)
        print(f"❌ 例外: {e}")
    finally:
        execution_status['running'] = False

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/trigger')
def trigger():
    if execution_status['running']:
        return jsonify({'status': 'error', 'message': '既に実行中です'})
    
    thread = threading.Thread(target=run_system_sync)
    thread.start()
    return jsonify({'status': 'success', 'message': '実行開始'})

@app.route('/trigger_with_instruction', methods=['POST'])
def trigger_with_instruction():
    if execution_status['running']:
        return jsonify({'status': 'error', 'message': '既に実行中です'})
    
    data = request.json
    instruction = data.get('instruction', '')
    
    thread = threading.Thread(target=run_system_sync, args=(instruction,))
    thread.start()
    return jsonify({'status': 'success', 'message': 'カスタム指示付きで実行開始'})

@app.route('/status')
def status():
    """ステータス取得"""
    log_file = Path('logs/unified_conversation.log')
    response_files = sorted(Path('.').glob('claude_response_*.txt'))
    
    # デバッグ情報
    debug_info = {
        'log_file_exists': log_file.exists(),
        'log_last_modified': time.strftime('%H:%M:%S', time.localtime(log_file.stat().st_mtime)) if log_file.exists() else 'なし',
        'process_count': len([p for p in Path('/proc').glob('[0-9]*') if (Path('/proc') / p.name / 'cmdline').exists()])
    }
    
    data = {
        'execution_status': execution_status,
        'debug': debug_info,
        'logs': '',
        'claude_response': ''
    }
    
    if log_file.exists():
        try:
            logs = log_file.read_text(encoding='utf-8').split('\n')
            data['logs'] = '\n'.join(logs[-30:])
        except Exception as e:
            data['logs'] = f"ログ読み込みエラー: {e}"
    
    if response_files:
        try:
            latest = response_files[-1]
            data['claude_response'] = latest.read_text(encoding='utf-8')[:1000]
        except Exception as e:
            data['claude_response'] = f"応答読み込みエラー: {e}"
    
    return jsonify(data)

if __name__ == '__main__':
    print("=" * 70)
    print("🤖 Claude Agent Dashboard 起動（完全動作版）")
    print("=" * 70)
    print("📍 アクセス: http://localhost:5000")
    print("=" * 70)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
