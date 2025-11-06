"""
DocumentationAgent - コードから自動的にドキュメントを生成

機能:
1. Pythonファイルの解析（AST使用）
2. README.md、API仕様書の自動生成
3. ナレッジベースへの登録
"""

import ast
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import asyncio


class DocumentationAgent:
    """コードから自動的にドキュメントを生成するエージェント"""

    def __init__(self, knowledge_path: str = "mvp_v4/knowledge/learned"):
        """
        初期化

        Args:
            knowledge_path: ナレッジ保存先パス
        """
        self.knowledge_path = knowledge_path
        self.stats = {"analyzed_files": 0, "generated_docs": 0, "errors": 0}

    async def analyze_python_file(self, file_path: str) -> Dict[str, Any]:
        """
        Pythonファイルを解析してドキュメント情報を抽出

        Args:
            file_path: 解析対象のPythonファイルパス

        Returns:
            解析結果（クラス、関数、docstring等）
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source)

            result = {
                "file_path": file_path,
                "classes": [],
                "functions": [],
                "imports": [],
                "module_docstring": ast.get_docstring(tree),
                "analyzed_at": datetime.now().isoformat(),
            }

            # クラス情報の抽出
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                        "methods": [],
                        "bases": [self._get_name(base) for base in node.bases],
                    }

                    # メソッド情報
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = {
                                "name": item.name,
                                "docstring": ast.get_docstring(item),
                                "args": [arg.arg for arg in item.args.args],
                                "is_async": isinstance(item, ast.AsyncFunctionDef),
                            }
                            class_info["methods"].append(method_info)

                    result["classes"].append(class_info)

                # トップレベル関数
                elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                    func_info = {
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                        "args": [arg.arg for arg in node.args.args],
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                    }
                    result["functions"].append(func_info)

                # インポート情報
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        result["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        result["imports"].append(node.module)

            self.stats["analyzed_files"] += 1
            return result

        except Exception as e:
            self.stats["errors"] += 1
            return {
                "file_path": file_path,
                "error": str(e),
                "analyzed_at": datetime.now().isoformat(),
            }

    def _get_name(self, node) -> str:
        """ASTノードから名前を取得"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return str(node)

    async def generate_readme(self, project_path: str, output_path: str = "README.md") -> str:
        """
        プロジェクト全体のREADME.mdを自動生成

        Args:
            project_path: プロジェクトルートパス
            output_path: 出力先パス

        Returns:
            生成されたREADMEの内容
        """
        python_files = list(Path(project_path).rglob("*.py"))

        # 各ファイルを解析
        analyses = []
        for py_file in python_files:
            if "__pycache__" not in str(py_file):
                analysis = await self.analyze_python_file(str(py_file))
                if "error" not in analysis:
                    analyses.append(analysis)

        # README生成
        readme_content = self._build_readme(analyses, project_path)

        # ファイル出力
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(readme_content)

        self.stats["generated_docs"] += 1
        return readme_content

    def _build_readme(self, analyses: List[Dict], project_path: str) -> str:
        """README.mdの内容を構築"""
        readme = f"""# Project Documentation

**自動生成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📋 プロジェクト概要

このプロジェクトは{len(analyses)}個のPythonモジュールで構成されています。

## 📊 統計情報

- 総ファイル数: {len(analyses)}
- 総クラス数: {sum(len(a.get('classes', [])) for a in analyses)}
- 総関数数: {sum(len(a.get('functions', [])) for a in analyses)}

## 🏗️ モジュール構成

"""

        for analysis in analyses:
            file_path = analysis.get("file_path", "")
            relative_path = os.path.relpath(file_path, project_path)

            readme += f"\n### 📄 {relative_path}\n\n"

            if analysis.get("module_docstring"):
                readme += f"{analysis['module_docstring']}\n\n"

            # クラス情報
            if analysis.get("classes"):
                readme += "**クラス:**\n\n"
                for cls in analysis["classes"]:
                    readme += f"- `{cls['name']}`"
                    if cls.get("docstring"):
                        readme += f": {cls['docstring'].split(chr(10))[0]}"
                    readme += "\n"
                readme += "\n"

            # 関数情報
            if analysis.get("functions"):
                readme += "**関数:**\n\n"
                for func in analysis["functions"]:
                    readme += f"- `{func['name']}({', '.join(func['args'])})`"
                    if func.get("docstring"):
                        readme += f": {func['docstring'].split(chr(10))[0]}"
                    readme += "\n"
                readme += "\n"

        return readme

    async def generate_api_spec(self, file_path: str, output_path: str) -> Dict[str, Any]:
        """
        API仕様書を生成

        Args:
            file_path: 解析対象ファイル
            output_path: 出力先パス

        Returns:
            API仕様情報
        """
        analysis = await self.analyze_python_file(file_path)

        api_spec = {"file": file_path, "generated_at": datetime.now().isoformat(), "endpoints": []}

        # クラスのメソッドをAPI仕様として出力
        for cls in analysis.get("classes", []):
            for method in cls.get("methods", []):
                endpoint = {
                    "class": cls["name"],
                    "method": method["name"],
                    "parameters": method["args"],
                    "is_async": method["is_async"],
                    "description": method.get("docstring", ""),
                }
                api_spec["endpoints"].append(endpoint)

        # JSON形式で保存
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(api_spec, f, indent=2, ensure_ascii=False)

        self.stats["generated_docs"] += 1
        return api_spec

    async def save_knowledge(self, event: str, details: Dict[str, Any]) -> bool:
        """
        ナレッジベースに登録

        Args:
            event: イベント名
            details: 詳細情報

        Returns:
            成功/失敗
        """
        try:
            knowledge_file = f"{self.knowledge_path}/auto_registered_knowledge.json"

            # 既存データ読み込み
            if os.path.exists(knowledge_file):
                with open(knowledge_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {"knowledge_base": [], "total_entries": 0, "last_updated": None}

            # 新規エントリ追加
            entry = {
                "event": event,
                "details": details,
                "timestamp": datetime.now().isoformat(),
                "agent": "DocumentationAgent",
            }

            data["knowledge_base"].append(entry)
            data["total_entries"] = len(data["knowledge_base"])
            data["last_updated"] = datetime.now().isoformat()

            # 保存
            os.makedirs(os.path.dirname(knowledge_file), exist_ok=True)
            with open(knowledge_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"❌ ナレッジ登録失敗: {e}")
            return False

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        タスク実行（統一インターフェース）

        Args:
            task: タスク情報

        Returns:
            実行結果
        """
        task_type = task.get("type")

        if task_type == "analyze":
            file_path = task.get("file_path")
            result = await self.analyze_python_file(file_path)
            await self.save_knowledge("code_analysis", result)
            return {"status": "success", "data": result}

        elif task_type == "generate_readme":
            project_path = task.get("project_path", ".")
            output_path = task.get("output_path", "README.md")
            content = await self.generate_readme(project_path, output_path)
            await self.save_knowledge(
                "readme_generated", {"project_path": project_path, "output_path": output_path}
            )
            return {"status": "success", "content": content}

        elif task_type == "generate_api_spec":
            file_path = task.get("file_path")
            output_path = task.get("output_path", "api_spec.json")
            spec = await self.generate_api_spec(file_path, output_path)
            await self.save_knowledge("api_spec_generated", spec)
            return {"status": "success", "spec": spec}

        else:
            return {"status": "error", "message": f"Unknown task type: {task_type}"}

    def get_stats(self) -> Dict[str, int]:
        """統計情報を取得"""
        return self.stats.copy()
