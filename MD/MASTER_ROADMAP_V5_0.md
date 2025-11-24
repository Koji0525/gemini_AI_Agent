251125🗺️ 統合マスターロードマップ ver5.0

**最終更新**: 2025-11-25  
**対象期間**: Phase 0（現状確認）→ Phase 6（完全自律稼働）  
**開発方式**: 既存システム保護型・積み上げ式開発  
**進捗管理**: `MD/PROGRESS_CHECKLIST.md` 単一ファイルで一元管理

---

## 📊 プロジェクト全体概要

### 現状（Phase 0: F1-F10実装済み）
```
【既存システムの状態】2025-11-25時点
総合評価: 78.2/100点
実装済み機能: F1-F10（10機能）
ファイル数: 47件
総コード行数: 12,847行
テスト成功率: 84.3%（基準値：これを下回らない）
ナレッジDB: 511件
API成功率: 95.9%

【既存コアファイル】
1. tools/sheets_manager.py (645行)
2. tools/safe_sheets_wrapper.py (312行)
3. tools/base_data_accessor.py (288行)
4. core_agents/pm_agent_v3_fixed.py (423行)
5. agents/complete_engine_ultimate.py (387行)
6. knowledge_system/core_agents/knowledge_manager.py (456行)
... 他41件
```

### 目標（Phase 6完了時）
```
【ver5.0完成時の状態】
総合評価: 90/100点（+11.8点向上）
実装済み機能: F1-F14（14機能）
ファイル数: 54件（+7件新規）
総コード行数: 20,747行（+7,900行追加）
テスト成功率: 90%以上（+5.7%向上）
エージェント生成能力: 5万~10万行規模
統合成功率: 95%以上
Epic処理能力: 1Epic/60秒
```

### なぜこの目標か（コンテキスト）
```
【課題1】コード生成規模の限界
現状: 1タスク=200-400行が限界
理由: Gemini max_tokens=20,000の制約
影響: 大規模エージェント（5万行）が作れない
解決: max_tokens=32,000 + 3層構造で5万~10万行生成可能に

【課題2】統合作業の手動化
現状: 複数タスクの統合が手動作業
理由: 統合機能（F11-F14）が未実装
影響: 統合ミス・重複コード・import漏れ
解決: 自動統合機能で95%以上の成功率

【課題3】進捗管理の複雑化
現状: タスク単位でしか管理できない
理由: Epic/Story/Sub-taskの3層構造未対応
影響: 大規模開発の全体像が見えない
解決: 3層構造+F11で全体進捗の可視化
```

---

## 🎯 Phase別ロードマップ

### Phase 0: 現状確認・診断【2時間】

**目的**: 既存システムの健全性確認と基準値の記録

#### M0.1: 既存システム診断
```
【タスク】
□ T0.1.1: 既存テスト実行・成功率測定
  実行コマンド: pytest tests/ -v --tb=short
  実行ファイル: sh/diagnose_existing_system.sh
  基準値: 84.3%以上であることを確認
  記録先: MD/PROGRESS_CHECKLIST.md
  所要時間: 30分
  
  【なぜ84.3%か】
  - 現在の安定稼働時の成功率
  - これを下回ると既存機能に問題発生
  - 新機能追加の前提条件

□ T0.1.2: 既存ファイル一覧の記録
  実行コマンド: sh/list_existing_files.sh
  対象: 全47件のPythonファイル
  記録形式: ファイルパス、行数、最終更新日
  記録先: MD/EXISTING_FILES_BASELINE.md
  所要時間: 10分
  
  【なぜ必要か】
  - 新規ファイルと既存ファイルを明確に区別
  - 誤って既存ファイルを上書きしない
  - 依存関係の追跡

□ T0.1.3: API成功率の測定
  実行コマンド: sh/measure_api_success_rate.sh
  対象API: Google Sheets API、Gemini API
  基準値: 95.9%以上
  記録先: MD/PROGRESS_CHECKLIST.md
  所要時間: 20分

□ T0.1.4: ナレッジDB統計の記録
  実行コマンド: python3 -c "from knowledge_system.core_agents.knowledge_manager import KnowledgeManager; km = KnowledgeManager(); print(km.get_statistics())"
  基準値: 511件以上
  記録先: MD/PROGRESS_CHECKLIST.md
  所要時間: 5分

【完了条件】
✅ すべてのテストが84.3%以上で成功
✅ 既存47件のファイルリストが記録済み
✅ API成功率が95.9%以上
✅ ナレッジDB統計が記録済み
✅ MD/PROGRESS_CHECKLIST.md に基準値を記録

【出力ファイル】
- MD/EXISTING_FILES_BASELINE.md
- MD/PROGRESS_CHECKLIST.md（更新）
```

