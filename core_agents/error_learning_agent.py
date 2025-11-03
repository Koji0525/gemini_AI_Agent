#!/usr/bin/env python3
"""
エラー学習エージェント
過去のエラーログから学習してナレッジベースに蓄積
"""

import asyncio
from datetime import datetime
from typing import List, Dict
from pathlib import Path
import hashlib

from browser_control.sheets_manager import GoogleSheetsManager
from agents.self_healing.error_classifier import ErrorClassifier


class ErrorLearningAgent:
    """エラー学習エージェント"""

    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets = sheets_manager
        self.classifier = ErrorClassifier()

    async def analyze_error_logs(self, log_file: str = "logs/autonomous_24h.log"):
        """エラーログ分析"""
        print("\n🔍 エラーログ分析開始...")

        # ログファイル読み込み
        log_path = Path(log_file)
        if not log_path.exists():
            print(f"❌ ログファイルなし: {log_file}")
            return

        content = log_path.read_text()

        # エラー行抽出
        error_lines = [line for line in content.split("\n") if "ERROR" in line or "❌" in line]

        print(f"📊 エラー行数: {len(error_lines)}")

        # パターン抽出
        patterns = self._extract_patterns(error_lines)

        # ナレッジベースに保存
        await self._save_patterns(patterns)

    def _extract_patterns(self, error_lines: List[str]) -> List[Dict]:
        """エラーパターン抽出"""
        patterns = {}

        for line in error_lines:
            # エラータイプ分類
            error_type = self.classifier.classify(line)

            # エラーメッセージ抽出（簡略版）
            error_msg = line.split("ERROR")[-1].strip()[:100]

            # パターンID生成
            pattern_id = hashlib.md5(f"{error_type}{error_msg}".encode()).hexdigest()[:8]

            if pattern_id not in patterns:
                patterns[pattern_id] = {
                    "pattern_id": pattern_id,
                    "error_type": error_type,
                    "error_message": error_msg,
                    "frequency": 0,
                    "first_seen": datetime.now().isoformat(),
                    "last_seen": None,
                }

            patterns[pattern_id]["frequency"] += 1
            patterns[pattern_id]["last_seen"] = datetime.now().isoformat()

        return list(patterns.values())

    async def _save_patterns(self, patterns: List[Dict]):
        """パターンをナレッジベースに保存"""
        if not patterns:
            print("⚠️ 保存するパターンなし")
            return

        print(f"\n💾 {len(patterns)}件のパターンを保存中...")

        # 既存データ取得
        existing = self.sheets.read_range("error_patterns!A2:H")
        next_row = len(existing) + 2

        # 新規パターンを追加
        for pattern in patterns:
            values = [
                [
                    pattern["pattern_id"],
                    pattern["error_type"],
                    pattern["error_message"],
                    pattern["frequency"],
                    pattern["first_seen"],
                    pattern["last_seen"],
                    "",  # resolution_recipe（後で追加）
                    "",  # success_rate（後で追加）
                ]
            ]

            self.sheets.update_range(f"error_patterns!A{next_row}:H{next_row}", values)
            next_row += 1

        print("✅ 保存完了")


async def main():
    """テスト実行"""
    from configuration.config_loader import load_config

    config = load_config()
    sheets = GoogleSheetsManager(config["spreadsheet_id"])

    agent = ErrorLearningAgent(sheets)
    await agent.analyze_error_logs()


if __name__ == "__main__":
    asyncio.run(main())
