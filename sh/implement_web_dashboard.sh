#!/bin/bash
# Webダッシュボード（F5+F9統合版）の構築

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Webダッシュボード（F5+F9統合版）の構築"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# 必要なディレクトリを作成
mkdir -p agents/web_dashboard
mkdir -p agents/web_dashboard/static
mkdir -p agents/web_dashboard/templates

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: FastAPIサーバーの作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: FastAPIサーバーの作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > agents/web_dashboard/dashboard_server.py << 'PYTHON'
"""
Webダッシュボードサーバー（F5+F9統合版）
FastAPIを使用した常時監視・指示インターフェース
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

# FastAPIのインポート
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("❌ FastAPIがインストールされていません")
    print("   pip install fastapi uvicorn --break-system-packages")
    sys.exit(1)

from tools.sheets_manager import GoogleSheetsManager
from agents.f9_human_interface import F9HumanInterface

app = FastAPI(title="自律開発システム ダッシュボード")

# グローバル変数
sheets_manager = None
f9_interface = None

class InstructionRequest(BaseModel):
    """人間指示のリクエストモデル"""
    instruction_type: str
    content: str
    priority: str = "medium"
    target_task: str = ""

@app.on_event("startup")
async def startup_event():
    """起動時の初期化"""
    global sheets_manager, f9_interface
    sheets_manager = GoogleSheetsManager()
    f9_interface = F9HumanInterface(sheets_manager)
    print("✅ ダッシュボードサーバー起動")

@app.get("/", response_class=HTMLResponse)
async def root():
    """メインダッシュボード"""
    html_content = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>自律開発システム - ダッシュボード</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            color: #667eea;
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            color: #666;
            font-size: 16px;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .card h2 {
            color: #333;
            font-size: 20px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }
        
        .stat-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .stat-label {
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 5px;
        }
        
        .stat-value {
            color: #333;
            font-size: 24px;
            font-weight: bold;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 20px;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            flex: 1;
            min-width: 150px;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
        }
        
        .btn-danger {
            background: #f56565;
            color: white;
        }
        
        .btn-danger:hover {
            background: #e53e3e;
            transform: translateY(-2px);
        }
        
        .btn-warning {
            background: #ed8936;
            color: white;
        }
        
        .btn-success {
            background: #48bb78;
            color: white;
        }
        
        .task-list {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .task-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid #48bb78;
        }
        
        .task-item.pending {
            border-left-color: #ed8936;
        }
        
        .task-item.failed {
            border-left-color: #f56565;
        }
        
        .task-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        
        .task-meta {
            color: #666;
            font-size: 12px;
        }
        
        .log-viewer {
            background: #1a1a1a;
            color: #00ff00;
            padding: 20px;
            border-radius: 8px;
            max-height: 400px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .form-input, .form-select, .form-textarea {
            width: 100%;
            padding: 10px;
            border: 2px solid #e2e8f0;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        .form-input:focus, .form-select:focus, .form-textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .form-textarea {
            resize: vertical;
            min-height: 100px;
        }
        
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .status-running {
            background: #c6f6d5;
            color: #22543d;
        }
        
        .status-paused {
            background: #fed7d7;
            color: #742a2a;
        }
        
        .refresh-info {
            text-align: center;
            color: #666;
            font-size: 12px;
            margin-top: 20px;
            padding: 10px;
            background: white;
            border-radius: 8px;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .loading {
            animation: pulse 1.5s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 自律開発システム - ダッシュボード</h1>
            <p class="subtitle">24時間稼働監視 & 人間指示インターフェース（F5 + F9統合）</p>
        </div>
        
        <div class="grid">
            <!-- システム状態 -->
            <div class="card">
                <h2>📊 システム状態</h2>
                <div class="stat-grid">
                    <div class="stat-item">
                        <div class="stat-label">総タスク数</div>
                        <div class="stat-value" id="totalTasks">-</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">完了タスク</div>
                        <div class="stat-value" id="completedTasks">-</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">実行中タスク</div>
                        <div class="stat-value" id="pendingTasks">-</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">平均品質</div>
                        <div class="stat-value" id="avgQuality">-</div>
                    </div>
                </div>
                <div class="button-group">
                    <button class="btn btn-primary" onclick="refreshStats()">🔄 更新</button>
                    <button class="btn btn-success" onclick="startSystem()">▶️ 開始</button>
                    <button class="btn btn-danger" onclick="pauseSystem()">⏸️ 一時停止</button>
                </div>
            </div>
            
            <!-- 人間指示（F9） -->
            <div class="card">
                <h2>💬 人間指示（F9）</h2>
                <div class="form-group">
                    <label class="form-label">指示タイプ</label>
                    <select class="form-select" id="instructionType">
                        <option value="add_task">📝 タスク追加</option>
                        <option value="pause_system">⏸️ システム一時停止</option>
                        <option value="resume_system">▶️ システム再開</option>
                        <option value="change_priority">🔄 優先度変更</option>
                        <option value="stop_task">⏹️ タスク停止</option>
                        <option value="message">💬 メッセージ</option>
                        <option value="emergency_stop">🚨 緊急停止</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">指示内容</label>
                    <textarea class="form-textarea" id="instructionContent" placeholder="指示内容を入力してください..."></textarea>
                </div>
                <div class="form-group">
                    <label class="form-label">優先度</label>
                    <select class="form-select" id="instructionPriority">
                        <option value="high">🔴 高</option>
                        <option value="medium" selected>🟡 中</option>
                        <option value="low">🟢 低</option>
                    </select>
                </div>
                <button class="btn btn-primary" onclick="sendInstruction()" style="width: 100%;">
                    📤 指示を送信
                </button>
            </div>
        </div>
        
        <div class="grid">
            <!-- ペンディングタスク -->
            <div class="card">
                <h2>⏳ ペンディングタスク</h2>
                <div class="task-list" id="pendingTasksList">
                    <p style="text-align: center; color: #666;">読み込み中...</p>
                </div>
            </div>
            
            <!-- 人間指示一覧 -->
            <div class="card">
                <h2>📨 人間指示一覧</h2>
                <div class="task-list" id="instructionsList">
                    <p style="text-align: center; color: #666;">読み込み中...</p>
                </div>
            </div>
        </div>
        
        <!-- ログビューアー -->
        <div class="card">
            <h2>📝 リアルタイムログ</h2>
            <div class="log-viewer" id="logViewer">
                <div class="loading">ログを読み込み中...</div>
            </div>
        </div>
        
        <div class="refresh-info">
            🔄 自動更新: 10秒ごと | 最終更新: <span id="lastUpdate">-</span>
        </div>
    </div>
    
    <script>
        // API呼び出し
        async function fetchStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                document.getElementById('totalTasks').textContent = data.total_tasks || 0;
                document.getElementById('completedTasks').textContent = data.completed_tasks || 0;
                document.getElementById('pendingTasks').textContent = data.pending_tasks || 0;
                document.getElementById('avgQuality').textContent = (data.avg_quality || 0).toFixed(1);
                
                updateTimestamp();
            } catch (error) {
                console.error('統計取得エラー:', error);
            }
        }
        
        async function fetchPendingTasks() {
            try {
                const response = await fetch('/api/tasks/pending');
                const tasks = await response.json();
                
                const container = document.getElementById('pendingTasksList');
                
                if (tasks.length === 0) {
                    container.innerHTML = '<p style="text-align: center; color: #666;">ペンディングタスクはありません</p>';
                    return;
                }
                
                container.innerHTML = tasks.map(task => `
                    <div class="task-item pending">
                        <div class="task-title">${task.task_id}</div>
                        <div class="task-meta">
                            優先度: ${task.priority} | 
                            推定時間: ${task.estimated_time}
                        </div>
                    </div>
                `).join('');
                
            } catch (error) {
                console.error('タスク取得エラー:', error);
            }
        }
        
        async function fetchInstructions() {
            try {
                const response = await fetch('/api/instructions');
                const instructions = await response.json();
                
                const container = document.getElementById('instructionsList');
                
                if (instructions.length === 0) {
                    container.innerHTML = '<p style="text-align: center; color: #666;">指示はありません</p>';
                    return;
                }
                
                container.innerHTML = instructions.map(inst => {
                    const statusClass = inst.status === 'pending' ? 'pending' : 'completed';
                    const statusIcon = inst.status === 'pending' ? '⏳' : '✅';
                    return `
                        <div class="task-item ${statusClass}">
                            <div class="task-title">${statusIcon} ${inst.instruction_type}</div>
                            <div class="task-meta">${inst.content}</div>
                            <div class="task-meta">${inst.timestamp}</div>
                        </div>
                    `;
                }).join('');
                
            } catch (error) {
                console.error('指示取得エラー:', error);
            }
        }
        
        async function fetchLogs() {
            try {
                const response = await fetch('/api/logs');
                const data = await response.json();
                
                const logViewer = document.getElementById('logViewer');
                logViewer.textContent = data.logs || 'ログがありません';
                logViewer.scrollTop = logViewer.scrollHeight;
                
            } catch (error) {
                console.error('ログ取得エラー:', error);
            }
        }
        
        async function sendInstruction() {
            const type = document.getElementById('instructionType').value;
            const content = document.getElementById('instructionContent').value;
            const priority = document.getElementById('instructionPriority').value;
            
            if (!content.trim()) {
                alert('指示内容を入力してください');
                return;
            }
            
            try {
                const response = await fetch('/api/instruction', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        instruction_type: type,
                        content: content,
                        priority: priority
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('✅ 指示を送信しました');
                    document.getElementById('instructionContent').value = '';
                    fetchInstructions();
                } else {
                    alert('❌ 指示の送信に失敗しました');
                }
                
            } catch (error) {
                console.error('指示送信エラー:', error);
                alert('❌ エラーが発生しました');
            }
        }
        
        function refreshStats() {
            fetchStats();
            fetchPendingTasks();
            fetchInstructions();
            fetchLogs();
        }
        
        function updateTimestamp() {
            const now = new Date();
            document.getElementById('lastUpdate').textContent = now.toLocaleTimeString('ja-JP');
        }
        
        async function startSystem() {
            if (confirm('システムを開始しますか？')) {
                await sendInstruction_API('resume_system', 'システム再開', 'high');
            }
        }
        
        async function pauseSystem() {
            if (confirm('システムを一時停止しますか？')) {
                await sendInstruction_API('pause_system', 'システム一時停止', 'high');
            }
        }
        
        async function sendInstruction_API(type, content, priority) {
            try {
                const response = await fetch('/api/instruction', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        instruction_type: type,
                        content: content,
                        priority: priority
                    })
                });
                
                const result = await response.json();
                if (result.success) {
                    alert('✅ 指示を送信しました');
                    refreshStats();
                }
            } catch (error) {
                console.error('エラー:', error);
            }
        }
        
        // 初期ロードと自動更新
        refreshStats();
        setInterval(refreshStats, 10000); // 10秒ごとに更新
    </script>
</body>
</html>
    """
    return html_content

