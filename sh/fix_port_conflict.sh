#!/bin/bash
# ポート競合の解決とダッシュボード再起動

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 ポート競合の解決"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: ポート8000を使用しているプロセスを確認
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "【STEP 1】ポート8000を使用しているプロセスを確認"
echo ""

PORT_IN_USE=$(lsof -ti:8000 2>/dev/null)

if [ -n "$PORT_IN_USE" ]; then
    echo "⚠️  ポート8000は既に使用されています"
    echo ""
    echo "【使用中のプロセス】"
    lsof -i:8000 2>/dev/null || ps aux | grep "$PORT_IN_USE"
    echo ""
    
    read -p "このプロセスを停止しますか？ [y/N] " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 プロセスを停止中..."
        kill -9 $PORT_IN_USE 2>/dev/null
        sleep 2
        
        # 確認
        if lsof -ti:8000 >/dev/null 2>&1; then
            echo "❌ プロセスの停止に失敗しました"
            echo "   手動で停止してください: kill -9 $PORT_IN_USE"
            exit 1
        else
            echo "✅ プロセスを停止しました"
        fi
    else
        echo "❌ キャンセルしました"
        echo ""
        echo "【代替案】別のポートを使用"
        echo "  bash start_dashboard.sh --port 8080"
        exit 0
    fi
else
    echo "✅ ポート8000は使用可能です"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: 改良版起動スクリプトの作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "【STEP 2】改良版起動スクリプトの作成"
echo ""

cat > start_dashboard_v2.sh << 'START'
#!/bin/bash
# Webダッシュボード起動スクリプト v2（ポート競合対応）

cd /workspaces/gemini_AI_Agent

# デフォルトポート
PORT=8000

# ポート指定オプション
while [[ $# -gt 0 ]]; do
    case $1 in
        --port|-p)
            PORT="$2"
            shift 2
            ;;
        *)
            echo "不明なオプション: $1"
            exit 1
            ;;
    esac
done

echo "🌐 Webダッシュボードを起動します..."
echo "   ポート: $PORT"
echo ""

# ポートが使用中かチェック
if lsof -ti:$PORT >/dev/null 2>&1; then
    echo "⚠️  ポート $PORT は既に使用されています"
    echo ""
    
    # 使用中のプロセスを表示
    echo "【使用中のプロセス】"
    lsof -i:$PORT 2>/dev/null
    echo ""
    
    read -p "このプロセスを停止して再起動しますか？ [y/N] " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        PID=$(lsof -ti:$PORT)
        echo "🔄 プロセス($PID)を停止中..."
        kill -9 $PID 2>/dev/null
        sleep 2
    else
        echo "❌ キャンセルしました"
        echo "   別のポートで起動: bash start_dashboard_v2.sh --port 8080"
        exit 0
    fi
fi

# FastAPIとuvicornのチェック
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  FastAPIがインストールされていません"
    echo "📦 インストール中..."
    pip install fastapi uvicorn --break-system-packages
fi

# サーバー起動
echo ""
echo "🚀 サーバーを起動中..."
python3 -c "
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')
from agents.web_dashboard.dashboard_server import start_server
start_server(port=$PORT)
"

START

chmod +x start_dashboard_v2.sh
echo "✅ 改良版起動スクリプト作成: start_dashboard_v2.sh"

# バックグラウンド起動スクリプトも更新
cat > start_dashboard_background_v2.sh << 'BG'
#!/bin/bash
# Webダッシュボードをバックグラウンドで起動 v2

cd /workspaces/gemini_AI_Agent

# デフォルトポート
PORT=8000

# ポート指定オプション
while [[ $# -gt 0 ]]; do
    case $1 in
        --port|-p)
            PORT="$2"
            shift 2
            ;;
        *)
            echo "不明なオプション: $1"
            exit 1
            ;;
    esac
done

