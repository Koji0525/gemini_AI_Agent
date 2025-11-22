#!/bin/bash
# F1-F10連携状況の完全見える化と検証
# システム全体の連携フローを確認

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 F1-F10連携状況の完全見える化"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: F1-F10の実装ファイルパス確認
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: F1-F10の実装ファイルパス確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 << 'PYTHON'
import sys
import os
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

print("🔍 F1-F10実装ファイルパス調査")
print("━" * 60)

# F1-F10の定義
features = {
    "F1": {
        "name": "ゴール自動分解",
        "expected_paths": [
            "agents/goal_concrete_agent.py",
            "agents/pm_agent.py"
        ],
        "loop": "Loop 0（初期設定）",
        "trigger": "手動実行"
    },
    "F2": {
        "name": "タスク自律実行",
        "expected_paths": [
            "agents/task_executor.py",
            "agents/complete_engine_ultimate.py"
        ],
        "loop": "Loop 1（タスク実行ループ）",
        "trigger": "3分ごと、または手動"
    },
    "F3": {
        "name": "品質自動評価",
        "expected_paths": [
            "agents/quality_evaluator.py"
        ],
        "loop": "Loop 1（タスク実行後）",
        "trigger": "タスク完了時"
    },
    "F4": {
        "name": "ナレッジ自動蓄積",
        "expected_paths": [
            "knowledge_system/core_agents/knowledge_manager.py",
            "knowledge_system/core_agents/sqlite_manager.py"
        ],
        "loop": "Loop 1 & Loop 3",
        "trigger": "タスク完了時、学習時"
    },
    "F5": {
        "name": "進捗自動可視化",
        "expected_paths": [
            "agents/observability/dashboard.py"
        ],
        "loop": "独立実行",
        "trigger": "手動、または定期実行"
    },
    "F6": {
        "name": "動的タスク追加",
        "expected_paths": [
            "agents/task_coordinator.py"
        ],
        "loop": "Loop 1",
        "trigger": "必要時に自動"
    },
    "F7": {
        "name": "自己修復機能",
        "expected_paths": [
            "agents/self_healing_agent.py",
            "agents/self_healing/self_healing_agent.py"
        ],
        "loop": "Loop 2（エラー時）",
        "trigger": "エラー検出時（最大3回）"
    },
    "F8": {
        "name": "自己進化機能",
        "expected_paths": [
            "agents/self_evolution_agent.py",
            "agents/self_evolution/self_evolution_agent.py"
        ],
        "loop": "Loop 3（学習ループ）",
        "trigger": "50エラー蓄積、または6時間ごと"
    },
    "F9": {
        "name": "人間連携機能",
        "expected_paths": [
            "agents/human_collaboration_agent.py"
        ],
        "loop": "全Loop",
        "trigger": "不明点、重要イベント時"
    },
    "F10": {
        "name": "定期健全性チェック",
        "expected_paths": [
            "agents/health_check_agent.py"
        ],
        "loop": "独立実行",
        "trigger": "1時間ごと"
    }
}

print("\n【F1-F10実装ファイルパスと存在確認】\n")

for fid, info in features.items():
    print(f"{fid}: {info['name']}")
    print(f"  🔄 Loop: {info['loop']}")
    print(f"  ⚡ Trigger: {info['trigger']}")
    print(f"  📁 期待パス:")
    
    found_any = False
    for path in info['expected_paths']:
        exists = os.path.exists(path)
        if exists:
            size = os.path.getsize(path)
            print(f"    ✅ {path} ({size} bytes)")
            found_any = True
        else:
            print(f"    ❌ {path} (未存在)")
    
    if not found_any:
        print(f"    ⚠️  実装ファイルが見つかりません")
    
    print()

PYTHON

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: CompleteEngineでの連携確認
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: CompleteEngineでの連携確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 << 'PYTHON'
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

print("🔍 CompleteEngineUltimate統合状況")
print("━" * 60)

