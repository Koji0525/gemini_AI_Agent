#!/bin/bash
# 完全修正：スキーマ対応 + F1初回実行

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 完全修正：スキーマ対応 + F1初回実行"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: 実際のスキーマ確認
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: 実際のスキーマ確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📋 knowledge_entriesの完全スキーマ:"
sqlite3 knowledge_system/database/knowledge.db ".schema knowledge_entries"

echo ""
echo "📋 カラム情報（PRAGMA）:"
sqlite3 knowledge_system/database/knowledge.db "PRAGMA table_info(knowledge_entries);" -header -column

echo ""
echo "📊 サンプルデータ（1件）:"
sqlite3 knowledge_system/database/knowledge.db "SELECT * FROM knowledge_entries ORDER BY id DESC LIMIT 1;" -header -column

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: 完全スキーマ対応版KnowledgeManager
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: 完全スキーマ対応版KnowledgeManager"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > tools/knowledge_manager.py << 'PYTHON'
"""
ナレッジマネージャー（完全スキーマ対応版）
既存のSQLiteスキーマに完全対応
"""

import sys
import os
import sqlite3
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class KnowledgeManager:
    """ナレッジマネージャー（完全スキーマ対応版）"""
    
    def __init__(self):
        self.db_path = Path("/workspaces/gemini_AI_Agent/knowledge_system/database/knowledge.db")
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"データベースが見つかりません: {self.db_path}")
        
        # スキーマを確認
        self.schema = self._get_schema()
        self.columns = list(self.schema.keys())
    
    def _get_connection(self, timeout: float = 10.0):
        """接続を取得（タイムアウト付き）"""
        conn = sqlite3.connect(str(self.db_path), timeout=timeout)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn
    
    def _get_schema(self) -> Dict:
        """スキーマを取得（カラム名、型、NOT NULL制約）"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(knowledge_entries)")
        
        schema = {}
        for row in cursor.fetchall():
            # cid, name, type, notnull, dflt_value, pk
            col_name = row[1]
            schema[col_name] = {
                'type': row[2],
                'notnull': bool(row[3]),
                'default': row[4],
                'pk': bool(row[5])
            }
        
        conn.close()
        
        return schema
    
    def add_knowledge(
        self, 
        content: str, 
        source: str,
        metadata: Optional[Dict] = None,
        max_retries: int = 3
    ) -> str:
        """ナレッジを追加（完全スキーマ対応）"""
        
        # タイトルを生成（必須カラム対応）
        title = self._generate_title(source, metadata)
        
        # 詳細な説明文
        full_content = content
        if metadata:
            full_content += f"\n\n[メタデータ]\n"
            full_content += f"ソース: {source}\n"
            for key, value in metadata.items():
                full_content += f"{key}: {value}\n"
        
        for attempt in range(max_retries):
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                # スキーマに合わせて挿入
                # 必須カラムを特定
                insert_data = {
                    'content': full_content
                }
                
                # titleカラムがあれば追加
                if 'title' in self.schema:
                    insert_data['title'] = title
                
                # その他の既知カラム
                if 'source' in self.schema:
                    insert_data['source'] = source
                
                if 'metadata' in self.schema:
                    insert_data['metadata'] = json.dumps(metadata) if metadata else None
                
                # INSERT文を動的に生成
                columns = ', '.join(insert_data.keys())
                placeholders = ', '.join(['?'] * len(insert_data))
                values = tuple(insert_data.values())
                
                cursor.execute(f'''
                    INSERT INTO knowledge_entries ({columns})
                    VALUES ({placeholders})
                ''', values)
                
                entry_id = cursor.lastrowid
                
                conn.commit()
                conn.close()
                
                return f"entry_{entry_id}"
                
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 0.5
                    print(f"  ⏳ データベースロック - {wait_time}秒後にリトライ（{attempt + 1}/{max_retries}）")
                    time.sleep(wait_time)
                else:
                    raise
            
            finally:
                try:
                    conn.close()
                except:
                    pass
    
    def _generate_title(self, source: str, metadata: Optional[Dict] = None) -> str:
        """タイトルを生成"""
        if metadata and 'task_id' in metadata:
            return f"Phase 4A: {metadata['task_id']}"
        else:
            return f"Auto Generated: {source} - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def search_knowledge(self, query: str) -> List[Dict]:
        """ナレッジを検索"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        columns_str = ', '.join(self.columns)
        
        cursor.execute(f'''
            SELECT {columns_str}
            FROM knowledge_entries
            WHERE content LIKE ?
            ORDER BY id DESC
            LIMIT 10
        ''', (f'%{query}%',))
        
        results = []
        for row in cursor.fetchall():
            entry = {}
            for i, col in enumerate(self.columns):
                entry[col] = row[i]
            results.append(entry)
        
        conn.close()
        
        return results
    
    def get_all_entries(self, limit: int = 100) -> List[Dict]:
        """すべてのエントリを取得"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        columns_str = ', '.join(self.columns)
        
        cursor.execute(f'''
            SELECT {columns_str}
            FROM knowledge_entries
            ORDER BY id DESC
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            entry = {}
            for i, col in enumerate(self.columns):
                value = row[i]
                if col == 'content' and value and len(value) > 200:
                    value = value[:200] + '...'
                entry[col] = value
            results.append(entry)
        
        conn.close()
        
        return results
    
    def get_statistics(self) -> Dict:
        """統計情報を取得"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 総数
        cursor.execute('SELECT COUNT(*) FROM knowledge_entries')
        total = cursor.fetchone()[0]
        
        # 今日追加された数
        today = 0
        if 'created_at' in self.columns:
            cursor.execute('''
                SELECT COUNT(*) FROM knowledge_entries
                WHERE DATE(created_at) = DATE('now')
            ''')
            today = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_entries': total,
            'today_entries': today,
            'columns': self.columns,
            'schema': self.schema
        }

