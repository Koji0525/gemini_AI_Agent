#!/usr/bin/env python3
"""
📦 File Version Manager v3.0（簡易化版）

【v3.0 変更の理由】
何が起きた:
- v2.0のコマンドが複雑で誤用が多発
- --quick オプションの挙動が不明確
- 新規バージョン作成の標準フローが確立されていない

原因:
- オプションが多すぎる（--quick, --backup, --promote）
- 引数の順序が複雑（位置引数 vs キーワード引数）
- 使用例が不足

狙い:
- 標準フロー統一: `tool.py <既存ファイル> "理由"` のみ
- 自動化強化: バックアップ + 新規作成 + 重複チェックを一括実行
- 拡張性: 将来的なCI/CD統合を考慮した設計

【設計思想】
- シンプル: 1つのコマンドで完結
- 汎用性: 他プロジェクトでも使用可能
- 保守性: 設定は外部ファイル化可能
"""

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


class FileVersionManagerV3:
    """ファイルバージョン管理ツール v3.0"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.backup_root = self.project_root / "_BACKUP"
        self.exclude_dirs = {
            "_WIP",
            "_ARCHIVE",
            "_BACKUP",
            "__pycache__",
            ".git",
            "node_modules",
            "wordpress-core",
            ".venv",
            "venv",
        }

    def create_new_version(self, existing_file: str, reason: str) -> int:
        """
        標準フロー: バックアップ + 新規バージョン作成

        Args:
            existing_file: 既存ファイルのパス（例: script_v05.py）
            reason: 変更理由（例: "高速化実装"）

        Returns:
            0: 成功, 1: 失敗
        """
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🚀 File Version Manager v3.0")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        existing_path = Path(existing_file)

        # ファイル存在チェック
        if not existing_path.exists():
            print(f"❌ エラー: ファイルが見つかりません: {existing_file}")
            return 1

        # STEP 1: バックアップ作成
        print("\n📦 STEP 1: バックアップ作成")
        print("=" * 50)

        backup_dir = self._create_backup(existing_path, reason)
        if not backup_dir:
            return 1

        print(f"✅ バックアップ完了: {backup_dir}")

        # STEP 2: 次のバージョン番号を検出
        print("\n🔢 STEP 2: バージョン番号検出")
        print("=" * 50)

        next_version = self._get_next_version(existing_path)
        if not next_version:
            print("❌ バージョン番号の検出に失敗")
            return 1

        print(f"✅ 次のバージョン: v{next_version}")

        # STEP 3: 新規バージョンファイル作成
        print("\n📝 STEP 3: 新規バージョンファイル作成")
        print("=" * 50)

        new_file = self._create_new_file(existing_path, next_version)
        if not new_file:
            return 1

        print(f"✅ 新規ファイル作成: {new_file}")

        # STEP 4: 重複チェック
        print("\n🔍 STEP 4: 重複チェック")
        print("=" * 50)

        duplicates = self._check_duplicates(new_file.name)
        if duplicates:
            print(f"⚠️  類似ファイル検出: {len(duplicates)}件")
            for dup in duplicates[:5]:
                print(f"   📄 {dup}")
            if len(duplicates) > 5:
                print(f"   ... 他 {len(duplicates) - 5}件")
        else:
            print("✅ 重複ファイルなし")

        # 完了メッセージ
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🎉 新規バージョン作成完了！")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("\n【次のステップ】")
        print(f"1. エディタで編集: {new_file}")
        print("2. 動作確認")
        print(f"3. 本番昇格: python3 tools/file_version_manager.py --promote {new_file}")

        return 0

    def _create_backup(self, file_path: Path, reason: str) -> Path:
        """バックアップディレクトリを作成してファイルをコピー"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.backup_root / f"{timestamp}_{reason}"

        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_file = backup_dir / file_path.name
            shutil.copy2(file_path, backup_file)
            return backup_dir
        except Exception as e:
            print(f"❌ バックアップエラー: {e}")
            return None

    def _get_next_version(self, file_path: Path) -> int:
        """
        次のバージョン番号を検出

        ロジック:
        1. ファイル名からバージョン番号を抽出（例: v05 → 5）
        2. 同じディレクトリ内の最大バージョンを検索
        3. max_version + 1 を返す
        """
        # 現在のバージョン番号を抽出
        match = re.search(r"_v(\d+)", file_path.stem)
        if not match:
            print("⚠️  バージョン番号が見つかりません（例: _v05）")
            return 1

        current_version = int(match.group(1))

        # 同じディレクトリ内の最大バージョンを検索
        base_name = re.sub(r"_v\d+.*$", "", file_path.stem)
        pattern = re.compile(rf"{re.escape(base_name)}_v(\d+)")

        max_version = current_version
        for sibling in file_path.parent.glob(f"{base_name}_v*.py"):
            match = pattern.search(sibling.stem)
            if match:
                ver = int(match.group(1))
                max_version = max(max_version, ver)

        return max_version + 1

    def _create_new_file(self, existing_path: Path, next_version: int) -> Path:
        """新規バージョンファイルを作成"""
        # ファイル名生成
        base_name = re.sub(r"_v\d+", "", existing_path.stem)
        suffix_match = re.search(r"_v\d+(.*)$", existing_path.stem)
        suffix = suffix_match.group(1) if suffix_match else ""

        # 修正: 桁数指定を削除（方法1）
        new_name = f"{base_name}_v{next_version}{suffix}.py"
        new_path = existing_path.parent / new_name

        try:
            shutil.copy2(existing_path, new_path)
            return new_path
        except Exception as e:
            print(f"❌ ファイル作成エラー: {e}")
            return None

    def _check_duplicates(self, filename: str) -> list:
        """プロジェクト全体で類似ファイルを検索"""
        base_name = re.sub(r"_v\d+.*$", "", Path(filename).stem)
        duplicates = []

        for py_file in self.project_root.rglob("*.py"):
            # 除外ディレクトリをスキップ
            if any(exclude in str(py_file) for exclude in self.exclude_dirs):
                continue

            if base_name in py_file.stem and py_file.name != filename:
                duplicates.append(str(py_file.relative_to(self.project_root)))

        return duplicates

    def promote_to_production(self, version_file: str) -> int:
        """
        バージョンファイルを本番環境に昇格

        Args:
            version_file: バージョンファイルのパス（例: script_v06.py）

        Returns:
            0: 成功, 1: 失敗
        """
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🚀 本番環境への昇格")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        version_path = Path(version_file)

        if not version_path.exists():
            print(f"❌ エラー: ファイルが見つかりません: {version_file}")
            return 1

        # 本番ファイル名を生成（バージョン番号を削除）
        base_name = re.sub(r"_v\d+.*$", "", version_path.stem)
        production_file = version_path.parent / f"{base_name}.py"

        print("\n📝 昇格対象:")
        print(f"   From: {version_path}")
        print(f"   To:   {production_file}")

        # 確認
        if production_file.exists():
            print("\n⚠️  警告: 本番ファイルが既に存在します")
            print("   上書きしますか？ (y/N): ", end="")
            response = input().strip().lower()
            if response != "y":
                print("❌ キャンセルしました")
                return 1

            # 既存ファイルをバックアップ
            self._create_backup(production_file, "本番昇格前バックアップ")
            print(f"✅ バックアップ完了")

        # コピー実行
        try:
            shutil.copy2(version_path, production_file)
            print(f"\n✅ 昇格完了: {production_file}")
            return 0
        except Exception as e:
            print(f"❌ 昇格エラー: {e}")
            return 1

    def check_duplicates_only(self, exclude_dirs: list = None) -> int:
        """重複チェックのみ実行"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🔍 重複ファイルチェック")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        if exclude_dirs:
            self.exclude_dirs.update(exclude_dirs)

        # バージョン付きファイルをグループ化
        version_files = {}
        for py_file in self.project_root.rglob("*.py"):
            if any(exclude in str(py_file) for exclude in self.exclude_dirs):
                continue

            match = re.search(r"(.+)_v\d+", py_file.stem)
            if match:
                base_name = match.group(1)
                if base_name not in version_files:
                    version_files[base_name] = []
                version_files[base_name].append(py_file)

        # 重複検出
        duplicates_found = False
        for base_name, files in version_files.items():
            if len(files) > 1:
                duplicates_found = True
                print(f"\n⚠️  重複検出: {base_name}")
                for f in sorted(files):
                    print(f"   📄 {f.relative_to(self.project_root)}")

        if not duplicates_found:
            print("\n✅ 重複ファイルなし")

        return 0


def main():
    parser = argparse.ArgumentParser(
        description="📦 File Version Manager v3.0（簡易化版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 【標準フロー】新規バージョン作成（バックアップ + 作成 + 重複チェック）
  python3 tools/file_version_manager.py <既存ファイル> "理由"

  例: v05 から v06 を作成
  python3 tools/file_version_manager.py \\
      agents/git_agent/auto_commit_push_v05_optimized.py \\
      "高速品質ゲート実装"

  # 【本番昇格】バージョンファイルを標準ファイルにする
  python3 tools/file_version_manager.py --promote <v06ファイル>

  # 【重複チェック】プロジェクト全体をスキャン
  python3 tools/file_version_manager.py --check-duplicates

v3.0 改善点:
  ✅ 標準フロー統一（1コマンドで完結）
  ✅ 自動化強化（バックアップ + 作成 + チェック）
  ✅ エラーハンドリング改善
  ✅ CI/CD統合を考慮した設計
        """,
    )

    # 位置引数（標準フロー用）
    parser.add_argument(
        "file",
        nargs="?",
        help="既存ファイルのパス（新規バージョン作成用）",
    )
    parser.add_argument(
        "reason",
        nargs="?",
        help="変更理由（新規バージョン作成用）",
    )

    # オプション引数
    parser.add_argument(
        "--promote",
        help="本番環境に昇格するバージョンファイル",
    )
    parser.add_argument(
        "--check-duplicates",
        action="store_true",
        help="重複チェックのみ実行",
    )
    parser.add_argument(
        "--exclude-dirs",
        nargs="*",
        help="除外ディレクトリ（重複チェック用）",
    )

    args = parser.parse_args()

    manager = FileVersionManagerV3()

    # コマンド振り分け
    if args.promote:
        return manager.promote_to_production(args.promote)
    elif args.check_duplicates:
        return manager.check_duplicates_only(args.exclude_dirs)
    elif args.file and args.reason:
        return manager.create_new_version(args.file, args.reason)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())


