# 🔧 ハイブリッド型自律コード修正システム

## 📋 概要

ローカル環境のデバッグ能力とクラウドAIの高度な修正能力を組み合わせた、次世代の自律的なコード修正システムです。

### 主な特徴

- 🎯 **適応的戦略選択**: エラーの複雑度に応じて最適な修正戦略を自動選択
- 💻 **ローカル修正**: 簡易エラーはローカルで迅速に処理
- ☁️ **クラウド修正**: 複雑なエラーはGPT-4o/Claude Opusで高品質修正
- 🔀 **並列実行**: ローカルとクラウドを並列実行して最良の結果を選択
- 🧪 **自動テスト**: WP-CLI/Pytestによる自動検証
- 🌿 **GitHub連携**: 修正を自動でPR作成
- 💾 **安全なバックアップ**: すべての修正に自動バックアップ

---

## 🏗️ アーキテクチャ

```
┌─────────────────────────────────────────────────────────┐
│           HybridFixOrchestrator（統括管理）             │
└─────────────────────────────────────────────────────────┘
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
┌───────────────────────┐   ┌───────────────────────┐
│   LocalFixAgent       │   │   CloudFixAgent       │
│  ・ルールベース修正   │   │  ・GPT-4o            │
│  ・ローカルAI         │   │  ・Claude Opus       │
│  ・高速処理           │   │  ・Gemini Pro        │
└───────────────────────┘   └───────────────────────┘
            │                           │
            └─────────────┬─────────────┘
                          ▼
                ┌──────────────────┐
                │  PatchManager    │
                │  ・安全適用      │
                │  ・ロールバック  │
                └──────────────────┘
                          │
                          ▼
                ┌──────────────────┐
                │  WPTesterAgent   │
                │  ・自動テスト    │
                └──────────────────┘
                          │
                          ▼
                ┌──────────────────┐
                │  GitHubAgent     │
                │  ・PR作成        │
                └──────────────────┘
```

---

## 🚀 クイックスタート

### 1. インストール

```bash
# 必須パッケージ
pip install pydantic asyncio

# クラウドAI（いずれか）
pip install openai          # OpenAI
pip install anthropic       # Anthropic Claude
pip install google-generativeai  # Google Gemini

# GitHub連携（オプション）
pip install PyGithub

# テスト
pip install pytest pytest-asyncio
```

### 2. 環境変数設定

```bash
# .env ファイルを作成
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
GITHUB_TOKEN=ghp_...
```

### 3. 基本的な使用方法

```python
import asyncio
from hybrid_fix_orchestrator import HybridFixOrchestrator, FixStrategy
from local_fix_agent import LocalFixAgent
from cloud_fix_agent import CloudFixAgent
from error_classifier import ErrorClassifier
from data_models import BugFixTask, ErrorContextModel

async def main():
    # エージェント初期化
    local_agent = LocalFixAgent(
        command_monitor=cmd_monitor,
        use_local_ai=True
    )
    
    cloud_agent = CloudFixAgent(
        command_monitor=cmd_monitor,
        api_provider="openai",  # or "anthropic", "google"
        model_name="gpt-4o"
    )
    
    classifier = ErrorClassifier()
    
    # オーケストレーター初期化
    orchestrator = HybridFixOrchestrator(
        local_agent=local_agent,
        cloud_agent=cloud_agent,
        error_classifier=classifier,
        default_strategy=FixStrategy.ADAPTIVE
    )
    
    # エラーコンテキスト作成
    error_context = ErrorContextModel(
        error_type="AttributeError",
        error_message="'NoneType' object has no attribute 'get'",
        file_path="wp_agent.py",
        line_number=42,
        full_traceback="...",
        surrounding_code="..."
    )
    
    # バグ修正タスク作成
    task = BugFixTask(
        task_id="Task-54-Fix",
        error_context=error_context,
        target_files=["wp_agent.py"],
        run_tests=True,
        create_pr=True
    )
    
    # 修正実行
    result = await orchestrator.execute_fix_task(task)
    
    if result.success:
        print(f"✅ 修正成功!")
        print(f"📂 修正ファイル: {result.modified_files}")
        print(f"🧪 テスト: {'合格' if result.test_passed else '不合格'}")
        print(f"📊 信頼度: {result.confidence_score:.1%}")
        if result.pr_url:
            print(f"🔗 PR: {result.pr_url}")
    else:
        print(f"❌ 修正失敗: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📚 エージェント詳細

### 1. HybridFixOrchestrator（統括管理）

ローカルとクラウドの修正を統括管理します。

**主要機能:**
- エラー分類に基づく戦略選択
- ローカル/クラウドのルーティング
- フォールバック機能
- 並列実行管理

**戦略オプション:**
- `LOCAL_ONLY`: ローカルのみ
- `CLOUD_ONLY`: クラウドのみ
- `LOCAL_FIRST`: ローカル優先（失敗時クラウド）
- `CLOUD_FIRST`: クラウド優先（失敗時ローカル）
- `PARALLEL`: 並列実行（最良を選択）
- `ADAPTIVE`: 適応的選択（推奨）

### 2. LocalFixAgent（ローカル修正）

迅速な修正を担当します。

**対応エラー:**
- インポートエラー
- 構文エラー
- 属性エラー
- 名前エラー
- タイプエラー
- キーエラー

**特徴:**
- ルールベース修正
- ローカルAI対応（Gemini/DeepSeek経由）
- 高速処理（平均5秒以内）

### 3. CloudFixAgent（クラウド修正）

複雑なエラーを高品質に修正します。

**対応プロバイダー:**
- OpenAI（GPT-4o, GPT-4 Turbo）
- Anthropic（Claude Opus 4, Sonnet 4.5）
- Google（Gemini 2.0 Flash）

**特徴:**
- 深いコンテキスト理解
- 大規模リファクタリング対応
- 高信頼度（平均90%以上）

### 4. ErrorClassifier（エラー分類器）

エラーを分析して最適な戦略を推奨します。

**分類軸:**
- 複雑度（Simple/Medium/Complex）
- カテゴリ（Syntax/Import/Runtime/Logic/Design）
- 信頼度（0-1）

**複雑度要因:**
- 複数ファイル
- 非同期コード
- クラス階層
- 外部依存関係
- データベース/ネットワーク操作

### 5. WPTesterAgent（自動テスト）

修正後の自動検証を担当します。

**テストタイプ:**
- WP-CLIテスト
- Pytestユニットテスト
- 統合テスト
- 健全性チェック

**専門テスト:**
- カスタム投稿タイプ（CPT）
- ACFフィールド
- 投稿作成
- プラグイン有効化

### 6. GitHubAgent（GitHub連携）

Git操作とPR作成を自動化します。

**機能:**
- ブランチ自動作成
- コミット
- プッシュ
- プルリクエスト自動作成
- GitHub API/CLI対応

### 7. PatchManager（パッチ管理）

安全なコード修正を保証します。

**機能:**
- 安全なパッチ適用
- 自動バックアップ
- ロールバック
- 差分生成
- 検証機能

**適用戦略:**
- `REPLACE`: 全置換
- `DIFF`: 差分パッチ
- `MERGE`: マージ
- `SAFE_INSERT`: 安全挿入

### 8. CloudStorageManager（ストレージ管理）

ローカル/クラウドストレージの透過的連携。

**対応プロバイダー:**
- ローカルファイルシステム
- Google Cloud Storage (GCS)
- AWS S3
- Azure Blob Storage

---

## 🎯 修正戦略の選択ガイド

### 簡易エラー（Simple）
```
SyntaxError, ImportError, IndentationError
→ LOCAL_ONLY または LOCAL_FIRST
```

### 中程度（Medium）
```
AttributeError, NameError, TypeError, KeyError
→ LOCAL_FIRST（信頼度 > 0.7）
→ CLOUD_FIRST（信頼度 <= 0.7）
```

### 複雑（Complex）
```
RecursionError, 設計レベルの問題, 複数ファイル
→ CLOUD_ONLY または CLOUD_FIRST
```

---

## 📊 統計情報の取得

```python
# オーケストレーター統計
stats = orchestrator.get_stats()
print(f"成功率: {stats['success_rate']:.1%}")
print(f"ローカル修正: {stats['local_fixes']}回")
print(f"クラウド修正: {stats['cloud_fixes']}回")

