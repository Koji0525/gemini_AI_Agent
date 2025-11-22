#!/bin/bash
# dashboard.html不足エラーの修正

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 dashboard.html不足エラーの修正"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# HTMLファイルを作成
mkdir -p agents/web_dashboard

cat > agents/web_dashboard/dashboard.html << 'HTML'
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
        
        .btn-success {
            background: #48bb78;
            color: white;
        }
        
        .btn-success:hover {
            background: #38a169;
            transform: translateY(-2px);
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
                        <option value="message">�� メッセージ</option>
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
HTML

echo "✅ HTMLファイル作成: agents/web_dashboard/dashboard.html"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ HTMLファイル不足エラー修正完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 修正内容:"
echo "  ✅ dashboard.html を作成"
echo "  ✅ 完全なHTML（CSS + JavaScript含む）"
echo ""
echo "🎯 ダッシュボード再起動:"
echo "  pkill -f dashboard_server.py"
echo "  bash start_dashboard_background_v2.sh"
echo ""

# 自動再起動
read -p "ダッシュボードを再起動しますか？ [Y/n] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "🔄 ダッシュボードを再起動中..."
    pkill -f dashboard_server.py 2>/dev/null
    sleep 2
    bash start_dashboard_background_v2.sh
    
    echo ""
    echo "✅ 再起動完了"
    echo "📍 アクセス: http://localhost:8000"
else
    echo "⏭️  スキップしました"
fi

