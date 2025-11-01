#!/usr/bin/env python3
"""
test_wordpress_agents_v01-fixed.py の修正スクリプト
"""
import re

with open("test_wordpress_agents_v01-fixed.py", "r", encoding="utf-8") as f:
    content = f.read()

# BrowserControllerの正しい初期化に修正
content = re.sub(
    r"browser = BrowserController\(\)\s*\n\s*await browser\.initialize\(\)",
    "browser = BrowserController()\n        await browser.setup_browser()\n        await browser.navigate_to_gemini()",
    content,
)

# タクソノミーエージェントのインポートを新しいバージョンに変更
content = content.replace(
    "from wordpress.wp_dev.wp_taxonomy_agent import WordPressTaxonomyAgent",
    "from wordpress.wp_dev.wp_taxonomy_agent_v01_basic import WordPressTaxonomyAgent",
)

# プラグインマネージャーのインポートを新しいバージョンに変更
content = content.replace(
    "from wordpress.wp_plugin_manager import WordPressPluginManager",
    "from wordpress.wp_plugin_manager_v01_add_execute import WordPressPluginManager",
)

with open("test_wordpress_agents_v01-fixed.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ test_wordpress_agents_v01-fixed.py を修正しました")
