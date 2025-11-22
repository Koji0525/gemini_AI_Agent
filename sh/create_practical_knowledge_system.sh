#!/bin/bash
# 実践的ナレッジシステム構築

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 実践的ナレッジシステム構築"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: ナレッジテンプレート定義
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cat > tools/knowledge_templates.py << 'PYTHON'
"""
ナレッジテンプレート
実践的で再利用可能なナレッジのフォーマット定義
"""

KNOWLEDGE_TEMPLATE = """
# {title}

## �� 概要
{summary}

## ❓ 問題・課題
{problem}

## ✅ 解決策
{solution}

## 💡 実装方法

### コード例
````{language}
{code_example}
````

### 説明
{explanation}

## 🎯 使用場面
{use_cases}

## ⚠️ 注意点
{cautions}

## 🔗 関連知識
{related_knowledge}

## 📊 メタ情報
- カテゴリ: {category}
- タグ: {tags}
- 品質スコア: {quality_score}/10
- 作成日: {created_at}
- 最終更新: {updated_at}
"""

PROBLEM_SOLUTION_TEMPLATE = """
# {title}

## 🔴 問題
{problem_description}

### 具体例
{problem_example}

## 🟢 解決策
{solution_description}

### 実装手順
{implementation_steps}

### コード
````{language}
{code}
````

## 📈 効果
{benefits}

## 🎓 学び
{learnings}
"""

SYSTEM_DESIGN_TEMPLATE = """
# {title}

## 🎯 目的
{purpose}

## 🏗️ アーキテクチャ
{architecture}

### コンポーネント
{components}

### データフロー
{data_flow}

## 💻 実装
````{language}
{implementation}
````

## 🔍 仕組み
{mechanism}

## �� 性能
{performance}

## 🔄 拡張性
{extensibility}
"""

BEST_PRACTICE_TEMPLATE = """
# {title}

## ✨ ベストプラクティス
{best_practice}

## ❌ アンチパターン
{anti_pattern}

## 📝 推奨コード
````{language}
{recommended_code}
````

## 🚫 非推奨コード
````{language}
{not_recommended_code}
````

## 💡 なぜこれが重要か
{importance}

## 🎯 適用場面
{application}
"""

def get_template(template_type: str) -> str:
    """テンプレート取得"""
    templates = {
        'general': KNOWLEDGE_TEMPLATE,
        'problem_solution': PROBLEM_SOLUTION_TEMPLATE,
        'system_design': SYSTEM_DESIGN_TEMPLATE,
        'best_practice': BEST_PRACTICE_TEMPLATE
    }
    return templates.get(template_type, KNOWLEDGE_TEMPLATE)

PYTHON

echo "  ✅ ナレッジテンプレート作成完了"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: Gemini APIによる高品質化エンジン
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cat > agents/automation/knowledge_enhancer.py << 'PYTHON'
"""
ナレッジ高品質化エンジン
Gemini APIを使って実践的なナレッジに変換
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.gemini_api import GeminiAPI
from tools.knowledge_templates import get_template

class KnowledgeEnhancer:
    """ナレッジ高品質化エンジン"""
    
    def __init__(self):
        self.gemini = GeminiAPI()
    
    def enhance_knowledge(self, raw_content: str, task_context: dict) -> dict:
        """
        生のコンテンツを実践的なナレッジに変換
        
        Args:
            raw_content: 生のコンテンツ
            task_context: タスクコンテキスト（task_id, output_path, quality_scoreなど）
        
        Returns:
            enhanced_knowledge: 高品質化されたナレッジ
        """
        
        # Geminiプロンプト構築
        prompt = self._build_enhancement_prompt(raw_content, task_context)
        
        # Gemini APIで高品質化
        enhanced_content = self.gemini.generate_content(prompt)
        
        # 品質チェック
        quality_score = self._assess_quality(enhanced_content)
        
        return {
            'content': enhanced_content,
            'quality_score': quality_score,
            'original_content': raw_content,
            'enhanced_at': datetime.now().isoformat()
        }
    
    def _build_enhancement_prompt(self, raw_content: str, context: dict) -> str:
        """高品質化プロンプト構築"""
        
        prompt = f"""
あなたは優秀な技術ドキュメントライターです。
以下の生のコンテンツを、後で使える実践的なナレッジに変換してください。

# 生のコンテンツ
{raw_content}

# タスクコンテキスト
- タスクID: {context.get('task_id', 'unknown')}
- 品質スコア: {context.get('quality_score', 0)}/10
- 出力パス: {context.get('output_path', 'unknown')}

# 変換要件

## 必須要素
1. **問題・課題**: どんな問題を解決するのか？
2. **解決策**: どうやって解決するのか？
3. **コード例**: 実際に使えるコード（最も重要な部分のみ）
4. **使用場面**: どんな時に使うのか？
5. **学び**: このナレッジから何を学べるか？

