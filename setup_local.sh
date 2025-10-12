#!/bin/bash
# ローカル環境セットアップ

echo "🔧 ローカル環境セットアップ"

# 1. 依存パッケージインストール
pip install -r requirements.txt

# 2. Playwright ブラウザインストール
playwright install chromium

# 3. 環境変数設定
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/service_account.json"

# 4. 設定ファイルコピー
cp .env.example .env

# 5. テスト実行
python test_tasks.py

echo "✅ セットアップ完了"