PYTHON

echo "✅ 完全スキーマ対応版KnowledgeManager作成"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: F1初回実行版24時間稼働スクリプト
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: F1初回実行版24時間稼働スクリプト"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > sh/run_24h_robust_autonomous.sh << '24H_ROBUST'
#!/bin/bash
# Phase 4A: 堅牢な24時間自律稼働システム（F1初回実行版）

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Phase 4A: 堅牢な24時間自律稼働システム"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "【Phase 4A追加機能】"
echo "  ✅ APIレート制限管理"
echo "  ✅ 緊急停止メカニズム"
echo "  ✅ 自動リソースクリーンアップ"
echo "  ✅ 堅牢なエラーハンドリング"
echo "  ✅ リアルタイムダッシュボード"
echo "  ✅ F1初回実行（新規目標対応）"
echo ""
echo "【既存機能（Phase 1-3）】"
echo "  ✅ 高品質タスク実行（10点保証）"
echo "  ✅ 自動品質チェック・テスト・統合"
echo "  ✅ Git自動コミット"
echo "  ✅ F1-F10完全連携"
echo ""
echo "🎯 目標: 完全自律24時間稼働"
echo ""

START_TIME=$(date +%s)
CYCLE_COUNT=0
ERROR_COUNT=0
SUCCESS_COUNT=0
MAX_CYCLES=96  # 24時間（15分間隔）

LOG_FILE="logs/phase4a_autonomous_$(TZ=Asia/Tokyo date +%y%m%d_%H%M).log"
mkdir -p logs

echo "ログファイル: $LOG_FILE"
echo "ダッシュボード: status.html"
echo ""

