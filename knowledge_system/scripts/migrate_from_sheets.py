"""
Google Sheetsからデータを移行
"""

import sys
from pathlib import Path

import yaml

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
from tools.sheets_manager import get_sheets_manager


def migrate_knowledge():
    """Google Sheetsからナレッジを移行"""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📦 Google Sheets → SQLite/FAISS 移行開始")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # 設定読み込み
    config_path = project_root / "knowledge_system" / "configuration" / "knowledge_config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # ナレッジマネージャー初期化
    db_path = project_root / config["database"]["path"]
    index_path = project_root / config["vector_search"]["index_path"]
    model_name = config["vector_search"]["model_name"]

    knowledge_manager = KnowledgeManager(str(db_path), str(index_path), model_name)

    # Google Sheets接続
    sheets = get_sheets_manager()
    config["migration"]["source_spreadsheet_id"]
    sheet_name = config["migration"]["source_sheet"]

    print(f"\n📥 シート読み込み: {sheet_name}")

    try:
        # データ取得
        data = sheets.read_sheet(sheet_name)
        print(f"✅ {len(data)}件のデータを取得")

        # データ移行
        success_count = 0
        error_count = 0

        for i, row in enumerate(data, 1):
            try:
                # ナレッジデータの構築
                knowledge = {
                    "scenario": row.get("Scenario", ""),
                    "cause": row.get("Cause", ""),
                    "solution": row.get("Solution", ""),
                    "success_rate": float(row.get("SuccessRate", 0)),
                    "confidence": float(row.get("Confidence", 0)),
                    "category": row.get("Category", ""),
                    "task_type": row.get("TaskType", ""),
                    "quality_score": int(row.get("QualityScore", 0)),
                    "source_system": "google_sheets",
                }

                # 登録
                knowledge_manager.register_knowledge(knowledge)
                success_count += 1

                if i % 10 == 0:
                    print(f"  進捗: {i}/{len(data)} ({success_count}件成功)")

            except Exception as e:
                error_count += 1
                print(f"  ⚠️ エラー (行{i}): {e}")

        # ベクトルインデックス保存
        print("\n�� ベクトルインデックスを保存中...")
        knowledge_manager.save_vector_index()

        # 統計情報表示
        stats = knowledge_manager.get_stats()

        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📊 移行完了サマリー")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"✅ 成功: {success_count}件")
        print(f"❌ エラー: {error_count}件")
        print(f"📚 総ナレッジ数: {stats['total_knowledge']}")
        print(f"🎯 平均信頼度: {stats['avg_confidence']}")
        print(f"�� 平均成功率: {stats['avg_success_rate']}")
        print(f"🔍 ベクトルインデックス: {stats['vector_index_size']}件")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    except Exception as e:
        print(f"❌ 移行エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    migrate_knowledge()
