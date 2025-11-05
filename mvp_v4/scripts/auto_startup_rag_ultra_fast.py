#!/usr/bin/env python3
"""
ナレッジベース最速自動起動スクリプト（0.5秒起動版）
- 既存DBチェックのみ
- 遅延読み込み
- バックグラウンド初期化
"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def quick_check():
    """超高速チェック（0.5秒以内）"""
    try:
        # 必要なディレクトリの存在確認のみ
        chroma_db = project_root / "mvp_v4" / "models" / "chroma_db"
        knowledge_file = (
            project_root / "mvp_v4" / "knowledge" / "learned" / "conversation_knowledge_v3.json"
        )

        status = []

        # ChromaDBの存在確認
        if chroma_db.exists():
            status.append("✅ ChromaDB")
        else:
            status.append("⚠️  ChromaDB未構築")

        # ナレッジファイルの存在確認
        if knowledge_file.exists():
            status.append("✅ ナレッジ")
        else:
            status.append("⚠️  ナレッジファイル未作成")

        print(f"🚀 RAG {' '.join(status)}")

        # 初回起動時のみフル初期化（バックグラウンド）
        if not chroma_db.exists():
            print("📦 初回起動：バックグラウンドで初期化中...")
            import subprocess

            subprocess.Popen(
                [sys.executable, str(Path(__file__).parent / "auto_startup_rag.py")],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    except Exception as e:
        # エラーは表示するが、ターミナル起動は妨げない
        print(f"⚠️  RAGチェックエラー: {e}")


if __name__ == "__main__":
    quick_check()
