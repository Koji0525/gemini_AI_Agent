# 📊 依存関係可視化ダッシュボード 運用マニュアル

**作成日時**: 2025-11-23 12:20 JST  
**対象**: Phase 1-2完了版ダッシュボード  
**ステータス**: 本番稼働可能

---

## 🚀 起動手順

### 方法1: 手動起動（開発・デバッグ用）
```bash
# 1. プロジェクトルートに移動
cd /workspaces/gemini_AI_Agent

# 2. APIサーバー起動（フォアグラウンド）
python3 agents/observer_enhanced/api_server.py

# 出力例:
# ============================================================
# 🚀 依存関係可視化APIサーバー (Phase 2完全版)
# ============================================================
# 📁 プロジェクトルート: /workspaces/gemini_AI_Agent
# 📍 ダッシュボード: http://localhost:5001
# 📖 APIドキュメント: http://localhost:5001/docs
# ⏰ 起動時刻: 2025-11-23 12:20:00
# ...
# 💡 Ctrl+C で停止
```

**メリット**: ログがリアルタイムで見える、デバッグしやすい  
**デメリット**: ターミナルを閉じると停止する

---

### 方法2: バックグラウンド起動（推奨）
```bash
# 1. プロジェクトルートに移動
cd /workspaces/gemini_AI_Agent

# 2. バックグラウンドで起動（ログは/tmp/api_server.logに出力）
python3 agents/observer_enhanced/api_server.py > /tmp/api_server.log 2>&1 &

# 3. プロセスID（PID）を確認
echo "PID: $!"

# 4. 起動確認
curl http://localhost:5001/api/health

# 成功時の出力例:
# {"status":"ok","timestamp":"2025-11-23T21:20:00+09:00",...}
```

**メリット**: ターミナルを閉じても動作継続、本番運用向け  
**デメリット**: ログ確認は別途必要

---

### 方法3: systemdサービス化（本番環境推奨）
```bash
# 1. サービスファイル作成
sudo tee /etc/systemd/system/dependency-dashboard.service > /dev/null << EOF
[Unit]
Description=Dependency Visualization Dashboard
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=/workspaces/gemini_AI_Agent
ExecStart=/usr/bin/python3 agents/observer_enhanced/api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 2. サービス有効化
sudo systemctl daemon-reload
sudo systemctl enable dependency-dashboard
sudo systemctl start dependency-dashboard

# 3. ステータス確認
sudo systemctl status dependency-dashboard
```

**メリット**: 自動起動、障害時の自動再起動、ログ管理  
**デメリット**: 初期設定が複雑

---

## 🔍 ステータス確認

### 1. プロセス確認
```bash
# APIサーバーが起動しているか確認
ps aux | grep api_server.py | grep -v grep

# 出力例:
# codespace  12345  0.5  1.2  123456  98765 ?  S  12:20  0:01 python3 agents/observer_enhanced/api_server.py
```

### 2. ポート確認
```bash
# ポート5001が使用されているか確認
lsof -i :5001

# 出力例:
# COMMAND   PID      USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
# python3 12345 codespace    5u  IPv4 123456      0t0  TCP *:5001 (LISTEN)
```

### 3. ヘルスチェック
```bash
# APIエンドポイントに接続確認
curl http://localhost:5001/api/health

# 成功時の出力:
# {
#   "status": "ok",
#   "timestamp": "2025-11-23T21:20:00.123456+09:00",
#   "data_loaded": true,
#   "total_modules": 1330,
#   ...
# }
```

### 4. ダッシュボード確認
```bash
# HTMLが正常に配信されているか確認
curl -I http://localhost:5001/

# 成功時の出力:
# HTTP/1.1 200 OK
# content-type: text/html; charset=utf-8
# ...
```

---

## ⏹️ 停止手順

### バックグラウンドプロセスの停止
```bash
# 方法1: プロセス名で停止
pkill -f "api_server.py"

# 方法2: PIDを指定して停止
kill <PID>

# 方法3: 強制停止（推奨しない）
kill -9 <PID>
```

### systemdサービスの停止
```bash
sudo systemctl stop dependency-dashboard
```

---

## 🔄 再起動手順

### 通常の再起動
```bash
# 1. 停止
pkill -f "api_server.py"

# 2. 起動
python3 agents/observer_enhanced/api_server.py > /tmp/api_server.log 2>&1 &

# 3. 確認
curl http://localhost:5001/api/health
```

### ワンライナー再起動
```bash
pkill -f "api_server.py" && sleep 2 && python3 agents/observer_enhanced/api_server.py > /tmp/api_server.log 2>&1 & && echo "PID: $!"
```

### systemdサービスの再起動
```bash
sudo systemctl restart dependency-dashboard
```

---

## 📋 ログ確認

### バックグラウンド実行時のログ
```bash
# リアルタイムでログを確認
tail -f /tmp/api_server.log

# 最新100行を確認
tail -100 /tmp/api_server.log

# エラーのみ抽出
grep -i error /tmp/api_server.log
```

### systemdサービスのログ
```bash
# 最新のログを確認
sudo journalctl -u dependency-dashboard -n 50

# リアルタイムでログを確認
sudo journalctl -u dependency-dashboard -f
```

---

## 🌐 アクセス方法

