#!/bin/bash
# M&Aポータル完全自動構築スクリプト

echo "🚀 M&Aポータル完全自動構築"
echo "============================================================"

# Task 1: 既に完了（functions.phpコード生成済み）
echo "✅ Task 1: カスタム投稿タイプコード生成完了"

# Task 2: ACF設定手順表示
echo ""
echo "⏳ Task 2: ACFフィールド設定"
python3 tools/acf_auto_setup.py wordpress_projects/ma_portal/acf_fields.json

# Task 3: デモデータ投入
echo ""
echo "⏳ Task 3: デモデータ投入"
echo "デモデータを投入しますか？ (y/n)"
read -r response

if [ "$response" = "y" ]; then
    python3 tools/demo_data_importer.py scripts/ma_demo_data.json
    python3 scripts/update_task_status.py MA_PORTAL_3 completed
else
    echo "スキップしました"
fi

# 進捗確認
echo ""
python3 scripts/check_ma_portal_progress.py

echo ""
echo "============================================================"
echo "🎉 自動化可能な部分は完了しました"
echo "============================================================"
echo ""
echo "📋 次のアクション:"
echo "   1. WordPress管理画面でACFフィールドを設定"
echo "   2. 必要に応じてデモデータを確認・調整"
echo "   3. Task 4: 検索ページ作成"
