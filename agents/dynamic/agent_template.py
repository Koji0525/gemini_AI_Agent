"""
Week 6: AgentTemplate - エージェントテンプレート基底クラス

動的にエージェントを生成するためのテンプレートシステム
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AgentMetadata:
    """エージェントのメタデータ"""
    name: str                      # エージェント名
    version: str                   # バージョン
    description: str               # 説明
    author: str                    # 作成者
    created_at: datetime           # 作成日時
    dependencies: List[str]        # 依存パッケージ
    capabilities: List[str]        # 機能リスト
    tags: List[str]               # タグ


@dataclass
class AgentConfig:
    """エージェント設定"""
    max_retries: int = 3          # 最大リトライ回数
    timeout: int = 30             # タイムアウト（秒）
    async_mode: bool = True       # 非同期モード
    logging_enabled: bool = True  # ログ有効化
    custom_params: Dict[str, Any] = None  # カスタムパラメータ


class AgentTemplate(ABC):
    """
    エージェントテンプレートの基底クラス
    
    全ての動的エージェントはこのクラスを継承する
    """
    
    def __init__(
        self,
        metadata: AgentMetadata,
        config: Optional[AgentConfig] = None
    ):
        """
        Args:
            metadata: エージェントのメタデータ
            config: エージェント設定
        """
        self.metadata = metadata
        self.config = config or AgentConfig()
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        エージェントのメイン処理
        
        Args:
            **kwargs: タスク固有のパラメータ
            
        Returns:
            実行結果
        """
        pass
    
    @abstractmethod
    def validate_input(self, **kwargs) -> bool:
        """
        入力パラメータの検証
        
        Args:
            **kwargs: 検証するパラメータ
            
        Returns:
            検証結果（True: 成功, False: 失敗）
        """
        pass
    
    @abstractmethod
    def get_required_params(self) -> List[str]:
        """
        必須パラメータのリストを取得
        
        Returns:
            必須パラメータ名のリスト
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        メタデータを辞書形式で取得
        
        Returns:
            メタデータ辞書
        """
        return {
            'name': self.metadata.name,
            'version': self.metadata.version,
            'description': self.metadata.description,
            'author': self.metadata.author,
            'created_at': self.metadata.created_at.isoformat(),
            'dependencies': self.metadata.dependencies,
            'capabilities': self.metadata.capabilities,
            'tags': self.metadata.tags,
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        実行統計を取得
        
        Returns:
            統計情報
        """
        success_rate = 0.0
        if self.execution_count > 0:
            success_rate = (self.success_count / self.execution_count) * 100
        
        return {
            'execution_count': self.execution_count,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'success_rate': f"{success_rate:.1f}%"
        }
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """
        エージェントを実行（統計記録付き）
        
        Args:
            **kwargs: タスクパラメータ
            
        Returns:
            実行結果
        """
        self.execution_count += 1
        
        try:
            # 入力検証
            if not self.validate_input(**kwargs):
                raise ValueError("Invalid input parameters")
            
            # 実行
            result = await self.execute(**kwargs)
            
            # 成功カウント
            self.success_count += 1
            
            return {
                'success': True,
                'result': result,
                'agent': self.metadata.name,
                'version': self.metadata.version
            }
            
        except Exception as e:
            # 失敗カウント
            self.failure_count += 1
            
            return {
                'success': False,
                'error': str(e),
                'agent': self.metadata.name,
                'version': self.metadata.version
            }
    
    def __str__(self) -> str:
        """文字列表現"""
        return f"{self.metadata.name} v{self.metadata.version}"
    
    def __repr__(self) -> str:
        """デバッグ用文字列表現"""
        return f"AgentTemplate(name='{self.metadata.name}', version='{self.metadata.version}')"


# ================================================
# 組み込みテンプレート例
# ================================================

class SimpleAPIAgentTemplate(AgentTemplate):
    """
    シンプルなAPI呼び出しエージェントテンプレート
    """
    
    def __init__(self):
        metadata = AgentMetadata(
            name="SimpleAPIAgent",
            version="1.0.0",
            description="Simple API calling agent template",
            author="System",
            created_at=datetime.now(),
            dependencies=["requests", "aiohttp"],
            capabilities=["api_call", "http_request"],
            tags=["api", "http", "simple"]
        )
        super().__init__(metadata)
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        API呼び出しを実行
        
        Required kwargs:
            - url: APIエンドポイント
            - method: HTTPメソッド (GET/POST/PUT/DELETE)
            - headers: HTTPヘッダー (optional)
            - data: リクエストボディ (optional)
        """
        import aiohttp
        
        url = kwargs['url']
        method = kwargs.get('method', 'GET')
        headers = kwargs.get('headers', {})
        data = kwargs.get('data', None)
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, json=data) as response:
                return {
                    'status_code': response.status,
                    'data': await response.json() if response.content_type == 'application/json' else await response.text(),
                    'headers': dict(response.headers)
                }
    
    def validate_input(self, **kwargs) -> bool:
        """入力検証"""
        return 'url' in kwargs
    
    def get_required_params(self) -> List[str]:
        """必須パラメータ"""
        return ['url']


class DataProcessingAgentTemplate(AgentTemplate):
    """
    データ処理エージェントテンプレート
    """
    
    def __init__(self):
        metadata = AgentMetadata(
            name="DataProcessingAgent",
            version="1.0.0",
            description="Data processing agent template",
            author="System",
            created_at=datetime.now(),
            dependencies=["pandas", "numpy"],
            capabilities=["data_transformation", "filtering", "aggregation"],
            tags=["data", "processing", "analytics"]
        )
        super().__init__(metadata)
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        データ処理を実行
        
        Required kwargs:
            - data: 処理するデータ（list or dict）
            - operation: 処理操作 (filter/transform/aggregate)
            - params: 操作パラメータ
        """
        data = kwargs['data']
        operation = kwargs['operation']
        params = kwargs.get('params', {})
        
        if operation == 'filter':
            # フィルタ処理の例
            return {'filtered_data': data}
        
        elif operation == 'transform':
            # 変換処理の例
            return {'transformed_data': data}
        
        elif operation == 'aggregate':
            # 集計処理の例
            return {'aggregated_data': len(data) if isinstance(data, list) else 0}
        
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def validate_input(self, **kwargs) -> bool:
        """入力検証"""
        return 'data' in kwargs and 'operation' in kwargs
    
    def get_required_params(self) -> List[str]:
        """必須パラメータ"""
        return ['data', 'operation']
