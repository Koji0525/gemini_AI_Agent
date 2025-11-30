#!/usr/bin/env python3
"""
契約ベース監視システム
- APIシグネチャの変更検知
- 既存契約の破壊検出
- 新規契約の追跡
"""

import ast
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Set


class APIContract:
    """API契約クラス"""

    def __init__(self, module_path: str):
        self.module_path = module_path
        self.classes: Dict[str, dict] = {}
        self.functions: Dict[str, dict] = {}
        self.imports: Set[str] = set()
        self.contract_hash = ""

    def to_dict(self):
        return {
            "module_path": self.module_path,
            "classes": self.classes,
            "functions": self.functions,
            "imports": list(self.imports),
            "contract_hash": self.contract_hash,
        }


class ContractMonitor:
    """契約監視システム"""

    def __init__(self):
        self.contracts_dir = Path("contracts")
        self.contracts_dir.mkdir(exist_ok=True)

        self.baseline_file = self.contracts_dir / "baseline.json"
        self.current_file = self.contracts_dir / "current.json"

        self.baseline_contracts: Dict[str, APIContract] = {}
        self.current_contracts: Dict[str, APIContract] = {}

        self.violations = []
        self.new_contracts = []
        self.modified_contracts = []

    def extract_contract(self, file_path: Path) -> APIContract:
        """ファイルからAPI契約を抽出"""
        contract = APIContract(str(file_path))

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(file_path))

            # クラス解析
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = {}

                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            # メソッドシグネチャ抽出
                            args = [arg.arg for arg in item.args.args]
                            returns = (
                                ast.unparse(item.returns) if item.returns else None
                            )

                            methods[item.name] = {
                                "args": args,
                                "returns": returns,
                                "line": item.lineno,
                            }

                    contract.classes[node.name] = {
                        "methods": methods,
                        "line": node.lineno,
                        "bases": [ast.unparse(base) for base in node.bases],
                    }

                elif isinstance(node, ast.FunctionDef):
                    # トップレベル関数
                    if not any(
                        isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)
                    ):
                        args = [arg.arg for arg in node.args.args]
                        returns = ast.unparse(node.returns) if node.returns else None

                        contract.functions[node.name] = {
                            "args": args,
                            "returns": returns,
                            "line": node.lineno,
                        }

                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        contract.imports.add(alias.name)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        contract.imports.add(node.module)

            # 契約ハッシュ生成
            contract_str = json.dumps(contract.to_dict(), sort_keys=True)
            contract.contract_hash = hashlib.md5(contract_str.encode()).hexdigest()

        except Exception as e:
            print(f"⚠️  契約抽出エラー {file_path}: {e}")

        return contract

    def scan_project(self, exclude_patterns=None):
        """プロジェクト全体をスキャン"""
        if exclude_patterns is None:
            exclude_patterns = ["myenv", ".git", "__pycache__", "archived_"]

        python_files = []
        for file_path in Path(".").rglob("*.py"):
            if not any(pattern in str(file_path) for pattern in exclude_patterns):
                python_files.append(file_path)

        print(f"🔍 {len(python_files)}個のファイルをスキャン中...")

        for i, file_path in enumerate(python_files, 1):
            if i % 100 == 0:
                print(f"  {i}/{len(python_files)}...")

            contract = self.extract_contract(file_path)
            self.current_contracts[str(file_path)] = contract

        print(f"✅ スキャン完了: {len(self.current_contracts)}個の契約")

    def load_baseline(self):
        """ベースライン契約をロード"""
        if self.baseline_file.exists():
            with open(self.baseline_file, "r") as f:
                data = json.load(f)

            for path, contract_dict in data.items():
                contract = APIContract(path)
                contract.classes = contract_dict["classes"]
                contract.functions = contract_dict["functions"]
                contract.imports = set(contract_dict["imports"])
                contract.contract_hash = contract_dict["contract_hash"]

                self.baseline_contracts[path] = contract

            print(f"✅ ベースラインロード: {len(self.baseline_contracts)}個の契約")
        else:
            print("⚠️  ベースラインなし - 初回実行")

    def save_baseline(self):
        """現在の状態をベースラインとして保存"""
        data = {
            path: contract.to_dict()
            for path, contract in self.current_contracts.items()
        }

        with open(self.baseline_file, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ ベースライン保存: {len(self.current_contracts)}個の契約")

    def detect_violations(self):
        """契約違反を検出"""
        self.violations = []
        self.new_contracts = []
        self.modified_contracts = []

        # 新規ファイル検出
        for path in self.current_contracts:
            if path not in self.baseline_contracts:
                self.new_contracts.append(path)

        # 変更検出
        for path, current in self.current_contracts.items():
            if path not in self.baseline_contracts:
                continue

            baseline = self.baseline_contracts[path]

            # ハッシュ比較
            if current.contract_hash != baseline.contract_hash:
                violations = self._compare_contracts(path, baseline, current)

                if violations:
                    self.violations.extend(violations)
                    self.modified_contracts.append(path)

        # 削除ファイル検出
        deleted_files = set(self.baseline_contracts.keys()) - set(
            self.current_contracts.keys()
        )

        for deleted_file in deleted_files:
            self.violations.append(
                {
                    "type": "FILE_DELETED",
                    "file": deleted_file,
                    "severity": "HIGH",
                    "message": f"ファイルが削除されました: {deleted_file}",
                }
            )

        return {
            "violations": self.violations,
            "new_contracts": self.new_contracts,
            "modified_contracts": self.modified_contracts,
            "deleted_files": list(deleted_files),
        }

    def _compare_contracts(
        self, path: str, baseline: APIContract, current: APIContract
    ):
        """契約を比較して違反を検出"""
        violations = []

        # クラスの変更検出
        for class_name, baseline_class in baseline.classes.items():
            if class_name not in current.classes:
                violations.append(
                    {
                        "type": "CLASS_DELETED",
                        "file": path,
                        "class": class_name,
                        "severity": "HIGH",
                        "message": f"クラス削除: {class_name}",
                    }
                )
                continue

            current_class = current.classes[class_name]

            # メソッドの変更検出
            for method_name, baseline_method in baseline_class["methods"].items():
                if method_name not in current_class["methods"]:
                    violations.append(
                        {
                            "type": "METHOD_DELETED",
                            "file": path,
                            "class": class_name,
                            "method": method_name,
                            "severity": "HIGH",
                            "message": f"メソッド削除: {class_name}.{method_name}",
                        }
                    )
                    continue

                current_method = current_class["methods"][method_name]

                # シグネチャ変更検出
                if baseline_method["args"] != current_method["args"]:
                    violations.append(
                        {
                            "type": "METHOD_SIGNATURE_CHANGED",
                            "file": path,
                            "class": class_name,
                            "method": method_name,
                            "severity": "MEDIUM",
                            "old_args": baseline_method["args"],
                            "new_args": current_method["args"],
                            "message": f"メソッドシグネチャ変更: {class_name}.{method_name}",
                        }
                    )

        # 関数の変更検出
        for func_name, baseline_func in baseline.functions.items():
            if func_name not in current.functions:
                violations.append(
                    {
                        "type": "FUNCTION_DELETED",
                        "file": path,
                        "function": func_name,
                        "severity": "HIGH",
                        "message": f"関数削除: {func_name}",
                    }
                )
                continue

            current_func = current.functions[func_name]

            if baseline_func["args"] != current_func["args"]:
                violations.append(
                    {
                        "type": "FUNCTION_SIGNATURE_CHANGED",
                        "file": path,
                        "function": func_name,
                        "severity": "MEDIUM",
                        "old_args": baseline_func["args"],
                        "new_args": current_func["args"],
                        "message": f"関数シグネチャ変更: {func_name}",
                    }
                )

        return violations

    def generate_report(self):
        """レポート生成"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_contracts": len(self.current_contracts),
                "new_files": len(self.new_contracts),
                "modified_files": len(self.modified_contracts),
                "violations": len(self.violations),
                "high_severity": len(
                    [v for v in self.violations if v["severity"] == "HIGH"]
                ),
                "medium_severity": len(
                    [v for v in self.violations if v["severity"] == "MEDIUM"]
                ),
            },
            "violations": self.violations,
            "new_files": self.new_contracts,
            "modified_files": self.modified_contracts,
        }

        with open("contract_violations_report.json", "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📄 契約監視レポート")
        print(f"  新規ファイル: {report['summary']['new_files']}件")
        print(f"  変更ファイル: {report['summary']['modified_files']}件")
        print(f"  契約違反: {report['summary']['violations']}件")
        print(f"    �� HIGH: {report['summary']['high_severity']}件")
        print(f"    🟡 MEDIUM: {report['summary']['medium_severity']}件")

        return report

    def run(self, update_baseline=False):
        """実行"""
        print("=" * 60)
        print("契約ベース監視システム")
        print("=" * 60)
        print()

        self.load_baseline()
        self.scan_project()

        if update_baseline:
            self.save_baseline()
            print("✅ ベースライン更新完了")
        else:
            self.detect_violations()
            self.generate_report()


if __name__ == "__main__":
    import sys

    monitor = ContractMonitor()

    # 引数で動作モード切り替え
    update_baseline = "--update-baseline" in sys.argv

    monitor.run(update_baseline=update_baseline)
