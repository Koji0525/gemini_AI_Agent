#!/usr/bin/env python3
"""
高速ナレッジ登録スクリプト - 直接実行版
"""
import os
import sys

# スクリプトのディレクトリを基準にパスを設定
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)  # knowledge_system の親ディレクトリ
sys.path.insert(0, project_root)

print(f"🔧 パス設定: {project_root}")

try:
    # 直接インポート（knowledge_system パッケージ経由）
    from knowledge_system.core_agents.knowledge_manager_v2 import \
        KnowledgeManagerV2
    from knowledge_system.core_agents.model_cache import ModelCache

    print("✅ モジュールインポート成功")
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    print("💡 代替方法で試行...")
    # 代替方法: 相対インポート
    import sys

    sys.path.insert(0, os.path.join(project_root, "knowledge_system"))
    from core_agents.knowledge_manager_v2 import KnowledgeManagerV2
    from core_agents.model_cache import ModelCache

    print("✅ 代替インポート成功")

from datetime import datetime


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
        print('使用方法: python fast_register_direct.py "タイトル" "内容" [カテゴリ] [タグ]')
        print('または: python run_knowledge_system.py fast_register_direct.py "タイトル" "内容"')
        sys.exit(1)

    title = sys.argv[1]
    content = sys.argv[2]
    category = sys.argv[3] if len(sys.argv) > 3 else "general"
    tags = sys.argv[4] if len(sys.argv) > 4 else ""

    fast_register_knowledge(title, content, category, tags)
