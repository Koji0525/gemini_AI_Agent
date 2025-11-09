#!/usr/bin/env python3
"""
高速ナレッジ登録スクリプト - 修正版
"""
import os
import sys
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 絶対インポートを使用
try:
    from knowledge_system.core_agents.knowledge_manager_v2 import \
        KnowledgeManagerV2
    from knowledge_system.core_agents.model_cache import ModelCache
except ImportError as e:
    print(f"インポートエラー: {e}")
    sys.exit(1)


def fast_register_knowledge(title, content, category="general", tags=""):
    """高速なナレッジ登録"""
    print(f"🚀 高速登録開始: {title}")

    # モデルキャッシュから取得（高速）
    model = ModelCache.get_model()

    # 知識マネージャー初期化
    km = KnowledgeManagerV2()

    # 埋め込み生成
    start_time = datetime.now()
    embedding = model.encode(content)
    embed_time = (datetime.now() - start_time).total_seconds()

    print(f"✅ 埋め込み生成: {embed_time:.2f}秒")

    # データベース登録
    knowledge_id = km.add_knowledge(
        title=title, content=content, category=category, tags=tags, embedding=embedding
    )

    total_time = (datetime.now() - start_time).total_seconds()
    print(f"✅ 登録完了: {knowledge_id} (総時間: {total_time:.2f}秒)")
    return knowledge_id


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('使用方法: python fast_register.py "タイトル" "内容" [カテゴリ] [タグ]')
        sys.exit(1)

    title = sys.argv[1]
    content = sys.argv[2]
    category = sys.argv[3] if len(sys.argv) > 3 else "general"
    tags = sys.argv[4] if len(sys.argv) > 4 else ""

    fast_register_knowledge(title, content, category, tags)
