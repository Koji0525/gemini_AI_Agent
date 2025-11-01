#!/bin/bash
# VNC起動スクリプト (1150x600解像度 - 修正版)

echo "🖥️ VNC起動中..."

# 既存のVNCプロセスをクリーンアップ
pkill -9 Xvnc 2>/dev/null
pkill -9 x11vnc 2>/dev/null
rm -f /tmp/.X1-lock 2>/dev/null
rm -f /tmp/.X11-unix/X1 2>/dev/null

# Xvfb起動（正しい解像度: 1150x600）
Xvfb :1 -screen 0 1150x600x24 &
sleep 2

# x11vnc起動
x11vnc -display :1 -forever -shared -rfbport 5901 &
sleep 2

# 環境変数設定
export DISPLAY=:1

echo "✅ VNC起動完了"
echo "   DISPLAY: $DISPLAY"
echo "   解像度: 1150x600 (修正済み)"
echo "   VNCポート: 5901"
echo "   noVNCポート: 6080 (Webアクセス)"

# プロセス確認
ps aux | grep -E "Xvfb|x11vnc" | grep -v grep
