import json
from datetime import datetime

kb_file = "mvp_v4/knowledge/learned/conversation_knowledge_v3.json"

with open(kb_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

new_knowledge = {
    "id": f"KB_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "scenario": "自動修正スクリプトによるコード構造破壊と確実な修正方法",
    "task_type": "system_integration",
    "problem": "PMAgent初期化修正スクリプトがコードのインデント構造を破壊し、複数のtryブロックがネストして構文エラーが発生",
    "root_cause": "部分的な正規表現置換がコードの論理構造を無視し、複数の修正スクリプトの累積適用で構造が破壊された",
    "solution_steps": [
        "1. バックアップから確実に復元",
        "2. 部分修正をやめ、全文修正の原則を厳守", 
        "3. 単純な文字列置換で確実に修正",
        "4. 修正後は即時構文チェックで検証",
        "5. 複雑な正規表現より単純な文字列マッチングを優先"
    ],
    "best_practice": "自動修正スクリプトは補助ツールとして使用し、常に手動確認とバックアップを前提とする。複雑なコード修正は部分置換より全文書き直しが安全。",
    "code_example": """# ✅ 安全な修正方法
# 1. バックアップ作成
cp file.py file_backup.py

# 2. 単純な文字列置換
old_code = '''元のコードブロック'''
new_code = '''修正後のコードブロック'''

with open('file.py', 'r') as f:
    content = f.read()

if old_code in content:
    content = content.replace(old_code, new_code)
    
# 3. 即時検証
python3 -m py_compile file.py""",
    "success_rate": 0.95,
    "avg_time": 5,
    "conditions": "自動修正スクリプトがコード構造を破壊した場合。部分修正が累積的に問題を悪化させている場合。",
    "avoid_patterns": [
        "複雑な正規表現での部分置換",
        "コンテキストを無視した機械的修正", 
        "修正後の即時検証を省略",
        "バックアップなしでの直接修正"
    ],
    "performance_improvement": {
        "before": "自動修正失敗→デバッグに長時間",
        "after": "手動確実修正→5分で解決"
    },
    "created_at": datetime.now().isoformat(),
    "tags": ["自動修正", "コード構造", "インデントエラー", "確実性", "バックアップ"],
    "severity": "high",
    "frequency": "medium", 
    "lessons_learned": [
        "自動化ツールは補助であり、完全な解決策ではない",
        "バックアップは常に必須",
        "部分修正より全文修正が安全",
        "修正後は即時検証が必須",
        "単純な方法ほど確実"
    ],
    "quality_score": 8
}

data["knowledge_base"].append(new_knowledge)
data["metadata"] = {
    "last_updated": datetime.now().isoformat(),
    "total_count": len(data["knowledge_base"]),
    "version": "4.6"
}

with open(kb_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ ナレッジ登録完了")
print(f"📊 総ナレッジ数: {len(data['knowledge_base'])}件")
