#!/usr/bin/env python3
"""
ナレッジ登録スクリプト - 絶対確実版
"""
import os
import sys

# 絶対確実なパス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
utils_dir = os.path.join(current_dir, "..", "utils")
sys.path.insert(0, utils_dir)

print(f"🔧 カレントディレクトリ: {current_dir}")
print(f"🔧 ユーティリティディレクトリ: {utils_dir}")
print(f"�� Pythonパス: {sys.path}")

try:
    # 直接インポート
    from database import add_knowledge
    from models import get_embedding

    print("✅ インポート成功")
except ImportError as e:
    print(f"❌ インポート失敗: {e}")
    sys.exit(1)


def main():
    if len(sys.argv) < 3:
        print('使用方法: python register_simple.py "タイトル" "内容" [カテゴリ] [タグ]')
        print('例: python register_simple.py "テスト" "これはテストです" "test" "テストタグ"')
        return 1

    title = sys.argv[1]
    content = sys.argv[2]
    category = sys.argv[3] if len(sys.argv) > 3 else "general"
    tags = sys.argv[4] if len(sys.argv) > 4 else ""

    print(f"🚀 ナレッジ登録開始: {title}")

    try:
        # 埋め込み生成
        embedding = get_embedding(content)
        print(f"✅ 埋め込み生成完了: {len(embedding)}次元")

        # データベース登録
        knowledge_id = add_knowledge(title, content, category, tags)

        if knowledge_id:
            print(f"🎉 登録完了: ID {knowledge_id}")
            return 0
        else:
            print("❌ 登録失敗")
            return 1

    except Exception as e:
        print(f"❌ エラー: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
