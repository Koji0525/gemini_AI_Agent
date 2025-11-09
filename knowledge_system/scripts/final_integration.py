"""
IntegratedOrchestratorに完全統合（v30作成）
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 最新Orchestratorを特定
orchestrator_files = list(project_root.glob("scripts/integrated_orchestrator*.py"))
latest = max(orchestrator_files, key=lambda x: x.stat().st_mtime)

print(f"📌 ベース: {latest.name}")

# v30を作成
v30_path = project_root / "scripts" / "integrated_orchestrator_v30_knowledge.py"

# ベースファイルを読み込み
with open(latest, "r", encoding="utf-8") as f:
    content = f.read()

# 統合コードを追加
integration_code = '''
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ナレッジシステム統合 (v30新機能)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
import yaml
from pathlib import Path as KnowledgePath

# ナレッジマネージャー初期化用
def _init_knowledge_system():
    """ナレッジシステム初期化"""
    try:
        from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
        
        config_path = KnowledgePath(__file__).parent.parent / 'knowledge_system/configuration/knowledge_config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        db_path = KnowledgePath(__file__).parent.parent / config['database']['path']
        index_path = KnowledgePath(__file__).parent.parent / config['vector_search']['index_path']
        model_name = config['vector_search']['model_name']
        
        return KnowledgeManager(str(db_path), str(index_path), model_name)
    except Exception as e:
        print(f"⚠️ ナレッジシステム初期化エラー: {e}")
        return None
'''

# __init__の直後に追加するパターンを探す
import_section = content.find("import")
if import_section != -1:
    # importセクションの後に追加
    next_class = content.find("class", import_section)
    if next_class != -1:
        content = content[:next_class] + integration_code + "\n\n" + content[next_class:]

# __init__メソッドにナレッジマネージャーを追加
init_pattern = "def __init__(self"
init_pos = content.find(init_pattern)
if init_pos != -1:
    # __init__の最後に追加
    next_def = content.find("\n    def ", init_pos + 100)
    if next_def != -1:
        knowledge_init = """
        
        # ナレッジシステム統合 (v30)
        self.knowledge_manager = _init_knowledge_system()
        if self.knowledge_manager:
            print("✅ ナレッジシステム統合完了")
"""
        content = content[:next_def] + knowledge_init + content[next_def:]

# タスク実行メソッドにナレッジ検索を追加
execute_pattern = "async def execute_task"
execute_pos = content.find(execute_pattern)
if execute_pos != -1:
    # execute_taskの先頭に追加
    method_body_start = content.find(":", execute_pos) + 1
    next_line = content.find("\n", method_body_start) + 1

    knowledge_search = """
        # ナレッジ検索 (v30新機能)
        if self.knowledge_manager and hasattr(self, 'knowledge_manager'):
            try:
                query = f"{task.get('title', '')} {task.get('description', '')}"
                knowledges = self.knowledge_manager.hybrid_search(query, top_k=3)
                if knowledges:
                    print(f"🔍 関連ナレッジ: {len(knowledges)}件発見")
                    task['_knowledge_hints'] = knowledges
            except Exception as e:
                print(f"⚠️ ナレッジ検索エラー: {e}")
"""

    content = content[:next_line] + knowledge_search + content[next_line:]

# ファイルに保存
with open(v30_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"✅ 作成完了: {v30_path.name}")
print(f"📊 サイズ: {v30_path.stat().st_size} bytes")

# 変更点を表示
print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("📝 v30の主な変更:")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("1. ナレッジマネージャー統合")
print("2. タスク実行前の自動ナレッジ検索")
print("3. 検索結果をtask['_knowledge_hints']に格納")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
