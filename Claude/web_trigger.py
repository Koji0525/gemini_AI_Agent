#!/usr/bin/env python3
"""
Webサーバー経由でトリガー
外出先からブラウザでアクセス可能
"""
from flask import Flask, jsonify
from pathlib import Path
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <h1>🤖 Claude Agent Controller</h1>
    <p><a href="/trigger">🔔 実行をトリガー</a></p>
    <p><a href="/status">📊 ステータス確認</a></p>
    '''

@app.route('/trigger')
def trigger():
    """実行をトリガー"""
    Path('TRIGGER').touch()
    return jsonify({
        'status': 'success',
        'message': 'トリガーを作成しました'
    })

@app.route('/status')
def status():
    """ステータス確認"""
    log_file = Path('logs/daemon.log')
    if log_file.exists():
        with open(log_file) as f:
            logs = f.readlines()[-20:]  # 最新20行
        return '<pre>' + ''.join(logs) + '</pre>'
    return 'ログなし'

if __name__ == '__main__':
    # pip install flask
    app.run(host='0.0.0.0', port=5000, debug=True)