---

### Phase 1: PMAgent v33 Epic実装【1週間】

**目的**: Epic分解機能の実装（F1拡張）

#### M1.1: PMAgent v33 Epic基本実装
```
【タスク】
□ T1.1.1: EpicTaskGeneratorクラス実装
  新規ファイル: core_agents/pm_agent_v33_epic.py (1,500行)
  実装内容:
    - max_tokens=32,000設定
    - Epic→Story分解ロジック
    - 2,500-3,000文字のStory説明生成
  依存: 既存 tools/sheets_manager.py
  テスト: tests/test_pm_agent_v33_epic.py (新規作成)
  所要時間: 2日
  
  【なぜmax_tokens=32,000か】
  - Gemini 2.5-flashの最大値
  - 1回で600-900行生成可能
  - 10個のStory定義を1回で生成

□ T1.1.2: Epicプロンプト設計
  実装メソッド: _create_epic_breakdown_prompt()
  プロンプト文字数: 3,000-4,000文字
  出力: 10個のStory × 2,500-3,000文字
  検証: 実際のEpicで生成テスト
  所要時間: 1日
  
  【なぜ2,500-3,000文字か】
  - 統合要件(400文字)を含む詳細度
  - テスト要件(400文字)を含む
  - サブタスク分解指針(300文字)を含む
  - 合計10項目で約2,600文字

□ T1.1.3: ナレッジ連携実装
  実装メソッド: _search_knowledge(), _format_knowledge_context()
  連携先: knowledge_system/core_agents/knowledge_manager.py（既存）
  検索数: 5件まで
  所要時間: 0.5日

□ T1.1.4: SafeSheetsWrapper連携
  実装メソッド: write_stories_to_sheet()
  連携先: tools/safe_sheets_wrapper.py（既存）
  書き込み先: pm_tasksシート
  フォーマット: 13列のスキーマ準拠
  所要時間: 0.5日

【完了条件】
✅ core_agents/pm_agent_v33_epic.py が作成済み（1,500行）
✅ テストファイル tests/test_pm_agent_v33_epic.py が作成済み
✅ テスト成功率 84.3%以上を維持
✅ Epic分解テスト（10 Stories生成）が成功
✅ 各Story説明が2,500-3,000文字
✅ pm_tasksシートへの書き込み成功

【診断コマンド】
sh/diagnose_phase1.sh
  - PMAgent v33のインポート確認
  - テスト実行
  - Story生成文字数の検証
  - 既存テスト成功率の確認

【出力ファイル】
- core_agents/pm_agent_v33_epic.py（新規）
- tests/test_pm_agent_v33_epic.py（新規）
- MD/PROGRESS_CHECKLIST.md（更新）
```

