#!/bin/bash
set -e

echo "=========================================="
echo "🎯 メイン実行スクリプト作成"
echo "=========================================="

cat > run_all_tasks.sh << 'RUN_ALL'
#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "🚀 全自動タスク実行"
echo "=========================================="

# DISPLAY設定
export DISPLAY=:1

# Xvfb確認
if ! pgrep -x "Xvfb" > /dev/null; then
    echo "⚠️  Xvfbが起動していません"
    echo "   ./setup_xvfb.sh を実行してください"
    exit 1
fi

echo "✅ 環境確認完了"

# TaskExecutor実行
echo ""
echo -e "${BLUE}タスク実行を開始します...${NC}"
echo ""

DISPLAY=:1 python3 scripts/task_executor.py

echo ""
echo "=========================================="
echo -e "${GREEN}✅ 完了${NC}"
echo "=========================================="

RUN_ALL

chmod +x run_all_tasks.sh

echo "✅ run_all_tasks.sh 作成完了"