@app.get("/api/stats")
async def get_stats():
    """システム統計を取得"""
    try:
        result = sheets_manager.service.spreadsheets().values().get(
            spreadsheetId=sheets_manager.spreadsheet_id,
            range="pm_tasks!A2:M1000"
        ).execute()
        
        values = result.get('values', [])
        
        total_tasks = len(values)
        completed_tasks = sum(1 for row in values if len(row) > 4 and row[4] == 'completed')
        pending_tasks = sum(1 for row in values if len(row) > 4 and row[4] == 'pending')
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'avg_quality': 8.5  # TODO: 実際の計算
        }
    except Exception as e:
        return {'error': str(e)}

@app.get("/api/tasks/pending")
async def get_pending_tasks():
    """ペンディングタスクを取得"""
    try:
        result = sheets_manager.service.spreadsheets().values().get(
            spreadsheetId=sheets_manager.spreadsheet_id,
            range="pm_tasks!A2:M1000"
        ).execute()
        
        values = result.get('values', [])
        
        pending = []
        for row in values:
            if len(row) > 4 and row[4] == 'pending':
                pending.append({
                    'task_id': row[0],
                    'description': row[2] if len(row) > 2 else '',
                    'priority': row[5] if len(row) > 5 else 'medium',
                    'estimated_time': row[6] if len(row) > 6 else '1h'
                })
        
        return pending[:10]  # 最新10件
    except Exception as e:
        return []

