#!/usr/bin/env python3
"""Claude Agent Dashboard（最終版）"""
from flask import Flask, jsonify, render_template_string, request
from pathlib import Path
import subprocess
import threading
import time

app = Flask(__name__)
current_process = None

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>🤖 Claude Agent Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', system-ui, sans-serif; 
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
            color: #333; 
            margin-bottom: 30px; 
            text-align: center;
            font-size: 2.5em;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
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
        button:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 5px 15px rgba(0,0,0,0.2); 
        }
        button:active { transform: translateY(0); }
        
        .btn-run { background: linear-gradient(135deg, #4CAF50, #45a049); color: white; }
        .btn-stop { background: linear-gradient(135deg, #f44336, #da190b); color: white; }
        .btn-status { background: linear-gradient(135deg, #2196F3, #0b7dda); color: white; }
        .btn-clear { background: linear-gradient(135deg, #FF9800, #fb8c00); color: white; }
        
        .instruction-box {
            margin: 20px 0;
            padding: 25px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .instruction-box h2 {
            margin-bottom: 15px;
            color: #333;
            font-size: 1.3em;
        }
        .instruction-box textarea {
            width: 100%;
            min-height: 100px;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 14px;
            font-family: 'Segoe UI', sans-serif;
            resize: vertical;
            transition: border 0.3s;
        }
        .instruction-box textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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
        
        .loading { 
            color: #FF9800; 
            font-size: 20px;
            animation: pulse 1.5s infinite;
            text-align: center;
            padding: 50px;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .success { 
            color: #4CAF50; 
            font-weight: bold; 
            padding: 15px;
            background: #e8f5e9;
            border-radius: 8px;
            margin: 10px 0;
        }
        .error { 
            color: #f44336; 
            font-weight: bold; 
            padding: 15px;
            background: #ffebee;
            border-radius: 8px;
            margin: 10px 0;
        }
        
        .log-section {
            margin: 20px 0;
        }
        .log-section h3 {
            color: #667eea;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 8px;
        }
        
        pre { 
            background: #2d2d2d; 
            color: #f8f8f2; 
            padding: 20px; 
            border-radius: 10px;
            overflow-x: auto;
            font-size: 13px;
            line-height: 1.6;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            padding: 20px;
            background: white;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
    </style>
    <script>
        let autoRefresh = null;
        
        function showLoading() {
            document.getElementById('status').innerHTML = 
                '<div class="loading">⏳ 実行中... (約12秒)</div>';
        }
        
        function runSystem() {
            showLoading();
            fetch('/trigger')
                .then(r => r.json())
                .then(data => {
                    setTimeout(checkStatus, 2000);
                })
                .catch(err => {
                    document.getElementById('status').innerHTML = 
                        '<div class="error">❌ エラー: ' + err + '</div>';
                });
        }
        
        function runWithInstruction() {
            const instruction = document.getElementById('instruction').value;
            if (!instruction.trim()) {
                alert('指示を入力してください');
                return;
            }
            
            showLoading();
            fetch('/trigger_with_instruction', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({instruction: instruction})
            })
                .then(r => r.json())
                .then(data => {
                    document.getElementById('instruction').value = '';
                    setTimeout(checkStatus, 3000);
                })
                .catch(err => {
                    document.getElementById('status').innerHTML = 
                        '<div class="error">❌ エラー: ' + err + '</div>';
                });
        }
        
        function emergencyStop() {
            if (confirm('実行中のプロセスを緊急停止しますか？')) {
                fetch('/stop')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('status').innerHTML = 
                            '<div class="error">🛑 ' + data.message + '</div>';
                    });
            }
        }
        
        function checkStatus() {
            fetch('/status')
                .then(r => r.json())
                .then(data => {
                    let html = '<div class="log-section">';
                    
                    // 統計情報
                    if (data.stats) {
                        html += '<div class="stats">';
                        html += '<div class="stat-card"><div class="stat-value">' + data.stats.run_count + '</div><div class="stat-label">実行回数</div></div>';
                        html += '<div class="stat-card"><div class="stat-value">' + data.stats.file_count + '</div><div class="stat-label">ログファイル数</div></div>';
                        html += '<div class="stat-card"><div class="stat-value">' + data.stats.last_run + '</div><div class="stat-label">最終実行</div></div>';
                        html += '</div>';
                    }
                    
                    // Claude応答
                    if (data.claude_response) {
                        html += '<h3>🤖 Claude の最新応答</h3>';
                        html += '<pre>' + data.claude_response + '</pre>';
                    }
                    
                    // ログ
                    if (data.logs) {
                        html += '<h3>📋 実行ログ（最新30行）</h3>';
                        html += '<pre>' + data.logs + '</pre>';
                    }
                    
                    html += '</div>';
                    document.getElementById('status').innerHTML = html;
                });
        }
        
        function clearLogs() {
            if (confirm('すべてのログをクリアしますか？')) {
                fetch('/clear_logs')
                    .then(r => r.json())
                    .then(data => {
                        alert(data.message);
                        checkStatus();
                    });
            }
        }
        
        function toggleAutoRefresh() {
            if (autoRefresh) {
                clearInterval(autoRefresh);
                autoRefresh = null;
                document.getElementById('autoRefreshBtn').textContent = '▶️ 自動更新';
            } else {
                autoRefresh = setInterval(checkStatus, 3000);
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
        <h1>🤖 Claude Agent Dashboard</h1>
        
        <div class="control-panel">
            <button class="btn-run" onclick="runSystem()">🚀 今すぐ実行</button>
            <button class="btn-stop" onclick="emergencyStop()">🛑 緊急停止</button>
            <button class="btn-status" onclick="checkStatus()">🔄 ステータス更新</button>
            <button class="btn-status" id="autoRefreshBtn" onclick="toggleAutoRefresh()">▶️ 自動更新</button>
            <button class="btn-clear" onclick="clearLogs()">🗑️ ログクリア</button>
        </div>
        
        <div class="instruction-box">
            <h2>📝 カスタム指示（Claudeに送る追加指示）</h2>
            <textarea id="instruction" placeholder="例: プロジェクトのtest/ディレクトリを確認して、テストカバレッジを改善する提案を3つしてください"></textarea>
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

def run_system(instruction=None):
    """システム実行"""
    global current_process
    
    try:
        if instruction:
            Path('CUSTOM_INSTRUCTION.txt').write_text(instruction, encoding='utf-8')
        
        current_process = subprocess.Popen(
            'python claude_unified_agent_fixed.py',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        current_process.wait()
        current_process = None
        
    except Exception as e:
        print(f"エラー: {e}")
        current_process = None

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/trigger')
def trigger():
    thread = threading.Thread(target=run_system)
    thread.start()
    return jsonify({'status': 'success', 'message': '実行開始'})

@app.route('/trigger_with_instruction', methods=['POST'])
def trigger_with_instruction():
    data = request.json
    instruction = data.get('instruction', '')
    
    thread = threading.Thread(target=run_system, args=(instruction,))
    thread.start()
    
    return jsonify({'status': 'success', 'message': 'カスタム指示付きで実行開始'})

@app.route('/stop')
def stop():
    global current_process
    if current_process:
        current_process.terminate()
        current_process = None
        return jsonify({'status': 'success', 'message': '緊急停止しました'})
    return jsonify({'status': 'info', 'message': '実行中のプロセスはありません'})

@app.route('/status')
def status():
    """ステータス取得"""
    log_file = Path('logs/unified_conversation.log')
    response_files = sorted(Path('.').glob('claude_response_*.txt'))
    
    data = {
        'stats': {
            'run_count': 0,
            'file_count': len(response_files),
            'last_run': 'なし'
        },
        'logs': '',
        'claude_response': ''
    }
    
    if log_file.exists():
        logs = log_file.read_text(encoding='utf-8').split('\n')
        data['logs'] = '\n'.join(logs[-30:])
        data['stats']['run_count'] = len([l for l in logs if '🤖 Claude統合エージェント 起動' in l])
        
        for line in reversed(logs):
            if '実行時刻:' in line:
                data['stats']['last_run'] = line.split('実行時刻:')[-1].strip()
                break
    
    if response_files:
        latest = response_files[-1]
        data['claude_response'] = latest.read_text(encoding='utf-8')
    
    return jsonify(data)

@app.route('/clear_logs')
def clear_logs():
    files = [
        Path('logs/unified_conversation.log'),
        Path('logs/unified_debug.log'),
        Path('logs/unified_error.log')
    ]
    for f in files:
        if f.exists():
            f.write_text('')
    return jsonify({'status': 'success', 'message': 'ログをクリアしました'})

if __name__ == '__main__':
    print("=" * 70)
    print("🤖 Claude Agent Dashboard 起動")
    print("=" * 70)
    print("📍 アクセス: http://localhost:5000")
    print("=" * 70)
    print("✅ カスタム指示 → claude_unified_agent_fixed.py 実行")
    print("=" * 70)
    app.run(host='0.0.0.0', port=5000, debug=False)
