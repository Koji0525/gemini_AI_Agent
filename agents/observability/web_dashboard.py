"""
Webダッシュボード
ブラウザでリアルタイム監視
"""

from datetime import datetime
from typing import Dict


def generate_html_dashboard(report: Dict) -> str:
    """HTMLダッシュボード生成"""

    overall = report.get("overall", {})
    status_color = {"HEALTHY": "#4CAF50", "WARNING": "#FF9800", "CRITICAL": "#F44336"}.get(
        overall.get("status", "UNKNOWN"), "#9E9E9E"
    )

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>システム監視ダッシュボード</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1a2e;
            color: #eee;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        .timestamp {{
            opacity: 0.8;
            font-size: 14px;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 10px 20px;
            border-radius: 5px;
            background: {status_color};
            font-weight: bold;
            margin-top: 15px;
            font-size: 18px;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .card {{
            background: #16213e;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        
        .card h2 {{
            font-size: 18px;
            margin-bottom: 15px;
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        
        .metric:last-child {{
            border-bottom: none;
        }}
        
        .metric-label {{
            font-size: 14px;
            opacity: 0.8;
        }}
        
        .metric-value {{
            font-size: 20px;
            font-weight: bold;
        }}
        
        .status-ok {{
            color: #4CAF50;
        }}
        
        .status-warning {{
            color: #FF9800;
        }}
        
        .status-error {{
            color: #F44336;
        }}
        
        .test-history {{
            margin-top: 15px;
        }}
        
        .test-item {{
            padding: 8px;
            background: rgba(255,255,255,0.05);
            margin: 5px 0;
            border-radius: 5px;
            font-size: 14px;
        }}
        
        .refresh-btn {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #667eea;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 50px;
            font-size: 16px;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            transition: all 0.3s;
        }}
        
        .refresh-btn:hover {{
            background: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 7px 20px rgba(102, 126, 234, 0.6);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 システム監視ダッシュボード</h1>
            <div class="timestamp">最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            <div class="status-badge">{overall.get('icon', '❓')} {overall.get('status', 'UNKNOWN')}</div>
        </div>
        
        <div class="grid">
            <!-- エージェント状態 -->
            <div class="card">
                <h2>🤖 エージェント状態</h2>
                {''.join([f'''
                <div class="metric">
                    <span class="metric-label">{name}</span>
                    <span class="metric-value {'status-ok' if info.get('healthy') else 'status-error'}">
                        {'✅ OK' if info.get('healthy') else '❌ ERROR'}
                    </span>
                </div>
                ''' for name, info in report.get('agents', {}).items()])}
            </div>
            
            <!-- テスト結果 -->
            <div class="card">
                <h2>🧪 テスト結果</h2>
                <div class="metric">
                    <span class="metric-label">総テスト数</span>
                    <span class="metric-value status-ok">{report.get('tests', {}).get('total_tests', 0)}件</span>
                </div>
                <div class="test-history">
                    <strong>履歴:</strong>
                    {''.join([f'''
                    <div class="test-item">
                        {datetime.fromisoformat(h['timestamp']).strftime('%H:%M:%S')} - {h['total_tests']}件
                    </div>
                    ''' for h in report.get('tests', {}).get('history', [])])}
                </div>
            </div>
            
            <!-- 連携状態 -->
            <div class="card">
                <h2>🔗 エージェント連携</h2>
                {''.join([f'''
                <div class="metric">
                    <span class="metric-label">{name}</span>
                    <span class="metric-value {'status-ok' if info.get('connected') else 'status-error'}">
                        {'✅' if info.get('connected') else '❌'}
                    </span>
                </div>
                ''' for name, info in report.get('integrations', {}).items()])}
            </div>
            
            <!-- タスク状態 -->
            <div class="card">
                <h2>📋 タスク状態</h2>
                <div class="metric">
                    <span class="metric-label">総タスク数</span>
                    <span class="metric-value">{report.get('tasks', {}).get('total', 0)}件</span>
                </div>
                {''.join([f'''
                <div class="metric">
                    <span class="metric-label">{status}</span>
                    <span class="metric-value">{count}件</span>
                </div>
                ''' for status, count in report.get('tasks', {}).get('by_status', {}).items()])}
            </div>
            
            <!-- ナレッジ状態 -->
            <div class="card">
                <h2>�� ナレッジシステム</h2>
                <div class="metric">
                    <span class="metric-label">総ナレッジ数</span>
                    <span class="metric-value status-ok">{report.get('knowledge', {}).get('total_entries', 0)}件</span>
                </div>
                <div class="metric">
                    <span class="metric-label">カテゴリ数</span>
                    <span class="metric-value">{report.get('knowledge', {}).get('total_categories', 0)}件</span>
                </div>
            </div>
        </div>
        
        <button class="refresh-btn" onclick="location.reload()">🔄 更新</button>
    </div>
    
    <script>
        // 60秒ごとに自動更新
        setTimeout(() => location.reload(), 60000);
    </script>
</body>
</html>
"""

    return html


def create_dashboard_file(output_path: str = "dashboard.html"):
    """ダッシュボードファイル作成"""
    from agents.observability.realtime_observer import RealtimeObserver

    observer = RealtimeObserver()
    report = observer.monitor_all()

    html = generate_html_dashboard(report)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n✅ ダッシュボード作成: {output_path}")
    print(f"📂 開くコマンド: open {output_path}")


if __name__ == "__main__":
    create_dashboard_file()
