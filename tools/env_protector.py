#!/usr/bin/env python3
"""
🛡️ .env保護ツール v1.0
目的: .envファイルの意図しない上書きを防止
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path


class EnvProtector:
    def __init__(self, env_path=".env"):
        self.env_path = Path(env_path)
        self.backup_dir = Path("_BACKUP/env_backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.lock_file = Path(".env.lock")

    def backup(self):
        """現在の.envをバックアップ"""
        if not self.env_path.exists():
            print("⚠️  .envファイルが存在しません")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"env_backup_{timestamp}.txt"

        shutil.copy2(self.env_path, backup_path)
        print(f"✅ バックアップ作成: {backup_path}")

        # メタデータ保存
        meta = {
            "timestamp": timestamp,
            "size": os.path.getsize(self.env_path),
            "keys": self._get_keys(),
        }
        meta_path = self.backup_dir / f"env_backup_{timestamp}.json"
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2)

        return backup_path

    def _get_keys(self):
        """現在の.envのキー一覧取得"""
        keys = []
        with open(self.env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key = line.split("=")[0].strip()
                    keys.append(key)
        return keys

    def protect(self):
        """読み取り専用に設定"""
        if not self.env_path.exists():
            print("⚠️  .envファイルが存在しません")
            return

        os.chmod(self.env_path, 0o444)  # 読み取り専用
        print(f"🔒 .envを読み取り専用に設定しました")

        # ロックファイル作成
        with open(self.lock_file, "w") as f:
            f.write(f"Locked at {datetime.now().isoformat()}\n")

    def unprotect(self):
        """書き込み可能に戻す"""
        if not self.env_path.exists():
            return

        os.chmod(self.env_path, 0o644)  # 読み書き可能
        print(f"🔓 .envを書き込み可能に戻しました")

        if self.lock_file.exists():
            self.lock_file.unlink()

    def validate_change(self, new_content):
        """変更内容の検証"""
        old_keys = set(self._get_keys())

        # 新しい内容からキーを抽出
        new_keys = set()
        for line in new_content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key = line.split("=")[0].strip()
                new_keys.append(key)

        deleted = old_keys - new_keys
        added = new_keys - old_keys

        if deleted:
            print(f"⚠️  削除される設定: {deleted}")
            response = input("本当に削除しますか？ (yes/no): ")
            if response.lower() != "yes":
                return False

        if added:
            print(f"ℹ️  追加される設定: {added}")

        return True

    def safe_update(self, updates: dict):
        """安全な更新（既存キーは保持）"""
        # バックアップ
        self.backup()

        # 既存の内容を読み込み
        existing = {}
        if self.env_path.exists():
            with open(self.env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        existing[key.strip()] = value.strip()

        # 更新（既存は保持、新規は追加）
        existing.update(updates)

        # 書き込み
        self.unprotect()
        with open(self.env_path, "w") as f:
            for key, value in sorted(existing.items()):
                f.write(f"{key}={value}\n")
        self.protect()

        print(f"✅ .envを安全に更新しました（{len(updates)}件）")


def main():
    import argparse

    parser = argparse.ArgumentParser(description=".env保護ツール")
    parser.add_argument("action", choices=["backup", "protect", "unprotect", "validate"])
    parser.add_argument("--env-path", default=".env", help=".envファイルのパス")

    args = parser.parse_args()
    protector = EnvProtector(args.env_path)

    if args.action == "backup":
        protector.backup()
    elif args.action == "protect":
        protector.protect()
    elif args.action == "unprotect":
        protector.unprotect()
    elif args.action == "validate":
        print("検証モード（対話式）")


if __name__ == "__main__":
    main()
