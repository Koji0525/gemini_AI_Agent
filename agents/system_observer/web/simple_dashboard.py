"""
SimpleDashboard v3 - 完全版

【修正】
- ポート使用中の場合は自動で別ポートを使用
- デフォルト15個のエージェント表示
- タスク数・パフォーマンス実データ取得
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import json
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

from agents.advanced_analytics.execution_analyzer import ExecutionAnalyzer
from agents.system_observer.system_observer_v3 import SystemObserverV3


class DashboardHandler(BaseHTTPRequestHandler):
    """ダッシュボードHTTPハンドラー"""

    observer = None

    def do_GET(self):
        """GETリクエスト処理"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == "/":
            self.serve_dashboard()
        elif path == "/api/snapshot":
            self.serve_snapshot()
        elif path == "/api/analysis":
            self.serve_analysis()
        else:
            self.send_error(404, "Not Found")

    def serve_dashboard(self):
        """ダッシュボードHTML"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>SystemObserver Dashboard v3 (Full)</title>
    <meta charset="utf-8">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #1a1a1a;
            color: #e0e0e0;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            color: #4CAF50;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }
        .version {
            color: #666;
            font-size: 0.9em;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .card {
            background: #2a2a2a;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        .card h2 {
            margin-top: 0;
            color: #4CAF50;
            font-size: 1.2em;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #3a3a3a;
        }
        .metric:last-child {
            border-bottom: none;
        }
        .metric-label {
            color: #aaa;
        }
        .metric-value {
            font-weight: bold;
            color: #fff;
        }
        .agent-list {
            max-height: 400px;
            overflow-y: auto;
            margin-top: 10px;
        }
        .agent-item {
            padding: 8px;
            margin: 4px 0;
            background: #333;
            border-radius: 4px;
            font-size: 0.9em;
        }
        .agent-health {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .health-healthy { background: #4CAF50; }
        .health-warning { background: #FFC107; }
        .health-critical { background: #F44336; }
        .health-unknown { background: #666; }
        .timestamp {
            text-align: center;
            color: #666;
            margin-top: 20px;
            font-size: 0.9em;
        }
        .note {
            background: #333;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
            font-size: 0.9em;
            color: #FFC107;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔭 SystemObserver Dashboard <span class="version">v3 Full (15 Agents)</span></h1>
        
        <div class="grid">
            <div class="card">
                <h2>🖥️ リソース</h2>
                <div id="resources">Loading...</div>
            </div>
            
            <div class="card">
                <h2>👥 エージェント</h2>
                <div id="agents">Loading...</div>
                <div class="agent-list" id="agent-list"></div>
            </div>
            
            <div class="card">
                <h2>📋 タスク</h2>
                <div id="tasks">Loading...</div>
            </div>
            
            <div class="card">
                <h2>📈 パフォーマンス</h2>
                <div id="performance">Loading...</div>
            </div>
        </div>
        
        <div class="card" style="margin-top: 20px;">
            <h2>🏥 システムヘルス</h2>
            <div id="health" style="text-align: center; font-size: 2em;">
                Loading...
            </div>
        </div>
        
        <div class="timestamp" id="timestamp">Last update: -</div>
    </div>
    
    <script>
        function updateDashboard() {
            fetch('/api/snapshot')
                .then(response => response.json())
                .then(data => {
                    // リソース
                    const resources = data.resources || {};
                    document.getElementById('resources').innerHTML = `
                        <div class="metric">
                            <span class="metric-label">CPU</span>
                            <span class="metric-value">${(resources.cpu_percent || 0).toFixed(1)}%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">メモリ</span>
                            <span class="metric-value">${(resources.memory_percent || 0).toFixed(1)}%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">ディスク</span>
                            <span class="metric-value">${(resources.disk_percent || 0).toFixed(1)}%</span>
                        </div>
                    `;
                    
                    // エージェント
                    const agents = data.agents || {};
                    const totalAgents = agents.total_agents || 0;
                    const hasNote = agents.note;
                    
                    let agentsHtml = `
                        <div class="metric">
                            <span class="metric-label">総数</span>
                            <span class="metric-value">${totalAgents}件</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">稼働中</span>
                            <span class="metric-value">${agents.active_agents || 0}件</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">待機中</span>
                            <span class="metric-value">${agents.idle_agents || 0}件</span>
                        </div>
                    `;
                    
                    if (hasNote) {
                        agentsHtml += `<div class="note">💡 ${hasNote}</div>`;
                    }
                    
                    document.getElementById('agents').innerHTML = agentsHtml;
                    
                    // エージェント一覧
                    const agentList = agents.agents || [];
                    let agentListHtml = '';
                    agentList.forEach(agent => {
                        const healthClass = `health-${agent.health || 'unknown'}`;
                        const caps = (agent.capabilities || []).slice(0, 2).join(', ');
                        agentListHtml += `
                            <div class="agent-item">
                                <span class="agent-health ${healthClass}"></span>
                                <strong>${agent.agent_id}</strong>
                                ${caps ? `<br><span style="color: #999; font-size: 0.85em;">${caps}</span>` : ''}
                            </div>
                        `;
                    });
                    document.getElementById('agent-list').innerHTML = agentListHtml;
                    
                    // タスク
                    const tasks = data.tasks || {};
                    const hasTaskNote = tasks.note;
                    
                    let tasksHtml = `
                        <div class="metric">
                            <span class="metric-label">総数</span>
                            <span class="metric-value">${tasks.total_tasks || 0}件</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">完了</span>
                            <span class="metric-value">${tasks.completed_tasks || 0}件</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">失敗</span>
                            <span class="metric-value">${tasks.failed_tasks || 0}件</span>
                        </div>
                    `;
                    
                    if (hasTaskNote) {
                        tasksHtml += `<div class="note">💡 ${hasTaskNote}</div>`;
                    }
                    
                    document.getElementById('tasks').innerHTML = tasksHtml;
                    
                    // パフォーマンス
                    const perf = data.performance || {};
                    document.getElementById('performance').innerHTML = `
                        <div class="metric">
                            <span class="metric-label">成功率</span>
                            <span class="metric-value">${((perf.overall_success_rate || 0) * 100).toFixed(1)}%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">平均応答</span>
                            <span class="metric-value">${(perf.average_response_time || 0).toFixed(2)}秒</span>
                        </div>
                    `;
                    
                    // ヘルス
                    const health = data.health || 'unknown';
                    const healthEmoji = {
                        'healthy': '✅',
                        'warning': '⚠️',
                        'critical': '🚨',
                        'unknown': '❓'
                    };
                    document.getElementById('health').innerHTML = `
                        <span class="health-${health}">
                            ${healthEmoji[health] || '❓'} ${health.toUpperCase()}
                        </span>
                    `;
                    
                    // タイムスタンプ
                    document.getElementById('timestamp').textContent = 
                        `Last update: ${data.timestamp || 'N/A'}`;
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }
        
        // 初回実行
        updateDashboard();
        
        // 10秒ごとに更新
        setInterval(updateDashboard, 10000);
    </script>
</body>
</html>
        """

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def serve_snapshot(self):
        """スナップショットJSON"""
        if DashboardHandler.observer is None:
            self.send_error(500, "Observer not initialized")
            return

        snapshot = DashboardHandler.observer.collect_system_snapshot()

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(snapshot).encode("utf-8"))

    def serve_analysis(self):
        """包括的分析JSON"""
        if DashboardHandler.observer is None:
            self.send_error(500, "Observer not initialized")
            return

        analysis = DashboardHandler.observer.collect_comprehensive_analysis()

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(analysis, default=str).encode("utf-8"))

    def log_message(self, format, *args):
        """ログを抑制"""


