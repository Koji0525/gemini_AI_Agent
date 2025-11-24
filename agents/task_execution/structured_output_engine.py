"""
構造化成果物エンジン v1.0
実行可能な成果物セットを生成

目標:
- 実際に動作するファイル群を生成
- ディレクトリ構造を持つ
- そのまま使える実装
- 複数タスクで統合可能
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple


class StructuredOutputEngine:
    """
    構造化成果物エンジン

    Geminiの出力（Markdown形式）から、
    実際のファイルセットを抽出・構造化する。
    """

    def __init__(self, base_output_dir: Path):
        """
        Args:
            base_output_dir: 成果物の基底ディレクトリ
        """
        self.base_output_dir = base_output_dir
        self.base_output_dir.mkdir(parents=True, exist_ok=True)

    def extract_files_from_markdown(self, markdown_text: str, task_id: str) -> Dict[str, str]:
        """
        Markdown形式のテキストから実際のファイルを抽出

        Args:
            markdown_text: Geminiが生成したMarkdownテキスト
            task_id: タスクID（ディレクトリ名に使用）

        Returns:
            {ファイルパス: ファイル内容} の辞書
        """
        files = {}

        # コードブロックを抽出（```python ... ``` の形式）
        code_blocks = self._extract_code_blocks(markdown_text)

        # ファイル名のヒントを探す
        file_hints = self._extract_file_hints(markdown_text)

        # コードブロックとファイル名を対応付け
        for i, (language, code) in enumerate(code_blocks):
            if language in ["python", "py"]:
                # ファイル名の推定
                if i < len(file_hints):
                    filename = file_hints[i]
                else:
                    # クラス名・関数名から推定
                    filename = self._infer_filename_from_code(code, i)

                files[filename] = code

            elif language in ["yaml", "yml"]:
                filename = file_hints[i] if i < len(file_hints) else f"config_{i}.yaml"
                files[filename] = code

            elif language == "json":
                filename = file_hints[i] if i < len(file_hints) else f"data_{i}.json"
                files[filename] = code

        # README生成（Markdownの説明部分から）
        readme_content = self._extract_readme_content(markdown_text)
        if readme_content:
            files["README.md"] = readme_content

        return files

    def _extract_code_blocks(self, text: str) -> List[Tuple[str, str]]:
        """
        Markdownからコードブロックを抽出

        Returns:
            [(言語, コード), ...] のリスト
        """
        pattern = r"```(\w+)?\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)

        code_blocks = []
        for language, code in matches:
            language = language.lower() if language else "text"
            code = code.strip()
            if code and len(code) > 50:  # 50文字以上のコードのみ
                code_blocks.append((language, code))

        return code_blocks

    def _extract_file_hints(self, text: str) -> List[str]:
        """
        ファイル名のヒントを抽出

        例: 「以下のファイルを作成: ml_pipeline.py」
        """
        hints = []

        # パターン1: "ファイル: xxx.py"
        pattern1 = r"ファイル[：:]\s*([a-zA-Z0-9_/\.]+\.(py|yaml|yml|json|md))"
        matches1 = re.findall(pattern1, text)
        hints.extend([m[0] for m in matches1])

        # パターン2: "xxx.py を作成"
        pattern2 = r"([a-zA-Z0-9_/\.]+\.(py|yaml|yml|json|md))\s*[をに]"
        matches2 = re.findall(pattern2, text)
        hints.extend([m[0] for m in matches2])

        # パターン3: コードブロックの直前の行
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if line.strip().startswith("```"):
                # 直前の行をチェック
                if i > 0:
                    prev_line = lines[i - 1].strip()
                    # ファイル名っぽい文字列を抽出
                    file_match = re.search(r"([a-zA-Z0-9_/]+\.(py|yaml|yml|json|md))", prev_line)
                    if file_match:
                        hints.append(file_match.group(1))

        return hints

    def _infer_filename_from_code(self, code: str, index: int) -> str:
        """
        コード内容からファイル名を推定

        Args:
            code: コード内容
            index: コードブロックのインデックス

        Returns:
            推定ファイル名
        """
        # クラス名を探す
        class_match = re.search(r"class\s+([A-Z][a-zA-Z0-9_]*)", code)
        if class_match:
            class_name = class_match.group(1)
            # CamelCase → snake_case
            snake_case = re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).lower()
            return f"{snake_case}.py"

        # 関数名を探す
        func_match = re.search(r"def\s+([a-z_][a-zA-Z0-9_]*)", code)
        if func_match:
            func_name = func_match.group(1)
            return f"{func_name}.py"

        # デフォルト
        return f"module_{index + 1}.py"

    def _extract_readme_content(self, text: str) -> str:
        """
        README用のコンテンツを抽出

        コードブロック以外の説明部分を集める
        """
        # コードブロックを除去
        text_without_code = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

        # 空行を整理
        lines = [line for line in text_without_code.split("\n") if line.strip()]

        if len(lines) < 10:  # 説明が少なすぎる場合はスキップ
            return ""

        return "\n".join(lines)

    def save_structured_output(self, files: Dict[str, str], task_id: str) -> Path:
        """
        ファイルセットを構造化して保存

        Args:
            files: {ファイルパス: 内容} の辞書
            task_id: タスクID

        Returns:
            保存先ディレクトリのパス
        """
        # タスク専用ディレクトリ作成
        task_dir = self.base_output_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n�� 構造化成果物保存: {task_dir}")

        saved_files = []

        for filepath, content in files.items():
            # サブディレクトリ対応
            full_path = task_dir / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # ファイル保存
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"  ✅ {filepath} ({len(content)}文字)")
            saved_files.append(filepath)

        # マニフェストファイル生成（どのファイルがあるかの記録）
        manifest = {
            "task_id": task_id,
            "files": saved_files,
            "total_files": len(saved_files),
            "main_file": self._identify_main_file(saved_files),
        }

        manifest_path = task_dir / "_manifest.json"
        import json

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        print(f"  📋 _manifest.json (メタ情報)")

        return task_dir

    def _identify_main_file(self, filenames: List[str]) -> str:
        """
        メインファイルを識別

        Args:
            filenames: ファイル名のリスト

        Returns:
            メインファイルと思われるファイル名
        """
        # 優先順位: main.py > __init__.py > 最初の.pyファイル
        for priority in ["main.py", "__init__.py"]:
            if priority in filenames:
                return priority

        # .pyファイルの最初
        py_files = [f for f in filenames if f.endswith(".py")]
        if py_files:
            return py_files[0]

        # それ以外は最初のファイル
        return filenames[0] if filenames else ""


if __name__ == "__main__":
    # テスト
    engine = StructuredOutputEngine(Path("/workspaces/gemini_AI_Agent/agent_outputs/structured"))

    # サンプルMarkdown
    sample_md = """
# 機械学習パイプライン実装

以下のファイルを作成します。

## ml_pipeline.py

\`\`\`python
\"\"\"機械学習パイプライン\"\"\"
import pandas as pd
from sklearn.model_selection import train_test_split

class MLPipeline:
    def __init__(self, model):
        self.model = model
    
    def train(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y)
        self.model.fit(X_train, y_train)
        return self.model.score(X_test, y_test)
\`\`\`

## config.yaml

\`\`\`yaml
model:
  type: RandomForest
  n_estimators: 100
\`\`\`

使用方法は README.md を参照してください。
"""

    files = engine.extract_files_from_markdown(sample_md, "test_task")
    output_dir = engine.save_structured_output(files, "test_task")

    print(f"\n✅ テスト完了: {output_dir}")
