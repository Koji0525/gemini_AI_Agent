"""
タスク実行テンプレートライブラリ
目的: 各タスクタイプに対応した高品質なテンプレートを提供
"""
from datetime import datetime
from typing import Dict, Any


class TemplateLibrary:
    """タスクタイプ別テンプレート集"""
    
    @staticmethod
    def get_keywords_mapping() -> Dict[str, list]:
        """タスクタイプとキーワードのマッピング"""
        return {
            'ui_ux': [
                'ui', 'ux', 'フロント', 'デザイン', 'プログレス', 'カラー',
                'ユーザビリティ', 'インターフェース', '画面', 'レイアウト',
                'ボタン', 'フォーム', 'メニュー', 'ナビゲーション'
            ],
            'api': [
                'api', 'rest', 'エンドポイント', 'サーバー', 'http', 'request',
                'response', 'json', 'graphql', 'webhook', 'microservice'
            ],
            'database': [
                'データ', 'database', 'db', 'sql', 'テーブル', 'クエリ',
                'postgresql', 'mysql', 'mongodb', 'redis', 'orm', 'migration'
            ],
            'testing': [
                'テスト', 'test', '品質', 'qa', 'unittest', 'pytest',
                '検証', 'バリデーション', 'e2e', 'integration', 'coverage'
            ],
            'backend': [
                'バックエンド', 'backend', 'サーバーサイド', 'ロジック',
                'サービス', 'ビジネスロジック', '処理', 'controller'
            ],
            'devops': [
                'デプロイ', 'ci/cd', 'docker', 'kubernetes', 'インフラ',
                'パイプライン', 'jenkins', 'github actions', 'terraform'
            ],
            'security': [
                'セキュリティ', 'security', '認証', '認可', '暗号化',
                'oauth', 'jwt', 'ssl', 'tls', '脆弱性'
            ],
            'documentation': [
                'ドキュメント', 'document', 'readme', 'マニュアル', 'ガイド',
                '仕様書', 'api doc', 'swagger', 'openapi'
            ],
            'performance': [
                'パフォーマンス', 'performance', '最適化', 'optimize',
                '高速化', 'チューニング', 'キャッシュ', 'レイテンシ'
            ],
            'refactoring': [
                'リファクタリング', 'refactor', '改善', 'クリーンアップ',
                'コード整理', 'リストラクチャリング', 'モダナイゼーション'
            ]
        }
    
    @staticmethod
    def detect_task_types(description: str) -> list:
        """
        タスク説明からタスクタイプを検出（複数可）
        
        Args:
            description: タスク説明文
        
        Returns:
            検出されたタスクタイプのリスト
        """
        description_lower = description.lower()
        mapping = TemplateLibrary.get_keywords_mapping()
        detected_types = []
        
        for task_type, keywords in mapping.items():
            if any(keyword in description_lower for keyword in keywords):
                detected_types.append(task_type)
        
        return detected_types if detected_types else ['generic']
    
    @staticmethod
    def get_quality_multiplier(task_types: list) -> float:
        """
        タスクタイプに基づく品質係数を取得
        
        複数のタイプが検出された場合は高い係数を適用
        """
        base_multiplier = 1.0
        if len(task_types) > 1:
            base_multiplier = 1.5  # 複合タスクは品質を上げる
        return base_multiplier


# 以下、各タスクタイプ用のテンプレート生成関数

