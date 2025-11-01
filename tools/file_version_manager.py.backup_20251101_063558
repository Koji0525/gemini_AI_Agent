#!/usr/bin/env python3
"""
ファイルバージョン管理ツール
- 自動バージョン検出
- 重複チェック
- 運用ルール準拠ファイル生成
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from datetime import datetime


class FileVersionManager:
    def __init__(self, project_root: str = "/workspaces/gemini_AI_Agent"):
        self.project_root = Path(project_root)
        self.excluded_dirs = ["_WIP", "_BACKUP", "_ARCHIVE", "__pycache__", ".git", "node_modules", "venv"]

    def _is_excluded(self, path: Path) -> bool:
        """除外ディレクトリチェック"""
        return any(excluded in str(path) for excluded in self.excluded_dirs)

    def scan_all_files(self, base_name: str) -> Dict[str, List[Path]]:
        """
        プロジェクト全体から指定されたベース名のファイルをスキャン

        Returns:
            {
                'base': [task_executor.py の場所リスト],
                'versioned': [task_executor_v01_xxx.py の場所リスト]
            }
        """
        results = {"base": [], "versioned": []}

        # パターン定義
        base_pattern = f"{base_name}.py"
        version_pattern = re.compile(rf"{re.escape(base_name)}_v\d{{2}}_\w+\.py")

        # 全ファイルスキャン
        for py_file in self.project_root.rglob("*.py"):
            if self._is_excluded(py_file):
                continue

            filename = py_file.name

            if filename == base_pattern:
                results["base"].append(py_file)
            elif version_pattern.match(filename):
                results["versioned"].append(py_file)

        return results

    def detect_max_version(self, base_name: str, target_dir: Path) -> int:
        """
        指定ディレクトリ内の最大バージョン番号を検出

        Returns:
            最大バージョン番号（存在しない場合は0）
        """
        pattern = re.compile(rf"{re.escape(base_name)}_v(\d{{2}})_\w+\.py")
        max_version = 0

        for py_file in target_dir.glob(f"{base_name}_v*_*.py"):
            match = pattern.match(py_file.name)
            if match:
                version = int(match.group(1))
                max_version = max(max_version, version)

        return max_version

    def check_duplicates(self) -> Dict[str, List[Path]]:
        """
        プロジェクト全体で重複ファイル名をチェック

        Returns:
            {
                'task_executor.py': [path1, path2, ...],
                ...
            }
        """
        file_map = defaultdict(list)

        for py_file in self.project_root.rglob("*.py"):
            if self._is_excluded(py_file):
                continue

            filename = py_file.name
            file_map[filename].append(py_file)

        # 重複のみ返す
        return {name: paths for name, paths in file_map.items() if len(paths) > 1}

    def validate_filename(self, filename: str) -> Tuple[bool, str]:
        """
        ファイル名が運用ルールに準拠しているかチェック

        Returns:
            (準拠しているか, エラーメッセージ)
        """
        # パターン: [ベース名]_v[XX]_[機能名].py
        pattern = re.compile(r"^[a-z_]+_v\d{2}_[a-z_]+\.py$")

        if not pattern.match(filename):
            if "-" in filename:
                return False, "❌ ハイフン使用禁止（アンダースコアのみ）"
            elif not re.search(r"_v\d{2}_", filename):
                return False, "❌ バージョン番号が不正（v01, v02形式）"
            else:
                return False, "❌ 命名規則違反（[base]_v[XX]_[feature].py）"

        return True, ""

    def generate_filename(self, base_name: str, feature_name: str, target_dir: Path) -> str:
        """
        運用ルールに準拠したファイル名を自動生成

        Args:
            base_name: ベースファイル名（例: task_executor）
            feature_name: 機能名（例: phase11_monitoring）
            target_dir: 配置先ディレクトリ

        Returns:
            生成されたファイル名
        """
        # 最大バージョン番号を取得
        max_version = self.detect_max_version(base_name, target_dir)
        next_version = max_version + 1

        # 機能名をサニタイズ（ハイフン→アンダースコア）
        clean_feature = feature_name.replace("-", "_").lower()

        # ファイル名生成
        filename = f"{base_name}_v{next_version:02d}_{clean_feature}.py"

        return filename

    def create_file(
        self, base_name: str, feature_name: str, target_dir: str, template_path: Optional[str] = None
    ) -> Path:
        """
        運用ルールに準拠したファイルを作成

        Args:
            base_name: ベースファイル名
            feature_name: 機能名
            target_dir: 配置先ディレクトリ
            template_path: テンプレートファイルのパス（任意）

        Returns:
            作成されたファイルのパス
        """
        target_path = Path(target_dir)

        # ファイル名生成
        filename = self.generate_filename(base_name, feature_name, target_path)
        filepath = target_path / filename

        # 重複チェック
        if filepath.exists():
            raise FileExistsError(f"❌ ファイルが既に存在します: {filepath}")

        # ファイル作成
        if template_path and Path(template_path).exists():
            # テンプレートからコピー
            import shutil

            shutil.copy2(template_path, filepath)
            print(f"✅ テンプレートからコピー: {template_path}")
        else:
            # 空ファイル作成（ヘッダー付き）
            header = f'''#!/usr/bin/env python3

    def backup_before_edit(self, file_path: str, reason: str = ""):
        """修正前の自動バックアップ"""
        from pathlib import Path
        from datetime import datetime
        
        if not Path(file_path).exists():
            print(f"❌ ファイルが見つかりません: {file_path}")
            return False
        
        # バックアップディレクトリ作成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reason_slug = reason.replace(" ", "_") if reason else "backup"
        backup_dir = Path(f"_BACKUP/{timestamp}_{reason_slug}")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # ファイルコピー
        import shutil
        dest = backup_dir / Path(file_path).name
        shutil.copy2(file_path, dest)
        
        print(f"✅ バックアップ作成: {dest}")
        return True

"""
{filename}

