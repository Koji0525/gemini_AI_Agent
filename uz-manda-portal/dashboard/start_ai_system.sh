#!/bin/bash

# 24時間AI開発システム起動スクリプト

echo "🚀 24時間AI開発システムを起動します..."
echo "開始時刻: $(date)"

# 環境変数を設定
export WP_URL="https://uzbek-ma.com"
export WP_USERNAME="uzbek"
export WP_PASSWORD="RkLU07FkrNpeiENdFx3swseJ"
export AUTO_DEVELOP="true"
export SELF_HEALING="true"
export CONTINUOUS_IMPROVEMENT="true"

# ダッシュボードを起動
echo "🌐 ダッシュボードを起動..."
cd /workspaces/gemini_AI_Agent/uz-manda-portal/dashboard
cp app_enhanced.py app.py
nohup uvicorn app:app --host 0.0.0.0 --port 8000 > ../logs/dashboard.log 2>&1 &

# AI開発システムを起動
echo "�� AI開発システムを起動..."
cd /workspaces/gemini_AI_Agent/uz-manda-portal
nohup python3 scripts/ai_development_system.py > logs/ai_system.log 2>&1 &

echo "✅ システムが起動しました"
echo "📊 ダッシュボード: http://localhost:8000"
echo "📋 AIシステムログ: tail -f logs/ai_system.log"
echo "📋 ダッシュボードログ: tail -f logs/dashboard.log"

# プロセスIDを表示
echo "🔄 実行中のプロセス:"
ps aux | grep -E "uvicorn|ai_development" | grep -v grep
