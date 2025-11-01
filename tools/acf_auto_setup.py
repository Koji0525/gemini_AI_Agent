#!/usr/bin/env python3
"""
ACFフィールド自動設定ツール（型安全版）
変更理由: 型ヒントエラー修正、Python 3.8+互換性確保
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any  # 型ヒント追加

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from wordpress.wp_dev.wp_rest_client import WordPressRESTClient
from configuration.wp_config_loader import WordPressConfigLoader


class ACFAutoSetup:
    """ACFフィールド自動設定"""

    def __init__(self):
        config_loader = WordPressConfigLoader()
        self.config = config_loader.load_config()
        self.client = WordPressRESTClient(self.config["wp_url"], self.config["wp_user"], self.config["wp_pass"])

    def setup_from_json(self, acf_json_path: str) -> bool:
        """ACF JSONからフィールドグループを作成"""
        print("🔧 ACFフィールド自動設定")
        print("=" * 70)

        # JSON読み込み
        with open(acf_json_path, "r", encoding="utf-8") as f:
            acf_config = json.load(f)

        print(f"\n📋 設定内容:")
        print(f"   タイトル: {acf_config.get('title', 'N/A')}")
        print(f"   フィールド数: {len(acf_config.get('fields', []))}")

        # WordPress管理画面での手動設定手順を出力
        print("\n" + "=" * 70)
        print("📝 ACFフィールド設定手順（コピペ推奨）")
        print("=" * 70)

        print("\n【Step 1】ACF フィールドグループ作成")
        print("   WordPress管理画面 → ACF → フィールドグループ → 新規追加")
        print(f"\n【Step 2】フィールドグループ名を入力")
        print(f"   → {acf_config.get('title')}")

        print("\n【Step 3】以下のフィールドを順番に追加:\n")

        for i, field in enumerate(acf_config.get("fields", []), 1):
            print(f"━━━ フィールド {i} ━━━")
            print(f"フィールドラベル: {field.get('label')}")
            print(f"フィールド名: {field.get('name')}")
            print(f"フィールドタイプ: {field.get('type')}")
            print(f"必須?: {'はい' if field.get('required') else 'いいえ'}")

            if field.get("type") == "select" and "choices" in field:
                print(f"選択肢:")
                for choice_key, choice_value in field["choices"].items():
                    print(f"  {choice_key} : {choice_value}")

            if "placeholder" in field:
                print(f"プレースホルダー: {field['placeholder']}")

            if field.get("type") == "number":
                if "min" in field:
                    print(f"最小値: {field['min']}")

            print()

        print("【Step 4】表示ルール設定")
        print("   ルール → 「投稿タイプ」「が次と等しい」「ma_company」")

        print("\n【Step 5】公開")
        print("   右上の「公開」ボタンをクリック")

        # PHP登録コード生成（オプション）
        self._generate_acf_php_code(acf_config)

        print("\n" + "=" * 70)
        print("✅ ACF設定手順の表示完了")
        print("=" * 70)

        return True

    def _generate_acf_php_code(self, acf_config: Dict[str, Any]) -> None:
        """ACF設定用PHPコード生成（オプション）"""
        output_file = Path("wordpress_projects/ma_portal/acf_register_code.php")

        code = (
            """<?php
/**
 * ACFフィールドグループ登録コード
 * このコードをfunctions.phpに追加すると、ACF GUIなしでフィールドを登録できます
 */

if( function_exists('acf_add_local_field_group') ):

acf_add_local_field_group(array(
    'key' => '"""
            + acf_config.get("key", "group_auto")
            + """',
    'title' => '"""
            + acf_config.get("title", "Custom Fields")
            + """',
    'fields' => array(
"""
        )

        for field in acf_config.get("fields", []):
            code += f"""        array(
            'key' => '{field.get('key', '')}',
            'label' => '{field.get('label', '')}',
            'name' => '{field.get('name', '')}',
            'type' => '{field.get('type', 'text')}',
            'required' => {1 if field.get('required') else 0},
"""

            if field.get("type") == "select" and "choices" in field:
                choices_str = ", ".join([f"'{k}' => '{v}'" for k, v in field["choices"].items()])
                code += f"            'choices' => array({choices_str}),\n"

            if "placeholder" in field:
                code += f"            'placeholder' => '{field['placeholder']}',\n"

            if field.get("type") == "number" and "min" in field:
                code += f"            'min' => {field['min']},\n"

            code += "        ),\n"

        code += """    ),
    'location' => array(
        array(
            array(
                'param' => 'post_type',
                'operator' => '==',
                'value' => 'ma_company',
            ),
        ),
    ),
    'position' => 'normal',
    'style' => 'default',
));

endif;
"""

        output_file.write_text(code, encoding="utf-8")
        print(f"\n💡 【オプション】ACF登録用PHPコードを生成しました")
        print(f"   ファイル: {output_file}")
        print(f"   用途: functions.phpに追加でGUI設定不要に")


def main():
    import sys

    if len(sys.argv) < 2:
        print("使い方: python3 acf_auto_setup.py <acf_fields.json>")
        sys.exit(1)

    acf_json = sys.argv[1]

    if not Path(acf_json).exists():
        print(f"❌ エラー: ファイルが見つかりません: {acf_json}")
        sys.exit(1)

    setup = ACFAutoSetup()
    setup.setup_from_json(acf_json)


if __name__ == "__main__":
    main()
