#!/bin/bash

echo "=" 
echo "🔍 WordPress自動デプロイシステム - セットアップチェック"
echo "="
echo ""

errors=0

# 必要なファイルをチェック
files=(
    "tools/wp_plugin_manager.py"
    "deploy_system/wp_auto_deploy_plugin/auto-deploy-receiver.php"
    "deploy_system/AUTO_DEPLOY_MASTER.py"
    "wp-setup"
    "wp-deploy"
    "QUICK_START.md"
)

echo "【ファイルチェック】"
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file が見つかりません"
        ((errors++))
    fi
done

echo ""
echo "【Python依存関係チェック】"
python3 -c "import requests" 2>/dev/null && echo "✅ requests" || echo "❌ requests (pip install requests で解決)"
python3 -c "import paramiko" 2>/dev/null && echo "✅ paramiko" || echo "⚠️ paramiko (SFTP使用時のみ必要)"

echo ""
if [ $errors -eq 0 ]; then
    echo "✅ すべて正常！"
    echo ""
    echo "📋 次のステップ:"
    echo "   ./wp-setup"
else
    echo "❌ $errors 個のエラーがあります"
    echo ""
    echo "📋 修正方法:"
    echo "   上記のスクリプトを再実行してください"
fi
