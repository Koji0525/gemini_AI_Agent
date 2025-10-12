#!/bin/bash
# ========================================
# Claude自動対話ヘルパー
# ========================================

echo "🤖 Claude自動対話システム 起動中..."
echo ""

# カラーコード
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ログディレクトリ作成
mkdir -p claude_logs
LOG_FILE="claude_logs/session_$(date +%Y%m%d_%H%M%S).log"

# セッション情報を記録
echo "========================================" | tee -a $LOG_FILE
echo "Claude対話セッション開始" | tee -a $LOG_FILE
echo "開始時刻: $(date)" | tee -a $LOG_FILE
echo "========================================" | tee -a $LOG_FILE

# 初期プロンプト
cat << 'PROMPT' | tee -a $LOG_FILE

【Claude への依頼】

現在のプロジェクト状況:
- プロジェクト: Gemini AI 自律エージェントシステム
- 環境: GitHub Codespaces
- 最新の進捗を報告します

実行したコマンド:
PROMPT

# コマンド実行と結果の記録
run_and_log() {
    local cmd="$1"
    local desc="$2"
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}▶ $desc${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "$ $cmd" | tee -a $LOG_FILE
    echo "" | tee -a $LOG_FILE
    
    # コマンド実行
    eval "$cmd" 2>&1 | tee -a $LOG_FILE
    local exit_code=${PIPESTATUS[0]}
    
    echo "" | tee -a $LOG_FILE
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ 成功 (終了コード: $exit_code)${NC}" | tee -a $LOG_FILE
    else
        echo -e "${RED}❌ エラー (終了コード: $exit_code)${NC}" | tee -a $LOG_FILE
    fi
    echo "" | tee -a $LOG_FILE
    
    return $exit_code
}

# メインの実行
main() {
    echo "【実行内容】" | tee -a $LOG_FILE
    echo "" | tee -a $LOG_FILE
    
    # 1. プロジェクト構造確認
    run_and_log "ls -la" "1. プロジェクト構造確認"
    
    # 2. 現在のエラー確認
    run_and_log "python autonomous_system.py --test-only" "2. テスト実行"
    
    # 3. 環境変数確認
    run_and_log "python check_all_config.py" "3. 環境設定確認"
    
    # まとめ
    echo "========================================" | tee -a $LOG_FILE
    echo "実行完了: $(date)" | tee -a $LOG_FILE
    echo "========================================" | tee -a $LOG_FILE
    echo "" | tee -a $LOG_FILE
    echo "【Claudeへの質問】" | tee -a $LOG_FILE
    echo "" | tee -a $LOG_FILE
    echo "上記の実行結果を見て、次にどうすればよいでしょうか？" | tee -a $LOG_FILE
    echo "" | tee -a $LOG_FILE
    echo "========================================" | tee -a $LOG_FILE
    echo "" | tee -a $LOG_FILE
    echo -e "${YELLOW}📋 ログファイル: $LOG_FILE${NC}"
    echo -e "${YELLOW}📋 Claudeに貼り付けてください！${NC}"
    echo ""
}

# 実行
main

# ログファイルの内容をクリップボードにコピー（オプション）
if command -v xclip &> /dev/null; then
    cat $LOG_FILE | xclip -selection clipboard
    echo "✅ ログをクリップボードにコピーしました"
fi
