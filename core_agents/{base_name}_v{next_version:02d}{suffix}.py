"""
PMAgentV33Epic - task_ID連番版

【修正内容】
- task_idを数字連番に変更（既存の最大値+1から採番）
- 例: 388, 389, 390, ...
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
from tools.sheets_manager import GoogleSheetsManager


class StoryGenerator:
    """ストーリー生成クラス"""

    def __init__(self, epic: Dict[str, Any], start_task_id: int):
        self.epic = epic
        self.epic_id = epic.get("goal_id", "UNKNOWN")
        self.start_task_id = start_task_id
        self.stories: List[Dict[str, Any]] = []

    def generate_stories(self) -> List[Dict[str, Any]]:
        """エピックからストーリーを生成"""
        self.epic.get("goal_description", "")

        # 簡易的に5つのストーリーに分解
        story_titles = [
            "要件定義と設計",
            "基盤実装",
            "コア機能実装",
            "テストと品質保証",
            "デプロイと運用準備",
        ]

        self.stories = []
        current_task_id = self.start_task_id

        for i, title in enumerate(story_titles, 1):
            story = {
                "task_id": str(current_task_id),  # 数字連番
                "epic_id": self.epic_id,
                "title": title,
                "description": f"{title}フェーズの実装",
                "priority": self._calculate_story_priority(i, len(story_titles)),
                "estimated_time": 8,  # 時間
                "dependencies": self._identify_dependencies(i, current_task_id),
                "acceptance_criteria": self._generate_acceptance_criteria(),
            }

            self.stories.append(story)
            current_task_id += 1

        return self.stories

    def _calculate_story_priority(self, story_index: int, total_stories: int) -> str:
        """ストーリー優先度を計算"""
        if story_index <= total_stories * 0.3:
            return "high"
        elif story_index <= total_stories * 0.7:
            return "medium"
        else:
            return "low"

    def _identify_dependencies(self, story_index: int, current_task_id: int) -> List[str]:
        """依存関係を特定"""
        if story_index == 1:
            return []
        else:
            # 1つ前のタスクIDに依存
            prev_task_id = str(current_task_id - 1)
            return [prev_task_id]

    def _generate_acceptance_criteria(self) -> List[str]:
        """受け入れ基準を生成"""
        return [
            "コードが正常にコンパイルされ、すべてのテストが通過すること",
            "単体テストカバレッジ90%以上",
            "コードレビュー完了",
        ]


class PMAgentV33Epic:
    """PMエージェント - エピック処理版（task_ID連番）"""

    def __init__(self, sheets_manager=None, knowledge_manager=None):
        self.sheets = sheets_manager or GoogleSheetsManager()
        self.knowledge = knowledge_manager or KnowledgeManager()
        self.batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _get_next_task_id(self) -> int:
        """次のtask_IDを取得"""
        try:
            # pm_tasksシートから既存のtask_idを取得
            tasks_data = self.sheets.read_range("pm_tasks!A:A")

            if not tasks_data or len(tasks_data) <= 1:
                # ヘッダーのみ、または空の場合は1から開始
                return 1

            # 最大のtask_idを探す
            max_id = 0
            for row in tasks_data[1:]:  # ヘッダー行をスキップ
                if row and row[0]:
                    try:
                        task_id = int(row[0])
                        max_id = max(max_id, task_id)
                    except ValueError:
                        # 数値以外は無視
                        continue

            # 次のIDは最大値+1
            next_id = max_id + 1
            print(f"    📊 既存タスク最大ID: {max_id} → 次のID: {next_id}")

            return next_id

        except Exception as e:
            print(f"    ⚠️  task_ID取得エラー: {e}")
            print(f"    → デフォルト値1を使用")
            return 1

    async def process_epics(self) -> bool:
        """アクティブなエピックを処理"""
        try:
            print("=" * 80)
            print("PMAgentV33Epic: エピック処理開始（task_ID連番版）")
            print("=" * 80)
            print()

            # project_goalシートからアクティブなエピックを取得
            print("[1/4] アクティブなエピック取得中...")
            goals_data = self.sheets.read_range("project_goal!A:Z")

            if not goals_data or len(goals_data) < 2:
                print("⚠️  ゴールデータが見つかりません")
                return False

            headers = goals_data[0]
            rows = goals_data[1:]

            # 列インデックス取得
            goal_id_idx = headers.index("goal_id")
            status_idx = headers.index("status")
            desc_idx = headers.index("goal_description") if "goal_description" in headers else 1

            # アクティブなエピックを抽出
            active_epics = []
            for row in rows:
                if len(row) > max(goal_id_idx, status_idx, desc_idx):
                    if row[status_idx].lower() == "active":
                        epic = {
                            "goal_id": row[goal_id_idx],
                            "status": row[status_idx],
                            "goal_description": row[desc_idx] if len(row) > desc_idx else "",
                        }
                        active_epics.append(epic)

            if not active_epics:
                print("⚠️  アクティブなエピックがありません")
                return False

            print(f"✅ {len(active_epics)}件のアクティブなエピック取得")
            print()

            # 次のtask_IDを取得
            print("[2/4] 次のtask_ID確認中...")
            next_task_id = self._get_next_task_id()
            print()

            # 各エピックを処理
            print("[3/4] エピック処理中...")
            success_count = 0
            current_task_id = next_task_id

            for i, epic in enumerate(active_epics, 1):
                print(f"  [{i}/{len(active_epics)}] エピック{epic['goal_id']}処理中...")

                success, tasks_created = await self._process_single_epic(epic, current_task_id)
                if success:
                    success_count += 1
                    current_task_id += tasks_created  # 次のエピック用にIDを進める
                    print(f"  ✅ エピック{epic['goal_id']}処理成功（{tasks_created}タスク作成）")
                else:
                    print(f"  ⚠️  エピック{epic['goal_id']}処理失敗")
                print()

            print(f"[4/4] 処理完了: {success_count}/{len(active_epics)}件成功")
            print()

            print("=" * 80)
            print(f"✅ PMAgentV33Epic処理完了")
            print("=" * 80)

            return success_count > 0

        except Exception as e:
            print(f"❌ エラー: {e}")
            import traceback

            traceback.print_exc()
            return False

    async def _process_single_epic(
        self, epic: Dict[str, Any], start_task_id: int
    ) -> tuple[bool, int]:
        """
        単一エピックを処理

        Returns:
            (success, tasks_created): 成功フラグと作成したタスク数
        """
        try:
            # ストーリー生成
            generator = StoryGenerator(epic, start_task_id)
            stories = generator.generate_stories()

            if not stories:
                print(f"    ⚠️  ストーリー生成失敗")
                return False, 0

            print(f"    ✅ {len(stories)}件のストーリー生成")

            # pm_tasksシートに書き込み
            success = await self._write_stories_to_sheets(epic_id=epic["goal_id"], stories=stories)

            return success, len(stories)

        except Exception as e:
            print(f"    ❌ エラー: {e}")
            return False, 0

    async def _write_stories_to_sheets(self, epic_id: str, stories: List[Dict[str, Any]]) -> bool:
        """
        ストーリーをpm_tasksシートに書き込み

        ヘッダー順序:
        A: task_id (数字連番)
        B: parent_goal_id
        C: description
        D: required_role
        E: status
        F: priority
        G: estimated_time
        H: dependencies
        I: created_at
        J: batch_id
        K: detail_file_path
        L: blank
        M: execution_type
        """
        try:
            rows_to_append = []

            for story in stories:
                # 正しい列順序で行を作成
                row = [
                    story["task_id"],  # A: task_id (数字)
                    epic_id,  # B: parent_goal_id
                    story["description"],  # C: description
                    "developer",  # D: required_role
                    "pending",  # E: status
                    story["priority"],  # F: priority
                    str(story["estimated_time"]),  # G: estimated_time
                    ",".join(story["dependencies"]),  # H: dependencies
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # I: created_at
                    self.batch_id,  # J: batch_id
                    "",  # K: detail_file_path
                    "",  # L: blank
                    "auto",  # M: execution_type
                ]

                rows_to_append.append(row)

            # シートに書き込み
            print(f"    📝 {len(rows_to_append)}行をpm_tasksシートに書き込み中...")
            success = self.sheets.append_rows("pm_tasks", rows_to_append)

            if success:
                print(f"    ✅ 書き込み成功")
            else:
                print(f"    ❌ 書き込み失敗")

            return success

        except Exception as e:
            print(f"    ❌ 書き込みエラー: {e}")
            import traceback

            traceback.print_exc()
            return False


async def main():
    """テスト実行用メイン関数"""
    print("\n")
    print("=" * 80)
    print("PMAgentV33Epic テスト実行（task_ID連番版）")
    print("=" * 80)
    print("\n")

    agent = PMAgentV33Epic()
    success = await agent.process_epics()

    if success:
        print("\n✅ テスト成功")
    else:
        print("\n⚠️  テスト失敗")


if __name__ == "__main__":
    asyncio.run(main())
