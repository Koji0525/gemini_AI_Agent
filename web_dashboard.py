#!/usr/bin/env python3
"""Claude Agent ダッシュボード（会話ログ表示版）"""
from flask import Flask, jsonify, render_template_string, request
from pathlib import Path
import subprocess
import threading
import json

app = Flask(__name__)
current_process = None

HTML_DASHBOARD = '''
<!DOCTYPE html>
<html>
<head>
    <title>🤖 Claude Agent Dashboard</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { color: #333; margin-bottom: 30px; text-align: center; font-size: 2.5em; }
        h2 { color: #667eea; margin: 20px 0 10px 0; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        
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
        .btn-run { background: #4CAF50; color: white; }
        .btn-stop { background: #f44336; color: white; }
        .btn-status { background: #2196F3; color: white; }
        .btn-clear { background: #FF9800; color: white; }
        
        .instruction-box {
            margin: 20px 0;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 10px;
        }
        .instruction-box textarea {
            width: 100%;
            min-height: 80px;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            resize: vertical;
        }
        
        .conversation-log {
            background: #f9f9f9;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            max-height: 600px;
            overflow-y: auto;
        }
        
        .message {
            margin: 15px 0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid;
        }
        .message.user {
            background: #e3f2fd;
            border-left-color: #2196F3;
        }
        .message.claude {
            background: #f3e5f5;
            border-left-color: #9c27b0;
        }
        .message.system {
            background: #fff3e0;
            border-left-color: #ff9800;
        }
        .message.command {
            background: #e8f5e9;
            border-left-color: #4caf50;
        }
        
        .timestamp { color: #999; font-size: 0.85em; margin-bottom: 5px; }
        .command-code {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 10px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            margin: 10px 0;
        }
        
        pre { 
            background: #2d2d2d; 
            color: #f8f8f2; 
            padding: 15px; 
            border-radius: 8px;
            overflow-x: auto;
            font-size: 13px;
            line-height: 1.5;
        }
        .loading { 
            color: #FF9800; 
            font-size: 18px;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .success { color: #4CAF50; font-weight: bold; }
        .error { color: #f44336; font-weight: bold; }
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
                    setTimeout(checkConversation, 2000);
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
                    setTimeout(checkConversation, 2000);
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
        
        function checkConversation() {
            fetch('/conversation')
                .then(r => r.json())
                .then(data => {
                    let html = '<h2>💬 Claude との会話履歴</h2>';
                    html += '<div class="conversation-log">';
                    
                    if (data.messages && data.messages.length > 0) {
                        data.messages.forEach(msg => {
                            html += '<div class="message ' + msg.type + '">';
                            html += '<div class="timestamp">' + msg.timestamp + '</div>';
                            html += '<div>' + msg.content + '</div>';
                            html += '</div>';
                        });
                    } else {
                        html += '<p>まだ会話履歴がありません</p>';
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
                        checkConversation();
                    });
            }
        }
        
        function toggleAutoRefresh() {
            if (autoRefresh) {
                clearInterval(autoRefresh);
                autoRefresh = null;
                document.getElementById('autoRefreshBtn').textContent = '▶️ 自動更新';
            } else {
                autoRefresh = setInterval(checkConversation, 3000);
                document.getElementById('autoRefreshBtn').textContent = '⏸️ 自動更新';
            }
        }
        
        window.onload = function() {
            checkConversation();
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>🤖 Claude Agent Dashboard</h1>
        
        <div class="control-panel">
            <button class="btn-run" onclick="runSystem()">🚀 今すぐ実行</button>
            <button class="btn-stop" onclick="emergencyStop()">🛑 緊急停止</button>
            <button class="btn-status" onclick="checkConversation()">🔄 会話更新</button>
            <button class="btn-status" id="autoRefreshBtn" onclick="toggleAutoRefresh()">▶️ 自動更新</button>
            <button class="btn-clear" onclick="clearLogs()">🗑️ ログクリア</button>
        </div>
        
        <div class="instruction-box">
            <h2>📝 カスタム指示（Claudeに送る追加指示）</h2>
            <textarea id="instruction" placeholder="例: プロジェクトのREADME.mdを確認して、ドキュメントの改善点を3つ提案してください"></textarea>
            <button class="btn-run" onclick="runWithInstruction()" style="width: 100%; margin-top: 10px;">
                �� 指示付きで実行
            </button>
        </div>
        
        <div id="status">
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
            'python claude_agent_daemon.py --once',
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
    return render_template_string(HTML_DASHBOARD)

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

@app.route('/conversation')
def conversation():
    """会話ログを取得"""
    log_file = Path('logs/claude_conversation.log')
    messages = []
    
    if log_file.exists():
        content = log_file.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        current_msg = None
        for line in lines:
            if '=' * 70 in line:
                if current_msg:
                    messages.append(current_msg)
                    current_msg = None
                continue
            
            if '📤 Claude に送信中' in line:
                current_msg = {'type': 'user', 'timestamp': '', 'content': ''}
            elif '📥 Claude からの応答' in line:
                current_msg = {'type': 'claude', 'timestamp': '', 'content': ''}
            elif '⚙️ コマンド実行開始' in line:
                current_msg = {'type': 'command', 'timestamp': '', 'content': ''}
            elif '📝 カスタム指示を検出' in line:
                current_msg = {'type': 'system', 'timestamp': '', 'content': 'カスタム指示: '}
            elif current_msg and line.strip():
                if line.startswith('['):
                    current_msg['timestamp'] = line.split(']')[0] + ']'
                else:
                    current_msg['content'] += line + '\n'
        
        if current_msg:
            messages.append(current_msg)
    
    return jsonify({'messages': messages[-20:]})  # 最新20件

@app.route('/clear_logs')
def clear_logs():
    files = [
        Path('logs/daemon.log'),
        Path('logs/claude_conversation.log'),
        Path('logs/autonomous_*.log')
    ]
    for f in files:
        if f.exists():
            f.write_text('')
    return jsonify({'status': 'success', 'message': 'ログをクリアしました'})

if __name__ == '__main__':
    print("=" * 70)
    print("🤖 Claude Agent Dashboard 起動（会話ログ表示版）")
    print("=" * 70)
    print("アクセス: http://localhost:5000")
    print("=" * 70)
    app.run(host='0.0.0.0', port=5000, debug=False)
