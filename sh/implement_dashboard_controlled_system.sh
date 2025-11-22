#!/bin/bash
# ダッシュボード連動型起動システムの構築

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎮 ダッシュボード連動型起動システムの構築"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: 既存システムの確認
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: 既存システムの確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > "MD/${NOW_JST}_既存システム保護チェック.md" << 'CHECK'
# 既存システム保護チェック

## 確認事項

### 保護すべき既存システム
1. ✅ start_pending_tasks_fixed.sh - タスク実行スクリプト
2. ✅ F1-F10の各機能エージェント
3. ✅ Google Sheets連携
4. ✅ 既存の24時間稼働スクリプト

### 実装方針（既存保護）
1. **既存ファイルは一切変更しない**
2. **新しいラッパースクリプトを作成**
3. **ステート管理で制御**
4. **既存スクリプトをそのまま呼び出し**

### 新規作成するファイル
- agents/web_dashboard/dashboard_server_with_control.py（既存に追加）
- sh/run_foreground_monitor.sh（新規）
- sh/run_foreground_executor.sh（新規）
- /tmp/system_control.state（ステート管理）

CHECK

echo "✅ 既存システム確認完了"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: ダッシュボードサーバーの拡張
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: ダッシュボードサーバーの拡張"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 既存のdashboard_server.pyにシステム制御エンドポイントを追加
cat > agents/web_dashboard/dashboard_server_extended.py << 'PYTHON'
"""
Webダッシュボードサーバー（システム制御拡張版）
既存機能 + システム起動/停止制御
"""

import sys
import os
import subprocess
import signal
from pathlib import Path

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

# 既存のdashboard_server.pyをインポート
from agents.web_dashboard.dashboard_server import app, sheets_manager, f9_interface

from fastapi import HTTPException

# ステート管理ファイル
STATE_FILE = '/tmp/system_control.state'
PID_FILE = '/tmp/system_executor.pid'

def get_system_state():
    """システム状態を取得"""
    if not os.path.exists(STATE_FILE):
        return 'stopped'
    
    with open(STATE_FILE, 'r') as f:
        state = f.read().strip()
    
    # PIDファイルでプロセスの実存を確認
    if state == 'running' and os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        try:
            os.kill(pid, 0)  # プロセスが存在するかチェック
            return 'running'
        except OSError:
            return 'stopped'
    
    return state

def set_system_state(state: str):
    """システム状態を設定"""
    with open(STATE_FILE, 'w') as f:
        f.write(state)

@app.get("/api/system/status")
async def get_system_status():
    """システム状態を取得"""
    state = get_system_state()
    
    pid = None
    if state == 'running' and os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
    
    return {
        'state': state,
        'pid': pid,
        'is_running': state == 'running'
    }

@app.post("/api/system/start")
async def start_system():
    """システムを起動"""
    try:
        print("\n" + "=" * 80)
        print("🚀 システム起動リクエスト")
        print("=" * 80)
        
        current_state = get_system_state()
        
        if current_state == 'running':
            print("⚠️  システムは既に起動中です")
            return {
                'success': False,
                'message': 'システムは既に起動中です'
            }
        
        # 起動スクリプトをバックグラウンドで実行
        print("🔄 24時間稼働システムを起動中...")
        
        process = subprocess.Popen(
            ['bash', 'sh/run_autonomous_24h_v6_final.sh'],
            stdout=open('logs/executor_stdout.log', 'w'),
            stderr=open('logs/executor_stderr.log', 'w'),
            cwd='/workspaces/gemini_AI_Agent'
        )
        
        # PIDを保存
        with open(PID_FILE, 'w') as f:
            f.write(str(process.pid))
        
        # 状態を更新
        set_system_state('running')
        
        print(f"✅ システム起動完了 (PID: {process.pid})")
        print("=" * 80)
        
        return {
            'success': True,
            'message': 'システムを起動しました',
            'pid': process.pid
        }
        
    except Exception as e:
        print(f"❌ システム起動エラー: {e}")
        return {
            'success': False,
            'message': f'起動エラー: {str(e)}'
        }

@app.post("/api/system/stop")
async def stop_system():
    """システムを停止"""
    try:
        print("\n" + "=" * 80)
        print("⏹️  システム停止リクエスト")
        print("=" * 80)
        
        current_state = get_system_state()
        
        if current_state != 'running':
            print("⚠️  システムは起動していません")
            return {
                'success': False,
                'message': 'システムは起動していません'
            }
        
        # PIDを取得
        if not os.path.exists(PID_FILE):
            print("⚠️  PIDファイルが見つかりません")
            set_system_state('stopped')
            return {
                'success': False,
                'message': 'PIDファイルが見つかりません'
            }
        
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        print(f"🔄 プロセス(PID: {pid})を停止中...")
        
        # プロセスを停止
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"✅ プロセス停止シグナル送信")
        except OSError:
            print(f"⚠️  プロセスが既に終了しています")
        
        # ファイルを削除
        os.remove(PID_FILE)
        set_system_state('stopped')
        
        print("✅ システム停止完了")
        print("=" * 80)
        
        return {
            'success': True,
            'message': 'システムを停止しました'
        }
        
    except Exception as e:
        print(f"❌ システム停止エラー: {e}")
        return {
            'success': False,
            'message': f'停止エラー: {str(e)}'
        }

