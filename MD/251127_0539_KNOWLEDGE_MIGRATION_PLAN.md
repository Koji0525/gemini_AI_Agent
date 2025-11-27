# ナレッジDB移行計画書

## 目的
過去ブランチ（v1.24.18-24h_task_251125）の569件のナレッジデータを、
現在のブランチ（v1.24.22-24h_F1-F2_improve_251127）に安全に移行する。

## 現状確認

### 現在のブランチ
- ブランチ: `v1.24.22-24h_F1-F2_improve_251127`
- ナレッジ件数: 約30件
- 開発状況: Phase 6B進行中（最新）

### 過去のブランチ
- ブランチ: `v1.24.18-24h_task_251125`
- ナレッジ件数: 569件
- 開発状況: Phase 0完了時点

## 移行戦略

### オプション1: SQLiteファイル直接移行（推奨）
**メリット**: 
- ブランチ切り替え不要
- 現在の作業に影響なし
- ロールバック容易

**手順**:
1. 現在のブランチで作業継続
2. 過去のDBファイルのみをGitから取得
3. データをマージ
4. 検証

### オプション2: ブランチ切り替え
**デメリット**:
- 作業中断
- コード競合のリスク
- 手間がかかる

**推奨**: オプション1を採用

## 詳細実施手順（オプション1）

### Phase 1: 安全確保（5分）

#### 1-1. 現在の状態を完全バックアップ
```bash
# 現在のブランチ確認
git branch --show-current

# 現在のDBバックアップ
BACKUP_TIME=$(date +%Y%m%d_%H%M%S)
mkdir -p knowledge_system/database/backups/pre_migration
cp knowledge_system/database/knowledge.db \
   knowledge_system/database/backups/pre_migration/knowledge_${BACKUP_TIME}.db

# 確認
ls -lh knowledge_system/database/backups/pre_migration/
sqlite3 knowledge_system/database/backups/pre_migration/knowledge_${BACKUP_TIME}.db \
  "SELECT COUNT(*) FROM knowledge_entries;"
```

**期待結果**: 30件（現在の件数）

#### 1-2. 過去ブランチのDBファイルパス確認
```bash
# 過去ブランチに存在するDBファイルを確認（ブランチ切り替えなし）
git show v1.24.18-24h_task_251125:knowledge_system/database/knowledge.db > /dev/null 2>&1
echo $?  # 0なら存在、128なら不在
```

### Phase 2: 過去DBファイル取得（5分）

#### 2-1. 過去ブランチのDBを一時ディレクトリに取得
```bash
# 一時ディレクトリ作成
mkdir -p /tmp/knowledge_migration

# 過去ブランチのDBファイルを取得（ブランチ切り替えなし）
git show v1.24.18-24h_task_251125:knowledge_system/database/knowledge.db \
  > /tmp/knowledge_migration/knowledge_569.db

# 検証
ls -lh /tmp/knowledge_migration/knowledge_569.db
sqlite3 /tmp/knowledge_migration/knowledge_569.db \
  "SELECT COUNT(*) FROM knowledge_entries;"
```

**期待結果**: 569件

#### 2-2. 過去DBのスキーマ確認
```bash
# テーブル構造確認
sqlite3 /tmp/knowledge_migration/knowledge_569.db << 'SQL'
.schema knowledge_entries
.schema knowledge_base
SELECT name FROM sqlite_master WHERE type='table';
SQL
```

**確認項目**:
- knowledge_entriesテーブルの存在
- カラム構造の互換性

### Phase 3: データマージ（10分）

#### 3-1. マージスクリプト作成
```python
# ファイル: /tmp/merge_knowledge.py
import sqlite3
import sys

def merge_knowledge_dbs(source_db, target_db):
    """
    ソースDBからターゲットDBへナレッジをマージ
    
    戦略:
    - 重複チェック（titleで判定）
    - 既存データは保持
    - 新規データのみ追加
    """
    source_conn = sqlite3.connect(source_db)
    target_conn = sqlite3.connect(target_db)
    
    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()
    
    # ソースデータ取得
    source_cursor.execute("""
        SELECT title, category, problem, solution, tags, created_at
        FROM knowledge_entries
        ORDER BY created_at
    """)
    
    source_entries = source_cursor.fetchall()
    
    print(f"ソースDB: {len(source_entries)}件")
    
    # ターゲットの既存タイトル取得
    target_cursor.execute("SELECT title FROM knowledge_entries")
    existing_titles = set(row[0] for row in target_cursor.fetchall())
    
    print(f"ターゲットDB（既存）: {len(existing_titles)}件")
    
    # マージ実行
    added = 0
    skipped = 0
    
    for entry in source_entries:
        title, category, problem, solution, tags, created_at = entry
        
        if title in existing_titles:
            skipped += 1
            continue
        
        try:
            target_cursor.execute("""
                INSERT INTO knowledge_entries 
                (title, category, problem, solution, tags, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, category, problem, solution, tags, created_at))
            
            added += 1
        except Exception as e:
            print(f"エラー: {title} - {e}")
    
    target_conn.commit()
    
    # 結果確認
    target_cursor.execute("SELECT COUNT(*) FROM knowledge_entries")
    final_count = target_cursor.fetchone()[0]
    
    print(f"\nマージ完了:")
    print(f"  追加: {added}件")
    print(f"  スキップ（重複）: {skipped}件")
    print(f"  最終件数: {final_count}件")
    
    source_conn.close()
    target_conn.close()
    
    return added, skipped, final_count

if __name__ == '__main__':
    source_db = '/tmp/knowledge_migration/knowledge_569.db'
    target_db = 'knowledge_system/database/knowledge.db'
    
    merge_knowledge_dbs(source_db, target_db)
```

