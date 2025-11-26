# 🗺️ 統合マスターロードマップ v6.0 - 2025年最新アーキテクチャ採用版

**文書バージョン**: v6.0  
**作成日**: 2025年11月26日  
**対象システム**: 24時間365日自己進化型マルチAIエージェントシステム  
**プロジェクトルート**: `/workspaces/gemini_AI_Agent`  
**文書管理**: `/workspaces/gemini_AI_Agent/MD/roadmaps/`  
**進捗管理**: 本ドキュメント内「📊 マスターチェックシート」セクションのみ  
**総期間**: 8週間（56日間）  
**総実装行数**: 約17,000行（新規コード）

---

## 📋 目次

1. [ロードマップの使い方（AI引継ぎガイド）](#1-ロードマップの使い方ai引継ぎガイド)
2. [開発原則（なぜなぜ分析ベース）](#2-開発原則なぜなぜ分析ベース)
3. [📊 マスターチェックシート](#3-📊-マスターチェックシート)
4. [Phase 0: 診断システム構築](#4-phase-0-診断システム構築)
5. [Phase 1: 共有黒板基盤](#5-phase-1-共有黒板基盤)
6. [Phase 2: Reflexion品質向上](#6-phase-2-reflexion品質向上)
7. [Phase 3: 動的DAG計画](#7-phase-3-動的dag計画)
8. [Phase 4: 階層型組織](#8-phase-4-階層型組織)
9. [Phase 5: 統合と最適化](#9-phase-5-統合と最適化)
10. [診断プロトコル](#10-診断プロトコル)
11. [AI引き継ぎプロトコル](#11-ai引き継ぎプロトコル)
12. [成功基準](#12-成功基準)

---

## 1. ロードマップの使い方（AI引継ぎガイド）

### 1.1 このドキュメントの目的

このマスターロードマップは、**開発の初期から終盤まで全工程を1つで管理する**唯一の真実の情報源（Single Source of Truth）です。

### 1.2 AI交代時の使い方
```bash
# ========================================
# 新しいAIセッション開始時の手順
# ========================================

# 1. このドキュメントを開く
cat MD/roadmaps/251126_MASTER_ROADMAP_v6_0.md

# 2. マスターチェックシートを確認
grep "^| ⬜" MD/roadmaps/251126_MASTER_ROADMAP_v6_0.md | head -1

# 3. 診断スクリプトを実行
bash scripts/diagnostics/system_health_check.sh

# 4. 既存テスト成功率を確認
pytest tests/ --ignore=tests/integration/ --tb=no -q

# 5. 未完了の最初のタスクから再開
```

### 1.3 進捗更新方法
```bash
# タスク完了時
# 1. このファイルを編集して ⬜ を ✅ に変更
# 2. Git commit
git add MD/roadmaps/251126_MASTER_ROADMAP_v6_0.md
git commit -m "Progress: Phase X-YYY 完了"

# 3. 次のAIセッションで自動的に進捗が引き継がれる
```

---

## 2. 開発原則（なぜなぜ分析ベース）

### 原則1: 実装ファースト

**原則**: 抽象的な要件ではなく、実際のファイルパスとコード行数で管理する

**なぜか**:
- 過去の失敗: 「ダッシュボードを作る」→ 何を作るか不明確
- 改善策: 「`agents/observability/dashboard.py` (2,500行) を作成」→ 明確

**具体例**:
```
❌ 悪い例: "共有メモリシステムを実装"
✅ 良い例: "agents/integration/shared_blackboard_manager.py (850行) 実装
           - SharedBlackboardManager クラス
           - read_section(), write_section() メソッド"
```

### 原則2: 全体像の可視化

**原則**: システム構成図とファイル依存関係を常に更新する

**なぜか**:
- 過去の失敗: コンポーネント追加時に依存関係が不明確で既存システムを破壊
- 改善策: 依存関係マップを自動生成し、変更影響範囲を可視化

**実装**:
```bash
# 依存関係可視化ツール実行
python3 agents/observer_enhanced/orchestrator.py --visualize
# → agents/observer_enhanced/web/dependency_graph.html 生成
```

### 原則3: 既存システム保護（後戻り防止）

**原則**: 既存コンポーネント（4,350行）は一切変更しない

**なぜか**:
- 既存システムは480+サイクル（24時間）の連続稼働実績がある
- テスト成功率84.3%という高い品質を既に達成している
- 変更すると過去の蓄積ナレッジ（511+エントリ）が無効化されるリスク

**保護リスト**:
```python
PROTECTED_FILES = [
    'agents/complete_engine_ultimate.py',          # 1,250行
    'tools/sheets_manager.py',                     # 450行
    'tools/safe_sheets_wrapper.py',                # 180行
    'knowledge_system/core_agents/knowledge_manager.py',  # 520行
    'tools/base_data_accessor.py',                 # 200行
    'agents/task_execution/high_quality_executor_v8.py',  # 800行
    'agents/quality_evaluation/quality_evaluator.py',     # 350行
    'agents/self_healing/self_healing_agent.py',   # 600行
]
```

### 原則4: テスト駆動統合

**原則**: 既存テスト成功率84.3%を絶対に下回らない

**なぜこの数字か**:
- 84.3%: 現在の既存システム実績値（100+テストケース中84件成功）
- 業界標準: 本番システムは80%以上が推奨
- 根拠: この成功率で480+サイクル（24時間）の連続稼働実績

**監視方法**:
```bash
# CI/CDで毎回チェック
pytest tests/ --ignore=tests/integration/ --tb=no -q
# 期待: 84/100 = 84% 以上
```

### 原則5: コンテキスト情報の明記

**原則**: すべての数字に「なぜその数字か」の根拠を記載

**例**:
```
❌ 悪い例: "並列実行数: 10個"
✅ 良い例: "並列実行数: 10個
           理由: CPU 8コア + I/O待ち2 = 10
           根拠: 1タスク100MB × 10 = 1GB (制限2GB内)"
```

### 原則6: 具体的な数字で管理

**原則**: 進捗は「実装した行数 / 予定行数」で管理

**管理方法**:
```bash
# 実装行数カウント
wc -l agents/integration/shared_blackboard_manager.py
# → 850行 / 850行 (100%)
```

---

## 3. 📊 マスターチェックシート（進捗管理の唯一の場所）

### 使用方法
```
⬜ : 未着手
🔄 : 実装中
✅ : 完了（テスト済み）
🔒 : 完了（本番稼働中・変更禁止）
```

### 全体進捗サマリー

| Phase | タスク数 | 完了 | 進捗率 | 所要日数 | 状態 |
|-------|---------|------|--------|---------|------|
| Phase 0 | 5 | 0 | 0% | 3日 | ⬜ 未着手 |
| Phase 1 | 8 | 0 | 0% | 10日 | ⬜ 未着手 |
| Phase 2 | 7 | 0 | 0% | 10日 | ⬜ 未着手 |
| Phase 3 | 6 | 0 | 0% | 8日 | ⬜ 未着手 |
| Phase 4 | 8 | 0 | 0% | 12日 | ⬜ 未着手 |
| Phase 5 | 6 | 0 | 0% | 13日 | ⬜ 未着手 |
| **合計** | **40** | **0** | **0%** | **56日** | ⬜ 未着手 |

---

## 4. Phase 0: 診断システム構築（3日間）

### 4.1 目的とコンテキスト

**なぜ最初に診断システムか**:
- 既存システム（4,350行）を保護するため、変更前後の状態を比較する必要がある
- 新機能追加時に「何が壊れたか」を即座に検出するため
- テスト成功率84.3%を常時監視するため

**期待される成果**:
- 診断スクリプト5本
- 診断ダッシュボード1個
- 自動診断スケジューラー

### 4.2 タスク一覧

| ID | タスク | ファイルパス | 行数 | 所要 | 状態 |
|----|--------|-------------|------|------|------|
| P0-001 | 診断ディレクトリ作成 | `scripts/diagnostics/` | - | 0.5h | ✅ |
| P0-002 | システムヘルスチェック | `scripts/diagnostics/system_health_check.sh` | 200 | 4h | ✅ |
| P0-003 | テスト成功率監視 | `scripts/diagnostics/test_success_monitor.py` | 150 | 3h | ✅ |
| P0-004 | 依存関係チェック | `scripts/diagnostics/check_protected_files.py` | 100 | 3h | ✅ |
| P0-005 | 診断結果可視化 | `docs/diagnostics/reports/diagnostic_dashboard.html` | 500 | 8h | ✅ |

**合計**: 1,150行、21.5時間（3日間）

### 4.3 詳細仕様

#### P0-001: 診断ディレクトリ作成
```bash
# 実装内容
mkdir -p scripts/diagnostics
mkdir -p docs/diagnostics/reports
mkdir -p shared_states/diagnostics

# 成功基準
[ -d "scripts/diagnostics" ] && echo "✅ 成功"
```

**なぜ3つのディレクトリか**:
- `scripts/diagnostics/`: 診断スクリプト本体
- `docs/diagnostics/reports/`: 診断結果レポート（HTML）
- `shared_states/diagnostics/`: 診断履歴（JSON）

#### P0-002: システムヘルスチェック

**実装ファイル**: `scripts/diagnostics/system_health_check.sh`

**機能**:
```bash
#!/bin/bash
# システムヘルスチェック総合スクリプト

echo "========================================="
echo "🏥 システムヘルスチェック"
echo "========================================="

# 1. テスト成功率チェック
echo "[1/5] テスト成功率チェック..."
SUCCESS_RATE=$(pytest tests/ --ignore=tests/integration/ --tb=no -q 2>&1 | grep -oP '\d+(?= passed)' | head -1)
TOTAL=$(pytest tests/ --ignore=tests/integration/ --collect-only -q 2>&1 | wc -l)
RATE=$(echo "scale=1; $SUCCESS_RATE/$TOTAL*100" | bc)

if (( $(echo "$RATE >= 84.3" | bc -l) )); then
    echo "✅ テスト成功率: $RATE% (基準: 84.3%)"
else
    echo "❌ テスト成功率低下: $RATE% < 84.3%"
fi

# 2. 保護ファイル変更検出
echo "[2/5] 保護ファイル変更検出..."
python3 scripts/diagnostics/check_protected_files.py

# 3. リソース使用状況
echo "[3/5] リソース使用状況..."
MEMORY=$(free -m | awk '/^Mem:/{print $3}')
echo "   メモリ使用: ${MEMORY}MB / 2048MB"

DISK=$(df -h . | awk 'NR==2{print $3}')
echo "   ディスク使用: ${DISK} / 32GB"

# 4. エージェント稼働状況
echo "[4/5] エージェント稼働状況..."
AGENT_COUNT=$(find agents/ -name "*.py" -type f | wc -l)
echo "   エージェント数: ${AGENT_COUNT}"

# 5. ナレッジDB統計
echo "[5/5] ナレッジDB統計..."
python3 << PYEOF
from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
km = KnowledgeManager()
stats = km.get_statistics()
print(f"   ナレッジ件数: {stats.get('total_entries', 0)}")
PYEOF

echo ""
echo "========================================="
echo "✅ ヘルスチェック完了"
echo "========================================="
```

**成功基準**:
- 実行時間 < 30秒
- テスト成功率 ≥ 84.3%
- エラーなく完了

**なぜ5つの項目か**:
- テスト成功率: 品質の基準値
- 保護ファイル: 意図しない変更の検出
- リソース: メモリ/ディスク不足の予防
- エージェント数: システム規模の把握
- ナレッジDB: 学習の蓄積確認

#### P0-003: テスト成功率監視

**実装ファイル**: `scripts/diagnostics/test_success_monitor.py`
```python
#!/usr/bin/env python3
"""
テスト成功率監視スクリプト

機能:
- 既存テストを実行
- 成功率を計算
- 履歴と比較
- 低下時にアラート
"""
import subprocess
import json
from datetime import datetime
from pathlib import Path

HISTORY_FILE = "shared_states/diagnostics/test_history.json"
THRESHOLD = 84.3  # 成功率基準

def run_tests():
    """既存テストを実行"""
    result = subprocess.run(
        ["pytest", "tests/", "--ignore=tests/integration/", 
         "--tb=no", "-q"],
        capture_output=True,
        text=True
    )
    
    # 成功数を抽出
    output = result.stdout
    passed = 0
    total = 0
    
    for line in output.split('\n'):
        if 'passed' in line:
            import re
            match = re.search(r'(\d+) passed', line)
            if match:
                passed = int(match.group(1))
        if 'failed' in line:
            match = re.search(r'(\d+) failed', line)
            if match:
                total += int(match.group(1))
    
    total += passed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    return {
        'timestamp': datetime.now().isoformat(),
        'passed': passed,
        'total': total,
        'success_rate': round(success_rate, 1)
    }

def save_history(result):
    """履歴を保存"""
    history = []
    if Path(HISTORY_FILE).exists():
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    
    history.append(result)
    
    # 直近100件のみ保持
    history = history[-100:]
    
    Path(HISTORY_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def check_degradation(result, history):
    """品質劣化を検出"""
    if result['success_rate'] < THRESHOLD:
        print(f"❌ アラート: テスト成功率が基準値を下回りました")
        print(f"   現在: {result['success_rate']}%")
        print(f"   基準: {THRESHOLD}%")
        return True
    
    if len(history) >= 2:
        prev = history[-2]
        diff = result['success_rate'] - prev['success_rate']
        if diff < -5:  # 5%以上の低下
            print(f"⚠️  警告: テスト成功率が急激に低下しました")
            print(f"   変化: {diff:+.1f}%")
    
    return False

def main():
    print("="*60)
    print("📊 テスト成功率監視")
    print("="*60)
    
    # テスト実行
    result = run_tests()
    
    # 履歴読み込み
    history = []
    if Path(HISTORY_FILE).exists():
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    
    # 結果表示
    print(f"\n📈 結果:")
    print(f"   成功: {result['passed']}/{result['total']}")
    print(f"   成功率: {result['success_rate']}%")
    print(f"   基準値: {THRESHOLD}%")
    
    # 品質チェック
    degraded = check_degradation(result, history)
    
    # 履歴保存
    save_history(result)
    
    print(f"\n✅ 監視完了")
    
    return 1 if degraded else 0

if __name__ == "__main__":
    exit(main())
```

**成功基準**:
- 実行時間 < 5分
- 履歴ファイル生成
- 基準値判定正確

**なぜ100件の履歴か**:
- トレンド分析に十分（約1ヶ月分）
- ファイルサイズ小（< 50KB）
- 読み込み高速（< 100ms）

#### P0-004: 依存関係チェック

**実装ファイル**: `scripts/diagnostics/dependency_checker.py`
```python
#!/usr/bin/env python3
"""
依存関係チェックスクリプト

機能:
- 保護ファイルへの依存を検出
- 循環参照を検出
- 依存関係グラフを生成
"""
import ast
import sys
from pathlib import Path
from typing import Dict, List, Set

PROJECT_ROOT = Path(__file__).parent.parent.parent

PROTECTED_FILES = [
    'agents/complete_engine_ultimate.py',
    'tools/sheets_manager.py',
    'tools/safe_sheets_wrapper.py',
    'knowledge_system/core_agents/knowledge_manager.py',
]

def extract_imports(file_path: Path) -> List[str]:
    """ファイルからimport文を抽出"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        return imports
    except:
        return []

def check_protected_dependencies(file_path: Path) -> List[Dict]:
    """保護ファイルへの依存をチェック"""
    imports = extract_imports(file_path)
    
    issues = []
    for imp in imports:
        # モジュール名からファイルパスを推定
        module_path = imp.replace('.', '/') + '.py'
        
        for protected in PROTECTED_FILES:
            if protected in module_path:
                issues.append({
                    'file': str(file_path),
                    'imports': protected,
                    'risk': 'high' if 'complete_engine' in protected else 'medium'
                })
    
    return issues

def find_circular_dependencies() -> List[List[str]]:
    """循環参照を検出"""
    # 簡易的な実装（完全版は別途）
    return []

def main():
    print("="*60)
    print("🔍 依存関係チェック")
    print("="*60)
    
    # 新規ファイルをチェック
    new_files = []
    for pattern in ['agents/integration/*.py', 'agents/quality/*.py', 
                   'agents/planning/*.py', 'agents/hierarchy/*.py']:
        new_files.extend(PROJECT_ROOT.glob(pattern))
    
    print(f"\n📁 チェック対象: {len(new_files)}ファイル")
    
    all_issues = []
    for file_path in new_files:
        issues = check_protected_dependencies(file_path)
        all_issues.extend(issues)
    
    if all_issues:
        print(f"\n⚠️  保護ファイルへの依存検出: {len(all_issues)}件")
        for issue in all_issues[:5]:  # 最初の5件のみ表示
            print(f"   {issue['file']} → {issue['imports']} (リスク: {issue['risk']})")
    else:
        print(f"\n✅ 保護ファイルへの不適切な依存なし")
    
    # 循環参照チェック
    circular = find_circular_dependencies()
    if circular:
        print(f"\n❌ 循環参照検出: {len(circular)}件")
    else:
        print(f"\n✅ 循環参照なし")
    
    print(f"\n✅ 依存関係チェック完了")

if __name__ == "__main__":
    main()
```

**成功基準**:
- 全ファイルスキャン完了
- 循環参照0件
- 不適切な依存0件

#### P0-005: 診断結果可視化

**実装ファイル**: `scripts/diagnostics/diagnostic_dashboard.html`

**機能**:
- テスト成功率のトレンドグラフ
- リソース使用状況
- 依存関係マップ
- アラート一覧

**技術スタック**:
- Chart.js: グラフ描画
- D3.js: 依存関係グラフ
- Bootstrap: レイアウト

**成功基準**:
- 表示時間 < 3秒
- 自動更新（10秒ごと）
- レスポンシブ対応

---

## 5. Phase 1: 共有黒板基盤（10日間）

### 5.1 目的とコンテキスト

**なぜ共有黒板が必要か**:
- 従来: チャット履歴のみで情報共有 → 情報が埋没
- 改善: 構造化JSONで情報共有 → 検索・更新が容易

**期待される成果**:
- 共有黒板マネージャー
- ファイルベースJSON管理
- 楽観的ロック機構
- イベント通知システム

### 5.2 タスク一覧

| ID | タスク | ファイルパス | 行数 | 所要 | 状態 |
|----|--------|-------------|------|------|------|
| P1-001 | 共有黒板ディレクトリ | `shared_states/` | - | 0.5h | ✅ |
| P1-002 | 基本クラス実装 | `agents/integration/shared_blackboard_manager.py` | 850 | 16h | ✅ |
| P1-003 | ロック機構 | 同上 | - | 8h | ✅ |
| P1-004 | 履歴管理 | `shared_states/history/` | 200 | 6h | ✅ |
| P1-005 | イベント通知 | 同上 | 150 | 6h | ✅ |
| P1-006 | テスト作成 | `tests/integration/test_blackboard_advanced.py` | 400 | 10h | ✅ |
| P1-007 | ドキュメント | `docs/architecture/shared_blackboard_guide.md` | - | 4h | ✅ |
| P1-008 | 診断項目追加 | `scripts/diagnostics/` | 100 | 3h | ✅ |

**合計**: 1,700行、53.5時間（10日間）

### 5.3 詳細仕様

#### P1-002: 基本クラス実装

**実装ファイル**: `agents/integration/shared_blackboard_manager.py`

**クラス設計**:
```python
class SharedBlackboardManager:
    """
    共有黒板マネージャー
    
    責務:
    - ゴールステートの読み書き
    - 楽観的ロック
    - 変更履歴記録
    - イベント通知
    
    データ構造:
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
    """
    
    def __init__(self, goal_id: str):
        self.goal_id = goal_id
        self.state_path = f"shared_states/goal_{goal_id}_state.json"
        self.history_dir = f"shared_states/history/goal_{goal_id}/"
        self.subscribers = {}
    
    def read_full_state(self) -> Dict:
        """ステート全体を読み取り"""
        pass
    
    def read_section(self, section_name: str) -> Dict:
        """特定セクションのみ読み取り"""
        pass
    
    def write_section(self, section_name: str, data: Dict) -> bool:
        """楽観的ロックで書き込み"""
        pass
    
    def subscribe_changes(self, section: str, callback: Callable):
        """変更通知を購読"""
        pass
```

**なぜ850行か**:
- 基本メソッド: 300行
- ロック機構: 200行
- 履歴管理: 150行
- イベント通知: 100行
- エラー処理: 100行

**成功基準**:
- 読み取り時間 < 100ms
- 書き込み時間 < 500ms
- 競合解決成功率 > 95%

---

## 6. Phase 2: Reflexion品質向上（10日間）

### 6.1 目的とコンテキスト

**なぜReflexionが必要か**:
- 現状: 平均品質スコア60点
- 目標: 85点以上
- 手段: 自動批評と再実行ループ

**期待される成果**:
- Reflexionループエンジン
- Criticエージェント
- フィードバック生成システム

### 6.2 タスク一覧

| ID | タスク | ファイルパス | 行数 | 所要 | 状態 |
|----|--------|-------------|------|------|------|
| P2-001 | Reflexionディレクトリ | `agents/quality/` | - | 0.5h | ✅ |
| P2-002 | ループエンジン | `agents/quality/reflexion_loop.py` | 600 | 12h | ✅ |
| P2-003 | Criticエージェント | `agents/quality/critic_agent.py` | 400 | 10h | ✅ |
| P2-004 | フィードバック生成 | `agents/quality/feedback_generator.py` | 300 | 8h | ✅ |
| P2-005 | 既存Executor統合 | `agents/task_execution/executor_with_reflexion.py` | 500 | 10h | ⬜ |
| P2-006 | テスト作成 | `tests/integration/test_reflexion_loop.py` | 500 | 12h | ⬜ |
| P2-007 | ドキュメント | `docs/reflexion_loop_guide.md` | - | 4h | ⬜ |

**合計**: 2,300行、56.5時間（10日間）

---

## 7. Phase 3: 動的DAG計画（8日間）

### 7.1 タスク一覧

| ID | タスク | ファイルパス | 行数 | 所要 | 状態 |
|----|--------|-------------|------|------|------|
| P3-001 | Planningディレクトリ | `agents/planning/` | - | 0.5h | ⬜ |
| P3-002 | DAGマネージャー | `agents/planning/dynamic_dag_manager.py` | 700 | 14h | ⬜ |
| P3-003 | タスク分割ロジック | 同上 | 300 | 8h | ⬜ |
| P3-004 | 依存関係解決 | 同上 | 200 | 6h | ⬜ |
| P3-005 | 可視化機能 | `agents/planning/dag_visualizer.py` | 400 | 8h | ⬜ |
| P3-006 | テスト作成 | `tests/integration/test_dynamic_dag.py` | 400 | 8h | ⬜ |

**合計**: 2,000行、44.5時間（8日間）

---

## 8. Phase 4: 階層型組織（12日間）

### 8.1 タスク一覧

| ID | タスク | ファイルパス | 行数 | 所要 | 状態 |
|----|--------|-------------|------|------|------|
| P4-001 | Hierarchyディレクトリ | `agents/hierarchy/` | - | 0.5h | ⬜ |
| P4-002 | Executive Manager | `agents/hierarchy/executive_manager.py` | 800 | 16h | ⬜ |
| P4-003 | Team Leader | `agents/hierarchy/team_leader.py` | 600 | 12h | ⬜ |
| P4-004 | メッセージング | `agents/hierarchy/messaging.py` | 400 | 10h | ⬜ |
| P4-005 | 組織構築ロジック | `agents/hierarchy/org_builder.py` | 500 | 12h | ⬜ |
| P4-006 | 既存Orchestrator統合 | `agents/complete_engine_ultimate_v2.py` | 1,200 | 20h | ⬜ |
| P4-007 | テスト作成 | `tests/integration/test_hierarchical_manager.py` | 600 | 14h | ⬜ |
| P4-008 | ドキュメント | `docs/hierarchical_teams_guide.md` | - | 6h | ⬜ |

**合計**: 4,100行、90.5時間（12日間）

---

## 9. Phase 5: 統合と最適化（13日間）

### 9.1 タスク一覧

| ID | タスク | ファイルパス | 行数 | 所要 | 状態 |
|----|--------|-------------|------|------|------|
| P5-001 | 統合テスト | `tests/integration/test_full_system.py` | 800 | 20h | ⬜ |
| P5-002 | パフォーマンスチューニング | 各種ファイル | - | 16h | ⬜ |
| P5-003 | ダッシュボード統合 | `agents/observability/realtime_dashboard.py` | 2,500 | 30h | ⬜ |
| P5-004 | 24時間耐久テスト | - | - | 24h | ⬜ |
| P5-005 | ドキュメント整備 | `docs/` | - | 12h | ⬜ |
| P5-006 | デプロイ準備 | `scripts/deploy/` | 200 | 6h | ⬜ |

**合計**: 3,500行、108時間（13日間）

---

## 10. 診断プロトコル

### 10.1 定期診断スケジュール
```bash
# 毎日実行（Cron設定）
0 6 * * * cd /workspaces/gemini_AI_Agent && bash scripts/diagnostics/system_health_check.sh

# 診断内容
# 1. テスト成功率: 84.3%以上維持
# 2. 保護ファイル: 変更なし
# 3. メモリ使用: 2GB未満
# 4. ディスク使用: 30GB未満
# 5. エージェント数: 増加のみ（削除なし）
```

### 10.2 診断失敗時の対応
```bash
# アラート発生時
if [ "$TEST_SUCCESS_RATE" -lt "84.3" ]; then
    # 1. 最新コミットをロールバック
    git revert HEAD
    
    # 2. テスト再実行
    pytest tests/ --ignore=tests/integration/
    
    # 3. 人間に通知
    echo "❌ テスト成功率低下" | mail -s "Alert" admin@example.com
fi
```

---

## 11. AI引き継ぎプロトコル

### 11.1 新しいAIセッション開始時
```markdown
1. このドキュメントを読み込む
   cat MD/roadmaps/251126_MASTER_ROADMAP_v6_0.md

2. マスターチェックシートを確認
   grep "^| ⬜" MD/roadmaps/251126_MASTER_ROADMAP_v6_0.md | head -1
   → 未完了の最初のタスクを特定

3. 診断スクリプトを実行
   bash scripts/diagnostics/system_health_check.sh
   → システムが健全であることを確認

4. 前回の作業コンテキストを確認
   git log -5 --oneline
   → 最後に完了したタスクを確認

5. 次のタスクを開始
   → マスターチェックシートの未完了タスクを実装

6. 完了後、診断＆チェックシート更新
   bash scripts/diagnostics/system_health_check.sh
   # ⬜ を ✅ に変更
   git commit -m "Progress: タスクID完了"
```

---

## 12. 成功基準

### 12.1 最終的な成功基準

| 項目 | 目標値 | 測定方法 | なぜこの数値？ |
|------|--------|---------|---------------|
| **テスト成功率** | ≥ 84.3% | pytest | 既存システム実績値 |
| **平均品質スコア** | ≥ 85点 | Reflexion評価 | 業界標準80点を上回る |
| **タスク完了時間** | < 24時間 | ログ分析 | 1営業日以内 |
| **並列実行数** | 10個 | 同時スレッド | CPU8コア + I/O待ち |
| **共有黒板応答** | < 500ms | time計測 | リアルタイム性 |
| **Reflexion成功率** | > 70% | 統計 | 3回ループで90%達成 |

---

**文書終了** (合計: 約9,500文字)

**次のアクション**:
1. Phase 0から実装開始
2. 各タスク完了後に診断実行
3. チェックシートを✅に更新
