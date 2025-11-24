# Phase 3: 統合機能（F11-F14）実装 準備

## 開始日時準備
2025-11-25

## Phase 3 目標

Epic→Story→Sub-taskの3層構造が完成し、
次は成果物を統合する機能（F11-F14）を実装する。

### 統合機能の役割
```
Epic (10,000行)
  ↓ Phase 1
10 Stories (各1,000行)
  ↓ Phase 2
40-50 Sub-tasks (各200-400行)
  ↓ Phase 3 ★ここを実装
統合・品質保証
  ↓
完成した成果物
```

## Phase 1-2 からの引継ぎ

### ✅ 完了事項（Phase 1）
1. PMAgent v33 Epic実装（686行）
2. Epic→10 Stories分解機能
3. 単体テスト13件成功（100%）
4. 知見5件登録

### ✅ 完了事項（Phase 2）
1. TaskExecutor v4 Sub-task実装（657行）
2. Story→4 Sub-tasks分解機能
3. 単体テスト15件成功（100%）
4. 知見3件追加登録

### 📚 蓄積知見（計8件）
**Phase 1 (5件)**
1. JSON解析エラーの堅牢な対処法
2. pytest環境変数管理
3. 既存システム保護型開発パターン
4. Gemini API max_tokens最適化
5. インターフェース確認の重要性

**Phase 2 (3件)**
6. Sub-task分解の実装パターン
7. 既存executorラッパー実装
8. Sub-taskプロンプト設計

### 🔒 保護対象ファイル（変更禁止）
- tools/sheets_manager.py
- tools/safe_sheets_wrapper.py
- tools/base_data_accessor.py
- knowledge_system/core_agents/knowledge_manager.py
- agents/complete_engine_ultimate.py
- agents/task_execution/high_quality_executor_v6.py
- core_agents/pm_agent_v33_epic.py ★Phase 1成果物
- agents/task_executor_v4_subtask.py ★Phase 2成果物

## Phase 3 実装計画

### M3.1: F11 進捗分析実装（3-4日）

#### 機能概要
Story完了度を計算し、不足Sub-taskを検出する

#### 実装内容
```python
# 新規ファイル: agents/integration/progress_analyzer_v2.py (800行)

class ProgressAnalyzer:
    """進捗可視化＆ギャップ分析"""
    
    def analyze_story_progress(self, story_id: str) -> Dict:
        """Story完了度を計算"""
        # Sub-task完了状況を集計
        # 不足Sub-taskを検出
        # 統合準備状況を判定
        pass
    
    def detect_missing_subtasks(self, story: Dict) -> List[Dict]:
        """不足Sub-taskを検出"""
        pass
```

**目標**:
- 実装行数: 800行
- 完了度計算精度: 95%以上
- ギャップ検出率: 90%以上
- 実行時間: <3秒

### M3.2: F12 コード統合実装（4-5日）

#### 機能概要
Sub-taskのコードを統合し、import文を調整する

#### 実装内容
```python
# 新規ファイル: agents/integration/code_integrator_v2.py (1,200行)

class CodeIntegrator:
    """成果物統合エージェント"""
    
    def integrate_subtasks(self, story_id: str) -> Dict:
        """Sub-taskのコードを統合"""
        # Sub-task成果物を収集
        # コードをマージ
        # import文を調整
        # 重複を削除
        pass
    
    def resolve_imports(self, code: str) -> str:
        """import文を自動調整"""
        pass
```

**目標**:
- 実装行数: 1,200行
- 統合成功率: 95%以上
- import文解決率: 98%以上
- 実行時間: <10秒

### M3.3: F13 依存関係解決実装（3-4日）

#### 機能概要
import文を自動追加し、循環依存を検出する

#### 実装内容
```python
# 新規ファイル: agents/integration/dependency_resolver_v2.py (600行)

class DependencyResolver:
    """依存関係解決エージェント"""
    
    def resolve_dependencies(self, code: str) -> str:
        """依存関係を自動解決"""
        # 未定義変数を検出
        # import文を自動追加
        # 循環依存をチェック
        pass
    
    def detect_circular_dependencies(self, files: List[str]) -> List[str]:
        """循環依存を検出"""
        pass
```

**目標**:
- 実装行数: 600行
- 依存関係解決率: 98%以上
- 循環依存検出率: 100%
- 実行時間: <5秒

### M3.4: F14 統合テスト実装（4-5日）

#### 機能概要
統合後コードをテストし、エラーを検出する

#### 実装内容
```python
# 新規ファイル: agents/integration/integration_tester_v2.py (1,000行)

class IntegrationTester:
    """統合テスト＆修正提案"""
    
    def test_integrated_code(self, story_id: str) -> Dict:
        """統合後コードをテスト"""
        # 構文チェック
        # ユニットテスト実行
        # Lintチェック
        # エラー検出
        pass
    
    def generate_fix_suggestions(self, errors: List[Dict]) -> List[Dict]:
        """修正タスクを生成"""
        pass
```

**目標**:
- 実装行数: 1,000行
- テスト実行率: 100%
- エラー検出精度: 95%以上
- 修正提案生成率: 90%以上

## 既存システム保護戦略（Phase 3）

### 1. 完全独立実装
```
agents/integration/  ← 新規ディレクトリ
├── progress_analyzer_v2.py
├── code_integrator_v2.py
├── dependency_resolver_v2.py
└── integration_tester_v2.py
```

### 2. 既存コードへの影響ゼロ
- Phase 1, 2の成果物は変更しない
- 新規ディレクトリで完全に独立
- インポートのみで統合

### 3. ラッパー方式の継続
Phase 2で成功したラッパー方式を継続使用

## Phase 3 完了条件

| 条件 | 目標値 |
|------|--------|
| F11-F14実装完了 | すべて完了 |
| 単体テスト成功率 | 90%以上 |
| 統合テスト成功 | 3件以上のE2Eテスト成功 |
| 性能テスト | 全目標値達成 |
| 既存システム変更 | 0件 |
| 既存テスト成功率 | 84.3%以上維持 |

## 開始準備状況

✅ Phase 1完了（Epic→Story）
✅ Phase 2完了（Story→Sub-task）
✅ 知見蓄積（8件）
✅ 既存システム完全保護
✅ テスト成功率100%維持

**Phase 3開始可能**: ✅

## 推定所要時間

- M3.1 (F11): 3-4日
- M3.2 (F12): 4-5日
- M3.3 (F13): 3-4日
- M3.4 (F14): 4-5日
- テスト・調整: 2-3日

**合計**: 約2週間（ロードマップ通り）