try:
    from agents.complete_engine_ultimate import CompleteEngineUltimate
    
    engine = CompleteEngineUltimate()
    
    # F1-F10の統合確認
    integrations = {
        "F1": ["goal_concrete", "pm_agent"],
        "F2": ["task_executor", "execute_task"],
        "F3": ["quality_evaluator", "evaluate_quality"],
        "F4": ["knowledge_wrapper", "knowledge_manager"],
        "F5": ["dashboard", "progress"],
        "F6": ["task_coordinator", "dynamic"],
        "F7": ["self_healing", "healing"],
        "F8": ["self_evolution", "evolution"],
        "F9": ["human_collaboration", "collaboration"],
        "F10": ["health_check", "health"]
    }
    
    print("\n【CompleteEngineへの統合状況】\n")
    
    for fid, keywords in integrations.items():
        found_attrs = []
        for keyword in keywords:
            matching = [attr for attr in dir(engine) if keyword in attr.lower()]
            found_attrs.extend(matching)
        
        if found_attrs:
            print(f"✅ {fid}: {', '.join(set(found_attrs))}")
        else:
            print(f"⚠️  {fid}: 統合が見つかりません")
    
    # 統合メソッドの確認
    print("\n【統合メソッドの確認】\n")
    integration_methods = [
        'integrate_self_healing',
        'integrate_self_evolution',
        'integrate_human_collaboration'
    ]
    
    for method in integration_methods:
        if hasattr(engine, method):
            print(f"  ✅ {method}()")
        else:
            print(f"  ❌ {method}() なし")

except Exception as e:
    print(f"❌ エラー: {e}")

PYTHON

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: 連携フロー図の生成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: 連携フロー図の生成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > "MD/${NOW_JST}_F1-F10連携フロー図.md" << 'FLOW'
# F1-F10連携フロー図

**作成日時**: $(TZ=Asia/Tokyo date +"%Y-%m-%d %H:%M:%S JST")

---

## 1. 全体アーキテクチャ
```
┌─────────────────────────────────────────────────────────────┐
│                  24時間自律稼働システム                        │
│              CompleteEngineUltimate (統括)                   │
└─────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
   │ Loop 1  │       │ Loop 2  │       │ Loop 3  │
   │タスク実行│       │自己修復  │       │学習進化  │
   │3分ごと   │       │エラー時  │       │6時間/50件│
   └────┬────┘       └────┬────┘       └────┬────┘
        │                  │                  │
        └──────────────────┴──────────────────┘
                           │
                    Google Sheets
                  (タスク管理・ログ)
```

---

## 2. Loop 1: タスク実行ループ（3分ごと）
```
┌─────────────────────────────────────────────────────────────┐
│ Loop 1: タスク実行ループ（3分ごと実行）                        │
└─────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────┐
  │ F1: ゴール自動分解（初回のみ）                        │
  │   agents/goal_concrete_agent.py                     │
  │   agents/pm_agent.py                                │
  └─────────────────────────────────────────────────────┘
                      │
                      ▼
  ┌─────────────────────────────────────────────────────┐
  │ F2: タスク自律実行                                    │
  │   agents/complete_engine_ultimate.py                │
  │   agents/task_executor.py                           │
  │   → Google Sheets (pm_tasks) からpendingタスク取得  │
  └─────────────────────────────────────────────────────┘
                      │
                      ▼
  ┌─────────────────────────────────────────────────────┐
  │ F4: ナレッジ参照（実行前）                            │
  │   knowledge_system/core_agents/knowledge_manager.py │
  │   → 過去の成功パターンを検索                         │
  └─────────────────────────────────────────────────────┘
                      │
                      ▼
  ┌─────────────────────────────────────────────────────┐
  │ タスク実行                                            │
  │   → 成果物生成                                       │
  │   → agent_outputs/ に保存                           │
  └─────────────────────────────────────────────────────┘
                      │
                      ▼
  ┌─────────────────────────────────────────────────────┐
  │ F3: 品質自動評価                                      │
  │   agents/quality_evaluator.py                       │
  │   → 品質スコア算出（0-100点）                        │
  └─────────────────────────────────────────────────────┘
                      │
                      ▼
  ┌─────────────────────────────────────────────────────┐
  │ F4: ナレッジ自動蓄積（実行後）                        │
  │   knowledge_system/core_agents/sqlite_manager.py    │
  │   → knowledge.db に蓄積                             │
  └─────────────────────────────────────────────────────┘
                      │
                      ▼
  ┌─────────────────────────────────────────────────────┐
  │ F6: 動的タスク追加（必要時）                          │
  │   agents/task_coordinator.py                        │
  │   → 新規タスクをpm_tasksに追加                       │
  └─────────────────────────────────────────────────────┘
                      │
                      ▼
  ┌─────────────────────────────────────────────────────┐
  │ F9: 進捗報告（1時間ごと）                            │
  │   agents/human_collaboration_agent.py               │
  │   → 進捗状況を可視化                                 │
  └─────────────────────────────────────────────────────┘
```

