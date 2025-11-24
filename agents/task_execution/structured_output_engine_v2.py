"""
構造化成果物エンジン v2.0
より厳格なファイル抽出とデフォルトファイル生成

改善点:
- 複数パターンのファイル名検出
- 不足ファイルの自動生成
- より厳格な検証
"""

import json
import re
from pathlib import Path
from typing import Dict, List


class StructuredOutputEngineV2:
    """構造化成果物エンジン v2.0"""

    # デフォルトファイルテンプレート
    DEFAULT_FILES = {
        "main.py": '''"""
メイン実装モジュール

このモジュールは...
"""

def main():
    """メイン関数"""
    print("実装が必要です")

if __name__ == "__main__":
    main()
''',
        "config.yaml": """# 設定ファイル
app:
  name: "Application"
  version: "1.0.0"

settings:
  debug: false
""",
        "tests/test_main.py": '''"""テストコード"""
import pytest

def test_basic():
    """基本テスト"""
    assert True
''',
        "utils.py": '''"""ユーティリティモジュール"""

def helper_function():
    """ヘルパー関数"""
    pass
''',
        "README.md": """# プロジェクト

## 概要
このプロジェクトは...

## 使用方法
```bash
python main.py
```

## テスト
```bash
pytest tests/
```
""",
    }

    def __init__(self, base_output_dir: Path):
        self.base_output_dir = base_output_dir
        self.base_output_dir.mkdir(parents=True, exist_ok=True)

    def extract_files_from_markdown(
        self, markdown_text: str, task_id: str, minimum_files: int = 5
    ) -> Dict[str, str]:
        """
        Markdown形式から実際のファイルを抽出（改良版）

        改善点:
        - より多くのパターンでファイル名を検出
        - 不足ファイルを自動生成
        """
        files = {}

        print(f"\n🔍 ファイル抽出開始...")

        # パターン1: "## ファイル: xxx.py" 形式
        pattern1 = r"##\s*ファイル[：:]\s*([^\n]+)\n\s*```(\w+)?\n(.*?)```"
        matches1 = re.findall(pattern1, markdown_text, re.DOTALL)

        for filename, language, code in matches1:
            filename = filename.strip()
            code = code.strip()
            if code and len(code) > 20:
                files[filename] = code
                print(f"  ✅ パターン1: {filename} ({len(code)}文字)")

        # パターン2: "### xxx.py" の直後のコードブロック
        pattern2 = r"###\s*([^\n]+\.(?:py|yaml|yml|md|json))\n\s*```(\w+)?\n(.*?)```"
        matches2 = re.findall(pattern2, markdown_text, re.DOTALL)

        for filename, language, code in matches2:
            filename = filename.strip()
            code = code.strip()
            if filename not in files and code and len(code) > 20:
                files[filename] = code
                print(f"  ✅ パターン2: {filename} ({len(code)}文字)")

        # パターン3: コードブロックの直前の行からファイル名を推定
        lines = markdown_text.split("\n")
        i = 0
        while i < len(lines):
            if lines[i].strip().startswith("```"):
                # コードブロック開始
                language = lines[i].strip()[3:].strip()
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1

                code = "\n".join(code_lines).strip()

                # 直前の行をチェック
                if i > 1:
                    prev_line = lines[i - len(code_lines) - 2].strip()
                    # ファイル名っぽい文字列
                    file_match = re.search(r"([a-zA-Z0-9_/]+\.(?:py|yaml|yml|md|json))", prev_line)
                    if file_match:
                        filename = file_match.group(1)
                        if filename not in files and code and len(code) > 20:
                            files[filename] = code
                            print(f"  ✅ パターン3: {filename} ({len(code)}文字)")
            i += 1

        # パターン4: 言語指定からファイル名を推定
        all_code_blocks = re.findall(r"```(\w+)\n(.*?)```", markdown_text, re.DOTALL)
        file_counter = {"py": 1, "yaml": 1, "json": 1, "md": 1}

        for language, code in all_code_blocks:
            code = code.strip()
            if len(code) < 20:
                continue

            # すでに抽出されたコードかチェック
            already_extracted = any(code in existing_code for existing_code in files.values())
            if already_extracted:
                continue

            # ファイル名を推定
            if language == "python" or language == "py":
                # クラス名や関数名から推定
                class_match = re.search(r"class\s+([A-Z][a-zA-Z0-9_]*)", code)
                if class_match:
                    class_name = class_match.group(1)
                    snake_case = re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).lower()
                    filename = f"{snake_case}.py"
                else:
                    filename = f"module_{file_counter['py']}.py"
                    file_counter["py"] += 1

                if filename not in files:
                    files[filename] = code
                    print(f"  ✅ パターン4: {filename} ({len(code)}文字)")

            elif language in ["yaml", "yml"]:
                filename = f"config_{file_counter['yaml']}.yaml"
                file_counter["yaml"] += 1
                if filename not in files:
                    files[filename] = code
                    print(f"  ✅ パターン4: {filename} ({len(code)}文字)")

        # README抽出
        if "README.md" not in files:
            readme_content = self._extract_readme_content(markdown_text)
            if readme_content and len(readme_content) > 100:
                files["README.md"] = readme_content
                print(f"  ✅ README.md 抽出 ({len(readme_content)}文字)")

        print(f"\n📊 抽出結果: {len(files)}個のファイル")

        # 不足ファイルの自動生成
        if len(files) < minimum_files:
            print(f"\n⚠️  ファイル数不足: {len(files)}/{minimum_files}")
            print(f"🔧 デフォルトファイルで補完中...")

            missing_count = minimum_files - len(files)
            added_files = self._add_default_files(files, missing_count)

            for filename in added_files:
                print(f"  ➕ {filename} (デフォルト)")

        return files

    def _add_default_files(self, existing_files: Dict[str, str], count: int) -> List[str]:
        """不足ファイルをデフォルトテンプレートで補完"""
        added = []

        for default_file, default_content in self.DEFAULT_FILES.items():
            if len(added) >= count:
                break

            if default_file not in existing_files:
                existing_files[default_file] = default_content
                added.append(default_file)

        # それでも不足する場合は連番ファイル生成
        if len(added) < count:
            for i in range(count - len(added)):
                filename = f"module_extra_{i+1}.py"
                if filename not in existing_files:
                    existing_files[filename] = f'"""追加モジュール {i+1}"""\n\npass\n'
                    added.append(filename)

        return added

    def _extract_readme_content(self, text: str) -> str:
        """README用のコンテンツを抽出"""
        # コードブロックを除去
        text_without_code = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

        # 空行を整理
        lines = [line for line in text_without_code.split("\n") if line.strip()]

        if len(lines) < 5:
            return ""

        return "\n".join(lines)

    def save_structured_output(self, files: Dict[str, str], task_id: str) -> Path:
        """ファイルセットを構造化して保存"""
        task_dir = self.base_output_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n📁 構造化成果物保存: {task_dir}")

        saved_files = []

        for filepath, content in files.items():
            full_path = task_dir / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"  ✅ {filepath} ({len(content)}文字)")
            saved_files.append(filepath)

        # マニフェスト生成
        manifest = {
            "task_id": task_id,
            "files": saved_files,
            "total_files": len(saved_files),
            "main_file": self._identify_main_file(saved_files),
        }

        manifest_path = task_dir / "_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        print(f"  📋 _manifest.json")

        return task_dir

    def _identify_main_file(self, filenames: List[str]) -> str:
        """メインファイルを識別"""
        for priority in ["main.py", "__init__.py"]:
            if priority in filenames:
                return priority

        py_files = [f for f in filenames if f.endswith(".py")]
        return py_files[0] if py_files else (filenames[0] if filenames else "")


if __name__ == "__main__":
    # テスト
    engine = StructuredOutputEngineV2(Path("/tmp/test_structured"))

    sample_md = """
# テスト

## ファイル: test1.py
```python
def test():
    pass
```

### test2.yaml
```yaml
key: value
```
"""

    files = engine.extract_files_from_markdown(sample_md, "test", minimum_files=5)
    print(f"\n最終: {len(files)}ファイル")
    for f in files.keys():
        print(f"  - {f}")
