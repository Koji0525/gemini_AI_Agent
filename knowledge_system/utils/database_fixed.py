#!/usr/bin/env python3
import sqlite3
import os
import json
import numpy as np
import faiss
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """確実に動作するデータベース管理クラス"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.ensure_database()
    
    def ensure_database(self):
        """データベースの存在を確認し、必要なら作成"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        if not os.path.exists(self.db_path):
            logger.info(f"データベースファイルが存在しないため作成: {self.db_path}")
            self._create_tables()
        else:
            logger.info(f"既存のデータベースを使用: {self.db_path}")
    
    def _create_tables(self):
        """テーブルを作成"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 知識エントリーテーブル
        cursor.execute('''
            CREATE TABLE knowledge_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                tags TEXT DEFAULT '',
                scenario TEXT DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                embedding BLOB,
                vector_synced BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # ベクトルマッピングテーブル
        cursor.execute('''
            CREATE TABLE vector_mappings (
                entry_id INTEGER,
                vector_index INTEGER,
                FOREIGN KEY (entry_id) REFERENCES knowledge_entries (id)
            )
        ''')
        
        # インデックス作成
        cursor.execute('CREATE INDEX idx_title ON knowledge_entries(title)')
        cursor.execute('CREATE INDEX idx_category ON knowledge_entries(category)')
        cursor.execute('CREATE INDEX idx_created ON knowledge_entries(created_at)')
        cursor.execute('CREATE INDEX idx_synced ON knowledge_entries(vector_synced)')
        
        conn.commit()
        conn.close()
        logger.info("データベーステーブルを作成完了")
    
    def get_connection(self):
        """データベース接続を取得"""
        return sqlite3.connect(self.db_path)
    
    def insert_knowledge_entry(self, entry_data: Dict[str, Any]) -> bool:
        """ナレッジエントリーを挿入"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO knowledge_entries 
                (title, content, category, tags, scenario, embedding)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                entry_data.get('title', ''),
                entry_data.get('content', ''),
                entry_data.get('category', 'general'),
                entry_data.get('tags', ''),
                entry_data.get('scenario', 'general'),
                entry_data.get('embedding')
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"ナレッジエントリーを登録: {entry_data.get('title')}")
            return True
            
        except Exception as e:
            logger.error(f"ナレッジ登録失敗: {e}")
            return False
    
    def get_unsynced_entries(self) -> List[Dict[str, Any]]:
        """未同期のエントリーを取得"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, content, tags, category
            FROM knowledge_entries 
            WHERE vector_synced = FALSE
        ''')
        
        entries = []
        for row in cursor.fetchall():
            entries.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'tags': row[3],
                'category': row[4]
            })
        
        conn.close()
        return entries
    
    def mark_as_synced(self, entry_id: int) -> bool:
        """エントリーを同期済みとしてマーク"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE knowledge_entries 
                SET vector_synced = TRUE 
                WHERE id = ?
            ''', (entry_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"同期マーク失敗: {e}")
            return False
    
    def add_vector_mapping(self, entry_id: int, vector_index: int) -> bool:
        """ベクトルマッピングを追加"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO vector_mappings (entry_id, vector_index)
                VALUES (?, ?)
            ''', (entry_id, vector_index))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"ベクトルマッピング追加失敗: {e}")
            return False
    
    def get_sync_stats(self) -> Dict[str, Any]:
        """同期統計を取得"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM knowledge_entries')
        total_entries = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM knowledge_entries WHERE vector_synced = TRUE')
        synced_entries = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM vector_mappings')
        vector_mappings = cursor.fetchone()[0]
        
        conn.close()
        
        sync_percentage = (synced_entries / total_entries * 100) if total_entries > 0 else 0
        
        return {
            'total_entries': total_entries,
            'synced_entries': synced_entries,
            'vector_mappings': vector_mappings,
            'sync_percentage': sync_percentage
        }
    
    def search_entries(self, query: str = None, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """キーワード検索"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        sql = '''
            SELECT id, title, content, category, tags, created_at
            FROM knowledge_entries 
            WHERE 1=1
        '''
        params = []
        
        if query:
            sql += ' AND (title LIKE ? OR content LIKE ? OR tags LIKE ?)'
            search_term = f'%{query}%'
            params.extend([search_term, search_term, search_term])
        
        if category:
            sql += ' AND category = ?'
            params.append(category)
        
        sql += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(sql, params)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'category': row[3],
                'tags': row[4],
                'created_at': row[5]
            })
        
        conn.close()
        return results
    
    def add_to_vector_index(self, entry_id: int, embedding: np.ndarray, index_dir: str) -> bool:
        """ベクトルインデックスに追加"""
        try:
            os.makedirs(index_dir, exist_ok=True)
            index_file = os.path.join(index_dir, "knowledge.index")
            mapping_file = os.path.join(index_dir, "index_mapping.json")
            
            # 既存のインデックスを読み込むか新規作成
            if os.path.exists(index_file):
                index = faiss.read_index(index_file)
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    mapping = json.load(f)
            else:
                dimension = embedding.shape[0]
                index = faiss.IndexFlatIP(dimension)  # 内積類似度
                mapping = []
            
            # エンベディングを正規化（内積類似度のため）
            embedding_norm = embedding / np.linalg.norm(embedding)
            
            # インデックスに追加
            index.add(np.array([embedding_norm]).astype('float32'))
            
            # マッピングを更新
            new_index = len(mapping)
            mapping.append(entry_id)
            
            # 保存
            faiss.write_index(index, index_file)
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(mapping, f, ensure_ascii=False, indent=2)
            
            # データベースを更新
            self.mark_as_synced(entry_id)
            self.add_vector_mapping(entry_id, new_index)
            
            logger.info(f"ベクトルインデックスに追加: エントリーID {entry_id}, インデックス {new_index}")
            return True
            
        except Exception as e:
            logger.error(f"ベクトルインデックス追加失敗: {e}")
            return False
    
    def vector_search(self, query_embedding: np.ndarray, top_k: int = 5, index_dir: str = None) -> List[Dict[str, Any]]:
        """ベクトル検索"""
        try:
            if index_dir is None:
                index_dir = os.path.join(os.path.dirname(self.db_path), "faiss_index")
            
            index_file = os.path.join(index_dir, "knowledge.index")
            mapping_file = os.path.join(index_dir, "index_mapping.json")
            
            if not os.path.exists(index_file):
                logger.warning("ベクトルインデックスが存在しません")
                return []
            
            # インデックスとマッピングを読み込み
            index = faiss.read_index(index_file)
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mapping = json.load(f)
            
            # クエリエンベディングを正規化
            query_embedding_norm = query_embedding / np.linalg.norm(query_embedding)
            
            # 検索実行
            distances, indices = index.search(np.array([query_embedding_norm]).astype('float32'), top_k)
            
            # 結果を取得
            conn = self.get_connection()
            cursor = conn.cursor()
            
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(mapping):
                    entry_id = mapping[idx]
                    cursor.execute('''
                        SELECT id, title, content, category, tags
                        FROM knowledge_entries 
                        WHERE id = ?
                    ''', (entry_id,))
                    
                    row = cursor.fetchone()
                    if row:
                        results.append({
                            'id': row[0],
                            'title': row[1],
                            'content': row[2],
                            'category': row[3],
                            'tags': row[4],
                            'similarity': float(distance)
                        })
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"ベクトル検索失敗: {e}")
            return []

# テスト用
if __name__ == "__main__":
    db = DatabaseManager("test.db")
    stats = db.get_sync_stats()
    print(f"統計: {stats}")