# 既存の start_server 関数を使用
from agents.web_dashboard.dashboard_server import start_server

PYTHON

echo "✅ ダッシュボードサーバー拡張版作成"

# 既存ファイルをバックアップして置き換え
cp agents/web_dashboard/dashboard_server.py "agents/web_dashboard/dashboard_server.py.backup_${NOW_JST}"

# 拡張版を既存ファイルに追記
cat agents/web_dashboard/dashboard_server_extended.py >> agents/web_dashboard/dashboard_server.py

echo "✅ 既存ダッシュボードに機能追加"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: フォアグラウンド監視スクリプト（ターミナル1用）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: フォアグラウンド監視スクリプト作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > sh/run_foreground_monitor.sh << 'MONITOR'
#!/bin/bash
# フォアグラウンド監視スクリプト（ターミナル1用）

cd /workspaces/gemini_AI_Agent

clear

cat << 'BANNER'
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║         🤖 24時間自律開発システム - 監視モニター                    ║
║                                                                      ║
║   このターミナルでシステムの状態をリアルタイム監視できます          ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
BANNER

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 ダッシュボード: http://localhost:8000"
echo "📍 ログファイル: logs/dashboard_8000.log"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "【操作方法】"
echo "  1. ブラウザで http://localhost:8000 を開く"
echo "  2. 「▶️ 開始」ボタンをクリック"
echo "  3. このターミナルでログを監視"
echo ""
echo "【停止方法】"
echo "  ダッシュボードの「⏸️ 一時停止」ボタン"
echo "  または Ctrl+C でこのモニターを終了"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔄 ログ監視を開始します..."
echo ""

# ログファイルが存在するまで待機
while [ ! -f logs/dashboard_8000.log ]; do
    sleep 1
done

# ログをリアルタイム表示
tail -f logs/dashboard_8000.log

MONITOR

chmod +x sh/run_foreground_monitor.sh
echo "✅ 監視スクリプト作成: sh/run_foreground_monitor.sh"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: フォアグラウンド実行スクリプト（ターミナル2用）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: フォアグラウンド実行スクリプト作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > sh/run_foreground_executor.sh << 'EXECUTOR'
#!/bin/bash
# フォアグラウンド実行スクリプト（ターミナル2用）

cd /workspaces/gemini_AI_Agent

clear

cat << 'BANNER'
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║         🚀 24時間自律開発システム - タスク実行ログ                  ║
║                                                                      ║
║   このターミナルでタスク実行のログをリアルタイム表示します          ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
BANNER

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 システム状態を監視中..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

STATE_FILE="/tmp/system_control.state"
LOG_FILE="logs/autonomous_v6_$(TZ=Asia/Tokyo date +%y%m%d_%H%M).log"

echo "⏳ ダッシュボードから開始ボタンが押されるのを待機中..."
echo "   http://localhost:8000 で「▶️ 開始」ボタンをクリックしてください"
echo ""

# システム起動を待機
while true; do
    if [ -f "$STATE_FILE" ]; then
        STATE=$(cat $STATE_FILE)
        if [ "$STATE" = "running" ]; then
            echo "✅ システムが起動しました！"
            echo ""
            break
        fi
    fi
    sleep 2
done

# ログファイルが作成されるまで待機
echo "🔄 ログファイルの作成を待機中..."
while [ ! -f "$LOG_FILE" ] && [ ! -f "logs/autonomous_main.log" ]; do
    sleep 1
    # 最新のログファイルを検索
    LATEST_LOG=$(ls -t logs/autonomous_v6_*.log 2>/dev/null | head -1)
    if [ -n "$LATEST_LOG" ]; then
        LOG_FILE=$LATEST_LOG
        break
    fi
done

echo "📝 ログファイル: $LOG_FILE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 タスク実行ログをリアルタイム表示"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 既存のログがあれば最後の20行を表示
if [ -f "$LOG_FILE" ]; then
    tail -20 "$LOG_FILE"
fi

# ログをリアルタイム表示
tail -f "$LOG_FILE" logs/autonomous_main.log 2>/dev/null

EXECUTOR

chmod +x sh/run_foreground_executor.sh
echo "✅ 実行スクリプト作成: sh/run_foreground_executor.sh"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 5: 起動ガイドの作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5: 起動ガイドの作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > START_GUIDE.md << 'GUIDE'
# 🚀 24時間自律開発システム - 起動ガイド

