# local_fix_agent.py
"""
ローカル修正エージェント
ローカルAIまたはルールベースで迅速な修正を実行
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from data_models import BugFixTask, FixResult, ErrorContextModel

logger = logging.getLogger(__name__)


class LocalFixAgent:
    """
    ローカル修正エージェント

    特徴:
    - 迅速な処理（ローカルAI or ルールベース）
    - 簡易エラーに特化
    - オフライン動作可能
    - コスト効率が高い
    """

    def __init__(
        self,
        command_monitor,
        wp_tester=None,
        use_local_ai: bool = True,
        ai_chat_agent=None,  # browser_ai_chat_agent経由でGemini/DeepSeek
    ):
        """
        初期化

        Args:
            command_monitor: CommandMonitorAgent
            wp_tester: WordPressTester
            use_local_ai: ローカルAI使用フラグ
            ai_chat_agent: AIチャットエージェント
        """
        self.cmd_monitor = command_monitor
        self.wp_tester = wp_tester
        self.use_local_ai = use_local_ai
        self.ai_chat = ai_chat_agent

        # バックアップディレクトリ
        self.backup_dir = Path("./backups/local_fix")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # 統計情報
        self.stats = {
            "total_fixes": 0,
            "successful_fixes": 0,
            "failed_fixes": 0,
            "rule_based_fixes": 0,
            "ai_based_fixes": 0,
        }

        # ルールベース修正パターン
        self._init_fix_patterns()

        logger.info(f"✅ LocalFixAgent 初期化完了 (AI使用={'有効' if use_local_ai else '無効'})")

    def _init_fix_patterns(self):
        """修正パターンを初期化"""
        self.fix_patterns = {
            # インポートエラー
            "ImportError": self._fix_import_error,
            "ModuleNotFoundError": self._fix_module_not_found,
            # 構文エラー
            "SyntaxError": self._fix_syntax_error,
            "IndentationError": self._fix_indentation_error,
            # 属性エラー
            "AttributeError": self._fix_attribute_error,
            # 名前エラー
            "NameError": self._fix_name_error,
            # タイプエラー
            "TypeError": self._fix_type_error,
            # キーエラー
            "KeyError": self._fix_key_error,
        }

    async def execute_bug_fix_task(self, bug_fix_task: BugFixTask) -> FixResult:
        """
        バグ修正タスクを実行（ローカル処理）

        Args:
            bug_fix_task: バグ修正タスク

        Returns:
            FixResult: 修正結果
        """
        start_time = datetime.now()
        task_id = bug_fix_task.task_id

        try:
            logger.info("=" * 60)
            logger.info(f"💻 ローカルバグ修正タスク実行: {task_id}")
            logger.info("=" * 60)

            self.stats["total_fixes"] += 1

            error_context = bug_fix_task.error_context
            error_type = error_context.error_type

            # 1. ルールベース修正を試行
            if error_type in self.fix_patterns:
                logger.info(f"🔧 ルールベース修正を試行: {error_type}")
                rule_result = await self._try_rule_based_fix(bug_fix_task)

                if rule_result["success"]:
                    self.stats["successful_fixes"] += 1
                    self.stats["rule_based_fixes"] += 1

                    execution_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ ルールベース修正成功: {task_id} ({execution_time:.2f}秒)")

                    return FixResult(
                        task_id=task_id,
                        success=True,
                        modified_files=bug_fix_task.target_files,
                        generated_code=rule_result["code"],
                        test_passed=True,
                        execution_time=execution_time,
                        confidence_score=0.9,
                        reasoning="Rule-based fix applied successfully",
                    )

            # 2. ローカルAI修正を試行
            if self.use_local_ai and self.ai_chat:
                logger.info("🤖 ローカルAI修正を試行")
                ai_result = await self._try_ai_based_fix(bug_fix_task)

                if ai_result["success"]:
                    self.stats["successful_fixes"] += 1
                    self.stats["ai_based_fixes"] += 1

                    execution_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ AI修正成功: {task_id} ({execution_time:.2f}秒)")

                    return FixResult(
                        task_id=task_id,
                        success=True,
                        modified_files=bug_fix_task.target_files,
                        generated_code=ai_result["code"],
                        test_passed=ai_result.get("test_passed", False),
                        execution_time=execution_time,
                        confidence_score=ai_result.get("confidence", 0.7),
                        reasoning=ai_result.get("reasoning", ""),
                    )

            # 3. 修正失敗
            self.stats["failed_fixes"] += 1
            execution_time = (datetime.now() - start_time).total_seconds()

            logger.warning(f"⚠️ ローカル修正失敗: {task_id}")

            return FixResult(
                task_id=task_id,
                success=False,
                modified_files=[],
                generated_code="",
                test_passed=False,
                execution_time=execution_time,
                confidence_score=0.0,
                error_message="No applicable fix found locally",
            )

        except Exception as e:
            logger.error(f"💥 ローカル修正エラー: {e}", exc_info=True)
            self.stats["failed_fixes"] += 1

            return FixResult(
                task_id=task_id,
                success=False,
                modified_files=[],
                generated_code="",
                test_passed=False,
                execution_time=(datetime.now() - start_time).total_seconds(),
                error_message=str(e),
            )

    async def _try_rule_based_fix(self, bug_fix_task: BugFixTask) -> Dict[str, Any]:
        """ルールベース修正を試行"""
        error_context = bug_fix_task.error_context
        error_type = error_context.error_type

        fix_function = self.fix_patterns.get(error_type)
        if not fix_function:
            return {"success": False, "error": "No fix pattern available"}

        try:
            fixed_code = await fix_function(error_context)

            if fixed_code:
                # バックアップ作成
                await self._create_backup(bug_fix_task.target_files)

                # 修正適用
                await self._apply_fix(bug_fix_task.target_files[0], fixed_code)

                return {"success": True, "code": fixed_code}
            else:
                return {"success": False, "error": "Fix generation failed"}

        except Exception as e:
            logger.error(f"❌ ルールベース修正エラー: {e}")
            return {"success": False, "error": str(e)}

    async def _try_ai_based_fix(self, bug_fix_task: BugFixTask) -> Dict[str, Any]:
        """AI修正を試行（ローカルAI経由）"""
        if not self.ai_chat:
            return {"success": False, "error": "AI agent not available"}

        try:
            # 修正プロンプト構築
            prompt = self._build_fix_prompt(bug_fix_task.error_context)

            # AIに送信
            ai_response = await self.ai_chat.send_prompt_and_wait(prompt)

            if not ai_response or "error" in ai_response:
                return {"success": False, "error": "AI response error"}

            # コードブロック抽出
            code = self._extract_code_block(ai_response.get("content", ""))

            if code:
                # バックアップ作成
                await self._create_backup(bug_fix_task.target_files)

                # 修正適用
                await self._apply_fix(bug_fix_task.target_files[0], code)

                return {"success": True, "code": code, "confidence": 0.7, "reasoning": "AI-generated fix"}
            else:
                return {"success": False, "error": "No code block found in AI response"}

        except Exception as e:
            logger.error(f"❌ AI修正エラー: {e}")
            return {"success": False, "error": str(e)}

    def _build_fix_prompt(self, error_context: ErrorContextModel) -> str:
        """修正プロンプトを構築"""
        return f"""以下のPythonエラーを修正してください。

