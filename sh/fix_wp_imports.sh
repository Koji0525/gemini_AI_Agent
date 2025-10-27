#!/bin/bash

echo "=========================================="
echo "🔧 WordPressエージェントのインポート修正"
echo "=========================================="

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. wp_taxonomy_agentの存在確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "wordpress/wp_dev/wp_taxonomy_agent.py" ]; then
    echo "✅ wp_taxonomy_agent.py 存在"
else
    echo "❌ wp_taxonomy_agent.py が見つかりません"
    echo "   wp_cpt_agent.py と wp_acf_agent.py がこれをインポートしています"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. wp_cpt_agent.py のインポート部分"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

grep "from.*taxonomy\|import.*taxonomy" wordpress/wp_dev/wp_cpt_agent.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. wp_acf_agent.py のインポート部分"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

grep "from.*taxonomy\|import.*taxonomy" wordpress/wp_dev/wp_acf_agent.py

echo ""
echo "=========================================="

