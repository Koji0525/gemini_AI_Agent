#!/bin/bash
# ナレッジベース完全統合と可視化

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 ナレッジベース完全統合と可視化"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: 既存ナレッジシステムの確認
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: 既存ナレッジシステムの確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📂 SQLiteデータベース確認:"
if [ -f "knowledge_system/database/knowledge.db" ]; then
    echo "  ✅ knowledge_system/database/knowledge.db 存在"
    
    # エントリ数確認
    ENTRY_COUNT=$(sqlite3 knowledge_system/database/knowledge.db "SELECT COUNT(*) FROM knowledge_entries;" 2>/dev/null || echo "0")
    echo "  📊 登録件数: ${ENTRY_COUNT}件"
    
    # テーブル構造確認
    echo ""
    echo "  📋 テーブル構造:"
    sqlite3 knowledge_system/database/knowledge.db ".schema knowledge_entries" 2>/dev/null || echo "    エラー: スキーマ取得失敗"
else
    echo "  ❌ SQLiteデータベースが見つかりません"
fi

echo ""
echo "📂 新規ナレッジベース確認:"
if [ -d "knowledge_base" ]; then
    echo "  ✅ knowledge_base/ 存在"
    
    # エントリ数確認
    JSON_COUNT=$(find knowledge_base/entries -name "*.json" 2>/dev/null | wc -l)
    echo "  📊 JSONエントリ数: ${JSON_COUNT}件"
    
    SIMPLE_COUNT=$(find knowledge_base/simple -name "*.json" 2>/dev/null | wc -l)
    echo "  📊 簡易エントリ数: ${SIMPLE_COUNT}件"
else
    echo "  ⚠️  knowledge_base/ が見つかりません"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: 既存システムに統合したKnowledgeManager v2作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: SQLite統合版KnowledgeManager作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > tools/knowledge_manager.py << 'PYTHON'
"""
ナレッジマネージャー（SQLite統合版）
既存のSQLiteデータベースを使用
"""

import sys
import os
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class KnowledgeManager:
    """ナレッジマネージャー（SQLite統合版）"""
    
    def __init__(self):
        self.db_path = Path("/workspaces/gemini_AI_Agent/knowledge_system/database/knowledge.db")
        
        # データベースが存在しない場合は作成
        if not self.db_path.exists():
            self.db_path.parent.mkdir(exist_ok=True, parents=True)
            self._init_database()
    
    def _init_database(self):
        """データベースを初期化"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                source TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_knowledge(
        self, 
        content: str, 
        source: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """ナレッジを追加"""
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute('''
            INSERT INTO knowledge_entries (content, source, metadata)
            VALUES (?, ?, ?)
        ''', (content, source, metadata_json))
        
        entry_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return f"entry_{entry_id}"
    
    def search_knowledge(self, query: str) -> List[Dict]:
        """ナレッジを検索"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 簡易的なキーワード検索
        cursor.execute('''
            SELECT id, content, source, metadata, created_at
            FROM knowledge_entries
            WHERE content LIKE ?
            ORDER BY created_at DESC
            LIMIT 10
        ''', (f'%{query}%',))
        
        results = []
        for row in cursor.fetchall():
            entry = {
                'id': row[0],
                'content': row[1],
                'source': row[2],
                'metadata': json.loads(row[3]) if row[3] else {},
                'created_at': row[4]
            }
            results.append(entry)
        
        conn.close()
        
        return results
    
    def get_all_entries(self, limit: int = 100) -> List[Dict]:
        """すべてのエントリを取得"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, content, source, metadata, created_at
            FROM knowledge_entries
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            entry = {
                'id': row[0],
                'content': row[1][:200] + '...' if len(row[1]) > 200 else row[1],
                'source': row[2],
                'metadata': json.loads(row[3]) if row[3] else {},
                'created_at': row[4]
            }
            results.append(entry)
        
        conn.close()
        
        return results
    
    def get_statistics(self) -> Dict:
        """統計情報を取得"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 総数
        cursor.execute('SELECT COUNT(*) FROM knowledge_entries')
        total = cursor.fetchone()[0]
        
        # 今日追加された数
        cursor.execute('''
            SELECT COUNT(*) FROM knowledge_entries
            WHERE DATE(created_at) = DATE('now')
        ''')
        today = cursor.fetchone()[0]
        
        # ソース別の統計
        cursor.execute('''
            SELECT source, COUNT(*) as count
            FROM knowledge_entries
            GROUP BY source
            ORDER BY count DESC
            LIMIT 10
        ''')
        
        sources = {}
        for row in cursor.fetchall():
            sources[row[0]] = row[1]
        
        conn.close()
        
        return {
            'total_entries': total,
            'today_entries': today,
            'sources': sources
        }

PYTHON

