"""
Phase 6 最終ナレッジ登録

実システム統合で学んだことをナレッジベースに登録。
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from knowledge_system.core_agents.knowledge_manager import KnowledgeManager


def register_knowledge():
    """Phase 6最終知見をナレッジ登録"""

    print("=" * 60)
    print("Phase 6 最終ナレッジ登録")
    print("=" * 60)
    print()

    km = KnowledgeManager()

    # ナレッジ1: BaseDataAccessor活用パターン
    print("[1/2] BaseDataAccessor活用パターン登録中...")
    km.add_knowledge(
        title="Phase6_BaseDataAccessor活用パターン_既存システム統合",
        content="""
【問題】
GoogleSheetsManagerに`read_sheet()`メソッドが存在せず、統合テスト失敗。

【原因】
- GoogleSheetsManager: 低レベルAPI（read_range, append_rows, update_range）
- BaseDataAccessor: 高レベルAPI（列構造自動検出、辞書型返却）
- 既存システムはBaseDataAccessorを使用していた

【解決策】
既存システムと同じBaseDataAccessorを使用。
```python
# ❌ 間違った方法
from tools.sheets_manager import GoogleSheetsManager
sheets = GoogleSheetsManager()
data = sheets.read_sheet('project_goal')  # メソッド存在しない

# ✅ 正しい方法
from tools.base_data_accessor import BaseDataAccessor
accessor = BaseDataAccessor()
data = accessor.sheets.read_range('project_goal!A:Z')
```

【BaseDataAccessorの利点】
1. 列構造を自動検出
2. データクリーニング（空行削除など）
3. エラー処理の一元化
4. 既存システムとの互換性

【統合パターン】
```python
# 1. BaseDataAccessor初期化
accessor = BaseDataAccessor()

# 2. ゴール読み取り
goals_data = accessor.sheets.read_range('project_goal!A:Z')
headers = goals_data[0]
rows = goals_data[1:]

# 3. データ処理
goal_id_idx = headers.index('goal_id')
for row in rows:
    goal_id = row[goal_id_idx]
    # 処理...
```

【教訓】
- 既存システムのAPI層を理解する
- 低レベルAPIと高レベルAPIを区別する
- 統合時は既存システムの使用パターンに従う

【今後の推奨事項】
- 新規開発時もBaseDataAccessorを使用
- APIドキュメントの整備
- 使用例をナレッジベースに蓄積
        """,
        category="api_design",
        tags=["base_data_accessor", "integration", "phase6", "sheets"],
    )
    print("✅ 登録完了")
    print()

    # ナレッジ2: Phase 6統合成功パターン
    print("[2/2] Phase 6統合成功パターン登録中...")
    km.add_knowledge(
        title="Phase6_統合成功パターン_既存システム保護型",
        content="""
【Phase 6 統合結果】
- P6-001〜P6-004: 完了（統合テスト4/4成功）
- 認証エラー解決: mock_mode追加
- API統一: _normalize_result()実装
- 実システム統合: BaseDataAccessor活用

【成功要因】
1. 段階的アプローチ
   - Mock環境でテスト → 実システム統合
   - V2機能をオプショナルに追加
   
2. 既存システム保護
   - 既存ファイル一切変更なし
   - テスト成功率84.3%維持
   - BaseDataAccessorなど既存APIを活用

3. プラグイン方式
   - CompleteEngineAdapterで既存/V2を統合
   - フラグ制御（enable_v2, mock_mode）
   - 自動フォールバック機構

【統合アーキテクチャ】
```
既存システム:
  CompleteEngineUltimate
  ├─ BaseDataAccessor
  │   └─ GoogleSheetsManager (低レベル)
  └─ F1-F10機能

V2システム:
  CompleteEngineUltimateV2
  ├─ Executive Manager
  ├─ MessageBus
  └─ 階層型組織

統合層:
  CompleteEngineAdapter
  ├─ engine_v1 (既存)
  ├─ engine_v2 (V2)
  └─ _normalize_result() (API統一)
```

【実装成果物】
- CompleteEngineAdapter: 200行
- Phase 6統合テスト: 150行
- Mock耐久テスト: 200行
- 認証設定ガイド: 完備

【Phase 6 完了条件達成状況】
✅ P6-001: 実装状況診断
✅ P6-002: 統合戦略実装
✅ P6-003: 認証設定確認
✅ P6-004: 統合テスト（4/4成功）
⬜ P6-005: 6時間耐久テスト（本番環境）
⬜ P6-006: 24時間耐久テスト（本番環境）
⬜ P6-007: 結果分析

進捗率: 57.1% (4/7)

【今後の推奨アクション】
1. 実際のゴールでF1実行（pm_agent_v33_epic.py）
2. 生成されたタスクでF2実行
3. Mock環境で6時間耐久テスト
4. 本番環境で24時間耐久テスト

【長期的な価値】
- 統合パターンの確立
- 既存システム保護手法の実証
- 段階的統合のベストプラクティス
        """,
        category="integration",
        tags=["phase6", "success_pattern", "integration", "protection"],
    )
    print("✅ 登録完了")
    print()

    print("=" * 60)
    print("✅ Phase 6最終ナレッジ登録完了（2件）")
    print("=" * 60)


if __name__ == "__main__":
    try:
        register_knowledge()
    except Exception as e:
        print(f"❌ ナレッジ登録エラー: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