def generate_api_template(task_id: str, description: str) -> Dict[str, Any]:
    """API実装用の高品質テンプレート"""
    return {
        'type': 'api',
        'files': {
            'api_implementation.py': f'''"""
API実装: {description}
タスクID: {task_id}
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="{description}",
    description="APIサーバー実装",
    version="1.0.0"
)

security = HTTPBearer()

# データモデル
class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    
class ItemResponse(ItemCreate):
    id: int
    created_at: str

# 仮のデータストア
items_db = []
item_id_counter = 1

# ミドルウェア：認証
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # TODO: 実際のトークン検証ロジック
    if token != "valid_token":
        raise HTTPException(status_code=401, detail="Invalid token")
    return token

# エンドポイント
@app.get("/")
async def root():
    return {{"message": "API稼働中", "version": "1.0.0"}}

@app.get("/health")
async def health_check():
    return {{"status": "healthy", "timestamp": "{datetime.now().isoformat()}"}}

@app.get("/api/v1/items", response_model=List[ItemResponse])
async def list_items(
    skip: int = 0,
    limit: int = 10,
    token: str = Depends(verify_token)
):
    """アイテム一覧取得（ページネーション対応）"""
    logger.info(f"Fetching items: skip={{skip}}, limit={{limit}}")
    return items_db[skip:skip+limit]

@app.post("/api/v1/items", response_model=ItemResponse, status_code=201)
async def create_item(
    item: ItemCreate,
    token: str = Depends(verify_token)
):
    """アイテム作成"""
    global item_id_counter
    new_item = ItemResponse(
        id=item_id_counter,
        **item.dict(),
        created_at=datetime.now().isoformat()
    )
    items_db.append(new_item)
    item_id_counter += 1
    logger.info(f"Created item: {{new_item.id}}")
    return new_item

@app.get("/api/v1/items/{{item_id}}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    token: str = Depends(verify_token)
):
    """特定アイテム取得"""
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
''',
            'README.md': f'''# API実装: {description}

## 📋 概要
タスクID: {task_id}

## 🚀 クイックスタート
```bash
# 依存関係インストール
pip install fastapi uvicorn pydantic

# サーバー起動
python api_implementation.py
```

## 📚 API仕様

### エンドポイント一覧

#### 1. ヘルスチェック
```
GET /health
```

#### 2. アイテム一覧取得
```
GET /api/v1/items?skip=0&limit=10
Authorization: Bearer {{token}}
```

#### 3. アイテム作成
```
POST /api/v1/items
Authorization: Bearer {{token}}
Content-Type: application/json

{{
  "name": "サンプル",
  "description": "説明",
  "price": 1000
}}
```

## 🧪 テスト方法
```bash
# curlでテスト
curl -X GET http://localhost:8000/health

# Pythonでテスト
python test_api.py
```

## 📊 パフォーマンス
- レスポンスタイム: < 50ms
- スループット: 1000 req/sec

---
生成日時: {datetime.now().isoformat()}
''',
            'test_api.py': '''import requests

def test_api():
    base_url = "http://localhost:8000"
    token = "valid_token"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Health check
    response = requests.get(f"{base_url}/health")
    assert response.status_code == 200
    
    # Create item
    response = requests.post(
        f"{base_url}/api/v1/items",
        headers=headers,
        json={"name": "Test", "description": "Test item", "price": 100}
    )
    assert response.status_code == 201
    
    print("✅ All tests passed!")

if __name__ == "__main__":
    test_api()
'''
        }
    }


