"""SQLiteナレッジシステム自動起動"""

import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

start = time.time()

try:
    # 起動確認ファイルチェック（重複起動防止）
    startup_flag = project_root / ".sqlite_knowledge_loaded"

    if startup_flag.exists():
        # 既に起動済み
        print("ℹ️ SQLiteナレッジシステムは起動済みです")
        sys.exit(0)

    print("🔧 SQLiteナレッジシステム初期化中...")

    import yaml

    # 設定読み込み
    config_path = project_root / "knowledge_system/configuration/knowledge_config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    db_path = project_root / config["database"]["path"]
    index_path = project_root / config["vector_search"]["index_path"]

    # 初期化（軽量チェックのみ）
    if not db_path.exists():
        print("⚠️ データベース未作成 - スキップ")
        sys.exit(0)

    # 起動フラグ作成
    startup_flag.touch()

    elapsed = time.time() - start
    print(f"✅ SQLiteナレッジシステム起動完了 ({elapsed:.2f}秒)")
    print(f"   データベース: {db_path.stat().st_size / 1024:.1f} KB")

except Exception as e:
    print(f"⚠️ 初期化エラー（無視して続行）: {e}")
    sys.exit(0)
