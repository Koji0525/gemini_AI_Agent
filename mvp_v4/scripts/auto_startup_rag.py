#!/usr/bin/env python3
"""
ナレッジベース自動起動スクリプト（永続化版v2 - 最適化）
初回起動またはフル初期化が必要な時のみ使用
"""
import gzip
import pickle
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def main():
    try:
        # キャッシュディレクトリ
        cache_dir = project_root / "mvp_v4" / ".cache"
        cache_dir.mkdir(exist_ok=True)
        cache_file = cache_dir / "rag_engine.pkl.gz"

        # キャッシュが存在する場合は高速読み込み
        if cache_file.exists():
            print("⚡ キャッシュから高速読み込み中...")
            with gzip.open(cache_file, "rb") as f:
                cached_data = pickle.load(f)
            print(f"✅ 高速起動完了 (キャッシュ: {cached_data.get('timestamp', 'N/A')})")
            return

        # キャッシュがない場合のみフル初期化
        print("🔧 初回起動：フル初期化中...")
        from mvp_v4.scripts.rag_engine_local import FrugalRAGEngine

        rag = FrugalRAGEngine()
        knowledge_file = (
            project_root / "mvp_v4" / "knowledge" / "learned" / "conversation_knowledge_v3.json"
        )

        if knowledge_file.exists():
            rag.load_knowledge([str(knowledge_file)])

            # キャッシュを作成
            from datetime import datetime

            cache_data = {
                "timestamp": datetime.now().isoformat(),
                "knowledge_file": str(knowledge_file),
                "status": "initialized",
            }
            with gzip.open(cache_file, "wb") as f:
                pickle.dump(cache_data, f)

            print("✅ ナレッジベース起動完了（キャッシュ作成済み）")
        else:
            print(f"⚠️  ナレッジファイルが見つかりません: {knowledge_file}")

    except ImportError as e:
        print(f"⚠️  モジュールのインポートエラー: {e}")
    except Exception as e:
        print(f"⚠️  ナレッジベース起動エラー: {e}")


if __name__ == "__main__":
    main()
