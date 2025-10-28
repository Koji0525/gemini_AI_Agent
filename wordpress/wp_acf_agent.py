"""wp_acf_agent.py - WordPress ACF管理（API/コード生成版）"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from config.config_loader import config
import aiohttp


class WordPressACFAgent:
    """WordPress ACF管理機能（コード生成版）"""

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
        print("🎯 WordPress ACFマネージャ: 実行開始")

        try:
            task_type = task.get("type", "unknown")

            if task_type == "create_field_group":
                return await self.create_field_group(task)
            elif task_type == "create_field":
                return await self.create_field(task)
            elif task_type == "import_field_group":
                return await self.import_field_group(task)
            elif task_type == "export_field_group":
                return await self.export_field_group(task)
            else:
                return {"success": False, "error": f"未知のタスクタイプ: {task_type}", "task_type": task_type}

        except Exception as e:
            print(f"❌ ACFマネージャ実行エラー: {e}")
            return {"success": False, "error": str(e), "task_type": task.get("type", "unknown")}

    async def create_field_group(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        ACFフィールドグループを作成

        Args:
            task: タスクデータ

        Returns:
            実行結果
        """
        print("🎯 ACFフィールドグループを作成します")

        field_group = {
            "title": task.get("title", "未設定フィールドグループ"),
            "key": task.get("key", f"group_{self._generate_random_key()}"),
            "fields": task.get("fields", []),
            "location": task.get("location", [[{"param": "post_type", "operator": "==", "value": "post"}]]),
            "menu_order": task.get("menu_order", 0),
            "position": task.get("position", "normal"),
            "style": task.get("style", "default"),
            "label_placement": task.get("label_placement", "top"),
            "instruction_placement": task.get("instruction_placement", "label"),
            "hide_on_screen": task.get("hide_on_screen", []),
        }

        # PHPコードを生成
        php_code = self._generate_field_group_php_code(field_group)

        return {
            "success": True,
            "message": "ACFフィールドグループのPHPコードを生成しました",
            "field_group": field_group,
            "php_code": php_code,
            "json_export": self._generate_field_group_json(field_group),
        }

    async def create_field(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        ACFフィールドを作成

        Args:
            task: タスクデータ

        Returns:
            実行結果
        """
        print("🎯 ACFフィールドを作成します")

        field = {
            "key": task.get("key", f"field_{self._generate_random_key()}"),
            "label": task.get("label", "未設定フィールド"),
            "name": task.get("name", "unspecified_field"),
            "type": task.get("type", "text"),
            "instructions": task.get("instructions", ""),
            "required": task.get("required", 0),
            "default_value": task.get("default_value", ""),
            "placeholder": task.get("placeholder", ""),
            "wrapper": task.get("wrapper", {"width": "", "class": "", "id": ""}),
        }

        # フィールドタイプに応じた追加設定
        field_type = field["type"]
        if field_type == "text" or field_type == "textarea":
            field["maxlength"] = task.get("maxlength", "")
        elif field_type == "number":
            field["min"] = task.get("min", "")
            field["max"] = task.get("max", "")
            field["step"] = task.get("step", "")
        elif field_type == "select":
            field["choices"] = task.get("choices", {})
            field["multiple"] = task.get("multiple", 0)
            field["ui"] = task.get("ui", 0)
            field["ajax"] = task.get("ajax", 0)
        elif field_type == "repeater":
            field["sub_fields"] = task.get("sub_fields", [])
            field["min"] = task.get("min", "")
            field["max"] = task.get("max", "")
            field["layout"] = task.get("layout", "table")
        elif field_type == "flexible_content":
            field["layouts"] = task.get("layouts", [])
        elif field_type == "group":
            field["sub_fields"] = task.get("sub_fields", [])
        elif field_type == "image" or field_type == "file":
            field["return_format"] = task.get("return_format", "array")
            field["preview_size"] = task.get("preview_size", "medium")
            field["library"] = task.get("library", "all")
            field["min_size"] = task.get("min_size", "")
            field["max_size"] = task.get("max_size", "")
            field["mime_types"] = task.get("mime_types", "")

        return {
            "success": True,
            "message": f"ACFフィールド '{field['label']}' を作成しました",
            "field": field,
            "php_code": self._generate_field_php_code(field),
        }

    async def import_field_group(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        ACFフィールドグループをインポート（JSONから）

        Args:
            task: タスクデータ

        Returns:
            実行結果
        """
        print("🎯 ACFフィールドグループをインポートします")

        json_data = task.get("json_data")
        if not json_data:
            return {"success": False, "error": "インポートするJSONデータが指定されていません"}

        try:
            if isinstance(json_data, str):
                field_group = json.loads(json_data)
            else:
                field_group = json_data

            php_code = self._generate_field_group_php_code(field_group)

            return {
                "success": True,
                "message": "ACFフィールドグループをJSONからインポートしました",
                "field_group": field_group,
                "php_code": php_code,
            }

        except Exception as e:
            return {"success": False, "error": f"JSONの解析に失敗しました: {str(e)}"}

    async def export_field_group(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        ACFフィールドグループをエクスポート（JSON形式で）

        Args:
            task: タスクデータ

        Returns:
            実行結果
        """
        print("🎯 ACFフィールドグループをエクスポートします")

        field_group = task.get("field_group")
        if not field_group:
            return {"success": False, "error": "エクスポートするフィールドグループが指定されていません"}

        json_export = self._generate_field_group_json(field_group)

        return {
            "success": True,
            "message": "ACFフィールドグループをJSON形式でエクスポートしました",
            "json_export": json_export,
        }

    def _generate_random_key(self) -> str:
        """
        ランダムなキーを生成

        Returns:
            ランダムキー
        """
        import random
        import string

        return "".join(random.choices(string.ascii_lowercase + string.digits, k=13))

    def _generate_field_group_php_code(self, field_group: Dict[str, Any]) -> str:
        """
        ACFフィールドグループのPHPコードを生成

        Args:
            field_group: フィールドグループデータ

        Returns:
            PHPコード
        """
        fields_php = ""
        for field in field_group.get("fields", []):
            fields_php += self._generate_field_php_code(field, indent=4)

        location_php = self._generate_location_php_code(field_group.get("location", []))

        php_code = f"""
// ACFフィールドグループ: {field_group['title']}
if( function_exists('acf_add_local_field_group') ):

    acf_add_local_field_group(array(
        'key' => '{field_group['key']}',
        'title' => '{field_group['title']}',
        'fields' => array({fields_php}
        ),
        'location' => array({location_php}
        ),
        'menu_order' => {field_group['menu_order']},
        'position' => '{field_group['position']}',
        'style' => '{field_group['style']}',
        'label_placement' => '{field_group['label_placement']}',
        'instruction_placement' => '{field_group['instruction_placement']}',
        'hide_on_screen' => {self._php_array(field_group.get('hide_on_screen', []))}
    ));

endif;
"""
        return php_code

    def _generate_field_php_code(self, field: Dict[str, Any], indent: int = 0) -> str:
        """
        ACFフィールドのPHPコードを生成

        Args:
            field: フィールドデータ
            indent: インデントレベル

        Returns:
            PHPコード
        """
        indent_str = " " * indent

        # 基本フィールド設定
        field_code = f"""
{indent_str}array(
{indent_str}    'key' => '{field['key']}',
{indent_str}    'label' => '{field['label']}',
{indent_str}    'name' => '{field['name']}',
{indent_str}    'type' => '{field['type']}',"""

        # オプションの設定を追加
        optional_fields = [
            ("instructions", field.get("instructions")),
            ("required", field.get("required", 0)),
            ("default_value", field.get("default_value")),
            ("placeholder", field.get("placeholder")),
        ]

        for key, value in optional_fields:
            if value not in [None, ""]:
                if isinstance(value, str):
                    field_code += f"\n{indent_str}    '{key}' => '{value}',"
                else:
                    field_code += f"\n{indent_str}    '{key}' => {value},"

        # ラッパー設定
        wrapper = field.get("wrapper", {})
        if any(wrapper.values()):
            field_code += f"\n{indent_str}    'wrapper' => array("
            for wrapper_key, wrapper_value in wrapper.items():
                if wrapper_value:
                    field_code += f"\n{indent_str}        '{wrapper_key}' => '{wrapper_value}',"
            field_code += f"\n{indent_str}    ),"

        field_code += f"\n{indent_str}),"

        return field_code

    def _generate_location_php_code(self, location: List) -> str:
        """
        ロケーションフィールドのPHPコードを生成

        Args:
            location: ロケーションデータ

        Returns:
            PHPコード
        """
        if not location:
            return ""

        location_php = ""
        for rule_group in location:
            location_php += "\n            array("
            for rule in rule_group:
                location_php += f"\n                array("
                location_php += f"\n                    'param' => '{rule.get('param', '')}',"
                location_php += f"\n                    'operator' => '{rule.get('operator', '==')}',"
                location_php += f"\n                    'value' => '{rule.get('value', '')}',"
                location_php += f"\n                ),"
            location_php += "\n            ),"

        return location_php

    def _generate_field_group_json(self, field_group: Dict[str, Any]) -> str:
        """
        ACFフィールドグループのJSONエクスポートを生成

        Args:
            field_group: フィールドグループデータ

        Returns:
            JSON文字列
        """
        return json.dumps(field_group, ensure_ascii=False, indent=2)

    def _php_array(self, data: Any) -> str:
        """
        PHPの配列表現を生成

        Args:
            data: 変換するデータ

        Returns:
            PHP配列表現
        """
        if isinstance(data, list):
            items = ", ".join([self._php_array(item) for item in data])
            return f"array({items})"
        elif isinstance(data, dict):
            items = []
            for key, value in data.items():
                items.append(f"'{key}' => {self._php_array(value)}")
            return f"array({', '.join(items)})"
        elif isinstance(data, str):
            return f"'{data}'"
        elif isinstance(data, bool):
            return "1" if data else "0"
        elif data is None:
            return "''"
        else:
            return str(data)


# テスト用の簡単な実行コード
if __name__ == "__main__":

    async def test():
        """テスト実行"""
        agent = WordPressACFAgent()

        # フィールドグループ作成テスト
        task = {
            "type": "create_field_group",
            "title": "テストフィールドグループ",
            "key": "group_test_123",
            "fields": [{"key": "field_test_1", "label": "テストフィールド", "name": "test_field", "type": "text"}],
        }

        result = await agent.execute(task)
        print(f"ACFフィールドグループテスト結果: {result['success']}")

        if result["success"]:
            print("✅ PHPコード生成成功")
            print(result["php_code"][:200] + "..." if len(result["php_code"]) > 200 else result["php_code"])

    asyncio.run(test())
