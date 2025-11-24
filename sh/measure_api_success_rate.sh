#!/bin/bash
# Phase 0 診断: API成功率の測定

echo "=================================================="
echo "Phase 0 診断: API成功率の測定"
echo "=================================================="
echo ""
echo "【目的】Google Sheets API / Gemini APIの健全性確認"
echo "【基準値】API成功率 95.9%以上"
echo ""

cd /workspaces/gemini_AI_Agent

# Google Sheets APIテスト
echo "📡 Google Sheets API テスト中..."

python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

success_count = 0
total_count = 0

# Google Sheets API テスト
try:
    from tools.sheets_manager import GoogleSheetsManager
    sheets = GoogleSheetsManager()
    
    # テスト1: project_goal読み込み
    total_count += 1
    try:
        data = sheets.read_range('project_goal!A1:D10')
        if data:
            print("✅ project_goal読み込み成功")
            success_count += 1
        else:
            print("⚠️ project_goal読み込み: データなし")
    except Exception as e:
        print(f"❌ project_goal読み込み失敗: {e}")
    
    # テスト2: pm_tasks読み込み
    total_count += 1
    try:
        data = sheets.read_range('pm_tasks!A1:M10')
        if data:
            print("✅ pm_tasks読み込み成功")
            success_count += 1
        else:
            print("⚠️ pm_tasks読み込み: データなし")
    except Exception as e:
        print(f"❌ pm_tasks読み込み失敗: {e}")
    
except Exception as e:
    print(f"❌ GoogleSheetsManager初期化失敗: {e}")
    total_count += 2

# Gemini API テスト
try:
    import google.generativeai as genai
    import os
    
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        total_count += 1
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content("Hello")
            print("✅ Gemini API接続成功")
            success_count += 1
        except Exception as e:
            print(f"❌ Gemini API接続失敗: {e}")
    else:
        print("⚠️ GEMINI_API_KEY未設定")
        total_count += 1
except Exception as e:
    print(f"❌ Gemini APIテスト失敗: {e}")
    total_count += 1

# 結果計算
if total_count > 0:
    success_rate = (success_count / total_count) * 100
    print(f"\n📊 API成功率: {success_rate:.1f}% ({success_count}/{total_count})")
    
    # 結果保存
    with open('/tmp/api_success_rate.txt', 'w') as f:
        f.write(f"{success_rate:.1f}")
else:
    print("\n❌ テストが実行されませんでした")
    with open('/tmp/api_success_rate.txt', 'w') as f:
        f.write("0.0")
PYEOF

API_SUCCESS_RATE=$(cat /tmp/api_success_rate.txt)

echo ""
echo "【基準値判定】"
if (( $(echo "$API_SUCCESS_RATE >= 95.9" | bc -l) )); then
    echo "✅ 基準値クリア: ${API_SUCCESS_RATE}% >= 95.9%"
    STATUS="SUCCESS"
else
    echo "⚠️ 基準値未達: ${API_SUCCESS_RATE}% < 95.9%"
    STATUS="WARNING"
fi

echo ""
echo "【実測値】${API_SUCCESS_RATE}%"
