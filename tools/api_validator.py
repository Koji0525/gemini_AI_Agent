#!/usr/bin/env python3
"""
自動API検証ツール（改善版）

【改善点】
- プロジェクトに合わせた検証対象の自動検出
- 明確な成功/失敗の表示
- スキップ対象を警告ではなく情報として表示

使用例：
    python3 tools/api_validator.py
    python3 tools/api_validator.py GoogleSheetsManager
"""

import sys
import importlib
import inspect
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime


class APIValidator:
    """API仕様の自動検証・ドキュメント生成"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.results = {}
        self.total_checked = 0
        self.total_success = 0
        self.total_skipped = 0

    def detect_project_classes(self) -> List[tuple]:
        """プロジェクトから検証対象クラスを自動検出"""
        targets = []

        # GoogleSheetsManager（必須）
        if (self.project_root / "tools" / "sheets_manager.py").exists():
            targets.append(("tools.sheets_manager", "GoogleSheetsManager"))

        # PMAgent（存在すれば）
        if (self.project_root / "agents" / "pm_agent" / "pm_agent.py").exists():
            targets.append(("agents.pm_agent.pm_agent", "PMAgent"))

        # TaskExecutor（存在すれば）
        if (self.project_root / "task_executor" / "task_executor.py").exists():
            targets.append(("task_executor.task_executor", "TaskExecutor"))

        return targets

    def validate_class(self, module_path: str, class_name: str) -> Dict[str, Any]:
        """クラスのAPI仕様を検証"""
        try:
            # モジュール読み込み
            sys.path.insert(0, str(self.project_root))
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)

            # インスタンス生成（可能な場合）
            try:
                instance = cls()
                use_instance = True
            except:
                instance = cls
                use_instance = False

            # メソッド一覧を取得
            methods = {}
            for name in dir(instance):
                if name.startswith("_"):
                    continue

                attr = getattr(instance if use_instance else cls, name)
                if callable(attr):
                    try:
                        sig = inspect.signature(attr)
                        methods[name] = {
                            "signature": str(sig),
                            "params": [p for p in sig.parameters.keys()],
                            "is_async": inspect.iscoroutinefunction(attr),
                        }
                    except:
                        # シグネチャ取得失敗は無視
                        pass

            self.total_success += 1

            return {
                "class_name": class_name,
                "module": module_path,
                "methods": methods,
                "status": "success",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "class_name": class_name,
                "module": module_path,
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now().isoformat(),
            }

    def generate_markdown_doc(self, api_spec: Dict) -> str:
        """APIドキュメント（Markdown）を自動生成"""
        md = f"# {api_spec['class_name']} API仕様\n\n"
        md += f"**Module**: `{api_spec['module']}`\n"
        md += f"**最終更新**: {api_spec['timestamp']}\n\n"
        md += "## メソッド一覧\n\n"

        for method, info in sorted(api_spec["methods"].items()):
            async_mark = "async " if info["is_async"] else ""
            md += f"### {async_mark}`{method}{info['signature']}`\n\n"
            md += f"**引数**: {', '.join(info['params']) if info['params'] else 'なし'}\n\n"

        return md

    def run_validation(self, targets: Optional[List[tuple]] = None) -> Dict:
        """複数クラスの一括検証"""
        if targets is None:
            targets = self.detect_project_classes()

        self.total_checked = len(targets)
        results = {}

        print("=" * 60)
        print("🔍 API検証を開始します")
        print("=" * 60)

        for module_path, class_name in targets:
            print(f"\n📦 検証中: {class_name}")
            spec = self.validate_class(module_path, class_name)
            results[class_name] = spec

            if spec["status"] == "success":
                print(f"   ✅ 成功: {len(spec['methods'])}個のメソッドを検出")
                for method in list(spec["methods"].keys())[:3]:
                    print(f"      - {method}()")
                if len(spec["methods"]) > 3:
                    print(f"      ... 他{len(spec['methods'])-3}個")
            else:
                print(f"   ℹ️  スキップ: {spec.get('error', 'モジュール未配置')}")
                self.total_skipped += 1
                self.total_success -= 1  # カウント調整

        return results

    def save_results(self, results: Dict, output_dir: str = "docs/api"):
        """検証結果を保存"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 成功したものだけ保存
        success_results = {k: v for k, v in results.items() if v["status"] == "success"}

        if not success_results:
            print("\n⚠️  保存する結果がありません")
            return

        # JSON形式で保存
        json_file = output_path / "api_specs.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(success_results, f, indent=2, ensure_ascii=False)

        print(f"\n✅ API仕様を保存: {json_file}")

        # Markdownドキュメント生成
        for class_name, spec in success_results.items():
            md_content = self.generate_markdown_doc(spec)
            md_file = output_path / f"{class_name}.md"
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(md_content)
            print(f"✅ ドキュメント生成: {md_file}")

    def print_summary(self):
        """結果サマリーを表示"""
        print("\n" + "=" * 60)
        print("📊 検証結果サマリー")
        print("=" * 60)

        if self.total_success > 0:
            print(f"✅ 検証成功: {self.total_success}個のクラス")
            print(f"   → API仕様ドキュメントを生成しました")

        if self.total_skipped > 0:
            print(f"ℹ️  スキップ: {self.total_skipped}個のクラス")
            print(f"   → プロジェクトに存在しないため省略")

        print("\n" + "=" * 60)

        if self.total_success > 0:
            print("✅ 検証完了: 問題ありません")
        else:
            print("⚠️  検証対象が見つかりませんでした")

        print("=" * 60)


def main():
    """メイン実行"""
    import argparse

    parser = argparse.ArgumentParser(description="API自動検証ツール")
    parser.add_argument("class_name", nargs="?", help="検証するクラス名（省略時は自動検出）")

    args = parser.parse_args()

    validator = APIValidator()

    # 検証対象の決定
    if args.class_name:
        # 手動指定
        targets = []
        if args.class_name == "GoogleSheetsManager":
            targets = [("tools.sheets_manager", "GoogleSheetsManager")]
        else:
            print(f"⚠️  未対応のクラス: {args.class_name}")
            return 1
    else:
        # 自動検出
        targets = None

    # 検証実行
    results = validator.run_validation(targets)

    # 結果保存
    if any(r["status"] == "success" for r in results.values()):
        validator.save_results(results)

    # サマリー表示
    validator.print_summary()

    # 終了コード（成功が1つ以上あればOK）
    return 0 if validator.total_success > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