#### M1.2: Epic分解テスト
```
【タスク】
□ T1.2.1: 単体テスト作成
  テストケース数: 10件
  カバレッジ目標: 90%以上
  テスト内容:
    - TC-EPIC-001: Epic分解基本動作
    - TC-EPIC-002: Story説明文字数検証
    - TC-EPIC-003: 依存関係の正確性
    - TC-EPIC-004: max_tokens=32,000動作確認
    - TC-EPIC-005: ナレッジ連携動作
    - TC-EPIC-006: pm_tasks書き込み検証
    - TC-EPIC-007: エラーハンドリング
    - TC-EPIC-008: リトライ機能
    - TC-EPIC-009: JSON解析精度
    - TC-EPIC-010: 既存システムへの影響なし
  所要時間: 1日

□ T1.2.2: 統合テスト
  実Epic使用: AIデューデリジェンスエージェント（10,000行）
  検証項目:
    - 10個のStory生成
    - 各Story 2,500-3,000文字
    - pm_tasksへの正常書き込み
    - 既存テスト成功率 84.3%以上維持
  所要時間: 0.5日

□ T1.2.3: 性能テスト
  測定項目:
    - Epic分解時間: 目標<60秒
    - メモリ使用量: 目標<600MB
    - API呼び出し回数: 1回/Epic
  所要時間: 0.5日

【完了条件】
✅ 単体テスト10件すべて成功
✅ 統合テスト成功
✅ Epic分解時間<60秒
✅ 既存テスト成功率 84.3%以上維持
✅ カバレッジ90%以上

【診断コマンド】
pytest tests/test_pm_agent_v33_epic.py -v --cov=core_agents/pm_agent_v33_epic --cov-report=term

【出力ファイル】
- MD/PROGRESS_CHECKLIST.md（更新）
- MD/PHASE1_TEST_RESULTS.md（テスト結果詳細）
```

---

### Phase 2: TaskExecutor v4 Sub-task実装【2週間】

**目的**: Story→Sub-task分解・実行機能（F2拡張）

#### M2.1: Sub-task分解機能実装
```
【タスク】
□ T2.1.1: SubTaskDecomposerクラス実装
  新規ファイル: agents/task_executor_v4_subtask.py (2,000行)
  実装内容:
    - Story→3-5個のSub-task分解
    - 各Sub-task: 200-400行の目標設定
    - サブタスク分解プロンプト設計
  依存: core_agents/pm_agent_v33_epic.py（Phase 1）
  テスト: tests/test_task_executor_v4.py（新規）
  所要時間: 3日
  
  【なぜ3-5個のSub-taskか】
  - 1Story=500-1,500行を分割
  - 各Sub-task=200-400行
  - 500÷400=1.25、1500÷200=7.5
  - 実用的な範囲として3-5個

□ T2.1.2: Gemini呼び出し最適化
  実装メソッド: _generate_subtask_code()
  max_tokens: 32,000
  目標生成行数: 600-900行/回
  リトライ: 最大3回（指数バックオフ）
  所要時間: 2日
  
  【なぜ600-900行か】
  - max_tokens=32,000の実測値
  - 安全マージン考慮
  - コメント・ドキュメント含む

□ T2.1.3: Sub-task結果のメモリ管理
  実装: 辞書形式でメモリ保持
  構造: {sub_task_1: {code: str, metadata: dict}, ...}
  統合準備: F12へのデータ受け渡し
  所要時間: 1日

□ T2.1.4: 既存RealExecutorとの統合
  既存ファイル: agents/task_execution/real_executor.py
  統合方法: v4をラッパーとして実装
  後方互換性: 既存のexecute_task()を維持
  所要時間: 2日

【完了条件】
✅ agents/task_executor_v4_subtask.py が作成済み（2,000行）
✅ Sub-task分解が正常動作
✅ 各Sub-taskが600-900行生成
✅ メモリ管理が正常動作
✅ 既存RealExecutorとの統合成功
✅ テスト成功率 84.3%以上維持

【診断コマンド】
sh/diagnose_phase2.sh
  - TaskExecutor v4のインポート確認
  - Sub-task分解テスト
  - 生成行数の検証
  - 既存テスト成功率の確認

【出力ファイル】
- agents/task_executor_v4_subtask.py（新規）
- tests/test_task_executor_v4.py（新規）
- MD/PROGRESS_CHECKLIST.md（更新）
```

#### M2.2: Sub-task実行テスト
```
【タスク】
□ T2.2.1: 単体テスト作成
  テストケース数: 15件
  カバレッジ目標: 90%以上
  所要時間: 2日

□ T2.2.2: 統合テスト（Story実行）
  実Story使用: Phase 1で生成したStory
  検証: 3-5個のSub-task生成→実行→統合
  所要時間: 1日

□ T2.2.3: 性能テスト
  測定項目:
    - Sub-task分解時間: 目標<5秒
    - Sub-task実行時間: 目標<3分/個
    - Story完了時間: 目標<20分
  所要時間: 1日

【完了条件】
✅ 単体テスト15件すべて成功
✅ 統合テスト成功
✅ 性能目標達成
✅ 既存テスト成功率 84.3%以上維持
✅ カバレッジ90%以上

【診断コマンド】
pytest tests/test_task_executor_v4.py -v --cov=agents/task_executor_v4_subtask

【出力ファイル】
- MD/PROGRESS_CHECKLIST.md（更新）
- MD/PHASE2_TEST_RESULTS.md
```

