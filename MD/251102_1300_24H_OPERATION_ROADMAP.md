# 🗺️ 24時間自律稼働システム 完全ロードマップ

## 📊 現状分析（Document 6より）

### ✅ 完了している機能

| 機能 | 状態 | 詳細 |
|------|------|------|
| **GitHub Issues連携** | ✅ コード実装完了 | `@bot stop`, `@bot resume`, `@bot status`コマンド動作確認済み |
| **進捗ダッシュボード** | ✅ 完全動作 | `progress_dashboard`で完了率91.7%、品質スコア9.1/10表示可能 |
| **自己修復機能** | ✅ Phase 9完了 | ErrorClassifier, RetryManager統合済み |
| **PM Agent** | ✅ 動作確認済み | 目標分解→タスク登録フロー完成 |
| **Task Coordinator** | ✅ 統合完了 | 自己修復機能付きで動作 |
| **シートマッピング** | ✅ 実装完了 | 既存シート構造を活用 |

### ⚠️ 未完了・設定必要な項目

| 項目 | 状態 | 必要な作業 |
|------|------|----------|
| **Cron自動実行** | ❌ 未稼働 | GitHub Actionsワークフローの有効化 |
| **GitHub Secrets** | ⚠️ 一部設定済み | GOOGLE_CREDENTIALSの追加が必要 |
| **重複シート削除** | ⚠️ 未実施 | 4シート(pm_goals等)の削除 |
| **デフォルトブランチ** | ⚠️ 要確認 | ワークフローファイルがmainブランチにあるか |

---

## 🎯 Phase 1: 即時対応（今日中）

### ステップ1-1: 重複シート削除（5分）
```bash
# 実行
python3 tools/cleanup_duplicate_sheets.py

# 確認プロンプトで'yes'を入力
```

**削除されるシート:**
- `pm_goals` → `project_goal`を使用
- `control_flags` → `setting`を使用
- `error_log` → `error_analysis`を使用
- `execution_history` → `history`を使用

### ステップ1-2: GitHub Secrets追加（10分）

**必要なSecret: GOOGLE_CREDENTIALS**
```bash
# 1. サービスアカウントJSONを取得
cat configuration/service_account.json

# 2. GitHubで設定
# Settings > Secrets and variables > Actions > New repository secret
# Name: GOOGLE_CREDENTIALS
# Value: JSONの内容全体をペースト
```

**確認:**
```bash
gh secret list
# 以下が表示されればOK:
# GOOGLE_CREDENTIALS
# SPREADSHEET_ID
# WP_URL
# WP_USER
# WP_PASS
# GEMINI_API_KEY
# ... (既存のSecrets)
```

### ステップ1-3: ワークフローファイルの確認（5分）
```bash
# ワークフローファイルがmainブランチにあるか確認
git branch
git checkout main  # mainでない場合
git pull origin main

# ワークフローファイルの存在確認
ls .github/workflows/autonomous_dev_system.yml

# GitHubにプッシュ
git add .github/workflows/autonomous_dev_system.yml
git commit -m "🚀 24時間自律開発システム ワークフロー追加"
git push origin main
```

---

## 🚀 Phase 2: 初回実行テスト（今日中）

### ステップ2-1: テスト目標の登録（5分）
```bash
# スプレッドシートのproject_goalシートに手動で追加:
# goal_id: TEST_20251102
# description: テスト実行 - システム動作確認
# priority: high
# status: active
# progress: 0%
# created_at: 2025-11-02T12:00:00
```

### ステップ2-2: GitHub Actionsで手動実行（10分）

1. **GitHubリポジトリを開く**
```
   https://github.com/<your-username>/<your-repo>/actions
```

2. **ワークフロー確認**
   - 左サイドバーに「24時間自律開発システム」が表示されるか確認
   - 表示されない場合 → mainブランチにワークフローファイルがない

3. **Run workflowをクリック**
```
   目標: テスト実行 - システム動作確認
   優先度: high
```

4. **実行開始**
   - 「Run workflow」を再度クリック
   - ワークフローが開始されるのを確認

5. **ログを確認**
```
   期待される出力:
   ✅ 認証情報セットアップ完了
   ✅ 目標登録完了
   ✅ PM Agentが目標を分解
   ✅ タスクがpm_tasksに登録
   ✅ Task Coordinatorがタスク実行
```

### ステップ2-3: スプレッドシートで確認（5分）
```
1. pm_tasksシートを開く
   → TEST_20251102から分解されたタスクがあるか

2. task_execution_logシートを開く
   → タスクの実行結果が記録されているか

3. progress_dashboardシートを開く
   → 進捗率が更新されているか
```

---

## ⏰ Phase 3: Cron自動実行の有効化（1-2日後）

### ステップ3-1: 初回Cron実行を待機
```
次の自動実行時刻:
- 0:00 JST
- 6:00 JST
- 12:00 JST
- 18:00 JST

※初回の自動実行を待つ（最大6時間）
```

