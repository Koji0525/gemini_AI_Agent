#!/bin/bash
# 完全版Flask Webアプリ実装

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 完全版Flask Webアプリ実装"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: ディレクトリ構成作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: ディレクトリ構成作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

mkdir -p app/templates
mkdir -p app/static/css
mkdir -p app/static/js

echo "✅ ディレクトリ作成完了"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: Flask本体（knowledge_webapp.py）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Flask本体作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

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

@app.route('/api/knowledge')
def api_knowledge():
    """API: ナレッジ一覧"""
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
    
    return jsonify({
        'total': len(entries),
        'entries': [dict(entry) for entry in entries]
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
            writer.writerow([entry[col] for col in columns])
        
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'knowledge_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    
    elif format == 'json':
        # JSON生成
        data = [dict(entry) for entry in entries]
        
        return jsonify({
            'total': len(data),
            'exported_at': datetime.now().isoformat(),
            'entries': data
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

echo "✅ Flask本体作成完了"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: HTMLテンプレート
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: HTMLテンプレート作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# base.html
cat > app/templates/base.html << 'HTML'
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}ナレッジベース管理システム{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="/" class="logo">📚 ナレッジベース</a>
            <ul class="nav-links">
                <li><a href="/">ホーム</a></li>
                <li><a href="/knowledge">ナレッジ一覧</a></li>
                <li><a href="/stats">統計</a></li>
                <li><a href="/api/knowledge">API</a></li>
            </ul>
        </div>
    </nav>
    
    <main class="container">
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        <p>© 2025 ナレッジベース管理システム | Phase 4A</p>
    </footer>
</body>
</html>
HTML

# index.html
cat > app/templates/index.html << 'HTML'
{% extends "base.html" %}

{% block content %}
<div class="hero">
    <h1>📚 ナレッジベース管理システム</h1>
    <p>すべてのナレッジを見える化・管理</p>
    
    <div class="quick-stats">
        <div class="stat-card">
            <h3>主な機能</h3>
            <ul>
                <li>✅ スプレッドシート風表示</li>
                <li>✅ 全データ閲覧可能</li>
                <li>✅ 高度な検索・フィルター</li>
                <li>✅ 品質チェック</li>
                <li>✅ CSV/JSONエクスポート</li>
            </ul>
        </div>
        
        <div class="stat-card">
            <h3>クイックアクセス</h3>
            <div class="quick-links">
                <a href="/knowledge" class="btn btn-primary">📋 ナレッジ一覧</a>
                <a href="/stats" class="btn btn-secondary">📊 統計・分析</a>
                <a href="/api/knowledge" class="btn btn-secondary">🔌 API</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
HTML

# knowledge_list.html（スプレッドシート風）
cat > app/templates/knowledge_list.html << 'HTML'
{% extends "base.html" %}

{% block title %}ナレッジ一覧 - ナレッジベース{% endblock %}

{% block content %}
<div class="knowledge-list">
    <h1>📋 ナレッジ一覧</h1>
    
    <!-- 検索・フィルター -->
    <div class="filter-panel">
        <form method="GET" action="/knowledge">
            <div class="filter-row">
                <input type="text" name="q" placeholder="🔍 キーワード検索..." value="{{ query }}" class="search-input">
                
                <input type="date" name="date_from" value="{{ date_from }}" placeholder="開始日">
                <input type="date" name="date_to" value="{{ date_to }}" placeholder="終了日">
                
                <select name="per_page">
                    <option value="50" {% if per_page == 50 %}selected{% endif %}>50件</option>
                    <option value="100" {% if per_page == 100 %}selected{% endif %}>100件</option>
                    <option value="200" {% if per_page == 200 %}selected{% endif %}>200件</option>
                </select>
                
                <button type="submit" class="btn btn-primary">検索</button>
                <a href="/knowledge" class="btn btn-secondary">リセット</a>
            </div>
        </form>
    </div>
    
    <!-- 統計情報 -->
    <div class="info-bar">
        <span>📊 総件数: <strong>{{ total }}</strong>件</span>
        <span>📄 表示: {{ (page-1) * per_page + 1 }}～{{ [page * per_page, total] | min }}件</span>
        <span>📃 ページ: {{ page }}/{{ total_pages }}</span>
        
        <div class="export-links">
            <a href="/export/csv" class="btn-small">CSV</a>
            <a href="/export/json" class="btn-small">JSON</a>
        </div>
    </div>
    
    <!-- スプレッドシート風テーブル -->
    <div class="table-container">
        <table class="knowledge-table">
            <thead>
                <tr>
                    {% for col in columns %}
                    <th>
                        <a href="?page={{ page }}&sort_by={{ col }}&sort_order={% if sort_by == col and sort_order == 'ASC' %}DESC{% else %}ASC{% endif %}&q={{ query }}&date_from={{ date_from }}&date_to={{ date_to }}&per_page={{ per_page }}">
                            {{ col }}
                            {% if sort_by == col %}
                                {% if sort_order == 'ASC' %}▲{% else %}▼{% endif %}
                            {% endif %}
                        </a>
                    </th>
                    {% endfor %}
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                {% for entry in entries %}
                <tr>
                    {% for col in columns %}
                    <td>
                        {% if col == 'content' %}
                            {{ entry[col][:100] }}...
                        {% else %}
                            {{ entry[col] }}
                        {% endif %}
                    </td>
                    {% endfor %}
                    <td>
                        <a href="/knowledge/{{ entry['id'] }}" class="btn-small">詳細</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    <!-- ページネーション -->
    <div class="pagination">
        {% if page > 1 %}
        <a href="?page={{ page - 1 }}&sort_by={{ sort_by }}&sort_order={{ sort_order }}&q={{ query }}&date_from={{ date_from }}&date_to={{ date_to }}&per_page={{ per_page }}" class="btn">« 前へ</a>
        {% endif %}
        
        {% for p in range(1, total_pages + 1) %}
            {% if p == page %}
                <span class="current-page">{{ p }}</span>
            {% elif p <= 3 or p > total_pages - 3 or (p >= page - 2 and p <= page + 2) %}
                <a href="?page={{ p }}&sort_by={{ sort_by }}&sort_order={{ sort_order }}&q={{ query }}&date_from={{ date_from }}&date_to={{ date_to }}&per_page={{ per_page }}">{{ p }}</a>
            {% elif p == 4 or p == total_pages - 3 %}
                <span>...</span>
            {% endif %}
        {% endfor %}
        
        {% if page < total_pages %}
        <a href="?page={{ page + 1 }}&sort_by={{ sort_by }}&sort_order={{ sort_order }}&q={{ query }}&date_from={{ date_from }}&date_to={{ date_to }}&per_page={{ per_page }}" class="btn">次へ »</a>
        {% endif %}
    </div>
</div>
{% endblock %}
HTML

# knowledge_detail.html
cat > app/templates/knowledge_detail.html << 'HTML'
{% extends "base.html" %}

{% block title %}ナレッジ詳細 #{{ entry['id'] }}{% endblock %}

{% block content %}
<div class="knowledge-detail">
    <h1>📄 ナレッジ詳細 #{{ entry['id'] }}</h1>
    
    <div class="detail-card">
        <h2>{{ entry['title'] }}</h2>
        
        <div class="meta-info">
            <span>🆔 ID: {{ entry['id'] }}</span>
            <span>📅 作成日時: {{ entry['created_at'] }}</span>
        </div>
        
        <div class="content-section">
            <h3>内容</h3>
            <pre>{{ entry['content'] }}</pre>
        </div>
        
        <div class="actions">
            <a href="/knowledge" class="btn">← 一覧に戻る</a>
        </div>
    </div>
</div>
{% endblock %}
HTML

# stats.html
cat > app/templates/stats.html << 'HTML'
{% extends "base.html" %}

{% block title %}統計・分析{% endblock %}

{% block content %}
<div class="stats-page">
    <h1>📊 統計・分析</h1>
    
    <!-- サマリーカード -->
    <div class="stats-summary">
        <div class="stat-card">
            <h3>総エントリ数</h3>
            <p class="stat-number">{{ total }}</p>
            <span>件</span>
        </div>
        
        <div class="stat-card">
            <h3>今日追加</h3>
            <p class="stat-number">{{ today }}</p>
            <span>件</span>
        </div>
        
        <div class="stat-card">
            <h3>今週追加</h3>
            <p class="stat-number">{{ this_week }}</p>
            <span>件</span>
        </div>
    </div>
    
    <!-- 日別統計 -->
    <div class="chart-section">
        <h2>📈 日別追加数（過去30日）</h2>
        <div class="chart">
            <table class="chart-table">
                <tbody>
                    {% for stat in daily_stats %}
                    <tr>
                        <td class="date">{{ stat['date'] }}</td>
                        <td class="bar">
                            <div class="bar-fill" style="width: {{ stat['count'] * 10 }}px">
                                {{ stat['count'] }}
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    
    <!-- 品質分布 -->
    <div class="chart-section">
        <h2>⭐ 品質スコア分布</h2>
        <div class="quality-chart">
            {% for score, count in quality_distribution.items() %}
            <div class="quality-bar">
                <span class="label">{{ score }}</span>
                <div class="bar-fill" style="width: {{ count * 5 }}px">
                    {{ count }}件
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
{% endblock %}
HTML

echo "✅ HTMLテンプレート作成完了"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: CSS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: CSS作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > app/static/css/style.css << 'CSS'
/* ナレッジベース管理システム CSS */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #f5f5f5;
    color: #333;
    line-height: 1.6;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}

/* ナビゲーション */
.navbar {
    background: #2c3e50;
    color: white;
    padding: 1rem 0;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.navbar .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-size: 1.5rem;
    font-weight: bold;
    color: white;
    text-decoration: none;
}

.nav-links {
    display: flex;
    list-style: none;
    gap: 2rem;
}

.nav-links a {
    color: white;
    text-decoration: none;
    transition: opacity 0.3s;
}

.nav-links a:hover {
    opacity: 0.8;
}

/* ヒーロー */
.hero {
    text-align: center;
    padding: 3rem 0;
}

.hero h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.quick-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}

.stat-card {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.stat-card h3 {
    margin-bottom: 1rem;
    color: #2c3e50;
}

.stat-card ul {
    list-style: none;
    text-align: left;
}

.stat-card li {
    padding: 0.5rem 0;
}

.quick-links {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

/* ボタン */
.btn {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    border-radius: 5px;
    text-decoration: none;
    transition: all 0.3s;
    border: none;
    cursor: pointer;
    font-size: 1rem;
}

.btn-primary {
    background: #3498db;
    color: white;
}

.btn-primary:hover {
    background: #2980b9;
}

.btn-secondary {
    background: #95a5a6;
    color: white;
}

.btn-secondary:hover {
    background: #7f8c8d;
}

.btn-small {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
}

/* フィルターパネル */
.filter-panel {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    margin-bottom: 1rem;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.filter-row {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}

.search-input {
    flex: 1;
    min-width: 300px;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 1rem;
}

input[type="date"], select {
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 1rem;
}

/* 情報バー */
.info-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: white;
    padding: 1rem;
    border-radius: 5px;
    margin-bottom: 1rem;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.info-bar span {
    margin-right: 2rem;
}

.export-links {
    display: flex;
    gap: 0.5rem;
}

/* テーブル */
.table-container {
    background: white;
    border-radius: 10px;
    overflow-x: auto;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.knowledge-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
}

.knowledge-table thead {
    background: #34495e;
    color: white;
    position: sticky;
    top: 0;
}

.knowledge-table th {
    padding: 1rem;
    text-align: left;
    font-weight: 600;
}

.knowledge-table th a {
    color: white;
    text-decoration: none;
    display: block;
}

.knowledge-table th a:hover {
    opacity: 0.8;
}

.knowledge-table td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #ecf0f1;
}

.knowledge-table tbody tr:hover {
    background: #f8f9fa;
}

/* ページネーション */
.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0.5rem;
    margin-top: 2rem;
    flex-wrap: wrap;
}

.pagination a, .pagination span {
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    border-radius: 5px;
    text-decoration: none;
    color: #333;
    transition: all 0.3s;
}

.pagination a:hover {
    background: #3498db;
    color: white;
    border-color: #3498db;
}

.current-page {
    background: #3498db;
    color: white;
    border-color: #3498db;
}

/* 詳細ページ */
.knowledge-detail {
    max-width: 1000px;
    margin: 2rem auto;
}

.detail-card {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.detail-card h2 {
    color: #2c3e50;
    margin-bottom: 1rem;
}

.meta-info {
    display: flex;
    gap: 2rem;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #ecf0f1;
}

.meta-info span {
    color: #7f8c8d;
}

.content-section {
    margin: 2rem 0;
}

.content-section h3 {
    color: #2c3e50;
    margin-bottom: 1rem;
}

.content-section pre {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 5px;
    overflow-x: auto;
    line-height: 1.6;
    white-space: pre-wrap;
}

.actions {
    margin-top: 2rem;
}

/* 統計ページ */
.stats-summary {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 2rem;
    margin-bottom: 2rem;
}

.stat-number {
    font-size: 3rem;
    font-weight: bold;
    color: #3498db;
    margin: 0.5rem 0;
}

.chart-section {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.chart-section h2 {
    color: #2c3e50;
    margin-bottom: 1.5rem;
}

.chart-table {
    width: 100%;
}

.chart-table td {
    padding: 0.5rem 0;
}

.chart-table .date {
    width: 120px;
    color: #7f8c8d;
}

.bar-fill {
    background: #3498db;
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 3px;
    display: inline-block;
    min-width: 30px;
    text-align: center;
}

.quality-chart {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.quality-bar {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.quality-bar .label {
    width: 100px;
    font-weight: 600;
}

/* フッター */
footer {
    text-align: center;
    padding: 2rem;
    color: #7f8c8d;
    margin-top: 4rem;
}
CSS

echo "✅ CSS作成完了"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 5: Flask依存インストール
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5: Flask依存インストール"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

pip install Flask --break-system-packages --quiet

echo "✅ Flask インストール完了"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 6: 起動スクリプト作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 6: 起動スクリプト作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > sh/start_knowledge_webapp.sh << 'START'
#!/bin/bash
# Flask Webアプリ起動

cd /workspaces/gemini_AI_Agent

python3 app/knowledge_webapp.py

START

chmod +x sh/start_knowledge_webapp.sh

echo "✅ 起動スクリプト作成完了"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 完全版Flask Webアプリ実装完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📂 ファイル構成:"
echo "  app/"
echo "    ├── knowledge_webapp.py  # Flask本体"
echo "    ├── templates/           # HTMLテンプレート"
echo "    │   ├── base.html"
echo "    │   ├── index.html"
echo "    │   ├── knowledge_list.html"
echo "    │   ├── knowledge_detail.html"
echo "    │   └── stats.html"
echo "    └── static/"
echo "        └── css/"
echo "            └── style.css"
echo ""
echo "🚀 起動方法:"
echo "  bash sh/start_knowledge_webapp.sh"
echo ""
echo "📖 アクセス方法:"
echo "  1. VS Codeの「ポート」パネルを開く"
echo "  2. ポート5000の「ブラウザで開く」をクリック"
echo "  3. http://localhost:5000 にアクセス"
echo ""
echo "✨ 主な機能:"
echo "  ✅ スプレッドシート風表示"
echo "  ✅ 全データ閲覧可能（521件すべて）"
echo "  ✅ キーワード検索"
echo "  ✅ 日付フィルター"
echo "  ✅ ソート機能"
echo "  ✅ ページネーション（50/100/200件表示）"
echo "  ✅ 詳細表示"
echo "  ✅ 統計・グラフ"
echo "  ✅ CSV/JSONエクスポート"
echo "  ✅ JSON API"
echo ""

