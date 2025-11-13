#!/usr/bin/env python3
"""
🎯 安全なコード修正 - 統合実行スクリプト

初心者でも簡単に使えるように設計:
1. テンプレートベース設定生成
2. 安全チェック付き実行
3. 結果レポート自動生成
"""

import subprocess
import sys
from pathlib import Path

# 同じディレクトリのモジュールをインポートできるようにパスを追加
sys.path.append(str(Path(__file__).parent))


def show_usage():
    """使い方を表示"""
    print(
        """
🚀 安全なコード修正ツール

使用方法:
  python3 run_safe_modification.py <コマンド> [オプション]

コマンド:
  init <ファイル>          - コード分析と修正提案
  template <タイプ>        - 設定テンプレート表示
  apply <設定ファイル>     - 修正を適用
  analyze <ファイル>       - コード品質分析
  batch <ディレクトリ>     - 一括分析

例:
  python3 run_safe_modification.py init my_module.py
  python3 run_safe_modification.py template imports
  python3 run_safe_modification.py apply config/change.yaml
  python3 run_safe_modification.py analyze scripts/task_executor.py
"""
    )


def main():
    if len(sys.argv) < 2:
        show_usage()
        return

    command = sys.argv[1]

    if command == "init" and len(sys.argv) > 2:
        target_file = Path(sys.argv[2])
        if target_file.exists():
            print(f"🔍 分析開始: {target_file}")
            # AI支援分析を実行
            subprocess.run(
                [sys.executable, "tools/code_modifier/ai_assisted_refactor.py", str(target_file)]
            )
        else:
            print("❌ 対象ファイルが見つかりません")

    elif command == "template" and len(sys.argv) > 2:
        template_type = sys.argv[2]
        try:
            from extensible_ast_framework import SafeCodeModifier

            modifier = SafeCodeModifier("dummy.yaml")
            print(modifier.create_template(template_type))
        except ImportError as e:
            print(f"❌ モジュールインポートエラー: {e}")
            print("📝 代わりに基本テンプレートを表示:")
            if template_type == "method":
                print(
                    """
file: target.py  
operations:
  - type: modify_method
    class: MyClass
    method: my_method
    signature:
      old: "def my_method(self):"
      new: "def my_method(self, param: str) -> bool:"
    add_code: |
        \"\"\"改良版メソッド\"\"\"
        return len(param) > 0
"""
                )
            elif template_type == "imports":
                print(
                    """
file: target.py
operations:
  - type: add_imports
    add:
      - "from pathlib import Path"
      - "import logging"
"""
                )
            elif template_type == "class":
                print(
                    """
file: target.py
operations:
  - type: add_class
    name: NewClass
    bases: [BaseClass]
    methods:
      - name: new_method
        args: self, data
        body: |
            \"\"\"新しいメソッド\"\"\"
            return processed_data
"""
                )

    elif command == "apply" and len(sys.argv) > 2:
        config_file = Path(sys.argv[2])
        if config_file.exists():
            print(f"🔧 修正適用: {config_file}")
            # 安全な修正を実行
            try:
                from extensible_ast_framework import SafeCodeModifier

                modifier = SafeCodeModifier(str(config_file))
                result = modifier.modify()
                if result.success:
                    print("✅ 修正が正常に完了しました")
                else:
                    print(f"❌ 修正に失敗: {result.message}")
            except ImportError:
                print("❌ 修正モジュールが利用できません")
        else:
            print("❌ 設定ファイルが見つかりません")

    elif command == "analyze" and len(sys.argv) > 2:
        target_file = Path(sys.argv[2])
        if target_file.exists():
            print(f"📊 詳細分析: {target_file}")
            subprocess.run(
                [sys.executable, "tools/code_modifier/ai_assisted_refactor.py", str(target_file)]
            )
        else:
            print("❌ 分析対象ファイルが見つかりません")

    else:
        show_usage()


if __name__ == "__main__":
    main()
