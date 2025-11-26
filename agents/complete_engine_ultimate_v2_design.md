# CompleteEngineUltimateV2 設計書

## 目的
既存CompleteEngineUltimate（保護）に階層型アーキテクチャを統合

## アーキテクチャ
```
CompleteEngineUltimateV2 (新規)
  ├── CompleteEngineUltimate (継承・保護)
  │   ├── 既存機能すべて維持
  │   └── F1-F10統合済み
  │
  └── 階層型レイヤー（追加）
      ├── ExecutiveManager
      ├── TeamLeader × 3-5
      └── HierarchicalWorker × 10-20
```

## 統合方針

### Option A: ハイブリッドモード（推奨）
```python
class CompleteEngineUltimateV2(CompleteEngineUltimate):
    def __init__(self, mode='legacy'):
        super().__init__()
        self.mode = mode
        if mode == 'hierarchical':
            self.executive = ExecutiveManager(...)
    
    def execute_goal(self, goal_id):
        if self.mode == 'legacy':
            return super().execute_goal(goal_id)  # 既存動作
        else:
            return self._execute_hierarchical(goal_id)  # 階層型
```

### 利点
- 既存システム完全保護
- 段階的移行可能
- A/Bテスト可能

## 実装ステップ
1. CompleteEngineUltimateV2クラス作成
2. モード切り替え機能
3. 階層型実行フロー
4. テスト（両モード）

## 成功基準
- legacy モード: 既存テスト100%成功
- hierarchical モード: 新規テスト100%成功
- モード切り替え: エラーなし
