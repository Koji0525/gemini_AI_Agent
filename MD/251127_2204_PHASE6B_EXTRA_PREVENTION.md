# Phase 6B-extra: ナレッジ消失再発防止策

## 実装項目（推定1時間）

### 1. ナレッジ自動エクスポート（30分）
```python
# tools/knowledge_exporter.py
class KnowledgeExporter:
    def export_to_json(self):
        """JSON形式でGit管理下にエクスポート"""
        # MD/knowledge_export/YYYYMMDD_knowledge.json
        
    def export_to_markdown(self):
        """重要ナレッジをMarkdownでエクスポート"""
        # MD/knowledge_export/YYYYMMDD_knowledge.md
```

### 2. 日次自動バックアップ（15分）
```bash
# sh/backup_knowledge_daily.sh
#!/bin/bash
# 毎日AM 2:00に実行
# 30日以上古いバックアップは自動削除
```

### 3. 復元手順文書化（15分）
- 今回の手順をMDに記録
- ワンコマンドで復元できるスクリプト作成

## 優先度
- Phase 6B完了後に実施
- または緊急性が高い場合は即実施
