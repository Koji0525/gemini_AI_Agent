#!/usr/bin/env python3
"""
バックアップとログファイルを安全にクリーンアップ
"""
import shutil
from pathlib import Path
from datetime import datetime
import json


class SafeCleanup:
    """安全なクリーンアップ"""

    def __init__(self):
        self.root = Path(".")
        self.archive = Path("_CLEANED_UP")
        self.dry_run = True  # デフォルトはドライラン

    def cleanup_backups(self, dry_run=True):
        """バックアップディレクトリをクリーンアップ"""
        self.dry_run = dry_run

        print("🧹 バックアップクリーンアップ開始")
        print(f"モード: {'ドライラン（実行なし）' if dry_run else '実行モード'}\n")

        targets = {
            "backups/": "バックアップディレクトリ",
            "error_logs/": "エラーログ",
            "__pycache__/": "Pythonキャッシュ",
            ".pytest_cache/": "Pytestキャッシュ",
        }

        total_size = 0
        total_files = 0

        for pattern, description in targets.items():
            size, count = self._process_directory(pattern, description)
            total_size += size
            total_files += count

        print("\n" + "=" * 80)
        print(f"📊 クリーンアップサマリー")
        print("=" * 80)
        print(f"削除対象ファイル数: {total_files}")
        print(f"削減可能サイズ: {total_size / (1024 * 1024):.2f} MB")

        if dry_run:
            print("\n⚠️ これはドライランです。実際には削除されていません。")
            print("実行するには: python safe_cleanup.py --execute")
        else:
            print(f"\n✅ クリーンアップ完了")
            print(f"アーカイブ場所: {self.archive}")

    def _process_directory(self, pattern, description):
        """ディレクトリを処理"""
        print(f"\n📁 {description} ({pattern})")

        paths = list(self.root.glob(pattern))
        if not paths:
            print("   該当なし")
            return 0, 0

        total_size = 0
        file_count = 0

        for path in paths:
            if path.is_dir():
                # ディレクトリ内のファイルサイズを計算
                for file in path.rglob("*"):
                    if file.is_file():
                        total_size += file.stat().st_size
                        file_count += 1

                print(f"   {path}: {file_count} ファイル, {total_size / (1024 * 1024):.2f} MB")

                if not self.dry_run:
                    # アーカイブに移動
                    dest = self.archive / path.name / datetime.now().strftime("%Y%m%d_%H%M%S")
                    dest.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(path), str(dest))
                    print(f"   → 移動完了: {dest}")

        return total_size, file_count

    def cleanup_old_logs(self, days=7, dry_run=True):
        """古いログファイルを削除"""
        self.dry_run = dry_run

        print(f"\n📝 {days}日以上前のログを削除")

        log_files = list(self.root.glob("error_logs/*.json"))
        old_files = []

        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)

        for log_file in log_files:
            if log_file.stat().st_mtime < cutoff:
                old_files.append(log_file)

        if not old_files:
            print("   削除対象なし")
            return

        print(f"   削除対象: {len(old_files)} ファイル")
        for f in old_files[:5]:
            print(f"     - {f}")
        if len(old_files) > 5:
            print(f"     ... 他 {len(old_files) - 5} ファイル")

        if not dry_run:
            for f in old_files:
                f.unlink()
            print(f"   ✅ {len(old_files)} ファイルを削除しました")


if __name__ == "__main__":
    import sys

    cleanup = SafeCleanup()

    # コマンドライン引数をチェック
    execute = "--execute" in sys.argv

    if not execute:
        print("=" * 80)
        print("⚠️ ドライランモード - 実際には削除されません")
        print("=" * 80)
        print()

    # バックアップディレクトリのクリーンアップ
    cleanup.cleanup_backups(dry_run=not execute)

    # 古いログの削除
    cleanup.cleanup_old_logs(days=7, dry_run=not execute)

    if not execute:
        print("\n" + "=" * 80)
        print("実際に削除する場合:")
        print("  python safe_cleanup.py --execute")
        print("=" * 80)
