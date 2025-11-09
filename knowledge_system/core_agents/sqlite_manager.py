"""
SQLiteデータベース管理モジュール
運用ルール6準拠: 1000行以下、単一責任
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class SQLiteKnowledgeManager:
    """ナレッジベースのSQLite管理"""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._setup_database()

    def _setup_database(self):
        """データベースとテーブルの初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # ナレッジエントリーテーブル
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge_entries (
                id TEXT PRIMARY KEY,
                scenario TEXT NOT NULL,
                cause TEXT,
                solution TEXT NOT NULL,
                learnings TEXT,  -- JSON array
                prevention TEXT, -- JSON array
                success_rate REAL DEFAULT 0.0,
                confidence REAL DEFAULT 0.0,
                title TEXT,
                category TEXT,
                priority TEXT DEFAULT '中',
                task_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                quality_score INTEGER DEFAULT 0,
                verified BOOLEAN DEFAULT FALSE,
                tags TEXT,  -- JSON array
                view_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                source_system TEXT DEFAULT 'migration'
            )
        """
        )

        # インデックス作成（検索高速化）
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scenario ON knowledge_entries(scenario)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON knowledge_entries(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_type ON knowledge_entries(task_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON knowledge_entries(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_confidence ON knowledge_entries(confidence)")

        # ベクトルマッピングテーブル（FAISS用）
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS vector_mappings (
                vector_index INTEGER PRIMARY KEY,
                knowledge_id TEXT NOT NULL,
                FOREIGN KEY (knowledge_id) REFERENCES knowledge_entries(id)
            )
        """
        )

        conn.commit()
        conn.close()
        print(f"✅ データベース初期化完了: {self.db_path}")

    def insert_knowledge(self, knowledge: Dict[str, Any]) -> str:
        """ナレッジを登録"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # IDの生成
        knowledge_id = knowledge.get("id", f"KNOW_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")

        # JSON配列の変換
        learnings = json.dumps(knowledge.get("learnings", []), ensure_ascii=False)
        prevention = json.dumps(knowledge.get("prevention", []), ensure_ascii=False)
        tags = json.dumps(knowledge.get("tags", []), ensure_ascii=False)

        cursor.execute(
            """
            INSERT OR REPLACE INTO knowledge_entries (
                id, scenario, cause, solution, learnings, prevention,
                success_rate, confidence, title, category, priority, task_type,
                quality_score, tags, source_system
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                knowledge_id,
                knowledge.get("scenario", ""),
                knowledge.get("cause", ""),
                knowledge.get("solution", ""),
                learnings,
                prevention,
                knowledge.get("success_rate", 0.0),
                knowledge.get("confidence", 0.0),
                knowledge.get("title", ""),
                knowledge.get("category", ""),
                knowledge.get("priority", "中"),
                knowledge.get("task_type", ""),
                knowledge.get("quality_score", 0),
                tags,
                knowledge.get("source_system", "migration"),
            ),
        )

        conn.commit()
        conn.close()
        return knowledge_id

    def search_by_keyword(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """キーワード検索"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM knowledge_entries
            WHERE scenario LIKE ? OR solution LIKE ? OR cause LIKE ?
            ORDER BY confidence DESC, success_rate DESC
            LIMIT ?
        """,
            (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", limit),
        )

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        # JSON文字列をリストに変換
        for result in results:
            result["learnings"] = json.loads(result.get("learnings", "[]"))
            result["prevention"] = json.loads(result.get("prevention", "[]"))
            result["tags"] = json.loads(result.get("tags", "[]"))

        return results

    def get_knowledge_by_id(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        """IDでナレッジを取得"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM knowledge_entries WHERE id = ?", (knowledge_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            result = dict(row)
            result["learnings"] = json.loads(result.get("learnings", "[]"))
            result["prevention"] = json.loads(result.get("prevention", "[]"))
            result["tags"] = json.loads(result.get("tags", "[]"))
            return result
        return None

    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM knowledge_entries")
        total_count = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(confidence) FROM knowledge_entries")
        avg_confidence = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT AVG(success_rate) FROM knowledge_entries")
        avg_success_rate = cursor.fetchone()[0] or 0.0

        cursor.execute(
            "SELECT category, COUNT(*) as count FROM knowledge_entries GROUP BY category"
        )
        categories = {row[0]: row[1] for row in cursor.fetchall()}

        conn.close()

        return {
            "total_knowledge": total_count,
            "avg_confidence": round(avg_confidence, 2),
            "avg_success_rate": round(avg_success_rate, 2),
            "categories": categories,
        }
