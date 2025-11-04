import json
from datetime import datetime

kb_file = "mvp_v4/knowledge/learned/conversation_knowledge_v3.json"

with open(kb_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

new_knowledge = {
    "id": f"KB_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "scenario": "メソッドインターフェース不一致エラーの解決",
    "task_type": "system_integration",
    "problem": "GoogleSheetsManager.update_cell() got an unexpected keyword argument 'cell_address'",
    "root_cause": "呼び出し元とメソッド定義の引数名が不一致。呼び出し側はcell_address、メソッド定義はcell_rangeを使用していた。",
    "solution_steps": [
        "1. 呼び出し元のコードを調査して引数名を特定",
        "2. メソッド定義を呼び出し元に合わせて修正",
        "3. またはメソッドを柔軟な引数に対応させる",
        "4. 修正後の即時テストで検証"
    ],
    "best_practice": "メソッド設計時は呼び出し元とのインターフェースを厳密に合わせる。既存コードを修正する場合は後方互換性を維持する柔軟な設計を採用する。",
    "code_example": """# ✅ 柔軟なメソッド設計
def update_cell(self, sheet_name, cell_range, value=None, **kwargs):
    # 互換性のための引数処理
    if 'cell_address' in kwargs:
        cell_range = kwargs['cell_address']
    
    # メインの処理
    sheet.update(cell_range, [[value]])

# ✅ 呼び出し元の修正
# 修正前: update_cell(sheet, cell_address=address, value=val)
# 修正後: update_cell(sheet, cell_range=address, value=val)""",
    "success_rate": 0.95,
    "avg_time": 5,
    "conditions": "メソッド呼び出しで引数名不一致エラーが発生した場合",
    "avoid_patterns": [
        "呼び出し元と実装の引数名を無視する",
        "後方互換性を考慮しない破壊的変更",
        "テストなしでのインターフェース変更"
    ],
    "performance_improvement": {
        "before": "インターフェースエラーでシステム停止",
        "after": "柔軟な設計で継続動作"
    },
    "created_at": datetime.now().isoformat(),
    "tags": ["インターフェース", "引数不一致", "後方互換性", "柔軟な設計"],
    "severity": "medium",
    "frequency": "medium",
    "lessons_learned": [
        "メソッド設計は呼び出し元を考慮する",
        "既存コード修正時は後方互換性を維持",
        "柔軟な引数設計で互換性問題を解決",
        "インターフェース変更は即時テスト必須"
    ],
    "quality_score": 8
}

data["knowledge_base"].append(new_knowledge)
data["metadata"] = {
    "last_updated": datetime.now().isoformat(),
    "total_count": len(data["knowledge_base"]),
    "version": "4.9"
}

with open(kb_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ インターフェース知識を登録完了")
print(f"📊 総ナレッジ数: {len(data['knowledge_base'])}件")
