# Deprecated Files - 2025-11-10

## pm_agent.py

### 移動理由
- 誰にも使われていない古い実装（642行）
- 全てのインポートは `core_agents.pm_agent` を使用
- 新しい実装: `core_agents/pm_agent.py` (235行)

### 移動日
2025-11-10

### 差分情報
- 旧実装: 642行
- 新実装: 235行
- 差分: 840行

### 復元方法
必要な場合は以下のコマンドで復元可能:
```bash
cp backups/deprecated/20251110/pm_agent.py ./pm_agent.py
```

### 関連情報
- インポート状況: 全ファイルが `core_agents.pm_agent` を使用
- テスト状況: 全テスト成功（76/76件）
- スコア: 84.3/100
