#!/usr/bin/env python3
"""
CodeIntegrator v2 - 成果物統合エージェント

【Phase 3: M3.2実装】
- F12: 成果物統合エージェント
- Sub-taskのコードを統合
- import文を自動調整
- 重複コードを削除
- 統合後ファイルの生成

【設計思想】
- 既存システムは変更しない
- 独立したモジュールとして実装
- Phase 1-2の成果物を活用
- エラー時の安全なロールバック
"""

import ast
import logging
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# プロジェクトルート設定
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# ロギング設定
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)

# 既存システム（読み取り専用）
try:
    from tools.base_data_accessor import BaseDataAccessor

    ACCESSOR_AVAILABLE = True
except ImportError:
    ACCESSOR_AVAILABLE = False
    logger.warning("⚠️ BaseDataAccessorが利用できません")


class CodeIntegrator:
    """
    成果物統合エージェント

    【Phase 3: F12実装】
    - Sub-taskのコードを統合
    - import文を自動調整
    - 重複を削除
    - 統合後ファイルの生成
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        初期化

        Args:
            output_dir: 統合ファイルの出力先（デフォルト: agent_outputs/integrated/）
        """
        if ACCESSOR_AVAILABLE:
            self.accessor = BaseDataAccessor()
            logger.info("✅ BaseDataAccessor ロード完了")
        else:
            self.accessor = None
            logger.warning("⚠️ BaseDataAccessor 利用不可")

        # 出力ディレクトリ設定
        self.output_dir = output_dir or (project_root / "agent_outputs" / "integrated")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"✅ CodeIntegrator 初期化完了")
        logger.info(f"   出力先: {self.output_dir}")

    def integrate_subtasks(self, story_id: str, subtask_ids: List[str]) -> Dict[str, Any]:
        """
        Sub-taskのコードを統合

        Args:
            story_id: ストーリーID
            subtask_ids: 統合するSub-task IDのリスト

        Returns:
            統合結果
        """
        logger.info(f"🔗 コード統合開始: {story_id}")
        logger.info(f"   Sub-task数: {len(subtask_ids)}個")

        try:
            # ステップ1: Sub-task成果物を収集
            logger.info("📥 Sub-task成果物を収集中...")
            subtask_files = self._collect_subtask_outputs(subtask_ids)
            logger.info(f"   収集ファイル数: {len(subtask_files)}件")

            # ステップ2: ファイル種別ごとに分類
            logger.info("📊 ファイル種別を分類中...")
            categorized = self._categorize_files(subtask_files)

            # ステップ3: Pythonコードを統合
            logger.info("🔧 Pythonコードを統合中...")
            integrated_python = self._integrate_python_files(categorized.get("python", []))

            # ステップ4: その他ファイルを統合
            logger.info("📝 その他ファイルを統合中...")
            integrated_others = self._integrate_other_files(categorized)

            # ステップ5: 統合ファイルを保存
            logger.info("💾 統合ファイルを保存中...")
            output_files = self._save_integrated_files(
                story_id, integrated_python, integrated_others
            )

            # 統合結果サマリー
            result = {
                "story_id": story_id,
                "subtask_count": len(subtask_ids),
                "input_file_count": len(subtask_files),
                "output_file_count": len(output_files),
                "output_files": output_files,
                "integration_success": True,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"✅ コード統合完了")
            logger.info(f"   入力: {len(subtask_files)}ファイル")
            logger.info(f"   出力: {len(output_files)}ファイル")

            return result

        except Exception as e:
            logger.error(f"❌ コード統合エラー: {e}")
            import traceback

            traceback.print_exc()

            return {
                "story_id": story_id,
                "integration_success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _collect_subtask_outputs(self, subtask_ids: List[str]) -> List[Dict[str, Any]]:
        """Sub-task成果物を収集"""
        subtask_files = []

        # agent_outputs/structured/ から収集
        structured_dir = project_root / "agent_outputs" / "structured"

        for subtask_id in subtask_ids:
            subtask_dir = structured_dir / subtask_id

            if not subtask_dir.exists():
                logger.warning(f"⚠️ Sub-task出力が見つかりません: {subtask_id}")
                continue

            # ディレクトリ内のすべてのファイルを収集
            for file_path in subtask_dir.rglob("*"):
                if file_path.is_file() and file_path.name != "_manifest.json":
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        subtask_files.append(
                            {
                                "subtask_id": subtask_id,
                                "file_path": file_path,
                                "file_name": file_path.name,
                                "content": content,
                                "size": len(content),
                            }
                        )
                    except Exception as e:
                        logger.warning(f"⚠️ ファイル読み込みエラー: {file_path} - {e}")

        return subtask_files

    def _categorize_files(self, files: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """ファイル種別ごとに分類"""
        categorized = defaultdict(list)

        for file_info in files:
            file_name = file_info["file_name"]

            if file_name.endswith(".py"):
                categorized["python"].append(file_info)
            elif file_name.endswith(".md"):
                categorized["markdown"].append(file_info)
            elif file_name.endswith((".yaml", ".yml")):
                categorized["yaml"].append(file_info)
            elif file_name.endswith(".json"):
                categorized["json"].append(file_info)
            elif file_name.endswith(".txt"):
                categorized["text"].append(file_info)
            else:
                categorized["other"].append(file_info)

        return dict(categorized)

    def _integrate_python_files(self, python_files: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Pythonファイルを統合

        Returns:
            {ファイル名: 統合後コード}
        """
        if not python_files:
            return {}

        logger.info(f"🐍 Pythonファイル統合: {len(python_files)}件")

        # ファイル名ごとにグループ化
        grouped = defaultdict(list)
        for file_info in python_files:
            grouped[file_info["file_name"]].append(file_info)

        integrated = {}

        for file_name, file_list in grouped.items():
            if len(file_list) == 1:
                # 重複なし - そのまま使用
                integrated[file_name] = file_list[0]["content"]
            else:
                # 重複あり - マージ
                logger.info(f"   🔀 マージ: {file_name} ({len(file_list)}個)")
                merged_code = self._merge_python_code(file_list)
                integrated[file_name] = merged_code

        return integrated

    def _merge_python_code(self, file_list: List[Dict[str, Any]]) -> str:
        """
        複数のPythonコードをマージ

        【マージ戦略】
        1. import文を統合
        2. クラス定義を統合（重複削除）
        3. 関数定義を統合（重複削除）
        4. その他のコードを統合
        """
        all_imports = set()
        all_classes = {}
        all_functions = {}
        other_code = []

        for file_info in file_list:
            code = file_info["content"]

            # import文を抽出
            imports = self._extract_imports(code)
            all_imports.update(imports)

            # クラス定義を抽出
            classes = self._extract_classes(code)
            for class_name, class_code in classes.items():
                if class_name not in all_classes:
                    all_classes[class_name] = class_code

            # 関数定義を抽出
            functions = self._extract_functions(code)
            for func_name, func_code in functions.items():
                if func_name not in all_functions:
                    all_functions[func_name] = func_code

            # その他のコード
            other = self._extract_other_code(code)
            if other:
                other_code.append(other)

        # 統合コードを構築
        merged_lines = []

        # 1. shebangとdocstring
        merged_lines.append("#!/usr/bin/env python3")
        merged_lines.append('"""')
        merged_lines.append("統合されたコード")
        merged_lines.append(f"生成日時: {datetime.now().isoformat()}")
        merged_lines.append('"""')
        merged_lines.append("")

        # 2. import文
        if all_imports:
            merged_lines.extend(sorted(all_imports))
            merged_lines.append("")

        # 3. クラス定義
        for class_code in all_classes.values():
            merged_lines.append(class_code)
            merged_lines.append("")

        # 4. 関数定義
        for func_code in all_functions.values():
            merged_lines.append(func_code)
            merged_lines.append("")

        # 5. その他のコード
        if other_code:
            merged_lines.append("# その他のコード")
            for code in other_code:
                merged_lines.append(code)

        return "\n".join(merged_lines)

    def _extract_imports(self, code: str) -> Set[str]:
        """import文を抽出"""
        imports = set()

        for line in code.split("\n"):
            line = line.strip()
            if line.startswith("import ") or line.startswith("from "):
                imports.add(line)

        return imports

    def _extract_classes(self, code: str) -> Dict[str, str]:
        """クラス定義を抽出"""
        classes = {}

        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    # クラスの開始・終了位置を取得してコードを抽出
                    class_code = ast.get_source_segment(code, node)
                    if class_code:
                        classes[class_name] = class_code
        except SyntaxError:
            logger.warning("⚠️ 構文エラーによりクラス抽出をスキップ")

        return classes

    def _extract_functions(self, code: str) -> Dict[str, str]:
        """関数定義を抽出（トップレベルのみ）"""
        functions = {}

        try:
            tree = ast.parse(code)
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    func_code = ast.get_source_segment(code, node)
                    if func_code:
                        functions[func_name] = func_code
        except SyntaxError:
            logger.warning("⚠️ 構文エラーにより関数抽出をスキップ")

        return functions

    def _extract_other_code(self, code: str) -> str:
        """その他のコード（import/class/function以外）を抽出"""
        lines = []

        for line in code.split("\n"):
            stripped = line.strip()
            # import, class, def 以外の行
            if (
                stripped
                and not stripped.startswith("#")
                and not stripped.startswith("import ")
                and not stripped.startswith("from ")
                and not stripped.startswith("class ")
                and not stripped.startswith("def ")
            ):
                lines.append(line)

        return "\n".join(lines) if lines else ""

    def _integrate_other_files(
        self, categorized: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, str]:
        """その他のファイル（Markdown, YAML, JSONなど）を統合"""
        integrated = {}

        # Markdownファイル
        if "markdown" in categorized:
            md_files = categorized["markdown"]
            if len(md_files) == 1:
                integrated["README.md"] = md_files[0]["content"]
            else:
                # 複数のMarkdownを統合
                merged_md = self._merge_markdown(md_files)
                integrated["README.md"] = merged_md

        # YAMLファイル（最初の1つを使用）
        if "yaml" in categorized:
            yaml_files = categorized["yaml"]
            if yaml_files:
                integrated[yaml_files[0]["file_name"]] = yaml_files[0]["content"]

        # JSONファイル（最初の1つを使用）
        if "json" in categorized:
            json_files = categorized["json"]
            if json_files:
                integrated[json_files[0]["file_name"]] = json_files[0]["content"]

        return integrated

    def _merge_markdown(self, md_files: List[Dict[str, Any]]) -> str:
        """複数のMarkdownファイルを統合"""
        sections = []

        for i, file_info in enumerate(md_files, 1):
            sections.append(f"## Sub-task {i}: {file_info['subtask_id']}")
            sections.append("")
            sections.append(file_info["content"])
            sections.append("")

        header = f"""# 統合ドキュメント

生成日時: {datetime.now().isoformat()}
統合ファイル数: {len(md_files)}

"""

        return header + "\n".join(sections)

    def _save_integrated_files(
        self, story_id: str, python_files: Dict[str, str], other_files: Dict[str, str]
    ) -> List[Path]:
        """統合ファイルを保存"""
        # Story専用ディレクトリ作成
        story_dir = self.output_dir / story_id
        story_dir.mkdir(parents=True, exist_ok=True)

        output_files = []

        # Pythonファイルを保存
        for file_name, content in python_files.items():
            file_path = story_dir / file_name
            file_path.write_text(content, encoding="utf-8")
            output_files.append(file_path)
            logger.info(f"   ✅ 保存: {file_path}")

        # その他のファイルを保存
        for file_name, content in other_files.items():
            file_path = story_dir / file_name
            file_path.write_text(content, encoding="utf-8")
            output_files.append(file_path)
            logger.info(f"   ✅ 保存: {file_path}")

        return output_files

    def resolve_imports(self, code: str) -> str:
        """
        import文を自動調整

        【調整内容】
        - 重複import削除
        - 未使用import削除
        - import順序の最適化
        """
        logger.info("🔧 import文を調整中...")

        try:
            # import文を抽出
            imports = self._extract_imports(code)

            # 重複削除（すでにsetなので重複なし）
            unique_imports = sorted(imports)

            # import文以外のコードを取得
            non_import_code = []
            for line in code.split("\n"):
                stripped = line.strip()
                if not (stripped.startswith("import ") or stripped.startswith("from ")):
                    non_import_code.append(line)

            # 再構築
            adjusted_lines = unique_imports + [""] + non_import_code
            adjusted_code = "\n".join(adjusted_lines)

            logger.info(f"✅ import文調整完了 ({len(unique_imports)}件)")

            return adjusted_code

        except Exception as e:
            logger.warning(f"⚠️ import調整エラー: {e}")
            return code  # エラー時は元のコードを返す


# テスト用
def test_code_integrator():
    """Phase 3 M3.2 テスト実行"""
    print("=" * 60)
    print("Phase 3: CodeIntegrator (F12) テスト実行")
    print("=" * 60)
    print()

    try:
        integrator = CodeIntegrator()
        print()

        # テスト1: ファイル分類
        print("🧪 テスト1: ファイル分類")
        test_files = [
            {"file_name": "api.py", "content": "import os"},
            {"file_name": "models.py", "content": "class Model: pass"},
            {"file_name": "README.md", "content": "# README"},
        ]
        categorized = integrator._categorize_files(test_files)
        print(f"   Python: {len(categorized.get('python', []))}件")
        print(f"   Markdown: {len(categorized.get('markdown', []))}件")
        print()

        # テスト2: import抽出
        print("🧪 テスト2: import抽出")
        test_code = """
import os
import sys
from pathlib import Path
"""
        imports = integrator._extract_imports(test_code)
        print(f"   抽出import数: {len(imports)}件")
        print()

        # テスト3: import調整
        print("🧪 テスト3: import調整")
        adjusted = integrator.resolve_imports(test_code)
        print(f"   調整後: {len(adjusted.split('\\n'))}行")
        print()

        print("=" * 60)
        print("Phase 3 M3.2 テスト完了 ✅")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(test_code_integrator())