### ステップ3-2: Cron実行の確認
```bash
# GitHub Actionsで確認
# https://github.com/<your-username>/<your-repo>/actions

# 自動実行が開始されたか確認:
# - トリガー: schedule
# - 実行時刻が0:00/6:00/12:00/18:00のいずれか
```

### ステップ3-3: トラブルシューティング

**Cronが実行されない場合:**
```bash
# 原因1: デフォルトブランチでない
git checkout main
git pull
git push

# 原因2: リポジトリがプライベート
# → Settingsで確認、必要に応じてパブリックに変更

# 原因3: ワークフローが無効化されている
# → Actions > ワークフロー > "Enable workflow"をクリック
```

---

## 📊 Phase 4: 監視体制の確立（1週間）

### ステップ4-1: 毎日の確認ルーチン（5分/日）
```bash
# 1. GitHub Actionsの確認
#    → 実行が成功しているか

# 2. スプレッドシート確認
python3 << 'CHECK_EOF'
from tools.sheets_manager import GoogleSheetsManager

manager = GoogleSheetsManager()

# タスク状況
tasks = manager.read_range('pm_tasks!A2:D100')
total = len(tasks)
completed = sum(1 for row in tasks if len(row) > 3 and row[3] == 'completed')

print(f"タスク進捗: {completed}/{total} ({completed/total*100:.1f}%)")

# エラー確認
errors = manager.read_range('error_log!A2:E100')
unresolved = sum(1 for row in errors if len(row) > 3 and row[3] != 'resolved')

print(f"未解決エラー: {unresolved}件")
CHECK_EOF
```

### ステップ4-2: 週次レビュー（30分/週）
```bash
# システム監視レポート実行
python3 tools/system_monitor.py

# 確認項目:
# - タスク完了率
# - エラー率
# - ナレッジベース成長率
# - 品質スコアのトレンド
# - ボトルネックの有無
```

---

## 🎯 Phase 5: 最適化（1ヶ月後）

### ステップ5-1: パフォーマンス分析
```bash
# 実行時間の分析
python3 << 'PERF_EOF'
from tools.sheets_manager import GoogleSheetsManager
from datetime import datetime

manager = GoogleSheetsManager()
logs = manager.read_range('execution_history!A2:F100')

# 実行時間の統計
execution_times = []
for row in logs:
    if len(row) > 4:
        try:
            start = datetime.fromisoformat(row[2])
            end = datetime.fromisoformat(row[3])
            duration = (end - start).total_seconds()
            execution_times.append(duration)
        except:
            pass

if execution_times:
    avg_time = sum(execution_times) / len(execution_times)
    max_time = max(execution_times)
    min_time = min(execution_times)
    
    print(f"平均実行時間: {avg_time/60:.1f}分")
    print(f"最長: {max_time/60:.1f}分")
    print(f"最短: {min_time/60:.1f}分")

---

## 📈 成功の指標と評価基準

### 短期目標（1週間後: 2025年11月9日）

| 指標 | 目標値 | 確認方法 |
|------|--------|----------|
| タスク完了数 | 10個以上 | `python3 tools/system_monitor.py` |
| タスク完了率 | 50%以上 | pm_tasksシートで確認 |
| エラー率 | 50%以下 | system_monitorのエラー統計 |
| 自己修復成功回数 | 3回以上 | error_analysisシートで`resolved`カウント |
| Cron自動実行 | 28回以上 | GitHub Actions履歴（7日×4回/日） |
| ナレッジベース | 5個以上 | knowledge_baseシートの行数 |

### 中期目標（1ヶ月後: 2025年12月2日）

| 指標 | 目標値 | 確認方法 |
|------|--------|----------|
| タスク完了数 | 50個以上 | system_monitor |
| タスク完了率 | 70%以上 | pm_tasksシート |
| エラー率 | 30%以下 | system_monitor |
| 平均品質スコア | 8.0以上 | task_execution_logのQuality_Score平均 |
| ナレッジベース | 20個以上 | knowledge_baseシート |
| 自動実行成功率 | 90%以上 | GitHub Actions成功/失敗比率 |

### 長期目標（3ヶ月後: 2026年2月2日）

| 指標 | 目標値 | 確認方法 |
|------|--------|----------|
| タスク完了数 | 200個以上 | system_monitor |
| タスク完了率 | 80%以上 | pm_tasksシート |
| エラー率 | 10%以下 | system_monitor |
| 平均品質スコア | 9.0以上 | task_execution_log |
| ナレッジベース | 50個以上 | knowledge_baseシート |
| 完全自律稼働日数 | 7日以上連続 | GitHub Actions履歴で人間介入なし |

---

## 🎯 各Phase実行コマンド早見表
```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Phase 1: 即時対応
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 重複シート削除
python3 tools/cleanup_duplicate_sheets.py

# GitHub Secrets確認
gh secret list

