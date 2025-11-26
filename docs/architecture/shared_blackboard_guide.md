# 共有黒板システム ガイド

## 概要

共有黒板（Shared Blackboard）は、複数のエージェントが構造化された情報を共有するための中央データストアです。

## アーキテクチャ

### 設計原則

1. **ファイルベース**: JSONファイルで永続化
2. **楽観的ロック**: 並行アクセス制御
3. **履歴管理**: 変更履歴を自動保存
4. **イベント駆動**: 変更通知システム

### データ構造
```json
{
  "meta": {
    "goal_id": "6",
    "version": 15,
    "last_updated": "2025-11-26T10:00:00"
  },
  "sections": {
    "data_collection": {...},
    "analysis": {...}
  }
}
```

## 使用方法

### 基本的な使い方
```python
from agents.integration.shared_blackboard_manager import SharedBlackboardManager

# インスタンス作成
blackboard = SharedBlackboardManager(goal_id="6")

# セクション書き込み
blackboard.write_section("data_collection", {
    "status": "completed",
    "quality_score": 85
})

# セクション読み取り
data = blackboard.read_section("data_collection")
```

### 楽観的ロック
```python
# 現在のバージョンを取得
version = blackboard.get_version()

# バージョン指定で書き込み
success = blackboard.write_section(
    "analysis",
    {"status": "in_progress"},
    expected_version=version
)

if not success:
    print("バージョン競合が発生しました")
```

### 変更通知
```python
def on_data_updated(section_name, data):
    print(f"{section_name} が更新されました")

# 購読
blackboard.subscribe_changes("data_collection", on_data_updated)
```

## パフォーマンス

- 読み取り: < 100ms
- 書き込み: < 500ms
- 履歴保存: 直近100件（自動削除）

## トラブルシューティング

### バージョン競合

楽観的ロックで競合が発生した場合、自動的に3回までリトライします。

### ファイルロックタイムアウト

5秒でタイムアウトします。長時間のロックが必要な場合は、処理を分割してください。

## 既存システムとの統合

既存システム（complete_engine_ultimate.py）は変更せず、新しいエージェントのみが共有黒板を使用します。

- 既存エージェント: Google Sheets経由で情報共有
- 新規エージェント: 共有黒板経由で情報共有

両方のシステムが並行して動作します。
