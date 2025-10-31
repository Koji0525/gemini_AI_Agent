#!/bin/bash
# M&Aポータル完全自動構築スクリプト v2.0（堅牢版）

echo "🚀 M&Aポータル完全自動構築 v2.0"
echo "============================================================"
echo ""

# Step 0: 環境チェック
echo "📋 Step 0: WordPress環境チェック"
echo "============================================================"

python3 tools/wordpress_readiness_checker.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 環境チェック失敗"
    echo ""
    echo "💡 まず以下を実行してください:"
    echo "   1. functions.phpにコードを追加"
    echo "      cat wordpress_projects/ma_portal/PASTE_TO_WORDPRESS.txt"
    echo "   2. https://uzbek-ma.com/wp-admin/theme-editor.php"
    echo "   3. コードを貼り付けて保存"
    echo "   4. このスクリプトを再実行"
    echo ""
    exit 1
fi

echo ""
echo "✅ 環境チェック完了 - 自動化を開始します"
echo ""

# Task 2: ACF設定手順表示
echo "============================================================"
echo "📋 Task 2: ACFフィールド設定"
echo "============================================================"
echo ""

python3 tools/acf_auto_setup.py wordpress_projects/ma_portal/acf_fields.json

echo ""
echo "⏸️  ACF設定を完了してから続行してください"
echo ""
echo "ACF設定は完了しましたか？ (y/n)"
read -r acf_response

if [ "$acf_response" != "y" ]; then
    echo "スキップしました - 後でACF設定を完了してください"
    exit 0
fi

# Task 3: デモデータ投入
echo ""
echo "============================================================"
echo "📊 Task 3: デモデータ投入"
echo "============================================================"
echo ""
echo "デモデータを投入しますか？ (y/n)"
read -r data_response

if [ "$data_response" = "y" ]; then
    python3 tools/demo_data_importer.py scripts/ma_demo_data.json
    
    if [ $? -eq 0 ]; then
        python3 scripts/update_task_status.py MA_PORTAL_3 completed
    fi
else
    echo "スキップしました"
fi

# 進捗確認
echo ""
python3 scripts/check_ma_portal_progress.py

echo ""
echo "============================================================"
echo "🎉 自動化完了"
echo "============================================================"
echo ""
echo "📋 次のステップ:"
echo "   • WordPress管理画面でデータを確認"
echo "   • Task 4: 検索ページ作成"
echo "   • Task 5: 動作確認"
