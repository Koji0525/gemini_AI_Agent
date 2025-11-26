"""
Phase 6 API統一パターンのナレッジ登録

【学んだこと】
- 既存システムとV2でAPIの返り値形式が異なる問題
- 統合アダプターでの返り値統一による解決
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from knowledge_system.core_agents.knowledge_manager import KnowledgeManager


def register_knowledge():
    """API統一パターンをナレッジ登録"""

    print("=" * 60)
    print("Phase 6: API統一パターン ナレッジ登録")
    print("=" * 60)
    print()

    km = KnowledgeManager()

    km.add_knowledge(
        title="Phase6_API統一パターン_返り値形式の統一",
        content="""
【問題】
既存システムとV2で返り値形式が異なり、統合テストが失敗。

既存: {'success': True, ...}
V2:   {'status': 'success', ...}

【原因】
- 異なる開発時期に実装されたため、APIが統一されていなかった
- V2はより詳細なstatus管理を志向
- 既存システムはシンプルなsuccess/failureのみ

【解決策】
統合アダプターに`_normalize_result()`メソッドを追加。
```python
def _normalize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
    # 既にsuccessキーがある場合はそのまま
    if 'success' in result:
        return result
    
    # statusキーがある場合は変換
    if 'status' in result:
        normalized = dict(result)
        normalized['success'] = (result['status'] == 'success')
        return normalized
    
    return result
```

【効果】
- テスト成功率: 3/4 → 4/4 (100%)
- API互換性: 完全維持
- 既存コード: 変更不要

【適用原則】
1. 既存システムのAPIを破壊しない
2. 新システムの返り値をアダプターで変換
3. 変換ロジックは統合層に集約

【今後の推奨事項】
- 新規開発時はAPI設計を統一
- 統合アダプターで互換性を保証
- ドキュメントにAPI仕様を明記
        """,
        category="api_design",
        tags=["api", "integration", "phase6", "compatibility"],
    )

    print("✅ ナレッジ登録完了")
    print("=" * 60)


if __name__ == "__main__":
    try:
        register_knowledge()
    except Exception as e:
        print(f"❌ ナレッジ登録エラー: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
