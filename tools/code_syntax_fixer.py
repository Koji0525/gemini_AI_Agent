#!/usr/bin/env python3
"""
拡張性のあるコード構文修正ツール
既存システムの連携を壊さずに安全に修正します
"""

import ast
import re
import sys
from pathlib import Path


class CodeSyntaxFixer:
    """コード構文修正ツール"""

    def __init__(self, project_root: str = "/workspaces/gemini_AI_Agent"):
        self.project_root = Path(project_root)
        self.fix_patterns = {
            "japanese_punctuation": {
                "pattern": r"[。、]",
                "description": "日本語句読点の除去",
                "fix_method": self._fix_japanese_punctuation,
            },
            "indentation": {
                "pattern": r"^(\s+)",
                "description": "インデントの修正",
                "fix_method": self._fix_indentation,
            },
            "encoding": {
                "pattern": r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]",
                "description": "不正なエンコード文字の除去",
                "fix_method": self._fix_encoding,
            },
        }

    def _fix_japanese_punctuation(self, line: str, line_num: int) -> str:
        """日本語句読点を安全に修正"""
        stripped = line.strip()

        # コード行の場合のみ修正
        if stripped and not (
            stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''")
        ):
            if "。" in line or "、" in line:
                print(f"🔧 行{line_num}: 日本語句読点をコメント化")
                return "# " + line

        return line

    def _fix_indentation(self, line: str, line_num: int) -> str:
        """インデントを修正"""
        # 基本的なインデントチェック（必要に応じて拡張）
        return line

    def _fix_encoding(self, line: str, line_num: int) -> str:
        """エンコード問題を修正"""
        # 制御文字などを除去
        cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]", "", line)
        if cleaned != line:
            print(f"🔧 行{line_num}: 不正なエンコード文字を除去")
        return cleaned

    def safe_fix_file(self, file_path: str, backup: bool = True) -> bool:
        """ファイルを安全に修正"""
        file_path = self.project_root / file_path

        if not file_path.exists():
            print(f"❌ ファイルが見つかりません: {file_path}")
            return False

        # バックアップ作成
        if backup:
            backup_path = file_path.with_suffix(f".backup.{Path(file_path).stem}")
            import shutil

            shutil.copy2(file_path, backup_path)
            print(f"📦 バックアップ作成: {backup_path}")

        # ファイル読み込み
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            print(f"❌ ファイルの読み込みに失敗: {file_path}")
            return False

        # 行ごとに処理
        lines = content.split("\n")
        fixed_lines = []
        changes_made = False

        for i, line in enumerate(lines, 1):
            fixed_line = line

            # 各修正パターンを適用
            for pattern_name, pattern_info in self.fix_patterns.items():
                original_line = fixed_line
                fixed_line = pattern_info["fix_method"](fixed_line, i)
                if fixed_line != original_line:
                    changes_made = True
                    print(f"   📝 {pattern_info['description']}を適用")

            fixed_lines.append(fixed_line)

        # 変更があった場合のみ書き込み
        if changes_made:
            fixed_content = "\n".join(fixed_lines)

            # 構文チェック
            try:
                ast.parse(fixed_content)
                print("✅ 構文チェック成功")
            except SyntaxError as e:
                print(f"❌ 修正後も構文エラー: {e}")
                return False

            # ファイル書き込み
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_content)

            print(f"✅ 修正完了: {file_path}")
            return True
        else:
            print(f"ℹ️ 修正必要なし: {file_path}")
            return True

    def add_fix_pattern(self, name: str, pattern: str, description: str, fix_method):
        """修正パターンを追加（拡張性）"""
        self.fix_patterns[name] = {
            "pattern": pattern,
            "description": description,
            "fix_method": fix_method,
        }
        print(f"✅ 修正パターン追加: {name} - {description}")


def main():
    """メイン実行関数"""
    if len(sys.argv) < 2:
        print("使用方法: python3 tools/code_syntax_fixer.py <ファイルパス>")
        sys.exit(1)

    file_path = sys.argv[1]
    fixer = CodeSyntaxFixer()

    print(f"�� コード構文修正を開始: {file_path}")
    success = fixer.safe_fix_file(file_path)

    if success:
        print("🎯 修正完了")
    else:
        print("❌ 修正失敗")
        sys.exit(1)


if __name__ == "__main__":
    main()
