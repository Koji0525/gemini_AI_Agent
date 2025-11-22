#!/bin/bash
# 完全自律システムの起動（ダッシュボード + 24時間稼働）

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 完全自律システムの起動"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: ダッシュボード起動確認
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "【STEP 1】ダッシュボード起動確認"
echo ""

if lsof -ti:8000 >/dev/null 2>&1; then
    echo "✅ ダッシュボードは既に起動中です"
    echo "   ポート: 8000"
    echo "   アクセス: http://localhost:8000"
else
    echo "⚠️  ダッシュボードが起動していません"
    echo "🔄 ダッシュボードを起動します..."
    bash start_dashboard_background_v2.sh
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: 24時間稼働システムの起動
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "【STEP 2】24時間稼働システムの起動"
echo ""

# 既存のプロセスをチェック
if pgrep -f "run_autonomous_24h" >/dev/null; then
    echo "⚠️  24時間稼働システムは既に起動中です"
    echo ""
    read -p "再起動しますか？ [y/N] " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 既存プロセスを停止..."
        pkill -f "run_autonomous_24h"
        sleep 3
    else
        echo "✅ 既存プロセスを継続使用します"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "✅ システムは稼働中です"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        exit 0
    fi
fi

echo "🚀 24時間稼働システムを起動します..."
echo ""

# バックグラウンドで起動
nohup bash sh/run_autonomous_24h_v6_final.sh > logs/autonomous_main.log 2>&1 &
MAIN_PID=$!

sleep 3

# 起動確認
if ps -p $MAIN_PID > /dev/null; then
    echo "✅ 24時間稼働システム起動完了 (PID: $MAIN_PID)"
else
    echo "❌ 起動に失敗しました"
    echo "   ログを確認: cat logs/autonomous_main.log"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 完全自律システム起動完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "【稼働中のコンポーネント】"
echo "  1. ✅ Webダッシュボード"
echo "     アクセス: http://localhost:8000"
echo "     ログ: tail -f logs/dashboard_8000.log"
echo ""
echo "  2. ✅ 24時間稼働システム (PID: $MAIN_PID)"
echo "     ログ: tail -f logs/autonomous_main.log"
echo "     詳細ログ: tail -f logs/autonomous_v6_*.log"
echo ""
echo "【人間指示の出し方（F9）】"
echo "  方法1: ブラウザで指示（推奨）"
echo "    1. http://localhost:8000 を開く"
echo "    2. 「人間指示（F9）」カードで指示を入力"
echo "    3. 指示タイプを選択（タスク追加など）"
echo "    4. 「指示を送信」ボタンをクリック"
echo "    5. 次のサイクル（最大15分）で自動処理"
echo ""
echo "  方法2: コマンドラインで指示"
echo "    ./f9 add -t add_task -c '新しいタスク内容' -p high"
echo ""
echo "  方法3: Google Sheets直接編集"
echo "    human_instructions シートに直接入力"
echo ""
echo "【タスク実行結果の確認】"
echo "  1. 成果物: agent_outputs/implementation/"
echo "  2. ログ: agent_outputs/auto_logs/"
echo "  3. 詳細: bash sh/show_task_outputs.sh [タスクID]"
echo ""
echo "【停止方法】"
echo "  すべて停止: bash sh/stop_all_systems.sh"
echo "  ダッシュボードのみ: pkill -f dashboard_server.py"
echo "  24時間稼働のみ: pkill -f run_autonomous_24h"
echo ""
echo "【監視方法】"
echo "  リアルタイムログ: tail -f logs/autonomous_main.log"
echo "  ダッシュボード: http://localhost:8000"
echo ""

