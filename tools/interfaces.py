"""
インターフェース契約書 v1.0
コンポーネント間の依存関係を明文化
"""

from typing import Protocol, Optional, List, Dict, Any
from typing_extensions import runtime_checkable


@runtime_checkable
class SheetsManagerProtocol(Protocol):
    """GoogleSheetsManagerが満たすべきインターフェース契約"""

    # 必須属性
    spreadsheet_id: Optional[str]
    authenticated: bool
    client: Optional[Any]
    sheet: Optional[Any]

    # 必須メソッド
    def read_sheet(self, sheet_name: str) -> List[Dict[str, Any]]:
        """シートを読み込む"""
        ...

    def get_sheet_data(self, sheet_name: str) -> List[Dict[str, Any]]:
        """シートデータを取得"""
        ...

    def write_sheet(self, sheet_name: str, data: List[List[Any]]) -> bool:
        """シートにデータを書き込む"""
        ...

    def authenticate(self) -> bool:
        """認証を実行"""
        ...


@runtime_checkable
class KnowledgeBaseManagerProtocol(Protocol):
    """KnowledgeBaseManagerが満たすべきインターフェース契約"""

    async def update(self, patterns: List[Dict[str, Any]]) -> bool:
        """ナレッジベースを更新"""
        ...

    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """ナレッジを検索"""
        ...


@runtime_checkable
class LogIntegratorProtocol(Protocol):
    """LogIntegratorが満たすべきインターフェース契約"""

    async def load_all_logs(self) -> List[Dict[str, Any]]:
        """全ログを読み込む"""
        ...


@runtime_checkable
class PatternExtractorProtocol(Protocol):
    """PatternExtractorが満たすべきインターフェース契約"""

    async def extract(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """パターンを抽出"""
        ...


# 契約検証ユーティリティ
def verify_contract(instance: Any, protocol: type) -> bool:
    """
    インスタンスがプロトコルを満たすか検証

    Args:
        instance: 検証対象のインスタンス
        protocol: プロトコルクラス

    Returns:
        契約を満たす場合True
    """
    return isinstance(instance, protocol)


def get_missing_attributes(instance: Any, protocol: type) -> List[str]:
    """
    プロトコルで要求される属性のうち、欠落しているものを返す

    Args:
        instance: 検証対象のインスタンス
        protocol: プロトコルクラス

    Returns:
        欠落している属性名のリスト
    """
    missing = []

    # プロトコルの注釈を取得
    annotations = getattr(protocol, "__annotations__", {})

    for attr_name in annotations:
        if not hasattr(instance, attr_name):
            missing.append(attr_name)

    return missing


if __name__ == "__main__":
    print("📋 インターフェース契約書 v1.0")
    print("=" * 50)
    print("定義済みプロトコル:")
    print("  ✅ SheetsManagerProtocol")
    print("  ✅ KnowledgeBaseManagerProtocol")
    print("  ✅ LogIntegratorProtocol")
    print("  ✅ PatternExtractorProtocol")