---

### Phase 3: 統合機能F11-F14実装【2週間】

**目的**: 自動統合・依存解決・テスト機能

#### M3.1: F11 進捗分析実装
```
【タスク】
□ T3.1.1: ProgressAnalyzerV2クラス実装
  新規ファイル: agents/integration/progress_analyzer_v2.py (800行)
  実装内容:
    - Story完了度計算
    - 不足コンポーネント検出
    - 統合準備状況判定
  依存: agents/task_executor_v4_subtask.py（Phase 2）
  テスト: tests/integration/test_progress_analyzer.py（新規）
  所要時間: 2日
  
  【なぜ完了度計算が必要か】
  - 大規模開発の進捗が見えない
  - どのコンポーネントが未完成か不明
  - 統合タイミングの判断材料

□ T3.1.2: ギャップ分析アルゴリズム
  実装メソッド: detect_missing_components()
  検出項目:
    - 未実装クラス
    - 未実装メソッド
    - 未実装テスト
  精度目標: 90%以上
  所要時間: 1日

□ T3.1.3: Dashboard連携
  既存ファイル: agents/observability/dashboard.py
  追加表示: Epic進捗率、Story完了度、ギャップ一覧
  所要時間: 1日

【完了条件】
✅ agents/integration/progress_analyzer_v2.py 作成済み（800行）
✅ ギャップ検出率90%以上
✅ Dashboard表示成功
✅ テスト成功率 84.3%以上維持

【出力ファイル】
- agents/integration/progress_analyzer_v2.py（新規）
- tests/integration/test_progress_analyzer.py（新規）
```

#### M3.2: F12 コード統合実装
```
【タスク】
□ T3.2.1: CodeIntegratorV2クラス実装
  新規ファイル: agents/integration/code_integrator_v2.py (1,200行)
  実装内容:
    - Sub-taskファイル結合
    - import文の統合・重複削除
    - クラス・関数の統合
  依存: agents/task_executor_v4_subtask.py（Phase 2）
  テスト: tests/integration/test_code_integrator.py（新規）
  所要時間: 3日
  
  【なぜimport文の統合が必要か】
  - Sub-taskごとに重複したimport
  - 統合時にimport順序の問題
  - 未使用importの削除

□ T3.2.2: ファイル結合アルゴリズム
  実装メソッド: merge_files()
  結合順序: 依存関係に基づく
  衝突解決: 命名規則に基づく
  所要時間: 2日

□ T3.2.3: 統合テスト
  統合成功率目標: 95%以上
  テストケース: 20件
  所要時間: 1日

【完了条件】
✅ agents/integration/code_integrator_v2.py 作成済み（1,200行）
✅ 統合成功率95%以上
✅ import文解決率98%以上
✅ テスト成功率 84.3%以上維持

【出力ファイル】
- agents/integration/code_integrator_v2.py（新規）
- tests/integration/test_code_integrator.py（新規）
```

#### M3.3: F13 依存関係解決実装
```
【タスク】
□ T3.3.1: DependencyResolverV2クラス実装
  新規ファイル: agents/integration/dependency_resolver_v2.py (600行)
  実装内容:
    - import文の自動追加
    - 循環依存の検出
    - 未定義変数の検出
  依存: agents/integration/code_integrator_v2.py（M3.2）
  テスト: tests/integration/test_dependency_resolver.py（新規）
  所要時間: 2日
  
  【なぜ循環依存検出が重要か】
  - 循環依存はImportErrorを引き起こす
  - 大規模コードで見落としやすい
  - 統合後の実行時エラーの主因

□ T3.3.2: import文自動追加
  実装メソッド: add_missing_imports()
  検出方法: ASTパーサー使用
  精度目標: 95%以上
  所要時間: 1日

□ T3.3.3: 依存関係グラフ生成
  出力形式: Graphviz DOT形式
  可視化: Dashboard統合
  所要時間: 1日

【完了条件】
✅ agents/integration/dependency_resolver_v2.py 作成済み（600行）
✅ 依存関係解決率98%以上
✅ 循環依存検出率100%
✅ テスト成功率 84.3%以上維持

【出力ファイル】
- agents/integration/dependency_resolver_v2.py（新規）
- tests/integration/test_dependency_resolver.py（新規）
```