def generate_database_template(task_id: str, description: str) -> Dict[str, Any]:
    """データベース実装用の高品質テンプレート"""
    return {
        'type': 'database',
        'files': {
            'database_handler.py': f'''"""
データベース実装: {description}
タスクID: {task_id}
"""
import sqlite3
from typing import List, Dict, Optional, Any
from contextlib import contextmanager
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseHandler:
    """データベース操作クラス（SQLite）"""
    
    def __init__(self, db_path: str = "app.db"):
        self.db_path = db_path
        self.initialize()
    
    @contextmanager
    def get_connection(self):
        """安全なDB接続コンテキストマネージャー"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {{e}}")
            raise
        finally:
            conn.close()
    
    def initialize(self):
        """テーブル初期化"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # usersテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # itemsテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # インデックス作成
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_user_id ON items(user_id)")
            
            logger.info("Database initialized successfully")
    
    # CRUD操作
    def create_user(self, username: str, email: str, password_hash: str) -> int:
        """ユーザー作成"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            logger.info(f"Created user: {{username}}")
            return cursor.lastrowid
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """メールアドレスでユーザー取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def create_item(self, user_id: int, name: str, description: str = "") -> int:
        """アイテム作成"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO items (user_id, name, description) VALUES (?, ?, ?)",
                (user_id, name, description)
            )
            logger.info(f"Created item: {{name}} for user {{user_id}}")
            return cursor.lastrowid
    
    def get_items_by_user(self, user_id: int) -> List[Dict]:
        """ユーザーのアイテム一覧取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM items WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def update_item_status(self, item_id: int, status: str) -> bool:
        """アイテムステータス更新"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE items SET status = ? WHERE id = ?",
                (status, item_id)
            )
            return cursor.rowcount > 0
    
    def delete_item(self, item_id: int) -> bool:
        """アイテム削除（論理削除）"""
        return self.update_item_status(item_id, 'deleted')
    
    def get_statistics(self) -> Dict[str, Any]:
        """統計情報取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
            active_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM items WHERE status = 'active'")
            active_items = cursor.fetchone()[0]
            
            return {{
                'active_users': active_users,
                'active_items': active_items,
                'timestamp': datetime.now().isoformat()
            }}

# 使用例
if __name__ == "__main__":
    db = DatabaseHandler()
    
    # ユーザー作成
    user_id = db.create_user("testuser", "test@example.com", "hashed_password")
    print(f"Created user ID: {{user_id}}")
    
    # アイテム作成
    item_id = db.create_item(user_id, "Sample Item", "This is a test")
    print(f"Created item ID: {{item_id}}")
    
    # 統計取得
    stats = db.get_statistics()
    print(f"Statistics: {{stats}}")
''',
            'README.md': f'''# データベース実装: {description}

## 📋 概要
タスクID: {task_id}

## 🗄️ テーブル設計

### users
| カラム | 型 | 制約 | 説明 |
|--------|-----|------|------|
| id | INTEGER | PK | ユーザーID |
| username | TEXT | UNIQUE | ユーザー名 |
| email | TEXT | UNIQUE | メールアドレス |

### items
| カラム | 型 | 制約 | 説明 |
|--------|-----|------|------|
| id | INTEGER | PK | アイテムID |
| user_id | INTEGER | FK | ユーザーID |
| name | TEXT | NOT NULL | アイテム名 |

## 🚀 使用方法
```python
from database_handler import DatabaseHandler

db = DatabaseHandler()
user_id = db.create_user("username", "email@example.com", "hash")
```

---
生成日時: {datetime.now().isoformat()}
'''
        }
    }