作成日: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
機能: {feature_name}
ベース: {base_name}
"""

# TODO: 実装をここに追加
'''
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(header)

        # 実行権限付与
        filepath.chmod(0o755)

        return filepath

    def interactive_create(self):
        """対話式ファイル作成"""
        print("\n" + "=" * 70)
        print("🎯 ファイルバージョン管理ツール")
        print("=" * 70)
        print()

        # STEP 1: ベースファイル名
        base_name = input("📝 ベースファイル名を入力（例: task_executor）: ").strip()
        if not base_name:
            print("❌ ベースファイル名は必須です")
            return

        # STEP 2: 配置先ディレクトリ
        print(f"\n📂 {base_name} の既存ファイルをスキャン中...")
        scan_results = self.scan_all_files(base_name)

        # 既存ファイルの表示
        if scan_results["base"]:
            print(f"\n🔍 ベースファイル（{base_name}.py）の場所:")
            for path in scan_results["base"]:
                print(f"   - {path.relative_to(self.project_root)}")

            # ディレクトリ候補
            target_dir_default = scan_results["base"][0].parent
        else:
            print(f"\n⚠️ {base_name}.py が見つかりません")
            target_dir_default = self.project_root / "scripts"

        if scan_results["versioned"]:
            print(f"\n📋 既存バージョンファイル:")
            # ディレクトリごとにグループ化
            dir_map = defaultdict(list)
            for path in scan_results["versioned"]:
                dir_map[path.parent].append(path)

            for dir_path, files in sorted(dir_map.items()):
                print(f"\n   📁 {dir_path.relative_to(self.project_root)}/")
                for file in sorted(files):
                    print(f"      - {file.name}")

        # ディレクトリ入力
        print(f"\n📂 配置先ディレクトリ:")
        print(f"   デフォルト: {target_dir_default.relative_to(self.project_root)}")
        target_dir_input = input("   変更する場合はパスを入力（Enterでデフォルト）: ").strip()

        if target_dir_input:
            target_dir = self.project_root / target_dir_input
        else:
            target_dir = target_dir_default

        if not target_dir.exists():
            print(f"❌ ディレクトリが存在しません: {target_dir}")
            return

        # STEP 3: 最大バージョン番号を表示
        max_version = self.detect_max_version(base_name, target_dir)
        next_version = max_version + 1

        print(f"\n🔢 バージョン情報:")
        print(f"   現在の最大バージョン: v{max_version:02d}")
        print(f"   次のバージョン: v{next_version:02d}")

        # STEP 4: 機能名
        feature_name = input("\n📝 機能名を入力（例: phase11_monitoring）: ").strip()
        if not feature_name:
            print("❌ 機能名は必須です")
            return

        # ファイル名生成
        filename = self.generate_filename(base_name, feature_name, target_dir)
        filepath = target_dir / filename

        # STEP 5: 確認
        print(f"\n✨ 生成されるファイル:")
        print(f"   📄 {filepath.relative_to(self.project_root)}")
        print()

        # バリデーション
        is_valid, error_msg = self.validate_filename(filename)
        if not is_valid:
            print(error_msg)
            return

        # 重複チェック
        print("🔍 重複チェック中...")
        duplicates = self.check_duplicates()
        if filename in duplicates:
            print(f"❌ 重複エラー: {filename} が以下の場所に存在します:")
            for dup_path in duplicates[filename]:
                print(f"   - {dup_path.relative_to(self.project_root)}")
            return

        print("✅ 重複なし")

        # STEP 6: テンプレート
        print("\n📋 テンプレート:")
        print("   1. 空ファイル（デフォルトヘッダーのみ）")
        print("   2. 既存ファイルからコピー")

        template_choice = input("   選択（1 or 2）[1]: ").strip() or "1"

        template_path = None
        if template_choice == "2":
            template_input = input("   コピー元ファイルのパスを入力: ").strip()
            if template_input:
                template_path = self.project_root / template_input
                if not template_path.exists():
                    print(f"⚠️ ファイルが見つかりません: {template_path}")
                    print("   空ファイルを作成します")
                    template_path = None

        # STEP 7: ファイル作成
        confirm = input("\n✅ ファイルを作成しますか？ (y/N): ").strip().lower()
        if confirm != "y":
            print("❌ キャンセルしました")
            return

        try:
            created_file = self.create_file(
                base_name, feature_name, str(target_dir), str(template_path) if template_path else None
            )

            print("\n" + "=" * 70)
            print("🎉 ファイル作成完了！")
            print("=" * 70)
            print(f"📄 {created_file.relative_to(self.project_root)}")
            print()
            print("📝 次のステップ:")
            print("   1. ファイルを編集して実装を追加")
            print("   2. 構文チェック: python3 -m py_compile <ファイル名>")
            print("   3. コミット前に重複チェックを実行")

        except Exception as e:
            print(f"❌ エラー: {e}")

    def quick_create(self, base_name: str, feature_name: str, target_dir: Optional[str] = None):
        """ワンライナー用の簡易作成"""
        if target_dir is None:
            # ベースファイルを探す
            scan_results = self.scan_all_files(base_name)
            if scan_results["base"]:
                target_dir = str(scan_results["base"][0].parent)
            else:
                target_dir = "scripts"

        target_path = self.project_root / target_dir
        created_file = self.create_file(base_name, feature_name, str(target_path))

        print(f"✅ 作成完了: {created_file.relative_to(self.project_root)}")
        return created_file


def main():
    import argparse

    parser = argparse.ArgumentParser(description="ファイルバージョン管理ツール")
    parser.add_argument("--check-duplicates", action="store_true", help="重複ファイルチェックのみ実行")
    parser.add_argument(
        "--quick", nargs=2, metavar=("BASE", "FEATURE"), help="ワンライナー作成: --quick task_executor phase11"
    )
    parser.add_argument("--target-dir", help="配置先ディレクトリ（--quick使用時）")

    args = parser.parse_args()

    manager = FileVersionManager()

    if args.check_duplicates:
        # 重複チェックのみ
        print("\n🔍 重複ファイルチェック開始...")
        duplicates = manager.check_duplicates()

        if not duplicates:
            print("✅ 重複ファイルなし")
        else:
            print(f"\n❌ {len(duplicates)}個の重複ファイルが検出されました:\n")
            for filename, paths in sorted(duplicates.items()):
                print(f"📄 {filename} ({len(paths)}個)")
                for path in paths:
                    print(f"   - {path.relative_to(manager.project_root)}")
                print()

    elif args.quick:
        # ワンライナー作成
        base_name, feature_name = args.quick
        manager.quick_create(base_name, feature_name, args.target_dir)

    else:
        # 対話式作成
        manager.interactive_create()


if __name__ == "__main__":
    main()
