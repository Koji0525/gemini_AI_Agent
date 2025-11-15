# 【既存システム保護型】マスターロードマップ v4.5

**最終更新**: 2025-11-14  
**総合実装率**: 92.7%  
**目標**: 既存システム保護型 要件定義書ver4.5 完全達成

---

## 📊 1. 進捗チェックシート（単一管理点）

### 全体KPI
| 指標 | 現状 | 目標 | 差分 | コンテキスト |
|------|------|------|------|--------------|
| **総合実装率** | 92.7% | 100% | +7.3% | あと4個の課題で完全達成 |
| **品質評価率** | 33.7% | 90%+ | +56.3% | スコア0が163/246件（原因: QualityEvaluatorのキー名不一致） |
| **テスト成功率** | 100% | 84.3%+ | ✅達成 | 既存システム破壊なし（5回に1回監視済み） |
| **タスク完了率** | 87.9% | 95%+ | +7.1% | 94/107タスク完了、13タスク残存 |
| **ナレッジ蓄積** | 432KB | 継続増加 | - | knowledge.db正常、527件蓄積済み |

### F1-F10機能別実装率
| 機能 | 実装率 | ステータス | 実装ファイル | 課題 |
|------|--------|-----------|-------------|------|
| **F0: ゴールの具体化** | 100% | ✅完了 | `agents/goal_concrete_agent.py` | なし |
| **F1: ゴール自動分解** | 100% | ✅完了 | `agents/complete_engine_ultimate.py` | なし |
| **F2: タスク自律実行** | 75% | ⚠️改善中 | `agents/complete_engine_ultimate.py::execute_task()` | 具体的作業内容の記録不足 |
| **F3: 品質自動評価** | 66.7% | ⚠️改善中 | `agents/quality_evaluator.py` | スコア0問題（キー名: overall_score vs quality_score） |
| **F4: ナレッジ自動蓄積** | 50% | ⚠️改善中 | `knowledge_system/simple_knowledge_wrapper.py` | FAISSインデックス未保存、register_knowledge未実装 |
| **F5: 進捗自動可視化** | 50% | ⚠️改善中 | `agents/observability/progress_dashboard.py` | タイムアウト問題、不足項目検出未実装 |
| **F6: 動的タスク追加** | 100% | ✅完了 | `agents/complete_engine_ultimate.py::generate_additional_tasks()` | なし |
| **F7: 自己修復機能** | 100% | ✅完了 | `agents/self_healing_agent.py` | 実戦投入待ち |
| **F8: 自己進化機能** | 100% | ✅完了 | `agents/self_evolution_agent.py` | 実戦投入待ち |
| **F9: 人間連携機能** | 100% | ✅完了 | `agents/human_collaboration_agent.py` | 実戦投入待ち |
| **F10: 健全性チェック** | 100% | ✅完了 | `agents/health_check_agent.py` | 実戦投入待ち |

---

## 🏗️ 2. システム全体構成図

### ファイル構造（実装ベース）
```
/workspaces/gemini_AI_Agent/
├── 【コアエンジン】
│   ├── agents/complete_engine_ultimate.py          [F1,F2,F6統合] ★触るな
│   ├── agents/autonomous_engine.py                 [既存エンジン] ★触るな
│   └── run_3_cycles.py                             [3周実行スクリプト] ★触るな
│
├── 【品質評価】
│   └── agents/quality_evaluator.py                 [F3] 要修正
│
├── 【ナレッジシステム】
│   ├── knowledge_system/
│   │   ├── database/
│   │   │   ├── knowledge.db                        [432KB, 527件] ★触るな
│   │   │   └── faiss_index.bin                     [未作成] 要作成
│   │   ├── simple_knowledge_wrapper.py             [F4] 要修正
│   │   └── core_agents/knowledge_manager.py        ★触るな
│
├── 【可視化・診断】
│   ├── agents/observability/progress_dashboard.py  [F5] 要修正
│   ├── show_goal_progress.py                       [ゴール別進捗] ★触るな
│   ├── goal_achievement_roadmap.py                 [達成ロードマップ] ★触るな
│   └── verify_implementation.py                    [実装確認] ★触るな
│
├── 【自己修復・進化】
│   ├── agents/self_healing_agent.py                [F7] ★触るな
│   ├── agents/self_evolution_agent.py              [F8] ★触るな
│   ├── agents/human_collaboration_agent.py         [F9] ★触るな
│   └── agents/health_check_agent.py                [F10] ★触るな
│
├── 【データアクセス】
│   ├── tools/base_data_accessor.py                 [Sheets読み書き] ★触るな
│   ├── tools/sheets_manager.py                     [Sheets API] ★触るな
│   └── tools/safe_sheets_wrapper.py                [安全ラッパー] ★触るな
│
└── 【出力】
    └── agent_outputs/                              [78ファイル] ★触るな
```

