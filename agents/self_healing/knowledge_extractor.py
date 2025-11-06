"""
ナレッジ抽出・整理スクリプト

【何が起きた】
knowledge_baseが「過去ログ」で重複が多い

【原因】
ログをそのまま蓄積しているだけで品質管理なし

【狙い】
- 重複排除
- 要約処理
- actionable_knowledgeシートへの整理
"""

import asyncio
from collections import defaultdict
from datetime import datetime
from tools.sheets_manager import GoogleSheetsManager
import os


class KnowledgeExtractor:
    def __init__(self, sheets_manager):
        self.sheets = sheets_manager

    async def extract_actionable_knowledge(self):
        """
        knowledge_baseから実用的なナレッジを抽出
        """
        print("🔍 ナレッジ抽出開始...")

        # 1. 生ログ取得（knowledge_base）
        raw_logs = await self.sheets.read_range("knowledge_base", "A2:F1500")
        print(f"   取得: {len(raw_logs)}件の生ログ")

        # 2. タスクタイプごとにグループ化
        grouped = defaultdict(list)
        for row in raw_logs:
            if not row or len(row) < 3:
                continue

            task_type = row[2] if len(row) > 2 else "unknown"
            grouped[task_type].append(row)

        print(f"   グループ化: {len(grouped)}種類のタスク")

        # 3. 各グループから代表的なナレッジを抽出
        actionable_knowledge = []
        knowledge_id = 1

        for task_type, logs in grouped.items():
            # 重複排除（パターンが同じものをまとめる）
            pattern_groups = defaultdict(list)
            for log in logs:
                pattern = log[4] if len(row) > 4 else ""
                pattern_groups[pattern].append(log)

            # 各パターンから代表的なナレッジを生成
            for pattern, pattern_logs in pattern_groups.items():
                if len(pattern_logs) < 3:  # 3件未満は信頼度低いのでスキップ
                    continue

                # ベストプラクティスを抽出
                best_practice = self._extract_best_practice(pattern_logs)

                # 成功率を計算（仮実装）
                success_rate = 0.8  # TODO: 実際の成功率を計算

                # 平均実行時間（仮実装）
                avg_time = 120  # TODO: 実際の実行時間を計算

                actionable = {
                    "knowledge_id": f"AK_{knowledge_id:04d}",
                    "task_type": task_type,
                    "scenario": pattern[:100],  # 100文字まで
                    "best_practice": best_practice,
                    "success_rate": success_rate,
                    "avg_time": avg_time,
                    "conditions": "",  # TODO: 条件抽出
                    "avoid_patterns": "",  # TODO: 失敗パターン抽出
                    "related_agents": task_type,
                    "confidence": len(pattern_logs) / 100,  # データ数から信頼度算出
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source_count": len(pattern_logs),
                }

                actionable_knowledge.append(actionable)
                knowledge_id += 1

        print(f"✅ 抽出完了: {len(actionable_knowledge)}件の実用ナレッジ")

        # 4. actionable_knowledgeシートに書き込み
        await self._save_to_actionable_sheet(actionable_knowledge)

        return actionable_knowledge

    def _extract_best_practice(self, logs):
        """ベストプラクティスを抽出（簡易版）"""
        # TODO: より高度な抽出ロジック実装
        if logs:
            return logs[0][5][:200] if len(logs[0]) > 5 else "N/A"
        return "N/A"

    async def _save_to_actionable_sheet(self, knowledge_list):
        """actionable_knowledgeシートに保存"""
        if not knowledge_list:
            return

        # 行データに変換
        rows = []
        for k in knowledge_list:
            row = [
                k["knowledge_id"],
                k["task_type"],
                k["scenario"],
                k["best_practice"],
                k["success_rate"],
                k["avg_time"],
                k["conditions"],
                k["avoid_patterns"],
                k["related_agents"],
                k["confidence"],
                k["last_updated"],
                k["source_count"],
            ]
            rows.append(row)

        # 一括書き込み

        # 標準環境変数ローダー（自動追加）import sysfrom pathlib import Pathsys.path.insert(0, str(Path(__file__).parent.parent))from tools.env_loader import StandardEnvLoaderif not StandardEnvLoader.load_and_verify():    print("環境変数の読み込みに失敗しました")    sys.exit(1)
        try:
            await self.sheets.append_rows("actionable_knowledge", rows)
            print(f"✅ actionable_knowledgeシートに{len(rows)}件書き込み完了")
        except Exception as e:
            print(f"⚠️  書き込みエラー: {e}")


async def main():
    """テスト実行"""
    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    sheets = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)

    extractor = KnowledgeExtractor(sheets)
    await extractor.extract_actionable_knowledge()


if __name__ == "__main__":
    asyncio.run(main())
