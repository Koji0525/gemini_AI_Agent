#!/usr/bin/env python3
"""
ナレッジ登録スクリプト - 確実に動作する版
"""
import os
import sys

# ユーティリティをインポート
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.database import add_knowledge
from utils.models import get_embedding


def main():
    if len(sys.argv) < 3:
        print('使用方法: python register.py "タイトル" "内容" [カテゴリ] [タグ]')
        print(
            '例: python register.py "エラー対処" "エラー時はログを確認" "troubleshooting" "エラー,デバッグ"'
        )
        return

    title = sys.argv[1]
    content = sys.argv[2]
    category = sys.argv[3] if len(sys.argv) > 3 else "general"
    tags = sys.argv[4] if len(sys.argv) > 4 else ""

    print(f"🚀 ナレッジ登録開始: {title}")

    try:
        # 埋め込み生成（必要に応じて）
        embedding = get_embedding(content)
        print(f"✅ 埋め込み生成完了: {len(embedding)}次元")

        # データベース登録
        knowledge_id = add_knowledge(title, content, category, tags)
        print(f"✅ 登録完了: ID {knowledge_id}")

    except Exception as e:
        print(f"❌ 登録失敗: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
