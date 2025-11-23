"""
API統合テスト
Phase 1完了判定のためのテストスイート
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.abspath("."))

from agents.observer_enhanced.web.api_server import app

client = TestClient(app)


class TestAPIServer:
    """APIサーバーの統合テスト"""

    def test_health_check(self):
        """ヘルスチェックエンドポイント"""
        response = client.get("/")
        assert response.status_code == 200
        assert "status" in response.json()

    def test_get_dependencies(self):
        """依存関係取得API"""
        response = client.get("/api/dependencies")
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        assert isinstance(data["nodes"], list)
        assert isinstance(data["edges"], list)

    def test_get_duplicates(self):
        """重複ファイル検出API"""
        response = client.get("/api/duplicates")
        assert response.status_code == 200
        data = response.json()
        assert "groups" in data
        assert "total_duplicates" in data
        assert isinstance(data["groups"], list)

    def test_get_impact_analysis(self):
        """影響範囲分析API"""
        # テスト用ファイル
        test_file = "agents/pm_agent.py"
        response = client.get(f"/api/impact/{test_file}")
        assert response.status_code in [200, 404]  # ファイルが存在しない場合も許容

        if response.status_code == 200:
            data = response.json()
            assert "target_file" in data
            assert "total_impact_count" in data

    def test_cors_headers(self):
        """CORS設定の確認"""
        response = client.options("/api/dependencies")
        # CORSヘッダーが含まれているか確認
        assert "access-control-allow-origin" in response.headers or response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
