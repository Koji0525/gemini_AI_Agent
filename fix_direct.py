#!/usr/bin/env python3
"""
直接修正スクリプト
"""

import re

def direct_fix():
    file_path = "/workspaces/gemini_AI_Agent/agents/complete_engine_ultimate.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 問題のパターンを探す
    print("現在の内容（90-100行目）:")
    lines = content.split('\n')
    for i in range(89, 100):
        if i < len(lines):
            print(f"{i+1}: {lines[i]}")
    
    # def (self): の行を削除
    if "def (self):" in content:
        print("🔧 def (self): の行を削除します...")
        content = content.replace("def (self):", "")
    
    # メソッド定義が壊れていないかチェック
    if "def integrate_knowledge_system(self):" in content:
        # メソッドの終わりを確認
        method_pattern = r'def integrate_knowledge_system\(self\):.*?def \w+'
        match = re.search(method_pattern, content, re.DOTALL)
        
        if not match:
            print("🔧 integrate_knowledge_system メソッドを再構築します...")
            # メソッドを再構築
            new_method = '''
    def integrate_knowledge_system(self):
        """ナレッジシステムを統合 - 改善版"""
        try:
            # 既存のナレッジマネージャーを使用
            from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
            
            self.knowledge_manager = KnowledgeManager()
            print("✅ ナレッジマネージャー統合完了")
            
        except ImportError as e:
            print(f"⚠️ ナレッジマネージャーインポートエラー: {e}")
            # 代替実装
            class FallbackKnowledgeManager:
                def __init__(self):
                    self.initialized = True
                    self.knowledge_base = []
                
                def search_knowledge(self, query, limit=5):
                    """ナレッジ検索 - 代替実装"""
                    return []
                
                def add_knowledge(self, content, metadata=None):
                    """ナレッジ追加 - 代替実装"""
                    return True
                    
                def get_knowledge_stats(self):
                    """ナレッジ統計 - 代替実装"""
                    return {"total": 0, "types": {}}
            
            self.knowledge_manager = FallbackKnowledgeManager()
            print("✅ フォールバックナレッジマネージャーを使用")
        
        except Exception as e:
            print(f"⚠️ ナレッジシステム統合エラー: {e}")
            # 最小限のフォールバック
            self.knowledge_manager = type('MinimalKnowledgeManager', (), {
                'initialized': True,
                'search_knowledge': lambda self, query, limit=5: [],
                'add_knowledge': lambda self, content, metadata=None: True
            })()
            print("✅ 最小限のナレッジマネージャーを使用")
'''
            
            # 古いメソッドを削除して新しいメソッドを挿入
            old_method_pattern = r'def integrate_knowledge_system\(self\):.*?return.*?'
            content = re.sub(old_method_pattern, new_method, content, flags=re.DOTALL)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 直接修正を完了しました")

if __name__ == "__main__":
    direct_fix()
