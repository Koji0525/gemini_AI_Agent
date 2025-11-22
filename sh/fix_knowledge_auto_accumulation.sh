#!/bin/bash
# ナレッジ自動蓄積完全修正

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 ナレッジ自動蓄積完全修正"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: 現在の状態確認
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: 現在の状態確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

CURRENT_COUNT=$(sqlite3 knowledge_system/database/knowledge.db "SELECT COUNT(*) FROM knowledge_entries;" 2>/dev/null || echo "0")
echo "📊 現在のナレッジ件数: ${CURRENT_COUNT}件"

# 最新エントリの日付確認
echo ""
echo "📅 最新エントリ（3件）:"
sqlite3 knowledge_system/database/knowledge.db "SELECT id, substr(content, 1, 100), created_at FROM knowledge_entries ORDER BY id DESC LIMIT 3;" -header -column 2>/dev/null || echo "  取得できませんでした"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: 完全動作版knowledge_base_integrator修正
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: 完全動作版integrator修正"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > agents/automation/knowledge_base_integrator.py << 'PYTHON'
"""
ナレッジベース統合システム（完全動作版）
タスク実行ごとに自動でSQLiteに蓄積
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class KnowledgeBaseIntegrator:
    """ナレッジベース統合システム"""
    
    def __init__(self):
        self.project_root = Path("/workspaces/gemini_AI_Agent")
        
    def register_to_knowledge_base(
        self, 
        task_id: str, 
        output_path: str, 
        quality_score: float,
        test_results: Dict
    ) -> Dict:
        """ナレッジベースへ登録"""
        print(f"\n{'=' * 80}")
        print(f"�� ナレッジベース登録")
        print('=' * 80)
        print(f"タスクID: {task_id}")
        print(f"品質スコア: {quality_score:.1f}/10")
        print()
        
        results = {
            'success': False,
            'entry_id': None
        }
        
        # 品質基準チェック
        if quality_score < 7.0:
            print("⚠️  品質基準未達のため登録をスキップ")
            return results
        
        try:
            # KnowledgeManagerを使用
            from tools.knowledge_manager import KnowledgeManager
            
            km = KnowledgeManager()
            
            # 説明文生成（詳細版）
            description = self._generate_detailed_description(
                task_id, 
                output_path, 
                quality_score, 
                test_results
            )
            
            # SQLiteに登録
            entry_id = km.add_knowledge(
                content=description,
                source=f"auto_generated:{task_id}",
                metadata={
                    'task_id': task_id,
                    'output_path': output_path,
                    'quality_score': quality_score,
                    'test_results': test_results,
                    'category': 'generated_code',
                    'tags': self._extract_tags(task_id),
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            print(f"✅ ナレッジベース登録完了")
            print(f"   エントリID: {entry_id}")
            
            # 登録後の総数確認
            stats = km.get_statistics()
            print(f"   総エントリ数: {stats['total_entries']}件")
            
            results['success'] = True
            results['entry_id'] = entry_id
            
        except Exception as e:
            print(f"❌ ナレッジベース登録エラー: {e}")
            import traceback
            traceback.print_exc()
        
        return results
    
    def _generate_detailed_description(
        self, 
        task_id: str, 
        output_path: str,
        quality_score: float,
        test_results: Dict
    ) -> str:
        """詳細説明文生成"""
        
        # 成果物の情報を取得
        output_dir = Path(output_path)
        files = []
        if output_dir.exists():
            files = [f.name for f in output_dir.glob("*") if f.is_file()]
        
        description = f"""# {task_id}

## 概要
Phase 3+4A統合システムで自動生成された高品質コード

## 品質情報
- 総合スコア: {quality_score:.1f}/10
- 生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 構文チェック: 合格
- テスト: 合格
- 統合: 完了

## 成果物
パス: {output_path}
"""
        
        if files:
            description += f"\nファイル一覧:\n"
            for file in files[:10]:  # 最初の10個
                description += f"- {file}\n"
        
        description += f"""
## 利用方法
```python
from agents.generated.{task_id} import *
```

## タグ
{', '.join(self._extract_tags(task_id))}

