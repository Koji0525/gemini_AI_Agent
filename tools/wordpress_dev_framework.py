#!/usr/bin/env python3
"""
WordPress開発自動化フレームワーク
変更理由: 手動作業を自動化、汎用性・拡張性・再利用性を確保
"""

import sys
import json
from pathlib import Path
from typing import Dict, List

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from wordpress.wp_dev.wp_rest_client import WordPressRESTClient
from configuration.wp_config_loader import WordPressConfigLoader


class WordPressProjectBuilder:
    """WordPress プロジェクト自動構築フレームワーク"""

    def __init__(self):
        config_loader = WordPressConfigLoader()
        self.config = config_loader.load_config()
        self.client = WordPressRESTClient(self.config["wp_url"], self.config["wp_user"], self.config["wp_pass"])

    def build_from_template(self, template_path: str):
        """テンプレートJSONからプロジェクトを自動構築"""
        print("🚀 WordPress プロジェクト自動構築")
        print("=" * 70)

        # テンプレート読み込み
        template = self._load_template(template_path)

        if not template:
            return False

        # 実行計画表示
        self._show_build_plan(template)

        # 確認
        response = input("\n実行しますか？ (y/n): ")
        if response.lower() != "y":
            print("キャンセルしました")
            return False

        # 順次実行
        results = {
            "post_types": [],
            "taxonomies": [],
            "acf_fields": [],
            "demo_data": [],
        }

        # 1. カスタム投稿タイプ作成（functions.phpコード生成）
        if "post_types" in template:
            print("\n📄 カスタム投稿タイプコード生成...")
            for cpt in template["post_types"]:
                code = self._generate_cpt_code(cpt)
                results["post_types"].append(code)
                print(f"   ✅ {cpt['slug']}")

        # 2. タクソノミー作成（functions.phpコード生成）
        if "taxonomies" in template:
            print("\n🏷️ タクソノミーコード生成...")
            for tax in template["taxonomies"]:
                code = self._generate_taxonomy_code(tax)
                results["taxonomies"].append(code)
                print(f"   ✅ {tax['slug']}")

        # 3. ACFフィールド設定（JSON生成）
        if "acf_fields" in template:
            print("\n📝 ACFフィールド設定生成...")
            acf_json = self._generate_acf_json(template["acf_fields"])
            results["acf_fields"] = acf_json
            print(f"   ✅ {len(template['acf_fields']['fields'])}個のフィールド")

        # 4. デモデータ投入（REST API経由）
        if "demo_data" in template:
            print("\n📊 デモデータ投入...")
            for data in template["demo_data"]:
                result = self._create_demo_post(data)
                results["demo_data"].append(result)
                if result.get("success"):
                    print(f"   ✅ {data['title']}")
                else:
                    print(f"   ❌ {data['title']}: {result.get('error')}")

        # 結果保存
        self._save_results(template, results)

        print("\n" + "=" * 70)
        print("✅ プロジェクト構築完了")
        print("=" * 70)

        return True

    def _load_template(self, template_path: str) -> Dict:
        """テンプレートファイル読み込み"""
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ テンプレート読み込みエラー: {e}")
            return None

    def _show_build_plan(self, template: Dict):
        """実行計画表示"""
        print("\n📋 実行計画:")

        if "post_types" in template:
            print(f"   • カスタム投稿タイプ: {len(template['post_types'])}個")

        if "taxonomies" in template:
            print(f"   • タクソノミー: {len(template['taxonomies'])}個")

        if "acf_fields" in template:
            print(f"   • ACFフィールド: {len(template['acf_fields']['fields'])}個")

        if "demo_data" in template:
            print(f"   • デモデータ: {len(template['demo_data'])}件")

    def _generate_cpt_code(self, cpt: Dict) -> str:
        """カスタム投稿タイプのPHPコード生成"""
        slug = cpt["slug"]
        labels = cpt.get("labels", {})

        code = f"""
// カスタム投稿タイプ: {slug}
function {slug}_register_post_type() {{
    register_post_type('{slug}', array(
        'labels' => array(
            'name' => '{labels.get("name", slug)}',
            'singular_name' => '{labels.get("singular_name", slug)}',
        ),
        'public' => true,
        'has_archive' => true,
        'menu_icon' => '{cpt.get("menu_icon", "dashicons-admin-post")}',
        'supports' => array('title', 'editor', 'thumbnail', 'excerpt'),
        'show_in_rest' => true,
    ));
}}
add_action('init', '{slug}_register_post_type');
"""
        return code

    def _generate_taxonomy_code(self, tax: Dict) -> str:
        """タクソノミーのPHPコード生成"""
        slug = tax["slug"]
        post_type = tax.get("post_type", "post")
        labels = tax.get("labels", {})

        code = f"""
// タクソノミー: {slug}
function {slug}_register_taxonomy() {{
    register_taxonomy('{slug}', '{post_type}', array(
        'labels' => array(
            'name' => '{labels.get("name", slug)}',
        ),
        'hierarchical' => {str(tax.get('hierarchical', True)).lower()},
        'show_in_rest' => true,
        'show_admin_column' => true,
    ));
}}
add_action('init', '{slug}_register_taxonomy');
"""
        return code

    def _generate_acf_json(self, acf_config: Dict) -> Dict:
        """ACFフィールドJSON生成"""
        return {
            "key": acf_config.get("key", "group_auto"),
            "title": acf_config.get("title", "Custom Fields"),
            "fields": acf_config.get("fields", []),
            "location": acf_config.get("location", []),
        }

    def _create_demo_post(self, data: Dict) -> Dict:
        """デモデータ投入"""
        try:
            post_data = {
                "title": data["title"],
                "content": data.get("content", ""),
                "status": "publish",
            }

            result = self.client.create_post(post_data)
            return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _save_results(self, template: Dict, results: Dict):
        """結果をファイルに保存"""
        output_dir = Path("wordpress_projects") / template.get("project_name", "project")
        output_dir.mkdir(parents=True, exist_ok=True)

        # functions.php コード
        functions_code = "<?php\n"
        functions_code += "// Auto-generated by WordPress Dev Framework\n\n"

        for code in results["post_types"]:
            functions_code += code + "\n"

        for code in results["taxonomies"]:
            functions_code += code + "\n"

        (output_dir / "functions_additions.php").write_text(functions_code, encoding="utf-8")

        # ACF JSON
        if results["acf_fields"]:
            acf_file = output_dir / "acf_fields.json"
            acf_file.write_text(json.dumps(results["acf_fields"], indent=2, ensure_ascii=False), encoding="utf-8")

        # レポート
        report = {
            "project": template.get("project_name"),
            "created_at": str(Path.cwd()),
            "results": {
                "post_types": len(results["post_types"]),
                "taxonomies": len(results["taxonomies"]),
                "acf_fields": bool(results["acf_fields"]),
                "demo_data": len([d for d in results["demo_data"] if d.get("success")]),
            },
        }

        (output_dir / "build_report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        print(f"\n📁 出力先: {output_dir}")


def main():
    import sys

    if len(sys.argv) < 2:
        print("使い方: python3 wordpress_dev_framework.py <template.json>")
        sys.exit(1)

    template_path = sys.argv[1]

    builder = WordPressProjectBuilder()
    builder.build_from_template(template_path)


if __name__ == "__main__":
    main()
