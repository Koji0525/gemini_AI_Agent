"""
HighQualityExecutorV9 - ハイブリッド品質向上実行エンジン

戦略:
1. 構造化プロンプト（明確な制約と目標）
2. Few-shot成功例（過去の成功パターン提示）
3. テンプレート駆動（一貫した構造）
4. 英語プロンプト（LLM理解向上）
5. 1回完全生成（反復改良の品質劣化を回避）

v8との違い:
- v8: 反復改良（3回生成）→ 品質劣化リスク
- v9: 1回完全生成 → 品質安定、ハイブリッド戦略

Version: 9.0
Created: 2024-11-26
"""

import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict

# プロジェクトルート追加
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

# Gemini API
import google.generativeai as genai
from dotenv import load_dotenv

from agents.quality.quality_checker import QualityChecker
from agents.task_execution.few_shot_library import FewShotLibrary
# 内部モジュール
from agents.task_execution.prompt_template_loader import PromptTemplateLoader


class HighQualityExecutorV9:
    """
        ハイブリッド品質向上実行エンジン v9.0

        設計思想:
        - 1回の生成で高品質な出力を実現
        - ハイブリッドプロンプト戦略
        - 品質チェックと自動再試行
        - 既存システムとの互換性維持

        使用例:
    ```python
        executor = HighQualityExecutorV9()
        result = executor.execute_task(task_data, goal_description)

        if result['success']:
            print(f"生成行数: {result['total_lines']}行")
            print(f"ファイル数: {result['file_count']}個")
    ```
    """

    def __init__(self):
        """初期化"""
        print("🚀 HighQualityExecutorV9 初期化中...")

        # 環境変数読み込み
        load_dotenv()

        # コンポーネント初期化
        self.template_loader = PromptTemplateLoader()
        self.few_shot_library = FewShotLibrary()
        self.quality_checker = QualityChecker()

        # Gemini API設定
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY環境変数が設定されていません")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")

        # 生成設定（品質重視）
        self.generation_config = {
            "temperature": 0.3,  # 低温度で安定性向上
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,  # 最大出力
        }

        print("✅ HighQualityExecutorV9 初期化完了")
        print(f"   - モデル: gemini-2.0-flash-exp")
        print(f"   - 温度: {self.generation_config['temperature']}")
        print(f"   - 最大トークン: {self.generation_config['max_output_tokens']}")

    def execute_task(
        self, task_data: Dict, goal_description: str = "", required_role: str = "general"
    ) -> Dict:
        """
        タスク実行（ハイブリッド戦略）

        フロー:
        1. ハイブリッドプロンプト構築
        2. Gemini API呼び出し（1回）
        3. 出力パース
        4. 品質チェック
        5. 不合格なら再試行（最大3回）

        Args:
            task_data: タスクデータ
            goal_description: ゴール説明
            required_role: 必要な役割

        Returns:
            実行結果辞書
        """
        task_id = task_data.get("task_id", "unknown")
        task_description = task_data.get("description", "")

        print("\n" + "=" * 80)
        print(f"🚀 HighQualityExecutorV9: タスク{task_id}実行")
        print("=" * 80)
        print(f"タスク: {task_description[:100]}...")
        print()

        start_time = time.time()

        # 最大3回試行
        for attempt in range(1, 4):
            print(f"\n{'─'*80}")
            print(f"試行 {attempt}/3")
            print(f"{'─'*80}")

            try:
                # 1. ハイブリッドプロンプト構築
                print(f"[1/5] ハイブリッドプロンプト構築中...")
                prompt = self._build_hybrid_prompt(
                    task_description=task_description,
                    goal_description=goal_description,
                    attempt=attempt,
                )
                print(f"✅ プロンプト構築完了（{len(prompt)}文字）")

                # 2. Gemini API呼び出し
                print(f"[2/5] Gemini API呼び出し中...")
                response = self._call_gemini_api(prompt)
                print(f"✅ API呼び出し完了（{len(response)}文字）")

                # 3. 出力パース
                print(f"[3/5] 出力パース中...")
                parsed_output = self._parse_output(response)
                print(
                    f"✅ パース完了（{parsed_output['file_count']}ファイル、{parsed_output['total_lines']}行）"
                )

                # 4. 品質チェック
                print(f"[4/5] 品質チェック中...")
                passed, issues = self.quality_checker.check_output(response)

                if passed:
                    print(f"✅ 品質チェック合格（試行{attempt}回目）")

                    elapsed_time = time.time() - start_time

                    # 5. 成功結果を返す
                    result = {
                        "success": True,
                        "output": response,
                        "parsed_output": parsed_output,
                        "total_lines": parsed_output["total_lines"],
                        "file_count": parsed_output["file_count"],
                        "files": parsed_output["files"],
                        "attempts": attempt,
                        "quality_score": self._calculate_quality_score(parsed_output),
                        "elapsed_time": elapsed_time,
                        "executor_version": "v9.0",
                    }

                    print(f"\n[5/5] タスク実行成功")
                    print(f"   - 実行時間: {elapsed_time:.1f}秒")
                    print(f"   - 総行数: {result['total_lines']}行")
                    print(f"   - ファイル数: {result['file_count']}個")
                    print(f"   - 品質スコア: {result['quality_score']}/100")

                    return result
                else:
                    print(f"⚠️  品質チェック不合格:")
                    for issue in issues:
                        print(f"   - {issue}")

                    if attempt < 3:
                        print(f"\n🔄 改善して再試行します...")

                        # 再試行用プロンプト追加
                        retry_prompt = self.quality_checker.generate_retry_prompt(issues)
                        task_description += "\n\n" + retry_prompt
                    else:
                        print(f"\n❌ 最大試行回数（3回）に達しました")

            except Exception as e:
                print(f"❌ 試行{attempt}でエラー: {e}")
                import traceback

                traceback.print_exc()

                if attempt < 3:
                    print(f"🔄 再試行します...")
                    time.sleep(2)  # エラー後は2秒待機

        # 全試行失敗
        elapsed_time = time.time() - start_time

        return {
            "success": False,
            "error": "3回試行しましたが品質基準を満たせませんでした",
            "attempts": 3,
            "elapsed_time": elapsed_time,
            "issues": issues if "issues" in locals() else [],
            "executor_version": "v9.0",
        }

    def _build_hybrid_prompt(
        self, task_description: str, goal_description: str, attempt: int
    ) -> str:
        """
        ハイブリッドプロンプト構築（5段階戦略）

        Stage 1: システムロール設定
        Stage 2: Few-shot成功例提示
        Stage 3: テンプレート構造
        Stage 4: 実際のタスク
        Stage 5: 出力形式指定

        Args:
            task_description: タスク説明
            goal_description: ゴール説明
            attempt: 試行回数

        Returns:
            ハイブリッドプロンプト
        """
        # Stage 1: システムロール（英語）
        system_role = """# SYSTEM ROLE
You are a senior Python developer with 15 years of experience.
Your specialty is generating production-ready, large-scale code.
You NEVER generate incomplete or placeholder code.
Every function you write is fully implemented and tested.
"""

        # Stage 2: Few-shot成功例
        similar_tasks = self.few_shot_library.search_similar(task_description, top_k=2)
        few_shot_section = self.few_shot_library.format_examples(similar_tasks)

        # Stage 3: テンプレート構造
        template_structure = """# MANDATORY STRUCTURE TEMPLATE

Each file MUST follow this structure:
```python
# filename: {module_name}.py
'''
Comprehensive module docstring (50+ lines)
- Purpose: What this module does
- Architecture: How it's organized  
- Components: Key classes and functions
- Usage: Examples of how to use
- Error Handling: How errors are managed
'''

# Imports (20+ lines)
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
# ... comprehensive imports

logger = logging.getLogger(__name__)

# Constants and Configuration (30+ lines)
CONFIG = {
    # Detailed configuration
}

# Main Class (500+ lines)
class MainClass:
    '''Comprehensive class docstring (50+ lines)'''
    
    def __init__(self, config: Dict[str, Any]):
        '''Detailed initialization (20+ lines)'''
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        # ... full implementation
    
    def method_1(self, param1: str) -> Dict:
        '''
        Detailed method docstring (15+ lines)
        
        Args:
            param1: Description
            
        Returns:
            Description
            
        Raises:
            Exception: When...
        '''
        # Full implementation (40+ lines)
        pass
    
    # ... 10+ more comprehensive methods

# Utility Functions (100+ lines)
def utility_1():
    '''Detailed docstring'''
    # Full implementation
    pass

# Error Classes (50+ lines)
class CustomError(Exception):
    '''Detailed error class'''
    pass

# Main Entry Point (50+ lines)
if __name__ == '__main__':
    # Comprehensive main logic
    pass
```
"""

        # Stage 4: 実際のタスク
        task_section = f"""# CURRENT TASK

【PROJECT CONTEXT】
This is part of a 50,000-line enterprise system called "gemini_AI_Agent".
Your implementation must be production-ready and substantial.

【GOAL】
{goal_description if goal_description else 'Complete the following task'}

【TASK DESCRIPTION】
{task_description}

【CRITICAL CONSTRAINTS - NON-NEGOTIABLE】
- MINIMUM 1,000 lines of total code across all files
- MINIMUM 3 files (main implementation + tests + README)
- Each function MUST have comprehensive docstrings (10+ lines)
- Each module MUST have comprehensive README.md (300+ lines)
- PEP8 compliant with type hints everywhere
- Comprehensive error handling in every method
- Extensive logging throughout
- Unit tests with 90%+ coverage goal

【TECHNICAL REQUIREMENTS】
- Python 3.10+
- Type hints on ALL functions and methods
- Docstrings following Google style
- Error handling: try-except with specific exceptions
- Logging: Use logging module, not print
- Testing: pytest framework with fixtures
- Code quality: pylint score 9.0+
"""

        # Stage 5: 出力形式
        output_format = """# MANDATORY OUTPUT FORMAT

Generate complete implementation in the following format.
Use markdown code blocks with filename comments:
```python
# filename: main_implementation.py
# [500-1000 lines of fully implemented code]
# NO placeholders like "# TODO" or "pass"
# EVERY function fully implemented
```
```python
# filename: test_main_implementation.py
# [300-400 lines of comprehensive tests]
# Multiple test classes
# Test fixtures and mocks
# Edge case coverage
```
```markdown
# filename: README.md
# [300-500 lines of documentation]

# Project Name

## Overview (100 lines)
Detailed explanation...

## Installation (50 lines)
Step-by-step instructions...

## Usage (100 lines)
Code examples with explanations...

## API Reference (50 lines)
Function and class documentation...

## Development Guide (100 lines)
How to contribute, test, debug...
```

【FINAL CRITICAL REMINDERS】
1. This is ONE-SHOT generation - no iteration allowed
2. Quality over speed - take time to generate complete code
3. EVERY constraint above is mandatory
4. Follow the template structure exactly
5. Match or exceed the Few-shot example quality
6. Generate COMPLETE implementation, not sketches
7. NO placeholder code - everything must be functional

BEGIN IMPLEMENTATION NOW:
"""

        # 全てを結合
        hybrid_prompt = (
            system_role
            + "\n"
            + few_shot_section
            + "\n"
            + template_structure
            + "\n"
            + task_section
            + "\n"
            + output_format
        )

        return hybrid_prompt

    def _call_gemini_api(self, prompt: str) -> str:
        """
        Gemini API呼び出し

        Args:
            prompt: プロンプト文字列

        Returns:
            生成されたテキスト
        """
        try:
            response = self.model.generate_content(prompt, generation_config=self.generation_config)

            return response.text

        except Exception as e:
            raise RuntimeError(f"Gemini API呼び出しエラー: {e}")

    def _parse_output(self, output_text: str) -> Dict[str, Any]:
        """
        出力をパース

        Args:
            output_text: 生成されたテキスト

        Returns:
            パース結果
        """
        files = []
        total_lines = 0

        # コードブロック抽出パターン
        pattern = r"```(?:python|markdown|yaml|json|txt)?\s*\n#?\s*filename:\s*([^\n]+)\n(.*?)```"
        matches = re.finditer(pattern, output_text, re.DOTALL)

        for match in matches:
            filename = match.group(1).strip()
            content = match.group(2)
            lines = len(content.split("\n"))

            files.append({"name": filename, "content": content, "lines": lines})

            total_lines += lines

        return {
            "files": files,
            "file_count": len(files),
            "total_lines": total_lines,
            "raw_text": output_text,
        }

    def _calculate_quality_score(self, parsed_output: Dict) -> int:
        """
        品質スコア計算

        スコア基準:
        - 行数: 1000行以上で満点（50点）
        - ファイル数: 3個以上で満点（30点）
        - README: 存在で満点（20点）

        Args:
            parsed_output: パース結果

        Returns:
            品質スコア（0-100）
        """
        score = 0

        # 行数スコア（50点満点）
        total_lines = parsed_output["total_lines"]
        if total_lines >= 1000:
            score += 50
        else:
            score += int(50 * (total_lines / 1000))

        # ファイル数スコア（30点満点）
        file_count = parsed_output["file_count"]
        if file_count >= 3:
            score += 30
        else:
            score += int(30 * (file_count / 3))

        # READMEスコア（20点満点）
        has_readme = any("README" in f["name"].upper() for f in parsed_output["files"])
        if has_readme:
            score += 20

        return min(score, 100)


# テスト用コード
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("HighQualityExecutorV9 テスト")
    print("=" * 80 + "\n")

    # 初期化テスト
    try:
        executor = HighQualityExecutorV9()
        print("✅ 初期化成功\n")

        # Mockタスクテスト
        mock_task = {
            "task_id": "TEST_001",
            "description": "データベース接続を管理するシンプルなモジュールを実装してください。",
        }

        print("📋 Mockタスク実行テスト:")
        print(f"   タスクID: {mock_task['task_id']}")
        print(f"   説明: {mock_task['description']}")
        print()

        # 注意: 実際のAPI呼び出しはコストがかかるため、テストは慎重に
        print("⚠️  実際のGemini API呼び出しテストは手動で実行してください")
        print(
            "   コマンド: python3 -c \"from agents.task_execution.high_quality_executor_v9 import HighQualityExecutorV9; e = HighQualityExecutorV9(); print(e.execute_task({'task_id': 'TEST', 'description': 'test'}))\""
        )

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback

        traceback.print_exc()