def generate_testing_template(task_id: str, description: str) -> Dict[str, Any]:
    """テスト実装用の高品質テンプレート"""
    return {
        'type': 'testing',
        'files': {
            'test_suite.py': f'''"""
テストスイート: {description}
タスクID: {task_id}
"""
import pytest
import unittest
from typing import Any
import time

class ComprehensiveTestSuite(unittest.TestCase):
    """包括的テストスイート"""
    
    @classmethod
    def setUpClass(cls):
        """テストクラス開始前の準備"""
        print("\\n" + "="*70)
        print(f"テストスイート開始: {description}")
        print("="*70)
    
    def setUp(self):
        """各テストメソッド実行前の準備"""
        self.start_time = time.time()
    
    def tearDown(self):
        """各テストメソッド実行後の処理"""
        elapsed = time.time() - self.start_time
        print(f"  実行時間: {{elapsed:.3f}}秒")
    
    # 機能テスト
    def test_001_basic_functionality(self):
        """基本機能が正常に動作することを確認"""
        result = self._execute_function({{"test": "data"}})
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'success')
    
    def test_002_input_validation(self):
        """入力検証が正しく機能することを確認"""
        # 空入力
        with self.assertRaises(ValueError):
            self._execute_function({{}})
        
        # 不正な型
        with self.assertRaises(TypeError):
            self._execute_function(None)
    
    def test_003_boundary_values(self):
        """境界値での動作を確認"""
        # 最小値
        result = self._execute_function({{"value": 0}})
        self.assertIsNotNone(result)
        
        # 最大値
        result = self._execute_function({{"value": 999999}})
        self.assertIsNotNone(result)
    
    def test_004_error_handling(self):
        """エラーハンドリングが適切に機能することを確認"""
        with self.assertRaises(Exception):
            self._execute_function({{"error": True}})
    
    def test_005_performance(self):
        """パフォーマンス要件を満たすことを確認"""
        start = time.time()
        for _ in range(100):
            self._execute_function({{"quick": True}})
        elapsed = time.time() - start
        
        # 100回の実行が1秒以内
        self.assertLess(elapsed, 1.0, "Performance requirement not met")
    
    def test_006_concurrent_execution(self):
        """並行実行時の動作を確認"""
        from concurrent.futures import ThreadPoolExecutor
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(self._execute_function, {{"id": i}})
                for i in range(10)
            ]
            results = [f.result() for f in futures]
        
        self.assertEqual(len(results), 10)
        self.assertTrue(all(r['status'] == 'success' for r in results))
    
    def test_007_data_integrity(self):
        """データ整合性が保たれることを確認"""
        data = {{"id": 1, "name": "test"}}
        result = self._execute_function(data)
        
        # 入力データが変更されていないことを確認
        self.assertEqual(data, {{"id": 1, "name": "test"}})
    
    def test_008_idempotency(self):
        """冪等性を確認（同じ操作を複数回実行しても結果が同じ）"""
        input_data = {{"action": "test"}}
        result1 = self._execute_function(input_data)
        result2 = self._execute_function(input_data)
        
        self.assertEqual(result1, result2)
    
    def _execute_function(self, data: dict) -> dict:
        """テスト対象の関数"""
        if data is None:
            raise TypeError("Data cannot be None")
        if not data:
            raise ValueError("Data cannot be empty")
        if data.get("error"):
            raise Exception("Intentional error for testing")
        
        return {{"status": "success", "data": data}}
    
    @classmethod
    def tearDownClass(cls):
        """テストクラス終了後の処理"""
        print("="*70)
        print("テストスイート完了")
        print("="*70)

# pytest互換のテスト関数
@pytest.mark.parametrize("input_value,expected", [
    (1, True),
    (0, True),
    (-1, False),
])
def test_parametrized(input_value, expected):
    """パラメータ化テスト"""
    result = input_value >= 0
    assert result == expected

if __name__ == "__main__":
    unittest.main(verbosity=2)
''',
            'README.md': f'''# テストスイート: {description}

## 📋 概要
タスクID: {task_id}

## 🧪 テストケース一覧

| # | テスト名 | カテゴリ | 説明 |
|---|----------|----------|------|
| 001 | basic_functionality | 機能 | 基本機能テスト |
| 002 | input_validation | バリデーション | 入力検証テスト |
| 003 | boundary_values | 境界値 | 境界値テスト |
| 004 | error_handling | エラー | エラーハンドリングテスト |
| 005 | performance | 性能 | パフォーマンステスト |
| 006 | concurrent_execution | 並行性 | 並行実行テスト |
| 007 | data_integrity | 整合性 | データ整合性テスト |
| 008 | idempotency | 冪等性 | 冪等性テスト |

## 🚀 実行方法
```bash
# unittest
python test_suite.py

# pytest
pytest test_suite.py -v

# カバレッジ
pytest test_suite.py --cov --cov-report=html
```

## ✅ 成功基準
- 全テスト: PASS
- カバレッジ: >80%
- パフォーマンス: 基準値以内

---
生成日時: {datetime.now().isoformat()}
'''
        }
    }
