#!/usr/bin/env python3
import csv
import json
import os
import sys

# 絶対パス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
utils_dir = os.path.join(parent_dir, "utils")

sys.path.insert(0, parent_dir)
sys.path.insert(0, utils_dir)

try:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "models_fixed", os.path.join(utils_dir, "models_fixed.py")
    )
    models_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(models_module)
    EmbeddingModel = models_module.EmbeddingModel

    spec = importlib.util.spec_from_file_location(
        "database_fixed", os.path.join(utils_dir, "database_fixed.py")
    )
    database_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(database_module)
    DatabaseManager = database_module.DatabaseManager

except Exception as e:
    print(f"❌ インポート失敗: {e}")
    sys.exit(1)


def register_from_csv(csv_file_path):
    """CSVファイルからバッチ登録"""
    print(f"📁 CSVファイルから登録: {csv_file_path}")

    try:
        db_path = os.path.join(parent_dir, "database", "knowledge.db")
        db = DatabaseManager(db_path)
        model = EmbeddingModel()

        with open(csv_file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            successful = 0
            total = 0

            for row in reader:
                total += 1
                try:
                    # 埋め込み生成
                    combined_text = (
                        f"{row.get('title', '')} {row.get('content', '')} {row.get('tags', '')}"
                    )
                    embedding = model.get_embedding(combined_text)

                    if embedding is not None:
                        entry_data = {
                            "title": row.get("title", ""),
                            "content": row.get("content", ""),
                            "category": row.get("category", "general"),
                            "tags": row.get("tags", ""),
                            "scenario": row.get("scenario", "general"),
                            "embedding": (
                                embedding.tobytes() if hasattr(embedding, "tobytes") else embedding
                            ),
                        }

                        success = db.insert_knowledge_entry(entry_data)
                        if success:
                            successful += 1
                            print(f"  ✅ 登録成功: {row.get('title', '')[:50]}...")
                        else:
                            print(f"  ⚠️  登録失敗: {row.get('title', '')[:50]}...")
                    else:
                        print(f"  ⚠️  埋め込み生成失敗: {row.get('title', '')[:50]}...")

                except Exception as e:
                    print(f"  ❌ エラー: {row.get('title', '')[:50]}... - {e}")
                    continue

            print(f"📊 バッチ登録完了: {successful}/{total} 件成功")
            return successful

    except Exception as e:
        print(f"❌ バッチ登録失敗: {e}")
        return 0


def register_from_json(json_file_path):
    """JSONファイルからバッチ登録"""
    print(f"📁 JSONファイルから登録: {json_file_path}")

    try:
        db_path = os.path.join(parent_dir, "database", "knowledge.db")
        db = DatabaseManager(db_path)
        model = EmbeddingModel()

        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            successful = 0
            total = len(data)

            for item in data:
                try:
                    # 埋め込み生成
                    combined_text = (
                        f"{item.get('title', '')} {item.get('content', '')} {item.get('tags', '')}"
                    )
                    embedding = model.get_embedding(combined_text)

                    if embedding is not None:
                        entry_data = {
                            "title": item.get("title", ""),
                            "content": item.get("content", ""),
                            "category": item.get("category", "general"),
                            "tags": item.get("tags", ""),
                            "scenario": item.get("scenario", "general"),
                            "embedding": (
                                embedding.tobytes() if hasattr(embedding, "tobytes") else embedding
                            ),
                        }

                        success = db.insert_knowledge_entry(entry_data)
                        if success:
                            successful += 1
                            print(f"  ✅ 登録成功: {item.get('title', '')[:50]}...")
                        else:
                            print(f"  ⚠️  登録失敗: {item.get('title', '')[:50]}...")
                    else:
                        print(f"  ⚠️  埋め込み生成失敗: {item.get('title', '')[:50]}...")

                except Exception as e:
                    print(f"  ❌ エラー: {item.get('title', '')[:50]}... - {e}")
                    continue

            print(f"📊 バッチ登録完了: {successful}/{total} 件成功")
            return successful

    except Exception as e:
        print(f"❌ バッチ登録失敗: {e}")
        return 0


def main():
    if len(sys.argv) < 3:
        print("使用方法:")
        print("  CSVファイルから登録: python batch_register.py csv <ファイルパス>")
        print("  JSONファイルから登録: python batch_register.py json <ファイルパス>")
        print("")
        print("CSV形式例:")
        print("  title,content,category,tags,scenario")
        print('  "タイトル","内容","technology","タグ1,タグ2","general"')
        print("")
        print("JSON形式例:")
        print(
            '  [{"title": "タイトル", "content": "内容", "category": "technology", "tags": "タグ1,タグ2", "scenario": "general"}]'
        )
        sys.exit(1)

    file_type = sys.argv[1]
    file_path = sys.argv[2]

    if not os.path.exists(file_path):
        print(f"❌ ファイルが見つかりません: {file_path}")
        sys.exit(1)

    if file_type == "csv":
        register_from_csv(file_path)
    elif file_type == "json":
        register_from_json(file_path)
    else:
        print(f"❌ 未知のファイルタイプ: {file_type}")
        sys.exit(1)


if __name__ == "__main__":
    main()
