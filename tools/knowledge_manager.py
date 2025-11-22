"""
ナレッジマネージャー（完全スキーマ対応版）
既存のSQLiteスキーマに完全対応
"""

import sys
import os
import sqlite3
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class KnowledgeManager:
    """ナレッジマネージャー（完全スキーマ対応版）"""
    
    def __init__(self):
        self.db_path = Path("/workspaces/gemini_AI_Agent/knowledge_system/database/knowledge.db")
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"データベースが見つかりません: {self.db_path}")
        
        # スキーマを確認
        self.schema = self._get_schema()
        self.columns = list(self.schema.keys())
    
    def _get_connection(self, timeout: float = 10.0):
        """接続を取得（タイムアウト付き）"""
        conn = sqlite3.connect(str(self.db_path), timeout=timeout)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn
    
    def _get_schema(self) -> Dict:
        """スキーマを取得（カラム名、型、NOT NULL制約）"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(knowledge_entries)")
        
        schema = {}
        for row in cursor.fetchall():
            # cid, name, type, notnull, dflt_value, pk
            col_name = row[1]
            schema[col_name] = {
                'type': row[2],
                'notnull': bool(row[3]),
                'default': row[4],
                'pk': bool(row[5])
            }
        
        conn.close()
        
        return schema
    
    def add_knowledge(
        self, 
        content: str, 
        source: str,
        metadata: Optional[Dict] = None,
        max_retries: int = 3
    ) -> str:
        """ナレッジを追加（完全スキーマ対応）"""
        
        # タイトルを生成（必須カラム対応）
        title = self._generate_title(source, metadata)
        
        # 詳細な説明文
        full_content = content
        if metadata:
            full_content += f"\n\n[メタデータ]\n"
            full_content += f"ソース: {source}\n"
            for key, value in metadata.items():
                full_content += f"{key}: {value}\n"
        
        for attempt in range(max_retries):
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                # スキーマに合わせて挿入
                # 必須カラムを特定
                insert_data = {
                    'content': full_content
                }
                
                # titleカラムがあれば追加
                if 'title' in self.schema:
                    insert_data['title'] = title
                
                # その他の既知カラム
                if 'source' in self.schema:
                    insert_data['source'] = source
                
                if 'metadata' in self.schema:
                    insert_data['metadata'] = json.dumps(metadata) if metadata else None
                
                # INSERT文を動的に生成
                columns = ', '.join(insert_data.keys())
                placeholders = ', '.join(['?'] * len(insert_data))
                values = tuple(insert_data.values())
                
                cursor.execute(f'''
                    INSERT INTO knowledge_entries ({columns})
                    VALUES ({placeholders})
                ''', values)
                
                entry_id = cursor.lastrowid
                
                conn.commit()
                conn.close()
                
                return f"entry_{entry_id}"
                
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 0.5
                    print(f"  ⏳ データベースロック - {wait_time}秒後にリトライ（{attempt + 1}/{max_retries}）")
                    time.sleep(wait_time)
                else:
                    raise
            
            finally:
                try:
                    conn.close()
                except:
                    pass
    
    def _generate_title(self, source: str, metadata: Optional[Dict] = None) -> str:
        """タイトルを生成"""
        if metadata and 'task_id' in metadata:
            return f"Phase 4A: {metadata['task_id']}"
        else:
            return f"Auto Generated: {source} - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def search_knowledge(self, query: str) -> List[Dict]:
        """ナレッジを検索"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        columns_str = ', '.join(self.columns)
        
        cursor.execute(f'''
            SELECT {columns_str}
            FROM knowledge_entries
            WHERE content LIKE ?
            ORDER BY id DESC
            LIMIT 10
        ''', (f'%{query}%',))
        
        results = []
        for row in cursor.fetchall():
            entry = {}
            for i, col in enumerate(self.columns):
                entry[col] = row[i]
            results.append(entry)
        
        conn.close()
        
        return results
    
    def get_all_entries(self, limit: int = 100) -> List[Dict]:
        """すべてのエントリを取得"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        columns_str = ', '.join(self.columns)
        
        cursor.execute(f'''
            SELECT {columns_str}
            FROM knowledge_entries
            ORDER BY id DESC
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            entry = {}
            for i, col in enumerate(self.columns):
                value = row[i]
                if col == 'content' and value and len(value) > 200:
                    value = value[:200] + '...'
                entry[col] = value
            results.append(entry)
        
        conn.close()
        
        return results
    
    def get_statistics(self) -> Dict:
        """統計情報を取得"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 総数
        cursor.execute('SELECT COUNT(*) FROM knowledge_entries')
        total = cursor.fetchone()[0]
        
        # 今日追加された数
        today = 0
        if 'created_at' in self.columns:
            cursor.execute('''
                SELECT COUNT(*) FROM knowledge_entries
                WHERE DATE(created_at) = DATE('now')
            ''')
            today = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_entries': total,
            'today_entries': today,
            'columns': self.columns,
            'schema': self.schema
        }

