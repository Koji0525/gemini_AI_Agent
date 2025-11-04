"""
Google Sheets → ChromaDB 変換スクリプト
既存ナレッジ（actionable_knowledge）をChromaDBに移行

【変更理由】
何が起きた: 既存の1,400件のナレッジがGoogle Sheetsに存在
原因: 新MVPシステムはChromaDB使用
狙い: 既存資産を活用してナレッジを一気に拡大
"""

import sys
import json
import os

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from browser_control.sheets_manager import GoogleSheetsManager
from mvp_v4.scripts.rag_engine_local import FrugalRAGEngine


def migrate_sheets_to_chroma():
    """Google SheetsのナレッジをChromaDBに移行"""

    print("\n" + "=" * 70)
    print("🔄 Google Sheets → ChromaDB 移行")
    print("=" * 70 + "\n")

    # 1. Sheetsからナレッジ読み込み
    print("📂 STEP 1: Google Sheetsからナレッジ読み込み")
    print("-" * 70)

    sheets = GoogleSheetsManager()

    try:
        knowledge_data = sheets.read_range("actionable_knowledge!A2:N100")
        print(f"✅ 読み込み成功: {len(knowledge_data)}行")
    except Exception as e:
        print(f"❌ エラー: {e}")
        return

    # 2. JSON形式に変換
    print("\n📝 STEP 2: JSON形式に変換")
    print("-" * 70)

    knowledge_json = {"knowledge_base": []}

    converted_count = 0

    for i, row in enumerate(knowledge_data, 1):
        if not row or len(row) < 3:
            continue

        try:
            kb_entry = {
                "id": row[0] if len(row) > 0 else f"MIGRATED_{i}",
                "task_type": row[1] if len(row) > 1 else "general",
                "scenario": row[2] if len(row) > 2 else "未設定",
                "best_practice": row[3] if len(row) > 3 else "",
                "code_example": row[4] if len(row) > 4 else "",
                "success_rate": float(row[6]) if len(row) > 6 and row[6] else 0.8,
                "avg_execution_time": float(row[7]) if len(row) > 7 and row[7] else 5.0,
                "conditions": [row[8]] if len(row) > 8 and row[8] else [],
                "avoid_patterns": [row[9]] if len(row) > 9 and row[9] else [],
                "error_fixes": {},
            }

            knowledge_json["knowledge_base"].append(kb_entry)
            converted_count += 1

        except Exception as e:
            print(f"⚠️ 行{i}の変換失敗: {e}")
            continue

    print(f"✅ 変換完了: {converted_count}件")

    # 3. JSONファイルとして保存
    print("\n💾 STEP 3: JSONファイル保存")
    print("-" * 70)

    output_file = "mvp_v4/knowledge/initial/sheets_migrated.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(knowledge_json, f, indent=2, ensure_ascii=False)

    print(f"✅ 保存完了: {output_file}")

    # 4. ChromaDBに投入
    print("\n🔨 STEP 4: ChromaDBにインデックス構築")
    print("-" * 70)

    rag = FrugalRAGEngine()
    rag.load_knowledge([output_file])

    print("\n" + "=" * 70)
    print(f"✅ 移行完了: {converted_count}件のナレッジをChromaDBに投入")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    migrate_sheets_to_chroma()