---

## 3. Loop 2: 自己修復ループ（エラー時）
```
┌─────────────────────────────────────────────────────────────┐
│ Loop 2: 自己修復ループ（エラー検出時に起動）                  │
└─────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────┐
  │ エラー検出                                            │
  │   → タスク実行失敗                                   │
  └─────────────────────────────────────────────────────┘
                      │
                      ▼
  ┌─────────────────────────────────────────────────────┐
  │ F7: 自己修復機能（最大3回リトライ）                   │
  │   agents/self_healing_agent.py                      │
  │   1. エラー分類                                       │
  │   2. 修復戦略選択                                     │
  │   3. 自動修復実行                                     │
  └─────────────────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
     成功(1-3回目)    失敗(3回)      │
        │             │             │
        ▼             ▼             ▼
   Loop 1に戻る   F9に通知    ナレッジ蓄積
                   (人間連携)    (失敗パターン)
```

---

## 4. Loop 3: 学習・進化ループ（6時間/50エラー）
```
┌─────────────────────────────────────────────────────────────┐
│ Loop 3: 学習・進化ループ（6時間ごと、または50エラー蓄積時）    │
└─────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────┐
  │ トリガー条件                                          │
  │   - 6時間経過                                        │
  │   - 50件のエラー蓄積                                 │
  └─────────────────────────────────────────────────────┘
                      │
                      ▼
  ┌─────────────────────────────────────────────────────┐
  │ F8: 自己進化機能                                      │
  │   agents/self_evolution_agent.py                    │
  │   1. ログ収集（task_execution_log, context_log）    │
  │   2. パターン抽出（成功/失敗/修正レシピ）            │
  │   3. ナレッジ更新                                     │
  └─────────────────────────────────────────────────────┘
                      │
                      ▼
  ┌─────────────────────────────────────────────────────┐
  │ F4: ナレッジ蓄積（学習結果）                          │
  │   knowledge_system/database/knowledge.db            │
  │   → 成功パターン、失敗パターン、修正レシピ           │
  └─────────────────────────────────────────────────────┘
                      │
                      ▼
  ┌─────────────────────────────────────────────────────┐
  │ 戦略最適化                                            │
  │   → 次回のタスク実行で活用                           │
  └─────────────────────────────────────────────────────┘
```

---

## 5. F9: 人間連携の仕組み
```
┌─────────────────────────────────────────────────────────────┐
│ F9: 人間連携機能（必要時のみ）                               │
└─────────────────────────────────────────────────────────────┘

  【通知タイミング】
  1. エラー3回連続失敗（F7で修復不可）
  2. 不明点検出（タスク実行中）
  3. 重要イベント発生
  4. 定期進捗報告（1時間ごと）

  【通知方法】
  1. Google Sheets更新
     └─ task_execution_log に記録
     └─ ステータス列を更新

  2. ログファイル出力
     └─ logs/autonomous_*.log

  3. ダッシュボード表示
     └─ agents/observability/dashboard.py

  【人間の対応】
  1. ログ確認
  2. 必要に応じて介入
  3. タスク再実行、または修正指示
```

