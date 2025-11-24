# Phase 2 キックオフ

## 開始日時
2025-11-25

## Phase 2 目標
Story→Sub-task分解機能の実装により、
1Story（500-1,500行）を3-5個のSub-task（200-400行）に自動分解し、
各Sub-taskを独立して実行可能にする。

## Phase 1からの引継ぎ

### ✅ 完了事項
1. PMAgent v33 Epic実装（686行）
2. Epic→Story分解機能（10件同時生成）
3. Google Sheets連携動作確認
4. 単体テスト13件成功（100%）
5. 既存システム保護成功（変更0件）

### 📚 獲得知見（ナレッジベース登録済み）
1. JSON解析エラーの堅牢な対処法
2. pytest環境変数管理のベストプラクティス
3. 既存システム保護型開発パターン
4. Gemini API max_tokens最適化
5. file_version_manager正しい使用方法

### 🔒 保護対象ファイル（変更禁止）
- tools/sheets_manager.py
- tools/safe_sheets_wrapper.py
- tools/base_data_accessor.py
- knowledge_system/core_agents/knowledge_manager.py
- agents/complete_engine_ultimate.py
- agents/task_execution/high_quality_executor_v6.py ★Phase 2で重要

## Phase 2 実装計画

### M2.1: Sub-task分解機能実装（1週間）

#### T2.1.1: SubTaskDecomposerクラス実装
```python
# 新規ファイル: agents/task_executor_v4_subtask.py
class SubTaskDecomposer:
    """Story→Sub-task分解エンジン"""
    
    def __init__(self):
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            generation_config={
                "max_output_tokens": 32000,
            }
        )
    
    async def decompose_story_to_subtasks(
        self,
        story: Dict,
        num_subtasks: int = 4
    ) -> List[Dict]:
        """1Story → 3-5個のSub-task"""
        pass
```

**目標**:
- 実装行数: 2,000行
- 1Story→3-5Sub-task分解
- 各Sub-task: 200-400行の目標設定

#### T2.1.2: Gemini呼び出し最適化
- max_tokens=32,000を継続使用
- プロンプト設計: Phase 1の知見を活用
- JSON解析: 堅牢な解析ロジック再利用

#### T2.1.3: Sub-task結果のメモリ管理
```python
class SubTaskMemoryManager:
    """Sub-task結果の一時保存"""
    
    def __init__(self):
        self.subtask_results = {}
    
    def save_subtask_result(self, subtask_id: str, result: Dict):
        """Sub-task結果を保存"""
        pass
    
    def get_all_results(self, story_id: str) -> List[Dict]:
        """Story配下のすべてのSub-task結果を取得"""
        pass
```

#### T2.1.4: 既存RealExecutorとの統合
**重要**: high_quality_executor_v6.py は変更しない

統合戦略:
1. task_executor_v4_subtask.py を**独立モジュール**として実装
2. high_quality_executor_v6 を**内部で呼び出す**（ラッパー方式）
3. 既存動作を保証
```python
# task_executor_v4_subtask.py
from agents.task_execution.high_quality_executor_v6 import HighQualityExecutorV6

class TaskExecutorV4SubTask:
    def __init__(self):
        self.base_executor = HighQualityExecutorV6()  # 既存を利用
        self.decomposer = SubTaskDecomposer()
    
    async def execute_story_with_subtasks(self, story: Dict):
        # 1. Story→Sub-task分解
        subtasks = await self.decomposer.decompose_story_to_subtasks(story)
        
        # 2. 各Sub-taskを既存executorで実行
        for subtask in subtasks:
            result = self.base_executor.execute_task(subtask)
        
        # 3. 統合
        return integrate_results(results)
```

### M2.2: Sub-task実行テスト（1週間）

#### T2.2.1: 単体テスト作成
- ファイル: tests/test_task_executor_v4_subtask.py
- テストケース: 15件以上
- カバレッジ: 90%以上

#### T2.2.2: 統合テスト
- 実際のStoryで3-5Sub-task生成テスト
- 各Sub-taskの独立実行確認
- 結果統合の確認

#### T2.2.3: 性能テスト
目標値:
- Sub-task分解時間: <5秒
- Sub-task実行時間: <3分/個
- Story完全完了: <20分

## Phase 2 完了条件

| 条件 | 目標値 |
|------|--------|
| Sub-task分解機能実装 | 完了 |
| 単体テスト成功率 | 90%以上 |
| 統合テスト成功 | 3-5Sub-task生成成功 |
| 性能テスト | 全目標値達成 |
| 既存システム保護 | 変更0件 |
| 既存テスト成功率 | 84.3%以上維持 |

## 開始準備状況

✅ Phase 1完了
✅ 知見のナレッジベース登録完了
✅ 既存システム保護確認完了
✅ Phase 2計画書作成完了

**Phase 2開始可能**: ✅
