#!/bin/bash

echo "=========================================="
echo "🔍 ディスプレイ環境診断"
echo "=========================================="

echo ""
echo "📋 [1/5] 利用可能なディスプレイサーバー"
echo "=========================================="

echo -n "VNC (tigervnc): "
if command -v vncserver &> /dev/null; then
    echo "✅ インストール済み"
else
    echo "❌ 未インストール"
fi

echo -n "Xvfb: "
if command -v Xvfb &> /dev/null; then
    echo "✅ インストール済み"
    Xvfb -version 2>&1 | head -1
else
    echo "❌ 未インストール"
fi

echo -n "X11vnc: "
if command -v x11vnc &> /dev/null; then
    echo "✅ インストール済み"
else
    echo "❌ 未インストール"
fi

echo ""
echo "📋 [2/5] 現在のDISPLAY設定"
echo "=========================================="
echo "DISPLAY: ${DISPLAY:-未設定}"

echo ""
echo "📋 [3/5] 実行中のXサーバー"
echo "=========================================="
if pgrep -x "Xvfb" > /dev/null; then
    echo "✅ Xvfb 実行中"
    pgrep -x "Xvfb" | head -1
elif pgrep -x "Xvnc" > /dev/null; then
    echo "✅ Xvnc 実行中"
    pgrep -x "Xvnc" | head -1
else
    echo "⚠️  Xサーバー未実行"
fi

echo ""
echo "📋 [4/5] Playwright設定"
echo "=========================================="
python3 << 'PYCHECK'
try:
    from playwright.sync_api import sync_playwright
    print("✅ Playwright インストール済み")
except:
    print("❌ Playwright 未インストール")
PYCHECK

echo ""
echo "📋 [5/5] 推奨する解決策"
echo "=========================================="

if command -v Xvfb &> /dev/null; then
    echo "🎯 推奨: Xvfb を使用"
    echo "   Xvfb は軽量で、ヘッドレス環境に最適です"
elif command -v vncserver &> /dev/null; then
    echo "🎯 推奨: VNCサーバー を使用"
else
    echo "🎯 推奨: ヘッドレスモード"
    echo "   ブラウザをヘッドレスモードで実行（最も簡単）"
fi

echo ""
echo "=========================================="
echo "✅ 診断完了"
echo "=========================================="

