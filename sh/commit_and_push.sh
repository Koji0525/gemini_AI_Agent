#!/bin/bash
# feature/browser-gemini-integration コミット＆プッシュ

echo "🚀 Git コミット＆プッシュ"
echo "========================================"

# 1. 変更ファイル確認
echo ""
echo "📋 変更ファイル一覧:"
git status --short | head -20
echo "..."
echo ""
echo "変更ファイル数: $(git status --short | wc -l)"

# 2. 全ファイルをステージング
echo ""
echo "📦 全ファイルをステージング..."
git add .
echo "✅ git add . 完了"

# 3. コミット
echo ""
echo "💾 コミット作成中..."
git commit -m "✅ Complete feature/browser-gemini-integration

🎯 完成機能:
- BrowserController完全非同期化（リトライ・エラーハンドリング）
- DesignAgent/DevAgent/ReviewAgentブラウザ統合
- TaskExecutor自動初期化
- VNC環境構築（1150x650）
- フォルダ整理（_ARCHIVE/_WIP準拠）
- タイムアウト統一管理（BrowserConfig）

✅ テスト結果:
- BrowserController: OK
- Agents: OK
- TaskExecutor: OK
- ErrorHandling: OK

📦 主要ファイル:
- browser_control/browser_controller.py
- scripts/task_executor.py
- core_agents/design_agent.py
- core_agents/dev_agent.py
- core_agents/review_agent.py

🎯 次のステップ:
- アカウントA（WordPress連携）とマージ準備完了"

if [ $? -eq 0 ]; then
    echo "✅ コミット成功"
else
    echo "❌ コミット失敗"
    exit 1
fi

# 4. プッシュ
echo ""
echo "🚀 リモートにプッシュ中..."
git push origin feature/browser-gemini-integration

if [ $? -eq 0 ]; then
    echo "✅ プッシュ成功"
else
    echo "❌ プッシュ失敗"
    exit 1
fi

echo ""
echo "========================================"
echo "✅ Git操作完了！"
echo ""
echo "🎯 次のアクション:"
echo "  1. GitHubでプルリクエスト作成"
echo "  2. アカウントAとマージ相談"
echo ""
