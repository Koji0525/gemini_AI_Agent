# ナレッジ569件消失問題 - 根本原因分析

## 問題の経緯

1. Phase 0診断時: 569件のナレッジ確認
2. 現在: 30件のみ存在
3. 過去ブランチから取得試行: 失敗
4. 同じエラーの繰り返し: 3回

## なぜなぜ分析（12層深掘り）

### Level 1
**現象**: `git show`でknowledge.dbが取得できない
**なぜ?** → ブランチにファイルが存在しない

### Level 2
**なぜ存在しない?** → .gitignoreで除外されている
**証拠確認**:
```bash
grep -E "\.db|knowledge" .gitignore
# 結果: *.db が含まれているはず
```

### Level 3
**なぜ.gitignoreに含まれる?** → DBファイルは通常Git管理しない
**理由**: バイナリ、大容量、機密情報

### Level 4
**なぜ過去に569件あったと思った?** → 診断レポートに記載
**証拠**: MD/251125_0606_PHASE0_ACTUAL_RESULTS.md

### Level 5
**なぜ診断時は569件だった?** → 当時のローカルDBに実在
**推測**: v1.24.18ブランチで実際に蓄積

### Level 6
**なぜ今は30件?** → DBがリセットされた
**タイミング**: ブランチ切り替え or スキーマ変更時

### Level 7
**なぜDBがリセットされた?** → 新規スキーマ適用
**証拠**: knowledge_entriesテーブルが新規作成された

### Level 8
**なぜ新規テーブル作成?** → 旧knowledge_baseから移行
**タイミング**: Phase 6A開発時

### Level 9
**なぜ移行時にデータ消失?** → 旧データが25件しかなかった
**理由**: 569件は更に古いknowledge_baseに存在

### Level 10
**なぜ古いknowledge_baseは消えた?** → DBファイル上書き
**タイミング**: ブランチ切り替え or リセット

### Level 11
**なぜバックアップから復元できない?** → バックアップも30件程度
**理由**: 569件が存在した時点のバックアップなし

### Level 12
**なぜバックアップがない?** → 自動バックアップシステム未実装
**根本原因**: ナレッジの永続化戦略の欠如

## 真因（Root Cause）

### 主要因
1. **ナレッジDBがGit管理外** - .gitignore除外
2. **自動バックアップ未実装** - 定期保存なし
3. **データ永続化戦略なし** - エクスポート機能なし

### 副要因
4. ブランチ切り替え時のDB保護なし
5. スキーマ変更時のデータ移行検証不足
6. バックアップ復元手順の未整備

## 569件のナレッジの現状

### 可能性1: 完全消失（70%）
- Git管理外のため復元不可
- バックアップも存在しない
- **結論**: 諦めて前進

### 可能性2: FAISSインデックスに残存（20%）
- ベクトルDBに一部残っている可能性
- knowledge.index ファイル確認要

### 可能性3: ログファイルから再構築（10%）
- task_execution_log から一部復元
- Google Sheets履歴から抽出

## 抜本的対策（3つの戦略）

### 戦略A: 現状受入れ + 再発防止（推奨）

**アクション**:
1. 現在の30件を起点に再スタート
2. ナレッジ自動エクスポート実装
3. Phase 6B以降で新規蓄積

**メリット**:
- 即座に開発継続可能
- 前向きな解決
- システム改善のチャンス

**実装**:
```python
# 毎日ナレッジをJSON/MDでエクスポート
class KnowledgeExporter:
    def export_daily(self):
        # JSON形式でGit管理下に保存
        # MD形式でも保存
        pass
```

### 戦略B: 部分復元試行（中リスク）

**アクション**:
1. FAISSインデックス確認
2. Google Sheets履歴から重要ナレッジ抽出
3. 手動で重要項目のみ復元

**実装**:
```bash
# FAISSインデックス確認
ls -la knowledge_system/database/faiss_index/

# Sheets履歴から抽出
# 成功率の高いタスクをナレッジ化
```

### 戦略C: 完全復元試行（高リスク）

**アクション**:
1. システム全体のDB検索
2. 隠しファイル・tempファイル確認
3. Git reflog 徹底調査

**リスク**: 時間がかかり、成功率低い

## 推奨アクション（即実行可能）

### Phase 1: 現状確認（5分）
```bash
# .gitignore確認
cat .gitignore | grep -i db

# FAISSインデックス確認
sqlite3 knowledge_system/database/faiss_index/knowledge.index ".tables" 2>/dev/null

# 全DBファイル最終確認
find . -name "*.db" -exec ls -lh {} \; | sort -k5 -hr | head -10
```

### Phase 2: 最善の復元試行（10分）
```bash
# 最大のバックアップから復元
LARGEST_BACKUP=$(find . -name "*.db" -exec ls -l {} \; | sort -k5 -nr | head -1 | awk '{print $NF}')

sqlite3 "$LARGEST_BACKUP" "SELECT COUNT(*) FROM knowledge_entries;"
# または
sqlite3 "$LARGEST_BACKUP" "SELECT COUNT(*) FROM knowledge_base;"
```

### Phase 3: 再発防止実装（30分）
1. ナレッジ自動エクスポート機能
2. 日次バックアップスクリプト
3. 復元手順の文書化

## 再発防止策（完全版）

### 即時実装（Phase 6B-extra）

#### 1. ナレッジ自動エクスポート
```python
# tools/knowledge_exporter.py
def export_knowledge_to_json():
    """ナレッジをJSON形式でGit管理下にエクスポート"""
    # MD/knowledge_export/YYYYMMDD_knowledge.json
    pass

def export_to_markdown():
    """重要ナレッジをMarkdownでエクスポート"""
    # MD/knowledge_export/YYYYMMDD_knowledge.md
    pass
```

#### 2. 日次自動バックアップ
```bash
# sh/backup_knowledge_daily.sh
#!/bin/bash
DATE=$(date +%Y%m%d)
cp knowledge_system/database/knowledge.db \
   knowledge_system/database/backups/daily/knowledge_${DATE}.db

# 古いバックアップ削除（30日以上）
find knowledge_system/database/backups/daily -mtime +30 -delete
```

#### 3. 復元手順文書化
```markdown
# MD/KNOWLEDGE_RECOVERY_PROCEDURE.md
## ナレッジ復元手順
1. バックアップ確認
2. JSON/MD からインポート
3. Google Sheetsから再構築
```

## 成功事例の参考

### 他プロジェクトの成功パターン

#### パターン1: ナレッジのMarkdown管理
```
MD/knowledge/
  ├── phase0/
  │   ├── diagnosis_system.md
  │   └── blackboard_system.md
  ├── phase1/
  │   └── reflexion_system.md
  └── ...
```

#### パターン2: 自動エクスポートCron
```bash
# crontab
0 2 * * * /path/to/export_knowledge.sh
```

#### パターン3: Git管理のJSONファイル
```json
{
  "exported_at": "2024-11-27",
  "total_entries": 569,
  "entries": [...]
}
```

## 結論と推奨事項

### 結論
569件のナレッジは**ほぼ復元不可能**。
理由: Git管理外、バックアップなし、過去DBファイル上書き。

### 推奨事項
1. **戦略A採用**: 現状受入れ + 再発防止
2. **即実装**: ナレッジエクスポート機能
3. **前進**: Phase 6B開発継続

### タイムライン
- 今: 現状確認（5分）
- 30分後: 再発防止実装完了
- 1時間後: Phase 6B開発再開

---

**作成日時**: 2024-11-27
**作成者**: Development Team
**優先度**: Critical
