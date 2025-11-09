#!/usr/bin/env python3
"""
データベース操作ユーティリティ - 確実動作版
"""
import sqlite3
import os
from pathlib import Path

def get_db_path():
    """データベースパスを確実に取得"""
    # スクリプトの位置から相対パスで確実に特定
    current_dir = Path(__file__).parent.parent
    db_path = current_dir / 'database' / 'knowledge.db'
    return str(db_path)

def get_db_connection():
    """データベース接続を確実に取得"""
    db_path = get_db_path()
    print(f"🔧 データベースパス: {db_path}")
    return sqlite3.connect(db_path)

def add_knowledge(title, content, category="general", tags=""):
    """ナレッジを確実に追加"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 実際のテーブル構造に基づいた挿入
        cursor.execute('''
            INSERT INTO knowledge_entries (title, cause, category, tags)
            VALUES (?, ?, ?, ?)
        ''', (title, content, category, tags))
        
        knowledge_id = cursor.lastrowid
        conn.commit()
        print(f"✅ ナレッジ登録成功: ID {knowledge_id}")
        return knowledge_id
        
    except Exception as e:
        print(f"❌ ナレッジ登録失敗: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def search_knowledge(query, limit=5):
    """ナレッジを確実に検索"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id, title, cause, category, tags 
            FROM knowledge_entries 
            WHERE cause LIKE ? OR title LIKE ?
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'category': row[3],
                'tags': row[4]
            })
        
        print(f"✅ 検索成功: {len(results)}件")
        return results
        
    except Exception as e:
        print(f"❌ 検索失敗: {e}")
        return []
    finally:
        conn.close()

def get_stats():
    """システム統計を確実に取得"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT COUNT(*) FROM knowledge_entries')
        total_entries = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM vector_mappings')
        total_mappings = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT category) FROM knowledge_entries')
        categories_count = cursor.fetchone()[0]
        
        sync_rate = (total_mappings / total_entries * 100) if total_entries > 0 else 0
        
        stats = {
            'total_entries': total_entries,
            'total_mappings': total_mappings,
            'categories_count': categories_count,
            'sync_rate': sync_rate
        }
        
        print(f"✅ 統計取得成功: {total_entries}エントリー, {sync_rate:.1f}%同期")
        return stats
        
    except Exception as e:
        print(f"❌ 統計取得失敗: {e}")
        return {}
    finally:
        conn.close()