#### M3.4: F14 統合テスト実装
```
【タスク】
□ T3.4.1: IntegrationTesterV2クラス実装
  新規ファイル: agents/integration/integration_tester_v2.py (1,000行)
  実装内容:
    - 構文チェック
    - ユニットテスト実行
    - 統合テスト実行
    - 修正タスク生成
  依存: agents/integration/code_integrator_v2.py（M3.2）
  テスト: tests/integration/test_integration_tester.py（新規）
  所要時間: 3日
  
  【なぜ自動テストが必要か】
  - 統合後の品質保証
  - 人間の目視確認は非効率
  - 修正タスクの自動生成で高速修復

□ T3.4.2: 修正タスク生成
  実装メソッド: generate_repair_tasks()
  生成率目標: 90%以上
  pm_tasks連携: 自動追加
  所要時間: 2日

□ T3.4.3: テスト実行パイプライン
  実行順序: 構文→ユニット→統合
  失敗時: 即座に修正タスク生成
  所要時間: 1日

【完了条件】
✅ agents/integration/integration_tester_v2.py 作成済み（1,000行）
✅ テスト実行率100%
✅ エラー検出精度95%以上
✅ 修正提案生成率90%以上
✅ テスト成功率 84.3%以上維持

【出力ファイル】
- agents/integration/integration_tester_v2.py（新規）
- tests/integration/test_integration_tester.py（新規）
```

---

### Phase 4: Epic管理統合【1週間】

**目的**: Epic全体の管理・オーケストレーション

#### M4.1: EpicOrchestrator実装
```
【タスク】
□ T4.1.1: EpicOrchestratorクラス実装
  新規ファイル: agents/epic_orchestrator.py (800行)
  実装内容:
    - Epic→Story→Sub-taskの全体制御
    - F11-F14の統合呼び出し
    - 進捗可視化
  依存: 
    - core_agents/pm_agent_v33_epic.py（Phase 1）
    - agents/task_executor_v4_subtask.py（Phase 2）
    - agents/integration/*（Phase 3）
  テスト: tests/test_epic_orchestrator.py（新規）
  所要時間: 3日
  
  【なぜOrchestratorが必要か】
  - 3層構造の制御が複雑
  - F11-F14の呼び出しタイミング管理
  - 全体フローの一元化

□ T4.1.2: CompleteEngine連携
  既存ファイル: agents/complete_engine_ultimate.py
  連携方法: EpicOrchestratorをラッパーとして統合
  後方互換性: 既存メソッド維持
  所要時間: 2日

□ T4.1.3: E2Eテスト
  実Epic使用: AIデューデリジェンスエージェント
  検証フロー:
    1. Epic読み込み
    2. 10個のStory生成
    3. 各Story→Sub-task分解・実行
    4. F11-F14による統合
    5. 最終成果物生成
  所要時間: 2日

【完了条件】
✅ agents/epic_orchestrator.py 作成済み（800行）
✅ CompleteEngine統合成功
✅ E2Eテスト成功
✅ テスト成功率 84.3%以上維持

【出力ファイル】
- agents/epic_orchestrator.py（新規）
- tests/test_epic_orchestrator.py（新規）
```

---

### Phase 5: 診断・監視システム強化【1週間】

**目的**: 定期診断・異常検知の自動化

