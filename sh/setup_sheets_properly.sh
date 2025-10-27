#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "📊 Google Sheets 設定（修正版）"
echo "=========================================="

# ====================================================================
# STEP 1: sheets_manager.pyの確認
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 1/4] sheets_manager.pyの確認${NC}"
echo "=========================================="

if [ -f "tools/sheets_manager.py" ]; then
    echo "✅ sheets_manager.py 確認"
    
    # 初期化方法を確認
    echo ""
    echo "初期化シグネチャ:"
    grep -A 5 "def __init__" tools/sheets_manager.py | head -10
else
    echo "❌ sheets_manager.py が見つかりません"
    exit 1
fi

# ====================================================================
# STEP 2: 設定ディレクトリ作成
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 2/4] 設定ディレクトリ作成${NC}"
echo "=========================================="

mkdir -p configuration

if [ ! -f "configuration/service_account.json" ]; then
    echo "⚠️  service_account.json が見つかりません"
    echo ""
    echo "Google Cloud Console から取得が必要です："
    echo "1. https://console.cloud.google.com/"
    echo "2. プロジェクト選択"
    echo "3. IAM と管理 → サービスアカウント"
    echo "4. キーを作成（JSON形式）"
    echo "5. configuration/service_account.json として保存"
    echo ""
    read -p "service_account.json を配置しましたか？ (y/n): " has_sa
    
    if [ "$has_sa" != "y" ]; then
        echo "❌ service_account.json が必要です"
        exit 1
    fi
fi

echo "✅ service_account.json 確認完了"

# ====================================================================
# STEP 3: スプレッドシートID入力
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 3/4] スプレッドシートID設定${NC}"
echo "=========================================="

echo ""
echo "📋 Google Sheets URL例:"
echo "   https://docs.google.com/spreadsheets/d/【このID部分】/edit"
echo ""

# デフォルト値を表示
DEFAULT_ID="1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s"
echo "デフォルトID: $DEFAULT_ID"
echo ""

read -p "スプレッドシートID (Enter=デフォルト使用): " INPUT_ID

if [ -z "$INPUT_ID" ]; then
    SHEET_ID="$DEFAULT_ID"
    echo "✅ デフォルトIDを使用"
else
    SHEET_ID="$INPUT_ID"
fi

echo ""
echo "設定されたID: $SHEET_ID"

# ====================================================================
# STEP 4: 環境変数ファイル作成
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 4/4] 環境変数ファイル作成${NC}"
echo "=========================================="

# .env ファイルに保存
cat > .env << ENV_FILE
# Google Sheets 設定
SPREADSHEET_ID=$SHEET_ID
SERVICE_ACCOUNT_FILE=configuration/service_account.json
ENV_FILE

echo "✅ .env ファイル作成完了"

# Pythonで読み込むヘルパーも作成
cat > configuration/config_loader.py << 'CONFIG_LOADER'
"""
設定ファイル読み込みヘルパー
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

def get_spreadsheet_id() -> str:
    """スプレッドシートIDを取得"""
    return os.getenv("SPREADSHEET_ID", "")

def get_service_account_file() -> str:
    """サービスアカウントファイルパスを取得"""
    return os.getenv("SERVICE_ACCOUNT_FILE", "configuration/service_account.json")

CONFIG_LOADER

echo "✅ config_loader.py 作成完了"

# python-dotenv インストール確認
if ! python3 -c "import dotenv" 2>/dev/null; then
    echo ""
    echo "⚠️  python-dotenv がインストールされていません"
    echo "   インストール中..."
    pip install python-dotenv -q
    echo "✅ インストール完了"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ 設定完了${NC}"
echo "=========================================="
echo ""
echo "📁 作成されたファイル:"
echo "   - .env"
echo "   - configuration/config_loader.py"
echo ""
echo "設定内容:"
echo "   スプレッドシートID: $SHEET_ID"
echo "   サービスアカウント: configuration/service_account.json"
echo ""
echo "次のステップ:"
echo "   ./test_sheets_integration_fixed.sh"
echo ""

