# ダッシュボード修正完了

## 修正内容

### 1. ファイル配置の修正
- ✅ すべての.mdファイルをMD/フォルダに配置
- ✅ MDファイルの命名規則に従う（YYMMDD_HHMM_FEATURE.md）

### 2. ダッシュボードの開始ボタン機能追加
- ✅ `/api/system/start` エンドポイント連携
- ✅ `/api/system/stop` エンドポイント連携
- ✅ システム状態表示（稼働中/停止中）
- ✅ ボタンの有効/無効切り替え

### 3. 動作フロー
```
【ダッシュボード】
  ↓ 開始ボタンクリック
【/api/system/start POST】
  ↓
【24時間稼働システム起動】
  ↓
【ターミナル2にログ表示開始】
  ↓
【15分ごとにpendingタスク実行】
```

## 使用方法

### 1. ダッシュボード再起動
```bash
pkill -f dashboard_server.py
bash start_dashboard_background_v2.sh
```

### 2. ターミナル2でログ監視
```bash
bash sh/run_foreground_executor.sh
```

### 3. ブラウザで開始
1. http://localhost:8000 を開く
2. 「▶️ 開始」ボタンをクリック
3. ターミナル2でログが流れ始める

## トラブルシューティング

### 開始ボタンを押しても動かない場合
1. ダッシュボードのログを確認
```bash
   tail -f logs/dashboard_8000.log
```

2. エンドポイントの動作確認
```bash
   curl -X POST http://localhost:8000/api/system/start
```

3. ダッシュボードを再起動
```bash
   pkill -f dashboard_server.py
   bash start_dashboard_background_v2.sh
```

