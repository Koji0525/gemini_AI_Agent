#!/usr/bin/env python3
"""
🔧 安全なコード変更ツール
コード変更時の機能削除を防止する自動化ツール
"""
import os
import re
import sys
import difflib
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Set, Tuple, Optional


class SafeCodeModifier:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backup_dir = self.project_root / "_BACKUP" / "code_changes"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, file_path: str) -> str:
        """ファイルのバックアップを作成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"{Path(file_path).name}.{timestamp}.backup"
        shutil.copy2(file_path, backup_file)
        return str(backup_file)

    def analyze_file_structure(self, content: str) -> dict:
        """ファイルの構造を分析"""
        structure = {"imports": set(), "classes": set(), "functions": set(), "constants": set()}

        # インポート文を検出
        imports = re.findall(
            r"^(import\s+\w+|from\s+\w+\s+import\s+[\w\s,]+)", content, re.MULTILINE
        )
        structure["imports"].update(imports)

        # クラスを検出
        classes = re.findall(r"^class\s+(\w+)", content, re.MULTILINE)
        structure["classes"].update(classes)

        # 関数を検出
        functions = re.findall(r"^def\s+(\w+)", content, re.MULTILINE)
        structure["functions"].update(functions)

        # 定数を検出（大文字の変数）
        constants = re.findall(r"^([A-Z_][A-Z0-9_]*)\s*=", content, re.MULTILINE)
        structure["constants"].update(constants)

        return structure

    def validate_change(self, original: str, modified: str) -> Tuple[bool, List[str]]:
        """変更の妥当性を検証"""
        issues = []

        # 元の構造と変更後の構造を分析
        original_structure = self.analyze_file_structure(original)
        modified_structure = self.analyze_file_structure(modified)

        # 削除された要素をチェック
        for category in ["imports", "classes", "functions", "constants"]:
            original_items = original_structure[category]
            modified_items = modified_structure[category]
            deleted = original_items - modified_items

            if deleted:
                issues.append(f"削除された{category}: {', '.join(deleted)}")

        # 重要なパターンが削除されていないかチェック
        critical_patterns = [
            (r"class\s+\w+.*:", "クラス定義"),
            (r"def\s+\w+\(.*\):", "関数定義"),
            (r"@\w+", "デコレータ"),
            (r"__\w+__", "マジックメソッド"),
        ]

        for pattern, description in critical_patterns:
            original_count = len(re.findall(pattern, original))
            modified_count = len(re.findall(pattern, modified))

            if modified_count < original_count:
                issues.append(f"{description}が {original_count} → {modified_count} に減少")

        return len(issues) == 0, issues

    def show_diff(self, original: str, modified: str, file_path: str):
        """変更差分を表示"""
        print(f"📋 {file_path} の変更差分:")
        print("=" * 60)

        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            modified.splitlines(keepends=True),
            fromfile="original",
            tofile="modified",
            n=3,
        )

        diff_lines = list(diff)
        if not diff_lines:
            print("変更はありません")
            return

        for line in diff_lines:
            if line.startswith("+"):
                print(f"\033[92m{line.rstrip()}\033[0m")  # 緑色
            elif line.startswith("-"):
                print(f"\033[91m{line.rstrip()}\033[0m")  # 赤色
            else:
                print(line.rstrip())

        print("=" * 60)

    def safe_modify(self, file_path: str, modification_func, description: str = "") -> bool:
        """安全なファイル修正を実行"""
        print(f"🔧 ファイル修正を開始: {file_path}")
        print(f"📝 修正内容: {description}")

        # ファイルの存在確認
        if not os.path.exists(file_path):
            print(f"❌ ファイルが存在しません: {file_path}")
            return False

        # バックアップ作成
        backup_path = self.create_backup(file_path)
        print(f"✅ バックアップを作成: {backup_path}")

        # 元の内容を読み込み
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()

        # ファイル構造を分析
        print("🔍 ファイル構造を分析中...")
        original_structure = self.analyze_file_structure(original_content)
        print(f"  クラス: {len(original_structure['classes'])}")
        print(f"  関数: {len(original_structure['functions'])}")
        print(f"  インポート: {len(original_structure['imports'])}")

        # 修正を適用
        try:
            modified_content = modification_func(original_content)
        except Exception as e:
            print(f"❌ 修正関数の実行エラー: {e}")
            return False

        # 変更の妥当性を検証
        is_valid, issues = self.validate_change(original_content, modified_content)

        if not is_valid:
            print("❌ 変更が検証に失敗しました:")
            for issue in issues:
                print(f"  ⚠️ {issue}")

            response = input("変更を続行しますか？ (y/N): ")
            if response.lower() != "y":
                print("変更をキャンセルしました")
                return False

        # 差分を表示
        self.show_diff(original_content, modified_content, file_path)

        # ユーザー確認
        response = input("この変更を適用しますか？ (y/N): ")
        if response.lower() != "y":
            print("変更をキャンセルしました")
            return False

        # 変更を適用
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)

        # 構文チェック
        try:
            if file_path.endswith(".py"):
                compile(modified_content, file_path, "exec")
                print("✅ 構文チェック成功")
        except SyntaxError as e:
            print(f"❌ 構文エラー: {e}")
            # バックアップから復元
            shutil.copy2(backup_path, file_path)
            print("✅ バックアップから復元しました")
            return False

        print("🎉 ファイル修正が完了しました")
        return True


def main():
    """コマンドラインインターフェース"""
    if len(sys.argv) < 3:
        print("使用方法: python3 tools/safe_code_modifier.py <ファイルパス> <修正内容の説明>")
        print(
            "例: python3 tools/safe_code_modifier.py tools/sheets_manager.py '環境変数読み込みを改善'"
        )
        sys.exit(1)

    file_path = sys.argv[1]
    description = " ".join(sys.argv[2:])

    modifier = SafeCodeModifier()

    # 修正関数の例（実際にはユーザーが定義する）
    def example_modification(content):
        """例: 単純な文字列置換"""
        # ここに実際の修正ロジックを実装
        return content

    success = modifier.safe_modify(file_path, example_modification, description)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