### 依存関係図
```
run_3_cycles.py
    └─→ CompleteEngineUltimate (complete_engine_ultimate.py)
            ├─→ SimpleKnowledgeWrapper (F4)
            ├─→ QualityEvaluator (F3)
            ├─→ SelfHealingAgent (F7)
            ├─→ SelfEvolutionAgent (F8)
            ├─→ HumanCollaborationAgent (F9)
            ├─→ HealthCheckAgent (F10)
            └─→ BaseDataAccessor
                    └─→ Google Sheets API
                            ├─→ project_goal (6行)
                            ├─→ pm_tasks (107行)
                            └─→ task_execution_log (246行)
```

---

## 🎯 3. Phase別実装計画

### 【Phase 1: 緊急】[推定1-2サイクル, 2-4時間]

#### 1-1. F3: 品質スコア記録修正 ⚠️CRITICAL

**なぜ課題か**: 品質評価率33.7%（目標90%）で、163/246件がスコア0。原因はQualityEvaluatorが返す`overall_score`を`quality_score`として取得しようとしているキー名の不一致。

**実装ファイル**: 
- `agents/complete_engine_ultimate.py` (行490-510付近)
- `agents/quality_evaluator.py` (返り値確認)

**修正内容**:
```python
# 修正前
quality_score = quality_result.get('quality_score', 0)

# 修正後
quality_score = quality_result.get('overall_score', quality_result.get('quality_score', 0)) / 10
```

**達成基準**:
- ✅ Quality_Scoreが0以外で記録される（90%以上）
- ✅ 品質評価率が90%以上になる
- ✅ 最新10件のログで正常なスコアを確認

**検証コマンド**:
```bash
python3 -c "from tools.base_data_accessor import BaseDataAccessor; a = BaseDataAccessor(); logs = a.read_sheet_as_dicts('task_execution_log'); q = [l for l in logs if l.get('Quality_Score') and float(l.get('Quality_Score', 0)) > 0]; print(f'{len(q)/len(logs)*100:.1f}%')"
```

---

#### 1-2. F2: タスク実行内容の具体化 ⚠️CRITICAL

**なぜ課題か**: 現在の実行結果は「タスク実行完了: task_id\n説明: description」という抽象的な出力のみ。実際のファイル作成、コマンド実行、データ処理などの具体的な作業が行われていない。これでは10/10件が抽象的と判定されている。

**実装ファイル**: 
- `agents/complete_engine_ultimate.py::execute_task()` (行395-425付近)

**修正内容**:
1. タスクタイプ別の実行ロジック追加:
```python
def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
    """タスク実行（具体的な作業を実行）"""
    task_id = task.get('task_id', 'UNKNOWN')
    exec_type = task.get('execution_type', 'general')
    
    # タスクタイプ別の具体的実行
    if exec_type == 'research':
        result = self._execute_research(task)
    elif exec_type == 'design':
        result = self._execute_design(task)
    elif exec_type == 'implementation':
        result = self._execute_implementation(task)
    # ... 他のタイプ
    
    # 実行結果をファイルに保存
    output_file = f"agent_outputs/{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    return result
```