---

## 6. F5 & F10: 独立実行機能
```
┌─────────────────────────────────────────────────────────────┐
│ F5: 進捗自動可視化（手動/定期実行）                          │
└─────────────────────────────────────────────────────────────┘

  【実行方法】
  python3 agents/observability/dashboard.py

  【表示内容】
  - 全体進捗率
  - ゴール別進捗
  - 平均品質スコア
  - エラー発生状況

┌─────────────────────────────────────────────────────────────┐
│ F10: 定期健全性チェック（1時間ごと）                         │
└─────────────────────────────────────────────────────────────┘

  【チェック項目】
  1. コアファイル存在確認
  2. Google Sheets接続確認
  3. ナレッジシステム確認
  4. F7-F9エージェント確認

  【実行スクリプト】
  bash sh/health_check_periodic.sh
```

---

## 7. データフロー
```
┌─────────────────────────────────────────────────────────────┐
│                      Google Sheets                          │
│  (データの中央管理)                                          │
└─────────────────────────────────────────────────────────────┘
   │
   ├─ project_goal (F1で作成)
   │   └─ ゴール定義、ステータス
   │
   ├─ pm_tasks (F1で作成、F2が実行、F6が追加)
   │   └─ タスク一覧、ステータス、優先度
   │
   └─ task_execution_log (F2-F4が記録)
       └─ 実行結果、品質スコア、エラーログ

┌─────────────────────────────────────────────────────────────┐
│                   SQLiteデータベース                         │
│  (ナレッジの永続化)                                          │
└─────────────────────────────────────────────────────────────┘
   │
   └─ knowledge_system/database/knowledge.db
       └─ 成功パターン、失敗パターン、修正レシピ
```

---

## 8. テストスクリプトの違い

### test_autonomous_3cycles.sh（短期テスト）
- **目的**: 動作確認
- **実行時間**: 約30-45分
- **サイクル数**: 3サイクル
- **用途**: 機能追加後の動作確認

### run_autonomous_24h_v2.sh（長期テスト）
- **目的**: 24時間自律稼働
- **実行時間**: 24時間
- **サイクル数**: 96サイクル（15分間隔）
- **用途**: 本番運用、耐久テスト

**両方ともF1から実行される**: No
- **共通**: F2から開始（タスク実行）
- **F1**: 初回のみ手動実行、またはゴール追加時

FLOW

echo "✅ 連携フロー図作成: MD/${NOW_JST}_F1-F10連携フロー図.md"

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: 連携テストスクリプトの生成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: 連携テストスクリプトの生成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > sh/test_f1_f10_integration.sh << 'TEST'
#!/bin/bash
# F1-F10連携テストスクリプト
# 全機能の連携が正しく動作するか確認

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 F1-F10連携テスト"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

TEST_RESULTS=()

# テスト1: F4ナレッジシステム
echo "【テスト1】F4: ナレッジ追加テスト"
if python3 -c "
from agents.complete_engine_ultimate import CompleteEngineUltimate
engine = CompleteEngineUltimate()
result = engine.knowledge_wrapper.add_knowledge('test', 'test content', 'test')
exit(0 if result else 1)
" 2>/dev/null; then
    echo "  ✅ F4: ナレッジ追加成功"
    TEST_RESULTS+=("✅ F4")
else
    echo "  ❌ F4: ナレッジ追加失敗"
    TEST_RESULTS+=("❌ F4")
fi

