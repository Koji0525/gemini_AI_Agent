"""wp_cpt_agent.py - WordPressカスタム投稿タイプ管理（API版）"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from config.config_loader import config
import aiohttp


class WordPressCPTAgent:
    """WordPressカスタム投稿タイプ管理機能（コード生成版）"""

    def __init__(self, wp_credentials: Dict = None):
        self.wp_credentials = wp_credentials or {
            "url": config.WP_URL,
            "username": config.WP_USER,
            "password": config.WP_PASS,
        }
        self.base_url = self.wp_credentials["url"]

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        タスクを実行（統一インターフェース）

        Args:
            task: 実行するタスク

        Returns:
            実行結果
        """
        print("📝 WordPress CPTマネージャ: 実行開始")

        try:
            task_type = task.get("type", "unknown")

            if task_type == "create_post_type":
                return await self.create_post_type(task)
            elif task_type == "list_post_types":
                return await self.list_post_types(task)
            elif task_type == "generate_php_code":
                return await self.generate_php_code(task)
            else:
                return {"success": False, "error": f"未知のタスクタイプ: {task_type}", "task_type": task_type}

        except Exception as e:
            print(f"❌ CPTマネージャ実行エラー: {e}")
            return {"success": False, "error": str(e), "task_type": task.get("type", "unknown")}

    async def create_post_type(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        カスタム投稿タイプを作成

        Args:
            task: タスクデータ

        Returns:
            実行結果
        """
        print("📝 カスタム投稿タイプを作成します")

        post_type_data = task.get("post_type_data", {})

        if not post_type_data:
            return {"success": False, "error": "投稿タイプデータが指定されていません"}

        # 必須フィールドの確認
        name = post_type_data.get("name", "")
        slug = post_type_data.get("slug", "")

        if not name or not slug:
            return {"success": False, "error": "投稿タイプ名(name)とスラッグ(slug)は必須です"}

        # PHPコードを生成
        php_code = self._generate_post_type_php_code(post_type_data)

        return {
            "success": True,
            "message": f"カスタム投稿タイプ '{name}' のPHPコードを生成しました",
            "post_type": post_type_data,
            "php_code": php_code,
            "implementation_notes": self._get_implementation_notes(),
        }

    async def list_post_types(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        登録済みの投稿タイプを一覧表示

        Args:
            task: タスクデータ

        Returns:
            実行結果
        """
        print("📝 投稿タイプ一覧を取得します")

        return {
            "success": True,
            "message": "投稿タイプ一覧機能（スタブ実装）",
            "note": "実際の実装ではWordPress REST APIを使用して登録済み投稿タイプを取得します",
            "common_post_types": ["post", "page", "attachment", "revision", "nav_menu_item"],
        }

    async def generate_php_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        PHPコードのみを生成

        Args:
            task: タスクデータ

        Returns:
            実行結果
        """
        print("📝 カスタム投稿タイプのPHPコードを生成します")

        post_type_data = task.get("post_type_data", {})

        if not post_type_data:
            return {"success": False, "error": "投稿タイプデータが指定されていません"}

        php_code = self._generate_post_type_php_code(post_type_data)

        return {"success": True, "message": "カスタム投稿タイプのPHPコードを生成しました", "php_code": php_code}

    def _generate_post_type_php_code(self, post_type_data: Dict[str, Any]) -> str:
        """
        カスタム投稿タイプのPHPコードを生成

        Args:
            post_type_data: 投稿タイプデータ

        Returns:
            PHPコード
        """
        name = post_type_data.get("name", "未設定")
        slug = post_type_data.get("slug", "custom_post_type")
        description = post_type_data.get("description", "")

        # デフォルトの設定
        labels = post_type_data.get("labels", {})
        if not labels:
            labels = {
                "name": name,
                "singular_name": name,
                "menu_name": name,
                "name_admin_bar": name,
                "add_new": "新規追加",
                "add_new_item": f"新規{name}を追加",
                "edit_item": f"{name}を編集",
                "new_item": f"新規{name}",
                "view_item": f"{name}を表示",
                "view_items": f"{name}一覧を表示",
                "search_items": f"{name}を検索",
                "not_found": f"{name}が見つかりません",
                "not_found_in_trash": "ゴミ箱内に{name}が見つかりません",
                "all_items": f"すべての{name}",
                "archives": f"{name}アーカイブ",
                "attributes": f"{name}属性",
                "insert_into_item": f"{name}に挿入",
                "uploaded_to_this_item": f"この{name}にアップロード",
            }

        # 引数の設定
        args = post_type_data.get("args", {})
        if not args:
            args = {
                "label": name,
                "description": description,
                "public": post_type_data.get("public", True),
                "has_archive": post_type_data.get("has_archive", True),
                "show_ui": True,
                "show_in_menu": True,
                "show_in_rest": post_type_data.get("show_in_rest", True),
                "rest_base": slug,
                "menu_position": post_type_data.get("menu_position", 5),
                "menu_icon": post_type_data.get("menu_icon", "dashicons-admin-post"),
                "capability_type": "post",
                "supports": post_type_data.get("supports", ["title", "editor", "thumbnail"]),
                "taxonomies": post_type_data.get("taxonomies", []),
                "hierarchical": False,
            }

        # PHPコードの生成
        php_code = f"""
// カスタム投稿タイプ: {name}
function register_custom_post_type_{slug}() {{
    $labels = array(
        {self._generate_labels_php_code(labels)}
    );

    $args = array(
        {self._generate_args_php_code(args)}
    );

    register_post_type('{slug}', $args);
}}
add_action('init', 'register_custom_post_type_{slug}');
"""
        return php_code

    def _generate_labels_php_code(self, labels: Dict[str, str]) -> str:
        """
        ラベルのPHPコードを生成

        Args:
            labels: ラベルデータ

        Returns:
            PHPコード
        """
        label_lines = []
        for key, value in labels.items():
            label_lines.append(f"'{key}' => '{value}',")

        return "\n        ".join(label_lines)

    def _generate_args_php_code(self, args: Dict[str, Any]) -> str:
        """
        引数のPHPコードを生成

        Args:
            args: 引数データ

        Returns:
            PHPコード
        """
        arg_lines = []
        for key, value in args.items():
            if isinstance(value, bool):
                php_value = "true" if value else "false"
            elif isinstance(value, list):
                # 安全なリストの生成
                items = ", ".join([f"'{item}'" for item in value])
                php_value = f"array({items})"
            elif isinstance(value, int):
                php_value = str(value)
            else:
                php_value = f"'{value}'"

            arg_lines.append(f"'{key}' => {php_value},")

        return "\n        ".join(arg_lines)

    def _get_implementation_notes(self) -> str:
        """
        実装に関する注意事項を取得

        Returns:
            注意事項
        """
        return """
実装手順:
1. 生成されたPHPコードをテーマのfunctions.phpファイルに追加
2. WordPress管理画面を更新
3. 新しい投稿タイプがメニューに表示されることを確認

注意点:
- スラッグは一意である必要があります
- 既存の投稿タイプや予約語と重複しないようにしてください
- 本番環境では必ずテストを行ってください
"""


# テスト用の簡単な実行コード
if __name__ == "__main__":

    async def test():
        """テスト実行"""
        agent = WordPressCPTAgent()

        # カスタム投稿タイプ作成テスト
        task = {
            "type": "create_post_type",
            "post_type_data": {
                "name": "テスト投稿タイプ",
                "slug": "test_cpt",
                "description": "統合テスト用のカスタム投稿タイプ",
                "public": True,
                "has_archive": True,
                "supports": ["title", "editor", "thumbnail"],
                "menu_position": 5,
                "menu_icon": "dashicons-admin-post",
            },
        }

        result = await agent.execute(task)
        print(f"CPTエージェントテスト結果: {result['success']}")

        if result["success"]:
            print("✅ PHPコード生成成功")
            print(result["php_code"])

    asyncio.run(test())
