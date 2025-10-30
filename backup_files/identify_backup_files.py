#!/usr/bin/env python3
"""
バックアップファイルとテストファイルを安全に特定するツール
"""
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime


class BackupIdentifier:
    """バックアップファイルを識別"""

    def __init__(self):
        self.root = Path(".")
        self.backup_patterns = [
            "backup",
            "_backup",
            "backups/",
            "_old",
            "_new",
            "_copy",
            "_v1",
            "_v2",
            "_test",
            "error_logs/",
            "logs/",
            "__pycache__/",
            ".pytest_cache/",
            "venv/",
            ".git/",
        ]

        self.categories = defaultdict(list)

    def categorize_files(self):
        """ファイルをカテゴリ分け"""
        print("🔍 ファイルをカテゴリ分けしています...\n")

        for item in self.root.rglob("*"):
            if item.is_file():
                self._categorize_single_file(item)

        self._print_summary()

    def _categorize_single_file(self, file_path):
        """1つのファイルをカテゴリ分け"""
        path_str = str(file_path)

        # venvは無視（巨大なので）
        if "venv/" in path_str:
            self.categories["venv"].append(file_path)
            return

        # .gitも無視
        if ".git/" in path_str:
            self.categories["git"].append(file_path)
            return

        # バックアップディレクトリ
        if "backups/" in path_str:
            self.categories["backups_dir"].append(file_path)
            return

        # エラーログ
        if "error_logs/" in path_str or "logs/" in path_str:
            self.categories["logs"].append(file_path)
            return

        # テストファイル
        if file_path.name.startswith("test_"):
            self.categories["test_files"].append(file_path)
            return

        # バックアップっぽい名前
        if any(pattern in file_path.name for pattern in ["_backup", "_old", "_copy", "_v1", "_v2"]):
            self.categories["backup_files"].append(file_path)
            return

        # cache系
        if "__pycache__" in path_str or ".pytest_cache" in path_str:
            self.categories["cache"].append(file_path)
            return

        # JSONファイル（ログや設定）
        if file_path.suffix == ".json" and file_path.name not in ["package.json", "service_account.json"]:
            self.categories["json_files"].append(file_path)
            return

        # アクティブファイル
        self.categories["active"].append(file_path)

    def _print_summary(self):
        """サマリー表示"""
        print("=" * 80)
        print("📊 ファイルカテゴリ別サマリー")
        print("=" * 80)

        # サイズを計算
        for category, files in sorted(self.categories.items()):
            total_size = sum(f.stat().st_size for f in files if f.exists())
            size_mb = total_size / (1024 * 1024)

            print(f"\n📁 {category}")
            print(f"   ファイル数: {len(files)}")
            print(f"   合計サイズ: {size_mb:.2f} MB")

            if category not in ["venv", "git", "cache", "active"]:
                print(f"   例:")
                for f in list(files)[:3]:
                    print(f"     - {f}")

    def generate_cleanup_plan(self):
        """クリーンアッププラン作成"""
        print("\n" + "=" * 80)
        print("🧹 クリーンアッププラン")
        print("=" * 80)

        cleanup_categories = {
            "backups_dir": "安全に削除可能",
            "logs": "古いログは削除可能",
            "cache": "削除推奨",
            "backup_files": "確認後削除可能",
            "json_files": "確認が必要",
        }

        for category, description in cleanup_categories.items():
            files = self.categories.get(category, [])
            if files:
                print(f"\n📦 {category} ({description})")
                print(f"   ファイル数: {len(files)}")
                total_size = sum(f.stat().st_size for f in files if f.exists())
                print(f"   削減可能サイズ: {total_size / (1024 * 1024):.2f} MB")

        return cleanup_categories

    def create_detailed_report(self):
        """詳細レポート作成"""
        import json

        report = {"timestamp": datetime.now().isoformat(), "categories": {}}

        for category, files in self.categories.items():
            if category not in ["venv", "git", "active"]:
                report["categories"][category] = {
                    "count": len(files),
                    "files": [str(f) for f in files],
                    "total_size_mb": sum(f.stat().st_size for f in files if f.exists()) / (1024 * 1024),
                }

        with open("backup_analysis.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print("\n💾 詳細レポートを backup_analysis.json に保存しました")


if __name__ == "__main__":
    identifier = BackupIdentifier()
    identifier.categorize_files()
    identifier.generate_cleanup_plan()
    identifier.create_detailed_report()