echo "🌐 Webダッシュボードをバックグラウンドで起動..."
echo "   ポート: $PORT"
echo ""

# 既存のプロセスを停止
echo "🔄 既存のダッシュボードプロセスを停止中..."
pkill -f "dashboard_server.py" 2>/dev/null
sleep 2

# ポートが使用中かチェック
if lsof -ti:$PORT >/dev/null 2>&1; then
    echo "⚠️  ポート $PORT は依然として使用されています"
    PID=$(lsof -ti:$PORT)
    echo "   PID: $PID を強制停止中..."
    kill -9 $PID 2>/dev/null
    sleep 2
fi

# FastAPIとuvicornのチェック
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 FastAPIをインストール中..."
    pip install fastapi uvicorn --break-system-packages
fi

# バックグラウンドで起動
mkdir -p logs

nohup python3 -c "
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')
from agents.web_dashboard.dashboard_server import start_server
start_server(port=$PORT)
" > logs/dashboard_${PORT}.log 2>&1 &

PID=$!
sleep 3

# 起動確認
if ps -p $PID > /dev/null; then
    echo "✅ 起動完了 (PID: $PID)"
    echo ""
    echo "📍 アクセス:"
    echo "   http://localhost:$PORT"
    echo "   http://0.0.0.0:$PORT"
    echo ""
    echo "📝 ログ確認:"
    echo "   tail -f logs/dashboard_${PORT}.log"
    echo ""
    echo "⏹️  停止方法:"
    echo "   pkill -f dashboard_server.py"
    echo "   または"
    echo "   kill $PID"
else
    echo "❌ 起動に失敗しました"
    echo "   ログを確認: cat logs/dashboard_${PORT}.log"
    exit 1
fi

BG

chmod +x start_dashboard_background_v2.sh
echo "✅ バックグラウンド起動v2作成: start_dashboard_background_v2.sh"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: ポート確認ツールの作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "【STEP 3】ポート確認ツールの作成"
echo ""

cat > tools/check_port.sh << 'CHECK'
#!/bin/bash
# ポート使用状況を確認

PORT=${1:-8000}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 ポート $PORT の使用状況"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if lsof -ti:$PORT >/dev/null 2>&1; then
    echo "⚠️  ポート $PORT は使用中です"
    echo ""
    echo "【詳細情報】"
    lsof -i:$PORT
    echo ""
    
    PID=$(lsof -ti:$PORT)
    echo "【プロセス情報】"
    ps aux | grep $PID | grep -v grep
    echo ""
    
    echo "【停止方法】"
    echo "  kill -9 $PID"
    echo "  または"
    echo "  pkill -f dashboard_server.py"
else
    echo "✅ ポート $PORT は使用可能です"
fi

CHECK

chmod +x tools/check_port.sh
echo "✅ ポート確認ツール作成: tools/check_port.sh"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ポート競合解決完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 新しい起動方法:"
echo ""
echo "【方法1: デフォルトポート（8000）】"
echo "  bash start_dashboard_v2.sh"
echo ""
echo "【方法2: 別のポートを指定】"
echo "  bash start_dashboard_v2.sh --port 8080"
echo ""
echo "【方法3: バックグラウンド起動】"
echo "  bash start_dashboard_background_v2.sh"
echo "  bash start_dashboard_background_v2.sh --port 8080"
echo ""
echo "🔍 ポート確認:"
echo "  bash tools/check_port.sh 8000"
echo ""
echo "⏹️  全ダッシュボード停止:"
echo "  pkill -f dashboard_server.py"
echo ""

# 自動的にダッシュボードを起動
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 ダッシュボードを起動します"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "デフォルトポート(8000)で起動しますか？ [Y/n] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Nn]$ ]]; then
    read -p "使用するポート番号を入力してください [8080]: " PORT
    PORT=${PORT:-8080}
    bash start_dashboard_background_v2.sh --port $PORT
else
    bash start_dashboard_background_v2.sh
fi