**達成基準**:
- ✅ agent_outputs/に実行結果ファイルが作成される
- ✅ output_dataに200文字以上の具体的内容が記録される
- ✅ 最新10件中5件以上が具体的と判定される

**検証コマンド**:
```bash
ls -lh /workspaces/gemini_AI_Agent/agent_outputs/ | tail -5
```

---


#### 1-3. 進捗計算の正確化 ⚠️HIGH

**課題**: ステータスだけで進捗を計算しているため、実際の成果物がなくても100%になる

**実態**: ゴール6は進捗100%と表示されているが、実際のツールは作られていない

**対策**:
1. 進捗計算に品質スコアと成果物の有無を含める
2. 実完了の定義: 品質スコア6点以上 + 出力200文字以上 + 構造化
3. calculate_real_progress.pyを使用した正確な進捗計算

**達成基準**:
- ✅ 実進捗と表示進捗が一致する
- ✅ 成果物がないタスクは未完了扱い

---

### 【Phase 2: 重要】[推定2-3サイクル, 4-6時間]

#### 2-1. F4: ナレッジシステムの完全統合 ⚠️HIGH

**なぜ課題か**: 
1. FAISSインデックスが未保存（検索は動作するが、永続化されていない）
2. `register_knowledge`メソッドが未実装（ナレッジ追加ができない）

この2つが欠けていると、システム再起動時にナレッジが失われたり、新規ナレッジの蓄積ができない。

**実装ファイル**: 
- `knowledge_system/simple_knowledge_wrapper.py`

**修正内容**:
1. FAISSインデックス保存機能追加:
```python
def save_faiss_index(self):
    """FAISSインデックスをディスクに保存"""
    index_path = Path(self.db_path).parent / 'faiss_index.bin'
    faiss.write_index(self.faiss_index, str(index_path))
```

2. register_knowledge実装:
```python
def register_knowledge(self, title: str, content: str, category: str = 'general') -> str:
    """ナレッジ登録"""
    entry_id = f"kb_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # DB登録
    self.db.execute(
        "INSERT INTO knowledge (entry_id, title, content, category) VALUES (?, ?, ?, ?)",
        (entry_id, title, content, category)
    )
    
    # FAISSインデックス更新
    embedding = self.model.encode([content])
    self.faiss_index.add(embedding)
    self.save_faiss_index()
    
    return entry_id
```

**達成基準**:
- ✅ FAISSインデックスファイルが作成される（knowledge_system/database/faiss_index.bin）
- ✅ register_knowledgeでナレッジ追加ができる
- ✅ システム再起動後も検索が動作する

**検証コマンド**:
```bash
python3 -c "from knowledge_system.simple_knowledge_wrapper import SimpleKnowledgeWrapper; w = SimpleKnowledgeWrapper(); w.register_knowledge('test', 'テスト内容', 'test'); print('OK')"
```

---

### 【Phase 3: 中優先】[推定2-3サイクル, 4-6時間]

#### 3-1. F5: 可視化機能の完全実装 ⚠️MEDIUM

**なぜ課題か**:
1. ダッシュボードがタイムアウトする（10秒で終わらない）→ 重い処理が原因
2. 不足項目自動検出が未実装→ 各ゴールの必須タスクタイプ（research/design/implementation/test/quality/doc）が揃っているかチェックできない

**実装ファイル**: 
- `agents/observability/progress_dashboard.py`

**修正内容**:
1. タイムアウト修正（重い処理の最適化）:
```python
# シート読み込みをキャッシュ
@lru_cache(maxsize=1)
def get_cached_data():
    return accessor.read_sheet_as_dicts('task_execution_log')
```

