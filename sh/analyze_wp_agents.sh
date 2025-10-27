#!/bin/bash

echo "=========================================="
echo "🔍 WordPressエージェント構造分析"
echo "=========================================="

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. wp_agent.py のクラス定義"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "クラス名:"
grep "^class " wordpress/wp_agent.py

echo ""
echo "__init__ メソッド:"
grep -A 10 "def __init__" wordpress/wp_agent.py | head -15

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. wp_cpt_agent.py のクラス定義"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "クラス名:"
grep "^class " wordpress/wp_dev/wp_cpt_agent.py

echo ""
echo "インポート部分:"
grep "^import\|^from" wordpress/wp_dev/wp_cpt_agent.py | head -10

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. wp_requirements_agent.py のクラス定義"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "クラス名:"
grep "^class " wordpress/wp_dev/wp_requirements_agent.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. wp_acf_agent.py のクラス定義"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "クラス名:"
grep "^class " wordpress/wp_dev/wp_acf_agent.py

echo ""
echo "インポート部分:"
grep "^import\|^from" wordpress/wp_dev/wp_acf_agent.py | head -10

echo ""
echo "=========================================="