#### M5.1: 診断スクリプト整備
```
【タスク】
□ T5.1.1: システム全診断スクリプト
  新規ファイル: sh/diagnose_full_system.sh
  診断項目:
    - 既存テスト成功率（84.3%基準）
    - 新規テスト成功率（90%目標）
    - API成功率（95.9%基準）
    - ナレッジDB統計
    - ファイル整合性
    - 依存関係チェック
  実行頻度: 1時間ごと
  所要時間: 2日

□ T5.1.2: 異常検知アラート
  実装: sh/alert_system.sh
  アラート条件:
    - テスト成功率<84.3%
    - API成功率<90%
    - メモリ使用量>800MB
    - CPU使用率>60%
  通知方法: ログファイル + コンソール
  所要時間: 1日

□ T5.1.3: 定期診断の自動化
  実装: crontabまたはsystemd timer
  実行間隔: 1時間
  ログ保存: logs/diagnostic_YYYYMMDD_HHMM.log
  所要時間: 1日

【完了条件】
✅ sh/diagnose_full_system.sh 作成済み
✅ sh/alert_system.sh 作成済み
✅ 定期診断が自動実行
✅ アラート機能が正常動作

【出力ファイル】
- sh/diagnose_full_system.sh（新規）
- sh/alert_system.sh（新規）
```

#### M5.2: 進捗ダッシュボード強化
```
【タスク】
□ T5.2.1: Epic進捗表示
  既存ファイル: agents/observability/dashboard.py
  追加機能:
    - Epic完了率
    - Story完了度一覧
    - Sub-task実行状況
    - F11-F14統合状況
  所要時間: 2日

□ T5.2.2: リアルタイム更新
  更新間隔: 5分
  表示項目: 上記すべて + アラート
  所要時間: 1日

【完了条件】
✅ Dashboard機能拡張完了
✅ Epic進捗が表示される
✅ リアルタイム更新が動作
```

---

### Phase 6: 統合テスト・最適化【1週間】

**目的**: 全機能の統合テスト・性能最適化

#### M6.1: 総合テストスイート
```
【タスク】
□ T6.1.1: 既存テスト再実行
  実行コマンド: pytest tests/ -v
  目標成功率: 90%以上（84.3%→90%）
  カバレッジ: 90%以上
  所要時間: 1日

□ T6.1.2: E2Eシナリオテスト
  シナリオ数: 5件
  シナリオ例:
    1. AIデューデリジェンスエージェント生成
    2. データ分析エージェント生成
    3. 自動化エージェント生成
    4. エラー発生→自動修復
    5. 統合失敗→修正タスク生成
  所要時間: 2日

□ T6.1.3: 性能ベンチマーク
  測定項目:
    - Epic分解時間
    - Story実行時間
    - Sub-task実行時間
    - 統合処理時間（F11-F14）
    - メモリ使用量
    - CPU使用率
  目標達成確認: すべての目標値クリア
  所要時間: 1日

【完了条件】
✅ テスト成功率90%以上
✅ E2Eシナリオ5件すべて成功
✅ 性能目標すべて達成
✅ カバレッジ90%以上

【出力ファイル】
- MD/PHASE6_FINAL_TEST_RESULTS.md
```

#### M6.2: ドキュメント整備
```
【タスク】
□ T6.2.1: 実装ドキュメント作成
  新規ファイル: MD/IMPLEMENTATION_GUIDE_V5_0.md
  内容:
    - 各コンポーネントの使い方
    - API仕様
    - 設定方法
  所要時間: 1日

□ T6.2.2: 運用手順書作成
  新規ファイル: MD/OPERATION_MANUAL_V5_0.md
  内容:
    - システム起動方法
    - 監視方法
    - トラブルシューティング
  所要時間: 1日

□ T6.2.3: ナレッジベース登録
  登録内容:
    - 実装パターン
    - 解決した課題
    - ベストプラクティス
  登録件数: 20件以上
  所要時間: 1日

【完了条件】
✅ 実装ガイド作成済み
✅ 運用手順書作成済み
✅ ナレッジ20件以上登録

【出力ファイル】
- MD/IMPLEMENTATION_GUIDE_V5_0.md（新規）
- MD/OPERATION_MANUAL_V5_0.md（新規）
```

---

## 📋 進捗管理

