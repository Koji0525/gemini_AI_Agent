#!/bin/bash
# F1-F10の使い方、注意点、特徴の完全ガイド作成

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 F1-F10完全ガイド作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

cat > "MD/${NOW_JST}_F1-F10完全ガイド.md" << 'GUIDE'
# F1-F10完全ガイド

**作成日時**: $(TZ=Asia/Tokyo date +"%Y-%m-%d %H:%M:%S JST")  
**対象**: 24時間自律稼働システム

---

## 📋 目次

1. [F1: ゴール自動分解](#f1-ゴール自動分解)
2. [F2: タスク自律実行](#f2-タスク自律実行)
3. [F3: 品質自動評価](#f3-品質自動評価)
4. [F4: ナレッジ自動蓄積](#f4-ナレッジ自動蓄積)
5. [F5: 進捗自動可視化](#f5-進捗自動可視化)
6. [F6: 動的タスク追加](#f6-動的タスク追加)
7. [F7: 自己修復機能](#f7-自己修復機能)
8. [F8: 自己進化機能](#f8-自己進化機能)
9. [F9: 人間連携機能](#f9-人間連携機能)
10. [F10: 定期健全性チェック](#f10-定期健全性チェック)
11. [統合運用](#統合運用)

---

## F1: ゴール自動分解

### 📌 概要
プロジェクトのゴールを実行可能なタスクに自動分解する機能。

### 🔄 Loop
**Loop 0（初期設定）** - 最初に1回だけ、または新ゴール追加時

### ⚡ トリガー
- 手動実行
- 新しいゴールがproject_goalシートに追加された時

### 📁 実装ファイル
- `agents/goal_concrete_agent.py`
- `core_agents/pm_agent_v31.py`

### 💻 使い方

#### 手動実行
```bash
# ゴール具体化の実行
python3 -c "
from agents.complete_engine_ultimate import CompleteEngineUltimate
engine = CompleteEngineUltimate()
# ゴール具体化は通常、CompleteEngineの初期化時に自動実行
"
```

#### Google Sheetsでの準備
1. `project_goal`シートに新しいゴールを追加
2. goal_id, goal_description, statusを記入
3. F1が自動的にタスクに分解

### ⚠️ 注意点
1. **実行頻度**: 初回のみ、または新ゴール追加時のみ
2. **既存タスク保護**: 既にタスクが存在する場合は追加分解しない
3. **品質**: タスク分解の品質はゴール記述の詳細度に依存

### ✨ 特徴
- ✅ 自然言語のゴールを構造化タスクに変換
- ✅ タスク間の依存関係を自動設定
- ✅ 優先度の自動判定
- ✅ pm_tasksシートに自動登録

### 📊 出力先
- Google Sheets: `pm_tasks`シート

---

## F2: タスク自律実行

### 📌 概要
pendingタスクを自動的に実行し、成果物を生成する機能。

### 🔄 Loop
**Loop 1（タスク実行ループ）** - 3分ごと、または手動実行

### ⚡ トリガー
- 定期実行（3分間隔）
- 手動実行（`start_pending_tasks.sh`）

### 📁 実装ファイル
- `agents/complete_engine_ultimate.py`
- `task_executor.py`
- `agents/task_executor_enhanced.py`

### 💻 使い方

#### 手動実行（推奨）
```bash
# 1件のタスクを実行
bash start_pending_tasks.sh --limit 1

# 3件のタスクを実行
bash start_pending_tasks.sh --limit 3

# 全てのpendingタスクを実行（注意！）
bash start_pending_tasks.sh
```

#### Pythonから実行
```python
from agents.complete_engine_ultimate import CompleteEngineUltimate

engine = CompleteEngineUltimate()
result = engine.execute_task(task_data)
```

### ⚠️ 注意点
1. **同時実行**: 複数のタスク実行を同時に開始しない
2. **タイムアウト**: 長時間タスクは途中で中断される可能性
3. **API制限**: Claude API使用量に注意
4. **成果物保存**: `agent_outputs/`ディレクトリを定期的に確認

### ✨ 特徴
- ✅ 実装、テスト、ドキュメント作成など多様なタスク対応
- ✅ F4（ナレッジ参照）で過去の成功パターンを活用
- ✅ F3（品質評価）で自動評価
- ✅ エラー時はF7（自己修復）が自動起動

### �� 出力先
- 成果物: `agent_outputs/implementation/`, `agent_outputs/testing/`
- ログ: `task_execution_log`シート
- ステータス: `pm_tasks`シートのstatus列

---

## F3: 品質自動評価

### 📌 概要
タスク実行結果の品質を自動評価し、スコアを付与する機能。

### 🔄 Loop
**Loop 1（タスク実行後）** - F2の実行直後

### ⚡ トリガー
- タスク完了時に自動実行

### 📁 実装ファイル
- `agents/quality_evaluator.py`

### 💻 使い方

#### 自動実行
F2のタスク実行時に自動的に評価される（通常は手動実行不要）

#### 手動評価
```python
from agents.complete_engine_ultimate import CompleteEngineUltimate

engine = CompleteEngineUltimate()
score = engine.quality_evaluator.evaluate(
    task_id="6_example_01",
    output_path="agent_outputs/implementation/...",
    task_type="implementation"
)
```

### ⚠️ 注意点
1. **評価基準**: 完了度、正確性、効率性、保守性の4項目
2. **スコア範囲**: 0-100点（60点以上が合格）
3. **低スコア**: 60点未満は改善提案が生成される

### ✨ 特徴
- ✅ 4つの観点から多角的評価
- ✅ 改善提案の自動生成
- ✅ 品質スコアはF8（自己進化）の学習に使用
- ✅ 評価結果はナレッジとして蓄積

### 📊 出力先
- `task_execution_log`シートの`quality_score`列

---

## F4: ナレッジ自動蓄積

### 📌 概要
タスク実行の成功パターン、失敗パターンを自動的にナレッジベースに蓄積する機能。

### 🔄 Loop
- **Loop 1**: タスク完了時に蓄積
- **Loop 3**: 学習時にパターン抽出

### ⚡ トリガー
- タスク完了時（自動）
- 学習サイクル時（6時間ごと、50エラー蓄積時）

### 📁 実装ファイル
- `knowledge_system/core_agents/knowledge_manager.py`
- `knowledge_system/core_agents/sqlite_manager.py`
- `knowledge_system/database/knowledge.db`

### 💻 使い方

#### ナレッジ追加（自動）
F2のタスク実行時に自動的に蓄積される

#### ナレッジ検索
```python
from agents.complete_engine_ultimate import CompleteEngineUltimate

engine = CompleteEngineUltimate()

# ナレッジ検索
results = engine.knowledge_wrapper.search_knowledge(
    query="エラー処理の実装方法",
    limit=5
)

# ナレッジ統計
stats = engine.knowledge_wrapper.get_statistics()
print(stats)  # {"total_knowledge": 512, ...}
```

#### 手動ナレッジ追加
```python
result = engine.knowledge_wrapper.add_knowledge(
    title="重要な学習事項",
    content="詳細な内容...",
    category="best_practice",
    tags="python,error_handling"
)
```

### ⚠️ 注意点
1. **データ形式**: 辞書型で渡す必要がある
2. **重複**: 類似ナレッジの重複に注意
3. **容量**: SQLiteデータベースのサイズ管理
4. **ベクトル検索**: FAISSインデックスの定期的な再構築

### ✨ 特徴
- ✅ SQLite + FAISSのハイブリッド検索
- ✅ 多言語対応（paraphrase-multilingual-MiniLM-L12-v2）
- ✅ 成功/失敗/修正レシピの3種類を蓄積
- ✅ 現在512件のナレッジを蓄積済み

### 📊 出力先
- `knowledge_system/database/knowledge.db`
- `knowledge_system/database/faiss_index/knowledge.index`

---

## F5: 進捗自動可視化

### 📌 概要
プロジェクト全体の進捗をダッシュボードで可視化する機能。

### �� Loop
**独立実行** - 手動実行、または定期実行

### ⚡ トリガー
- 手動実行
- 定期実行（cron設定）

### 📁 実装ファイル
- `agents/observability/dashboard.py`
- `agents/f5_f6_integration.py`（統合モジュール）

### 💻 使い方

#### ダッシュボード表示
```bash
# コマンドライン実行
python3 agents/observability/dashboard.py
```

#### CompleteEngineから実行
```python
from agents.complete_engine_ultimate import CompleteEngineUltimate
from agents.f5_f6_integration import F5F6Integration

engine = CompleteEngineUltimate()

# F5統合
integration = F5F6Integration(
    sheets_manager=getattr(engine, 'sheets', None)
)
integration.integrate_to_engine(engine)

# 進捗表示
engine.show_progress()

# 進捗サマリー取得
summary = engine.get_progress_summary()
print(summary)
```

### ⚠️ 注意点
1. **API使用**: Google Sheets APIの読み取り制限
2. **メソッド名**: `read_sheet()`ではなく正しいメソッド名を使用
3. **表示**: ターミナルでの表示のみ（Webダッシュボードは別途開発）

### ✨ 特徴
- ✅ ゴール別進捗率の表示
- ✅ 平均品質スコアの算出
- ✅ タスク完了率の可視化
- ✅ リアルタイム更新対応

### 📊 出力先
- 標準出力（ターミナル）

---

## F6: 動的タスク追加

### 📌 概要
システム実行中に必要に応じてタスクを動的に追加する機能。

### 🔄 Loop
**Loop 1** - タスク実行中、必要時に自動

### ⚡ トリガー
- タスク実行中に追加作業が必要と判断された時
- 手動でのタスク追加要求

### 📁 実装ファイル
- `agents/f5_f6_integration.py`（DynamicTaskManager）
- `agents/complete_engine_ultimate.py`（既存メソッド活用）

### 💻 使い方

#### 動的タスク追加
```python
from agents.complete_engine_ultimate import CompleteEngineUltimate
from agents.f5_f6_integration import F5F6Integration

engine = CompleteEngineUltimate()

# F6統合
integration = F5F6Integration(
    sheets_manager=getattr(engine, 'sheets', None)
)
integration.integrate_to_engine(engine)

# タスク追加
result = engine.add_dynamic_task(
    goal_id="6",
    description="緊急修正タスク",
    priority="high",
    dependencies=""
)
print(result)  # {"success": True, "task_id": "6_dynamic_..."}
```

#### 既存メソッドの活用
```python
# CompleteEngineの既存メソッド
engine.generate_additional_tasks()  # 追加タスク生成
engine.save_tasks_to_sheet(tasks)   # Sheetsに保存
```

### ⚠️ 注意点
1. **重複**: 同じタスクの重複追加に注意
2. **優先度**: 既存タスクとの優先度バランス
3. **依存関係**: 依存関係の循環参照を避ける
4. **承認**: 重要なタスクは人間の承認を推奨

### ✨ 特徴
- ✅ 実行時の柔軟な対応
- ✅ 優先度の動的調整
- ✅ バッチIDで動的タスクを識別
- ✅ Google Sheetsに即座に反映

### 📊 出力先
- `pm_tasks`シート（batch_id="dynamic"）

---

## F7: 自己修復機能

### 📌 概要
タスク実行中のエラーを自動検出し、最大3回まで自動修復を試みる機能。

### 🔄 Loop
**Loop 2（自己修復ループ）** - エラー検出時に起動

### ⚡ トリガー
- タスク実行エラー検出時（自動）
- 最大3回までリトライ

### 📁 実装ファイル
- `agents/self_healing_agent.py`
- `agents/self_healing/self_healing_agent.py`

### 💻 使い方

#### 自動実行
F2のタスク実行中にエラーが発生すると自動的に起動（手動実行不要）

#### 動作フロー
```
エラー検出
  ↓
F7: 自己修復起動
  ↓
1回目リトライ → 成功 → 続行
  ↓ 失敗
2回目リトライ → 成功 → 続行
  ↓ 失敗
3回目リトライ → 成功 → 続行
  ↓ 失敗
F9: 人間への通知
```

### ⚠️ 注意点
1. **リトライ回数**: 最大3回まで
2. **修復戦略**: エラーの種類によって修復方法が異なる
3. **ログ記録**: すべての修復試行がログに記録される
4. **API使用量**: リトライによりAPI使用量が増加

### ✨ 特徴
- ✅ 9カテゴリ63パターンのエラー分類
- ✅ 適応的リトライ戦略（指数バックオフ）
- ✅ ナレッジベース参照による修復
- ✅ 修復履歴の自動記録

### 📊 出力先
- `context_log`シート（修復履歴）
- `task_execution_log`シート（retry_count）

---

## F8: 自己進化機能

### 📌 概要
成功パターン・失敗パターンを学習し、システムを自動的に改善する機能。

### 🔄 Loop
**Loop 3（学習・進化ループ）** - 6時間ごと、または50エラー蓄積時

### ⚡ トリガー
- 6時間経過
- 50件のエラー蓄積
- 手動実行

### 📁 実装ファイル
- `agents/self_evolution_agent.py`
- `agents/self_healing/self_learning_pipeline.py`

### 💻 使い方

#### 自動実行
トリガー条件を満たすと自動的に実行される

#### 手動実行（開発時のみ）
```python
from agents.complete_engine_ultimate import CompleteEngineUltimate

engine = CompleteEngineUltimate()

# 自己進化の実行
if hasattr(engine, 'self_evolution'):
    # 成功パターン学習
    engine.self_evolution.learn_from_success(
        task_id="6_example_01",
        quality_score=85
    )
    
    # パフォーマンス最適化
    engine.self_evolution.optimize_performance()
```

### ⚠️ 注意点
1. **学習頻度**: 過度な学習は逆効果
2. **データ量**: 十分なデータがないと学習効果が低い
3. **時間**: 学習処理には時間がかかる（数分〜数十分）
4. **ナレッジ品質**: 低品質タスクからの学習は避ける

### ✨ 特徴
- ✅ 成功パターン、失敗パターン、修正レシピの3種学習
- ✅ 品質スコア月間+0.5向上が目標
- ✅ A/Bテスト自動実施
- ✅ 戦略の自動最適化

### 📊 出力先
- `knowledge.db`（学習済みパターン）
- `context_log`シート（学習履歴）

---

## F9: 人間連携機能

### 📌 概要
不明点の質問、重要イベントの報告、人間の指示受付を行う機能。

### 🔄 Loop
**全Loop** - 全ループで必要時に起動

### ⚡ トリガー
- 不明点検出時
- エラー3回連続失敗時（F7で修復不可）
- 重要イベント発生時
- 定期進捗報告（1時間ごと）

### 📁 実装ファイル
- `agents/human_collaboration_agent.py`

### 💻 使い方

#### 自動通知
システムが自動的に判断して通知（手動操作不要）

#### 通知確認方法
```bash
# ログファイル確認
tail -f logs/autonomous_*.log

# Google Sheets確認
# task_execution_logシートのerror_message列

# ダッシュボード確認
python3 agents/observability/dashboard.py
```

#### 手動で質問
```python
from agents.complete_engine_ultimate import CompleteEngineUltimate

engine = CompleteEngineUltimate()

if hasattr(engine, 'human_collaboration'):
    # 質問の送信
    engine.human_collaboration.request_feedback(
        topic="タスク優先度の確認",
        question="タスクAとBのどちらを優先すべきですか？"
    )
```

### ⚠️ 注意点
1. **通知頻度**: 過度な通知は避ける
2. **応答待ち**: 人間の応答を待つ場合、システムが一時停止
3. **GitHub Issues**: Issues経由の指示も可能（設定が必要）

### ✨ 特徴
- ✅ 能動的な質問生成
- ✅ 複数チャネル通知（Sheets、ログ、ダッシュボード）
- ✅ 進捗報告の自動生成
- ✅ 人間の指示受付（stop/resume）

### �� 出力先
- `logs/autonomous_*.log`
- `task_execution_log`シート
- GitHub Issues（オプション）

---

## F10: 定期健全性チェック

### 📌 概要
システムの健全性を定期的にチェックし、異常を早期発見する機能。

### 🔄 Loop
**独立実行** - 1時間ごと

### ⚡ トリガー
- 1時間ごと（cron設定）
- 手動実行

### 📁 実装ファイル
- `agents/health_check_agent.py`
- `sh/health_check_periodic.sh`

### 💻 使い方

#### 手動実行
```bash
# 健全性チェック実行
bash sh/health_check_periodic.sh
```

#### 定期実行設定（cron）
```bash
# crontab編集
crontab -e

# 1時間ごとに実行
0 * * * * cd /workspaces/gemini_AI_Agent && bash sh/health_check_periodic.sh >> logs/health_check.log 2>&1
```

#### Pythonから実行
```python
from agents.complete_engine_ultimate import CompleteEngineUltimate

engine = CompleteEngineUltimate()

if hasattr(engine, 'health_check'):
    status = engine.health_check.check_system_health()
    print(status)
```

### ⚠️ 注意点
1. **チェック項目**: ファイル、API接続、エージェントの3項目
2. **ログ蓄積**: ログファイルが増え続けるので定期削除
3. **通知**: 異常検出時は必ず確認する

### ✨ 特徴
- ✅ コアファイルの存在確認
- ✅ Google Sheets接続確認
- ✅ ナレッジシステム確認
- ✅ F7-F9エージェント確認
- ✅ 異常時の自動通知

### 📊 出力先
- `logs/health_check_*.log`

---

## 統合運用

### 🚀 テストスクリプトの使い分け

#### 3サイクルテスト（短期確認）
```bash
# 目的: 動作確認
# 時間: 約30-45分
# 用途: 機能追加後、修正後の確認
bash sh/test_autonomous_3cycles.sh
```

#### 24時間稼働テスト（長期耐久）
```bash
# 目的: 24時間自律稼働
# 時間: 24時間
# 用途: 本番運用、耐久テスト
bash sh/run_autonomous_24h_v2.sh
```

### 📊 推奨運用フロー
```
1. 初期設定
   ↓
   F1: ゴール分解（手動、1回のみ）
   
2. 開発サイクル
   ↓
   F2: タスク実行（3分ごと、または手動）
   → F3: 品質評価（自動）
   → F4: ナレッジ蓄積（自動）
   
3. 監視
   ↓
   F5: 進捗確認（1時間ごと）
   F10: 健全性チェック（1時間ごと）
   
4. エラー時
   ↓
   F7: 自己修復（最大3回、自動）
   → 失敗時 → F9: 人間通知
   
5. 学習・改善
   ↓
   F8: 自己進化（6時間ごと、自動）
   → ナレッジ更新 → 次回のF2で活用
```

### 🛡️ 安全運用のポイント

1. **バックアップ**: 定期的にGoogle Sheetsをバックアップ
2. **ログ確認**: 毎日ログファイルを確認
3. **API使用量**: Claudeの使用量を監視
4. **人間確認**: 重要な変更前に人間が確認
5. **テスト**: 大きな変更後は必ず3サイクルテスト

### 🔧 トラブルシューティング

#### F4エラー: AttributeError
```bash
# 原因: knowledge_manager.pyのメソッド不一致
# 解決済み: insert_knowledge()に辞書形式で渡す
```

#### F5エラー: read_sheet not found
```bash
# 原因: GoogleSheetsManagerのメソッド名が異なる
# 対処: 正しいメソッド名を使用（get_sheet_data等）
```

#### API制限エラー
```bash
# 対処: --limit オプションでタスク数を制限
bash start_pending_tasks.sh --limit 1
```

---

## 📚 参考資料

- ロードマップ: `MD/*_MASTER_ROADMAP_*.md`
- 連携フロー図: `MD/*_F1-F10連携フロー図.md`
- テスト結果: `logs/`ディレクトリ
- ナレッジDB: `knowledge_system/database/knowledge.db`

---

**最終更新**: $(TZ=Asia/Tokyo date +"%Y-%m-%d %H:%M:%S JST")

GUIDE

echo "✅ F1-F10完全ガイド作成: MD/${NOW_JST}_F1-F10完全ガイド.md"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ガイド作成完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📄 作成ファイル: MD/${NOW_JST}_F1-F10完全ガイド.md"
echo ""
echo "📖 確認コマンド:"
echo "  cat MD/${NOW_JST}_F1-F10完全ガイド.md"
echo ""

