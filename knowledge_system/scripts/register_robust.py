#!/usr/bin/env python3
import os
import sys
from datetime import datetime

# パス設定を確実化
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, "utils"))

try:
    from utils.database import DatabaseManager
    from utils.models import EmbeddingModel

    print("✅ インポート成功")
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    print(f"🔧 Pythonパス: {sys.path}")
    sys.exit(1)


def register_knowledge(title, content, category="general", tags=""):
    """確実に動作するナレッジ登録関数"""
    try:
        # データベースマネージャー初期化
        db_path = os.path.join(parent_dir, "database", "knowledge.db")
        db_manager = DatabaseManager(db_path)

        # 埋め込みモデル初期化
        print("📥 モデルをロード中...")
        model = EmbeddingModel()
        print("✅ モデルロード成功")

        # 埋め込み生成
        print("🔄 埋め込み生成中...")
        combined_text = f"{title} {content} {tags}"
        embedding = model.get_embedding(combined_text)
        if embedding is None:
            print("❌ 埋め込み生成失敗")
            return False

        print(f"✅ 埋め込み生成完了: {len(embedding)}次元")

        # データベース登録
        entry_data = {
            "title": title,
            "content": content,
            "category": category,
            "tags": tags,
            "scenario": "general",  # 必須カラムを明示的に設定
            "embedding": embedding.tobytes() if hasattr(embedding, "tobytes") else embedding,
            "created_at": datetime.now().isoformat(),
        }

        success = db_manager.insert_knowledge_entry(entry_data)
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
        print('使用方法: python register_robust.py "タイトル" "内容" [カテゴリ] [タグ]')
        print('例: python register_robust.py "テスト" "テスト内容" "technology" "テスト,確認"')
        sys.exit(1)

    title = sys.argv[1]
    content = sys.argv[2]
    category = sys.argv[3] if len(sys.argv) > 3 else "general"
    tags = sys.argv[4] if len(sys.argv) > 4 else ""

    print(f"�� ナレッジ登録開始: {title}")
    success = register_knowledge(title, content, category, tags)

    if success:
        print("🎉 登録完了")
    else:
        print("💥 登録失敗")
        sys.exit(1)


if __name__ == "__main__":
    main()
