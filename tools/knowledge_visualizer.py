"""
ナレッジベース可視化ツール（既存スキーマ適応版）
SQLiteデータベースの実際のスキーマに合わせて実装
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
    """ナレッジベース可視化（既存スキーマ適応版）"""
    
    def __init__(self):
        self.db_path = Path("/workspaces/gemini_AI_Agent/knowledge_system/database/knowledge.db")
        
        if self.db_path.exists():
            self.columns = self._get_columns()
        else:
            self.columns = []
    
    def _get_columns(self) -> List[str]:
        """カラム名を取得"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(knowledge_entries)")
        columns = [row[1] for row in cursor.fetchall()]
        
        conn.close()
        
        return columns
    
    def generate_report(self) -> str:
        """レポートを生成"""
        print(f"\n{'=' * 80}")
        print(f"📚 ナレッジベース完全レポート")
        print('=' * 80)
        print()
        
        if not self.db_path.exists():
            print("❌ データベースが見つかりません")
            return ""
        
        # スキーマ情報
        print("📋 データベース情報")
        print("-" * 80)
        print(f"  データベース: {self.db_path}")
        print(f"  カラム: {', '.join(self.columns)}")
        print()
        
        # 統計情報
        stats = self._get_statistics()
        
        print("📊 統計情報")
        print("-" * 80)
        print(f"  総エントリ数: {stats['total']}件")
        if 'today' in stats:
            print(f"  今日追加: {stats['today']}件")
        if 'this_week' in stats:
            print(f"  今週追加: {stats['this_week']}件")
        if 'this_month' in stats:
            print(f"  今月追加: {stats['this_month']}件")
        print()
        
        # 最新エントリ
        print("📝 最新エントリ（最新20件）")
        print("-" * 80)
        latest = self._get_latest_entries(20)
        
        for i, entry in enumerate(latest, 1):
            print(f"\n  [{i}] ID: {entry.get('id', 'N/A')}")
            
            # 作成日時
            if 'created_at' in entry:
                print(f"      作成日時: {entry['created_at']}")
            
            # 内容
            content = entry.get('content', '')
            if content:
                # 最初の200文字
                content_preview = content[:200]
                print(f"      内容: {content_preview}...")
                
                # メタデータが含まれていれば抽出
                if '[メタデータ]' in content:
                    print(f"      ※ メタデータ含む")
        
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
        
        stats = {}
        
        # 総数
        cursor.execute('SELECT COUNT(*) FROM knowledge_entries')
        stats['total'] = cursor.fetchone()[0]
        
        # created_atカラムがあれば日付別統計
        if 'created_at' in self.columns:
            # 今日
            cursor.execute('''
                SELECT COUNT(*) FROM knowledge_entries
                WHERE DATE(created_at) = DATE('now')
            ''')
            stats['today'] = cursor.fetchone()[0]
            
            # 今週
            cursor.execute('''
                SELECT COUNT(*) FROM knowledge_entries
                WHERE DATE(created_at) >= DATE('now', '-7 days')
            ''')
            stats['this_week'] = cursor.fetchone()[0]
            
            # 今月
            cursor.execute('''
                SELECT COUNT(*) FROM knowledge_entries
                WHERE DATE(created_at) >= DATE('now', 'start of month')
            ''')
            stats['this_month'] = cursor.fetchone()[0]
        
        conn.close()
        
        return stats
    
    def _get_latest_entries(self, limit: int = 20) -> List[Dict]:
        """最新エントリを取得"""
        conn = sqlite3.connect(str(self.db_path))
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
                entry[col] = row[i]
            results.append(entry)
        
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
        .entry-date {{
            color: #888;
        }}
        .entry-content {{
            margin-top: 10px;
            color: #ccc;
            white-space: pre-wrap;
            max-height: 200px;
            overflow-y: auto;
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
            <h2>📋 データベース情報</h2>
            <div class="stat">
                <span>カラム:</span>
                <span>{', '.join(self.columns)}</span>
            </div>
        </div>
        
        <div class="stats-card">
            <h2>📊 統計情報</h2>
            <div class="stat">
                <span>総エントリ数:</span>
                <span>{stats['total']}件</span>
            </div>
'''
        
        if 'today' in stats:
            html += f'''
            <div class="stat">
                <span>今日追加:</span>
                <span>{stats['today']}件</span>
            </div>
'''
        
        if 'this_week' in stats:
            html += f'''
            <div class="stat">
                <span>今週追加:</span>
                <span>{stats['this_week']}件</span>
            </div>
'''
        
        if 'this_month' in stats:
            html += f'''
            <div class="stat">
                <span>今月追加:</span>
                <span>{stats['this_month']}件</span>
            </div>
'''
        
        html += '''
        </div>
        
        <div class="stats-card">
            <h2>📝 最新エントリ（最新20件）</h2>
'''
        
        for entry in latest:
            entry_id = entry.get('id', 'N/A')
            created_at = entry.get('created_at', 'N/A')
            content = entry.get('content', '')
            
            # コンテンツをHTMLエスケープ
            content = content.replace('<', '&lt;').replace('>', '&gt;')
            
            # 最初の500文字
            if len(content) > 500:
                content = content[:500] + '...'
            
            html += f'''
            <div class="entry">
                <div class="entry-id">ID: {entry_id}</div>
'''
            
            if created_at != 'N/A':
                html += f'<div class="entry-date">作成: {created_at}</div>'
            
            html += f'''
                <div class="entry-content">{content}</div>
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

