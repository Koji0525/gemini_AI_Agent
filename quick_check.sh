#!/bin/bash
echo "🔍 簡易チェック"
echo "="

echo "1️⃣ 必須ファイル確認:"
for file in claude_unified_agent.py web_dashboard_v2.py .env; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (不足)"
    fi
done

echo ""
echo "2️⃣ 環境変数確認:"
if [ -f .env ]; then
    if grep -q "ANTHROPIC_API_KEY" .env; then
        echo "  ✅ ANTHROPIC_API_KEY 設定済み"
    else
        echo "  ❌ ANTHROPIC_API_KEY 未設定"
    fi
else
    echo "  ❌ .env ファイルなし"
fi

echo ""
echo "3️⃣ Pythonパッケージ確認:"
python -c "import anthropic; print('  ✅ anthropic')" 2>/dev/null || echo "  ❌ anthropic"
python -c "import flask; print('  ✅ flask')" 2>/dev/null || echo "  ❌ flask"
python -c "from dotenv import load_dotenv; print('  ✅ python-dotenv')" 2>/dev/null || echo "  ❌ python-dotenv"

echo ""
echo "4️⃣ ログディレクトリ確認:"
if [ -d "logs" ]; then
    echo "  ✅ logs/ 存在"
    echo "  📁 ファイル数: $(ls -1 logs/*.log 2>/dev/null | wc -l)"
else
    echo "  ⚠️ logs/ なし（自動作成されます）"
fi

echo ""
echo "=" 
