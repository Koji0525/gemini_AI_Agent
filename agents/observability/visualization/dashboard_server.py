"""
DashboardServer - Webダッシュボードサーバー

【Phase 2.1: リアクティブダッシュボード】
Flask + WebSocketでリアルタイム可視化
"""

import sys
from pathlib import Path

from flask import Flask, jsonify
from flask_socketio import SocketIO, emit

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.observability.observability_manager import \
    get_observability_manager

app = Flask(__name__)
app.config["SECRET_KEY"] = "observability-dashboard-secret"
socketio = SocketIO(app, cors_allowed_origins="*")

obs_manager = get_observability_manager()


@app.route("/")
def index():
    """ダッシュボードトップページ"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Observability Dashboard v2.0</title>
    <meta charset="utf-8">
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0a0e27;
            color: #e0e6ed;
            padding: 20px;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        .header h1 { 
            font-size: 2em; 
            margin-bottom: 10px;
            color: white;
        }
        .header .subtitle {
            opacity: 0.9;
            font-size: 1.1em;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 25px;
            backdrop-filter: blur(10px);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(102,126,234,0.4);
        }
        .card-title {
            font-size: 1.3em;
            margin-bottom: 15px;
            color: #a5b4fc;
            display: flex;
            align-items: center;
        }
        .card-title .icon {
            margin-right: 10px;
            font-size: 1.5em;
        }
        .metric {
            font-size: 2.5em;
            font-weight: bold;
            color: #60a5fa;
            margin: 10px 0;
        }
        .metric-label {
            color: #94a3b8;
            font-size: 0.9em;
        }
        #network-graph {
            width: 100%;
            height: 500px;
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .trace-item {
            padding: 12px;
            margin: 8px 0;
            background: rgba(255,255,255,0.05);
            border-left: 3px solid #60a5fa;
            border-radius: 6px;
            font-size: 0.9em;
        }
        .trace-item.success { border-left-color: #34d399; }
        .trace-item.error { border-left-color: #f87171; }
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
        }
        .status-badge.success { background: #065f46; color: #34d399; }
        .status-badge.error { background: #7f1d1d; color: #f87171; }
        .live-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            background: #34d399;
            border-radius: 50%;
            margin-left: 10px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔭 Observability Dashboard v2.0</h1>
        <div class="subtitle">
            Phase 2.1: リアクティブダッシュボード
            <span class="live-indicator"></span>
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <div class="card-title"><span class="icon">📊</span>トレース統計</div>
            <div class="metric" id="total-traces">0</div>
            <div class="metric-label">総トレース数</div>
            <div class="metric" id="success-rate">0%</div>
            <div class="metric-label">成功率</div>
        </div>

        <div class="card">
            <div class="card-title"><span class="icon">👥</span>エージェント</div>
            <div class="metric" id="agent-count">0</div>
            <div class="metric-label">稼働中エージェント</div>
            <div class="metric" id="instrumented-count">0</div>
            <div class="metric-label">計装済み</div>
        </div>

        <div class="card">
            <div class="card-title"><span class="icon">⚡</span>パフォーマンス</div>
            <div class="metric" id="avg-duration">0ms</div>
            <div class="metric-label">平均実行時間</div>
        </div>
    </div>

    <div class="card">
        <div class="card-title"><span class="icon">🕐</span>最新トレース</div>
        <div id="recent-traces"></div>
    </div>

    <script>
        const socket = io();
        
        socket.on('connect', () => {
            console.log('✅ WebSocket接続成功');
            socket.emit('request_stats');
        });

        socket.on('stats_update', (data) => {
            console.log('📊 統計更新:', data);
            
            // トレース統計
            if (data.traces) {
                document.getElementById('total-traces').textContent = 
                    data.traces.total_traces || 0;
                
                const successRate = (data.traces.success_rate || 0) * 100;
                document.getElementById('success-rate').textContent = 
                    successRate.toFixed(1) + '%';
            }

            // エージェント情報
            if (data.opentelemetry) {
                document.getElementById('agent-count').textContent = '7'; // 固定値
                document.getElementById('instrumented-count').textContent = '3'; // 固定値
            }

            // パフォーマンス
            document.getElementById('avg-duration').textContent = '150ms'; // 仮値
        });

        socket.on('new_trace', (trace) => {
            console.log('🆕 新規トレース:', trace);
            
            const container = document.getElementById('recent-traces');
            const item = document.createElement('div');
            item.className = `trace-item ${trace.status}`;
            
            const statusBadge = `<span class="status-badge ${trace.status}">${trace.status}</span>`;
            
            item.innerHTML = `
                <strong>${trace.operation_name || 'unknown'}</strong> ${statusBadge}
                <div style="margin-top: 5px; color: #94a3b8;">
                    ID: ${trace.trace_id || 'N/A'} | 
                    時間: ${trace.duration_ms || 0}ms
                </div>
            `;
            
            container.insertBefore(item, container.firstChild);
            
            // 最大10件まで表示
            while (container.children.length > 10) {
                container.removeChild(container.lastChild);
            }
        });

        // 定期的に統計をリクエスト
        setInterval(() => {
            socket.emit('request_stats');
        }, 5000);
    </script>
</body>
</html>
    """


@app.route("/api/stats")
def get_stats():
    """統計APIエンドポイント"""
    stats = obs_manager.get_comprehensive_stats()
    return jsonify(stats)


@socketio.on("request_stats")
def handle_stats_request():
    """統計リクエストハンドラ"""
    stats = obs_manager.get_comprehensive_stats()
    emit("stats_update", stats)


@socketio.on("connect")
def handle_connect():
    """クライアント接続ハンドラ"""
    print("✅ クライアント接続")


def start_server(host="0.0.0.0", port=5000):
    """サーバー起動"""
    print(f"🚀 ダッシュボードサーバー起動: http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=False)


if __name__ == "__main__":
    start_server()
