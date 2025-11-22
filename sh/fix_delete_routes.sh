#!/bin/bash
# 削除機能完全実装

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 削除機能完全実装"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Flaskプロセス停止
echo "📍 STEP 1: Flaskプロセス停止"
pkill -f "knowledge_webapp.py" || echo "  プロセスなし"
sleep 2

# Flask本体を完全に再作成（削除機能付き）
echo ""
echo "📍 STEP 2: Flask本体（削除機能付き）完全再作成"

cat > app/knowledge_webapp.py << 'PYTHON'
"""
完全版Flask Webアプリ - ナレッジベース管理システム
削除機能完全実装版
"""

import sys
import os
import sqlite3
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
import io
import csv

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = 'knowledge-management-secret-key-2025'

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
    """sqlite3.Rowを辞書に変換"""
    result = {}
    for key in row.keys():
        value = row[key]
        if isinstance(value, bytes):
            try:
                value = value.decode('utf-8')
            except:
                value = str(value)
        result[key] = value
    return result

def backup_database():
    """データベースバックアップ"""
    backup_dir = Path('/workspaces/gemini_AI_Agent/knowledge_system/backups')
    backup_dir.mkdir(exist_ok=True)
    
    backup_path = backup_dir / f"knowledge_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2(DB_PATH, backup_path)
    
    return str(backup_path)

@app.route('/')
def index():
    """ホーム"""
    return render_template('index.html')

@app.route('/knowledge')
def knowledge_list():
    """ナレッジ一覧"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'DESC')
    
    query = request.args.get('q', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    columns = get_schema()
    
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
    
    cursor.execute(f'SELECT COUNT(*) as count FROM knowledge_entries WHERE {where_sql}', params)
    total = cursor.fetchone()['count']
    
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

@app.route('/manage')
def manage():
    """管理ページ"""
    return render_template('manage.html')

@app.route('/delete/single', methods=['POST'])
def delete_single():
    """個別削除（チェックボックス）"""
    print("🗑️ 削除リクエスト受信")
    
    entry_ids = request.form.getlist('entry_ids')
    print(f"削除対象ID: {entry_ids}")
    
    if not entry_ids:
        flash('削除するエントリを選択してください', 'warning')
        return redirect(url_for('knowledge_list'))
    
    # バックアップ
    backup_path = backup_database()
    print(f"バックアップ作成: {backup_path}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    deleted_count = 0
    for entry_id in entry_ids:
        cursor.execute('DELETE FROM knowledge_entries WHERE id = ?', (entry_id,))
        deleted_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"✅ {deleted_count}件削除完了")
    
    flash(f'{deleted_count}件のエントリを削除しました', 'success')
    flash(f'バックアップ: {backup_path}', 'info')
    
    return redirect(url_for('knowledge_list'))

@app.route('/delete/range', methods=['POST'])
def delete_range():
    """範囲削除"""
    id_from = request.form.get('id_from')
    id_to = request.form.get('id_to')
    
    if not id_from or not id_to:
        flash('IDの範囲を指定してください', 'warning')
        return redirect(url_for('manage'))
    
    backup_path = backup_database()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM knowledge_entries 
        WHERE id BETWEEN ? AND ?
    ''', (id_from, id_to))
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    flash(f'ID {id_from}～{id_to} の {deleted_count}件を削除しました', 'success')
    flash(f'バックアップ: {backup_path}', 'info')
    
    return redirect(url_for('manage'))

@app.route('/delete/bulk', methods=['POST'])
def delete_bulk():
    """一括削除"""
    condition = request.form.get('condition')
    date_from = request.form.get('date_from')
    date_to = request.form.get('date_to')
    
    if not condition:
        flash('削除条件を選択してください', 'warning')
        return redirect(url_for('manage'))
    
    backup_path = backup_database()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    deleted_count = 0
    
    if condition == 'date_range':
        cursor.execute('''
            DELETE FROM knowledge_entries 
            WHERE DATE(created_at) BETWEEN ? AND ?
        ''', (date_from, date_to))
        deleted_count = cursor.rowcount
    
    elif condition == 'test_entries':
        cursor.execute('''
            DELETE FROM knowledge_entries 
            WHERE title LIKE '%test%' OR title LIKE '%テスト%' 
            OR content LIKE '%test%' OR content LIKE '%テスト%'
        ''')
        deleted_count = cursor.rowcount
    
    elif condition == 'low_quality':
        cursor.execute('''
            DELETE FROM knowledge_entries 
            WHERE content LIKE '%quality_score:%'
            AND CAST(
                SUBSTR(
                    content,
                    INSTR(content, 'quality_score: ') + 15,
                    4
                ) AS REAL
            ) < 7.0
        ''')
        deleted_count = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    flash(f'{deleted_count}件のエントリを削除しました', 'success')
    flash(f'バックアップ: {backup_path}', 'info')
    
    return redirect(url_for('manage'))

@app.route('/stats')
def stats():
    """統計"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
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
    
    cursor.execute('''
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM knowledge_entries
        WHERE DATE(created_at) >= DATE('now', '-30 days')
        GROUP BY DATE(created_at)
        ORDER BY date
    ''')
    daily_stats = cursor.fetchall()
    
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
    """APIドキュメント"""
    return render_template('api_docs.html')

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
        output = io.StringIO()
        writer = csv.writer(output)
        
        columns = get_schema()
        writer.writerow(columns)
        
        for entry in entries:
            row = []
            for col in columns:
                value = entry[col]
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
        entries_dict = [row_to_dict(entry) for entry in entries]
        
        return jsonify({
            'total': len(entries_dict),
            'exported_at': datetime.now().isoformat(),
            'entries': entries_dict
        })

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("�� Flask Webアプリ起動（削除機能完全版）")
    print("=" * 80)
    print()
    print("📖 アクセス方法:")
    print("   1. VS Codeの「ポート」パネルを開く")
    print("   2. ポート5000の「ブラウザで開く」をクリック")
    print()
    print("🌐 URL:")
    print("   http://localhost:5000")
    print()
    print("🗑️ 削除機能:")
    print("   - /delete/single  : 個別削除（チェックボックス）")
    print("   - /delete/range   : 範囲削除")
    print("   - /delete/bulk    : 一括削除")
    print()
    print("=" * 80)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)

