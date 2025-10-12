#!/usr/bin/env python3
"""Claude Agent ダッシュボード v2（完全動作版）"""
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
    <title>🤖 Claude Agent Dashboard v2</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px; min-height: 100vh;
        }
        .container { 
            max-width: 1400px; margin: 0 auto; 
            background: white; border-radius: 20px;
            padding: 40px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { 
            color: #333; margin-bottom: 30px; 
            text-align: center; font-size: 2.8em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        h2 { 
            color: #667eea; margin: 25px 0 15px 0;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px; font-size: 1.5em;
        }
        
        .controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 12px; margin-bottom: 30px;
        }
        button {
            padding: 16px 20px; font-size: 15px;
            font-weight: 600; cursor: pointer;
            border: none; border-radius: 12px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        button:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        }
        button:active { transform: translateY(-1px); }
        
        .btn-run { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-stop { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; }
        .btn-refresh { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; }
        .btn-clear { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; }
        
        .instruction-panel {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            padding: 25px; border-radius: 15px;
            margin: 25px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .instruction-panel h3 {
            margin: 0 0 15px 0; color: #333;
            font-size: 1.3em;
        }
        textarea {
            width: 100%; min-height: 100px;
            padding: 15px; border: 2px solid #ddd;
            border-radius: 10px; font-size: 14px;
            font-family: inherit; resize: vertical;
            transition: border-color 0.3s;
        }
        textarea:focus {
            outline: none; border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
        }
        
        .status-area {
            background: #f8f9fa;
            border-radius: 15px; padding: 25px;
            margin-top: 25px; min-height: 400px;
            max-height: 700px; overflow-y: auto;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
        }
        
        .message {
            margin: 12px 0; padding: 18px;
            border-radius: 12px; border-left: 5px solid;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .msg-user { border-left-color: #2196F3; background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); }
        .msg-claude { border-left-color: #9c27b0; background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%); }
        .msg-system { border-left-color: #ff9800; background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); }
        .msg-command { border-left-color: #4caf50; background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); }
        .msg-error { border-left-color: #f44336; background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%); }
        
        .timestamp {
            color: #666; font-size: 0.85em;
            margin-bottom: 8px; font-weight: 500;
        }
        .content {
            color: #333; line-height: 1.6;
            white-space: pre-wrap; word-wrap: break-word;
        }
        
        .loading {
            text-align: center; padding: 40px;
            font-size: 20px; color: #667eea;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .badge {
            display: inline-block;
            padding: 4px 10px; border-radius: 12px;
            font-size: 0.85em; font-weight: 600;
            margin-left: 8px;
        }
        .badge-success { background: #4caf50; color: white; }
        .badge-warning { background: #ff9800; color: white; }
        .badge-error { background: #f44336; color: white; }
    </style>
    <script>
        let autoRefresh = null;
        
        function showLoading() {
            document.getElementById('status').innerHTML = 
                '<div class="loading">⏳ 実行中... しばらくお待ちください</div>';
        }
        
        function runSystem() {
            showLoading();
            fetch('/trigger')
                .then(r => r.json())
                .then(data => {
                    if (data.status === 'success') {
                        setTimeout(loadConversation, 3000);
                    } else {
                        showError(data.message);
                    }
                })
                .catch(err => showError('実行エラー: ' + err));
        }
        
        function runWithInstruction() {
            const instruction = document.getElementById('instruction').value.trim();
            if (!instruction) {
                alert('📝 指示を入力してください');
                return;
            }
            
            showLoading();
            fetch('/trigger_custom', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({instruction: instruction})
            })
                .then(r => r.json())
                .then(data => {
                    if (data.status === 'success') {
                        document.getElementById('instruction').value = '';
                        setTimeout(loadConversation, 3000);
                    } else {
                        showError(data.message);
                    }
                })
                .catch(err => showError('実行エラー: ' + err));
        }
        
        function emergencyStop() {
            if (confirm('🛑 実行中のプロセスを緊急停止しますか？')) {
                fetch('/stop')
                    .then(r => r.json())
                    .then(data => {
                        alert(data.message);
                        loadConversation();
                    });
            }
        }
        
        function loadConversation() {
            fetch('/conversation')
                .then(r => r.json())
                .then(data => {
                    let html = '<h2>�� 会話履歴</h2>';
                    
                    if (data.messages && data.messages.length > 0) {
                        data.messages.forEach(msg => {
                            html += `<div class="message msg-${msg.type}">
                                <div class="timestamp">${msg.timestamp}</div>
                                <div class="content">${escapeHtml(msg.content)}</div>
                            </div>`;
                        });
                    } else {
                        html += '<div class="message msg-system"><div class="content">まだ会話履歴がありません。「🚀 実行」ボタンで開始してください。</div></div>';
                    }
                    
                    document.getElementById('status').innerHTML = html;
                })
                .catch(err => showError('読み込みエラー: ' + err));
        }
        
        function clearLogs() {
            if (confirm('🗑️ すべてのログをクリアしますか？')) {
                fetch('/clear')
                    .then(r => r.json())
                    .then(data => {
                        alert(data.message);
                        loadConversation();
                    });
            }
        }
        
        function toggleAutoRefresh() {
            const btn = document.getElementById('autoRefreshBtn');
            if (autoRefresh) {
                clearInterval(autoRefresh);
                autoRefresh = null;
                btn.textContent = '▶️ 自動更新';
            } else {
                autoRefresh = setInterval(loadConversation, 3000);
                btn.textContent = '⏸️ 停止';
            }
        }
        
        function showError(message) {
            document.getElementById('status').innerHTML = 
                `<div class="message msg-error"><div class="content">❌ ${message}</div></div>`;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        window.onload = () => loadConversation();
    </script>
</head>
<body>
    <div class="container">
        <h1>🤖 Claude Agent Dashboard v2</h1>
        
        <div class="controls">
            <button class="btn-run" onclick="runSystem()">🚀 実行</button>
            <button class="btn-stop" onclick="emergencyStop()">🛑 停止</button>
            <button class="btn-refresh" onclick="loadConversation()">🔄 更新</button>
            <button class="btn-refresh" id="autoRefreshBtn" onclick="toggleAutoRefresh()">▶️ 自動更新</button>
            <button class="btn-clear" onclick="clearLogs()">🗑️ クリア</button>
        </div>
        
        <div class="instruction-panel">
            <h3>📝 カスタム指示</h3>
            <textarea id="instruction" placeholder="例: プロジェクトのREADME.mdを確認して、ドキュメントの改善点を3つ提案してください"></textarea>
            <button class="btn-run" onclick="runWithInstruction()" style="width: 100%; margin-top: 15px;">
                📤 この指示で実行
            </button>
        </div>
        
        <div class="status-area" id="status">
            <div class="loading">読み込み中...</div>
        </div>
    </div>
</body>
</html>
'''

def run_unified_agent(instruction=None):
    """統合エージェント実行"""
    global current_process
    try:
        if instruction:
            Path('CUSTOM_INSTRUCTION.txt').write_text(instruction, encoding='utf-8')
        
        current_process = subprocess.Popen(
            'python claude_unified_agent.py',
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
    thread = threading.Thread(target=run_unified_agent)
    thread.start()
    return jsonify({'status': 'success', 'message': '実行を開始しました'})

@app.route('/trigger_custom', methods=['POST'])
def trigger_custom():
    data = request.json
    instruction = data.get('instruction', '')
    thread = threading.Thread(target=run_unified_agent, args=(instruction,))
    thread.start()
    return jsonify({'status': 'success', 'message': 'カスタム指示付きで実行を開始しました'})

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
    """会話ログ取得"""
    log_file = Path('logs/unified_conversation.log')
    messages = []
    
    if log_file.exists():
        lines = log_file.read_text(encoding='utf-8').split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            
            # ログ解析
            if '[INFO]' in line or '[SUCCESS]' in line:
                if '📤 Claude APIに送信中' in line:
                    msg_type = 'user'
                elif '📥 Claude からの応答' in line:
                    msg_type = 'claude'
                elif '⚙️ コマンド実行' in line:
                    msg_type = 'command'
                elif '📝 カスタム指示' in line:
                    msg_type = 'system'
                else:
                    msg_type = 'system'
                
                # タイムスタンプ抽出
                timestamp = line.split(']')[0] + ']' if '[' in line else ''
                content = line.split('] ', 1)[1] if '] ' in line else line
                
                messages.append({
                    'type': msg_type,
                    'timestamp': timestamp,
                    'content': content
                })
            elif '[ERROR]' in line:
                timestamp = line.split(']')[0] + ']' if '[' in line else ''
                content = line.split('] ', 1)[1] if '] ' in line else line
                messages.append({
                    'type': 'error',
                    'timestamp': timestamp,
                    'content': content
                })
    
    return jsonify({'messages': messages[-30:]})

@app.route('/clear')
def clear():
    """ログクリア"""
    for f in Path('logs').glob('*.log'):
if f.exists():
            f.write_text('')
    return jsonify({'status': 'success', 'message': 'ログをクリアしました'})

if __name__ == '__main__':
    print("=" * 70)
    print("🤖 Claude Agent Dashboard v2 起動")
    print("=" * 70)
    print("📍 URL: http://localhost:5000")
    print("🔧 統合エージェント: claude_unified_agent.py")
    print("=" * 70)
    app.run(host='0.0.0.0', port=5000, debug=False)
