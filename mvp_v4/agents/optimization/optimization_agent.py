"""
OptimizationAgent - パフォーマンス最適化
"""

import os
import json
import time
import ast
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
import cProfile
import pstats
import io

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class OptimizationAgent:
    """パフォーマンス最適化エージェント"""

    def __init__(self, project_root: str = "mvp_v4"):
        self.project_root = Path(project_root)
        self.knowledge_dir = self.project_root / "knowledge" / "learned"
        self.reports_dir = self.project_root / "reports" / "optimization"

        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.profile_results = []

        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key and genai:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
        else:
            self.model = None

    def profile_function(self, func: Callable) -> Dict[str, Any]:
        """関数のプロファイリング"""
        profiler = cProfile.Profile()
        profiler.enable()
        start_time = time.time()

        try:
            result = func()
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)

        end_time = time.time()
        profiler.disable()

        profile_data = {
            "function": func.__name__,
            "execution_time": end_time - start_time,
            "success": success,
            "error": error,
            "timestamp": datetime.now().isoformat(),
        }

        self.profile_results.append(profile_data)
        return profile_data

    def analyze_code_patterns(self, file_path: Path) -> List[Dict[str, Any]]:
        """コードパターンを解析"""
        suggestions = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()

            tree = ast.parse(code)

            for node in ast.walk(tree):
                # 大きな関数の検出
                if isinstance(node, ast.FunctionDef):
                    func_lines = len([n for n in ast.walk(node) if isinstance(n, ast.stmt)])
                    if func_lines > 50:
                        suggestions.append(
                            {
                                "type": "large_function",
                                "severity": "low",
                                "message": f"関数が大きい（約{func_lines}行）",
                                "suggestion": "関数を小さく分割することを検討してください",
                                "line": node.lineno,
                            }
                        )

        except Exception as e:
            print(f"⚠️ コード解析エラー: {e}")

        return suggestions

    def optimize_project(self, target_dir: Optional[Path] = None) -> Dict[str, Any]:
        """プロジェクト全体の最適化分析"""
        if target_dir is None:
            target_dir = self.project_root / "agents"

        print(f"🔍 最適化分析開始: {target_dir}")

        py_files = list(target_dir.rglob("*.py"))
        py_files = [f for f in py_files if "__pycache__" not in str(f)]

        all_suggestions = []

        for py_file in py_files[:5]:  # 最初の5ファイルのみ
            suggestions = self.analyze_code_patterns(py_file)
            for suggestion in suggestions:
                suggestion["file"] = str(py_file)
                all_suggestions.append(suggestion)

        results = {
            "timestamp": datetime.now().isoformat(),
            "files_analyzed": len(py_files),
            "total_suggestions": len(all_suggestions),
            "suggestions": all_suggestions[:10],
        }

        # ナレッジ保存
        knowledge_file = self.knowledge_dir / "auto_registered_knowledge.json"
        knowledge_data = []
        if knowledge_file.exists():
            knowledge_data = json.loads(knowledge_file.read_text())

        knowledge_data.append(
            {
                "timestamp": datetime.now().isoformat(),
                "agent": "OptimizationAgent",
                "category": "最適化/パフォーマンス",
                "details": results,
                "success": True,
            }
        )

        knowledge_file.write_text(json.dumps(knowledge_data, ensure_ascii=False, indent=2))

        print(f"✅ 最適化分析完了: {len(all_suggestions)}件の提案")
        return results