## フォーマット
````markdown
# [タイトル]

## 📋 概要
簡潔な説明（1-2行）

## ❓ 問題・課題
具体的な問題の説明

## ✅ 解決策
解決方法の説明

## 💡 実装方法

### 主要コード
```python
# 最も重要な部分のみ（10-30行）
def example():
    pass
```

### 説明
コードの説明

## 🎯 使用場面
- 場面1: ...
- 場面2: ...

## 🎓 学び
このナレッジから得られる重要な学び

## 🔗 関連知識
- 関連技術1
- 関連技術2
````

## 重要な指針
- **実践的**: 後で実際に使えること
- **簡潔**: 無駄な情報は省く
- **コード優先**: 説明よりコード例を重視
- **再利用可能**: コピペですぐ使える
- **検索可能**: キーワードを適切に含める

変換後のMarkdownを出力してください。
"""
        
        return prompt
    
    def _assess_quality(self, content: str) -> float:
        """品質評価"""
        
        quality_criteria = {
            'has_problem': '問題' in content or '課題' in content,
            'has_solution': '解決' in content,
            'has_code': '```' in content,
            'has_use_case': '使用' in content or '場面' in content,
            'has_learning': '学び' in content or 'ポイント' in content,
            'sufficient_length': len(content) > 500,
            'has_structure': '##' in content
        }
        
        score = sum(quality_criteria.values()) / len(quality_criteria) * 10
        
        return round(score, 1)
    
    def batch_enhance(self, knowledge_list: list) -> list:
        """一括高品質化"""
        
        enhanced_list = []
        
        for knowledge in knowledge_list:
            try:
                enhanced = self.enhance_knowledge(
                    knowledge['content'],
                    knowledge.get('context', {})
                )
                enhanced_list.append(enhanced)
            except Exception as e:
                print(f"  ⚠️  高品質化エラー: {e}")
                continue
        
        return enhanced_list

PYTHON

echo "  ✅ ナレッジ高品質化エンジン作成完了"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: 既存ナレッジ改善ツール
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cat > agents/automation/knowledge_upgrader.py << 'PYTHON'
"""
既存ナレッジ改善ツール
低品質なナレッジを実践的なナレッジに変換
"""

import sys
import os
import sqlite3
from pathlib import Path

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.knowledge_manager import KnowledgeManager
from agents.automation.knowledge_enhancer import KnowledgeEnhancer

class KnowledgeUpgrader:
    """既存ナレッジ改善"""
    
    def __init__(self):
        self.km = KnowledgeManager()
        self.enhancer = KnowledgeEnhancer()
    
    def upgrade_low_quality_entries(self, quality_threshold: float = 7.0):
        """低品質エントリを改善"""
        
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📈 既存ナレッジ改善")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()
        
        # 低品質エントリを取得
        low_quality = self._find_low_quality_entries(quality_threshold)
        
        print(f"📊 改善対象: {len(low_quality)}件")
        print()
        
        upgraded_count = 0
        
        for entry in low_quality:
            print(f"  🔄 改善中: ID {entry['id']}")
            
            try:
                # 高品質化
                enhanced = self.enhancer.enhance_knowledge(
                    entry['content'],
                    {
                        'task_id': entry.get('title', 'unknown'),
                        'quality_score': 5.0
                    }
                )
                
                # 更新
                self._update_entry(entry['id'], enhanced['content'])
                
                print(f"     ✅ 改善完了 (品質: {enhanced['quality_score']}/10)")
                upgraded_count += 1
                
            except Exception as e:
                print(f"     ❌ エラー: {e}")
        
        print()
        print(f"✅ {upgraded_count}/{len(low_quality)}件を改善しました")
    
    def _find_low_quality_entries(self, threshold: float) -> list:
        """低品質エントリを検索"""
        
        # 簡易的な品質判定基準
        # - contentが短い（< 300文字）
        # - コードブロックがない
        # - 構造化されていない
        
        conn = sqlite3.connect('/workspaces/gemini_AI_Agent/knowledge_system/database/knowledge.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM knowledge_entries
            WHERE LENGTH(content) < 300
            OR content NOT LIKE '%```%'
            ORDER BY id DESC
            LIMIT 50
        ''')
        
        entries = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return entries
    
    def _update_entry(self, entry_id: int, new_content: str):
        """エントリ更新"""
        
        conn = sqlite3.connect('/workspaces/gemini_AI_Agent/knowledge_system/database/knowledge.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE knowledge_entries
            SET content = ?
            WHERE id = ?
        ''', (new_content, entry_id))
        
        conn.commit()
        conn.close()

PYTHON

echo "  ✅ 既存ナレッジ改善ツール作成完了"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: knowledge_base_integrator更新
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cat > agents/automation/knowledge_base_integrator.py << 'PYTHON'
"""
ナレッジベース統合（高品質版）
Phase 3完了後にナレッジベースに登録
"""

import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.knowledge_manager import KnowledgeManager
from agents.automation.knowledge_enhancer import KnowledgeEnhancer

class KnowledgeBaseIntegrator:
    """ナレッジベース統合（高品質版）"""
    
    def __init__(self):
        self.km = KnowledgeManager()
        self.enhancer = KnowledgeEnhancer()
    
    def register_to_knowledge_base(
        self,
        task_id: str,
        output_path: str,
        quality_score: float,
        test_results: dict
    ) -> dict:
        """
        ナレッジベースに登録（高品質化付き）
        
        Args:
            task_id: タスクID
            output_path: 出力パス
            quality_score: 品質スコア
            test_results: テスト結果
        
        Returns:
            result: 登録結果
        """
        
        print()
        print("=" * 80)
        print("📚 ナレッジベース登録（高品質版）")
        print("=" * 80)
        print(f"タスクID: {task_id}")
        print(f"品質スコア: {quality_score}/10")
        print()
        
        # 品質閾値チェック
        if quality_score < 7.0:
            print(f"⚠️  品質スコアが低いため登録をスキップ (<7.0)")
            return {'success': False, 'reason': 'low_quality'}
        
        # 生のコンテンツ生成
        raw_content = self._generate_raw_content(
            task_id, output_path, quality_score, test_results
        )
        
        # 高品質化
        print("🔄 Gemini APIで高品質化中...")
        enhanced = self.enhancer.enhance_knowledge(
            raw_content,
            {
                'task_id': task_id,
                'output_path': output_path,
                'quality_score': quality_score
            }
        )
        
        print(f"✅ 高品質化完了 (品質: {enhanced['quality_score']}/10)")
        
        # ナレッジベースに登録
        try:
            entry_id = self.km.add_knowledge(
                content=enhanced['content'],
                source=f'auto_generated:{task_id}',
                metadata={
                    'task_id': task_id,
                    'output_path': output_path,
                    'quality_score': enhanced['quality_score'],
                    'test_results': test_results,
                    'category': 'generated_code',
                    'tags': ['auto_generated', 'phase3', 'phase4a', 'enhanced'],
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            print(f"✅ ナレッジベース登録完了 ({entry_id})")
            
            return {
                'success': True,
                'entry_id': entry_id,
                'quality_score': enhanced['quality_score']
            }
        
        except Exception as e:
            print(f"❌ ナレッジベース登録エラー: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_raw_content(
        self,
        task_id: str,
        output_path: str,
        quality_score: float,
        test_results: dict
    ) -> str:
        """生のコンテンツ生成"""
        
        # README.mdを読み込み
        readme_path = Path(output_path) / 'README.md'
        readme_content = ""
        
        if readme_path.exists():
            readme_content = readme_path.read_text()
        
        # 主要コードファイルを読み込み
        main_code = ""
        main_py = Path(output_path) / 'main.py'
        
        if main_py.exists():
            main_code = main_py.read_text()
        
        raw_content = f"""