2. 不足項目検出追加:
```python
def detect_missing_task_types(goal_id: str) -> List[str]:
    """ゴールの不足タスクタイプを検出"""
    required_types = ['research', 'design', 'implementation', 'test', 'quality_improvement', 'documentation']
    
    tasks = accessor.read_sheet_as_dicts('pm_tasks', filter_func=lambda t: t.get('parent_goal_id') == goal_id)
    existing_types = set(t.get('execution_type') for t in tasks)
    
    missing = [t for t in required_types if t not in existing_types]
    return missing
```

**達成基準**:
- ✅ ダッシュボードが10秒以内に実行完了
- ✅ 各ゴールの不足タイプが表示される
- ✅ F5実装率が100%になる

**検証コマンド**:
```bash
timeout 10 python3 /workspaces/gemini_AI_Agent/agents/observability/progress_dashboard.py
```

---

## 🛡️ 4. 既存システム保護リスト

### 絶対に触ってはいけないファイル（★触るな）

| ファイル | 理由 | テスト成功率 |
|---------|------|-------------|
| `agents/autonomous_engine.py` | 既存エンジン、全機能の基盤 | 100% |
| `tools/base_data_accessor.py` | Sheets操作の全基盤 | 100% |
| `tools/sheets_manager.py` | API接続の核 | 100% |
| `tools/safe_sheets_wrapper.py` | 安全性保証 | 100% |
| `knowledge_system/database/knowledge.db` | 432KB/527件のナレッジ | - |
| `agent_outputs/*` | 78ファイルの実行結果 | - |
| `run_3_cycles.py` | 3周実行の確立されたフロー | 100% |

### 修正可能だが注意が必要なファイル

| ファイル | 修正範囲 | 注意点 |
|---------|---------|--------|
| `agents/complete_engine_ultimate.py` | execute_task(), save_to_execution_log() のみ | 他のメソッドは触らない |
| `agents/quality_evaluator.py` | 返り値のキー名確認のみ | ロジック変更禁止 |
| `knowledge_system/simple_knowledge_wrapper.py` | register_knowledge追加、save_faiss_index追加 | 既存メソッドは触らない |
| `agents/observability/progress_dashboard.py` | キャッシュ追加、detect_missing_task_types追加 | 既存表示ロジックは触らない |

---

## 🔬 5. 定期診断システム

### 5-1. システム破壊検知スクリプト

**実行頻度**: 5回に1回の実装後、または毎日1回

**診断項目**:
1. ✅ 既存ファイルの存在確認
2. ✅ 構文エラーチェック（py_compile）
3. ✅ インポートテスト
4. ✅ テスト成功率確認（84.3%以上）
5. ✅ データ整合性確認（Sheets接続、DB接続）

**診断コマンド**:
```bash
python3 /workspaces/gemini_AI_Agent/system_health_check.py
```

### 5-2. 診断結果の可視化

診断結果は以下に記録:
- `診断ログ`: `logs/health_check_YYYYMMDD_HHMMSS.json`
- `ダッシュボード`: `agents/observability/progress_dashboard.py`

---

## 🤖 6. AI引継ぎ用コンテキスト

### 開発の背景と意図

**このシステムの目的**:
- 24時間自律稼働するAIエージェントシステムの構築
- 人間の介入頻度: 1回/2-3日が目標
- 既存システムを破壊せず、機能を積み上げ式に追加

**重要な設計判断**:
1. **なぜGoogle Sheetsを使うのか**: 人間が直接確認・編集できる透明性が必要だから
2. **なぜ品質評価率90%が目標なのか**: 低品質タスクを自動で改善するループを回すため（現状33.7%では改善ループが機能しない）
3. **なぜテスト成功率84.3%が基準なのか**: 過去の分析で、この水準を下回ると既存機能が破壊される可能性が高いと判明したため
4. **なぜF7-F10が実戦投入待ちなのか**: ファイルは作成済みだが、CompleteEngineUltimateとの統合が完了していないため

