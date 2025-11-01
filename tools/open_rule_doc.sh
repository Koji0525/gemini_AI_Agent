#!/bin/bash
# ルールドキュメントを開く

RULE_ID=$1

if [ -z "$RULE_ID" ]; then
    echo "使い方: ./tools/open_rule_doc.sh <ルールID>"
    echo ""
    echo "例:"
    echo "  ./tools/open_rule_doc.sh R001"
    exit 1
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. ルール検索してリンク取得
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DOC_LINK=$(python3 << PYEOF
import sys
import os
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from dotenv import load_dotenv
load_dotenv('.env')

from tools.sheets_manager import GoogleSheetsManager

sheets = GoogleSheetsManager(
    spreadsheet_id=os.getenv("SPREADSHEET_ID"),
    service_account_file="configuration/service_account.json"
)

spreadsheet = sheets.gc.open_by_key(os.getenv("SPREADSHEET_ID"))
rules_sheet = spreadsheet.worksheet('dev_rules')

all_data = rules_sheet.get_all_values()

for row in all_data[1:]:
    if row[0] == "$RULE_ID":
        print(row[4])  # doc_link
        break
PYEOF
)

if [ -z "$DOC_LINK" ]; then
    echo "❌ $RULE_ID が見つかりません"
    exit 1
fi

echo "📄 $RULE_ID のドキュメント:"
echo "   $DOC_LINK"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. 開き方を選択
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "どの方法で開きますか？"
echo ""
echo "1) ブラウザで開く（GitHub）"
echo "2) VSCodeで開く（ローカル）"
echo "3) ターミナルで表示"
echo "4) URLをコピー"
echo ""
read -p "選択 (1-4): " choice

case $choice in
    1)
        echo "🌐 ブラウザで開きます..."
        if [[ "$DOC_LINK" == http* ]]; then
            # GitHub URL
            xdg-open "$DOC_LINK" 2>/dev/null || open "$DOC_LINK" 2>/dev/null || echo "$DOC_LINK"
        else
            # 相対パス → ローカルファイルをブラウザで
            LOCAL_FILE=$(echo "$DOC_LINK" | cut -d'#' -f1)
            xdg-open "$LOCAL_FILE" 2>/dev/null || open "$LOCAL_FILE" 2>/dev/null
        fi
        ;;
    2)
        echo "📝 VSCodeで開きます..."
        LOCAL_FILE=$(echo "$DOC_LINK" | sed 's|.*/blob/.*/||' | cut -d'#' -f1)
        code "$LOCAL_FILE"
        ;;
    3)
        echo "📖 ターミナルで表示..."
        LOCAL_FILE=$(echo "$DOC_LINK" | sed 's|.*/blob/.*/||' | cut -d'#' -f1)
        
        # アンカーがある場合はその部分を探す
        if [[ "$DOC_LINK" == *"#"* ]]; then
            ANCHOR=$(echo "$DOC_LINK" | cut -d'#' -f2)
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "セクション: $ANCHOR"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            # セクション見出しを検索
            grep -A 20 "$ANCHOR" "$LOCAL_FILE" | head -30
        else
            cat "$LOCAL_FILE" | less
        fi
        ;;
    4)
        echo "📋 URLをクリップボードにコピー..."
        echo "$DOC_LINK" | pbcopy 2>/dev/null || echo "$DOC_LINK" | xclip -selection clipboard 2>/dev/null || echo "$DOC_LINK"
        echo "✅ コピー完了: $DOC_LINK"
        ;;
    *)
        echo "❌ 無効な選択"
        ;;
esac
