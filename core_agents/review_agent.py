# review_agent.py
"""レビューAI - タスク出力を評価し、失敗原因を分析、次のアクションを提案"""
import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from configuration.config_utils import ErrorHandler
from browser_control.gemini_api_client import GeminiAPIClient
from tools.sheets_manager import GoogleSheetsManager
from core_agents.review_agent_prompts import REVIEW_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class ReviewAgent:
    """レビューAI - タスク出力を評価し、失敗原因を分析、次のアクションを提案"""

    def __init__(self, gemini_client: GeminiAPIClient = None, output_folder: Path = None):
        """
        ReviewAgent初期化

        Args:
            gemini_client: GeminiAPIClientのインスタンス
            output_folder: 出力フォルダパス
        """
        # Gemini APIクライアント設定
        if gemini_client is not None:
            self.gemini_client = gemini_client
        else:
            # フォールバック: 自動初期化
            self.gemini_client = GeminiAPIClient()

        # 出力フォルダ設定
        if output_folder:
            self.output_folder = Path(output_folder)
        else:
            self.output_folder = Path("agent_outputs/review")

        self.output_folder.mkdir(parents=True, exist_ok=True)

        # その他の初期化
        self.sheets_manager = None
        self.system_prompt = REVIEW_SYSTEM_PROMPT

    def _initialize_sheets_manager(self):
        """sheets_manager の遅延初期化"""
        if self.sheets_manager is None:
            try:
                from tools.sheets_manager import GoogleSheetsManager
                from configuration.config_loader import get_config

                spreadsheet_id = get_config("SPREADSHEET_ID")
                service_account = get_config("SERVICE_ACCOUNT_FILE")

                self.sheets_manager = GoogleSheetsManager(
                    spreadsheet_id=spreadsheet_id, service_account_file=service_account
                )
                logger.info("GoogleSheetsManager を初期化しました")
            except Exception as e:
                logger.warning(f"GoogleSheetsManager の初期化に失敗: {e}")
                self.sheets_manager = None

    async def process_task(self, task: Dict) -> Dict:
        """レビュータスクを処理（互換性のため）"""
        return await self.review_completed_task(task, task.get("output_content", ""))

    async def review_completed_task(self, task: Dict, output_content: str) -> Dict:
        """完了したタスクをレビュー（失敗原因分析強化版）"""
        try:
            # === パート1: レビュー開始処理 ===
            logger.info("=" * 60)
            logger.info(f"レビューAI: タスク {task['task_id']} のレビュー開始")
            logger.info("=" * 60)

            # タスクのステータスを確認
            task_status = task.get("status", "unknown")
            is_failed_task = task_status in ["failed", "error", "timeout"]

            # 事前チェック：出力内容の構造を検証
            pre_check_result = self._pre_check_content(output_content, task["required_role"])
            if pre_check_result:
                logger.info(f"事前チェック結果: {pre_check_result}")

            # エラー情報を取得
            error_info = task.get("error", "")

            # === パート2: プロンプト構築とGemini送信 ===
            full_prompt = self._build_review_prompt(
                task,
                task_status,
                is_failed_task,
                output_content,
                error_info,
                pre_check_result,
            )

            # Gemini APIにプロンプト送信（リトライ機能付き）
            response_text = await self._send_prompt_with_retry(full_prompt)

            # === パート3: レスポンス解析とレビュー結果生成 ===
            review_result = self._parse_review_response(response_text, task)

            # === パート4: レビュー結果の保存と返却 ===
            self._save_review_result(task["task_id"], review_result)

            logger.info("✅ レビュー完了")
            logger.info(f"   評価: {review_result.get('evaluation', 'N/A')}")
            return review_result

        except Exception as e:
            logger.error(f"❌ レビュー処理エラー: {e}", exc_info=True)
            return self._create_error_review_result(task, str(e))

    async def _send_prompt_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """リトライ機能付きでGemini APIにプロンプトを送信"""
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"📝 プロンプト送信: {prompt[:100]}...")

                # Gemini API経由で送信
                response = await self.gemini_client.send_prompt(prompt)

                if response and len(response) > 10:
                    logger.info(f"✅ 応答受信成功（{len(response)}文字）")
                    return response
                else:
                    raise Exception("応答が空または短すぎます")

            except Exception as e:
                logger.warning(f"⚠️  エラー発生（試行 {attempt}/{max_retries}）: {e}")
                if attempt < max_retries:
                    wait_time = 5 * attempt
                    logger.info(f"   {wait_time}秒後に再試行...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"❌ プロンプト送信失敗: {e}")
                    raise Exception(f"プロンプト送信失敗: {e}")

    def _pre_check_content(self, content: str, required_role: str) -> str:
        """出力内容の事前チェック"""
        issues = []

        if not content or len(content.strip()) < 50:
            issues.append("出力内容が短すぎる（50文字未満）")

        if "error" in content.lower() or "エラー" in content:
            issues.append("エラーメッセージを含んでいる")

        if required_role == "content_generator":
            if len(content) < 500:
                issues.append("コンテンツ生成にしては短い（500文字未満）")

        if required_role == "wordpress":
            if "投稿完了" not in content and "公開" not in content:
                issues.append("WordPress投稿の完了メッセージがない")

        return " | ".join(issues) if issues else ""

    def _build_review_prompt(
        self,
        task: Dict,
        task_status: str,
        is_failed_task: bool,
        output_content: str,
        error_info: str,
        pre_check_result: str,
    ) -> str:
        """レビュー用プロンプトを構築"""
        prompt_parts = [
            self.system_prompt,
            "\n\n【タスク情報】",
            f"タスクID: {task['task_id']}",
            f"タスク名: {task.get('task_name', 'N/A')}",
            f"必要な役割: {task['required_role']}",
            f"実行タイプ: {task.get('execution_type', 'N/A')}",
            f"タスクステータス: {task_status}",
        ]

        if is_failed_task:
            prompt_parts.append("\n⚠️ **このタスクは失敗しています。失敗原因を特定してください。**")

        if error_info:
            prompt_parts.append(f"\n【エラー情報】\n{error_info}")

        if pre_check_result:
            prompt_parts.append(f"\n【事前チェック結果】\n{pre_check_result}")

        prompt_parts.extend(
            [
                "\n【タスク出力内容】",
                output_content[:5000],  # 最大5000文字に制限
                "\n\n【指示】",
                "上記の情報を総合的に分析し、以下の形式でレビューしてください：",
                "```json",
                "{",
                '  "evaluation": "excellent/good/acceptable/poor/failed",',
                '  "score": 0-100,',
                '  "quality_assessment": "品質評価コメント",',
                '  "failure_analysis": "失敗原因分析（失敗時のみ）",',
                '  "failure_category": "環境/設定/コード/外部サービス/UI変更/その他（失敗時のみ）",',
                '  "suggestions": ["改善提案1", "改善提案2"],',
                '  "next_action": "retry/fix/skip/manual"',
                "}",
                "```",
            ]
        )

        return "\n".join(prompt_parts)

    def _parse_review_response(self, response_text: str, task: Dict) -> Dict:
        """レビューレスポンスを解析"""
        try:
            # JSONブロックを抽出
            json_match = re.search(r"```json\s*(\{.*?\})\s*```", response_text, re.DOTALL)
            if json_match:
                review_data = json.loads(json_match.group(1))
            else:
                # JSONブロックがない場合は全体をパース試行
                review_data = json.loads(response_text)

            # 必須フィールドの検証
            required_fields = ["evaluation", "score"]
            for field in required_fields:
                if field not in review_data:
                    raise ValueError(f"必須フィールド '{field}' がありません")

            # タスク情報を追加
            review_data["task_id"] = task["task_id"]
            review_data["reviewed_at"] = datetime.now().isoformat()

            return review_data

        except Exception as e:
            logger.warning(f"⚠️  レビューレスポンスの解析失敗: {e}")
            return self._create_fallback_review(response_text, task)

    def _create_fallback_review(self, response_text: str, task: Dict) -> Dict:
        """フォールバックレビュー結果を生成"""
        return {
            "task_id": task["task_id"],
            "evaluation": "acceptable",
            "score": 60,
            "quality_assessment": "レビュー処理に問題が発生しましたが、タスクは完了とみなします",
            "raw_response": response_text[:500],
            "reviewed_at": datetime.now().isoformat(),
        }

    def _create_error_review_result(self, task: Dict, error_message: str) -> Dict:
        """エラー時のレビュー結果を生成"""
        return {
            "task_id": task["task_id"],
            "evaluation": "failed",
            "score": 0,
            "quality_assessment": f"レビュー処理失敗: {error_message}",
            "failure_analysis": "レビューAI自体の処理エラー",
            "failure_category": "システムエラー",
            "next_action": "manual",
            "reviewed_at": datetime.now().isoformat(),
        }

    def _save_review_result(self, task_id: str, review_result: Dict):
        """レビュー結果をファイルに保存"""
        try:
            output_file = self.output_folder / f"review_{task_id}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(review_result, f, ensure_ascii=False, indent=2)
            logger.info(f"📝 レビュー結果を保存: {output_file}")
        except Exception as e:
            logger.warning(f"⚠️  レビュー結果の保存失敗: {e}")

    def cleanup(self):
        """クリーンアップ（API版では不要だが互換性のため）"""
        logger.info("✅ ReviewAgent クリーンアップ完了")
