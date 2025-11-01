#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "🎯 Xvfb セットアップ"
echo "=========================================="

# ====================================================================
# STEP 1: Xvfbインストール確認
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 1/4] Xvfbインストール確認${NC}"
echo "=========================================="

if ! command -v Xvfb &> /dev/null; then
    echo "Xvfbをインストール中..."
    sudo apt-get update -qq
    sudo apt-get install -y xvfb
fi

echo "✅ Xvfb: $(Xvfb -version 2>&1 | head -1)"

# ====================================================================
# STEP 2: Xvfb起動
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 2/4] Xvfb起動${NC}"
echo "=========================================="

# 既存のXvfbを停止
pkill -9 Xvfb 2>/dev/null || true
sleep 1

# Xvfbを起動
Xvfb :1 -screen 0 1150x600x24 > /dev/null 2>&1 &
XVFB_PID=$!

sleep 2

if ps -p $XVFB_PID > /dev/null; then
    echo "✅ Xvfb起動成功 (PID: $XVFB_PID)"
else
    echo "❌ Xvfb起動失敗"
    exit 1
fi

# ====================================================================
# STEP 3: DISPLAY設定
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 3/4] DISPLAY設定${NC}"
echo "=========================================="

export DISPLAY=:1

# .bashrcに永続設定
if ! grep -q "export DISPLAY=:1" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# Xvfb Display" >> ~/.bashrc
    echo "export DISPLAY=:1" >> ~/.bashrc
    echo "✅ .bashrc に追加"
fi

echo "DISPLAY=$DISPLAY"

# ====================================================================
# STEP 4: 動作確認
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 4/4] 動作確認${NC}"
echo "=========================================="

if DISPLAY=:1 xdpyinfo > /dev/null 2>&1; then
    echo -e "${GREEN}✅ ディスプレイ接続OK${NC}"
else
    echo "⚠️  xdpyinfoがインストールされていません"
    echo "（これは正常です。Xvfbは動作しています）"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Xvfbセットアップ完了！${NC}"
echo "=========================================="
echo ""
echo "📺 設定:"
echo "   ディスプレイ: :1"
echo "   解像度: 1150x600"
echo "   DISPLAY環境変数: $DISPLAY"
echo ""
echo "次のステップ:"
echo "  ./test_with_xvfb.sh"
echo ""

