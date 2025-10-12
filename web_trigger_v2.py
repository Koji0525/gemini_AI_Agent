#!/usr/bin/env python3
"""
Webサーバー経由でトリガー（即座実行版）
"""
from flask import Flask, jsonify, render_template_string
from pathlib import Path
import subprocess
import threading

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🤖 Claude Agent Controller</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        button { padding: 15px 30px; font-size: 18px; cursor: pointer; margin: 10px; }
        .success { background: #4CAF50; color: white; border: none; }
        .info { background: #2196F3; color: white; border: none; }
        #status { margin-top: 20px; padding: 20px; background: #f0f0f0; }
        .loading { color: #FF9800; }
    </style>
    <script>
        function trigger() {
            document.getElementById('status').innerHTML = '<div class="loading">⏳ 実行中...</div>';
            fetch('/trigger')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('status').innerHTML = 
                        '<div style="color: green;">✅ ' + data.message + '</div>';
                });
        }
        
        function checkStatus() {
            fetch('/status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('status').innerHTML = 
                        '<pre>' + data.logs + '</pre>';
                });
        }
    </script>
</head>
<body>
    <h1>🤖 Claude Agent Controller</h1>
    <button class="success" onclick="trigger()">🚀 今すぐ実行</button>
    <button class="info" onclick="checkStatus()">📊 ステータス確認</button>
    <div id="status"></div>
</body>
</html>
'''

def run_system():
    """バックグラウンドで実行"""
    subprocess.run('python claude_agent_daemon.py --once', shell=True)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/trigger')
def trigger():
    """即座に実行"""
    # バックグラウンドで実行
    thread = threading.Thread(target=run_system)
    thread.start()
    
    return jsonify({
        'status': 'success',
        'message': '実行を開始しました！（約10-15秒で完了）'
    })

@app.route('/status')
def status():
    """ステータス確認"""
    log_file = Path('logs/daemon.log')
    if log_file.exists():
        with open(log_file) as f:
            logs = ''.join(f.readlines()[-30:])
        return jsonify({'logs': logs})
    return jsonify({'logs': 'ログなし'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
