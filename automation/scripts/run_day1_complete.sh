#!/bin/bash

echo "============================================================"
echo "�� Day 1 完全実行フロー"
echo "============================================================"
echo ""

# STEP 1: .env設定
echo "【STEP 1】.env設定"
echo "----------------------------"
bash automation/scripts/setup_env.sh

echo ""
echo ""

# STEP 2: 設定確認
echo "【STEP 2】設定確認"
echo "----------------------------"
python3 automation/scripts/verify_env.py

echo ""
echo ""

# STEP 3: WP自動ログインテスト
echo "【STEP 3】WP自動ログインテスト"
echo "----------------------------"
python3 automation/modules/wp_login_v2.py

echo ""
echo ""

# STEP 4: Day 1統合テスト
echo "【STEP 4】Day 1統合テスト"
echo "----------------------------"
python3 automation/tests/test_day1_v2.py

echo ""
echo "============================================================"
echo "✅ Day 1 完全実行フロー完了"
echo "============================================================"

