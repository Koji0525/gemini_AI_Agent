"""wp_taxonomy_agent.py - WordPress分類法管理（API版）"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from config.config_loader import config
import aiohttp


class WordPressTaxonomyAgent:
    """WordPress分類法管理機能（REST API版）"""

    def __init__(self, wp_credentials: Dict = None):
        self.wp_credentials = wp_credentials or {
            "url": config.WP_URL,
            "username": config.WP_USER,
            "password": config.WP_PASS,
        }
        self.base_url = self.wp_credentials["url"]
        self.api_base = f"{self.base_url}/wp-json/wp/v2"

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        タスクを実行（統一インターフェース）

        Args:
            task: 実行するタスク

        Returns:
            実行結果
        """
        print("🏷️ WordPress分類法マネージャ: 実行開始")

        try:
            task_type = task.get("type", "unknown")

            if task_type == "create_taxonomy":
                return await self.create_taxonomy(task)
            elif task_type == "create_term":
                return await self.create_term(task)
            elif task_type == "list_taxonomies":
                return await self.list_taxonomies(task)
            else:
                return {"success": False, "error": f"未知のタスクタイプ: {task_type}", "task_type": task_type}

        except Exception as e:
            print(f"❌ 分類法マネージャ実行エラー: {e}")
            return {"success": False, "error": str(e), "task_type": task.get("type", "unknown")}

    async def _make_api_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """
        WordPress REST APIリクエストを実行

        Args:
            endpoint: APIエンドポイント
            method: HTTPメソッド
            data: 送信データ

        Returns:
            APIレスポンス
        """
        url = f"{self.api_base}/{endpoint}"
        auth = aiohttp.BasicAuth(self.wp_credentials["username"], self.wp_credentials["password"])

        try:
            async with aiohttp.ClientSession(auth=auth) as session:
                if method.upper() == "GET":
                    async with session.get(url) as response:
                        return await self._handle_response(response)
                elif method.upper() == "POST":
                    async with session.post(url, json=data) as response:
                        return await self._handle_response(response)
                elif method.upper() == "PUT":
                    async with session.put(url, json=data) as response:
                        return await self._handle_response(response)
                elif method.upper() == "DELETE":
                    async with session.delete(url) as response:
                        return await self._handle_response(response)
                else:
                    return {"success": False, "error": f"未対応のHTTPメソッド: {method}"}
        except Exception as e:
            return {"success": False, "error": f"APIリクエストエラー: {str(e)}"}

    async def _handle_response(self, response) -> Dict[str, Any]:
        """
        APIレスポンスを処理

        Args:
            response: aiohttpレスポンス

        Returns:
            処理結果
        """
        try:
            response_data = await response.json()

            if response.status in [200, 201]:
                return {"success": True, "data": response_data, "status_code": response.status}
            else:
                return {
                    "success": False,
                    "error": f"APIエラー: {response.status} - {response_data}",
                    "status_code": response.status,
                    "data": response_data,
                }
        except Exception as e:
            return {"success": False, "error": f"レスポンス解析エラー: {str(e)}", "status_code": response.status}

    async def create_taxonomy(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        カスタム分類法を作成

        Args:
            task: タスクデータ

        Returns:
            実行結果
        """
        print("🏷️ カスタム分類法を作成します")

        taxonomy_data = {
            "name": task.get("name", "Unknown Taxonomy"),
            "slug": task.get("slug", ""),
            "description": task.get("description", ""),
            "hierarchical": task.get("hierarchical", True),
            "show_ui": task.get("show_ui", True),
            "show_in_menu": task.get("show_in_menu", True),
            "show_in_rest": task.get("show_in_rest", True),
            "rest_base": task.get("rest_base", ""),
            "rest_controller_class": "WP_REST_Terms_Controller",
        }

        # 注意: WordPressコアAPIでは分類法の直接作成はできないため、
        # カスタム分類法は通常、テーマやプラグインのコードで登録されます
        # ここでは代替実装を提供

        result = {
            "success": True,
            "message": "カスタム分類法の作成要件を生成しました（実際の登録にはコード実装が必要）",
            "taxonomy_data": taxonomy_data,
            "php_code": self._generate_taxonomy_php_code(taxonomy_data),
        }

        return result

    def _generate_taxonomy_php_code(self, taxonomy_data: Dict[str, Any]) -> str:
        """
        カスタム分類法のPHPコードを生成

        Args:
            taxonomy_data: 分類法データ

        Returns:
            PHPコード
        """
        php_code = f"""
// カスタム分類法の登録
function register_custom_taxonomy_{taxonomy_data['slug']}() {{
    $labels = array(
        'name' => '{taxonomy_data['name']}',
        'singular_name' => '{taxonomy_data['name']}',
        'search_items' => '{taxonomy_data['name']}を検索',
        'all_items' => 'すべての{taxonomy_data['name']}',
        'parent_item' => '親{taxonomy_data['name']}',
        'parent_item_colon' => '親{taxonomy_data['name']}:',
        'edit_item' => '{taxonomy_data['name']}を編集',
        'update_item' => '{taxonomy_data['name']}を更新',
        'add_new_item' => '新規{taxonomy_data['name']}を追加',
        'new_item_name' => '新規{taxonomy_data['name']}名',
        'menu_name' => '{taxonomy_data['name']}'
    );

    $args = array(
        'hierarchical' => { 'true' if taxonomy_data['hierarchical'] else 'false' },
        'labels' => $labels,
        'show_ui' => { 'true' if taxonomy_data['show_ui'] else 'false' },
        'show_in_menu' => { 'true' if taxonomy_data['show_in_menu'] else 'false' },
        'show_in_rest' => { 'true' if taxonomy_data['show_in_rest'] else 'false' },
        'show_admin_column' => true,
        'query_var' => true,
        'rewrite' => array('slug' => '{taxonomy_data['slug']}'),
    );

    register_taxonomy('{taxonomy_data['slug']}', array('post'), $args);
}}
add_action('init', 'register_custom_taxonomy_{taxonomy_data['slug']}');
"""
        return php_code

    async def create_term(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        タームを作成

        Args:
            task: タスクデータ

        Returns:
            実行結果
        """
        taxonomy = task.get("taxonomy", "category")
        name = task.get("name", "")
        slug = task.get("slug", "")
        description = task.get("description", "")

        if not name:
            return {"success": False, "error": "ターム名が指定されていません"}

        print(f"🏷️ タームを作成します: {name} (分類法: {taxonomy})")

        term_data = {
            "name": name,
            "slug": slug if slug else name.lower().replace(" ", "-"),
            "description": description,
            "taxonomy": taxonomy,
        }

        # WordPress REST APIを使用してタームを作成
        result = await self._make_api_request(f"terms/{taxonomy}", "POST", term_data)

        if result["success"]:
            return {
                "success": True,
                "message": f"ターム '{name}' を作成しました",
                "term_id": result["data"].get("id"),
                "term_data": result["data"],
            }
        else:
            return result

    async def list_taxonomies(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        利用可能な分類法を一覧表示

        Args:
            task: タスクデータ

        Returns:
            実行結果
        """
        print("🏷️ 分類法一覧を取得します")

        result = await self._make_api_request("taxonomies")

        if result["success"]:
            taxonomies = result["data"]
            taxonomy_list = []

            for slug, taxonomy in taxonomies.items():
                taxonomy_list.append(
                    {
                        "slug": slug,
                        "name": taxonomy.get("name", ""),
                        "description": taxonomy.get("description", ""),
                        "hierarchical": taxonomy.get("hierarchical", False),
                        "rest_base": taxonomy.get("rest_base", ""),
                    }
                )

            return {
                "success": True,
                "message": f"{len(taxonomy_list)}個の分類法を取得しました",
                "taxonomies": taxonomy_list,
            }
        else:
            return result


# テスト用の簡単な実行コード
if __name__ == "__main__":

    async def test():
        """テスト実行"""
        agent = WordPressTaxonomyAgent()

        # 分類法一覧取得テスト
        task = {"type": "list_taxonomies"}

        result = await agent.execute(task)
        print(f"分類法一覧テスト結果: {result['success']}")

        if result["success"]:
            print(f"取得した分類法数: {len(result['taxonomies'])}")

        # ターム作成テスト（必要な場合はコメントを外す）
        # task2 = {
        #     "type": "create_term",
        #     "taxonomy": "category",
        #     "name": "テストカテゴリー"
        # }
        # result2 = await agent.execute(task2)
        # print(f"ターム作成テスト結果: {result2}")

    asyncio.run(test())