### 単一チェックリストの運用
```
【進捗管理ファイル】
MD/PROGRESS_CHECKLIST.md

【更新ルール】
1. 各タスク完了時に即座に更新
2. AIチャット交代時に必ず参照
3. 診断スクリプトで自動検証
4. Phase完了時に診断実行

【チェック項目】
□ タスク完了
✅ タスク完了＋診断OK
❌ タスク失敗（原因記録）
⏸️ タスク保留（理由記録）

【診断コマンド】
sh/update_progress.sh
  - チェックリスト更新
  - 診断実行
  - 結果記録
```

---

## 🔍 定期診断システム

### 診断実行タイミング
```
【Phase完了時診断】
- Phase 0完了時: sh/diagnose_phase0.sh
- Phase 1完了時: sh/diagnose_phase1.sh
- Phase 2完了時: sh/diagnose_phase2.sh
- Phase 3完了時: sh/diagnose_phase3.sh
- Phase 4完了時: sh/diagnose_phase4.sh
- Phase 5完了時: sh/diagnose_phase5.sh
- Phase 6完了時: sh/diagnose_phase6_final.sh

【1時間ごと診断】（Phase 5以降）
- sh/diagnose_hourly.sh
  - 既存テスト成功率
  - API成功率
  - リソース使用量
  - ファイル整合性
```

### 診断基準値
```
【絶対に下回ってはいけない基準】
- 既存テスト成功率: 84.3%以上
- API成功率: 95.9%以上

【目標値】
- 新規含むテスト成功率: 90%以上
- Epic分解時間: <60秒
- Story実行時間: <20分
- 統合成功率: 95%以上
- メモリ使用量: <600MB（ピーク）
- CPU使用率: <40%（実行時）

【なぜこの基準か】
84.3%: 現在の安定稼働時の値。これを下回ると既存機能に問題
95.9%: 現在のAPI成功率。ネットワーク品質の指標
90%: 新機能追加後の目標。5.7%の向上
```

---

## 🛡️ 後戻り防止策

### 実装保護メカニズム
```
【ファイルロック】
既存47件のファイルは読み取り専用
変更検知: sh/detect_unauthorized_changes.sh
1時間ごとに自動チェック

【テスト保護】
既存テストは変更禁止
新規テストのみ追加可能
テスト成功率84.3%をCI/CDのゲート条件

【バックアップ】
Phase開始時: 全ファイルバックアップ
実行コマンド: sh/backup_before_phase.sh
保存先: backups/phaseX_YYYYMMDD/

【ロールバック】
異常検知時: 前Phase状態に自動復元
実行コマンド: sh/rollback_to_previous_phase.sh
条件: テスト成功率<84.3%
```

### AI引継ぎプロトコル
```
【AIチャット交代時の手順】
1. MD/PROGRESS_CHECKLIST.md を参照
2. 最新の診断結果を確認
3. 未完了タスクの確認
4. コンテキスト情報の読み込み:
   - MD/MASTER_ROADMAP_V5_0.md
   - MD/REQUIREMENTS_V5_0.md
   - MD/EXISTING_FILES_BASELINE.md
5. 診断実行: sh/diagnose_current_state.sh
6. 続きから作業開始

【コンテキスト情報】
各ファイルに「なぜ」を明記
数値には根拠を記載
依存関係を可視化
```

---

## 📊 成功基準（最終確認）

### Phase 6完了時の検証項目
```
【機能】
✅ F1-F14すべて実装済み
✅ Epic→Story→Sub-taskの3層動作
✅ max_tokens=32,000動作
✅ F11-F14統合機能動作

【品質】
✅ テスト成功率90%以上
✅ カバレッジ90%以上
✅ Lintエラーゼロ
✅ ドキュメント完備

【性能】
✅ Epic分解<60秒
✅ Story実行<20分
✅ 統合成功率>95%
✅ メモリ<600MB
✅ CPU<40%

【運用】
✅ 診断システム稼働
✅ アラートシステム稼働
✅ 進捗チェックリスト更新
✅ ナレッジ20件以上登録

【既存システム保護】
✅ 既存テスト84.3%以上維持
✅ 既存47件のファイル無変更
✅ API成功率95.9%以上維持
✅ ナレッジDB511件以上維持
```

---

