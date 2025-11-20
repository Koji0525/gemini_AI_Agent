import logging
import json
import os
from typing import Dict, Any, List

def setup_logging(log_file: str = "integration_test.log", level=logging.INFO) -> logging.Logger:
    """
    ロギングを設定します。コンソールとファイルの両方に出力します。

    Args:
        log_file (str): ログ出力ファイルの名前。
        level: ロギングのレベル (例: logging.INFO, logging.DEBUG)。

    Returns:
        logging.Logger: 設定されたロガーオブジェクト。
    """
    logger = logging.getLogger("IntegrationTest")
    logger.setLevel(level)

    # 既存のハンドラをクリア（二重出力を防ぐため）
    if logger.hasHandlers():
        logger.handlers.clear()

    # コンソールハンドラ
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # ファイルハンドラ
    file_handler = logging.FileHandler(log_file)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    logger.info(f"ロギングがファイル '{log_file}' とコンソールに設定されました。")
    return logger

def load_config(config_path: str) -> Dict[str, Any]:
    """
    指定されたパスからJSON設定ファイルを読み込みます。

    Args:
        config_path (str): 設定ファイルへのパス。

    Returns:
        Dict[str, Any]: 読み込まれた設定を辞書形式で返します。

    Raises:
        FileNotFoundError: 設定ファイルが見つからない場合。
        json.JSONDecodeError: 設定ファイルの形式が不正な場合。
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"設定ファイルが見つかりません: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config

def save_report(report_data: Dict[str, Any], filepath: str):
    """
    テスト結果レポートを指定されたパスにJSON形式で保存します。

    Args:
        report_data (Dict[str, Any]): 保存するレポートデータ。
        filepath (str): レポートを保存するファイルのパス。
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)
        logging.getLogger("IntegrationTest").info(f"レポートを '{filepath}' に保存しました。")
    except Exception as e:
        logging.getLogger("IntegrationTest").error(f"レポートの保存中にエラーが発生しました: {e}", exc_info=True)
        raise

class MockKnowledgeSystem:
    """
    F4 ナレッジシステムのモック実装。
    シンプルな辞書を使ってデータの読み書きをシミュレートします。
    """
    def __init__(self):
        self._store = {}
        logging.getLogger("IntegrationTest").debug("MockKnowledgeSystem が初期化されました。")

    def write(self, key: str, value: Any) -> bool:
        """
        ナレッジシステムにデータを書き込みます。

        Args:
            key (str): データに関連付けられるキー。
            value (Any): 保存するデータ。

        Returns:
            bool: 書き込みが成功した場合はTrue、それ以外はFalse。
        """
        try:
            self._store[key] = value
            logging.getLogger("IntegrationTest").debug(f"MockKnowledgeSystem: '{key}' にデータを書き込みました。")
            return True
        except Exception as e:
            logging.getLogger("IntegrationTest").error(f"MockKnowledgeSystem: 書き込みエラー - {e}", exc_info=True)
            return False

    def read(self, key: str) -> Any:
        """
        ナレッジシステムからデータを読み込みます。

        Args:
            key (str): 読み込むデータのキー。

        Returns:
            Any: 読み込まれたデータ。キーが見つからない場合はNone。
        """
        data = self._store.get(key)
        if data is not None:
            logging.getLogger("IntegrationTest").debug(f"MockKnowledgeSystem: '{key}' からデータを読み込みました。")
        else:
            logging.getLogger("IntegrationTest").warning(f"MockKnowledgeSystem: '{key}' が見つかりません。")
        return data

class MockGoogleSheetsAPI:
    """
    Google Sheets API連携のモック実装。
    実際のAPI呼び出しは行わず、成功/失敗をシミュレートします。
    """
    def __init__(self):
        logging.getLogger("IntegrationTest").debug("MockGoogleSheetsAPI が初期化されました。")
        # 実際のAPIでは認証情報などがここに含まれる

    def update_sheet(self, sheet_id: str, range_name: str, data: List[List[Any]]) -> str:
        """
        指定されたGoogleシートのセル範囲を更新する操作をシミュレートします。

        Args:
            sheet_id (str): 更新対象のシートID。
            range_name (str): 更新対象のセル範囲（例: "Sheet1!A1:B1"）。
            data (List[List[Any]]): 更新するデータ。行と列のリスト。

        Returns:
            str: 成功または失敗を示すメッセージ。
        """
        logging.getLogger("IntegrationTest").debug(f"MockGoogleSheetsAPI: シート '{sheet_id}', 範囲 '{range_name}' をデータ '{data}' で更新する操作をシミュレートします。")
        # ここで実際のAPI呼び出しやエラーシミュレーションを行う
        if sheet_id and range_name and data:
            # 簡略化のため常に成功と仮定
            return f"SUCCESS: Google Sheets '{sheet_id}' updated for range '{range_name}'."
        else:
            return "FAILED: Invalid parameters for Google Sheets update."

# F1-F10機能リスト
F_FUNCTIONS = [
    {"id": "F1", "name": "ゴール分解 (Goal Decomposition)"},
    {"id": "F2", "name": "計画策定 (Planning)"},
    {"id": "F3", "name": "実行管理 (Execution Management)"},
    {"id": "F4", "name": "ナレッジシステム (Knowledge System)"},
    {"id": "F5", "name": "モニタリング (Monitoring)"},
    {"id": "F6", "name": "異常検知 (Anomaly Detection)"},
    {"id": "F7", "name": "自己回復 (Self-Healing)"},
    {"id": "F8", "name": "学習・適応 (Learning and Adaptation)"},
    {"id": "F9", "name": "人間との協調 (Human Collaboration)"},
    {"id": "F10", "name": "健全性チェック (Health Check)"},
]