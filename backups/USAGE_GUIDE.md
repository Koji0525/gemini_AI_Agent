# 🎯 完全統合システム 使い方ガイド

## 📋 基本的な使い方

### 1. タスクの実行
```bash
# pendingタスクを実行
python3 agents/task_execution/real_executor.py
```

**実行されること:**
- ✅ pendingタスクを検索
- ✅ タスク内容に基づいて実行
- ✅ agent_outputs/にファイル保存
- ✅ task_execution_logシートに記録
- ✅ pm_tasksのステータスをcompletedに更新
- ✅ ナレッジベースに蓄積

### 2. オブザーバビリティ（進捗確認）
```bash
# リアルタイムダッシュボード表示
python3 agents/observability/dashboard.py
```

**表示される情報:**
- 📊 ゴール進捗（%）
- 📋 タスク一覧とステータス
- ⭐ 品質スコア
- 📂 最近の出力ファイル
- 🎯 次のアクション

### 3. 人間との対話

#### 方法1: human_feedbackシートを使う

1. スプレッドシートで`human_feedback`シートを開く
2. システムからの質問を確認（question列）
3. response列（E列）に回答を記入
4. システムが自動的に読み取り

#### 方法2: コマンドラインから
```bash
# 対話エージェントのテスト
python3 agents/human_interface/interactive_agent.py
```

### 4. 完全統合システムの起動
```bash
# 24時間連続稼働
nohup python3 scripts/orchestrator_v55_ultimate.py > logs/system.log 2>&1 &

# ログ確認
tail -f logs/system.log
```

## 📂 ファイル構成
```
/workspaces/gemini_AI_Agent/
├── agent_outputs/           # タスク実行結果
│   └── {task_id}_{timestamp}.txt
├── logs/                    # システムログ
│   └── orchestrator_v55.log
├── agents/
│   ├── task_execution/      # タスク実行エンジン
│   ├── observability/       # ダッシュボード
│   └── human_interface/     # 対話機能
└── scripts/
    └── orchestrator_v55_ultimate.py  # メインシステム
```

## 🔍 トラブルシューティング

### Q: タスクが実行されない
```bash
# pendingタスクの確認
python3 -c "
from tools.base_data_accessor import BaseDataAccessor
accessor = BaseDataAccessor()
pending = accessor.read_sheet_as_dicts('pm_tasks', filter_func=lambda t: t.get('status', '').lower() == 'pending')
print(f'pending: {len(pending)}件')
"
```

### Q: ステータスが更新されない
```bash
# 手動で実行エンジンを起動
python3 agents/task_execution/real_executor.py
```

### Q: ダッシュボードが表示されない
```bash
# 依存パッケージの確認
pip install -r requirements.txt

# ダッシュボード単独実行
python3 agents/observability/dashboard.py
```

## 📊 スプレッドシート構成

### pm_tasksシート
- タスク一覧
- ステータス管理（pending/completed）
- 依存関係

### task_execution_logシート
- 実行履歴
- 品質スコア
- 出力ファイルパス

### human_feedbackシート
- システムからの質問
- 人間の回答
- 対話履歴

## �� 推奨ワークフロー

1. **朝**: ダッシュボードで進捗確認
2. **日中**: pendingタスクを実行
3. **夕方**: 品質レビュー
4. **夜**: 24時間稼働システム起動

## 💡 ヒント

- **並列実行**: 複数のタスクを同時実行可能
- **品質向上**: スコア7未満は再実行推奨
- **ナレッジ活用**: 類似タスクの参照で効率化
- **人間の介入**: 重要な判断は質問が来る

## 📞 サポート

問題が発生した場合:
1. logs/orchestrator_v55.logを確認
2. エラーメッセージを記録
3. 該当するステップを再実行