## 📁 ファイル構造（最終）
```
gemini_AI_Agent/
├── MD/                                 ← すべてのMDファイル
│   ├── MASTER_ROADMAP_V5_0.md         ← このファイル
│   ├── PROGRESS_CHECKLIST.md          ← 進捗管理（単一ソース）
│   ├── REQUIREMENTS_V5_0.md           ← 要件定義
│   ├── EXISTING_FILES_BASELINE.md     ← 既存ファイル一覧
│   ├── IMPLEMENTATION_GUIDE_V5_0.md   ← 実装ガイド
│   ├── OPERATION_MANUAL_V5_0.md       ← 運用手順書
│   ├── PHASE1_TEST_RESULTS.md         ← Phase 1テスト結果
│   ├── PHASE2_TEST_RESULTS.md         ← Phase 2テスト結果
│   └── PHASE6_FINAL_TEST_RESULTS.md   ← 最終テスト結果
│
├── sh/                                 ← すべてのshファイル
│   ├── diagnose_phase0.sh             ← Phase 0診断
│   ├── diagnose_phase1.sh             ← Phase 1診断
│   ├── diagnose_phase2.sh             ← Phase 2診断
│   ├── diagnose_phase3.sh             ← Phase 3診断
│   ├── diagnose_phase4.sh             ← Phase 4診断
│   ├── diagnose_phase5.sh             ← Phase 5診断
│   ├── diagnose_phase6_final.sh       ← Phase 6最終診断
│   ├── diagnose_hourly.sh             ← 1時間ごと診断
│   ├── diagnose_full_system.sh        ← システム全診断
│   ├── alert_system.sh                ← アラートシステム
│   ├── backup_before_phase.sh         ← Phase前バックアップ
│   ├── rollback_to_previous_phase.sh  ← ロールバック
│   ├── update_progress.sh             ← 進捗更新
│   ├── list_existing_files.sh         ← 既存ファイル一覧
│   └── detect_unauthorized_changes.sh ← 不正変更検知
│
├── core_agents/
│   ├── pm_agent_v3_fixed.py           ← 既存（423行）
│   └── pm_agent_v33_epic.py           ← 新規（1,500行）Phase 1
│
├── agents/
│   ├── complete_engine_ultimate.py    ← 既存（387行）
│   ├── epic_orchestrator.py           ← 新規（800行）Phase 4
│   ├── task_executor_v4_subtask.py    ← 新規（2,000行）Phase 2
│   ├── integration/
│   │   ├── progress_analyzer_v2.py    ← 新規（800行）Phase 3
│   │   ├── code_integrator_v2.py      ← 新規（1,200行）Phase 3
│   │   ├── dependency_resolver_v2.py  ← 新規（600行）Phase 3
│   │   └── integration_tester_v2.py   ← 新規（1,000行）Phase 3
│   └── observability/
│       └── dashboard.py               ← 既存（拡張）Phase 5
│
├── tests/
│   ├── test_pm_agent_v33_epic.py      ← 新規 Phase 1
│   ├── test_task_executor_v4.py       ← 新規 Phase 2
│   ├── test_epic_orchestrator.py      ← 新規 Phase 4
│   └── integration/
│       ├── test_progress_analyzer.py  ← 新規 Phase 3
│       ├── test_code_integrator.py    ← 新規 Phase 3
│       ├── test_dependency_resolver.py← 新規 Phase 3
│       └── test_integration_tester.py ← 新規 Phase 3
│
└── ... 他既存ファイル47件（無変更）
```

---

## 🔄 継続的改善

### ナレッジ蓄積戦略
```
【Phase完了時に登録】
- 実装パターン
- 解決した課題
- ベストプラクティス
- 失敗事例と対策

【カテゴリ】
- epic_management
- story_execution
- subtask_generation
- integration_techniques
- testing_strategies
- performance_optimization

【活用】
- 次のEpic開発時に参照
- プロンプト改善に活用
- エラー修復に活用
```

---

**このロードマップは単一のマスタードキュメントとして、Phase 0からPhase 6までの全工程を管理します。進捗は MD/PROGRESS_CHECKLIST.md で一元管理し、AIチャット交代時もシームレスに継続できます。**
