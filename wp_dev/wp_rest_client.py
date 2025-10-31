#!/usr/bin/env python3
"""
WordPress REST API クライアント（軽量版）
変更理由: playwright依存を排除し、直接REST APIで通信
"""

import requests
from typing import Dict, Optional
import json


class WordPressRESTClient:
    """WordPress REST API 直接通信クライアント"""

    def __init__(self, wp_url: str, wp_user: str, wp_pass: str):
        self.wp_url = wp_url.rstrip("/")
        self.api_base = f"{self.wp_url}/wp-json/wp/v2"
        self.auth = (wp_user, wp_pass)

    def test_connection(self) -> bool:
        """接続テスト"""
        try:
            response = requests.get(self.api_base, auth=self.auth, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ 接続エラー: {e}")
            return False

    def create_post(self, post_data: Dict) -> Dict:
        """投稿作成"""
        url = f"{self.api_base}/posts"

        try:
            response = requests.post(url, json=post_data, auth=self.auth, timeout=30)

            if response.status_code in [200, 201]:
                return {"success": True, "data": response.json(), "message": "投稿作成成功"}
            else:
                return {"success": False, "error": response.text, "status_code": response.status_code}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_posts(self, post_type: str = "posts", params: Dict = None) -> Dict:
        """投稿取得"""
        url = f"{self.api_base}/{post_type}"

        try:
            response = requests.get(url, params=params or {}, auth=self.auth, timeout=30)

            if response.status_code == 200:
                return {"success": True, "data": response.json(), "total": response.headers.get("X-WP-Total", 0)}
            else:
                return {"success": False, "error": response.text}

        except Exception as e:
            return {"success": False, "error": str(e)}
