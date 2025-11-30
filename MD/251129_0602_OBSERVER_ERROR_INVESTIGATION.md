# オブザーバー起動失敗 - 調査レポート

## エラー内容
```
FileNotFoundError: [Errno 2] No such file or directory: 
'archived_orchestrators_20251125_112234/scripts/integrated_orchestrator_latest.py'
```

## 問題箇所

- ファイル: `scripts/analysis/dependency_mapper.py`
- 行: 115 (`'file_size': file_path.stat().st_size`)

## 調査結果

### 1. エラーパスの特徴
- 相対パス（カレントディレクトリ基準）
- アーカイブディレクトリ（11/25作成）
- 現在は存在しない

### 2. dependency_mapper.pyの動作
- 全Pythonファイルを再帰的に走査
- 存在しないファイルへのリンク/参照を検出
- stat()呼び出し時にエラー

### 3. 根本原因（推定）
- .gitignoreで除外されたディレクトリ
- または削除されたディレクトリへの参照が残存
- dependency_mapper.pyに例外処理不足

## 修正方針

### オプションA: dependency_mapper.py修正（推奨）
- stat()呼び出しに例外処理追加
- 存在しないファイルはスキップ
- **既存システムに影響なし**

### オプションB: アーカイブディレクトリ削除
- archived_orchestrators_*を完全削除
- **他システムへの影響を要確認**

### オプションC: 除外パターン追加
- dependency_mapper.pyに除外パターン追加
- archived_*をスキップ
- **最小限の変更**

## 推奨アクション

1. オプションA実装（安全）
2. 動作確認
3. 問題なければオプションBで掃除

---

**作成日**: 2025-11-28
**優先度**: High
**影響範囲**: オブザーバーシステムのみ
