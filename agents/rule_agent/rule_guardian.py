#!/usr/bin/env python3
"""ルール遵守チェックエージェント"""

import sys

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from tools.rule_search import search_rules


class RuleGuardian:
    """ルール遵守を監視"""

    def check_before_commit(self):
        """コミット前チェック"""

        print("🛡️ ルール遵守チェック")

        # 変更ファイルを取得
        import subprocess

        result = subprocess.run(["git", "diff", "--name-only", "--cached"], capture_output=True, text=True)

        changed_files = result.stdout.strip().split("\n")

        # 各ファイルに対して関連ルールを確認
        for file in changed_files:
            if file.endswith(".py"):
                print(f"\n📄 {file}")

                # バックアップ確認
                if not self._has_backup(file):
                    print("  ⚠️ バックアップなし（R001違反）")
                    return False

        print("\n✅ 全ルール遵守")
        return True

    def _has_backup(self, file):
        """バックアップ存在確認"""
        from pathlib import Path

        backups = list(Path("_BACKUP").rglob(Path(file).name))
        return len(backups) > 0


if __name__ == "__main__":
    guardian = RuleGuardian()

    if not guardian.check_before_commit():
        print("\n❌ ルール違反を検出")
        sys.exit(1)
