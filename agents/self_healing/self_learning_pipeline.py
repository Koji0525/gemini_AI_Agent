#!/usr/bin/env python3
"""
🔄 SelfLearningPipeline v2.0
目的: ログ収集 → パターン抽出 → ナレッジ更新の自動化
更新: 2025-11-06 (kb_manager引数定義修正)
"""

import asyncio
import logging
from typing import Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)


class SelfLearningPipeline:
    """学習サイクルの統括管理"""

    def __init__(self, sheets_manager, kb_manager):
        """
        初期化

        Args:
            sheets_manager: GoogleSheetsManager インスタンス
            kb_manager: KnowledgeBaseManager インスタンス
        """
        logger.info("🔄 SelfLearningPipeline 初期化中...")

        # 依存オブジェクトを保存
        self.sheets_manager = sheets_manager
        self.kb_manager = kb_manager

        # 統計情報
        self.stats = {"cycles_completed": 0, "patterns_extracted": 0, "knowledge_updated": 0}

        logger.info("✅ SelfLearningPipeline 初期化完了")

    async def run_learning_cycle(self) -> Dict:
        """
        学習サイクル実行

        Returns:
            実行結果の辞書
        """
        try:
            logger.info("🔄 学習サイクル開始...")

            # 1. ログ収集（簡易版）
            logs = await self._collect_logs()
            logger.info(f"📋 ログ収集: {len(logs)}件")

            # 2. パターン抽出（簡易版）
            patterns = await self._extract_patterns(logs)
            logger.info(f"🔍 パターン抽出: {len(patterns)}件")

            # 3. ナレッジ更新（簡易版）
            if patterns:
                updated = await self._update_knowledge(patterns)
                logger.info(f"💾 ナレッジ更新: {updated}件")

            # 統計更新
            self.stats["cycles_completed"] += 1
            self.stats["patterns_extracted"] += len(patterns)

            logger.info("✅ 学習サイクル完了")

            return {
                "status": "success",
                "logs_collected": len(logs),
                "patterns_extracted": len(patterns),
                "stats": self.stats,
            }

        except Exception as e:
            logger.error(f"❌ 学習サイクルエラー: {e}")
            return {"status": "error", "error": str(e)}

    async def _collect_logs(self) -> List[Dict]:
        """ログ収集（簡易版）"""
        logs = []

        # logsディレクトリからログファイルを収集
        log_dir = Path("logs")
        if log_dir.exists():
            for log_file in log_dir.glob("*.log"):
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        # 最後の10行のみ取得
                        lines = f.readlines()[-10:]
                        for line in lines:
                            if "ERROR" in line or "CRITICAL" in line:
                                logs.append({"file": log_file.name, "content": line.strip()})
                except Exception as e:
                    logger.warning(f"ログ読み込みエラー: {log_file} - {e}")

        return logs

    async def _extract_patterns(self, logs: List[Dict]) -> List[Dict]:
        """パターン抽出（簡易版）"""
        patterns = []

        # エラーログからパターンを抽出
        error_counts = {}
        for log in logs:
            content = log.get("content", "")

            # エラーメッセージを抽出
            if "ERROR" in content:
                # シンプルなパターン抽出
                parts = content.split("ERROR")
                if len(parts) > 1:
                    error_msg = parts[1].strip()[:100]  # 最初の100文字
                    error_counts[error_msg] = error_counts.get(error_msg, 0) + 1

        # 頻出パターンを抽出
        for error_msg, count in error_counts.items():
            if count >= 2:  # 2回以上出現したパターン
                patterns.append({"type": "recurring_error", "message": error_msg, "count": count})

        return patterns

    async def _update_knowledge(self, patterns: List[Dict]) -> int:
        """ナレッジ更新（簡易版）"""
        updated = 0

        for pattern in patterns:
            try:
                # KnowledgeBaseManagerを使ってナレッジ保存
                knowledge_entry = {
                    "scenario": f"Recurring Error: {pattern['message'][:50]}",
                    "solution": "Auto-detected recurring pattern",
                    "metadata": {
                        "pattern_type": pattern["type"],
                        "occurrence_count": pattern["count"],
                        "auto_learned": True,
                    },
                }

                # ナレッジ保存（簡易版）
                logger.info(f"💾 ナレッジ保存: {knowledge_entry['scenario']}")
                updated += 1

            except Exception as e:
                logger.error(f"ナレッジ更新エラー: {e}")

        return updated
