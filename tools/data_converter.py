"""
スプレッドシートデータ変換ヘルパー
リスト形式 → 辞書形式への変換
"""

from typing import Any, Dict, List


class DataConverter:
    """スプレッドシートデータを辞書形式に変換"""

    @staticmethod
    def convert_goal_to_dict(goal_row: List[Any]) -> Dict[str, Any]:
        """
        ゴール行を辞書に変換

        Args:
            goal_row: [goal_id, status, description] 形式のリスト

        Returns:
            {
                'goal_id': str,
                'status': str,
                'description': str
            }
        """
        if not goal_row or len(goal_row) == 0:
            return {}

        return {
            "goal_id": goal_row[0] if len(goal_row) > 0 else "",
            "status": goal_row[1] if len(goal_row) > 1 else "pending",
            "description": goal_row[2] if len(goal_row) > 2 else "",
        }

    @staticmethod
    def convert_task_to_dict(task_row: List[Any], headers: List[str]) -> Dict[str, Any]:
        """
        タスク行を辞書に変換

        Args:
            task_row: タスクデータのリスト
            headers: ヘッダー行のリスト

        Returns:
            {header: value} 形式の辞書
        """
        if not task_row or not headers:
            return {}

        task_dict = {}
        for i, header in enumerate(headers):
            if i < len(task_row):
                task_dict[header] = task_row[i]
            else:
                task_dict[header] = ""

        return task_dict

    @staticmethod
    def convert_goals_list_to_dicts(goals_data: List[List[Any]]) -> List[Dict[str, Any]]:
        """
        複数のゴール行を辞書のリストに変換

        Args:
            goals_data: [[goal_id, status, description], ...] 形式

        Returns:
            [{goal_id, status, description}, ...] 形式
        """
        return [DataConverter.convert_goal_to_dict(row) for row in goals_data]

    @staticmethod
    def convert_tasks_list_to_dicts(
        tasks_data: List[List[Any]], headers: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        複数のタスク行を辞書のリストに変換

        Args:
            tasks_data: タスクデータのリスト（ヘッダー行を含む場合と含まない場合がある）
            headers: ヘッダー行（Noneの場合は1行目をヘッダーとして使用）

        Returns:
            [{header: value}, ...] 形式のリスト
        """
        if not tasks_data or len(tasks_data) == 0:
            return []

        # ヘッダーが指定されていない場合は1行目を使用
        if headers is None:
            headers = tasks_data[0]
            data_rows = tasks_data[1:]
        else:
            data_rows = tasks_data

        return [DataConverter.convert_task_to_dict(row, headers) for row in data_rows]


# テスト用
if __name__ == "__main__":
    converter = DataConverter()

    # テスト1: ゴール変換
    print("🧪 テスト1: ゴール変換")
    goal_row = ["GOAL_001", "active", "テストゴール"]
    goal_dict = converter.convert_goal_to_dict(goal_row)
    print(f"入力: {goal_row}")
    print(f"出力: {goal_dict}")
    print()

    # テスト2: 複数ゴール変換
    print("🧪 テスト2: 複数ゴール変換")
    goals_data = [["GOAL_001", "active", "ゴール1"], ["GOAL_002", "pending", "ゴール2"]]
    goals_dicts = converter.convert_goals_list_to_dicts(goals_data)
    print(f"入力: {goals_data}")
    print(f"出力: {goals_dicts}")