PYTHON

echo "  ✅ Flask本体（削除機能完全版）作成完了"

# バックアップディレクトリ作成
echo ""
echo "📍 STEP 3: バックアップディレクトリ作成"
mkdir -p knowledge_system/backups
echo "  ✅ knowledge_system/backups 作成完了"

# ルート確認
echo ""
echo "📍 STEP 4: 削除ルート確認"
if grep -q "/delete/single" app/knowledge_webapp.py; then
    echo "  ✅ /delete/single ルート確認"
else
    echo "  ❌ /delete/single ルートなし"
fi

if grep -q "/delete/range" app/knowledge_webapp.py; then
    echo "  ✅ /delete/range ルート確認"
else
    echo "  ❌ /delete/range ルートなし"
fi

if grep -q "/delete/bulk" app/knowledge_webapp.py; then
    echo "  ✅ /delete/bulk ルート確認"
else
    echo "  ❌ /delete/bulk ルートなし"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 削除機能完全実装完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Flask Webアプリを起動してください:"
echo ""
echo "   bash sh/start_knowledge_webapp.sh"
echo ""
echo "📖 テスト手順:"
echo "   1. http://localhost:5000/knowledge を開く"
echo "   2. チェックボックスでエントリを選択"
echo "   3. 「選択を削除」をクリック"
echo "   4. 確認ダイアログで「OK」"
echo "   5. 削除完了メッセージが表示される"
echo ""
echo "💾 バックアップ:"
echo "   knowledge_system/backups/ に自動保存"
echo ""