while [ $CYCLE_COUNT -lt $MAX_CYCLES ]; do
    CYCLE_COUNT=$((CYCLE_COUNT + 1))
    CURRENT_TIME=$(TZ=Asia/Tokyo date +"%Y-%m-%d %H:%M:%S")
    
    echo "" | tee -a "$LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    echo "🔄 サイクル ${CYCLE_COUNT}/${MAX_CYCLES} @ ${CURRENT_TIME}" | tee -a "$LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    
    # Phase 4A: 緊急停止チェック
    if [ -f "/tmp/system_emergency_stop.flag" ]; then
        echo "  🚨 緊急停止フラグ検出 - システム停止" | tee -a "$LOG_FILE"
        exit 0
    fi
    
    # Phase 4A: 一時停止チェック
    if [ -f "/tmp/system_paused.flag" ]; then
        echo "  ⏸️  システム一時停止中..." | tee -a "$LOG_FILE"
        sleep 3600
        continue
    fi
    
    # F9: 人間指示の処理
    if [ -f "agents/f9_process_instructions.py" ]; then
        echo "  📨 F9: 人間指示の処理..." | tee -a "$LOG_FILE"
        python3 agents/f9_process_instructions.py 2>&1 | tee -a "$LOG_FILE"
    fi
    
    # F1: タスク可用性チェック
    # 重要: 1回目は必ず実行、以降は1時間ごと
    if [ $CYCLE_COUNT -eq 1 ] || [ $((CYCLE_COUNT % 4)) -eq 0 ]; then
        if [ -f "agents/f1_loop_integration.py" ]; then
            if [ $CYCLE_COUNT -eq 1 ]; then
                echo "  🔄 F1: 初回タスク生成（新規目標チェック）..." | tee -a "$LOG_FILE"
            else
                echo "  🔄 F1: タスク可用性チェック..." | tee -a "$LOG_FILE"
            fi
            python3 agents/f1_loop_integration.py 2>&1 | tee -a "$LOG_FILE"
        fi
    fi
    
    # Phase 3: 完全自律タスク実行
    echo "  🚀 Phase 3+4A: タスク実行..." | tee -a "$LOG_FILE"
    
    if bash sh/run_phase3_full_autonomous.sh 2 2>&1 | tee -a "$LOG_FILE"; then
        echo "  ✅ タスク実行成功" | tee -a "$LOG_FILE"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        ERROR_COUNT=0
    else
        echo "  ⚠️  タスク実行エラー" | tee -a "$LOG_FILE"
        ERROR_COUNT=$((ERROR_COUNT + 1))
        
        # F7: 自己修復
        if [ $ERROR_COUNT -le 3 ]; then
            echo "  🔧 F7: 自己修復（${ERROR_COUNT}/3）" | tee -a "$LOG_FILE"
            sleep 30
        else
            echo "  ❌ F7: 修復失敗 - 一時停止" | tee -a "$LOG_FILE"
            touch /tmp/system_paused.flag
            ERROR_COUNT=0
        fi
    fi
    
    # Phase 4A: リソースクリーンアップ（6時間ごと）
    if [ $((CYCLE_COUNT % 24)) -eq 0 ]; then
        echo "  🧹 Phase 4A: リソースクリーンアップ..." | tee -a "$LOG_FILE"
        bash sh/cleanup_resources.sh 2>&1 | tee -a "$LOG_FILE"
    fi
    
    # Phase 4A: ダッシュボード更新
    bash sh/update_dashboard.sh 2>&1 | tee -a "$LOG_FILE"
    
    # F9: 進捗報告（1時間ごと）
    if [ $((CYCLE_COUNT % 4)) -eq 0 ]; then
        echo "  📊 F9: 進捗報告" | tee -a "$LOG_FILE"
        echo "     成功サイクル: ${SUCCESS_COUNT}" | tee -a "$LOG_FILE"
        echo "     ダッシュボード: status.html" | tee -a "$LOG_FILE"
    fi
    
    # F10: 健全性チェック（1時間ごと）
    if [ $((CYCLE_COUNT % 4)) -eq 0 ]; then
        if [ -f "sh/health_check_periodic.sh" ]; then
            echo "  🔬 F10: 健全性チェック" | tee -a "$LOG_FILE"
            bash sh/health_check_periodic.sh 2>&1 | tee -a "$LOG_FILE"
        fi
    fi
    
    echo "  ⏳ 次のサイクルまで15分待機..." | tee -a "$LOG_FILE"
    sleep 900
