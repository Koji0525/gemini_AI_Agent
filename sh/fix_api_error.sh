#!/bin/bash
# APIエラー修正

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 APIエラー修正"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Flask本体を修正
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

@app.route('/api/knowledge')
def api_knowledge():
    """API: ナレッジ一覧（bytes型対応）"""
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
    print("�� URL:")
    print("   http://localhost:5000")
    print()
    print("=" * 80)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)

PYTHON

echo "✅ APIエラー修正完了"
echo ""
echo "🔄 Flask Webアプリを再起動してください:"
echo "   1. 現在のFlaskサーバーを停止（Ctrl+C）"
echo "   2. bash sh/start_knowledge_webapp.sh で再起動"
echo "   3. http://localhost:5000/api/knowledge にアクセス"
echo ""

