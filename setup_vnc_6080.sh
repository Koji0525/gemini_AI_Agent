#!/bin/bash
# VNC 6080ポート追加（WebSocket経由）

echo "🌐 VNC 6080ポート セットアップ"
echo "========================================"

# noVNCインストール確認
if ! command -v websockify &> /dev/null; then
    echo "📦 websockify インストール中..."
    pip install websockify --quiet
fi

# noVNCダウンロード（軽量版）
if [ ! -d "noVNC" ]; then
    echo "📦 noVNC ダウンロード中..."
    git clone --depth 1 https://github.com/novnc/noVNC.git
    cd noVNC
    git checkout v1.4.0
    cd ..
fi

# websockify起動（6080ポートで5901に接続）
echo "🚀 websockify 起動中..."
pkill -f websockify 2>/dev/null
cd noVNC
./utils/novnc_proxy --vnc localhost:5901 --listen 6080 &
cd ..

sleep 2

echo ""
echo "✅ VNC 6080ポート起動完了！"
echo ""
echo "📺 ブラウザでVNC画面を見る方法:"
echo "  1. GitHubのCodespaces画面で「ポート」タブを開く"
echo "  2. 6080ポートを探す"
echo "  3. 「ブラウザで開く」をクリック"
echo ""
echo "または:"
echo "  http://localhost:6080/vnc.html"
echo ""
