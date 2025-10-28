#!/usr/bin/env python3
"""
インポート文の修正スクリプト v01
"""
import re


def fix_imports(file_path, old_import, new_import):
    """ファイルのインポート文を修正"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    old_content = content
    content = content.replace(old_import, new_import)

    if old_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ 修正: {file_path}")
        return True
    else:
        print(f"✅ 修正不要: {file_path}")
        return False


# 修正リスト
fixes = [
    # ファイルパス, 古いインポート, 新しいインポート
    (
        "test_wordpress_agents_v01_fixed.py",
        "from wordpress.wp_dev.wp_taxonomy_agent_v01_basic import WordPressTaxonomyAgent",
        "from wordpress.wp_dev.wp_taxonomy_agent_v01_basic import WordPressTaxonomyAgent",
    ),
    (
        "test_wordpress_agents_v01_fixed.py",
        "from wordpress.wp_plugin_manager_v01_add_execute import WordPressPluginManager",
        "from wordpress.wp_plugin_manager_v01_add_execute import WordPressPluginManager",
    ),
    (
        "test_integrated_system_v01_fixed.py",
        "from agents.wordpress.wp_design_generator_v01_fix_browser import WPDesignGenerator",
        "from agents.wordpress.wp_design_generator_v01_fix_browser import WPDesignGenerator",
    ),
    (
        "test_integrated_system_v01_fixed.py",
        "from wordpress.wp_dev.wp_taxonomy_agent_v01_basic import WordPressTaxonomyAgent",
        "from wordpress.wp_dev.wp_taxonomy_agent_v01_basic import WordPressTaxonomyAgent",
    ),
    (
        "test_integrated_system_v01_fixed.py",
        "from wordpress.wp_plugin_manager_v01_add_execute import WordPressPluginManager",
        "from wordpress.wp_plugin_manager_v01_add_execute import WordPressPluginManager",
    ),
]

for file_path, old_import, new_import in fixes:
    if not fix_imports(file_path, old_import, new_import):
        # インポートが見つからない場合は別のパターンを試す
        old_pattern = old_import.replace("_v01_", "-v01-")
        if old_pattern != old_import:
            fix_imports(file_path, old_pattern, new_import)

print("🎉 インポート修正完了")
