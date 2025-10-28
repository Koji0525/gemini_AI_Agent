#!/usr/bin/env python3
"""
WordPressタクソノミーエージェント v01 - 基本機能
タクソノミー（分類）の作成と管理を担当
"""
import asyncio
from pathlib import Path
from typing import Dict, Any, List
import json


class WordPressTaxonomyAgent:
    """WordPressタクソノミーエージェント"""

    def __init__(self, browser, output_folder: Path = None):
        self.browser = browser
        self.output_folder = output_folder or Path("agent_outputs/taxonomies")
        self.output_folder.mkdir(parents=True, exist_ok=True)

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """タスクを実行"""
        print("📋 WordPressタクソノミーエージェント: 実行開始")

        try:
            task_type = task.get("type", "unknown")

            if task_type == "taxonomy_creation":
                return await self.create_taxonomy(task)
            else:
                return {"success": False, "error": f"未知のタスクタイプ: {task_type}", "task_type": task_type}

        except Exception as e:
            return {"success": False, "error": str(e), "task_type": task.get("type", "unknown")}

    async def create_taxonomy(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """タクソノミーを作成"""
        taxonomy_spec = task.get("taxonomy_spec", {})
        taxonomy_name = taxonomy_spec.get("name", "unknown")

        print(f"🏷️ タクソノミー作成: {taxonomy_name}")

        # タクソノミー仕様の検証
        if not await self._validate_taxonomy_spec(taxonomy_spec):
            return {"success": False, "error": "タクソノミー仕様が無効です", "taxonomy_name": taxonomy_name}

        # PHPコードを生成
        php_code = self._generate_taxonomy_php_code(taxonomy_spec)

        # ファイルに保存
        file_path = await self._save_taxonomy_code(php_code, taxonomy_name, task.get("task_id", "unknown"))

        return {
            "success": True,
            "taxonomy_name": taxonomy_name,
            "php_file": str(file_path),
            "code_preview": php_code[:200] + "..." if len(php_code) > 200 else php_code,
        }

    async def _validate_taxonomy_spec(self, taxonomy_spec: Dict[str, Any]) -> bool:
        """タクソノミー仕様を検証"""
        required_fields = ["name", "post_types"]
        for field in required_fields:
            if field not in taxonomy_spec:
                print(f"❌ 必須フィールド '{field}' がありません")
                return False

        return True

    def _generate_taxonomy_php_code(self, taxonomy_spec: Dict[str, Any]) -> str:
        """タクソノミー用PHPコードを生成"""
        name = taxonomy_spec["name"]
        post_types = taxonomy_spec["post_types"]
        hierarchical = taxonomy_spec.get("hierarchical", False)
        show_ui = taxonomy_spec.get("show_ui", True)
        show_admin_column = taxonomy_spec.get("show_admin_column", True)

        php_code = f"""/**
 * タクソノミー: {name}
 * 関連投稿タイプ: {', '.join(post_types)}
 */

function register_{name}_taxonomy() {{
    $labels = array(
        'name'              => _x('{name.capitalize()}s', 'taxonomy general name'),
        'singular_name'     => _x('{name.capitalize()}', 'taxonomy singular name'),
        'search_items'      => __('Search {name.capitalize()}s'),
        'all_items'         => __('All {name.capitalize()}s'),
        'parent_item'       => __('Parent {name.capitalize()}'),
        'parent_item_colon' => __('Parent {name.capitalize()}:'),
        'edit_item'         => __('Edit {name.capitalize()}'),
        'update_item'       => __('Update {name.capitalize()}'),
        'add_new_item'      => __('Add New {name.capitalize()}'),
        'new_item_name'     => __('New {name.capitalize()} Name'),
        'menu_name'         => __('{name.capitalize()}s'),
    );

    $args = array(
        'hierarchical'      => {str(hierarchical).lower()},
        'labels'            => $labels,
        'show_ui'           => {str(show_ui).lower()},
        'show_admin_column' => {str(show_admin_column).lower()},
        'query_var'         => true,
        'rewrite'           => array('slug' => '{name}'),
    );

    register_taxonomy('{name}', {self._format_post_types(post_types)}, $args);
}}
add_action('init', 'register_{name}_taxonomy');
"""
        return php_code

    def _format_post_types(self, post_types: List[str]) -> str:
        """投稿タイプをPHP配列形式に変換"""
        if len(post_types) == 1:
            return f"'{post_types[0]}'"
        else:
            formatted = ", ".join([f"'{pt}'" for pt in post_types])
            return f"array({formatted})"

    async def _save_taxonomy_code(self, php_code: str, taxonomy_name: str, task_id: str) -> Path:
        """タクソノミーコードをファイルに保存"""
        filename = f"taxonomy_{taxonomy_name}_{task_id}.php"
        file_path = self.output_folder / filename

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("<?php\n")
            f.write(php_code)

        print(f"💾 タクソノミーコードを保存: {file_path}")
        return file_path


async def test_taxonomy_agent():
    """タクソノミーエージェントのテスト"""
    try:
        print("🧪 タクソノミーエージェントテスト開始")

        # モックブラウザを使用
        class MockBrowser:
            pass

        browser = MockBrowser()
        agent = WordPressTaxonomyAgent(browser)

        # テストタスク
        test_task = {
            "type": "taxonomy_creation",
            "taxonomy_spec": {
                "name": "industry_category",
                "post_types": ["ma_case"],
                "hierarchical": True,
                "show_ui": True,
                "show_admin_column": True,
            },
            "task_id": "test_001",
        }

        result = await agent.execute(test_task)

        print("📊 テスト結果:")
        print(f"  成功: {result.get('success')}")
        if result.get("success"):
            print(f"  タクソノミー: {result.get('taxonomy_name')}")
            print(f"  ファイル: {result.get('php_file')}")
        else:
            print(f"  エラー: {result.get('error')}")

    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_taxonomy_agent())
