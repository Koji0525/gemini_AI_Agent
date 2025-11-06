# 🚀 24時間自律開発システム 完全ガイド

**作成日**: 2025-11-06  
**バージョン**: v2.0  
**ステータス**: 本番稼働可能

---

## 📋 目次

1. [システム概要](#システム概要)
2. [アーキテクチャ](#アーキテクチャ)
3. [コンポーネント詳細](#コンポーネント詳細)
4. [使用方法](#使用方法)
5. [運用ガイド](#運用ガイド)
6. [トラブルシューティング](#トラブルシューティング)

---

## システム概要

### 🎯 目的
- **24時間連続稼働**: 人間の介入なしで自律的に開発を継続
- **継続的学習**: エラーから学習し、自動的に改善
- **品質保証**: タスク実行結果を自動評価し、低品質なものを再実行

### ✨ 主要機能
1. **自律タスク実行**: Google Sheetsからタスクを取得して自動実行
2. **品質フィードバック**: 実行結果を評価し、7点未満は自動リトライ
3. **継続的学習**: エラーログからパターンを抽出し、ナレッジベースに蓄積
4. **自動修復**: 過去の成功事例を活用して問題を自動解決

### 📊 実績
- **稼働実績**: 5分間テストで10タスク実行成功
- **ナレッジベース**: 160件蓄積
- **エラー率**: 0%
- **学習サイクル**: 30秒毎に自動実行

---

## アーキテクチャ

### 🏗️ 全体構成
```
┌─────────────────────────────────────────────────────────┐
│         AutonomousDevelopmentOrchestrator              │
│         (24時間自律開発統合オーケストレータ)              │
└────────────┬────────────────────────────┬──────────────┘
             │                            │
    ┌────────▼────────┐          ┌───────▼────────┐
    │   Loop 1        │          │   Loop 2       │
    │  学習・修復      │          │  タスク実行     │
    │  (30秒毎)       │          │  (3分毎)       │
    └────────┬────────┘          └───────┬────────┘
             │                            │
    ┌────────▼────────────┐      ┌───────▼─────────────┐
    │ SelfLearningPipeline│      │ QualityFeedbackLoop │
    │  - ログ収集          │      │  - タスク実行        │
    │  - パターン抽出      │      │  - 品質評価          │
    │  - ナレッジ更新      │      │  - 自動リトライ      │
    │  - 修正戦略生成      │      │                     │
    └─────────────────────┘      └─────────────────────┘
```

### �� 2つのループ

#### Loop 1: 学習・修復ループ（30秒毎）
1. **ログ収集**: 過去のエラーログを収集
2. **パターン抽出**: 共通するエラーパターンを抽出
3. **ナレッジ更新**: 解決策をナレッジベースに登録
4. **修正適用**: 必要に応じて自動修正を適用

#### Loop 2: タスク実行ループ（3分毎）
1. **タスク取得**: Google Sheetsから pending タスクを取得
2. **ナレッジ検索**: 関連する過去のナレッジを検索
3. **タスク実行**: ナレッジを活用してタスクを実行
4. **品質評価**: ReviewAgentが4基準で評価
5. **フィードバック**: 7点未満なら改善して再実行（最大3回）
6. **結果記録**: Google Sheetsに実行結果を記録

---

## コンポーネント詳細

### 1️⃣ TaskExecutor
**役割**: タスク実行エンジン  
**場所**: `task_executor/task_executor_main.py`

**主要機能**:
- pending タスクの取得
- RAGエンジンによるナレッジ検索（過去の成功事例を活用）
- タスク実行
- 実行結果の記録

**技術**:
- FrugalRAGEngine: ローカルベクトル検索（高速・低コスト）
- Sentence Transformers: セマンティック検索

### 2️⃣ ReviewAgent
**役割**: 品質評価エージェント  
**場所**: `core_agents/review_agent.py`

**評価基準**（4項目）:
1. **完成度** (30%): タスクが完全に完了しているか
2. **正確性** (30%): エラーや警告がないか
3. **効率性** (20%): 実行時間が適切か
4. **保守性** (20%): ログやエラーハンドリングがあるか

**スコアリング**:
- 9-10点: 優秀
- 7-8点: 良好
- 1-6点: 改善必要（自動リトライ）

### 3️⃣ QualityFeedbackLoop
**役割**: 品質フィードバックループ  
**場所**: `core_agents/review_agent.py`

**プロセス**:
1. タスク実行
2. 品質評価
3. 7点以上 → 完了
4. 7点未満 → 改善策適用 → 再実行（最大3回）

**改善策**:
- 完成度低 → 優先度を high に設定
- 正確性低 → 厳格なバリデーション適用

### 4️⃣ SelfLearningPipeline
**役割**: 継続的学習エンジン  
**場所**: `agents/self_healing/self_learning_pipeline.py`

**学習サイクル**:
1. ログ収集（LogIntegrator）
2. パターン抽出（PatternExtractor）
3. ナレッジ更新（KnowledgeBaseManager）
4. 修正戦略生成（DecisionSupportSystem）

### 5️⃣ KnowledgeSync
**役割**: ナレッジベース同期  
**場所**: `tools/knowledge_sync.py`

**機能**:
- 起動時に自動同期
- 複数ファイルの統合
- 統計情報のキャッシュ

---

## 使用方法

### 🚀 起動方法

#### 1. 通常起動（Ctrl+Cで停止可能）
```bash
python3 autonomous_development_orchestrator.py
```

#### 2. バックグラウンド起動（24時間連続稼働）
```bash
nohup python3 autonomous_development_orchestrator.py \
    > logs/orchestrator_$(date +%Y%m%d_%H%M%S).log 2>&1 &

# プロセス確認
ps aux | grep autonomous_development_orchestrator
```

#### 3. テスト起動（5分間）
```bash
timeout 300 python3 autonomous_development_orchestrator.py
```

### 📊 ログ確認

#### リアルタイムログ
```bash
tail -f logs/orchestrator_*.log
```

#### ログ分析
```bash
# エラー確認
grep -i "error\|exception" logs/orchestrator_*.log

# 成功数カウント
grep -i "✅" logs/orchestrator_*.log | wc -l

# 学習サイクル確認
grep "学習サイクル" logs/orchestrator_*.log
```

### 🛑 停止方法

#### フォアグラウンド実行の場合
```bash
Ctrl + C
```

#### バックグラウンド実行の場合
```bash
# プロセスID確認
ps aux | grep autonomous_development_orchestrator

# 停止
kill -SIGINT <PID>
```

---

## 運用ガイド

### 📈 監視項目

#### 1. 稼働状況（5分毎に自動出力）
- 稼働時間
- 学習サイクル実行回数
- タスクサイクル実行回数
- 実行タスク数
- 品質レビュー数
- 品質リトライ数
- 修正適用数

#### 2. ナレッジベース統計
```bash
python3 tools/knowledge_sync.py
```

出力例:
```
📊 ナレッジベース同期完了
====================================
�� 総ナレッジ数: 160件
📁 同期ファイル数: 2個
====================================
```

### 🔧 メンテナンス

#### 週次メンテナンス
1. **ログローテーション**
```bash
# 1週間以上前のログを圧縮
find logs/ -name "*.log" -mtime +7 -exec gzip {} \;
```

2. **ナレッジベースバックアップ**
```bash
cp -r mvp_v4/knowledge/learned/ \
   _BACKUP/knowledge_$(date +%Y%m%d)/
```

#### 月次メンテナンス
1. **統計レポート生成**
```bash
python3 << 'EOF'
import json
from datetime import datetime, timedelta

# ナレッジ統計
knowledge_files = [
    'mvp_v4/knowledge/learned/conversation_knowledge_v3.json',
    'mvp_v4/knowledge/learned/conversation_knowledge_v4.json'
]

total = 0
for file in knowledge_files:
    with open(file) as f:
        data = json.load(f)
        count = len(data) if isinstance(data, list) else len(data.get('knowledge_base', []))
        total += count
        print(f"{file}: {count}件")

print(f"総計: {total}件")