# ワークフローファイル確認
ls .github/workflows/autonomous_dev_system.yml

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Phase 2: 初回実行テスト
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ローカルテスト
python3 scripts/integrated_orchestrator_v05_final.py

# システムヘルスチェック
python3 tools/final_health_check.py

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Phase 4: 監視
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# システム監視レポート
python3 tools/system_monitor.py

# タスク状況確認
python3 -c "
from tools.sheets_manager import GoogleSheetsManager
m = GoogleSheetsManager()
tasks = m.read_range('pm_tasks!A2:D100')
print(f'総タスク: {len(tasks)}')
print(f'完了: {sum(1 for r in tasks if len(r)>3 and r[3]==\"completed\")}')
"

# エラー状況確認
python3 -c "
from tools.sheets_manager import GoogleSheetsManager
m = GoogleSheetsManager()
errors = m.read_range('error_log!A2:E100')
print(f'総エラー: {len(errors)}')
print(f'未解決: {sum(1 for r in errors if len(r)>3 and r[3]!=\"resolved\")}')
"
```

---

## 🚨 トラブルシューティング早見表

### 問題1: GitHub Actionsが実行されない
```bash
# 確認1: ワークフローがmainブランチにあるか
git branch
git checkout main
git log --oneline -5 .github/workflows/

# 確認2: ワークフローファイルの構文エラー
# GitHubで Actions > ワークフロー名 > "..." > View workflow file

# 確認3: リポジトリ設定
# Settings > Actions > General > "Allow all actions and reusable workflows"

# 確認4: 手動で1度実行
# Actions > ワークフロー名 > Run workflow
```

### 問題2: 認証エラーが発生する
```bash
# 確認1: Secrets設定
gh secret list

# 確認2: サービスアカウントファイル
cat configuration/service_account.json | jq .

# 確認3: スプレッドシート権限
# サービスアカウントのメールアドレスに編集者権限があるか確認

# 確認4: ローカルテスト
python3 << 'EOF'
from tools.sheets_manager import GoogleSheetsManager
try:
    m = GoogleSheetsManager()
    data = m.read_range('pm_tasks!A1:A1')
    print("✅ 認証成功")
except Exception as e:
    print(f"❌ 認証失敗: {e}")
EOF
```

### 問題3: タスクが実行されない
```bash
# 確認1: project_goalにactiveな目標があるか
python3 << 'EOF'
from tools.sheets_manager import GoogleSheetsManager
m = GoogleSheetsManager()
goals = m.read_range('pm_goals!A2:F100')
active = [r for r in goals if len(r)>3 and r[3]=='active']
print(f"アクティブな目標: {len(active)}件")
for goal in active:
    print(f"  - {goal[0]}: {goal[1]}")
EOF

# 確認2: pm_tasksにpendingタスクがあるか
python3 << 'EOF'
from tools.sheets_manager import GoogleSheetsManager
m = GoogleSheetsManager()
tasks = m.read_range('pm_tasks!A2:K100')
pending = [r for r in tasks if len(r)>3 and r[3]=='pending']
print(f"保留中タスク: {len(pending)}件")
EOF

# 確認3: オーケストレーターのログ確認
# GitHub Actions > 最新実行 > "オーケストレーター実行" ステップのログ
```

### 問題4: エラー率が高い
```bash
# エラー分析
python3 << 'EOF'
from tools.sheets_manager import GoogleSheetsManager
from collections import Counter

m = GoogleSheetsManager()
errors = m.read_range('error_log!A2:E100')

# エラータイプ別集計
error_types = [r[1] for r in errors if len(r)>1]
counter = Counter(error_types)

print("【エラータイプTOP5】")
for error_type, count in counter.most_common(5):
    print(f"  {error_type}: {count}回")
    
print("\n【対策】")
print("1. 最頻出エラーのknowledge_baseレシピを確認")
print("2. エージェントのプロンプト改善")
print("3. タイムアウト設定の見直し")
EOF
```

---

## ✅ チェックリスト

### Phase 1完了確認
- [ ] 重複シート削除完了
- [ ] GOOGLE_CREDENTIALS設定完了
- [ ] ワークフローファイルmainブランチ配置完了

### Phase 2完了確認
- [ ] テスト目標登録完了
- [ ] GitHub Actions手動実行成功
- [ ] スプレッドシートに結果記録確認

### Phase 3完了確認
- [ ] 初回Cron自動実行成功
- [ ] 6時間ごとの実行確認（24時間監視）

### Phase 4完了確認
- [ ] system_monitor.py動作確認
- [ ] 毎日のチェックルーチン確立
- [ ] 週次レビュー実施

### Phase 5完了確認
- [ ] パフォーマンス分析実施
- [ ] ナレッジベース整理完了
- [ ] エージェント改善実施

### Phase 6完了確認（オプション）
- [ ] Slack通知設定完了
- [ ] Google Apps Script監視設定完了

---

**最終更新**: 2025年11月2日  
**次回更新予定**: 2025年11月9日（Phase 3-4完了後）