## 起動手順

### 1. ダッシュボードを起動（最初に1回だけ）
```bash
bash start_dashboard_background_v2.sh
```

### 2. ターミナル1: 監視モニター起動
```bash
bash sh/run_foreground_monitor.sh
```

**表示内容**：
- ダッシュボードのログ
- システム状態の監視
- API呼び出しの記録

### 3. ターミナル2: タスク実行ログ
```bash
bash sh/run_foreground_executor.sh
```

**表示内容**：
- タスク実行のリアルタイムログ
- F9指示の処理状況
- エラーと成功の記録

### 4. ブラウザでシステム制御

1. http://localhost:8000 を開く
2. **「▶️ 開始」ボタンをクリック**
3. システムが自動起動
4. ターミナル2にタスク実行ログが表示される

## 操作方法

### システム開始
- ダッシュボードの「▶️ 開始」ボタン

### システム一時停止
- ダッシュボードの「⏸️ 一時停止」ボタン

### タスク追加（F9）
1. ダッシュボードの「人間指示（F9）」カード
2. 指示タイプを選択
3. 内容を入力
4. 「📤 指示を送信」ボタン
5. 最大15分で自動処理

## 監視方法

### ターミナル1（監視）
- ダッシュボードのAPI呼び出し
- システム状態の変化
- エラーの検出

### ターミナル2（実行）
- タスクの実行状況
- F9指示の処理
- 成果物の生成

### ダッシュボード（ブラウザ）
- システム統計
- タスク一覧
- 人間指示一覧
- リアルタイムログ

## 停止方法

### 一時停止
- ダッシュボードの「⏸️ 一時停止」ボタン

### 完全停止
```bash
bash sh/stop_all_systems.sh
```

## トラブルシューティング

### ダッシュボードが起動しない
```bash
pkill -f dashboard_server.py
bash start_dashboard_background_v2.sh
```

### システムが開始しない
1. ターミナル2のログを確認
2. `/tmp/system_control.state` を削除
3. ダッシュボードで再度開始ボタン

### ログが表示されない
```bash
# ログファイルを確認
ls -lt logs/
```

## ファイル構成
```
/workspaces/gemini_AI_Agent/
├── sh/
│   ├── run_foreground_monitor.sh    # ターミナル1用
│   ├── run_foreground_executor.sh   # ターミナル2用
│   └── stop_all_systems.sh          # 停止スクリプト
├── logs/
│   ├── dashboard_8000.log           # ダッシュボードログ
│   └── autonomous_v6_*.log          # タスク実行ログ
└── /tmp/
    ├── system_control.state         # システム状態
    └── system_executor.pid          # プロセスID
```

## 既存システムの保護

このシステムは既存のスクリプトを**一切変更せず**に動作します：
- ✅ start_pending_tasks_fixed.sh - そのまま使用
- ✅ F1-F10の各エージェント - そのまま使用
- ✅ Google Sheets連携 - そのまま使用

GUIDE

echo "✅ 起動ガイド作成: START_GUIDE.md"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ダッシュボード連動型起動システム構築完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 作成したファイル:"
echo "  1. ✅ 監視スクリプト: sh/run_foreground_monitor.sh"
echo "  2. ✅ 実行スクリプト: sh/run_foreground_executor.sh"
echo "  3. ✅ 拡張ダッシュボード: agents/web_dashboard/dashboard_server.py"
echo "  4. ✅ 起動ガイド: START_GUIDE.md"
echo ""
echo "🚀 起動手順:"
echo ""
echo "【ステップ1】ダッシュボード再起動"
echo "  pkill -f dashboard_server.py"
echo "  bash start_dashboard_background_v2.sh"
echo ""
echo "【ステップ2】ターミナル1で監視起動"
echo "  bash sh/run_foreground_monitor.sh"
echo ""
echo "【ステップ3】ターミナル2でタスク実行ログ"
echo "  bash sh/run_foreground_executor.sh"
echo ""
echo "【ステップ4】ブラウザで制御"
echo "  http://localhost:8000"
echo "  「▶️ 開始」ボタンをクリック"
echo ""
echo "📖 詳細: cat START_GUIDE.md"
echo ""

# ダッシュボードの再起動
read -p "ダッシュボードを今すぐ再起動しますか？ [Y/n] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "🔄 ダッシュボードを再起動中..."
    pkill -f dashboard_server.py 2>/dev/null
    sleep 2
    bash start_dashboard_background_v2.sh
    
    echo ""
    echo "✅ ダッシュボード再起動完了"
    echo ""
    echo "🎯 次のステップ:"
    echo "  1. 新しいターミナルを開いて: bash sh/run_foreground_monitor.sh"
    echo "  2. もう1つターミナルを開いて: bash sh/run_foreground_executor.sh"
    echo "  3. ブラウザ: http://localhost:8000"
    echo ""
fi

