#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "🌐 VNC完全修正"
echo "=========================================="

# ====================================================================
# STEP 1: 既存のVNCプロセスを停止
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 1/5] 既存のVNCプロセス停止${NC}"
echo "=========================================="

# 既存のVNCプロセスを探して停止
if pgrep -x "Xvnc" > /dev/null; then
    echo "既存のVNCプロセスを停止中..."
    vncserver -kill :1 2>/dev/null || true
    sleep 2
fi

# Xvfbも停止
pkill -9 Xvfb 2>/dev/null || true

echo "✅ プロセス停止完了"

# ====================================================================
# STEP 2: VNC設定ファイルの作成
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 2/5] VNC設定ファイル作成${NC}"
echo "=========================================="

mkdir -p ~/.vnc

# パスワードなしのVNC設定
cat > ~/.vnc/xstartup << 'XSTARTUP'
#!/bin/bash
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
exec startxfce4
XSTARTUP

chmod +x ~/.vnc/xstartup

echo "✅ 設定ファイル作成完了"

# ====================================================================
# STEP 3: VNCサーバー起動
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 3/5] VNCサーバー起動${NC}"
echo "=========================================="

# VNCサーバーを起動（解像度1150x600）
vncserver :1 -geometry 1150x600 -depth 24 > /dev/null 2>&1 || {
    echo -e "${YELLOW}⚠️  VNC起動失敗、再試行します...${NC}"
    sleep 2
    vncserver :1 -geometry 1150x600 -depth 24
}

sleep 3

# ====================================================================
# STEP 4: DISPLAY環境変数の設定
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 4/5] DISPLAY環境変数設定${NC}"
echo "=========================================="

export DISPLAY=:1

# .bashrcに永続設定を追加
if ! grep -q "export DISPLAY=:1" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# VNC Display" >> ~/.bashrc
    echo "export DISPLAY=:1" >> ~/.bashrc
    echo "✅ .bashrc に DISPLAY=:1 を追加"
fi

echo "DISPLAY=$DISPLAY"

# ====================================================================
# STEP 5: VNC動作確認
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 5/5] VNC動作確認${NC}"
echo "=========================================="

if pgrep -x "Xvnc" > /dev/null; then
    echo -e "${GREEN}✅ VNCサーバー起動中${NC}"
    
    # ディスプレイテスト
    if DISPLAY=:1 xdpyinfo > /dev/null 2>&1; then
        echo -e "${GREEN}✅ ディスプレイ接続OK${NC}"
    else
        echo -e "${YELLOW}⚠️  ディスプレイ接続に問題があります${NC}"
    fi
else
    echo -e "${RED}❌ VNCサーバーが起動していません${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ VNC修正完了！${NC}"
echo "=========================================="
echo ""
echo "�� VNCアクセス情報:"
echo "   ディスプレイ: :1"
echo "   解像度: 1150x600"
echo "   DISPLAY環境変数: $DISPLAY"
echo ""

