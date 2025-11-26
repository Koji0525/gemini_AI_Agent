# 🚀 クイックスタートガイド

## Phase 6統合完了！実運用開始

全統合テスト4/4成功。実際のスプレッドシート連携でタスク分解と実行が可能になりました。

---

## 📋 前提条件

- ✅ Google Sheets API認証設定完了
- ✅ `configuration/service_account.json` 配置済み
- ✅ `.env` ファイル設定済み
- ✅ スプレッドシートID設定済み
- ✅ Phase 6統合テスト成功

---

## 🎯 基本的な使い方

### 1️⃣ F1: ゴール分解

Google Sheetsの`project_goal`シートにあるゴールを、`pm_tasks`シートのタスクに分解します。
```bash
# ゴール分解実行
bash scripts/run_production_system.sh f1
```

**何が起きるか:**
- `project_goal`シートから`status=active`のゴールを取得
- PMAgentV33Epicがゴールを分析
- エピック→ストーリー→タスクに分解
- `pm_tasks`シートにタスクを追加

### 2️⃣ F2: タスク実行

`pm_tasks`シートの`status=pending`タスクを1件実行します。
```bash
# タスク実行（1件）
bash scripts/run_production_system.sh f2
```

**何が起きるか:**
- `pm_tasks`シートから`status=pending`の最優先タスクを取得
- CompleteEngineUltimateがタスクを実行
- 実行結果を`task_execution_log`シートに記録
- タスクステータスを更新（`pending`→`completed` or `failed`）

### 3️⃣ 完全自動（F1→F2）

ゴール分解してからタスク実行まで一気に実行します。
```bash
# 完全自動実行
bash scripts/run_production_system.sh auto
```

**何が起きるか:**
1. F1でゴール分解
2. 自動でF2を実行
3. 1サイクル完了

### 4️⃣ 24時間自律稼働

15分間隔で96サイクル（24時間）連続実行します。
```bash
# 24時間自律稼働
bash scripts/run_production_system.sh 24h
```

**何が起きるか:**
- 15分ごとにF2実行
- 96サイクル連続稼働
- エラー発生時は自動修復（F7）
- 成功パターンを学習（F8）

### 5️⃣ V2モード（階層型システム）

CompleteEngineUltimateV2で実行（Executive Manager、MessageBus使用）
```bash
# V2モード実行
bash scripts/run_production_system.sh v2
```

**何が起きるか:**
- 階層型組織モデルで実行
- Executive Manager → Team Leader → Worker Agent
- MessageBusで通信管理

---

## 📊 Google Sheetsの構造

### project_goal シート

ゴールを管理するシート。

| goal_id | goal_description | status | created_at |
|---------|-----------------|--------|------------|
| 1 | ウズベキスタンのM&Aポータル... | active | 2025-01-01 |
| 6 | 新しいゴール | active | 2025-11-26 |

**重要な列:**
- `goal_id`: ゴールの一意識別子
- `status`: `active`（実行対象）、`completed`（完了）、`cancelled`（中止）

### pm_tasks シート

タスクを管理するシート。

| task_id | goal_id | epic_id | story_id | task_description | status | priority |
|---------|---------|---------|----------|-----------------|--------|----------|
| T001 | 1 | E001 | S001 | タスク内容 | pending | high |

**重要な列:**
- `task_id`: タスクの一意識別子
- `goal_id`: 関連するゴールID
- `status`: `pending`（実行待ち）、`in_progress`（実行中）、`completed`（完了）
- `priority`: `high`、`medium`、`low`

### task_execution_log シート

タスク実行履歴を記録するシート。

| execution_id | task_id | status | elapsed_time | error_message | created_at |
|-------------|---------|--------|--------------|---------------|------------|
| EX001 | T001 | success | 12.5 | null | 2025-11-26 09:00 |

---

## 🔧 トラブルシューティング

### エラー: 認証情報が取得できません

**原因:** `service_account.json`が見つからない

**対処:**
```bash
# ファイル確認
ls -l configuration/service_account.json

# なければ配置
cp path/to/service_account.json configuration/
```

### エラー: アクティブなゴールがありません

**原因:** `project_goal`シートに`status=active`のゴールがない

**対処:**
1. Google Sheetsを開く
2. `project_goal`シートでゴールの`status`列を`active`に設定

### エラー: pendingタスクがありません

**原因:** `pm_tasks`シートに実行可能なタスクがない

**対処:**
```bash
# F1でゴール分解を実行
bash scripts/run_production_system.sh f1
```

### F1実行してもタスクが生成されない

**原因:** ゴールの記述が不明瞭、またはエラー発生

**対処:**
1. ログを確認: `logs/`ディレクトリ
2. ゴールの記述を具体的に修正
3. 再度F1実行

---

## 📈 モニタリング

### 実行ログ確認
```bash
# 最新ログ表示
tail -f logs/$(ls -t logs/ | head -1)

# エラーログのみ
grep ERROR logs/*.log
```

### スプレッドシート確認

1. [Google Sheets](https://docs.google.com/spreadsheets/)を開く
2. スプレッドシートIDで検索（`.env`に記載）
3. シートを確認:
   - `project_goal`: ゴール状況
   - `pm_tasks`: タスク進捗
   - `task_execution_log`: 実行履歴

### ナレッジベース確認
```bash
# 最新ナレッジ検索
python3 << 'EOF'
from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
km = KnowledgeManager()
results = km.search_knowledge("Phase6")
for r in results[:5]:
    print(f"- {r['title']}")
EOF
```

---

## 🎯 次のステップ

### Phase 6完了後

1. **P6-005**: 6時間耐久テスト
```bash
   # 24サイクル（6時間）
   for i in {1..24}; do
       bash scripts/run_production_system.sh f2
       sleep 900  # 15分待機
   done
```

2. **P6-006**: 24時間耐久テスト
```bash
   bash scripts/run_production_system.sh 24h
```

3. **P6-007**: 結果分析とナレッジ登録

### Phase 7への移行

Phase 6完了後、Phase 7（機能拡張）へ：
- F11: 動的タスク追加
- F12: 高度な依存関係管理
- F13: 予測的スケジューリング

---

## 📚 参考資料

- **認証設定**: `MD/phase6_authentication_guide.md`
- **統合テスト**: `tests/integration/test_phase6_integration.py`
- **ナレッジベース**: `knowledge_system/database/knowledge.db`
- **マスターロードマップ**: `/mnt/project/251126____統合マスターロードマップ_v6_0_-_2025.txt`

---

**最終更新**: 2025年11月26日  
**Phase 6統合**: ✅ 完了（4/4テスト成功）
