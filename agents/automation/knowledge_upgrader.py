"""
既存ナレッジ改善ツール
低品質なナレッジを実践的なナレッジに変換
"""

import sys
import os
import sqlite3
from pathlib import Path

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.knowledge_manager import KnowledgeManager
from agents.automation.knowledge_enhancer import KnowledgeEnhancer

class KnowledgeUpgrader:
    """既存ナレッジ改善"""
    
    def __init__(self):
        self.km = KnowledgeManager()
        self.enhancer = KnowledgeEnhancer()
    
    def upgrade_low_quality_entries(self, quality_threshold: float = 7.0):
        """低品質エントリを改善"""
        
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📈 既存ナレッジ改善")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()
        
        # 低品質エントリを取得
        low_quality = self._find_low_quality_entries(quality_threshold)
        
        print(f"📊 改善対象: {len(low_quality)}件")
        print()
        
        upgraded_count = 0
        
        for entry in low_quality:
            print(f"  🔄 改善中: ID {entry['id']}")
            
            try:
                # 高品質化
                enhanced = self.enhancer.enhance_knowledge(
                    entry['content'],
                    {
                        'task_id': entry.get('title', 'unknown'),
                        'quality_score': 5.0
                    }
                )
                
                # 更新
                self._update_entry(entry['id'], enhanced['content'])
                
                print(f"     ✅ 改善完了 (品質: {enhanced['quality_score']}/10)")
                upgraded_count += 1
                
            except Exception as e:
                print(f"     ❌ エラー: {e}")
        
        print()
        print(f"✅ {upgraded_count}/{len(low_quality)}件を改善しました")
    
    def _find_low_quality_entries(self, threshold: float) -> list:
        """低品質エントリを検索"""
        
        # 簡易的な品質判定基準
        # - contentが短い（< 300文字）
        # - コードブロックがない
        # - 構造化されていない
        
        conn = sqlite3.connect('/workspaces/gemini_AI_Agent/knowledge_system/database/knowledge.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM knowledge_entries
            WHERE LENGTH(content) < 300
            OR content NOT LIKE '%```%'
            ORDER BY id DESC
            LIMIT 50
        ''')
        
        entries = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return entries
    
    def _update_entry(self, entry_id: int, new_content: str):
        """エントリ更新"""
        
        conn = sqlite3.connect('/workspaces/gemini_AI_Agent/knowledge_system/database/knowledge.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE knowledge_entries
            SET content = ?
            WHERE id = ?
        ''', (new_content, entry_id))
        
        conn.commit()
        conn.close()

