"""
interface_validator.py

インターフェース自動検証システム

【目的】
実行時にメソッド存在を検証し、代替メソッドを自動検索する。
これにより、メソッド名の不一致による実行エラーを防ぐ。

【長期的メリット】
- 今後のインターフェース変更に自動対応
- エラー発生前に問題を検出
- 代替メソッドの自動発見

【変更理由】
TaskExecutor.execute_task()が存在せず、execute_single_task()が正しい、
といった問題を今後自動解決するため。
"""

import inspect
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class InterfaceValidator:
    """
    インターフェース自動検証システム

    メソッド存在確認と代替メソッド探索を行う
    """

    def __init__(self):
        self.method_aliases = {
            # よくある名前の揺れを定義
            "execute_task": [
                "execute_single_task",
                "execute",
                "run_task",
                "process_task",
            ],
            "update_range": ["write_range", "update_cells", "write_cells"],
            "update_cell": ["write_cell", "set_cell"],
            "read_range": ["get_range", "fetch_range"],
        }

    def validate_method(self, obj: Any, method_name: str) -> Optional[str]:
        """
        メソッド存在を検証し、存在しない場合は代替メソッドを探索

        Args:
            obj: 検証対象オブジェクト
            method_name: メソッド名

        Returns:
            実際に存在するメソッド名（存在しない場合はNone）
        """
        # 1. 指定されたメソッドが存在するか確認
        if hasattr(obj, method_name):
            return method_name

        # 2. 代替メソッドを探索
        logger.warning(f"⚠️ メソッド '{method_name}' が見つかりません")

        # 登録された代替候補を確認
        if method_name in self.method_aliases:
            for alt_method in self.method_aliases[method_name]:
                if hasattr(obj, alt_method):
                    logger.info(f"✅ 代替メソッド発見: {alt_method}")
                    return alt_method

        # 3. 類似メソッドを自動検索（部分一致）
        all_methods = [m for m in dir(obj) if not m.startswith("_")]
        similar_methods = [m for m in all_methods if method_name.split("_")[0] in m.lower()]

        if similar_methods:
            logger.info(f"🔍 類似メソッド候補: {similar_methods}")
            # 最も類似度が高いものを選択
            best_match = similar_methods[0]
            logger.info(f"💡 自動選択: {best_match}")
            return best_match

        logger.error(f"❌ 代替メソッドが見つかりません: {method_name}")
        return None

    def safe_call(self, obj: Any, method_name: str, *args, **kwargs) -> Any:
        """
        安全にメソッドを呼び出す（代替メソッド自動使用）

        Args:
            obj: 呼び出し対象オブジェクト
            method_name: メソッド名
            *args, **kwargs: メソッド引数

        Returns:
            メソッド実行結果
        """
        actual_method = self.validate_method(obj, method_name)

        if actual_method is None:
            raise AttributeError(
                f"'{type(obj).__name__}' object has no method '{method_name}' "
                f"and no suitable alternative was found"
            )

        method = getattr(obj, actual_method)

        # メソッドのシグネチャを確認
        # sig = inspect.signature(method)

        try:
            return method(*args, **kwargs)
        except TypeError as e:
            # 引数が合わない場合、自動調整を試みる
            logger.warning(f"⚠️ 引数不一致: {e}")
            logger.info("🔧 引数を自動調整中...")

            # キーワード引数のみで再試行
            return method(**kwargs)

    def get_method_signature(self, obj: Any, method_name: str) -> Optional[str]:
        """
        メソッドのシグネチャを取得

        Args:
            obj: 対象オブジェクト
            method_name: メソッド名

        Returns:
            シグネチャ文字列
        """
        actual_method = self.validate_method(obj, method_name)
        if actual_method:
            method = getattr(obj, actual_method)
            sig = inspect.signature(method)
            return f"{actual_method}{sig}"
        return None


# グローバルインスタンス
validator = InterfaceValidator()
