---
name: 🤖 Bot制御コマンド
about: 24時間自律開発システムへの制御指示
title: '[BOT] '
labels: bot-control
assignees: ''
---

## 制御コマンド

以下のコマンドをコメントに入力してください：

### システム制御
- `@bot stop` - システムを停止
- `@bot resume` - システムを再開

### タスク管理
- `@bot priority-up <task_id>` - タスクの優先度アップ
- `@bot status` - 現在の進捗状況

### メンテナンス
- `@bot backup-now` - 即座にバックアップ
- `@bot logs <task_id>` - タスクのログ表示

### その他
- `@bot help` - ヘルプ表示

---

## 使用例
```
@bot status
```

または
```
@bot priority-up TASK-123
```
