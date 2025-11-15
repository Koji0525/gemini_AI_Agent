"""
タスクタイプ自動検出システム

タスクの説明文から最適なテンプレートタイプを自動判定
"""

from typing import Dict, List, Tuple, Optional
from pathlib import Path
import re


class TaskTypeDetector:
    """タスクタイプ自動検出"""
    
    def __init__(self):
        # タスクタイプごとのキーワード定義
        self.keywords = {
            "api": {
                "primary": ["API", "REST", "RESTful", "エンドポイント", "FastAPI"],
                "secondary": ["HTTP", "リクエスト", "レスポンス", "JSON", "CRUD"]
            },
            "data": {
                "primary": ["データ処理", "データ分析", "pandas", "CSV", "Excel"],
                "secondary": ["集計", "変換", "クリーニング", "ETL", "データセット"]
            },
            "web": {
                "primary": ["Webアプリ", "Web", "Flask", "Django", "フロントエンド"],
                "secondary": ["HTML", "UI", "画面", "ページ", "ブラウザ"]
            },
            "test": {
                "primary": ["テスト", "pytest", "unittest", "テストコード"],
                "secondary": ["検証", "品質保証", "QA", "カバレッジ"]
            },
            "cli": {
                "primary": ["CLI", "コマンドライン", "Click", "コマンド"],
                "secondary": ["引数", "オプション", "サブコマンド", "ターミナル"]
            },
            "docs": {
                "primary": ["ドキュメント", "仕様書", "README", "マニュアル"],
                "secondary": ["説明", "ガイド", "手順書", "API仕様"]
            }
        }
        
        # テンプレートマッピング
        self.template_map = {
            "api": {
                "code": "api/fastapi_rest.py",
                "readme": "api/README_fastapi.md",
                "requirements": ["fastapi==0.104.0", "uvicorn[standard]==0.24.0", "pydantic==2.4.0"]
            },
            "data": {
                "code": "data/pandas_pipeline.py",
                "readme": "data/README_pandas.md",
                "requirements": ["pandas==2.1.0", "numpy==1.24.0", "openpyxl==3.1.0"]
            },
            "web": {
                "code": "web/flask_app.py",
                "readme": "web/README.md",
                "requirements": ["Flask==3.0.0", "Flask-SQLAlchemy==3.1.0", "Flask-CORS==4.0.0"]
            },
            "test": {
                "code": "test/pytest_suite.py",
                "readme": "test/README.md",
                "requirements": ["pytest==7.4.0", "pytest-cov==4.1.0", "pytest-mock==3.11.0"]
            },
            "cli": {
                "code": "cli_detailed.py",
                "readme": "readme_detailed.md",
                "requirements": ["click>=8.0.0"]
            },
            "docs": {
                "code": None,
                "readme": "docs/technical_spec.md",
                "requirements": []
            }
        }
    
    def detect(self, description: str) -> str:
        """タスクタイプを検出
        
        Args:
            description: タスクの説明文
        
        Returns:
            検出されたタスクタイプ (api, data, web, test, cli, docs)
        """
        scores = self._calculate_scores(description)
        
        if not scores:
            # デフォルトはCLI
            return "cli"
        
        # 最高スコアのタイプを返す
        best_type = max(scores.items(), key=lambda x: x[1])
        
        print(f"  🔍 タスクタイプ検出:")
        for task_type, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"    - {task_type}: {score}点")
        
        return best_type[0]
    
    def _calculate_scores(self, description: str) -> Dict[str, int]:
        """各タスクタイプのスコアを計算"""
        scores = {}
        
        description_lower = description.lower()
        
        for task_type, keywords in self.keywords.items():
            score = 0
            
            # プライマリキーワード: 10点
            for keyword in keywords["primary"]:
                if keyword.lower() in description_lower:
                    score += 10
            
            # セカンダリキーワード: 3点
            for keyword in keywords["secondary"]:
                if keyword.lower() in description_lower:
                    score += 3
            
            if score > 0:
                scores[task_type] = score
        
        return scores
    
    def get_template_info(self, task_type: str) -> Dict:
        """テンプレート情報を取得"""
        return self.template_map.get(task_type, self.template_map["cli"])
    
    def get_all_types(self) -> List[str]:
        """利用可能な全タスクタイプを取得"""
        return list(self.keywords.keys())


# ========================================
# 使用例とテスト
# ========================================

if __name__ == "__main__":
    detector = TaskTypeDetector()
    
    # テストケース
    test_cases = [
        "RESTful APIを実装する",
        "データ分析パイプラインを作成",
        "Flask Webアプリケーション開発",
        "pytestでテストコードを書く",
        "CLIツールをClickで実装",
        "技術仕様書を作成",
        "ユーザー認証機能の実装",  # 曖昧なケース
    ]
    
    print("="*60)
    print("タスクタイプ検出テスト")
    print("="*60)
    
    for description in test_cases:
        print(f"\n📝 タスク: {description}")
        task_type = detector.detect(description)
        template_info = detector.get_template_info(task_type)
        
        print(f"  ✅ 検出結果: {task_type}")
        print(f"  📄 テンプレート: {template_info['code']}")
        print(f"  📦 必要パッケージ: {', '.join(template_info['requirements'][:2])}")
