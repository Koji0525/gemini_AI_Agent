"""
汎用Pythonコード構造変更ツール v2
- ネストされた関数定義を正しく処理
- インデントレベルで判断
"""

import ast
import re
import sys
from typing import List, Dict


class CodeStructureModifier:
    """Pythonコードの構造を安全に変更 v2"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        with open(file_path, "r", encoding="utf-8") as f:
            self.content = f.read()

        try:
            ast.parse(self.content)
            print(f"✅ 元ファイル構文OK: {file_path}")
        except SyntaxError as e:
            raise ValueError(f"❌ 元ファイルに構文エラー: {e}")

    def add_imports(self, imports: List[str]) -> "CodeStructureModifier":
        """インポート文を追加（重複チェック付き）"""
        lines = self.content.split("\n")

        # dotenvの次に追加
        target_line = -1
        for i, line in enumerate(lines):
            if "from dotenv import load_dotenv" in line:
                target_line = i
                break

        if target_line == -1:
            # dotenvがない場合は最後のインポート行
            for i, line in enumerate(lines):
                if line.strip().startswith(("import ", "from ")):
                    target_line = i

        added_count = 0
        for imp in imports:
            imp_stripped = imp.strip()
            module_name = imp_stripped.split("import")[-1].strip().split()[0]
            if module_name not in self.content:
                lines.insert(target_line + 1 + added_count, imp_stripped)
                added_count += 1
                print(f"✅ インポート追加: {module_name}")
            else:
                print(f"⏭️  既に存在: {module_name}")

        self.content = "\n".join(lines)
        return self

    def modify_class_init(
        self, class_name: str, new_params: Dict[str, str], initialization_code: str
    ) -> "CodeStructureModifier":
        """特定クラスの__init__を変更（ネストされた関数対応）"""
        lines = self.content.split("\n")

        # クラス定義を探す
        class_line = -1
        for i, line in enumerate(lines):
            if re.match(rf"^class {class_name}[\(:]", line):
                class_line = i
                print(f"✅ クラス発見: {class_name} (行{i+1})")
                break

        if class_line == -1:
            print(f"⚠️ クラス {class_name} が見つかりません")
            return self

        # そのクラスの__init__を探す
        init_line = -1
        class_indent = len(lines[class_line]) - len(lines[class_line].lstrip())

        for i in range(class_line + 1, len(lines)):
            # 次のクラス定義が来たら終了
            if re.match(r"^class ", lines[i]):
                break

            # __init__を探す（クラス直下のメソッドのみ）
            if re.search(r"^\s+def __init__\(", lines[i]):
                line_indent = len(lines[i]) - len(lines[i].lstrip())
                # クラス直下のメソッド（インデント+4）のみ対象
                if line_indent == class_indent + 4:
                    init_line = i
                    print(f"✅ __init__発見: (行{i+1})")
                    break

        if init_line == -1:
            print(f"⚠️ {class_name}.__init__ が見つかりません")
            return self

        init_indent = len(lines[init_line]) - len(lines[init_line].lstrip())

        # __init__のシグネチャを変更
        current_sig = lines[init_line]

        if any(param in current_sig for param in new_params.keys()):
            print(f"⏭️  {class_name}.__init__ は既に修正済み")
        else:
            if current_sig.rstrip().endswith("):"):
                param_lines = []
                for name, hint in new_params.items():
                    param_lines.append(f"{name}: {hint}")

                param_str = ", " + ", ".join(param_lines)
                lines[init_line] = current_sig.replace("):", param_str + "):", 1)
                print(f"✅ {class_name}.__init__にパラメータ追加")

        # 初期化コードを追加（__init__の最後 = 同じインデントレベルの次のメソッド直前）
        init_end = -1
        for i in range(init_line + 1, len(lines)):
            line_stripped = lines[i].lstrip()
            if not line_stripped:
                continue

            line_indent = len(lines[i]) - len(lines[i].lstrip())

            # 同じインデントレベルのメソッド定義またはクラス定義
            if line_indent == init_indent and line_stripped.startswith(("def ", "async def ")):
                init_end = i
                print(f"✅ __init__終了位置: (行{i+1}) {line_stripped[:40]}")
                break

            # クラス定義
            if line_indent <= class_indent and line_stripped.startswith("class "):
                init_end = i
                break

        if init_end == -1:
            init_end = len(lines)

        # 初期化コードが既に存在するかチェック
        init_body = "\n".join(lines[init_line:init_end])
        check_keyword = "self.decision_support"

        if check_keyword in init_body:
            print(f"⏭️  初期化コードは既に存在")
        else:
            # インデントを調整して挿入
            init_code_lines = initialization_code.strip().split("\n")
            indented_code = []
            for line in init_code_lines:
                if line.strip():
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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python3 ast_based_modifier_v2.py <ファイルパス>")
        sys.exit(1)

    file_path = sys.argv[1]
    print(f"\n📁 対象ファイル: {file_path}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    try:
        modifier = CodeStructureModifier(file_path)

        print("\n【ステップ1】インポート追加")
        modifier.add_imports(
            [
                "from agents.self_healing.logging.decision_support_system import DecisionSupportSystem",
                "from agents.self_healing.logging.knowledge_base_manager import KnowledgeBaseManager",
                "from core_agents.human_interaction_agent_v02_github_api import HumanInteractionAgent",
            ]
        )

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