# ==========================================
# 追加機能: 最新版記録システム
# 追加日: 2025-11-10
# ==========================================

import json
from datetime import datetime


class VersionTracker:
    """
    最新バージョンを記録・管理するクラス
    VERSION_STATUS.json と連携
    """

    def __init__(self, status_file: str = "scripts/VERSION_STATUS.json"):
        self.status_file = Path(status_file)
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        self.status = self._load_status()

    def _load_status(self) -> dict:
        """ステータスファイルを読み込み"""
        if self.status_file.exists():
            with open(self.status_file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {
                "last_updated": None,
                "production": {},
                "staging": {},
                "deprecated": [],
                "history": [],
            }

    def _save_status(self):
        """ステータスファイルを保存"""
        self.status["last_updated"] = datetime.now().isoformat()

        with open(self.status_file, "w", encoding="utf-8") as f:
            json.dump(self.status, f, indent=2, ensure_ascii=False)

        print(f"✅ {self.status_file} を更新しました")

    def register_version(
        self,
        file_path: str,
        status: str,
        description: str = "",
        features: list = None,
        test_result: str = "not_tested",
    ):
        """
        新しいバージョンを登録

        Args:
            file_path: ファイルパス
            status: "production" | "staging" | "development"
            description: 説明
            features: 機能リスト
            test_result: テスト結果
        """
        file_path = Path(file_path)

        if not file_path.exists():
            print(f"⚠️  ファイルが存在しません: {file_path}")
            return False

        version_info = {
            "file": file_path.name,
            "path": str(file_path),
            "status": test_result,
            "description": description,
            "features": features or [],
            "registered_at": datetime.now().isoformat(),
            "file_size": file_path.stat().st_size,
        }

        if status == "production":
            if self.status["production"]:
                self.status["history"].append(
                    {**self.status["production"], "demoted_at": datetime.now().isoformat()}
                )

            self.status["production"] = version_info
            print(f"✅ 本番環境版として登録: {file_path.name}")

        elif status == "staging":
            self.status["staging"] = version_info
            print(f"✅ ステージング版として登録: {file_path.name}")

        self._save_status()
        return True

    def get_production_version(self) -> dict:
        """本番環境版の情報を取得"""
        return self.status.get("production", {})

    def get_staging_version(self) -> dict:
        """ステージング版の情報を取得"""
        return self.status.get("staging", {})

    def print_status(self):
        """現在のステータスを表示"""
        print("\n" + "=" * 60)
        print("📊 バージョンステータス")
        print("=" * 60)

        prod = self.status.get("production", {})
        if prod:
            print(f"\n✅ 本番環境版:")
            print(f"   ファイル: {prod.get('file', 'N/A')}")
            print(f"   ステータス: {prod.get('status', 'N/A')}")
        else:
            print(f"\n⚠️  本番環境版: 未設定")

        stg = self.status.get("staging", {})
        if stg:
            print(f"\n🔧 ステージング版:")
            print(f"   ファイル: {stg.get('file', 'N/A')}")
            print(f"   ステータス: {stg.get('status', 'N/A')}")

        print("\n" + "=" * 60)

    def mark_as_broken(self, file_name: str, error: str):
        """バージョンを壊れているとしてマーク"""

        # stagingを確認
        if self.status["staging"].get("file") == file_name:
            self.status["staging"]["status"] = "broken"
            self.status["staging"]["error"] = error
            self.status["staging"]["marked_at"] = datetime.now().isoformat()
            self._save_status()
            print(f"⚠️  {file_name} を壊れているとマーク")
            return True

        # productionを確認
        if self.status["production"].get("file") == file_name:
            self.status["production"]["status"] = "broken"
            self.status["production"]["error"] = error
            self.status["production"]["marked_at"] = datetime.now().isoformat()
            self._save_status()
            print(f"🚨 警告: 本番環境版 {file_name} が壊れています！")
            return True

        return False

    def mark_as_broken(self, file_name: str, error: str):
        """バージョンを壊れているとしてマーク"""
        if self.status["staging"].get("file") == file_name:
            self.status["staging"]["status"] = "broken"
            self.status["staging"]["error"] = error
            self.status["staging"]["marked_at"] = datetime.now().isoformat()
            self._save_status()
            print(f"⚠️  {file_name} を壊れているとマーク")
            return True
        if self.status["production"].get("file") == file_name:
            self.status["production"]["status"] = "broken"
            self.status["production"]["error"] = error
            self._save_status()
            print(f"🚨 警告: 本番環境版 {file_name} が壊れています！")
            return True
        return False