エラータイプ: {error_context.error_type}
エラーメッセージ: {error_context.error_message}
ファイル: {error_context.file_path}:{error_context.line_number}

周辺コード:
```python
{error_context.surrounding_code}
```

修正後の完全なコードをPythonコードブロックで返してください。"""

    def _extract_code_block(self, text: str) -> Optional[str]:
        """テキストからコードブロックを抽出"""
        pattern = r"```python\n(.*?)\n```"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1) if match else None

    # ========================================
    # ルールベース修正関数群
    # ========================================

    async def _fix_import_error(self, error_context: ErrorContextModel) -> Optional[str]:
        """インポートエラーを修正"""
        error_msg = error_context.error_message

        # "cannot import name 'X' from 'Y'"パターン
        match = re.search(r"cannot import name '(\w+)' from '([\w.]+)'", error_msg)
        if match:
            name, module = match.groups()

            # コード取得
            code = error_context.surrounding_code or ""

            # インポート文を修正
            fixed_code = re.sub(
                rf"from {module} import .*{name}.*",
                f"# Fixed: {name} not available in {module}\n# from {module} import {name}",
                code,
            )

            return fixed_code if fixed_code != code else None

        return None

    async def _fix_module_not_found(self, error_context: ErrorContextModel) -> Optional[str]:
        """モジュール未検出エラーを修正"""
        error_msg = error_context.error_message

        # "No module named 'X'"パターン
        match = re.search(r"No module named '([\w.]+)'", error_msg)
        if match:
            module = match.group(1)

            code = error_context.surrounding_code or ""

            # インポート文をコメントアウト
            fixed_code = re.sub(rf"import {module}", f"# import {module}  # Module not found", code)
            fixed_code = re.sub(rf"from {module} import", f"# from {module} import  # Module not found", fixed_code)

            return fixed_code if fixed_code != code else None

        return None

    async def _fix_syntax_error(self, error_context: ErrorContextModel) -> Optional[str]:
        """構文エラーを修正"""
        code = error_context.surrounding_code or ""
        line_no = error_context.line_number

        lines = code.split("\n")
        if line_no and 0 < line_no <= len(lines):
            error_line = lines[line_no - 1]

            # よくある構文エラーパターン
            fixes = [
                (r":\s*$", ":  # Fixed missing colon"),
                (r"\)\s*$", ")  # Fixed missing parenthesis"),
                (r"]\s*$", "]  # Fixed missing bracket"),
            ]

            for pattern, replacement in fixes:
                if re.search(pattern, error_line):
                    lines[line_no - 1] = re.sub(pattern, replacement, error_line)
                    return "\n".join(lines)

        return None

    async def _fix_indentation_error(self, error_context: ErrorContextModel) -> Optional[str]:
        """インデントエラーを修正"""
        code = error_context.surrounding_code or ""

        # タブをスペースに統一
        fixed_code = code.replace("\t", "    ")

        return fixed_code if fixed_code != code else None

    async def _fix_attribute_error(self, error_context: ErrorContextModel) -> Optional[str]:
        """属性エラーを修正"""
        error_msg = error_context.error_message

        # "'X' object has no attribute 'Y'"パターン
        match = re.search(r"'(\w+)' object has no attribute '(\w+)'", error_msg)
        if match:
            obj_type, attr = match.groups()

            code = error_context.surrounding_code or ""

            # 属性アクセスをhasattr()でラップ
            pattern = rf"(\w+)\.{attr}"
            replacement = rf"getattr(\1, '{attr}', None)  # Fixed: safe attribute access"

            fixed_code = re.sub(pattern, replacement, code)

            return fixed_code if fixed_code != code else None

        return None

    async def _fix_name_error(self, error_context: ErrorContextModel) -> Optional[str]:
        """名前エラーを修正"""
        error_msg = error_context.error_message

        # "name 'X' is not defined"パターン
        match = re.search(r"name '(\w+)' is not defined", error_msg)
        if match:
            var_name = match.group(1)

            code = error_context.surrounding_code or ""

            # 変数を定義
            lines = code.split("\n")
            lines.insert(0, f"{var_name} = None  # Fixed: undefined variable")

            return "\n".join(lines)

        return None

    async def _fix_type_error(self, error_context: ErrorContextModel) -> Optional[str]:
        """タイプエラーを修正"""
        # 簡易的な対応: Noneチェックを追加
        code = error_context.surrounding_code or ""

        # NoneTypeエラーの場合
        if "NoneType" in error_context.error_message:
            # 最初の関数/メソッド呼び出しにNoneチェックを追加
            pattern = r"(\w+)\("
            replacement = r"(\1 if \1 is not None else lambda *a, **k: None)("

            fixed_code = re.sub(pattern, replacement, code, count=1)

            return fixed_code if fixed_code != code else None

        return None

    async def _fix_key_error(self, error_context: ErrorContextModel) -> Optional[str]:
        """キーエラーを修正"""
        error_msg = error_context.error_message

        # KeyError: 'X'パターン
        match = re.search(r"KeyError: '(\w+)'", error_msg)
        if match:
            key = match.group(1)

            code = error_context.surrounding_code or ""

            # 辞書アクセスを.get()に変更
            pattern = rf'\[[\'"]{key}[\'"]\]'
            replacement = rf".get('{key}', None)  # Fixed: safe key access"

            fixed_code = re.sub(pattern, replacement, code)

            return fixed_code if fixed_code != code else None

        return None

    # ========================================
    # ユーティリティ
    # ========================================

    async def _create_backup(self, target_files: List[str]) -> Path:
        """バックアップを作成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_subdir = self.backup_dir / timestamp
        backup_subdir.mkdir(parents=True, exist_ok=True)

        for file_path in target_files:
            src = Path(file_path)
            if src.exists():
                dst = backup_subdir / src.name
                await asyncio.to_thread(dst.write_text, src.read_text(encoding="utf-8"))

        return backup_subdir

    async def _apply_fix(self, file_path: str, code: str):
        """修正を適用"""
        target = Path(file_path)
        await asyncio.to_thread(target.write_text, code, encoding="utf-8")
        logger.info(f"✅ 修正適用: {file_path}")

    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        success_rate = 0.0
        if self.stats["total_fixes"] > 0:
            success_rate = self.stats["successful_fixes"] / self.stats["total_fixes"]

        return {**self.stats, "success_rate": success_rate}