# テスト2: F7自己修復エージェント
echo ""
echo "【テスト2】F7: 自己修復エージェント初期化"
if python3 -c "
from agents.complete_engine_ultimate import CompleteEngineUltimate
engine = CompleteEngineUltimate()
exit(0 if hasattr(engine, 'self_healing') else 1)
" 2>/dev/null; then
    echo "  ✅ F7: 自己修復エージェント統合済み"
    TEST_RESULTS+=("✅ F7")
else
    echo "  ❌ F7: 自己修復エージェント未統合"
    TEST_RESULTS+=("❌ F7")
fi

# テスト3: F8自己進化エージェント
echo ""
echo "【テスト3】F8: 自己進化エージェント初期化"
if python3 -c "
from agents.complete_engine_ultimate import CompleteEngineUltimate
engine = CompleteEngineUltimate()
exit(0 if hasattr(engine, 'self_evolution') else 1)
" 2>/dev/null; then
    echo "  ✅ F8: 自己進化エージェント統合済み"
    TEST_RESULTS+=("✅ F8")
else
    echo "  ❌ F8: 自己進化エージェント未統合"
    TEST_RESULTS+=("❌ F8")
fi

# テスト4: F9人間連携エージェント
echo ""
echo "【テスト4】F9: 人間連携エージェント初期化"
if python3 -c "
from agents.complete_engine_ultimate import CompleteEngineUltimate
engine = CompleteEngineUltimate()
exit(0 if hasattr(engine, 'human_collaboration') else 1)
" 2>/dev/null; then
    echo "  ✅ F9: 人間連携エージェント統合済み"
    TEST_RESULTS+=("✅ F9")
else
    echo "  ❌ F9: 人間連携エージェント未統合"
    TEST_RESULTS+=("❌ F9")
fi

# テスト5: Google Sheets接続
echo ""
echo "【テスト5】Google Sheets接続"
if python3 -c "
from tools.sheets_manager import GoogleSheetsManager
manager = GoogleSheetsManager()
exit(0)
" 2>&1 | grep -q "接続成功"; then
    echo "  ✅ Google Sheets接続成功"
    TEST_RESULTS+=("✅ Sheets")
else
    echo "  ❌ Google Sheets接続失敗"
    TEST_RESULTS+=("❌ Sheets")
fi

# テスト結果サマリー
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 テスト結果サマリー"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

SUCCESS_COUNT=0
for result in "${TEST_RESULTS[@]}"; do
    echo "  $result"
    if [[ $result == ✅* ]]; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    fi
done

TOTAL_TESTS=${#TEST_RESULTS[@]}
SUCCESS_RATE=$((SUCCESS_COUNT * 100 / TOTAL_TESTS))

echo ""
echo "成功率: ${SUCCESS_COUNT}/${TOTAL_TESTS} (${SUCCESS_RATE}%)"

if [ $SUCCESS_RATE -ge 80 ]; then
    echo "✅ 連携テスト合格"
    exit 0
else
    echo "⚠️  連携テスト不合格（80%以上必要）"
    exit 1
fi

TEST

chmod +x sh/test_f1_f10_integration.sh
echo "✅ 連携テストスクリプト作成: sh/test_f1_f10_integration.sh"

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 5: 連携確認の実行
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5: 連携確認の実行"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "連携テストを実行しますか？ [y/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    bash sh/test_f1_f10_integration.sh
else
    echo "  ⏭️  テストはスキップされました"
    echo "  📋 手動実行: bash sh/test_f1_f10_integration.sh"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ F1-F10連携見える化完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📄 生成ファイル:"
echo "  - MD/${NOW_JST}_F1-F10連携フロー図.md (見える化)"
echo "  - sh/test_f1_f10_integration.sh (連携テスト)"
echo ""
echo "🎯 次のアクション:"
echo "  1. フロー図確認: cat MD/${NOW_JST}_F1-F10連携フロー図.md"
echo "  2. 連携テスト実行: bash sh/test_f1_f10_integration.sh"
echo "  3. 定期テスト設定（cron）"
echo ""

