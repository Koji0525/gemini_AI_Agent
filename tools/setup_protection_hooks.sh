#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎣 プレコミットフック自動セットアップ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e

HOOKS_DIR=".git/hooks"
mkdir -p "$HOOKS_DIR"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# pre-commit hook
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cat > "$HOOKS_DIR/pre-commit" << 'HOOK_END'
#!/bin/bash
# 🛡️ 自動保護プレコミットフック

echo "🔍 コミット前チェック開始..."

# .envファイルの変更チェック
if git diff --cached --name-only | grep -q "^\.env$"; then
    echo "⚠️  .envファイルが変更されています"
    
    # バックアップ作成
    if [ -f ".env" ]; then
        python3 tools/env_protector.py backup
    fi
    
    echo "❓ .envの変更を本当にコミットしますか？ (yes/no)"
    read -r response
    if [ "$response" != "yes" ]; then
        echo "❌ コミット中止"
        exit 1
    fi
fi

# Pythonファイルの大幅削減チェック
for file in $(git diff --cached --name-only | grep '\.py$'); do
    if [ -f "$file" ]; then
        OLD_LINES=$(git show HEAD:"$file" 2>/dev/null | wc -l || echo "0")
        NEW_LINES=$(wc -l < "$file")
        
        if [ "$OLD_LINES" -gt 100 ] && [ "$NEW_LINES" -lt $((OLD_LINES * 7 / 10)) ]; then
            echo "⚠️  $file: 行数が大幅削減 ($OLD_LINES → $NEW_LINES)"
            echo "   影響分析を実行しますか？ (yes/no)"
            read -r response
            if [ "$response" = "yes" ]; then
                # 一時ファイルに旧バージョンを保存
                TEMP_OLD=$(mktemp)
                git show HEAD:"$file" > "$TEMP_OLD"
                
                # 分析実行
                python3 tools/code_impact_analyzer.py "$TEMP_OLD" "$file"
                
                rm "$TEMP_OLD"
                
                echo "❓ この変更を続行しますか？ (yes/no)"
                read -r response2
                if [ "$response2" != "yes" ]; then
                    echo "❌ コミット中止"
                    exit 1
                fi
            fi
        fi
    fi
done

echo "✅ チェック完了"
HOOK_END

chmod +x "$HOOKS_DIR/pre-commit"
echo "✅ pre-commitフック設置完了"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# post-checkout hook (.env保護の自動化)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cat > "$HOOKS_DIR/post-checkout" << 'HOOK_END'
#!/bin/bash
# 🔒 チェックアウト後の自動保護

if [ -f ".env" ]; then
    python3 tools/env_protector.py protect
    echo "🔒 .envを自動保護しました"
fi
HOOK_END

chmod +x "$HOOKS_DIR/post-checkout"
echo "✅ post-checkoutフック設置完了"

echo ""
echo "🎉 プレコミットフック設置完了！"
echo "   → .env変更時: 自動バックアップ＋確認"
echo "   → コード大幅削減時: 影響分析＋確認"
echo "   → ブランチ切替後: .env自動保護"
