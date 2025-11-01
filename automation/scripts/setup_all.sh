#!/bin/bash

echo "============================================================"
echo "🚀 WordPress自動化システム 完全セットアップ"
echo "============================================================"
echo ""

# STEP 1: Pythonパッケージ確認
echo "【STEP 1】Pythonパッケージ確認"
echo "----------------------------"

# 必須パッケージのリスト
packages=("playwright" "python-dotenv" "asyncio")

for package in "${packages[@]}"; do
    if python3 -c "import ${package}" 2>/dev/null; then
        echo "✅ ${package} インストール済み"
    else
        echo "❌ ${package} 未インストール"
        echo "   pip install ${package}"
    fi
done

echo ""

# STEP 2: Playwrightブラウザインストール
echo "【STEP 2】Playwrightブラウザインストール"
echo "----------------------------"

if [ -d "/home/codespace/.cache/ms-playwright/chromium_headless_shell-1187" ]; then
    echo "✅ Chromiumブラウザは既にインストール済み"
else
    echo "📥 Chromiumブラウザをインストール中..."
    python3 -m playwright install chromium
    echo "✅ Chromiumブラウザインストール完了"
fi

echo ""

# STEP 3: システム依存関係
echo "【STEP 3】システム依存関係インストール"
echo "----------------------------"

echo "📦 システム依存関係をインストール中..."
python3 -m playwright install-deps chromium 2>/dev/null || echo "⚠️  一部の依存関係がインストールできませんでした（通常は問題ありません）"

echo ""

# STEP 4: .env設定
echo "【STEP 4】.env設定"
echo "----------------------------"

if grep -q "WP_URL=" .env 2>/dev/null; then
    echo "✅ WordPress設定は既に存在します"
else
    echo "�� WordPress設定を追加中..."
    
    if [ ! -f .env ]; then
        touch .env
    fi
    
    # バックアップ
    cp .env .env.backup 2>/dev/null
    
    # WordPress設定を追加
    cat >> .env << 'ENVEOF'

# WordPress設定
WP_URL=https://uzbek-ma.com
WP_USER=uzbek
WP_PASS=57QV*sUgdJ3OJie1dD7P1^DC
ENVEOF
    
    echo "✅ WordPress設定を追加しました"
fi

echo ""

# STEP 5: 設定確認
echo "【STEP 5】設定確認"
echo "----------------------------"

python3 automation/scripts/verify_env.py

echo ""

# STEP 6: ディレクトリ作成
echo "【STEP 6】必要なディレクトリ作成"
echo "----------------------------"

mkdir -p automation/{logs,logs/day1,modules,tests,scripts,pipelines,dashboard,docs}

echo "✅ ディレクトリ構造作成完了"

echo ""
echo "============================================================"
echo "🎉 セットアップ完了"
echo "============================================================"
echo ""
echo "次のステップ:"
echo "  python3 automation/modules/wp_login_v2.py"
echo ""