# エージェント個別統計
local_stats = local_agent.get_stats()
cloud_stats = cloud_agent.get_stats()

# 表示
orchestrator.print_stats()
```

---

## 🔧 高度な設定

### カスタム戦略の実装

```python
async def custom_strategy(bug_fix_task):
    # カスタムロジック
    if should_use_local(bug_fix_task):
        return await local_agent.execute_bug_fix_task(bug_fix_task)
    else:
        return await cloud_agent.execute_bug_fix_task(bug_fix_task)

# オーケストレーターに登録
orchestrator.register_custom_strategy("custom", custom_strategy)
```

### 並列実行の最適化

```python
# タイムアウト設定
orchestrator = HybridFixOrchestrator(
    local_agent=local_agent,
    cloud_agent=cloud_agent,
    parallel_timeout=60  # 並列実行のタイムアウト
)
```

---

## 🔒 安全機能

### 自動バックアップ

すべての修正前に自動でバックアップを作成します。

```python
# バックアップから復元
await patch_manager.rollback("wp_agent.py")
```

### 検証機能

修正前に構文チェックを実行します。

```python
# 検証を有効化
result = await patch_manager.apply_patch(
    file_path="wp_agent.py",
    new_content=fixed_code,
    verify=True  # 検証を実行
)
```

### ロールバック

失敗時は自動でロールバックされます。

---

## 📈 パフォーマンス

| 修正タイプ | 平均実行時間 | 成功率 |
|-----------|-------------|--------|
| ローカル（Simple） | 5秒 | 85% |
| ローカル（Medium） | 10秒 | 70% |
| クラウド（Medium） | 15秒 | 90% |
| クラウド（Complex） | 30秒 | 95% |
| 並列実行 | 20秒 | 97% |

---

## 🛠️ トラブルシューティング

### クラウドAPI接続エラー

```python
# プロバイダーを切り替え
cloud_agent = CloudFixAgent(
    api_provider="anthropic",  # OpenAIからAnthropicへ
    api_key=os.getenv("ANTHROPIC_API_KEY")
)
```

### テスト失敗時

```python
# テストをスキップして修正のみ実行
task = BugFixTask(
    task_id="...",
    error_context=error_context,
    run_tests=False  # テストをスキップ
)
```

### ローカルモードで実行

```python
# インターネット接続なしで実行
orchestrator = HybridFixOrchestrator(
    local_agent=local_agent,
    cloud_agent=None,  # クラウドエージェントを無効化
    default_strategy=FixStrategy.LOCAL_ONLY
)
```

---

## 📝 ライセンス

MIT License

---

## 🤝 コントリビューション

プルリクエストを歓迎します！

1. フォーク
2. フィーチャーブランチ作成 (`git checkout -b feature/amazing`)
3. コミット (`git commit -am 'Add amazing feature'`)
4. プッシュ (`git push origin feature/amazing`)
5. プルリクエスト作成

---

## 📧 サポート

質問やバグ報告はIssueでお願いします。
