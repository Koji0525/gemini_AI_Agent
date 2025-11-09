#!/usr/bin/env python3
"""テストキャッシュ管理システム"""

import hashlib
import json
import time
from pathlib import Path
from typing import Dict, List


class TestCacheManager:
    """テストキャッシュを管理するクラス"""

    def __init__(self, cache_dir: str = ".test_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        self.hash_file = self.cache_dir / "file_hashes.json"
        self.results_file = self.cache_dir / "test_results.json"
        self.last_run_file = self.cache_dir / "last_run.json"

        self.file_hashes = self._load_hashes()
        self.test_results = self._load_results()
        self.last_run = self._load_last_run()

    def _load_hashes(self) -> Dict[str, str]:
        """保存されたハッシュ値を読み込み"""
        if self.hash_file.exists():
            with open(self.hash_file, "r") as f:
                return json.load(f)
        return {}

    def _load_results(self) -> Dict[str, dict]:
        """保存されたテスト結果を読み込み"""
        if self.results_file.exists():
            with open(self.results_file, "r") as f:
                return json.load(f)
        return {}

    def _load_last_run(self) -> Dict[str, float]:
        """最終実行時刻を読み込み"""
        if self.last_run_file.exists():
            with open(self.last_run_file, "r") as f:
                return json.load(f)
        return {}

    def _save_hashes(self):
        """ハッシュ値を保存"""
        with open(self.hash_file, "w") as f:
            json.dump(self.file_hashes, f, indent=2)

    def _save_results(self):
        """テスト結果を保存"""
        with open(self.results_file, "w") as f:
            json.dump(self.test_results, f, indent=2)

    def _save_last_run(self):
        """最終実行時刻を保存"""
        with open(self.last_run_file, "w") as f:
            json.dump(self.last_run, f, indent=2)

    def calculate_file_hash(self, file_path: str) -> str:
        """ファイルのハッシュ値を計算"""
        path = Path(file_path)
        if not path.exists():
            return ""

        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            hasher.update(f.read())
        return hasher.hexdigest()

    def has_file_changed(self, file_path: str) -> bool:
        """ファイルが変更されたかチェック"""
        current_hash = self.calculate_file_hash(file_path)
        stored_hash = self.file_hashes.get(file_path, "")
        return current_hash != stored_hash

    def get_changed_files(self, file_paths: List[str]) -> List[str]:
        """変更されたファイルのリストを取得"""
        changed = []
        for file_path in file_paths:
            if self.has_file_changed(file_path):
                changed.append(file_path)
        return changed

    def update_file_hash(self, file_path: str):
        """ファイルのハッシュ値を更新"""
        self.file_hashes[file_path] = self.calculate_file_hash(file_path)
        self._save_hashes()

    def record_test_result(self, file_path: str, passed: bool, error_msg: str = ""):
        """テスト結果を記録"""
        self.test_results[file_path] = {
            "passed": passed,
            "timestamp": time.time(),
            "error": error_msg,
        }
        self.last_run[file_path] = time.time()
        self._save_results()
        self._save_last_run()

    def was_test_passed(self, file_path: str) -> bool:
        """前回のテストが成功したかチェック"""
        result = self.test_results.get(file_path, {})
        return result.get("passed", False)

    def should_skip_test(self, file_path: str) -> bool:
        """テストをスキップすべきか判定"""
        # ファイルが変更されていない かつ 前回成功している
        return not self.has_file_changed(file_path) and self.was_test_passed(file_path)

    def get_files_to_test(self, all_files: List[str]) -> tuple[List[str], List[str]]:
        """
        テストすべきファイルとスキップするファイルを返す

        Returns:
            (テストするファイル, スキップするファイル)
        """
        to_test = []
        to_skip = []

        for file_path in all_files:
            if self.should_skip_test(file_path):
                to_skip.append(file_path)
            else:
                to_test.append(file_path)

        return to_test, to_skip

    def clear_cache(self):
        """キャッシュをクリア"""
        self.file_hashes = {}
        self.test_results = {}
        self.last_run = {}
        self._save_hashes()
        self._save_results()
        self._save_last_run()
        print("✅ キャッシュをクリアしました")


def main():
    """CLIインターフェース"""
    import sys

    cache = TestCacheManager()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "clear":
            cache.clear_cache()

        elif command == "status":
            print(f"📊 キャッシュ状態:")
            print(f"  追跡中のファイル数: {len(cache.file_hashes)}")
            print(f"  テスト結果数: {len(cache.test_results)}")

            # 成功数
            passed = sum(1 for r in cache.test_results.values() if r.get("passed"))
            print(f"  成功: {passed}/{len(cache.test_results)}")

        elif command == "list":
            print("📝 キャッシュされたファイル:")
            for file_path in sorted(cache.file_hashes.keys()):
                status = "✅" if cache.was_test_passed(file_path) else "❌"
                print(f"  {status} {file_path}")

        else:
            print("使用方法:")
            print("  python tools/test_cache_manager.py status  # 状態確認")
            print("  python tools/test_cache_manager.py list    # ファイル一覧")
            print("  python tools/test_cache_manager.py clear   # キャッシュクリア")

    else:
        print("テストキャッシュマネージャー")
        print("使用方法: python tools/test_cache_manager.py [command]")


if __name__ == "__main__":
    main()