echo "✅ SQLite統合版KnowledgeManager作成"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: ナレッジベース可視化ツール作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: ナレッジベース可視化ツール作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > tools/knowledge_visualizer.py << 'PYTHON'
"""
ナレッジベース可視化ツール
SQLiteデータベースの中身を完全表示
"""

import sys
import os
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class KnowledgeVisualizer:
    """ナレッジベース可視化"""
    
    def __init__(self):
        self.db_path = Path("/workspaces/gemini_AI_Agent/knowledge_system/database/knowledge.db")
        
    def generate_report(self) -> str:
        """レポートを生成"""
        print(f"\n{'=' * 80}")
        print(f"📚 ナレッジベース完全レポート")
        print('=' * 80)
        print()
        
        if not self.db_path.exists():
            print("❌ データベースが見つかりません")
            return ""
        
        # 統計情報
        stats = self._get_statistics()
        
        print("📊 統計情報")
        print("-" * 80)
        print(f"  総エントリ数: {stats['total']}件")
        print(f"  今日追加: {stats['today']}件")
        print(f"  今週追加: {stats['this_week']}件")
        print(f"  今月追加: {stats['this_month']}件")
        print()
        
        # ソース別統計
        print("📋 ソース別統計")
        print("-" * 80)
        for source, count in stats['sources'].items():
            print(f"  {source}: {count}件")
        print()
        
        # 最新エントリ
        print("📝 最新エントリ（最新20件）")
        print("-" * 80)
        latest = self._get_latest_entries(20)
        
        for i, entry in enumerate(latest, 1):
            print(f"\n  [{i}] ID: {entry['id']}")
            print(f"      ソース: {entry['source']}")
            print(f"      作成日時: {entry['created_at']}")
            
            # メタデータ
            if entry['metadata']:
                print(f"      メタデータ:")
                metadata = json.loads(entry['metadata']) if isinstance(entry['metadata'], str) else entry['metadata']
                if 'task_id' in metadata:
                    print(f"        - タスクID: {metadata['task_id']}")
                if 'quality_score' in metadata:
                    print(f"        - 品質スコア: {metadata['quality_score']}")
            
            # 内容（最初の200文字）
            content = entry['content'][:200]
            print(f"      内容: {content}...")
        
        print()
        print("=" * 80)
        
        # HTMLレポート生成
        html_path = self._generate_html_report(stats, latest)
        print(f"\n📄 HTMLレポート: {html_path}")
        
        return str(html_path)
    
    def _get_statistics(self) -> Dict:
        """統計情報を取得"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 総数
        cursor.execute('SELECT COUNT(*) FROM knowledge_entries')
        total = cursor.fetchone()[0]
        
        # 今日
        cursor.execute('''
            SELECT COUNT(*) FROM knowledge_entries
            WHERE DATE(created_at) = DATE('now')
        ''')
        today = cursor.fetchone()[0]
        
        # 今週
        cursor.execute('''
            SELECT COUNT(*) FROM knowledge_entries
            WHERE DATE(created_at) >= DATE('now', '-7 days')
        ''')
        this_week = cursor.fetchone()[0]
        
        # 今月
        cursor.execute('''
            SELECT COUNT(*) FROM knowledge_entries
            WHERE DATE(created_at) >= DATE('now', 'start of month')
        ''')
        this_month = cursor.fetchone()[0]
        
        # ソース別
        cursor.execute('''
            SELECT source, COUNT(*) as count
            FROM knowledge_entries
            GROUP BY source
            ORDER BY count DESC
        ''')
        
        sources = {}
        for row in cursor.fetchall():
            sources[row[0] if row[0] else 'unknown'] = row[1]
        
        conn.close()
        
        return {
            'total': total,
            'today': today,
            'this_week': this_week,
            'this_month': this_month,
            'sources': sources
        }
    
    def _get_latest_entries(self, limit: int = 20) -> List[Dict]:
        """最新エントリを取得"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, content, source, metadata, created_at
            FROM knowledge_entries
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'content': row[1],
                'source': row[2],
                'metadata': row[3],
                'created_at': row[4]
            })
        
        conn.close()
        
        return results
    
    def _generate_html_report(self, stats: Dict, latest: List[Dict]) -> str:
        """HTMLレポートを生成"""
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ナレッジベースレポート</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            background: #1a1a1a;
            color: #00ff00;
            padding: 20px;
            margin: 0;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
        }}
        .stats-card {{
            background: #2a2a2a;
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }}
        .stat {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #444;
        }}
        .entry {{
            background: #2a2a2a;
            border-left: 4px solid #00ff00;
            padding: 15px;
            margin: 10px 0;
        }}
        .entry-id {{
            color: #00aaff;
            font-weight: bold;
        }}
        .entry-source {{
            color: #ffaa00;
        }}
        .entry-date {{
            color: #888;
        }}
        .timestamp {{
            text-align: center;
            color: #888;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 ナレッジベースレポート</h1>
        
        <div class="stats-card">
            <h2>📊 統計情報</h2>
            <div class="stat">
                <span>総エントリ数:</span>
                <span>{stats['total']}件</span>
            </div>
            <div class="stat">
                <span>今日追加:</span>
                <span>{stats['today']}件</span>
            </div>
            <div class="stat">
                <span>今週追加:</span>
                <span>{stats['this_week']}件</span>
            </div>
            <div class="stat">
                <span>今月追加:</span>
                <span>{stats['this_month']}件</span>
            </div>
        </div>
        
        <div class="stats-card">
            <h2>📋 ソース別統計</h2>
'''
        
        for source, count in stats['sources'].items():
            html += f'''
            <div class="stat">
                <span>{source}:</span>
                <span>{count}件</span>
            </div>
'''
        
        html += '''
        </div>
        
        <div class="stats-card">
            <h2>📝 最新エントリ（最新20件）</h2>
'''
        
        for entry in latest:
            metadata = json.loads(entry['metadata']) if entry['metadata'] else {}
            task_id = metadata.get('task_id', 'N/A')
            quality_score = metadata.get('quality_score', 'N/A')
            
            content = entry['content'][:200] + '...' if len(entry['content']) > 200 else entry['content']
            content = content.replace('<', '&lt;').replace('>', '&gt;')
            
            html += f'''
            <div class="entry">
                <div class="entry-id">ID: {entry['id']}</div>
                <div class="entry-source">ソース: {entry['source']}</div>
                <div class="entry-date">作成: {entry['created_at']}</div>
'''
            
            if task_id != 'N/A':
                html += f'<div>タスクID: {task_id}</div>'
            if quality_score != 'N/A':
                html += f'<div>品質スコア: {quality_score}</div>'
            
            html += f'''
                <div style="margin-top: 10px; color: #ccc;">{content}</div>
            </div>
'''
        
        html += f'''
        </div>
        
        <div class="timestamp">
            生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
'''
        
        html_path = Path("knowledge_report.html")
        html_path.write_text(html)
        
        return str(html_path)

PYTHON

echo "✅ ナレッジベース可視化ツール作成"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: 実行スクリプト作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: 実行スクリプト作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > sh/show_knowledge_base.sh << 'SHOW'
#!/bin/bash
# ナレッジベース表示

cd /workspaces/gemini_AI_Agent

python3 << PYTHON
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.knowledge_visualizer import KnowledgeVisualizer

visualizer = KnowledgeVisualizer()
html_path = visualizer.generate_report()

print(f"\n📖 HTMLレポートを開くには:")
print(f"   open {html_path}")

PYTHON

SHOW

chmod +x sh/show_knowledge_base.sh

echo "✅ 実行スクリプト作成"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 5: テスト登録と確認
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5: テスト登録と確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 << PYTHON
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.knowledge_manager import KnowledgeManager
from datetime import datetime

print("🧪 KnowledgeManager統合テスト")
print()

# 初期化
km = KnowledgeManager()

# 統計取得（登録前）
stats_before = km.get_statistics()
print(f"📊 登録前の統計:")
print(f"   総エントリ数: {stats_before['total_entries']}件")
print(f"   今日追加: {stats_before['today_entries']}件")
print()

# テスト登録
print("📝 テストエントリを登録中...")
entry_id = km.add_knowledge(
    content=f"Phase 4Aテストエントリ - {datetime.now().isoformat()}",
    source="phase4a_test",
    metadata={
        'task_id': 'test_phase4a',
        'quality_score': 10.0,
        'test': True
    }
)

print(f"✅ 登録完了: {entry_id}")
print()

# 統計取得（登録後）
stats_after = km.get_statistics()
print(f"📊 登録後の統計:")
print(f"   総エントリ数: {stats_after['total_entries']}件")
print(f"   今日追加: {stats_after['today_entries']}件")
print()

# 増加確認
if stats_after['total_entries'] > stats_before['total_entries']:
    print(f"✅ エントリ数が増加しました！")
    print(f"   {stats_before['total_entries']}件 → {stats_after['total_entries']}件 (+{stats_after['total_entries'] - stats_before['total_entries']})")
else:
    print(f"⚠️  エントリ数が増加していません")

PYTHON

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ナレッジベース完全統合完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "�� 現在の状態:"
echo "  SQLiteデータベース: knowledge_system/database/knowledge.db"
echo "  統合: ✅ 完了"
echo ""
echo "📖 ナレッジベース表示:"
echo "  bash sh/show_knowledge_base.sh"
echo ""
echo "🔍 SQLiteで直接確認:"
echo "  sqlite3 knowledge_system/database/knowledge.db \"SELECT COUNT(*) FROM knowledge_entries;\""
echo ""
echo "📄 HTMLレポート:"
echo "  open knowledge_report.html"
echo ""

# 自動実行
read -p "今すぐナレッジベースを表示しますか？ [Y/n] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📚 ナレッジベース表示"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    bash sh/show_knowledge_base.sh
fi

