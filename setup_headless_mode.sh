#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "🎯 ヘッドレスモードセットアップ"
echo "=========================================="

# ====================================================================
# BrowserControllerをヘッドレスモードに変更
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 1/2] BrowserController修正${NC}"
echo "=========================================="

python3 << 'PYFIX'
# BrowserController を一時的にヘッドレスモードに変更

with open("browser_control/browser_controller.py", "r", encoding="utf-8") as f:
    content = f.read()

# バックアップ
with open("browser_control/browser_controller.py.backup_headless", "w", encoding="utf-8") as f:
    f.write(content)

# headless=Falseを探してTrueに変更
if "headless=False" in content:
    content = content.replace("headless=False", "headless=True")
    
    with open("browser_control/browser_controller.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ ヘッドレスモードに変更しました")
else:
    print("⚠️  既にヘッドレスモード、または設定が見つかりません")

PYFIX

# ====================================================================
# STEP 2: 説明
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 2/2] 説明${NC}"
echo "=========================================="

echo ""
echo "ヘッドレスモードでは:"
echo "  ✅ ディスプレイサーバー不要"
echo "  ✅ 軽量・高速"
echo "  ⚠️  VNCで画面確認不可"
echo ""
echo "このモードは以下の用途に最適:"
echo "  - 自動化タスクの実行"
echo "  - CI/CD環境"
echo "  - デバッグ不要な本番実行"
echo ""

echo "=========================================="
echo -e "${GREEN}✅ ヘッドレスモード設定完了！${NC}"
echo "=========================================="
echo ""
echo "次のステップ:"
echo "  python3 run_uzbekistan_task.py"
echo ""
echo "元に戻す場合:"
echo "  cp browser_control/browser_controller.py.backup_headless browser_control/browser_controller.py"
echo ""

