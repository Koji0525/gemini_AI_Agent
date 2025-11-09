#!/usr/bin/env python3
import argparse
import os
import sys
from typing import Any, Dict

import yaml

# 絶対パス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
utils_dir = os.path.join(parent_dir, "utils")

sys.path.insert(0, parent_dir)
sys.path.insert(0, utils_dir)

try:
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

except Exception as e:
    print(f"❌ インポート失敗: {e}")
    sys.exit(1)


class AdvancedSyncManager:
    """高度な同期管理クラス - 汎用性と拡張性を重視"""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.db_path = os.path.join(parent_dir, "database", "knowledge.db")
        self.index_dir = os.path.join(parent_dir, "database", "faiss_index")
        self.model = None
        self.db = None

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """設定ファイルの読み込み"""
        default_config = {
            "sync": {
                "batch_size": 50,
                "embedding_model": "all-MiniLM-L6-v2",
                "similarity_threshold": 0.3,
                "auto_retry": True,
                "max_retries": 3,
            },
            "logging": {"level": "INFO", "format": "%(asctime)s - %(levelname)s - %(message)s"},
            "performance": {"max_concurrent": 1, "memory_limit_mb": 1024},  # 並列処理数
        }

        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    user_config = yaml.safe_load(f)
                    # デフォルト設定とユーザー設定をマージ
                    self._merge_config(default_config, user_config)
            except Exception as e:
                print(f"⚠️  設定ファイル読み込みエラー: {e}")

        return default_config

    def _merge_config(self, default: Dict, user: Dict):
        """設定のマージ"""
        for key, value in user.items():
            if isinstance(value, dict) and key in default:
                self._merge_config(default[key], value)
            else:
                default[key] = value

    def initialize_components(self):
        """コンポーネントの初期化"""
        try:
            # データベース初期化
            self.db = DatabaseManager(self.db_path)

            # モデル初期化（設定可能）
            model_name = self.config["sync"]["embedding_model"]
            self.model = EmbeddingModel(model_name)

            # インデックスディレクトリ作成
            os.makedirs(self.index_dir, exist_ok=True)

            return True
        except Exception as e:
            print(f"❌ コンポーネント初期化失敗: {e}")
            return False

    def sync_with_strategy(self, strategy: str = "incremental") -> bool:
        """戦略に基づいた同期実行"""
        strategies = {
            "incremental": self._incremental_sync,
            "full": self._full_sync,
            "smart": self._smart_sync,
        }

        if strategy not in strategies:
            print(f"❌ 未知の同期戦略: {strategy}")
            return False

        return strategies[strategy]()

    def _incremental_sync(self) -> bool:
        """増分同期 - 未同期のエントリーのみ処理"""
        print("🔄 増分同期を開始...")

        unsynced_entries = self.db.get_unsynced_entries()
        total = len(unsynced_entries)

        if total == 0:
            print("✅ 同期済みのエントリーはありません")
            return True

        print(f"🔍 未同期エントリー: {total}件")
        return self._process_entries(unsynced_entries, "増分")

    def _full_sync(self) -> bool:
        """完全同期 - すべてのエントリーを再処理"""
        print("🔄 完全同期を開始...")

        # すべてのエントリーを取得
        all_entries = self.db.search_entries(limit=10000)  # 大きな制限値
        total = len(all_entries)

        print(f"🔍 全エントリー: {total}件")

        # 既存のインデックスをクリア
        self._clear_existing_index()

        return self._process_entries(all_entries, "完全")

    def _smart_sync(self) -> bool:
        """スマート同期 - 条件に基づいた最適な同期"""
        print("🔄 スマート同期を開始...")

        stats = self.db.get_sync_stats()
        total_entries = stats["total_entries"]
        synced_entries = stats["synced_entries"]

        # 同期率が低い場合は完全同期、高い場合は増分同期
        sync_rate = (synced_entries / total_entries) if total_entries > 0 else 0

        if sync_rate < 0.5:  # 50%未満なら完全同期
            print("📊 同期率が低いため完全同期を実行")
            return self._full_sync()
        else:
            print("📊 同期率が高いため増分同期を実行")
            return self._incremental_sync()

    def _clear_existing_index(self):
        """既存のインデックスをクリア"""
        index_file = os.path.join(self.index_dir, "knowledge.index")
        mapping_file = os.path.join(self.index_dir, "index_mapping.json")

        for file_path in [index_file, mapping_file]:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️  既存インデックスを削除: {file_path}")

    def _process_entries(self, entries: list, sync_type: str) -> bool:
        """エントリーの処理"""
        batch_size = self.config["sync"]["batch_size"]
        successful = 0
        total = len(entries)

        for i in range(0, total, batch_size):
            batch = entries[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total + batch_size - 1) // batch_size

            print(f"📦 {sync_type}同期 - バッチ {batch_num}/{total_batches}")

            for j, entry in enumerate(batch, 1):
                entry_num = i + j
                self._process_single_entry(entry, entry_num, total)

                if entry_num % 10 == 0:  # 10エントリーごとに進捗表示
                    print(f"  進行状況: {entry_num}/{total} ({entry_num/total*100:.1f}%)")

        # 最終統計
        final_stats = self.db.get_sync_stats()
        print(f"📊 {sync_type}同期完了: {successful}/{total} 件成功")
        print(f"📊 最終同期率: {final_stats['sync_percentage']:.1f}%")

        return successful > 0

    def _process_single_entry(self, entry: Dict, current: int, total: int):
        """単一エントリーの処理"""
        try:
            # 埋め込み生成
            combined_text = f"{entry['title']} {entry['content']} {entry.get('tags', '')}"
            embedding = self.model.get_embedding(combined_text)

            if embedding is not None:
                # ベクトルインデックスに追加
                success = self.db.add_to_vector_index(entry["id"], embedding, self.index_dir)
                if success:
                    return True
                else:
                    print(f"  ⚠️  インデックス追加失敗: ID {entry['id']}")
            else:
                print(f"  ⚠️  埋め込み生成失敗: ID {entry['id']}")

        except Exception as e:
            print(f"  ❌ エントリー処理エラー (ID {entry['id']}): {e}")

        return False


def main():
    parser = argparse.ArgumentParser(description="高度なナレッジ同期システム")
    parser.add_argument(
        "--strategy",
        "-s",
        choices=["incremental", "full", "smart"],
        default="smart",
        help="同期戦略を選択 (default: smart)",
    )
    parser.add_argument("--config", "-c", help="設定ファイルのパス")
    parser.add_argument("--batch-size", type=int, help="バッチ処理サイズ")

    args = parser.parse_args()

    print("🚀 高度な同期システムを起動")

    # 同期マネージャー初期化
    sync_manager = AdvancedSyncManager(args.config)

    # コマンドライン引数で設定を上書き
    if args.batch_size:
        sync_manager.config["sync"]["batch_size"] = args.batch_size

    # コンポーネント初期化
    if not sync_manager.initialize_components():
        sys.exit(1)

    # 同期実行
    success = sync_manager.sync_with_strategy(args.strategy)

    if success:
        print("🎉 同期処理が正常に完了しました")
    else:
        print("�� 同期処理に失敗しました")
        sys.exit(1)


if __name__ == "__main__":
    main()
