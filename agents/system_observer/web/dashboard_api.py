"""
Dashboard API - SystemObserver用Webダッシュボード（FastAPI）

【Phase 2.1: Reactダッシュボード開発】
RESTful APIによるリアルタイムデータ配信
"""

import asyncio
import sys
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agents.system_observer.system_observer import SystemObserver

app = FastAPI(title="SystemObserver Dashboard API", version="1.0.0")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SystemObserver初期化
observer = SystemObserver()


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {"status": "ok", "service": "SystemObserver Dashboard API"}


@app.get("/api/system/snapshot")
async def get_system_snapshot():
    """システムスナップショットを取得"""
    snapshot = observer.collect_system_snapshot()
    return snapshot


@app.get("/api/system/resources")
async def get_resources():
    """リソースメトリクスを取得"""
    snapshot = observer.collect_system_snapshot()
    return snapshot.get("resources", {})


@app.get("/api/system/agents")
async def get_agents():
    """エージェント状態を取得"""
    snapshot = observer.collect_system_snapshot()
    return snapshot.get("agents", {})


@app.get("/api/system/tasks")
async def get_tasks():
    """タスクメトリクスを取得"""
    snapshot = observer.collect_system_snapshot()
    return snapshot.get("tasks", {})


@app.get("/api/system/performance")
async def get_performance():
    """パフォーマンスメトリクスを取得"""
    snapshot = observer.collect_system_snapshot()
    return snapshot.get("performance", {})


@app.get("/api/system/health")
async def get_health():
    """システムヘルスを取得"""
    snapshot = observer.collect_system_snapshot()
    return {"health": snapshot.get("health", "unknown"), "timestamp": snapshot.get("timestamp")}


@app.get("/api/system/history")
async def get_history(count: int = 10):
    """スナップショット履歴を取得"""
    history = observer.get_recent_snapshots(count)
    return {"count": len(history), "snapshots": history}


@app.websocket("/ws/realtime")
async def websocket_realtime(websocket: WebSocket):
    """WebSocketによるリアルタイムデータ配信"""
    await websocket.accept()

    try:
        while True:
            # スナップショット収集
            snapshot = observer.collect_system_snapshot()

            # JSON送信
            await websocket.send_json(snapshot)

            # 5秒待機
            await asyncio.sleep(5)

    except Exception as e:
        print(f"WebSocketエラー: {e}")
    finally:
        await websocket.close()


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """シンプルなHTMLダッシュボード"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SystemObserver Dashboard</title>
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
            .health-healthy { color: #4CAF50; }
            .health-warning { color: #FFC107; }
            .health-critical { color: #F44336; }
            .timestamp {
                text-align: center;
                color: #666;
                margin-top: 20px;
                font-size: 0.9em;
            }
            .status-badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 0.85em;
                font-weight: bold;
            }
            .status-healthy { background: #4CAF50; color: white; }
            .status-warning { background: #FFC107; color: black; }
            .status-critical { background: #F44336; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔭 SystemObserver Dashboard</h1>
            
            <div class="grid">
                <!-- リソース -->
                <div class="card">
                    <h2>🖥️ リソース</h2>
                    <div id="resources">Loading...</div>
                </div>
                
                <!-- エージェント -->
                <div class="card">
                    <h2>👥 エージェント</h2>
                    <div id="agents">Loading...</div>
                </div>
                
                <!-- タスク -->
                <div class="card">
                    <h2>📋 タスク</h2>
                    <div id="tasks">Loading...</div>
                </div>
                
                <!-- パフォーマンス -->
                <div class="card">
                    <h2>📈 パフォーマンス</h2>
                    <div id="performance">Loading...</div>
                </div>
            </div>
            
            <!-- システムヘルス -->
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
                fetch('/api/system/snapshot')
                    .then(response => response.json())
                    .then(data => {
                        // リソース
                        const resources = data.resources || {};
                        document.getElementById('resources').innerHTML = `
                            <div class="metric">
                                <span class="metric-label">CPU</span>
                                <span class="metric-value">${resources.cpu_percent?.toFixed(1) || 'N/A'}%</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">メモリ</span>
                                <span class="metric-value">${resources.memory_percent?.toFixed(1) || 'N/A'}%</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">ディスク</span>
                                <span class="metric-value">${resources.disk_percent?.toFixed(1) || 'N/A'}%</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">状態</span>
                                <span class="metric-value status-badge status-${resources.status || 'unknown'}">
                                    ${resources.status || 'N/A'}
                                </span>
                            </div>
                        `;
                        
                        // エージェント
                        const agents = data.agents || {};
                        document.getElementById('agents').innerHTML = `
                            <div class="metric">
                                <span class="metric-label">総数</span>
                                <span class="metric-value">${agents.total_agents || 0}件</span>
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
                        
                        // タスク
                        const tasks = data.tasks || {};
                        document.getElementById('tasks').innerHTML = `
                            <div class="metric">
                                <span class="metric-label">総数</span>
                                <span class="metric-value">${tasks.total_tasks || 0}件</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">実行中</span>
                                <span class="metric-value">${tasks.running_tasks || 0}件</span>
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
                        
                        // パフォーマンス
                        const perf = data.performance || {};
                        document.getElementById('performance').innerHTML = `
                            <div class="metric">
                                <span class="metric-label">成功率</span>
                                <span class="metric-value">${(perf.overall_success_rate * 100)?.toFixed(1) || 'N/A'}%</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">平均応答</span>
                                <span class="metric-value">${perf.average_response_time?.toFixed(2) || 'N/A'}秒</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">エラー率</span>
                                <span class="metric-value">${(perf.error_rate * 100)?.toFixed(1) || 'N/A'}%</span>
                            </div>
                        `;
                        
                        // ヘルス
                        const health = data.health || 'unknown';
                        const healthClass = `health-${health}`;
                        const healthEmoji = {
                            'healthy': '✅',
                            'warning': '⚠️',
                            'critical': '🚨',
                            'unknown': '❓'
                        };
                        document.getElementById('health').innerHTML = `
                            <span class="${healthClass}">
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
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 SystemObserver Dashboard API 起動")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 Dashboard: http://localhost:8000/dashboard")
    print("📡 API Docs:  http://localhost:8000/docs")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    uvicorn.run(app, host="0.0.0.0", port=8000)
