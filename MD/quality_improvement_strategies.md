# 品質大幅向上の具体的戦略

## 問題の本質

**現状**: 反復改良（refinement）は精度悪化のリスクがある
- 1回目: 良い出力
- 2回目: 改良で逆に劣化
- 3回目: さらに劣化

**理由**: 
- 改良指示が曖昧
- 前回の良い部分を失う
- トークン制限で内容が削減される

## 10の品質向上戦略

### 【戦略1】構造化プロンプト + Few-shot（最優先）

**効果**: ⭐⭐⭐⭐⭐（5/5）
**リスク**: ⭐（1/5）

**実装方法**:
`````python
prompt = f"""
あなたは経験10年のシニアPython開発者です。

【必須要件】
- このタスクは5万行プロジェクトの一部です
- 最低1000行のコード生成が必須です
- 複数ファイル（3ファイル以上）必須
- README.md（300行以上）必須

【成功例】（必ずこのレベルで出力）
過去の成功例: データベース接続モジュール
- main.py: 580行（接続管理、プール、トランザクション）
- test_main.py: 365行（ユニット、統合、モック）
- README.md: 300行（概要、API、使用例）
合計: 1,245行、3ファイル

【今回のタスク】
{task_description}

【必須成果物】
1. メインコード（500-1000行）
2. テストコード（200-400行）
3. README.md（300-500行）

【出力形式】
各ファイルをマークダウンコードブロックで：
````python
# filename: main.py
[コード500行以上]
````

【重要】1回で完全実装してください。反復改良はしません。
"""
`````

**メリット**:
- 1回で高品質出力
- 反復改良の劣化リスクなし
- Few-shotで具体例提示
- 定量指標明確

### 【戦略2】ファイル単位生成（段階的）

**効果**: ⭐⭐⭐⭐（4/5）
**リスク**: ⭐⭐（2/5）

**実装方法**:
1. ステップ1: main.py生成（500行）
2. ステップ2: test_main.py生成（300行）
3. ステップ3: README.md生成（300行）

**メリット**:
- 各ファイルに集中
- トークン制限の回避
- 品質が安定

**デメリット**:
- API呼び出し回数増加
- ファイル間の整合性確認必要

### 【戦略3】メタプロンプト方式

**効果**: ⭐⭐⭐⭐（4/5）
**リスク**: ⭐⭐（2/5）

**実装方法**:
`````python
# Step 1: 設計書生成
design_prompt = """
以下のタスクの詳細設計書を作成してください。

【タスク】
{task_description}

【設計書に含めるべき内容】
1. ファイル構成（3ファイル以上）
2. 各ファイルの役割と行数（合計1000行以上）
3. クラス設計
4. 関数設計
5. テスト戦略

出力はJSON形式で。
"""

# Step 2: 設計に基づいて実装
implementation_prompt = f"""
以下の設計書に従って、完全実装してください。

【設計書】
{design_json}

各ファイルを設計書の行数通りに実装してください。
"""
`````

**メリット**:
- LLMに設計させてから実装
- 構造が明確
- 行数が保証される

### 【戦略4】テンプレート駆動開発

**効果**: ⭐⭐⭐⭐⭐（5/5）
**リスク**: ⭐（1/5）

