#!/usr/bin/env python3
import os
import sys

# 絶対パス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
utils_dir = os.path.join(parent_dir, "utils")

print(f"🔧 カレントディレクトリ: {current_dir}")
print(f"🔧 ユーティリティディレクトリ: {utils_dir}")

# 確実なインポート方法
try:
    # 方法1: 直接インポート
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

    print("✅ 直接インポート成功")

except Exception as e:
    print(f"❌ 直接インポート失敗: {e}")
    sys.exit(1)


def register_knowledge_definitive(title, content, category="general", tags=""):
    """確実なナレッジ登録"""
    try:
        db_path = os.path.join(parent_dir, "database", "knowledge.db")
        print(f"🔧 データベースパス: {db_path}")

        db = DatabaseManager(db_path)
        model = EmbeddingModel()

        print("📥 モデルをロード中...")
        embedding = model.get_embedding(f"{title} {content}")

        if embedding is None:
            print("❌ 埋め込み生成失敗")
            return False

        print(f"✅ 埋め込み生成成功: {len(embedding)}次元")

        entry_data = {
            "title": title,
            "content": content,
            "category": category,
            "tags": tags,
            "scenario": "general",
            "embedding": embedding.tobytes() if hasattr(embedding, "tobytes") else embedding,
        }

        success = db.insert_knowledge_entry(entry_data)

        if success:
            print("✅ ナレッジ登録成功")
            return True
        else:
            print("❌ ナレッジ登録失敗")
            return False

    except Exception as e:
        print(f"❌ 登録中にエラー: {e}")
        return False


def main():
    if len(sys.argv) < 3:
        print('使用方法: python register_definitive.py "タイトル" "内容" [カテゴリ] [タグ]')
        print('例: python register_definitive.py "テスト" "テスト内容" "technology" "テスト,確認"')
        sys.exit(1)

    title = sys.argv[1]
    content = sys.argv[2]
    category = sys.argv[3] if len(sys.argv) > 3 else "general"
    tags = sys.argv[4] if len(sys.argv) > 4 else ""

    print(f"🚀 ナレッジ登録開始: {title}")
    success = register_knowledge_definitive(title, content, category, tags)

    if success:
        print("🎉 登録完了")
    else:
        print("💥 登録失敗")
        sys.exit(1)


if __name__ == "__main__":
    main()
