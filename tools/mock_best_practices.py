"""
モックのベストプラクティスガイド
"""

from unittest.mock import MagicMock


class MockBestPractices:
    """モックのベストプラクティス"""

    @staticmethod
    def create_realistic_mock(return_data=None, side_effect=None):
        """
        現実的なモックを作成

        Args:
            return_data: 戻り値のデータ
            side_effect: 副作用（例外や動的な戻り値）
        """
        mock = MagicMock()

        if return_data is not None:
            mock.return_value = return_data

        if side_effect is not None:
            mock.side_effect = side_effect

        return mock

    @staticmethod
    def mock_sheets_data(rows=3, headers=None):
        """
        スプレッドシートデータのモックを作成

        Args:
            rows: データ行数
            headers: ヘッダー行（Noneの場合はデフォルト）
        """
        if headers is None:
            headers = ["ID", "タイトル", "内容", "日付"]

        data = [headers]

        for i in range(1, rows + 1):
            data.append([f"id_{i}", f"タイトル{i}", f"内容{i}", f"2024-01-{i:02d}"])

        return data

    @staticmethod
    def verify_mock_usage(mock_obj, expected_calls=1, method_name=None):
        """
        モックの使用状況を検証

        Args:
            mock_obj: モックオブジェクト
            expected_calls: 期待される呼び出し回数
            method_name: メソッド名（Noneの場合はモックオブジェクト自体）
        """
        if method_name:
            actual_calls = getattr(mock_obj, method_name).call_count
        else:
            actual_calls = mock_obj.call_count

        assert (
            actual_calls == expected_calls
        ), f"期待される呼び出し回数: {expected_calls}, 実際: {actual_calls}"


# 使用例
def example_usage():
    """使用例"""
    practices = MockBestPractices()

    # スプレッドシートデータのモック
    sheets_data = practices.mock_sheets_data(rows=5)
    mock_sheets = practices.create_realistic_mock(return_value=sheets_data)

    # APIクライアントのモック
    mock_api = practices.create_realistic_mock(return_value={"status": "success", "data": "test"})

    return mock_sheets, mock_api


if __name__ == "__main__":
    mock_sheets, mock_api = example_usage()
    print("✅ モックベストプラクティスの例を生成しました")
