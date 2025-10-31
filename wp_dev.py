"""
WordPress開発タスクルーター（完全動作版）
"""

import asyncio
import logging
from typing import Dict, Optional
from pathlib import Path

from configuration.config_utils import ErrorHandler

logger = logging.getLogger(__name__)


class WordPressDevAgent:
    """WordPress開発タスクルーター（完全動作版）"""

    def __init__(self, browser, output_folder: Path = None):
        self.browser = browser
        self.output_folder = output_folder or Path("./outputs/wordpress")
        self.output_folder.mkdir(parents=True, exist_ok=True)

        # 専門エージェントの初期化
        self._init_specialized_agents()

        logger.info("✅ WordPressDevAgent 初期化完了")

    def _init_specialized_agents(self):
        """専門エージェントを初期化"""
        try:
            from wordpress.wp_dev import (
                WordPressRequirementsAgent,
                WordPressCPTAgent,
                WordPressTaxonomyAgent,
                WordPressACFAgent,
            )

            self.requirements_agent = WordPressRequirementsAgent(self.browser, self.output_folder)
            self.cpt_agent = WordPressCPTAgent(self.browser, self.output_folder)
            self.taxonomy_agent = WordPressTaxonomyAgent(self.browser, self.output_folder)
            self.acf_agent = WordPressACFAgent(self.browser, self.output_folder)

            logger.info("✅ 専門エージェント初期化完了")

        except ImportError as e:
            logger.warning(f"⚠️ インポートエラー: {e}")
            self.requirements_agent = None
            self.cpt_agent = None
            self.taxonomy_agent = None
            self.acf_agent = None

    async def execute(self, task: Dict) -> Dict:
        """
        execute メソッド（必須）
        他のエージェントとの互換性のため
        """
        return await self.process_task(task)

    async def process_task(self, task: Dict) -> Dict:
        """
        process_task メソッド（必須）
        実際のタスク処理
        """
        task_id = task.get("task_id", "UNKNOWN")
        description = task.get("description", "").lower()

        try:
            logger.info(f"🔧 WordPress開発タスク: {task_id}")

            # タスクタイプを判定
            task_type = self._determine_task_type(description)
            logger.info(f"📊 タスクタイプ: {task_type}")

            # エージェントに振り分け
            if task_type == "requirements":
                if self.requirements_agent:
                    return await self.requirements_agent.execute(task)
                else:
                    return await self._fallback_execution(task)

            elif task_type == "cpt":
                if self.cpt_agent:
                    return await self.cpt_agent.execute(task)
                else:
                    return await self._fallback_execution(task)

            elif task_type == "taxonomy":
                if self.taxonomy_agent:
                    return await self.taxonomy_agent.execute(task)
                else:
                    return await self._fallback_execution(task)

            elif task_type == "acf":
                if self.acf_agent:
                    return await self.acf_agent.execute(task)
                else:
                    return await self._fallback_execution(task)

            else:
                # フォールバック
                return await self._fallback_execution(task)

        except Exception as e:
            logger.error(f"❌ エラー: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e), "task_id": task_id}

    def _determine_task_type(self, description: str) -> str:
        """タスクタイプ判定（柔軟版）"""
        # 要件定義（デフォルト）
        requirements_patterns = [
            "要件定義",
            "requirements",
            "仕様書",
            "設計書",
            "ポータル",
            "cocoon",
            "polylang",
            "多言語",
            "m&a",
            "ウズベキスタン",
            "wordpress",
        ]

        if any(kw in description for kw in requirements_patterns):
            return "requirements"

        # CPT
        if any(kw in description for kw in ["cpt", "custom post type", "カスタム投稿", "ma_case"]):
            return "cpt"

        # タクソノミー
        if any(kw in description for kw in ["taxonomy", "タクソノミー", "カテゴリ", "industry"]):
            return "taxonomy"

        # ACF
        if any(kw in description for kw in ["acf", "advanced custom fields", "カスタムフィールド"]):
            return "acf"

        # デフォルト
        return "requirements"

    async def _fallback_execution(self, task: Dict) -> Dict:
        """フォールバック実行"""
        logger.warning("⚠️ エージェント不在 - Geminiで直接実行")

        try:
            prompt = f"""WordPressタスクを実行してください：

{task.get('description', '')}

簡潔に実装方法を説明してください。"""

            await self.browser.send_prompt(prompt)
            success = await self.browser.wait_for_text_generation(max_wait=120)

            if success:
                response = await self.browser.extract_latest_text_response()
                return {
                    "success": True,
                    "message": "フォールバック実行完了",
                    "summary": response[:300] if response else "N/A",
                    "full_text": response or "",
                }
            else:
                return {"success": False, "error": "タイムアウト"}

        except Exception as e:
            return {"success": False, "error": str(e)}