**過去の失敗と学習**:
- ❌ 失敗1: ファイルの一括書き換えで既存機能が破壊された → 対策: ★触るなリスト作成
- ❌ 失敗2: 品質スコアのキー名不一致でスコアが0になった → 対策: Phase 1-1で修正予定
- ❌ 失敗3: ダッシュボードのタイムアウト → 対策: Phase 3-1でキャッシュ追加予定

---

## 📅 7. マイルストーン

| Week | Phase | 目標 | KPI | 完了条件 |
|------|-------|------|-----|---------|
| **Week 1** (現在) | Phase 1 | 品質評価率90%達成 | 90%以上 | F3修正完了、最新100件で確認 |
| **Week 2** | Phase 2 | ナレッジシステム完全統合 | F4実装率100% | FAISSインデックス作成、register_knowledge動作 |
| **Week 3** | Phase 3 | 可視化機能完全実装 | F5実装率100% | ダッシュボード10秒以内、不足検出動作 |
| **Week 4** | 実戦投入 | F7-F10の実戦投入 | 人間介入1回/2日 | 3日間の自律稼働成功 |

---

## 🚀 8. 実行コマンド一覧

### 日常実行
```bash
# 3周実行（メイン）
python3 /workspaces/gemini_AI_Agent/run_3_cycles.py

# 進捗確認
python3 /workspaces/gemini_AI_Agent/goal_achievement_roadmap.py

# ダッシュボード
python3 /workspaces/gemini_AI_Agent/agents/observability/progress_dashboard.py
```

### 診断・確認
```bash
# システム健全性チェック
python3 /workspaces/gemini_AI_Agent/system_health_check.py

# 実装状況確認
python3 /workspaces/gemini_AI_Agent/verify_implementation.py

# 品質評価率確認
python3 -c "from tools.base_data_accessor import BaseDataAccessor; a = BaseDataAccessor(); logs = a.read_sheet_as_dicts('task_execution_log'); q = [l for l in logs if l.get('Quality_Score') and float(l.get('Quality_Score', 0)) > 0]; print(f'{len(q)/len(logs)*100:.1f}%')"
```

### Phase別実装
```bash
# Phase 1開始
python3 /workspaces/gemini_AI_Agent/implement_phase1.py

# Phase 2開始
python3 /workspaces/gemini_AI_Agent/implement_phase2.py

# Phase 3開始
python3 /workspaces/gemini_AI_Agent/implement_phase3.py
```

---

## �� 9. 更新履歴

| 日付 | 更新者 | 変更内容 | 実装率変化 |
|------|--------|---------|-----------|
| 2025-11-14 | Kazuhiko | 初版作成 | 92.7% |
| 2025-11-14 | AI | Phase 1実装（F3,F2修正） | 33.7% |
| 2025-11-14 | AI | F0追加（ゴール具体化） | - |
| 2025-11-14 | AI | 統合完了（進捗計算+会話機能） | - |
| - | - | - | - |

---

## ✅ 10. 完了チェックリスト

### Phase 1（緊急）
- [ ] F3: 品質スコア記録修正完了
- [ ] F2: タスク実行内容の具体化完了
- [ ] 品質評価率90%達成確認
- [ ] システム健全性チェック実施（テスト成功率100%）

### Phase 2（重要）
- [ ] F4: FAISSインデックス保存実装
- [ ] F4: register_knowledge実装
- [ ] F4実装率100%達成確認
- [ ] ナレッジ検索・登録の動作確認

### Phase 3（中）
- [ ] F5: ダッシュボードタイムアウト修正
- [ ] F5: 不足項目自動検出実装
- [ ] F5実装率100%達成確認
- [ ] ダッシュボード10秒以内実行確認

### 最終確認
- [ ] 総合実装率100%達成
- [ ] テスト成功率84.3%以上維持
- [ ] 3日間の自律稼働成功
- [ ] 人間介入頻度1回/2日達成

---

**このロードマップは常に最新の状態に保ち、AI・人間の両方がこのファイル1つを参照すれば開発の全体像と進捗が把握できるようにします。**
