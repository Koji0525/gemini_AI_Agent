#!/bin/bash
# 重要な文書とコードを保護

CRITICAL_FILES=(
    "docs/incident_registry/20251123_file_leak_prevention.md"
    "agents/git_agent/comprehensive_commit.py"
    "scripts/detect_missing_files.sh"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        # 読み取り専用に設定
        chmod 444 "$file"
        echo "✅ 保護完了: $file"
    fi
done

# 保護状態確認スクリプト
cat > scripts/verify_protection.sh << 'VERIFY_EOF'
#!/bin/bash
# 保護ファイルの整合性確認

echo "🔒 保護ファイル状態確認"
for file in "${CRITICAL_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        perms=$(stat -c "%A" "$file")
        if [[ "$perms" == "-r--r--r--" ]]; then
            echo "✅ $file: 保護済み"
        else
            echo "❌ $file: 保護されていません"
            echo "   現在の権限: $perms"
        fi
    fi
done
VERIFY_EOF
