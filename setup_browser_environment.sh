#!/bin/bash
# feature/browser-gemini-integration 環境セットアップ

echo "🚀 ブラウザ統合開発環境セットアップ"
echo "========================================="

# 1. Playwright インストール
echo ""
echo "📦 Step 1/5: Playwright インストール"
pip install playwright --quiet
pip install playwright-stealth --quiet

# 2. Playwright ブラウザインストール
echo ""
echo "📦 Step 2/5: Chromiumブラウザインストール"
python3 -m playwright install chromium
python3 -m playwright install-deps chromium

# 3. VNC関連パッケージインストール
echo ""
echo "📦 Step 3/5: VNC環境構築"
sudo apt-get update -qq
sudo apt-get install -y -qq x11vnc xvfb

# 4. 必要なディレクトリ作成
echo ""
echo "📦 Step 4/5: 作業ディレクトリ作成"
mkdir -p browser_data
mkdir -p temp_workspace/downloads
mkdir -p agent_outputs/{pm,design,dev,review}
mkdir -p logs/browser

# 5. 環境変数設定
echo ""
echo "📦 Step 5/5: 環境変数設定"
export DISPLAY=:1
echo "export DISPLAY=:1" >> ~/.bashrc

echo ""
echo "✅ セットアップ完了！"
echo ""
echo "次のステップ:"
echo "  1. VNC起動: ./start_vnc.sh"
echo "  2. テスト実行: python3 test_browser_setup.py"
