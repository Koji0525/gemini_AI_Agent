# cloud_fix_agent.py
"""
クラウド修正エージェント
複雑なエラーをクラウドAIで修正
"""

import asyncio
import logging
import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from data_models import BugFixTask, FixResult, ErrorContextModel

logger = logging.getLogger(__name__)


class CloudFixAgent:
    """
    クラウド修正エージェント

    特徴:
    - 高性能AI（GPT-4o, Claude Opus, Gemini等）
    - 複雑なエラー対応
    - コンテキスト理解が深い
    - 大規模リファクタリング対応
    """

    def __init__(
        self,
        command_monitor,
        wp_tester=None,
        api_provider: str = "openai",  # openai, anthropic, google
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        """
        初期化

        Args:
            command_monitor: CommandMonitorAgent
            wp_tester: WordPressTester
            api_provider: APIプロバイダー
            api_key: APIキー
            model_name: モデル名（省略時はデフォルト）
        """
        self.cmd_monitor = command_monitor
        self.wp_tester = wp_tester
        self.api_provider = api_provider
        self.api_key = api_key or os.getenv(f"{api_provider.upper()}_API_KEY")

        # モデル名の設定
        self.model_name = model_name or self._get_default_model()

        # バックアップディレクトリ
        self.backup_dir = Path("./backups/cloud_fix")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # 修正履歴
        self.fix_history = []

        # 統計情報
        self.stats = {
            "total_fixes": 0,
            "successful_fixes": 0,
            "failed_fixes": 0,
            "total_api_calls": 0,
            "total_tokens_used": 0,
        }

        # クライアント初期化
        self._init_api_client()

        logger.info(f"✅ CloudFixAgent 初期化完了 (provider={api_provider}, model={self.model_name})")

    def _get_default_model(self) -> str:
        """デフォルトモデル名を取得"""
        defaults = {"openai": "gpt-4o", "anthropic": "claude-opus-4", "google": "gemini-2.0-flash-exp"}
        return defaults.get(self.api_provider, "gpt-4o")

    def _init_api_client(self):
        """APIクライアントを初期化"""
        # .env から API キーを読み込む
        import os
        from dotenv import load_dotenv

        load_dotenv(override=True)

        # API キーが設定されていない場合は環境変数から取得
        if not self.api_key:
            self.api_key = os.getenv("OPENAI_API_KEY")

        if self.api_provider == "openai":
            try:
                import openai

                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info(f"✅ OpenAI API クライアント初期化完了 (model={self.model_name})")
            except ImportError:
                logger.error("❌ openai パッケージがインストールされていません")
                self.client = None

        elif self.api_provider == "anthropic":
            try:
                import anthropic

                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info(f"✅ Anthropic API クライアント初期化完了 (model={self.model_name})")
            except ImportError:
                logger.error("❌ anthropic パッケージがインストールされていません")
                self.client = None

        elif self.api_provider == "google":
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model_name)
                logger.info(f"✅ Google Gemini API クライアント初期化完了 (model={self.model_name})")
            except ImportError:
                logger.error("❌ google-generativeai パッケージがインストールされていません")
                self.client = None

    async def execute_bug_fix_task(self, bug_fix_task: BugFixTask) -> FixResult:
        """
        バグ修正タスクを実行（クラウドAI使用）

        Args:
            bug_fix_task: バグ修正タスク

        Returns:
            FixResult: 修正結果
        """
        start_time = datetime.now()
        task_id = bug_fix_task.task_id

        try:
            logger.info("=" * 60)
            logger.info(f"☁️ クラウドバグ修正タスク実行: {task_id}")
            logger.info("=" * 60)

            self.stats["total_fixes"] += 1

            # 1. 詳細な修正プロンプトを構築
            fix_prompt = self._build_detailed_fix_prompt(bug_fix_task.error_context)
            logger.info(f"📝 詳細プロンプト構築完了 ({len(fix_prompt)}文字)")

            # 2. クラウドAIに修正を依頼
            ai_result = await self._request_cloud_ai_fix(fix_prompt)

            if not ai_result["success"]:
                self.stats["failed_fixes"] += 1
                return self._create_failed_result(
                    task_id, f"クラウドAI修正依頼失敗: {ai_result.get('error')}", start_time
                )

            generated_code = ai_result["generated_code"]
            modified_files = ai_result.get("modified_files", bug_fix_task.target_files)
            confidence = ai_result.get("confidence", 0.0)
            reasoning = ai_result.get("reasoning", "")

            logger.info(f"🤖 クラウドAI修正コード取得 ({len(generated_code)}文字, 信頼度={confidence})")

            # 3. バックアップ作成
            backup_path = await self._create_backup(bug_fix_task.target_files)
            logger.info(f"💾 バックアップ作成: {backup_path}")

            # 4. 修正コードを適用
            apply_result = await self._apply_fix_code(modified_files, generated_code)

            if not apply_result["success"]:
                self.stats["failed_fixes"] += 1
                return self._create_failed_result(
                    task_id, f"修正コード適用失敗: {apply_result.get('error')}", start_time
                )

            # 5. テスト実行（オプション）
            test_passed = True
            if self.wp_tester and getattr(bug_fix_task, "run_tests", False):
                test_result = await self._run_tests(bug_fix_task)
                test_passed = test_result["success"]

                if not test_passed:
                    logger.warning(f"⚠️ テスト失敗: {test_result.get('error')}")
                    # バックアップから復元
                    await self._restore_from_backup(backup_path)
                    self.stats["failed_fixes"] += 1
                    return self._create_failed_result(task_id, f"テスト失敗: {test_result.get('error')}", start_time)

            execution_time = (datetime.now() - start_time).total_seconds()

            # 修正履歴に追加
            self.fix_history.append(
                {
                    "task_id": task_id,
                    "timestamp": datetime.now().isoformat(),
                    "provider": self.api_provider,
                    "model": self.model_name,
                    "confidence": confidence,
                    "success": True,
                    "execution_time": execution_time,
                }
            )

            self.stats["successful_fixes"] += 1

            logger.info(f"✅ クラウド修正完了: {task_id} ({execution_time:.2f}秒)")

            return FixResult(
                task_id=task_id,
                success=True,
                modified_files=modified_files,
                generated_code=generated_code,
                test_passed=test_passed,
                execution_time=execution_time,
                confidence_score=confidence,
                reasoning=reasoning,
                backup_path=str(backup_path),
            )

        except Exception as e:
            logger.error(f"💥 クラウド修正エラー: {e}", exc_info=True)
            self.stats["failed_fixes"] += 1
            return self._create_failed_result(task_id, str(e), start_time)

    def _build_detailed_fix_prompt(self, error_context: ErrorContextModel) -> str:
        """
        クラウドAI用の詳細なプロンプトを構築

        Args:
            error_context: エラーコンテキスト

        Returns:
            str: 詳細な修正プロンプト
        """
        prompt_parts = []

        # システムプロンプト
        prompt_parts.append(
            """あなたは熟練したPython開発者であり、エラー修正のエキスパートです。
以下のエラーを分析し、最適な修正コードを生成してください。

## 出力形式
以下のJSON形式で出力してください：

```json
{
    "analysis": "エラーの詳細な分析",
    "root_cause": "根本原因",
    "fix_strategy": "修正戦略",
    "modified_files": {
        "ファイルパス1": "完全な修正後のコード",
        "ファイルパス2": "完全な修正後のコード"
    },
    "confidence": 0.95,
    "reasoning": "この修正を選んだ理由",
    "test_suggestions": ["テストケース1", "テストケース2"],
    "potential_side_effects": ["副作用1", "副作用2"]
}
```
"""
        )
        prompt_parts.append("")

        # エラー情報（詳細）
        prompt_parts.append("=" * 60)
        prompt_parts.append("【エラー情報】")
        prompt_parts.append("=" * 60)
        prompt_parts.append(f"エラータイプ: {error_context.error_type}")
        prompt_parts.append(f"エラーメッセージ: {error_context.error_message}")
        prompt_parts.append(f"深刻度: {error_context.severity.value}")
        prompt_parts.append(f"カテゴリ: {error_context.error_category.value}")
        prompt_parts.append(
            f"発生ファイル: {(error_context.error_location.file_path if error_context.error_location else "unknown")}:{(error_context.error_location.line_number if error_context.error_location else 0)}"
        )
        prompt_parts.append("")

        # スタックトレース（全体）
        if error_context.full_traceback:
            prompt_parts.append("【完全なスタックトレース】")
            prompt_parts.append("```python")
            prompt_parts.append(error_context.full_traceback)
            prompt_parts.append("```")
            prompt_parts.append("")

        # 周辺コード（詳細）
        if error_context.surrounding_code:
            prompt_parts.append("【周辺コード（前後10行）】")
            prompt_parts.append("```python")
            prompt_parts.append(error_context.surrounding_code)
            prompt_parts.append("```")
            prompt_parts.append("")

        # ローカル変数（全体）
        if error_context.local_variables:
            prompt_parts.append("【ローカル変数の状態】")
            prompt_parts.append("```python")
            for var_name, var_value in error_context.local_variables.items():
                prompt_parts.append(f"{var_name} = {var_value}")
            prompt_parts.append("```")
            prompt_parts.append("")

        # コンテキスト情報
        if hasattr(error_context, "context_info") and error_context.context_info:
            prompt_parts.append("【追加コンテキスト】")
            for key, value in getattr(error_context, "context_info", {}).items():
                prompt_parts.append(f"- {key}: {value}")
            prompt_parts.append("")

        # 過去の修正履歴（参考）
        if self.fix_history:
            prompt_parts.append("【過去の修正履歴（参考）】")
            recent_fixes = self.fix_history[-3:]  # 直近3件
            for fix in recent_fixes:
                if fix.get("success"):
                    prompt_parts.append(f"- {fix['task_id']}: 成功 (信頼度={fix.get('confidence', 'N/A')})")
            prompt_parts.append("")

        prompt_parts.append("=" * 60)
        prompt_parts.append("上記の情報を基に、最適な修正コードをJSON形式で提供してください。")
        prompt_parts.append("=" * 60)

        return "\n".join(prompt_parts)

    async def _request_cloud_ai_fix(self, prompt: str) -> Dict[str, Any]:
        """
        クラウドAIに修正を依頼

        Args:
            prompt: 修正プロンプト

        Returns:
            Dict: AI応答結果
        """
        try:
            self.stats["total_api_calls"] += 1

            if self.api_provider == "openai":
                return await self._request_openai(prompt)
            elif self.api_provider == "anthropic":
                return await self._request_anthropic(prompt)
            elif self.api_provider == "google":
                return await self._request_google(prompt)
            else:
                return {"success": False, "error": f"未サポートのプロバイダー: {self.api_provider}"}

        except Exception as e:
            logger.error(f"❌ AI API呼び出しエラー: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def _request_openai(self, prompt: str) -> Dict[str, Any]:
        """OpenAI APIにリクエスト"""
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "あなたは熟練したPython開発者です。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            self.stats["total_tokens_used"] += response.usage.total_tokens

            result = json.loads(content)

            return {
                "success": True,
                "generated_code": result.get("modified_files", {}),
                "modified_files": list(result.get("modified_files", {}).keys()),
                "confidence": result.get("confidence", 0.8),
                "reasoning": result.get("reasoning", ""),
                "analysis": result.get("analysis", ""),
                "test_suggestions": result.get("test_suggestions", []),
            }

        except Exception as e:
            logger.error(f"❌ OpenAI API エラー: {e}")
            return {"success": False, "error": str(e)}

    async def _request_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Anthropic APIにリクエスト"""
        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=self.model_name,
                max_tokens=4096,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text
            self.stats["total_tokens_used"] += response.usage.input_tokens + response.usage.output_tokens

            result = json.loads(content)

            return {
                "success": True,
                "generated_code": result.get("modified_files", {}),
                "modified_files": list(result.get("modified_files", {}).keys()),
                "confidence": result.get("confidence", 0.8),
                "reasoning": result.get("reasoning", ""),
                "analysis": result.get("analysis", ""),
            }

        except Exception as e:
            logger.error(f"❌ Anthropic API エラー: {e}")
            return {"success": False, "error": str(e)}

    async def _request_google(self, prompt: str) -> Dict[str, Any]:
        """Google Gemini APIにリクエスト"""
        try:
            response = await asyncio.to_thread(
                self.client.generate_content,
                prompt,
                generation_config={"temperature": 0.3, "response_mime_type": "application/json"},
            )

            content = response.text
            result = json.loads(content)

            return {
                "success": True,
                "generated_code": result.get("modified_files", {}),
                "modified_files": list(result.get("modified_files", {}).keys()),
                "confidence": result.get("confidence", 0.8),
                "reasoning": result.get("reasoning", ""),
            }

        except Exception as e:
            logger.error(f"❌ Google Gemini API エラー: {e}")
            return {"success": False, "error": str(e)}

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

    async def _apply_fix_code(self, modified_files: Dict[str, str], code: str) -> Dict[str, Any]:
        """修正コードを適用"""
        try:
            if isinstance(code, dict):
                # 辞書形式（ファイルパス: コード）
                for file_path, file_code in code.items():
                    target = Path(file_path)
                    await asyncio.to_thread(target.write_text, file_code, encoding="utf-8")
                    logger.info(f"✅ 修正適用: {file_path}")
            else:
                # 単一コード
                if modified_files:
                    target = Path(modified_files[0])
                    await asyncio.to_thread(target.write_text, code, encoding="utf-8")
                    logger.info(f"✅ 修正適用: {modified_files[0]}")

            return {"success": True}

        except Exception as e:
            logger.error(f"❌ 修正コード適用エラー: {e}")
            return {"success": False, "error": str(e)}

    async def _restore_from_backup(self, backup_path: Path):
        """バックアップから復元"""
        try:
            for backup_file in backup_path.glob("*"):
                # 元のファイルパスを推定（簡易版）
                original_path = Path(backup_file.name)
                if original_path.exists():
                    content = await asyncio.to_thread(backup_file.read_text, encoding="utf-8")
                    await asyncio.to_thread(original_path.write_text, content, encoding="utf-8")
                    logger.info(f"♻️ バックアップから復元: {original_path}")
        except Exception as e:
            logger.error(f"❌ バックアップ復元エラー: {e}")

    async def _run_tests(self, bug_fix_task: BugFixTask) -> Dict[str, Any]:
        """テストを実行"""
        if not self.wp_tester:
            return {"success": True, "message": "テスター未設定"}

        try:
            test_result = await self.wp_tester.run_tests(bug_fix_task.task_id)
            return {
                "success": test_result.get("passed", False),
                "error": test_result.get("error") if not test_result.get("passed") else None,
            }
        except Exception as e:
            logger.error(f"❌ テスト実行エラー: {e}")
            return {"success": False, "error": str(e)}

    def _create_failed_result(self, task_id: str, error_message: str, start_time: datetime) -> FixResult:
        """失敗結果を作成"""
        execution_time = (datetime.now() - start_time).total_seconds()

        return FixResult(
            task_id=task_id,
            success=False,
            modified_files=[],
            generated_code="",
            test_passed=False,
            execution_time=execution_time,
            error_message=error_message,
            confidence_score=0.0,
        )

    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        success_rate = 0.0
        if self.stats["total_fixes"] > 0:
            success_rate = self.stats["successful_fixes"] / self.stats["total_fixes"]

        return {**self.stats, "success_rate": success_rate, "provider": self.api_provider, "model": self.model_name}
