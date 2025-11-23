# 📋 Phase 2実装計画: 高度な分析機能

**作成日時**: 2025-11-23 08:50 JST  
**前提**: Phase 1完了（依存関係分析基盤構築済み）  
**目標**: 静的解析では検出できない依存関係の可視化  
**期間**: 2-3日

---

## 🎯 Phase 2の目的

Phase 1で構築した基盤を拡張し、以下の「見えない依存関係」を可視化:

1. **環境変数依存** - `os.getenv()`, `os.environ`
2. **ファイルI/O依存** - `open()`, `Path.read_text()`
3. **外部コマンド依存** - `subprocess.run()`, `os.system()`
4. **データベース依存** - SQLクエリ、接続先
5. **ネットワーク依存** - API呼び出し、URL

これらは通常のインポート解析では検出できないため、AST解析を拡張する必要があります。

---

## 📊 Phase 2タスク分解

### Task 2-1: 隠れた依存関係検出エンジン (1日)

**目標**: 環境変数、ファイルI/O、外部コマンドの使用を検出

**実装ファイル**:
```
scripts/analysis/hidden_dependency_detector.py
```

**機能**:
- AST Visitor拡張
- 環境変数アクセスの検出（`os.getenv`, `os.environ`）
- ファイル操作の検出（`open`, `Path`メソッド）
- 外部コマンド実行の検出（`subprocess`, `os.system`）

**出力**:
```json
{
  "file": "tools/config_loader.py",
  "hidden_dependencies": {
    "env_vars": ["GOOGLE_SHEETS_CREDENTIALS", "CLAUDE_API_KEY"],
    "files": ["config.json", ".env"],
    "commands": ["git log", "python --version"]
  }
}
```

**検証方法**:
```bash
python3 scripts/analysis/hidden_dependency_detector.py
# 期待: 50+ファイルで環境変数依存を検出
```

---

### Task 2-2: 循環依存検出 (半日)

**目標**: モジュール間の循環参照を自動検出

**実装ファイル**:
```
scripts/analysis/cycle_detector.py
```

**アルゴリズム**:
1. 依存関係グラフから有向グラフを構築
2. DFS（深さ優先探索）で閉路を検出
3. 検出された循環依存パスを報告

**出力**:
```json
{
  "cycles": [
    {
      "path": ["agents/pm_agent.py", "tools/sheets_manager.py", "agents/pm_agent.py"],
      "severity": "medium",
      "recommendation": "sheets_managerの一部機能を独立モジュールに分離"
    }
  ]
}
```

**検証方法**:
```bash
python3 scripts/analysis/cycle_detector.py
# 期待: 既知の循環依存が検出される
```

---

### Task 2-3: 破壊的変更検知 (1日)

**目標**: API変更、関数シグネチャ変更を自動検出

**実装ファイル**:
```
scripts/analysis/breaking_change_detector.py
```

**機能**:
- Git diff解析
- 関数シグネチャ変更検出
- 削除されたメソッド検出
- 変更影響範囲の自動計算

**出力**:
```json
{
  "file": "tools/sheets_manager.py",
  "changes": [
    {
      "type": "signature_change",
      "function": "get_sheet_data",
      "old": "def get_sheet_data(sheet_name)",
      "new": "def get_sheet_data(sheet_name, range_name=None)",
      "impact": "high",
      "affected_files": 257
    }
  ]
}
```

---

### Task 2-4: APIエンドポイント追加 (半日)

**拡張エンドポイント**:
```
GET /api/hidden-dependencies       - 隠れた依存関係一覧
GET /api/cycles                    - 循環依存一覧
GET /api/breaking-changes          - 破壊的変更検知結果
GET /api/risk-score/{file_path}    - ファイルのリスクスコア
```

---

### Task 2-5: ダッシュボード拡張 (半日)

**追加UI要素**:
- 🔴 隠れた依存関係パネル
- 🔄 循環依存警告表示
- ⚠️ 破壊的変更アラート
- 📊 リスクスコアヒートマップ

---

## 🎯 Phase 2成功基準

| 指標 | 目標 | 測定方法 |
|------|------|----------|
| 環境変数検出率 | 95%+ | 手動検証 |
| 循環依存検出 | 全て検出 | 既知ケースでテスト |
| 破壊的変更検出 | 90%+ | Git履歴でテスト |
| API応答時間 | <200ms | 各エンドポイント |

---

## 📅 実装スケジュール

### Day 1 (3h)
- ✅ hidden_dependency_detector.py実装
- ✅ 環境変数検出テスト
- ✅ ファイルI/O検出テスト

### Day 2 (3h)
- ✅ cycle_detector.py実装
- ✅ breaking_change_detector.py実装
- ✅ Git diff解析ロジック

### Day 3 (2h)
- ✅ APIエンドポイント追加
- ✅ ダッシュボードUI拡張
- ✅ 統合テスト

---

## 🚨 リスク管理

### リスク1: AST解析の限界
**内容**: 動的コード実行は解析不可
**対策**: 検出できない旨を明示的に表示

### リスク2: Git履歴の大きさ
**内容**: 大量のコミットで解析が遅延
**対策**: 直近100コミットのみ解析

### リスク3: 既存システムへの影響
**対策**: 完全に独立したモジュールとして実装

---

## 🔜 Phase 3プレビュー

Phase 2完了後は以下に進みます:
- CI/CD統合
- Git hook自動実行
- Slack通知連携
- 継続的監視機能

---

**次のコマンド**: Phase 2実装開始
```bash
python3 scripts/analysis/hidden_dependency_detector.py
```
