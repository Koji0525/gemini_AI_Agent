"""
DocumentationAgent - コードから自動的にドキュメント生成
"""

import os
import json
import ast
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class DocumentationAgent:
    """コード自動ドキュメント生成エージェント"""

    def __init__(self, project_root: str = "mvp_v4"):
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / "docs"
        self.knowledge_dir = self.project_root / "knowledge" / "learned"

        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)

        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key and genai:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
        else:
            self.model = None

    def analyze_code(self, file_path: Path) -> Dict[str, Any]:
        """Pythonコードを解析"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()

            tree = ast.parse(code)
            info = {
                "file": str(file_path),
                "classes": [],
                "functions": [],
                "docstring": ast.get_docstring(tree) or "",
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "docstring": ast.get_docstring(node) or "",
                        "methods": [],
                    }
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info["methods"].append(
                                {"name": item.name, "args": [arg.arg for arg in item.args.args]}
                            )
                    info["classes"].append(class_info)

                elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                    info["functions"].append(
                        {"name": node.name, "args": [arg.arg for arg in item.args.args]}
                    )

            return info
        except Exception as e:
            return {"file": str(file_path), "error": str(e)}

    def generate_docs_for_project(self, target_dir: Optional[Path] = None) -> Dict[str, Any]:
        """プロジェクト全体のドキュメント生成"""
        if target_dir is None:
            target_dir = self.project_root / "agents"

        print(f"📚 ドキュメント生成開始: {target_dir}")

        py_files = list(target_dir.rglob("*.py"))
        py_files = [f for f in py_files if "__pycache__" not in str(f)]

        results = {
            "timestamp": datetime.now().isoformat(),
            "files_analyzed": len(py_files),
            "generated_docs": [],
        }

        readme = f"# Project Documentation\n\nGenerated: {datetime.now()}\n\n"
        readme += f"## Analyzed Files: {len(py_files)}\n\n"

        for py_file in py_files:
            info = self.analyze_code(py_file)
            if "error" not in info:
                readme += f"### {py_file.name}\n"
                if info.get("classes"):
                    readme += f"**Classes:** {', '.join([c['name'] for c in info['classes']])}\n\n"

        readme_path = self.docs_dir / "PROJECT_README.md"
        readme_path.write_text(readme, encoding="utf-8")

        results["generated_docs"].append({"type": "readme", "file": str(readme_path)})

        # ナレッジ保存
        knowledge_file = self.knowledge_dir / "auto_registered_knowledge.json"
        knowledge_data = []
        if knowledge_file.exists():
            knowledge_data = json.loads(knowledge_file.read_text())

        knowledge_data.append(
            {
                "timestamp": datetime.now().isoformat(),
                "agent": "DocumentationAgent",
                "category": "ドキュメント/自動生成",
                "details": results,
                "success": True,
            }
        )

        knowledge_file.write_text(json.dumps(knowledge_data, ensure_ascii=False, indent=2))

        print(f"✅ ドキュメント生成完了: {len(results['generated_docs'])}件")
        return results
