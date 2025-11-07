"""
スプレッドシートデータ変換ヘルパー

SafeSheetsWrapperが返す2次元配列を辞書形式に変換
"""

from typing import Any, Dict, List


class SheetsDataConverter:
    """スプレッドシートデータ変換クラス"""

    @staticmethod
    def rows_to_dicts(rows: List[List[Any]], headers: List[str] = None) -> List[Dict[str, Any]]:
        """
        2次元配列を辞書のリストに変換

        Args:
            rows: スプレッドシートから読み込んだ行データ
            headers: カラム名のリスト（Noneの場合は最初の行を使用）

        Returns:
            辞書のリスト
        """
        if not rows:
            return []

        # ヘッダーが指定されていない場合、最初の行をヘッダーとして使用
        if headers is None:
            if len(rows) < 2:
                return []
            headers = rows[0]
            data_rows = rows[1:]
        else:
            data_rows = rows

        # 各行を辞書に変換
        result = []
        for row in data_rows:
            # 行の長さがヘッダーより短い場合は空文字で埋める
            padded_row = row + [""] * (len(headers) - len(row))
            row_dict = {headers[i]: padded_row[i] for i in range(len(headers))}
            result.append(row_dict)

        return result

    @staticmethod
    def dict_to_row(data: Dict[str, Any], headers: List[str]) -> List[Any]:
        """
        辞書を行データに変換

        Args:
            data: 辞書データ
            headers: カラム名のリスト

        Returns:
            行データ
        """
        return [data.get(header, "") for header in headers]


if __name__ == "__main__":
    # テスト
    converter = SheetsDataConverter()

    # テストデータ
    rows = [
        ["goal_id", "description", "status"],
        ["GOAL_001", "テストゴール", "active"],
        ["GOAL_002", "完了ゴール", "completed"],
    ]

    # 変換
    dicts = converter.rows_to_dicts(rows)
    print("✅ 変換結果:")
    for d in dicts:
        print(f"  {d}")
