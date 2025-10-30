#!/usr/bin/env python3
"""
ContextLogger: 判断プロセス・コンテキスト記録システム
エラーだけでなく、「なぜその判断をしたのか」を記録し、
自律エージェントが過去の経験から学習できるようにする。
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import traceback
import platform
import psutil


class DecisionContext:
    """判断コンテキストを保持するデータクラス"""

    def __init__(
        self,
        task_id: str,
        error_type: str,
        error_message: str,
        modification_reason: str,
        decision_process: str,
        modification_purpose: str,
        expected_result: str,
    ):
        self.task_id = task_id
        self.error_type = error_type
        self.error_message = error_message
        self.modification_reason = modification_reason
        self.decision_process = decision_process
        self.modification_purpose = modification_purpose
        self.expected_result = expected_result

        # システム状態の自動取得
        self.system_state = self._capture_system_state()

        # オプション情報
        self.alternatives: List[str] = []
        self.prevention_strategy: str = ""
        self.pattern_name: str = ""
        self.learning_tags: List[str] = []
        self.timestamp = datetime.now()

    def _capture_system_state(self) -> Dict[str, Any]:
        """システム状態をキャプチャ"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage("/").percent,
                "platform": platform.system(),
                "python_version": platform.python_version(),
            }
        except Exception as e:
            return {"error": str(e)}

    def add_alternative(self, alternative: str):
        """代替案を追加"""
        self.alternatives.append(alternative)

    def set_prevention_strategy(self, strategy: str):
        """再発防止策を設定"""
        self.prevention_strategy = strategy

    def set_pattern(self, pattern_name: str):
        """パターン名を設定"""
        self.pattern_name = pattern_name

    def add_learning_tag(self, tag: str):
        """学習タグを追加"""
        if tag not in self.learning_tags:
            self.learning_tags.append(tag)

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "log_id": f"CTX_{self.timestamp.strftime('%Y%m%d_%H%M%S')}_{self.task_id}",
            "task_id": self.task_id,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "modification_reason": self.modification_reason,
            "system_state": json.dumps(self.system_state, ensure_ascii=False),
            "decision_process": self.decision_process,
            "modification_purpose": self.modification_purpose,
            "expected_result": self.expected_result,
            "alternatives": json.dumps(self.alternatives, ensure_ascii=False),
            "prevention_strategy": self.prevention_strategy,
            "pattern_name": self.pattern_name,
            "learning_tags": ",".join(self.learning_tags),
        }

    def to_row(self, headers: List[str]) -> List[str]:
        """Google Sheets行形式に変換"""
        data = self.to_dict()
        return [str(data.get(h, "")) for h in headers]


class ContextLogger:
    """コンテキストロガー"""

    SHEET_NAME = "context_log"

    def __init__(self, sheets_manager):
        """
        初期化

        Args:
            sheets_manager: GoogleSheetsManagerインスタンス
        """
        self.sheets_manager = sheets_manager
        self.gc = sheets_manager.gc
        self.spreadsheet_id = sheets_manager.spreadsheet_id
        self._ensure_sheet_exists()
        print("✅ ContextLogger初期化完了")

    def _ensure_sheet_exists(self):
        """シートが存在することを確認"""
        try:
            spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
            worksheet_list = spreadsheet.worksheets()
            sheet_names = [ws.title for ws in worksheet_list]

            if self.SHEET_NAME not in sheet_names:
                print(f"⚠️ {self.SHEET_NAME}シートが見つかりません")
        except Exception as e:
            print(f"⚠️ {self.SHEET_NAME}シート初期化エラー: {e}")

    def _get_sheet(self):
        """シートを取得"""
        try:
            spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
            return spreadsheet.worksheet(self.SHEET_NAME)
        except Exception as e:
            print(f"⚠️ シート取得エラー ({self.SHEET_NAME}): {e}")
            return None

    async def log_decision(self, context: DecisionContext) -> bool:
        """
        判断プロセスをログに記録

        Args:
            context: 判断コンテキスト

        Returns:
            成功時True
        """
        try:
            sheet = self._get_sheet()
            if not sheet:
                return False

            # ヘッダーを取得
            headers = sheet.row_values(1)

            # コンテキストを行形式に変換
            row = context.to_row(headers)

            # 追加
            sheet.append_row(row)

            print(f"✅ コンテキスト記録: {context.error_type} - {context.modification_reason[:30]}...")
            return True

        except Exception as e:
            print(f"❌ コンテキスト記録エラー: {e}")
            traceback.print_exc()
            return False

    def search_similar_contexts(
        self, error_type: Optional[str] = None, learning_tags: Optional[List[str]] = None, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        類似のコンテキストを検索

        Args:
            error_type: エラータイプ
            learning_tags: 学習タグ
            limit: 返す結果の最大数

        Returns:
            類似コンテキストのリスト
        """
        try:
            sheet = self._get_sheet()
            if not sheet:
                return []

            records = sheet.get_all_records()

            # フィルタリング
            filtered = []
            for record in records:
                match = True

                # エラータイプでフィルタ
                if error_type and record.get("error_type") != error_type:
                    match = False

                # タグでフィルタ
                if learning_tags:
                    record_tags = record.get("learning_tags", "").split(",")
                    if not any(tag in record_tags for tag in learning_tags):
                        match = False

                if match:
                    filtered.append(record)

            # 新しい順にソート
            filtered.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

            return filtered[:limit]

        except Exception as e:
            print(f"⚠️ コンテキスト検索エラー: {e}")
            return []

    def get_pattern_usage_count(self, pattern_name: str) -> int:
        """特定パターンの使用回数を取得"""
        try:
            sheet = self._get_sheet()
            if not sheet:
                return 0

            records = sheet.get_all_records()
            count = sum(1 for r in records if r.get("pattern_name") == pattern_name)
            return count

        except Exception as e:
            print(f"⚠️ パターン使用回数取得エラー: {e}")
            return 0
