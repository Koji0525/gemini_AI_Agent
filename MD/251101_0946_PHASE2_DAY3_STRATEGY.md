# 🎯 Phase 2 Day 3 実装戦略

## 📊 現状把握

### 既存エージェントの確認完了
- ✅ **pm_agent.py** (642行) - プロジェクトルート
- ✅ **task_executor.py** (151行) - プロジェクトルート
- ✅ **wp_orchestrator.py** - agents/wordpress/specialized/

### 開発ツールの整備完了
- ✅ **dev.py** - 統合開発コマンド
- ✅ **file_version_manager.py** - ファイル作成のゲートキーパー
- ✅ **auto_commit_push.py** - Git操作の自動化
- ✅ **enterprise_path_resolver.py** - ファイル発見の専門家

---

## 🚀 実装戦略（3段階アプローチ）

### STEP 1: 既存エージェントの詳細分析（15分）
**目的**: 既存コードの構造と依存関係を完全理解
```bash
# 1-1. pm_agent.py の構造確認
python3 << 'PYEOF'
import ast
import inspect
from pathlib import Path

# pm_agent.py のクラスとメソッドを抽出
code = Path('pm_agent.py').read_text()
tree = ast.parse(code)

print("📂 pm_agent.py の構造:")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        print(f"\n📌 class {node.name}:")
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                args = [a.arg for a in item.args.args]
                print(f"   • {item.name}({', '.join(args)})")
PYEOF

# 1-2. task_executor.py の構造確認
python3 << 'PYEOF'
import ast
from pathlib import Path

code = Path('task_executor.py').read_text()
tree = ast.parse(code)

print("\n📂 task_executor.py の構造:")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        print(f"\n📌 class {node.name}:")
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                args = [a.arg for a in item.args.args]
                print(f"   • {item.name}({', '.join(args)})")
PYEOF

# 1-3. 依存関係確認
echo ""
echo "📦 依存関係分析:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📂 pm_agent.py のインポート:"
grep -E "^import |^from " pm_agent.py | head -20

echo ""
echo "📂 task_executor.py のインポート:"
grep -E "^import |^from " task_executor.py | head -20
```

### STEP 2: Integrated Orchestrator v1.0 設計（20分）
**目的**: Document 4 の設計を既存コードに適合

**設計原則**:
1. **リソース注入の徹底** (運用ルール 8)
   - GoogleSheetsManager は外部から注入
   - BrowserController は外部から注入

2. **非同期処理の統一** (運用ルール 9)
   - すべて async/await で統一

3. **1機能1クラス** (運用ルール 4.7)
   - Orchestrator は「調整のみ」
   - 実際の処理は各エージェントに委譲

**統合フロー**:
```
GitHub Actions (6時間ごと)
    ↓
IntegratedOrchestrator.run_continuous_cycle()
    ↓
    ├─→ 1. pm_agent.get_pending_tasks()
    │      └─→ Google Sheets 'pm_task_queue' 読み取り
    │
    ├─→ 2. task_executor.execute_task(task)
    │      └─→ タスクルーティング
    │            └─→ wp_orchestrator.execute()
    │
    ├─→ 3. 結果を pm_agent.update_task_status()
    │      └─→ Google Sheets 更新
    │
    └─→ 4. 次サイクルまで待機 or タイムアウト
```

### STEP 3: 実装・テスト（25分）
**目的**: 最小限の機能で動作確認

**実装範囲**:
- ✅ PM Agent からタスク取得
- ✅ Task Executor へのルーティング
- ✅ 結果の報告
- ✅ タイムアウト制御
- ⚠️ WordPress Orchestrator は次フェーズ（Phase 2 Day 4）

---

## 🛡️ リスク管理

### 既知のリスク
1. **pm_agent.py の __init__ 引数不一致**
   - 対策: 運用ルール 4.5 に従い、事前に確認

2. **task_executor.py の非同期処理**
   - 対策: async/await の統一を確認

3. **Google Sheets API のレート制限**
   - 対策: 適切な待機時間を設定

### 成功基準
- ✅ pm_task_queue からタスク取得成功
- ✅ タスクのステータス更新成功
- ✅ 5分間の連続実行が安定動作
- ✅ エラー時の適切なログ出力

---

## 📈 期待される効果

### 短期的効果（Phase 2 完了時）
- 🎯 目標入力から実行までの自動化
- 📊 進捗の可視化
- 🔄 6時間ごとの自動開発サイクル

### 長期的効果（システム成熟後）
- 🚀 開発効率10倍向上
- 🛡️ 自己修復による安定性向上
- 📈 継続的な学習による精度向上

---

**作成日時**: $(date '+%Y年%m月%d日 %H:%M:%S')  
**目的**: Phase 2 Day 3 の実装指針  
**次回**: 既存エージェントの詳細分析
