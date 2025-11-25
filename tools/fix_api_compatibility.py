"""
API互換性問題の自動修正ツール
append_row → append_rows などの修正を自動化
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List


class APICompatibilityFixer:
    """API互換性問題を自動修正"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.replacements = {
            # GoogleSheetsManager のメソッド置換
            r"sheets\.append_row\(": "sheets.append_rows(",
            r"self\.sheets\.append_row\(": "self.sheets.append_rows(",
            r"worksheet\.append_row\(": "worksheet.append_rows(",
            r"sheet\.append_row\(": "sheet.append_rows(",
            r"log_sheet\.append_row\(": "log_sheet.append_rows(",
            r"kb_sheet\.append_row\(": "kb_sheet.append_rows(",
            r"context_sheet\.append_row\(": "context_sheet.append_rows(",
            r"retry_sheet\.append_row\(": "retry_sheet.append_rows(",
            r"task_sheet\.append_row\(": "task_sheet.append_rows(",
            r"design_sheet\.append_row\(": "design_sheet.append_rows(",
            # write_data の置換
            r"sheets\.write_data\(": "sheets.update_range(",
            r"self\.sheets\.write_data\(": "self.sheets.update_range(",
            # write_rows の置換
            r"accessor\.write_rows\(": "accessor.sheets.append_rows(",
        }

    def find_affected_files(self, root_dir: str = ".") -> List[Path]:
        """影響を受けるファイルを検索"""
        affected_files = []
        python_files = list(Path(root_dir).rglob("*.py"))

        for file_path in python_files:
            if self._file_has_compatibility_issues(file_path):
                affected_files.append(file_path)

        return affected_files

    def _file_has_compatibility_issues(self, file_path: Path) -> bool:
        """ファイルに互換性問題があるかチェック"""
        try:
            content = file_path.read_text(encoding="utf-8")

            for pattern in self.replacements:
                if re.search(pattern, content):
                    return True

            return False
        except Exception as e:
            self.logger.warning(f"ファイル読み込みエラー {file_path}: {e}")
            return False

    def fix_file(self, file_path: Path, backup: bool = True) -> bool:
        """単一ファイルを修正"""
        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content

            # バックアップ作成
            if backup:
                backup_path = file_path.with_suffix(".py.backup")
                backup_path.write_text(original_content, encoding="utf-8")
                self.logger.info(f"バックアップ作成: {backup_path}")

            # 置換実行
            for pattern, replacement in self.replacements.items():
                content = re.sub(pattern, replacement, content)

            # 変更がある場合のみ書き込み
            if content != original_content:
                file_path.write_text(content, encoding="utf-8")
                self.logger.info(f"修正完了: {file_path}")
                return True
            else:
                self.logger.info(f"変更なし: {file_path}")
                return False

        except Exception as e:
            self.logger.error(f"ファイル修正エラー {file_path}: {e}")
            return False

    def fix_all_files(self, root_dir: str = ".", backup: bool = True) -> Dict[str, Any]:
        """すべてのファイルを修正"""
        affected_files = self.find_affected_files(root_dir)
        results = {
            "total_files": len(affected_files),
            "fixed_files": 0,
            "failed_files": 0,
            "details": [],
        }

        self.logger.info(f"修正対象ファイル数: {len(affected_files)}")

        for file_path in affected_files:
            try:
                success = self.fix_file(file_path, backup)

                if success:
                    results["fixed_files"] += 1
                    results["details"].append({"file": str(file_path), "status": "fixed"})
                else:
                    results["details"].append({"file": str(file_path), "status": "no_changes"})

            except Exception as e:
                results["failed_files"] += 1
                results["details"].append(
                    {"file": str(file_path), "status": "error", "error": str(e)}
                )

        return results


def main():
    """メイン実行関数"""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    fixer = APICompatibilityFixer()

    print("🔧 API互換性問題の自動修正を開始します...")

    # 影響を受けるファイルの検索
    affected_files = fixer.find_affected_files()
    print(f"📁 修正対象ファイル: {len(affected_files)}件")

    for file_path in affected_files:
        print(f"  - {file_path}")

    if not affected_files:
        print("✅ 修正対象ファイルはありません")
        return

    # 修正の実行
    print("\n🔧 修正を実行します...")
    results = fixer.fix_all_files(backup=True)

    # 結果の表示
    print(f"\n📊 修正結果:")
    print(f"  ✅ 修正完了: {results['fixed_files']}件")
    print(
        f"  ℹ️  変更なし: {results['total_files'] - results['fixed_files'] - results['failed_files']}件"
    )
    print(f"  ❌ 失敗: {results['failed_files']}件")

    if results["failed_files"] > 0:
        print("\n⚠️ 失敗したファイル:")
        for detail in results["details"]:
            if detail["status"] == "error":
                print(f"  - {detail['file']}: {detail['error']}")


if __name__ == "__main__":
    main()