**実装方法**:
`````python
template = """
````python
# filename: {filename}
'''
{module_docstring}
'''

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class {main_class_name}:
    '''
    {class_docstring}
    '''
    
    def __init__(self, config: Dict[str, Any]):
        '''初期化'''
        self.config = config
        logger.info(f"{self.__class__.__name__} initialized")
    
    # [ここに50個のメソッドを実装]
    # 各メソッド10-20行 = 500-1000行
    
    def method_1(self):
        '''メソッド1の説明'''
        pass
    
    # ... 以下49個のメソッド
"""
````

プロンプトでテンプレートを埋めるよう指示。

**メリット**:
- 構造が保証される
- 行数が自然に増える
- 実装が確実

### 【戦略5】プロンプトチェーン

**効果**: ⭐⭐⭐⭐（4/5）
**リスク**: ⭐⭐（2/5）

**実装方法**:
1. Prompt 1: 要件分析（100行）
2. Prompt 2: アーキテクチャ設計（200行）
3. Prompt 3: 詳細設計（300行）
4. Prompt 4: 実装（500行）
5. Prompt 5: テスト（300行）
6. Prompt 6: ドキュメント（300行）

各プロンプトは前の出力を入力として使用。

**メリット**:
- 段階的に品質向上
- 各段階で検証可能
- トークン制限回避

### 【戦略6】高性能モデル使用

**効果**: ⭐⭐⭐（3/5）
**リスク**: ⭐（1/5）

**実装方法**:
````python
# 現在: gemini-2.0-flash-exp
# 変更: gemini-2.5-pro または claude-opus-4

model = genai.GenerativeModel('gemini-2.5-pro')
````

**メリット**:
- より長いコンテキスト
- より高品質な出力
- 複雑な指示の理解向上

**デメリット**:
- コスト増加

### 【戦略7】温度パラメータ最適化

**効果**: ⭐⭐⭐（3/5）
**リスク**: ⭐（1/5）

**実装方法**:
````python
generation_config = {
    'temperature': 0.3,  # 低温度で一貫性向上
    'top_p': 0.95,
    'top_k': 40,
    'max_output_tokens': 8192,  # 最大出力
}
````

**メリット**:
- 出力の安定性向上
- 長い出力が可能

### 【戦略8】RAG活用（過去の成功例参照）

**効果**: ⭐⭐⭐⭐（4/5）
**リスク**: ⭐⭐（2/5）

**実装方法**:
````python
# 1. 過去の成功例をベクトル化して保存
# 2. タスク実行時に類似タスクの成功例を検索
# 3. 成功例をプロンプトに含める

similar_tasks = knowledge_manager.search_similar_tasks(task_description)

prompt = f"""
【類似タスクの成功例】
{similar_tasks[0]['output']}  # 1200行の成功例

【今回のタスク】
{task_description}

上記の成功例と同等の品質で実装してください。
"""
````

**メリット**:
- 実際の成功パターン活用
- 品質の証明済み

### 【戦略9】コード生成専門プロンプト

**効果**: ⭐⭐⭐⭐⭐（5/5）
**リスク**: ⭐（1/5）

**実装方法**:
````python
prompt = f"""
# SYSTEM ROLE
You are a code generation specialist with 15 years of experience.
Your outputs are ALWAYS production-ready, well-tested, and extensively documented.

# CRITICAL CONSTRAINTS
- MINIMUM 1000 lines of code (this is NON-NEGOTIABLE)
- MINIMUM 3 files
- EVERY function must have docstrings
- EVERY module must have comprehensive README.md (300+ lines)

# QUALITY STANDARDS
- PEP8 compliant
- Type hints everywhere
- Error handling comprehensive
- Logging implemented
- Unit tests with 90%+ coverage

# OUTPUT FORMAT
Generate complete, production-ready code in the following format:
```python
# filename: main.py
# [500-1000 lines of implementation]
```
```python
# filename: test_main.py
# [300-400 lines of tests]
```
```markdown
# filename: README.md
# [300-500 lines of documentation]
```

# TASK
{task_description}

# REMINDER
This is part of a 50,000+ line project. Your contribution must be substantial.
Generate COMPLETE implementation in ONE response. Do NOT iterate.
"""
````

**メリット**:
- 英語で明確な指示
- システムロールで専門家設定
- NON-NEGOTIABLE制約

### 【戦略10】ハイブリッドアプローチ（推奨）

**効果**: ⭐⭐⭐⭐⭐（5/5）
**リスク**: ⭐（1/5）

**実装方法**:
戦略1（構造化+Few-shot） + 戦略4（テンプレート） + 戦略9（英語プロンプト）
````python
prompt = f"""
# SYSTEM ROLE
You are a senior Python developer specializing in large-scale systems.

# SUCCESS EXAMPLE (MANDATORY REFERENCE)
Previous successful task: Database Connection Module
- main.py: 580 lines (connection pool, transactions, retry logic)
- test_main.py: 365 lines (unit, integration, mocks)
- README.md: 300 lines (overview, API docs, examples)
Total: 1,245 lines, 3 files

# TEMPLATE STRUCTURE
Use this template and expand each section:
```python
# filename: {{module_name}}.py
'''
Comprehensive module docstring (50 lines)
'''

# Imports (20 lines)
import ...

# Constants (20 lines)
CONFIG = ...

# Main Class (400 lines)
class MainClass:
    '''Class docstring (30 lines)'''
    
    def __init__(self): ...  # 20 lines
    def method_1(self): ...  # 30 lines
    def method_2(self): ...  # 30 lines
    # ... 10 more methods
    
# Utility Functions (100 lines)
def util_1(): ...
def util_2(): ...

# Error Classes (50 lines)
class CustomError: ...

# Main Entry Point (50 lines)
if __name__ == '__main__':
    ...
```

# CURRENT TASK (Part of 50,000-line project)
{task_description}

# MANDATORY DELIVERABLES
1. Main implementation: 500-1000 lines
2. Comprehensive tests: 300-400 lines  
3. Detailed README.md: 300-500 lines
4. Additional files as needed

# CRITICAL
Generate COMPLETE implementation in ONE response.
This is production code for a major system.
Quality over speed. Completeness is mandatory.
"""
````

**メリット**:
- 複数戦略の長所を統合
- 最高の成功率
- 安定した高品質出力

## 推奨実装順序

1. **即座に実装**: 戦略10（ハイブリッド）
2. **補助**: 戦略3（メタプロンプト）
3. **長期**: 戦略8（RAG）

## 実装コード

次のステップで、戦略10のハイブリッドアプローチを
high_quality_executor_v9.py として実装します。