@app.get("/api/instructions")
async def get_instructions():
    """人間指示一覧を取得"""
    try:
        instructions = f9_interface.check_human_instructions()
        return [{
            'timestamp': inst.get('timestamp', ''),
            'instruction_type': inst.get('instruction_type', ''),
            'status': inst.get('status', ''),
            'content': inst.get('content', '')
        } for inst in instructions[:10]]
    except Exception as e:
        return []

@app.post("/api/instruction")
async def add_instruction(request: InstructionRequest):
    """人間指示を追加"""
    try:
        success = f9_interface.add_instruction(
            instruction_type=request.instruction_type,
            content=request.content,
            priority=request.priority,
            target_task=request.target_task
        )
        return {'success': success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs")
async def get_logs():
    """最新ログを取得"""
    try:
        log_files = sorted(Path('logs').glob('autonomous_v*.log'), key=os.path.getmtime, reverse=True)
        
        if log_files:
            with open(log_files[0], 'r', encoding='utf-8') as f:
                lines = f.readlines()
                return {'logs': ''.join(lines[-50:])}  # 最新50行
        
        return {'logs': 'ログファイルが見つかりません'}
    except Exception as e:
        return {'logs': f'エラー: {str(e)}'}

def start_server(port: int = 8000):
    """サーバーを起動"""
    print(f"\n{'=' * 80}")
    print("🌐 Webダッシュボードサーバー起動")
    print('=' * 80)
    print(f"\n📍 アクセスURL: http://localhost:{port}")
    print(f"📍 または: http://0.0.0.0:{port}")
    print("\n🎯 機能:")
    print("  ✅ F5: リアルタイム監視（10秒ごと自動更新）")
    print("  ✅ F9: 人間指示インターフェース")
    print("  ✅ タスク一覧表示")
    print("  ✅ ログビューアー")
    print("\n⏹️  停止: Ctrl+C")
    print('=' * 80)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    start_server()

PYTHON

echo "✅ FastAPIサーバー作成: agents/web_dashboard/dashboard_server.py"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: 起動スクリプトの作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: 起動スクリプトの作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > start_dashboard.sh << 'START'
#!/bin/bash
# Webダッシュボードを起動

cd /workspaces/gemini_AI_Agent

echo "🌐 Webダッシュボードを起動します..."
echo ""

# FastAPIとuvicornのチェック
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  FastAPIがインストールされていません"
    echo "📦 インストール中..."
    pip install fastapi uvicorn --break-system-packages
fi

# サーバー起動
python3 agents/web_dashboard/dashboard_server.py

START

chmod +x start_dashboard.sh
echo "✅ 起動スクリプト作成: start_dashboard.sh"

# バックグラウンド起動スクリプト
cat > start_dashboard_background.sh << 'BG'
#!/bin/bash
# Webダッシュボードをバックグラウンドで起動

cd /workspaces/gemini_AI_Agent

echo "🌐 Webダッシュボードをバックグラウンドで起動..."

# 既存のプロセスを停止
pkill -f "dashboard_server.py" 2>/dev/null

# バックグラウンドで起動
nohup python3 agents/web_dashboard/dashboard_server.py > logs/dashboard.log 2>&1 &

PID=$!
echo "✅ 起動完了 (PID: $PID)"
echo "📍 アクセス: http://localhost:8000"
echo "📝 ログ: tail -f logs/dashboard.log"
echo "⏹️  停止: pkill -f dashboard_server.py"

BG

chmod +x start_dashboard_background.sh
echo "✅ バックグラウンド起動スクリプト作成: start_dashboard_background.sh"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Webダッシュボード構築完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 機能:"
echo "  ✅ F5: リアルタイム監視（10秒ごと自動更新）"
echo "  ✅ F9: 人間指示インターフェース（ブラウザから操作）"
echo "  ✅ タスク一覧表示（ペンディング/完了）"
echo "  ✅ 人間指示一覧"
echo "  ✅ リアルタイムログビューアー"
echo "  ✅ システム制御（開始/一時停止）"
echo ""
echo "🚀 起動方法:"
echo "  # フォアグラウンド起動（開発用）"
echo "  bash start_dashboard.sh"
echo ""
echo "  # バックグラウンド起動（常時稼働用）"
echo "  bash start_dashboard_background.sh"
echo ""
echo "📍 アクセス:"
echo "  http://localhost:8000"
echo ""
echo "⏹️  停止方法:"
echo "  Ctrl+C（フォアグラウンド）"
echo "  pkill -f dashboard_server.py（バックグラウンド）"
echo ""
echo "📝 ログ確認:"
echo "  tail -f logs/dashboard.log"
echo ""