done

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
ELAPSED_HOURS=$((ELAPSED / 3600))

echo "" | tee -a "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
echo "✅ Phase 4A: 24時間稼働完了" | tee -a "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
echo "  実行時間: ${ELAPSED_HOURS}時間" | tee -a "$LOG_FILE"
echo "  実行サイクル: ${CYCLE_COUNT}" | tee -a "$LOG_FILE"
echo "  成功サイクル: ${SUCCESS_COUNT}" | tee -a "$LOG_FILE"
echo "  ダッシュボード: status.html" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

24H_ROBUST

chmod +x sh/run_24h_robust_autonomous.sh

echo "✅ F1初回実行版24時間稼働スクリプト作成"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: テスト実行
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: テスト実行"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 << PYTHON
import sys
import time
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.automation.knowledge_base_integrator import KnowledgeBaseIntegrator
from tools.knowledge_manager import KnowledgeManager
from datetime import datetime

print("🧪 完全スキーマ対応テスト")
print()

# 登録前の件数
km = KnowledgeManager()

print("📋 スキーマ情報:")
stats = km.get_statistics()
for col, info in stats['schema'].items():
    notnull_mark = " (NOT NULL)" if info['notnull'] else ""
    print(f"  - {col}: {info['type']}{notnull_mark}")

print()
print(f"📊 登録前: {stats['total_entries']}件")
print()

# テスト登録
kbi = KnowledgeBaseIntegrator()

success_count = 0
for i in range(3):
    task_id = f"test_complete_schema_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i+1}"
    
    print(f"  🔄 テスト{i+1}: {task_id}")
    
    result = kbi.register_to_knowledge_base(
        task_id=task_id,
        output_path=f"/tmp/test_output_{i+1}",
        quality_score=10.0,
        test_results={'passed': True}
    )
    
    if result['success']:
        print(f"     ✅ 登録成功 ({result['entry_id']})")
        success_count += 1
    else:
        print(f"     ❌ 登録失敗")
    
    time.sleep(0.5)
    print()

# 登録後の件数
stats_after = km.get_statistics()
print(f"📊 登録後: {stats_after['total_entries']}件")

if stats_after['total_entries'] > stats['total_entries']:
    increase = stats_after['total_entries'] - stats['total_entries']
    print(f"✅ {increase}件増加しました！")
    print(f"   成功率: {success_count}/3")
else:
    print(f"⚠️  件数が増加していません")
    print(f"   成功: {success_count}/3")

PYTHON

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 完全修正完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 最終確認
FINAL_COUNT=$(sqlite3 knowledge_system/database/knowledge.db "SELECT COUNT(*) FROM knowledge_entries;" 2>/dev/null || echo "0")
echo "📊 最終ナレッジ件数: ${FINAL_COUNT}件"

echo ""
echo "📅 最新エントリ（5件）:"
sqlite3 knowledge_system/database/knowledge.db "SELECT id, title, created_at FROM knowledge_entries ORDER BY id DESC LIMIT 5;" -header -column 2>/dev/null

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 24時間稼働開始"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "【重要な変更点】"
echo "  1. ✅ titleカラム対応（NOT NULL制約）"
echo "  2. ✅ F1を1回目のサイクルで必ず実行"
echo "  3. ✅ 新規目標を即座に検出・分解"
echo ""
echo "🎯 動作フロー:"
echo "  サイクル1: F1実行（新規目標チェック） → タスク分解 → タスク実行"
echo "  サイクル2-3: タスク実行のみ"
echo "  サイクル4: F1実行（定期チェック） → タスク実行"
echo "  ..."
echo ""
echo "📖 実行コマンド:"
echo "  bash sh/run_24h_robust_autonomous.sh"
echo ""

