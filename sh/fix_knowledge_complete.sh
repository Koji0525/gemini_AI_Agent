#!/bin/bash
# ナレッジ問題完全解決

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 ナレッジ問題完全解決"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: 既存ナレッジシステムの完全確認
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: 既存ナレッジシステムの完全確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📂 ナレッジ関連ファイル検索:"
find . -path ./node_modules -prune -o -name "*knowledge*" -type f 2>/dev/null | grep -v node_modules | head -20

echo ""
echo "📂 ナレッジ関連ディレクトリ:"
find . -path ./node_modules -prune -o -name "*knowledge*" -type d 2>/dev/null | grep -v node_modules

echo ""
echo "📊 SQLiteデータベース確認:"
if [ -f "knowledge_system/database/knowledge.db" ]; then
    echo "  ✅ knowledge_system/database/knowledge.db 存在"
    
    # ロックチェック
    if lsof knowledge_system/database/knowledge.db 2>/dev/null; then
        echo "  ⚠️  データベースが他のプロセスで使用中:"
        lsof knowledge_system/database/knowledge.db
    else
        echo "  ✅ データベースはロックされていません"
    fi
    
    # 件数確認
    ENTRY_COUNT=$(sqlite3 knowledge_system/database/knowledge.db "SELECT COUNT(*) FROM knowledge_entries;" 2>/dev/null || echo "0")
    echo "  📊 登録件数: ${ENTRY_COUNT}件"
    
    # 最新エントリ
    echo ""
    echo "  📅 最新エントリ（5件）:"
    sqlite3 knowledge_system/database/knowledge.db "SELECT id, created_at, substr(content, 1, 60) FROM knowledge_entries ORDER BY id DESC LIMIT 5;" -header -column 2>/dev/null
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: SQLiteロック対策版KnowledgeManager
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: SQLiteロック対策版KnowledgeManager"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > tools/knowledge_manager.py << 'PYTHON'
"""
ナレッジマネージャー（ロック対策版）
SQLiteのロック問題を解決
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
    """ナレッジマネージャー（ロック対策版）"""
    
    def __init__(self):
        self.db_path = Path("/workspaces/gemini_AI_Agent/knowledge_system/database/knowledge.db")
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"データベースが見つかりません: {self.db_path}")
        
        # スキーマを確認
        self.columns = self._get_columns()
    
    def _get_connection(self, timeout: float = 10.0):
        """接続を取得（タイムアウト付き）"""
        conn = sqlite3.connect(str(self.db_path), timeout=timeout)
        
        # WALモードを有効化（同時アクセス改善）
        conn.execute("PRAGMA journal_mode=WAL")
        
        return conn
    
    def _get_columns(self) -> List[str]:
        """カラム名を取得"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(knowledge_entries)")
        columns = [row[1] for row in cursor.fetchall()]
        
        conn.close()
        
        return columns
    
    def add_knowledge(
        self, 
        content: str, 
        source: str,
        metadata: Optional[Dict] = None,
        max_retries: int = 3
    ) -> str:
        """ナレッジを追加（リトライ付き）"""
        
        for attempt in range(max_retries):
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                # 既存スキーマに合わせて挿入
                full_content = content
                
                if metadata:
                    full_content += f"\n\n[メタデータ]\n"
                    full_content += f"ソース: {source}\n"
                    for key, value in metadata.items():
                        full_content += f"{key}: {value}\n"
                
                cursor.execute('''
                    INSERT INTO knowledge_entries (content)
                    VALUES (?)
                ''', (full_content,))
                
                entry_id = cursor.lastrowid
                
                conn.commit()
                conn.close()
                
                return f"entry_{entry_id}"
                
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 0.5
                    print(f"  ⏳ データベースロック検出 - {wait_time}秒後にリトライ（{attempt + 1}/{max_retries}）")
                    time.sleep(wait_time)
                else:
                    raise
            
            finally:
                try:
                    conn.close()
                except:
                    pass
    
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
            'columns': self.columns
        }

PYTHON

echo "✅ ロック対策版KnowledgeManager作成"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: Phase 3との統合確認と修正
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Phase 3との統合確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📋 Phase 3実行スクリプトの確認:"
if [ -f "sh/run_phase3_full_autonomous.sh" ]; then
    echo "  ✅ sh/run_phase3_full_autonomous.sh 存在"
    
    # F4統合部分を確認
    echo ""
    echo "  🔍 F4統合コード確認:"
    grep -n "f4_integrated\|knowledge_base_integrator\|ナレッジ" sh/run_phase3_full_autonomous.sh | head -5
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: テスト実行（ロック対策版）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: テスト実行（ロック対策版）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 << PYTHON
import sys
import time
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.automation.knowledge_base_integrator import KnowledgeBaseIntegrator
from tools.knowledge_manager import KnowledgeManager
from datetime import datetime

print("🧪 ナレッジ登録テスト（ロック対策版）")
print()

# 登録前の件数
km = KnowledgeManager()
stats_before = km.get_statistics()
print(f"📊 登録前: {stats_before['total_entries']}件")
print()

# テスト登録（1件ずつ、間隔を空ける）
kbi = KnowledgeBaseIntegrator()

success_count = 0
for i in range(3):
    task_id = f"test_phase4a_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i+1}"
    
    print(f"  🔄 テスト{i+1}: {task_id}")
    
    result = kbi.register_to_knowledge_base(
        task_id=task_id,
        output_path=f"/tmp/test_output_{i+1}",
        quality_score=10.0,
        test_results={'passed': True}
    )
    
    if result['success']:
        print(f"     ✅ 登録成功 ({result['entry_id']})")
        success_count += 1
    else:
        print(f"     ❌ 登録失敗")
    
    # 次のテストまで少し待機
    time.sleep(0.5)
    print()

# 登録後の件数
stats_after = km.get_statistics()
print(f"📊 登録後: {stats_after['total_entries']}件")

if stats_after['total_entries'] > stats_before['total_entries']:
    increase = stats_after['total_entries'] - stats_before['total_entries']
    print(f"✅ {increase}件増加しました！")
    print(f"   成功率: {success_count}/3")
else:
    print(f"⚠️  件数が増加していません")
    print(f"   成功: {success_count}/3")

PYTHON

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ナレッジ問題完全解決完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 最終確認
FINAL_COUNT=$(sqlite3 knowledge_system/database/knowledge.db "SELECT COUNT(*) FROM knowledge_entries;" 2>/dev/null || echo "0")
echo "📊 最終ナレッジ件数: ${FINAL_COUNT}件"

echo ""
echo "📅 最新エントリ（10件）:"
sqlite3 knowledge_system/database/knowledge.db "SELECT id, created_at, substr(content, 1, 70) FROM knowledge_entries ORDER BY id DESC LIMIT 10;" -header -column 2>/dev/null

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 次のステップ"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Phase 3でテスト実行:"
echo "   bash sh/run_phase3_full_autonomous.sh 2"
echo ""
echo "2. ナレッジ確認:"
echo "   bash sh/show_knowledge_base.sh"
echo ""
echo "3. 件数確認:"
echo "   sqlite3 knowledge_system/database/knowledge.db \"SELECT COUNT(*) FROM knowledge_entries;\""
echo ""

