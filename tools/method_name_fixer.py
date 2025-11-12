#!/usr/bin/env python3
"""
メソッド名不一致修正ツール
既存コードのメソッド名を一括修正する汎用ツール
"""

import os
import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class MethodNameFixer:
    """メソッド名不一致修正ツール"""

    def __init__(self, config_file: str = None):
        self.method_mappings = self._load_default_mappings()
        if config_file and os.path.exists(config_file):
            self._load_custom_mappings(config_file)

    def _load_default_mappings(self) -> Dict[str, str]:
        """デフォルトのメソッド名マッピングを読み込み"""
        return {
            # Google Sheets関連
            "append_row": "append_rows",
            "safe_get_data": "safe_read",
            # 知識管理関連
            "add_knowledge_entry": "add_knowledge",
            # 共通パターン
            "get_data": "read",
            "put_data": "write",
            "update_data": "update",
        }

    def _load_custom_mappings(self, config_file: str):
        """カスタムマッピングを読み込み"""
        try:
            import yaml

            with open(config_file, "r", encoding="utf-8") as f:
                custom_mappings = yaml.safe_load(f)
                if custom_mappings and "method_mappings" in custom_mappings:
                    self.method_mappings.update(custom_mappings["method_mappings"])
        except Exception as e:
            logger.warning(f"カスタムマッピングの読み込みに失敗: {e}")

    def find_method_usage(self, directory: str, method_name: str) -> List[Tuple[str, int, str]]:
        """
        指定したメソッド名の使用箇所を検索

        Args:
            directory: 検索ディレクトリ
            method_name: 検索するメソッド名

        Returns:
            [(ファイルパス, 行番号, 行内容), ...]
        """
        results = []
        pattern = rf"\.{method_name}\s*\("

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            for line_num, line in enumerate(f, 1):
                                if re.search(pattern, line):
                                    results.append((file_path, line_num, line.strip()))
                    except Exception as e:
                        logger.warning(f"ファイル読み込みエラー: {file_path} - {e}")

        return results

    def fix_method_name(
        self, file_path: str, line_num: int, old_method: str, new_method: str
    ) -> bool:
        """
        単一ファイルのメソッド名を修正

        Args:
            file_path: ファイルパス
            line_num: 行番号
            old_method: 古いメソッド名
            new_method: 新しいメソッド名

        Returns:
            修正成功可否
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if line_num > len(lines):
                logger.error(f"行番号 {line_num} がファイル範囲外です: {file_path}")
                return False

            old_line = lines[line_num - 1]
            new_line = re.sub(rf"\.{re.escape(old_method)}\s*\(", f".{new_method}(", old_line)

            if old_line != new_line:
                lines[line_num - 1] = new_line

                # バックアップ作成
                backup_path = f"{file_path}.backup"
                if not os.path.exists(backup_path):
                    import shutil

                    shutil.copy2(file_path, backup_path)

                # 修正を書き込み
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)

                logger.info(f"✅ 修正完了: {file_path}:{line_num}")
                logger.info(f"   前: {old_line.strip()}")
                logger.info(f"   後: {new_line.strip()}")
                return True
            else:
                logger.warning(f"⚠️  修正不要: {file_path}:{line_num}")
                return False

        except Exception as e:
            logger.error(f"❌ 修正失敗: {file_path}:{line_num} - {e}")
            return False

    def scan_and_fix_all(self, directory: str, dry_run: bool = False) -> Dict[str, Dict]:
        """
        全メソッド名をスキャンして修正

        Args:
            directory: 検索ディレクトリ
            dry_run: 実際の修正を行わず検索のみ

        Returns:
            修正結果の統計
        """
        results = {"scanned_files": 0, "found_issues": 0, "fixed_issues": 0, "details": {}}

        for old_method, new_method in self.method_mappings.items():
            logger.info(f"🔍 検索中: {old_method} → {new_method}")
            usages = self.find_method_usage(directory, old_method)

            results["details"][old_method] = {
                "new_method": new_method,
                "found_count": len(usages),
                "fixed_count": 0,
                "usages": [],
            }

            if usages:
                results["found_issues"] += len(usages)
                logger.info(f"   📍 発見: {len(usages)} 箇所")

                for file_path, line_num, line_content in usages:
                    results["details"][old_method]["usages"].append(
                        {"file": file_path, "line": line_num, "content": line_content}
                    )

                    if not dry_run:
                        if self.fix_method_name(file_path, line_num, old_method, new_method):
                            results["details"][old_method]["fixed_count"] += 1
                            results["fixed_issues"] += 1
            else:
                logger.info("   ✅ 問題なし")

        return results

    def generate_report(self, results: Dict, output_file: str = None):
        """レポート生成"""
        report = [
            "=" * 60,
            "メソッド名不一致修正レポート",
            "=" * 60,
            f"スキャンディレクトリ: {results.get('directory', 'N/A')}",
            f"スキャンファイル数: {results.get('scanned_files', 'N/A')}",
            f"発見問題数: {results['found_issues']}",
            f"修正問題数: {results['fixed_issues']}",
            "",
            "詳細:",
        ]

        for old_method, detail in results["details"].items():
            report.append(f"\n🔧 {old_method} → {detail['new_method']}")
            report.append(f"   発見: {detail['found_count']} 箇所")
            report.append(f"   修正: {detail['fixed_count']} 箇所")

            if detail["usages"]:
                report.append("   使用箇所:")
                for usage in detail["usages"]:
                    report.append(f"     📄 {usage['file']}:{usage['line']}")
                    report.append(f"        {usage['content']}")

        report_text = "\n".join(report)
        print(report_text)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report_text)
            logger.info(f"📊 レポートを保存: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="メソッド名不一致修正ツール")
    parser.add_argument("directory", help="スキャンするディレクトリ")
    parser.add_argument("--config", help="カスタム設定ファイル")
    parser.add_argument("--dry-run", action="store_true", help="実際の修正を行わず検索のみ")
    parser.add_argument("--report", help="レポート出力ファイル")
    parser.add_argument("--method", help="特定のメソッドのみ修正 (例: append_row)")

    args = parser.parse_args()

    if not os.path.exists(args.directory):
        logger.error(f"ディレクトリが存在しません: {args.directory}")
        return

    fixer = MethodNameFixer(args.config)

    if args.method:
        # 単一メソッドのみ修正
        if args.method in fixer.method_mappings:
            new_method = fixer.method_mappings[args.method]
            logger.info(f"🔧 単一メソッド修正: {args.method} → {new_method}")
            usages = fixer.find_method_usage(args.directory, args.method)

            if usages:
                logger.info(f"📍 発見: {len(usages)} 箇所")
                for file_path, line_num, line_content in usages:
                    if not args.dry_run:
                        fixer.fix_method_name(file_path, line_num, args.method, new_method)
            else:
                logger.info("✅ 問題なし")
        else:
            logger.error(f"未知のメソッド: {args.method}")
            logger.info(f"利用可能メソッド: {', '.join(fixer.method_mappings.keys())}")
    else:
        # 全メソッド修正
        results = fixer.scan_and_fix_all(args.directory, args.dry_run)
        results["directory"] = args.directory
        fixer.generate_report(results, args.report)


if __name__ == "__main__":
    main()