#### 3-2. マージ実行（DRY RUN）
```bash
# まずはDRY RUN（実際のDBをコピーしてテスト）
cp knowledge_system/database/knowledge.db \
   /tmp/knowledge_migration/knowledge_test.db

# テストマージ実行
python3 /tmp/merge_knowledge.py  # ターゲットを/tmp/knowledge_test.dbに変更

# 結果確認
sqlite3 /tmp/knowledge_migration/knowledge_test.db \
  "SELECT COUNT(*) FROM knowledge_entries;"
```

**期待結果**: 約569件（重複を除く）

#### 3-3. 本番マージ実行
```bash
# DRY RUNが成功したら、本番実行
python3 /tmp/merge_knowledge.py

# 即座に確認
sqlite3 knowledge_system/database/knowledge.db \
  "SELECT COUNT(*) FROM knowledge_entries;"
```

### Phase 4: 検証（10分）

#### 4-1. データ整合性確認
```bash
# カテゴリ別件数
sqlite3 knowledge_system/database/knowledge.db << 'SQL'
SELECT category, COUNT(*) 
FROM knowledge_entries 
GROUP BY category 
ORDER BY COUNT(*) DESC;
SQL

# 日付範囲確認
sqlite3 knowledge_system/database/knowledge.db << 'SQL'
SELECT MIN(created_at), MAX(created_at)
FROM knowledge_entries;
SQL

# 最新10件
sqlite3 knowledge_system/database/knowledge.db << 'SQL'
SELECT id, title, category
FROM knowledge_entries
ORDER BY id DESC
LIMIT 10;
SQL
```

#### 4-2. ダッシュボード確認
```bash
# ダッシュボード起動
bash sh/start_knowledge_webapp.sh &
DASHBOARD_PID=$!

# 10秒待機
sleep 10

# ブラウザで確認: http://localhost:8080
echo "ダッシュボードで件数確認してください"
echo "期待: 約569件表示"

# 確認後停止
kill $DASHBOARD_PID
```

#### 4-3. KnowledgeManager動作確認
```bash
python3 << 'PYEOF'
from knowledge_system.core_agents.knowledge_manager import KnowledgeManager

km = KnowledgeManager()
stats = km.get_statistics()

print("KnowledgeManager統計:")
print(f"  総エントリ数: {stats.get('total_entries', 0)}件")
print(f"  カテゴリ数: {stats.get('unique_categories', 0)}個")

# 検索テスト
results = km.search_knowledge("Phase", limit=5)
print(f"\n検索テスト（'Phase'）: {len(results)}件")
PYEOF
```

### Phase 5: ロールバック手順（必要時）

もし問題が発生した場合の復旧手順：
```bash
# オプションA: バックアップから復元
cp knowledge_system/database/backups/pre_migration/knowledge_${BACKUP_TIME}.db \
   knowledge_system/database/knowledge.db

# オプションB: 過去ブランチから再取得
git show v1.24.18-24h_task_251125:knowledge_system/database/knowledge.db \
  > knowledge_system/database/knowledge.db

# 確認
sqlite3 knowledge_system/database/knowledge.db \
  "SELECT COUNT(*) FROM knowledge_entries;"
```

**ロールバック時間**: 5分以内

## リスク評価

| リスク | 確率 | 影響 | 対策 |
|--------|------|------|------|
| データ損失 | 低 | 高 | 事前バックアップ |
| スキーマ不一致 | 低 | 中 | 事前スキーマ確認 |
| 重複データ | 中 | 低 | 重複チェック機能 |
| 作業中断 | 低 | 中 | ブランチ切り替え不要 |

## タイムライン

| Phase | タスク | 所要時間 | 累積時間 |
|-------|--------|----------|----------|
| 1 | 安全確保 | 5分 | 5分 |
| 2 | 過去DB取得 | 5分 | 10分 |
| 3 | データマージ | 10分 | 20分 |
| 4 | 検証 | 10分 | 30分 |
| 5 | ロールバック（必要時） | 5分 | 35分 |

**合計**: 約30分（問題なければ20分）

## 成功基準

- [x] 現在のブランチは変更なし
- [x] ナレッジ件数が500件以上
- [x] 既存30件のデータは保持
- [x] ダッシュボードで全件表示
- [x] KnowledgeManagerが正常動作
- [x] Phase 6B開発に影響なし

## 次のアクション

1. この計画書をレビュー
2. 承認後、Phase 1から順次実行
3. 各Phaseで確認しながら進行
4. 問題があれば即座にロールバック
5. 成功後、Phase 6B-03に移行

---

**作成日時**: 2024-11-27  
**作成者**: Development Team  
**レビュー**: 実行前に確認必須  
**承認**: ユーザー確認後
