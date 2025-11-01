# 🗺️ システム連携マップ v1.0

## 既存エージェント連携フロー
```
[GitHub Actions入力]
        ↓
[Goal Input Agent] ← **新規開発必要**
        ↓
[PM Agent] ← **既存（動作確認済み）**
    ├─ 目標分解: `decompose_goal()`
    ├─ タスク登録: `pm_tasks` シート
    └─ 進捗監視: `progress_dashboard` シート
        ↓
[Task Executor] ← **既存（拡張必要）**
    ├─ タスク読取: `read_pending_tasks()`
    ├─ ルーティング: `route_to_agent()`
    └─ 実行制御: `execute_task()`
        ↓
[WordPress Orchestrator] ← **既存（動作確認済み）**
    ├─ 認証: `authenticate()`
    ├─ CPT作成: WP CPT Agent
    ├─ ACF設定: WP ACF Agent
    └─ 自動設定: WP AutoConfig Agent
        ↓
[自己修復システム] ← **既存（統合必要）**
    ├─ ErrorClassifier
    ├─ RetryManager
    ├─ DecisionSupportSystem
    └─ KnowledgeBaseManager
        ↓
[結果報告]
    ├─ PM Agentへフィードバック
    └─ Progress Dashboardへ反映
```

## 📍 連携が必要な箇所

### 1️⃣ 入力ゲートウェイ
- **現状**: GitHub Actions → 手動実行
- **必要**: Goal Input Agent
- **連携先**: PM Agent (`pm_tasks`シート)

### 2️⃣ 実行制御ハブ
- **現状**: Task Executor（個別実行）
- **必要**: 統合オーケストレーター
- **連携先**: PM Agent + WordPress Orchestrator + 自己修復

### 3️⃣ 人間インタラクション
- **現状**: なし
- **必要**: Human Interaction Agent
- **連携先**: Task Executor（制御フラグ経由）

### 4️⃣ 進捗可視化
- **現状**: 基本ダッシュボード
- **必要**: リアルタイム更新機能
- **連携先**: Progress Monitor + Webダッシュボード
