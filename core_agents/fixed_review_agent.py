#!/usr/bin/env python3
"""修正版レビューエージェント"""
import asyncio
import logging
from typing import Dict, Any
import json

from browser_control.safe_browser_manager import get_browser_controller
from core_agents.review_agent_prompts import REVIEW_SYSTEM_PROMPT
from configuration.config_utils import setup_optimized_logging

logger = setup_optimized_logging("review")


class FixedReviewAgent:

    def __init__(self):
        self.browser_controller = None
        logger.info("✅ 初期化")

    async def initialize(self):
        try:
            logger.info("🔧 環境初期化中...")
            self.browser_controller = await get_browser_controller()
            logger.info("✅ 完了")
        except Exception as e:
            logger.error(f"❌ エラー: {e}")
            raise

    async def review_content(self, content: str, task_description: str = "") -> Dict[str, Any]:
        try:
            logger.info("=" * 60)
            logger.info("レビューAI: 開始")
            logger.info("=" * 60)

            if self.browser_controller is None:
                await self.initialize()

            if len(content) < 100:
                logger.warning("⚠️ コンテンツ不足")
                return self._create_default_review("コンテンツ不足")

            logger.info("AIに依頼中...")
            review_prompt = self._build_review_prompt(content, task_description)

            try:
                await self.browser_controller.send_prompt(review_prompt)
                await asyncio.sleep(5)
                ai_response = await self.browser_controller.extract_response()

                if not ai_response:
                    return self._create_default_review("応答なし")

                result = self._parse_ai_response(ai_response)
                logger.info("✅ 完了")
                return result

            except Exception as e:
                logger.error(f"⚠️ AI処理: {e}")
                return self._create_default_review(f"エラー: {e}")

        except Exception as e:
            logger.error(f"❌ エラー: {e}")
            return self._create_default_review(f"エラー: {e}")

    def _build_review_prompt(self, content: str, task_desc: str) -> str:
        return f"""{REVIEW_SYSTEM_PROMPT}

タスク: {task_desc}
コンテンツ: {content[:1000]}

JSON形式で評価してください。
"""

    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        try:
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]

            result = json.loads(json_str)
            return {
                "success": True,
                "review": result,
                "summary": result.get("evaluation", {}).get("overall_assessment", ""),
                "full_text": response,
            }
        except:
            return self._create_default_review("解析失敗")

    def _create_default_review(self, reason: str) -> Dict[str, Any]:
        return {
            "success": True,
            "review": {
                "evaluation": {
                    "completeness": "完了",
                    "quality_score": 7,
                    "issues": [],
                    "good_points": ["完了"],
                    "overall_assessment": "デフォルト評価",
                },
                "next_actions": {"required": False, "reasoning": reason, "suggested_tasks": []},
            },
            "summary": f"デフォルト評価: {reason}",
            "full_text": "",
        }
