#!/bin/bash
# APIページをHTML化

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 APIページHTML化（既存連携保護）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: Flask本体を修正（APIルート追加）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cat > app/knowledge_webapp.py << 'PYTHON'
"""
完全版Flask Webアプリ - ナレッジベース管理システム
すべてのナレッジをスプレッドシート風に表示・管理
"""

import sys
import os
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file
import io
import csv

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

DB_PATH = '/workspaces/gemini_AI_Agent/knowledge_system/database/knowledge.db'

def get_db_connection():
    """データベース接続"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_schema():
    """スキーマ取得"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(knowledge_entries)")
    columns = [row['name'] for row in cursor.fetchall()]
    conn.close()
    return columns

def row_to_dict(row):
    """sqlite3.Rowを辞書に変換（bytes型を処理）"""
    result = {}
    for key in row.keys():
        value = row[key]
        
        # bytes型を文字列に変換
        if isinstance(value, bytes):
            try:
                value = value.decode('utf-8')
            except:
                value = str(value)
        
        result[key] = value
    
    return result

@app.route('/')
def index():
    """ホーム"""
    return render_template('index.html')

@app.route('/knowledge')
def knowledge_list():
    """ナレッジ一覧（スプレッドシート風）"""
    
    # パラメータ取得
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'DESC')
    
    # フィルター
    query = request.args.get('q', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # スキーマ取得
    columns = get_schema()
    
    # WHERE句構築
    where_clauses = []
    params = []
    
    if query:
        where_clauses.append('(title LIKE ? OR content LIKE ?)')
        params.extend([f'%{query}%', f'%{query}%'])
    
    if date_from:
        where_clauses.append('DATE(created_at) >= ?')
        params.append(date_from)
    
    if date_to:
        where_clauses.append('DATE(created_at) <= ?')
        params.append(date_to)
    
    where_sql = ' AND '.join(where_clauses) if where_clauses else '1=1'
    
    # 総件数取得
    cursor.execute(f'SELECT COUNT(*) as count FROM knowledge_entries WHERE {where_sql}', params)
    total = cursor.fetchone()['count']
    
    # データ取得
    offset = (page - 1) * per_page
    
    sql = f'''
        SELECT *
        FROM knowledge_entries
        WHERE {where_sql}
        ORDER BY {sort_by} {sort_order}
        LIMIT ? OFFSET ?
    '''
    
    cursor.execute(sql, params + [per_page, offset])
    entries = cursor.fetchall()
    
    conn.close()
    
    # ページネーション計算
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('knowledge_list.html',
                          entries=entries,
                          columns=columns,
                          page=page,
                          per_page=per_page,
                          total=total,
                          total_pages=total_pages,
                          sort_by=sort_by,
                          sort_order=sort_order,
                          query=query,
                          date_from=date_from,
                          date_to=date_to)

@app.route('/knowledge/<int:entry_id>')
def knowledge_detail(entry_id):
    """ナレッジ詳細"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM knowledge_entries WHERE id = ?', (entry_id,))
    entry = cursor.fetchone()
    
    conn.close()
    
    if entry is None:
        return "エントリが見つかりません", 404
    
    return render_template('knowledge_detail.html', entry=entry)

@app.route('/stats')
def stats():
    """統計・分析"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 基本統計
    cursor.execute('SELECT COUNT(*) as total FROM knowledge_entries')
    total = cursor.fetchone()['total']
    
    cursor.execute('''
        SELECT COUNT(*) as today 
        FROM knowledge_entries 
        WHERE DATE(created_at) = DATE('now')
    ''')
    today = cursor.fetchone()['today']
    
    cursor.execute('''
        SELECT COUNT(*) as week 
        FROM knowledge_entries 
        WHERE DATE(created_at) >= DATE('now', '-7 days')
    ''')
    this_week = cursor.fetchone()['week']
    
    # 日別統計（過去30日）
    cursor.execute('''
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM knowledge_entries
        WHERE DATE(created_at) >= DATE('now', '-30 days')
        GROUP BY DATE(created_at)
        ORDER BY date
    ''')
    daily_stats = cursor.fetchall()
    
    # 品質スコア分布（メタデータから抽出）
    cursor.execute('''
        SELECT content
        FROM knowledge_entries
        WHERE content LIKE '%quality_score%'
    ''')
    entries_with_quality = cursor.fetchall()
    
    quality_distribution = {
        '10.0': 0,
        '9.0-9.9': 0,
        '8.0-8.9': 0,
        '7.0-7.9': 0,
        '< 7.0': 0
    }
    
    for entry in entries_with_quality:
        content = entry['content']
        if 'quality_score: 10.0' in content:
            quality_distribution['10.0'] += 1
        elif 'quality_score: 9' in content:
            quality_distribution['9.0-9.9'] += 1
        elif 'quality_score: 8' in content:
            quality_distribution['8.0-8.9'] += 1
        elif 'quality_score: 7' in content:
            quality_distribution['7.0-7.9'] += 1
    
    conn.close()
    
    return render_template('stats.html',
                          total=total,
                          today=today,
                          this_week=this_week,
                          daily_stats=daily_stats,
                          quality_distribution=quality_distribution)

@app.route('/api')
def api_docs():
    """APIドキュメントページ（HTML）"""
    return render_template('api_docs.html')

@app.route('/api/knowledge')
def api_knowledge():
    """API: ナレッジ一覧（JSON）"""
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 100))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if query:
        cursor.execute('''
            SELECT * FROM knowledge_entries
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY id DESC
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', limit))
    else:
        cursor.execute('''
            SELECT * FROM knowledge_entries
            ORDER BY id DESC
            LIMIT ?
        ''', (limit,))
    
    entries = cursor.fetchall()
    conn.close()
    
    # bytes型を処理して辞書に変換
    entries_dict = [row_to_dict(entry) for entry in entries]
    
    return jsonify({
        'total': len(entries_dict),
        'entries': entries_dict
    })

@app.route('/export/<format>')
def export(format):
    """エクスポート"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM knowledge_entries ORDER BY id DESC')
    entries = cursor.fetchall()
    conn.close()
    
    if format == 'csv':
        # CSV生成
        output = io.StringIO()
        writer = csv.writer(output)
        
        # ヘッダー
        columns = get_schema()
        writer.writerow(columns)
        
        # データ
        for entry in entries:
            row = []
            for col in columns:
                value = entry[col]
                # bytes型を文字列に変換
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-8')
                    except:
                        value = str(value)
                row.append(value)
            writer.writerow(row)
        
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'knowledge_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    
    elif format == 'json':
        # JSON生成（bytes型対応）
        entries_dict = [row_to_dict(entry) for entry in entries]
        
        return jsonify({
            'total': len(entries_dict),
            'exported_at': datetime.now().isoformat(),
            'entries': entries_dict
        })

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("🚀 Flask Webアプリ起動")
    print("=" * 80)
    print()
    print("📖 アクセス方法:")
    print("   1. VS Codeの「ポート」パネルを開く")
    print("   2. ポート5000の「ブラウザで開く」をクリック")
    print("   3. またはURLを直接開く")
    print()
    print("🌐 URL:")
    print("   http://localhost:5000")
    print()
    print("=" * 80)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)

PYTHON

echo "✅ Flask本体修正完了"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: APIドキュメントページ作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cat > app/templates/api_docs.html << 'HTML'
{% extends "base.html" %}

{% block title %}API ドキュメント{% endblock %}

{% block content %}
<div class="api-docs">
    <h1>🔌 API ドキュメント</h1>
    
    <div class="api-section">
        <h2>概要</h2>
        <p>ナレッジベース管理システムのREST APIです。JSON形式でデータを取得できます。</p>
    </div>
    
    <div class="api-section">
        <h2>📋 エンドポイント一覧</h2>
        
        <!-- エンドポイント1: ナレッジ一覧 -->
        <div class="endpoint-card">
            <div class="endpoint-header">
                <span class="method get">GET</span>
                <code class="endpoint-path">/api/knowledge</code>
            </div>
            
            <div class="endpoint-body">
                <h3>説明</h3>
                <p>ナレッジエントリの一覧を取得します。</p>
                
                <h3>パラメータ</h3>
                <table class="param-table">
                    <thead>
                        <tr>
                            <th>パラメータ</th>
                            <th>型</th>
                            <th>説明</th>
                            <th>デフォルト</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><code>q</code></td>
                            <td>string</td>
                            <td>検索キーワード</td>
                            <td>-</td>
                        </tr>
                        <tr>
                            <td><code>limit</code></td>
                            <td>integer</td>
                            <td>取得件数（最大100件）</td>
                            <td>100</td>
                        </tr>
                    </tbody>
                </table>
                
                <h3>使用例</h3>
                <div class="code-block">
                    <pre><code># 全件取得
curl http://localhost:5000/api/knowledge

# 検索（Phase 4A）
curl "http://localhost:5000/api/knowledge?q=Phase+4A"

# 件数指定（10件）
curl "http://localhost:5000/api/knowledge?limit=10"</code></pre>
                </div>
                
                <h3>レスポンス例</h3>
                <div class="code-block">
                    <pre><code>{
  "total": 528,
  "entries": [
    {
      "id": 528,
      "title": "Phase 4A: 7_24時間稼働最終確認_023321_04",
      "content": "# 7_24時間稼働最終確認...",
      "created_at": "2025-11-21 18:07:08",
      "category": "general",
      "tags": "",
      "vector_synced": 0
    },
    ...
  ]
}</code></pre>
                </div>
                
                <h3>テスト実行</h3>
                <button class="btn btn-primary" onclick="testAPI('/api/knowledge')">
                    このAPIを実行
                </button>
            </div>
        </div>
    </div>
    
    <div class="api-section">
        <h2>💾 エクスポート</h2>
        
        <div class="export-options">
            <div class="export-card">
                <h3>CSV形式</h3>
                <p>全データをCSV形式でダウンロード</p>
                <a href="/export/csv" class="btn btn-primary">CSV ダウンロード</a>
            </div>
            
            <div class="export-card">
                <h3>JSON形式</h3>
                <p>全データをJSON形式でダウンロード</p>
                <a href="/export/json" class="btn btn-secondary">JSON ダウンロード</a>
            </div>
        </div>
    </div>
    
    <div class="api-section">
        <h2>�� レスポンスフィールド</h2>
        
        <table class="field-table">
            <thead>
                <tr>
                    <th>フィールド</th>
                    <th>型</th>
                    <th>説明</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><code>id</code></td>
                    <td>integer</td>
                    <td>エントリID（ユニーク）</td>
                </tr>
                <tr>
                    <td><code>title</code></td>
                    <td>string</td>
                    <td>タイトル</td>
                </tr>
                <tr>
                    <td><code>content</code></td>
                    <td>string</td>
                    <td>本文（Markdown形式）</td>
                </tr>
                <tr>
                    <td><code>created_at</code></td>
                    <td>datetime</td>
                    <td>作成日時</td>
                </tr>
                <tr>
                    <td><code>category</code></td>
                    <td>string</td>
                    <td>カテゴリ</td>
                </tr>
                <tr>
                    <td><code>tags</code></td>
                    <td>string</td>
                    <td>タグ（カンマ区切り）</td>
                </tr>
            </tbody>
        </table>
    </div>
    
    <div class="api-section">
        <h2>🔗 統合例</h2>
        
        <h3>Python</h3>
        <div class="code-block">
            <pre><code>import requests

# ナレッジ一覧取得
response = requests.get('http://localhost:5000/api/knowledge')
data = response.json()

print(f"総件数: {data['total']}")
for entry in data['entries'][:5]:
    print(f"[{entry['id']}] {entry['title']}")

# 検索
response = requests.get('http://localhost:5000/api/knowledge', 
                       params={'q': 'Phase 4A', 'limit': 10})
results = response.json()
print(f"検索結果: {results['total']}件")</code></pre>
        </div>
        
        <h3>JavaScript</h3>
        <div class="code-block">
            <pre><code>// ナレッジ一覧取得
fetch('http://localhost:5000/api/knowledge')
    .then(response => response.json())
    .then(data => {
        console.log(`総件数: ${data.total}`);
        data.entries.forEach(entry => {
            console.log(`[${entry.id}] ${entry.title}`);
        });
    });

// 検索
fetch('http://localhost:5000/api/knowledge?q=Phase+4A&limit=10')
    .then(response => response.json())
    .then(results => {
        console.log(`検索結果: ${results.total}件`);
    });</code></pre>
        </div>
    </div>
</div>

<div id="api-result" class="api-result" style="display: none;">
    <h3>API実行結果</h3>
    <pre id="result-content"></pre>
</div>

<script>
function testAPI(endpoint) {
    const resultDiv = document.getElementById('api-result');
    const resultContent = document.getElementById('result-content');
    
    resultDiv.style.display = 'block';
    resultContent.textContent = '実行中...';
    
    fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            resultContent.textContent = JSON.stringify(data, null, 2);
        })
        .catch(error => {
            resultContent.textContent = `エラー: ${error}`;
        });
}
</script>

<style>
.api-docs {
    max-width: 1200px;
    margin: 0 auto;
}

.api-section {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.api-section h2 {
    color: #2c3e50;
    margin-bottom: 1.5rem;
    border-bottom: 3px solid #3498db;
    padding-bottom: 0.5rem;
}

.endpoint-card {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    margin-bottom: 2rem;
    overflow: hidden;
}

.endpoint-header {
    background: #34495e;
    color: white;
    padding: 1rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.method {
    padding: 0.3rem 0.8rem;
    border-radius: 4px;
    font-weight: bold;
    font-size: 0.9rem;
}

.method.get {
    background: #27ae60;
}

.endpoint-path {
    color: white;
    font-size: 1.1rem;
}

.endpoint-body {
    padding: 1.5rem;
}

.endpoint-body h3 {
    color: #2c3e50;
    margin-top: 1.5rem;
    margin-bottom: 1rem;
}

.param-table, .field-table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
}

.param-table th, .field-table th {
    background: #34495e;
    color: white;
    padding: 0.75rem;
    text-align: left;
}

.param-table td, .field-table td {
    padding: 0.75rem;
    border-bottom: 1px solid #ecf0f1;
}

.param-table code, .field-table code {
    background: #ecf0f1;
    padding: 0.2rem 0.5rem;
    border-radius: 3px;
    color: #e74c3c;
}

.code-block {
    background: #2c3e50;
    color: #ecf0f1;
    padding: 1.5rem;
    border-radius: 5px;
    overflow-x: auto;
    margin: 1rem 0;
}

.code-block pre {
    margin: 0;
}

.code-block code {
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    line-height: 1.6;
}

.export-options {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
}

.export-card {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 8px;
    text-align: center;
}

.export-card h3 {
    color: #2c3e50;
    margin-bottom: 1rem;
}

.api-result {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    margin-top: 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.api-result pre {
    background: #2c3e50;
    color: #ecf0f1;
    padding: 1.5rem;
    border-radius: 5px;
    overflow-x: auto;
    max-height: 500px;
}
</style>
{% endblock %}
HTML

echo "✅ APIドキュメントページ作成完了"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 修正完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📖 変更内容:"
echo "  1. /api → APIドキュメントページ（HTML）"
echo "  2. /api/knowledge → JSON API（既存通り）"
echo "  3. ナビゲーションの「API」は /api へリンク"
echo ""
echo "🔄 Flask Webアプリを再起動してください:"
echo "   1. 現在のサーバーを停止（Ctrl+C）"
echo "   2. bash sh/start_knowledge_webapp.sh"
echo ""
echo "✅ 確認項目:"
echo "   - http://localhost:5000/api → HTMLページ表示"
echo "   - http://localhost:5000/api/knowledge → JSON表示"
echo "   - 他のページ（/, /knowledge, /stats）→ 正常動作"
echo ""