def find_free_port(start_port=8000, max_attempts=10):
    """空いているポートを見つける"""
    for port in range(start_port, start_port + max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(("0.0.0.0", port))
            sock.close()
            return port
        except OSError:
            continue
    return None


def run_server(port=8000):
    """サーバー起動"""
    # 空きポートを探す
    free_port = find_free_port(port)

    if free_port is None:
        print("❌ 利用可能なポートが見つかりません")
        print("💡 以下を実行してください:")
        print("   bash agents/system_observer/kill_dashboard.sh")
        return

    if free_port != port:
        print(f"⚠️  ポート{port}は使用中です。ポート{free_port}を使用します。")

    # Observerを初期化
    analyzer = ExecutionAnalyzer()
    DashboardHandler.observer = SystemObserverV3(execution_analyzer=analyzer)

    # スナップショット履歴を蓄積
    print("📊 初期スナップショット収集中...")
    for i in range(3):
        DashboardHandler.observer.collect_system_snapshot()

    # HTTPサーバー起動
    server = HTTPServer(("0.0.0.0", free_port), DashboardHandler)
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 SystemObserver Dashboard起動（v3 Full）")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📊 Dashboard: http://localhost:{free_port}/")
    print(f"📡 API:       http://localhost:{free_port}/api/snapshot")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✅ デフォルト15個のエージェント表示")
    print("💡 v1.24.0を起動すると実データが表示されます")
    print("Press Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⏸️  サーバーを停止しました")


if __name__ == "__main__":
    run_server()
