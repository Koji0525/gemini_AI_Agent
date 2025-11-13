"""
自己修復エージェント v1.0
エラーの自動検出と修復を担当
Phase 1: 基本的なエラー分類とリトライ機能
"""

import os
import sys
import time
from datetime import datetime
from typing import Any, Callable, Dict

project_root = os.path.abspath(os.path.dirname(__file__) + "/../..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools.base_data_accessor import BaseDataAccessor


class ErrorClassifier:
    """エラー分類器"""

    ERROR_TYPES = {
        "API_ERROR": ["API", "Connection", "Timeout", "HTTPError"],
        "DATA_ERROR": ["KeyError", "ValueError", "IndexError", "AttributeError"],
        "FILE_ERROR": ["FileNotFoundError", "PermissionError", "IOError"],
        "IMPORT_ERROR": ["ModuleNotFoundError", "ImportError"],
        "UNKNOWN": [],
    }

    def classify(self, error: Exception) -> str:
        """エラーを分類"""
        error_str = str(error)
        error_type = type(error).__name__

        for category, keywords in self.ERROR_TYPES.items():
            if category == "UNKNOWN":
                continue

            for keyword in keywords:
                if keyword in error_str or keyword in error_type:
                    return category

        return "UNKNOWN"


class RetryManager:
    """リトライ管理"""

    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def retry_with_backoff(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """
        指数バックオフでリトライ

        Args:
            func: 実行する関数
            *args, **kwargs: 関数の引数

        Returns:
            実行結果
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                print(f"  🔄 リトライ {attempt + 1}/{self.max_retries}")

                result = func(*args, **kwargs)

                print(f"  ✅ リトライ成功")
                return {"success": True, "result": result, "attempts": attempt + 1}

            except Exception as e:
                last_error = e

                if attempt < self.max_retries - 1:
                    # バックオフ時間計算
                    wait_time = self.backoff_factor**attempt
                    print(f"  ⏳ {wait_time}秒待機...")
                    time.sleep(wait_time)
                else:
                    print(f"  ❌ リトライ失敗")

        return {"success": False, "error": str(last_error), "attempts": self.max_retries}


class SelfHealingAgent(BaseDataAccessor):
    """自己修復エージェント"""

    def __init__(self):
        super().__init__()
        self.error_classifier = ErrorClassifier()
        self.retry_manager = RetryManager()

        # 統計情報
        self.stats = {
            "total_errors": 0,
            "healed_errors": 0,
            "failed_heals": 0,
            "healing_rate": 0.0,
            "by_type": {},
        }

        print("✅ SelfHealingAgent v1.0 初期化完了")

    def detect_and_heal(self, error: Exception, context: Dict) -> Dict[str, Any]:
        """
        エラー検出と修復

        Args:
            error: 発生したエラー
            context: エラー発生時のコンテキスト

        Returns:
            修復結果
        """
        print(f"\n🔧 自己修復開始")
        print(f"エラー: {type(error).__name__}: {error}")

        self.stats["total_errors"] += 1

        # STEP 1: エラー分類
        error_type = self.error_classifier.classify(error)
        print(f"  分類: {error_type}")

        # 統計更新
        if error_type not in self.stats["by_type"]:
            self.stats["by_type"][error_type] = 0
        self.stats["by_type"][error_type] += 1

        # STEP 2: 修復戦略決定
        strategy = self.decide_healing_strategy(error_type, error, context)
        print(f"  戦略: {strategy['name']}")

        # STEP 3: 修復実行
        result = self.execute_healing(strategy, error, context)

        # STEP 4: 結果記録
        self.record_healing(error_type, strategy, result)

        # 統計更新
        if result["success"]:
            self.stats["healed_errors"] += 1
            print(f"  ✅ 修復成功")
        else:
            self.stats["failed_heals"] += 1
            print(f"  ❌ 修復失敗")

        self.stats["healing_rate"] = self.stats["healed_errors"] / self.stats["total_errors"] * 100

        return result

    def decide_healing_strategy(
        self, error_type: str, error: Exception, context: Dict
    ) -> Dict[str, Any]:
        """修復戦略決定"""

        if error_type == "API_ERROR":
            return {"name": "APIリトライ", "type": "retry", "max_retries": 3, "backoff_factor": 2.0}

        elif error_type == "DATA_ERROR":
            return {"name": "データ修正", "type": "data_fix"}

        elif error_type == "FILE_ERROR":
            return {"name": "ファイル作成", "type": "file_create"}

        elif error_type == "IMPORT_ERROR":
            return {"name": "代替インポート", "type": "alternative"}

        else:
            return {"name": "デフォルトリトライ", "type": "retry", "max_retries": 1}

    def execute_healing(self, strategy: Dict, error: Exception, context: Dict) -> Dict[str, Any]:
        """修復実行"""

        if strategy["type"] == "retry":
            # リトライ戦略
            if "func" in context:
                return self.retry_manager.retry_with_backoff(
                    context["func"], *context.get("args", []), **context.get("kwargs", {})
                )
            else:
                return {"success": False, "reason": "実行関数が指定されていません"}

        elif strategy["type"] == "data_fix":
            # データ修正戦略
            return self.fix_data_error(error, context)

        elif strategy["type"] == "file_create":
            # ファイル作成戦略
            return self.create_missing_file(error, context)

        elif strategy["type"] == "alternative":
            # 代替手段戦略
            return self.try_alternative(error, context)

        else:
            return {"success": False, "reason": f'未知の戦略: {strategy["type"]}'}

    def fix_data_error(self, error: Exception, context: Dict) -> Dict[str, Any]:
        """データエラー修正"""
        print("    データエラー修正を試行")

        # 簡易実装：エラーの種類に応じた対応
        if isinstance(error, KeyError):
            missing_key = str(error).strip("'")
            print(f"    欠損キー: {missing_key}")

            # デフォルト値を設定
            if "data" in context:
                context["data"][missing_key] = ""
                return {"success": True, "fixed_key": missing_key}

        return {"success": False, "reason": "修正方法が見つかりません"}

    def create_missing_file(self, error: Exception, context: Dict) -> Dict[str, Any]:
        """欠損ファイル作成"""
        print("    ファイル作成を試行")

        if isinstance(error, FileNotFoundError):
            filename = str(error).split("'")[1] if "'" in str(error) else None

            if filename:
                print(f"    ファイル作成: {filename}")

                # ディレクトリ作成
                dirname = os.path.dirname(filename)
                if dirname and not os.path.exists(dirname):
                    os.makedirs(dirname)

                # 空ファイル作成
                with open(filename, "w") as f:
                    f.write("")

                return {"success": True, "created_file": filename}

        return {"success": False, "reason": "ファイル名が特定できません"}

    def try_alternative(self, error: Exception, context: Dict) -> Dict[str, Any]:
        """代替手段実行"""
        print("    代替手段を試行")

        # 簡易実装
        return {"success": False, "reason": "代替手段が未実装"}

    def record_healing(self, error_type: str, strategy: Dict, result: Dict):
        """修復ログ記録"""

        # healing_logシートに記録（存在する場合）
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "error_type": error_type,
                "strategy": strategy["name"],
                "success": result["success"],
                "details": str(result),
            }

            # TODO: シートへの記録を実装

        except Exception as e:
            print(f"    ⚠️ ログ記録失敗: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """統計情報取得"""
        return self.stats.copy()


def main():
    """テスト実行"""
    print("=" * 80)
    print("🧪 SelfHealingAgent テスト")
    print("=" * 80)

    agent = SelfHealingAgent()

    # テスト1: APIエラー
    print("\nテスト1: APIエラー")

    def failing_api_call():
        raise ConnectionError("API connection failed")

    try:
        failing_api_call()
    except Exception as e:
        result = agent.detect_and_heal(e, {"func": lambda: "Success"})
        print(f"結果: {result}")

    # 統計表示
    print("\n" + "=" * 80)
    print("📊 統計情報")
    print("=" * 80)
    stats = agent.get_statistics()
    print(f"総エラー数: {stats['total_errors']}")
    print(f"修復成功: {stats['healed_errors']}")
    print(f"修復失敗: {stats['failed_heals']}")
    print(f"修復成功率: {stats['healing_rate']:.1f}%")
    print(f"\nエラータイプ別:")
    for error_type, count in stats["by_type"].items():
        print(f"  {error_type}: {count}件")


if __name__ == "__main__":
    main()