### ローカル環境（GitHub Codespaces）

1. **ダッシュボード**: http://localhost:5001
2. **API仕様書**: http://localhost:5001/docs
3. **診断ページ**: http://localhost:5001/diagnostic

### Codespaces ポート転送設定

GitHub Codespacesでは、ポート5001が自動的に転送されます。

**確認方法**:
1. VS Code下部の「PORTS」タブをクリック
2. ポート5001が「Forwarded Address」に表示される
3. 🌐アイコンをクリックでブラウザで開く

---

## 🔧 トラブルシューティング

### 問題1: ポートが既に使用されている

**症状**:
```
OSError: [Errno 98] Address already in use
```

**解決方法**:
```bash
# 既存プロセスを停止
pkill -f "api_server.py"

# ポートを使用しているプロセスを強制停止
lsof -ti:5001 | xargs kill -9

# 再起動
python3 agents/observer_enhanced/api_server.py > /tmp/api_server.log 2>&1 &
```

---

### 問題2: ダッシュボードが表示されない

**症状**: ブラウザで http://localhost:5001 にアクセスしても表示されない

**確認手順**:
```bash
# 1. APIサーバーが起動しているか確認
ps aux | grep api_server.py | grep -v grep

# 2. ヘルスチェック
curl http://localhost:5001/api/health

# 3. HTMLファイルが存在するか確認
ls -la agents/observer_enhanced/templates/index.html

# 4. ログ確認
tail -50 /tmp/api_server.log
```

**解決方法**:
- APIサーバーが起動していない → 起動する
- ファイルが存在しない → Git pullで最新版を取得
- エラーログがある → エラー内容を確認して修正

---

### 問題3: データが古い

**症状**: ダッシュボードの統計データが最新ではない

**解決方法**:
```bash
# 1. 依存関係データを再生成
python3 scripts/analysis/dependency_mapper.py

# 2. APIサーバーを再起動
pkill -f "api_server.py"
sleep 2
python3 agents/observer_enhanced/api_server.py > /tmp/api_server.log 2>&1 &

# 3. ブラウザで強制リロード（Ctrl+F5）
```

---

### 問題4: 時刻がずれている

**症状**: 更新時刻が実際の時刻と異なる

**確認方法**:
```bash
# サーバー時刻を確認
curl http://localhost:5001/api/health | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('Server time:', data.get('timestamp'))
"

# システム時刻を確認
TZ=Asia/Tokyo date
```

**解決方法**:
- サーバーを再起動
- `pytz`が正しくインストールされているか確認: `pip list | grep pytz`

---

## 📊 定期メンテナンス

### 日次タスク
```bash
# 1. ログローテーション（ログが大きくなりすぎないように）
if [ $(stat -f%z /tmp/api_server.log) -gt 10000000 ]; then
    mv /tmp/api_server.log /tmp/api_server.log.old
    touch /tmp/api_server.log
fi

# 2. 依存関係データ更新（オプション）
python3 scripts/analysis/dependency_mapper.py
```

### 週次タスク
```bash
# 1. 隠れた依存関係の再スキャン
python3 scripts/analysis/hidden_dependency_detector.py

# 2. 循環依存チェック
python3 scripts/analysis/cycle_detector.py

# 3. 破壊的変更チェック
python3 scripts/analysis/breaking_change_detector.py

# 4. APIサーバー再起動（メモリリフレッシュ）
pkill -f "api_server.py"
sleep 2
python3 agents/observer_enhanced/api_server.py > /tmp/api_server.log 2>&1 &
```

---

## 🚀 クイックスタートコマンド

### 完全起動スクリプト
```bash
#!/bin/bash
# complete_startup.sh

cd /workspaces/gemini_AI_Agent

echo "🔍 既存プロセス確認..."
if ps aux | grep -v grep | grep api_server.py > /dev/null; then
    echo "⚠️  既存プロセスを停止中..."
    pkill -f "api_server.py"
    sleep 2
fi

echo "📊 依存関係データ確認..."
if [ ! -f "docs/dependency_map.json" ]; then
    echo "📈 依存関係データ生成中..."
    python3 scripts/analysis/dependency_mapper.py
fi

echo "🚀 APIサーバー起動中..."
python3 agents/observer_enhanced/api_server.py > /tmp/api_server.log 2>&1 &
PID=$!
echo "✅ 起動完了 (PID: $PID)"

sleep 3

echo "🔍 ヘルスチェック..."
if curl -s http://localhost:5001/api/health > /dev/null; then
    echo "✅ APIサーバー正常稼働"
    echo "�� ダッシュボード: http://localhost:5001"
else
    echo "❌ APIサーバー起動失敗"
    echo "📋 ログ確認: tail /tmp/api_server.log"
fi
```

**使用方法**:
```bash
chmod +x complete_startup.sh
./complete_startup.sh
```

---

## �� サポート情報

**問題が解決しない場合**:
1. ログファイルを確認: `tail -100 /tmp/api_server.log`
2. プロセス状態を確認: `ps aux | grep api_server.py`
3. ポート状態を確認: `lsof -i :5001`
4. システムリソースを確認: `free -h`, `df -h`

---

**作成者**: AI Development Assistant  
**最終更新**: 2025-11-23 12:20 JST  
**バージョン**: Phase 2完全版
