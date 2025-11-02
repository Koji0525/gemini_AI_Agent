"""
汎用Pythonコード構造変更ツール（シンプル版）
- ASTで構文検証のみ
- 文字列操作はシンプルに（インデント破壊なし）
- 他のプロジェクトにも横展開可能

使い方:
    python3 tools/code_modifier/ast_based_modifier.py <ファイルパス>
"""

import ast
import re
import sys
from typing import List, Dict


class CodeStructureModifier:
    """Pythonコードの構造を安全に変更"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        with open(file_path, "r", encoding="utf-8") as f:
            self.content = f.read()

        # 構文チェック
        try:
            ast.parse(self.content)
            print(f"✅ 元ファイル構文OK: {file_path}")
        except SyntaxError as e:
            raise ValueError(f"❌ 元ファイルに構文エラー: {e}")

    def add_imports(self, imports: List[str]) -> "CodeStructureModifier":
        """インポート文を追加（重複チェック付き）"""
        lines = self.content.split("\n")

        # 既存のインポート終了位置を探す
        last_import_line = 0
        for i, line in enumerate(lines):
            if line.strip().startswith(("import ", "from ")):
                last_import_line = i

        # 重複チェックして追加
        added_count = 0
        for imp in imports:
            imp_stripped = imp.strip()
            # モジュール名を抽出して重複チェック
            module_name = imp_stripped.split("import")[-1].strip().split()[0]
            if module_name not in self.content:
                lines.insert(last_import_line + 1 + added_count, imp_stripped)
                added_count += 1
                print(f"✅ インポート追加: {module_name}")
            else:
                print(f"⏭️  既に存在: {module_name}")

        self.content = "\n".join(lines)
        return self

    def modify_class_init(
        self, class_name: str, new_params: Dict[str, str], initialization_code: str
    ) -> "CodeStructureModifier":
        """
        特定クラスの__init__を変更

        Args:
            class_name: 対象クラス名（例: "IntegratedOrchestrator"）
            new_params: 追加するパラメータ
                       {'decision_support': 'DecisionSupportSystem = None'}
            initialization_code: __init__内に追加するコード（インデントなし）
        """
        lines = self.content.split("\n")

        # ステップ1: クラス定義を探す
        class_line = -1
        for i, line in enumerate(lines):
            if re.match(rf"^class {class_name}[\(:]", line):
                class_line = i
                print(f"✅ クラス発見: {class_name} (行{i+1})")
                break

        if class_line == -1:
            print(f"⚠️ クラス {class_name} が見つかりません")
            return self

        # ステップ2: そのクラスの__init__を探す
        init_line = -1
        for i in range(class_line + 1, len(lines)):
            # 次のクラス定義が来たら終了
            if re.match(r"^class ", lines[i]):
                break
            if re.search(r"^\s+def __init__\(", lines[i]):
                init_line = i
                print(f"✅ __init__発見: (行{i+1})")
                break

        if init_line == -1:
            print(f"⚠️ {class_name}.__init__ が見つかりません")
            return self

        # ステップ3: 現在のインデントレベルを取得
        init_indent = len(lines[init_line]) - len(lines[init_line].lstrip())

        # ステップ4: __init__のシグネチャを変更
        current_sig = lines[init_line]

        # 既に修正済みかチェック
        if any(param in current_sig for param in new_params.keys()):
            print(f"⏭️  {class_name}.__init__ は既に修正済み")
        else:
            # シグネチャ変更
            if current_sig.rstrip().endswith("):"):
                # 単一行の場合: def __init__(self):
                param_lines = []
                for name, hint in new_params.items():
                    param_lines.append(f"{name}: {hint}")

                param_str = ",\n" + " " * (init_indent + 8)
                param_str += (",\n" + " " * (init_indent + 8)).join(param_lines)

                lines[init_line] = current_sig.replace("):", param_str + "):", 1)
                print(f"✅ {class_name}.__init__にパラメータ追加")
            else:
                print(f"⚠️ 複数行__init__は手動で修正してください")

        # ステップ5: 初期化コードを追加
        # __init__の最後を探す（次のメソッド定義またはクラス定義の直前）
        init_end = -1
        for i in range(init_line + 1, len(lines)):
            line_stripped = lines[i].lstrip()
            # メソッド定義またはクラス定義が来たら
            if line_stripped.startswith(("def ", "async def ", "class ", "@")):
                init_end = i
                break

        if init_end == -1:
            # ファイル末尾まで
            init_end = len(lines)

        # 初期化コードが既に存在するかチェック
        init_body = "\n".join(lines[init_line:init_end])

        # キーワードで既存チェック（例: self.decision_support）
        check_keyword = (
            initialization_code.split("\n")[1].strip().split("=")[0].strip()
            if "\n" in initialization_code
            else "Phase 1"
        )

        if check_keyword in init_body:
            print(f"⏭️  初期化コードは既に存在")
        else:
            # インデントを調整して挿入
            init_code_lines = initialization_code.strip().split("\n")
            indented_code = []
            for line in init_code_lines:
                if line.strip():  # 空行以外
                    indented_code.append(" " * (init_indent + 8) + line)
                else:
                    indented_code.append("")

            # 空行を追加してから挿入
            lines.insert(init_end, "")
            for line in reversed(indented_code):
                lines.insert(init_end, line)

            print(f"✅ {class_name}.__init__に初期化コード追加")

        self.content = "\n".join(lines)
        return self

    def validate_and_save(self, output_path: str = None) -> bool:
        """構文チェックして保存"""
        if output_path is None:
            output_path = self.file_path

        try:
            ast.parse(self.content)
            print("✅ 構文チェック成功")
        except SyntaxError as e:
            print(f"❌ 構文エラー: {e}")
            print(f"   行{e.lineno}: {e.text}")
            return False

        # バックアップ
        if output_path == self.file_path:
            backup_path = self.file_path + ".backup"
            with open(self.file_path, "r", encoding="utf-8") as f:
                with open(backup_path, "w", encoding="utf-8") as b:
                    b.write(f.read())
            print(f"✅ バックアップ: {backup_path}")

        # 保存
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self.content)
        print(f"✅ 保存完了: {output_path}")

        return True

    def preview_changes(self, line_start: int, line_end: int):
        """変更箇所をプレビュー"""
        lines = self.content.split("\n")
        print("\n【変更後のプレビュー】")
        for i in range(max(0, line_start - 1), min(len(lines), line_end + 1)):
            print(f"{i+1:4d}: {lines[i]}")


# ==================================================
# 使用例：IntegratedOrchestratorにPhase 1統合
# ==================================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python3 ast_based_modifier.py <ファイルパス>")
        sys.exit(1)

    file_path = sys.argv[1]
    print(f"\n📁 対象ファイル: {file_path}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    try:
        modifier = CodeStructureModifier(file_path)

        # 1. インポート追加
        print("\n【ステップ1】インポート追加")
        modifier.add_imports(
            [
                "from agents.self_healing.logging.decision_support_system import DecisionSupportSystem",
                "from agents.self_healing.logging.knowledge_base_manager import KnowledgeBaseManager",
                "from core_agents.human_interaction_agent_v02_github_api import HumanInteractionAgent",
            ]
        )

        # 2. IntegratedOrchestrator.__init__を変更
        print("\n【ステップ2】IntegratedOrchestrator.__init__変更")
        modifier.modify_class_init(
            class_name="IntegratedOrchestrator",
            new_params={
                "decision_support": "DecisionSupportSystem = None",
                "human_agent": "HumanInteractionAgent = None",
            },
            initialization_code="""
# Phase 1: 自己修復・人間介入機能
self.decision_support = decision_support
self.human_agent = human_agent
print("✅ Phase 1機能初期化完了")
""",
        )

        # 3. プレビュー（IntegratedOrchestratorの__init__付近）
        lines = modifier.content.split("\n")
        for i, line in enumerate(lines):
            if "class IntegratedOrchestrator" in line:
                modifier.preview_changes(i, i + 30)
                break

        # 4. 保存
        print("\n【ステップ3】保存")
        if modifier.validate_and_save():
            print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("✅ Phase 1統合完了")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        else:
            print("\n❌ 失敗")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