タスクID: {task_id}
出力パス: {output_path}
品質スコア: {quality_score}/10

README:
{readme_content}

主要コード:
{main_code[:1000] if main_code else "（コードなし）"}

テスト結果:
{test_results}
"""
        
        return raw_content

PYTHON

echo "  ✅ knowledge_base_integrator更新完了"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 5: テスト実行スクリプト
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cat > sh/test_knowledge_enhancement.sh << 'TESTBASH'
#!/bin/bash
# ナレッジ高品質化テスト

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 ナレッジ高品質化テスト"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 << PYTHON
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.automation.knowledge_enhancer import KnowledgeEnhancer

# テスト用の生コンテンツ
raw_content = """
カラム固定機能を実装した。
position: sticky を使って左端と右端を固定。
これで横スクロールしても見やすくなった。
"""

context = {
    'task_id': 'test_column_fix',
    'quality_score': 8.0
}

# 高品質化
enhancer = KnowledgeEnhancer()

print("📝 元のコンテンツ:")
print(raw_content)
print()

print("🔄 高品質化中...")
enhanced = enhancer.enhance_knowledge(raw_content, context)

print()
print("✨ 高品質化後:")
print("=" * 80)
print(enhanced['content'])
print("=" * 80)
print()
print(f"📊 品質スコア: {enhanced['quality_score']}/10")

PYTHON

TESTBASH

chmod +x sh/test_knowledge_enhancement.sh

echo "  ✅ テストスクリプト作成完了"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 実践的ナレッジシステム構築完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

