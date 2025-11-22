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

