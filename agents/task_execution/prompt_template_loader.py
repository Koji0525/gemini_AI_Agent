"""
プロンプトテンプレートローダー

プロンプトテンプレートを一元管理し、変数展開を行う。
これにより、プロンプトの保守性が向上する。

Version: 1.0
Created: 2024-11-26
"""

import re
from pathlib import Path
from typing import Any, Dict


class PromptTemplateLoader:
    """
        プロンプトテンプレート管理クラス

        機能:
        - テンプレートファイルの読み込み
        - 変数展開（{variable}形式）
        - キャッシュ機構
        - エラーハンドリング

        使用例:
    ```python
        loader = PromptTemplateLoader()
        template = loader.load_template('large_scale_implementation')
        prompt = loader.inject_variables(template, {'task_description': '...'})
    ```
    """

    def __init__(self, template_dir: str = "prompts/templates"):
        """
        初期化

        Args:
            template_dir: テンプレートディレクトリパス
        """
        self.template_dir = Path(template_dir)
        self.cache = {}  # テンプレートキャッシュ

        # ディレクトリ存在確認
        if not self.template_dir.exists():
            print(f"⚠️  テンプレートディレクトリが存在しません: {self.template_dir}")
            print(f"   作成します...")
            self.template_dir.mkdir(parents=True, exist_ok=True)

    def load_template(self, template_name: str) -> str:
        """
        テンプレート読み込み（キャッシュ付き）

        Args:
            template_name: テンプレート名（拡張子なし）

        Returns:
            テンプレート文字列

        Raises:
            FileNotFoundError: テンプレートファイルが見つからない
        """
        # キャッシュチェック
        if template_name in self.cache:
            print(f"✅ キャッシュからテンプレート取得: {template_name}")
            return self.cache[template_name]

        # ファイルパス構築
        template_path = self.template_dir / f"{template_name}.txt"

        if not template_path.exists():
            raise FileNotFoundError(
                f"テンプレートファイル未発見: {template_path}\n"
                f"利用可能なテンプレート: {self.list_templates()}"
            )

        # ファイル読み込み
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template = f.read()

            # キャッシュに保存
            self.cache[template_name] = template

            print(f"✅ テンプレート読み込み成功: {template_name} ({len(template)}文字)")

            return template

        except Exception as e:
            raise IOError(f"テンプレート読み込みエラー: {template_path}\n{e}")

    def inject_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """
        変数展開

        テンプレート内の {variable_name} を実際の値に置換。

        Args:
            template: テンプレート文字列
            variables: 変数辞書

        Returns:
            変数展開後の文字列

        Example:
            template = "Hello {name}, you are {age} years old"
            variables = {'name': 'Alice', 'age': 30}
            result = "Hello Alice, you are 30 years old"
        """
        result = template

        # 全ての変数を置換
        for key, value in variables.items():
            placeholder = f"{{{key}}}"

            # 値を文字列に変換
            str_value = str(value) if value is not None else ""

            # 置換
            result = result.replace(placeholder, str_value)

        # 未置換の変数をチェック（警告）
        unresolved = re.findall(r"\{(\w+)\}", result)
        if unresolved:
            print(f"⚠️  未解決の変数: {unresolved}")

        return result

    def list_templates(self) -> list:
        """
        利用可能なテンプレート一覧を取得

        Returns:
            テンプレート名のリスト
        """
        if not self.template_dir.exists():
            return []

        templates = []
        for file_path in self.template_dir.glob("*.txt"):
            templates.append(file_path.stem)

        return templates

    def clear_cache(self):
        """キャッシュをクリア"""
        self.cache.clear()
        print("✅ テンプレートキャッシュをクリアしました")

    def get_cache_info(self) -> Dict[str, int]:
        """
        キャッシュ情報を取得

        Returns:
            キャッシュ統計
        """
        return {
            "cached_templates": len(self.cache),
            "total_size": sum(len(t) for t in self.cache.values()),
            "template_names": list(self.cache.keys()),
        }


# テスト用コード
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PromptTemplateLoader テスト")
    print("=" * 60 + "\n")

    # 初期化
    loader = PromptTemplateLoader()

    # 利用可能なテンプレート表示
    templates = loader.list_templates()
    print(f"利用可能なテンプレート: {len(templates)}個")
    for t in templates:
        print(f"  - {t}")
    print()

    # テンプレート作成（テスト用）
    test_template_path = Path("prompts/templates/test_template.txt")
    test_template_path.parent.mkdir(parents=True, exist_ok=True)

    with open(test_template_path, "w", encoding="utf-8") as f:
        f.write(
            """
# Test Template

Hello {name}!

Your task is: {task_description}

Requirements:
- Minimum lines: {min_lines}
- Minimum files: {min_files}
"""
        )

    print("✅ テストテンプレート作成完了\n")

    # テンプレート読み込みテスト
    try:
        template = loader.load_template("test_template")
        print(f"✅ テンプレート読み込み成功\n")

        # 変数展開テスト
        variables = {
            "name": "Developer",
            "task_description": "Implement database connection module",
            "min_lines": 1000,
            "min_files": 3,
        }

        result = loader.inject_variables(template, variables)

        print("変数展開結果:")
        print("-" * 60)
        print(result)
        print("-" * 60)
        print()

        # キャッシュ情報
        cache_info = loader.get_cache_info()
        print(f"キャッシュ情報: {cache_info}")

    except Exception as e:
        print(f"❌ エラー: {e}")
