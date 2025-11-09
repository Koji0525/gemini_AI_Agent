# knowledge_system/scripts/init_database.py
import sys
import os
import yaml
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from core_agents.sqlite_manager import SQLiteManager

def load_config():
    """設定ファイルからデータベースパスを読み込みます。"""
    config_path = project_root / "configuration" / "knowledge_config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"設定ファイルが見つかりません: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    if config is None:
        raise ValueError(f"設定ファイル '{config_path}' の読み込みに失敗したか、ファイルが空です。")

    database_config = config.get("database")
    if not database_config:
        raise ValueError("設定ファイルに 'database' セクションが見つかりません。")

    db_path = database_config.get("path")
    if not db_path:
        raise ValueError("設定ファイルにデータベースの 'path' が指定されていません。")

    return project_root / db_path

def initialize_database():
    """
    データベースを初期化します。
    SQLiteManagerをインスタンス化するだけで、テーブルが自動的に作成されます。
    """
    try:
        db_path = load_config()
        print(f"データベースを初期化しています: {db_path}")

        # SQLiteManagerはコンストラクタで接続とテーブル作成を行います
        db_manager = SQLiteManager(db_path)
        db_manager.close()

        print("データベースの初期化が正常に完了しました。")
        print(f"'knowledge'テーブルが'{db_path}'に準備されました。")

    except (FileNotFoundError, ValueError) as e:
        print(f"エラー: {e}", file=sys.stderr)
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}", file=sys.stderr)

if __name__ == "__main__":
    initialize_database()