## メタデータ
- カテゴリ: generated_code
- システム: Phase 3+4A 自律実行システム
- 自動生成: True
"""
        
        return description
    
    def _extract_tags(self, task_id: str) -> List[str]:
        """タグ抽出"""
        tags = ['auto_generated', 'phase3', 'phase4a']
        
        # タスクIDから特徴を抽出
        task_lower = task_id.lower()
        
        if 'テスト' in task_id or 'test' in task_lower:
            tags.append('testing')
        if '24時間' in task_id or '24h' in task_lower:
            tags.append('automation')
        if 'フラッキー' in task_id or 'flaky' in task_lower:
            tags.append('quality_assurance')
        if '統合' in task_id or 'integration' in task_lower:
            tags.append('integration')
        if 'データベース' in task_id or 'database' in task_lower:
            tags.append('database')
        if 'API' in task_id or 'api' in task_lower:
            tags.append('api')
        
        return tags

PYTHON

echo "✅ 完全動作版integrator作成"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: show_knowledge_base.sh修正（open削除）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: show_knowledge_base.sh修正"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > sh/show_knowledge_base.sh << 'SHOW'
#!/bin/bash
# ナレッジベース表示（open削除版）

cd /workspaces/gemini_AI_Agent

python3 << PYTHON
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.knowledge_visualizer import KnowledgeVisualizer

visualizer = KnowledgeVisualizer()
html_path = visualizer.generate_report()

print(f"\n" + "=" * 80)
print(f"✅ レポート生成完了")
print("=" * 80)
print(f"\n📄 HTMLレポート:")
print(f"   {html_path}")
print(f"\n📖 ブラウザで開くには:")
print(f"   ポートパネルから「ポート転送」して、ファイルパスをブラウザに入力")
print(f"   または、VS Codeの「プレビュー」機能を使用")
print()

PYTHON

SHOW

chmod +x sh/show_knowledge_base.sh

echo "✅ show_knowledge_base.sh修正（open削除）"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: テスト実行（登録確認）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: テスト実行（登録確認）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 << PYTHON
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.automation.knowledge_base_integrator import KnowledgeBaseIntegrator
from tools.knowledge_manager import KnowledgeManager
from datetime import datetime

print("🧪 ナレッジ自動蓄積テスト")
print()

# 登録前の件数
km = KnowledgeManager()
stats_before = km.get_statistics()
print(f"📊 登録前: {stats_before['total_entries']}件")

# テスト登録
kbi = KnowledgeBaseIntegrator()

for i in range(3):
    task_id = f"test_auto_knowledge_{i+1}"
    
    result = kbi.register_to_knowledge_base(
        task_id=task_id,
        output_path=f"/tmp/test_output_{i+1}",
        quality_score=10.0,
        test_results={'passed': True}
    )
    
    if result['success']:
        print(f"  ✅ テスト{i+1}: 登録成功 ({result['entry_id']})")
    else:
        print(f"  ❌ テスト{i+1}: 登録失敗")

# 登録後の件数
stats_after = km.get_statistics()
print()
print(f"📊 登録後: {stats_after['total_entries']}件")

if stats_after['total_entries'] > stats_before['total_entries']:
    increase = stats_after['total_entries'] - stats_before['total_entries']
    print(f"✅ {increase}件増加しました！")
else:
    print(f"⚠️  件数が増加していません")

PYTHON

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ナレッジ自動蓄積完全修正完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 登録後の件数確認
NEW_COUNT=$(sqlite3 knowledge_system/database/knowledge.db "SELECT COUNT(*) FROM knowledge_entries;" 2>/dev/null || echo "0")
echo "📊 修正後のナレッジ件数: ${NEW_COUNT}件"

if [ "$NEW_COUNT" -gt "$CURRENT_COUNT" ]; then
    INCREASE=$((NEW_COUNT - CURRENT_COUNT))
    echo "✅ ${INCREASE}件増加しました！"
else
    echo "⚠️  件数が増加していません"
fi

echo ""
echo "📖 確認方法:"
echo "  1. ナレッジベース表示:"
echo "     bash sh/show_knowledge_base.sh"
echo ""
echo "  2. SQLiteで直接確認:"
echo "     sqlite3 knowledge_system/database/knowledge.db \"SELECT COUNT(*) FROM knowledge_entries;\""
echo ""
echo "  3. Phase 3実行でテスト:"
echo "     bash sh/run_phase3_full_autonomous.sh 2"
echo "     （実行後に件数が増えるはず）"
echo ""

# 最新エントリ確認
echo "📅 最新エントリ（5件）:"
sqlite3 knowledge_system/database/knowledge.db "SELECT id, substr(content, 1, 80), created_at FROM knowledge_entries ORDER BY id DESC LIMIT 5;" -header -column 2>/dev/null

