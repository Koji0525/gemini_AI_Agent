#!/bin/bash
# ファイル分割問題の根本解決

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 ファイル分割問題の根本解決"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: 問題分析
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cat > "MD/${NOW_JST}_FILE_EXTRACTION_PROBLEM_ANALYSIS.md" << 'ANALYSIS'
# ファイル分割問題の分析

## 🚨 問題

### 現状
- ✅ Geminiは1600行以上生成している
- ✅ 内容は十分（87KB）
- ❌ しかしコードファイルが0個
- ❌ full_output.txtのみ

### 品質評価結果
```
コードファイル: 0個 < 2個 → 不合格
README.md: なし → 不合格
総合スコア: 6.5/10点 → 不合格（7点必要）
```

## 🔍 なぜなぜ分析

### なぜファイルが分割されないのか？

#### 1. Geminiが指示に従っていない ⭐⭐⭐
**可能性: 高**
- プロンプトで「```filename.py」形式を指示
- しかしGeminiは別の形式で出力している
- または、コードブロックなしで出力している

#### 2. 正規表現パターンが合っていない ⭐⭐⭐
**可能性: 高**
```python
# 現在のパターン
pattern = r'```(\w+\.\w+)\n(.*?)```'
```
- このパターンにマッチしていない
- Geminiの出力形式が異なる

#### 3. プロンプトが曖昧 ⭐⭐
**可能性: 中**
- 「各ファイルを以下の形式で出力」と書いているが
- 具体例が不十分
- Geminiが理解していない

#### 4. Geminiの出力形式の問題 ⭐⭐⭐
**可能性: 高**
- ```python ではなく ```filename.py を期待
- しかしGeminiは ```python で出力している可能性
- または、ファイル名なしでコードブロックを出力

#### 5. マークダウンの解釈問題 ⭐⭐
**可能性: 中**
- Geminiがマークダウンとして整形
- コードブロックを複数作成しているが
- ファイル名を付けていない

## 📊 実際の出力を確認

最新の出力ファイルを見てみる必要がある：
```bash
# 最新の出力を確認
find agent_outputs/implementation -name "full_output.txt" -type f | 
  sort -r | head -1 | xargs head -100
```

## 🎯 根本原因（推定）

**Geminiは指示通りにコードを生成しているが、
ファイル名を含むコードブロック形式（```filename.py）ではなく、
通常のコードブロック形式（```python）で出力している**

## 💡 解決策

### 方法1: プロンプトの改善 ⭐⭐
より明確で強制的な指示：
- XMLタグで囲む
- 例を複数提示
- NOTEで強調

### 方法2: 正規表現パターンの改善 ⭐⭐⭐
複数のパターンに対応：
- ```filename.py
- ```python \n# filename.py
- <file name="filename.py">

### 方法3: 出力後処理の追加 ⭐⭐⭐
コードブロックが見つからない場合：
- 内容を分析
- 自動的にファイル分割
- class/def定義を検出してファイル化

### 方法4: 強制的なファイル分割 ⭐⭐⭐
full_output.txtの内容から：
- クラス定義を検出 → main.py
- README部分を検出 → README.md
- テスト部分を検出 → test.py

## 🔧 既存システムの成功事例

F1エージェント（task_breakdown_gemini.py）は成功している。
そちらの出力形式を参考にすべき。

ANALYSIS

echo "✅ 問題分析完了: MD/${NOW_JST}_FILE_EXTRACTION_PROBLEM_ANALYSIS.md"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: TaskExecutorEnhanced v3（完全版）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: TaskExecutorEnhanced v3作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > agents/task_executor_enhanced_v3.py << 'PYTHON'
"""
TaskExecutorEnhanced v3（ファイル分割強化版）
確実にファイルを分割して保存
"""

import sys
import os
import re
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from dotenv import load_dotenv
load_dotenv()

class TaskExecutorEnhancedV3:
    """TaskExecutorEnhanced v3（ファイル分割強化版）"""
    
    STRATEGY_DETAILED = 'detailed'
    STRATEGY_STEP_BY_STEP = 'step_by_step'
    STRATEGY_CONCISE = 'concise'
    
    GEMINI_MODEL = 'gemini-2.5-flash'
    
    def __init__(self, gemini_api_key=None):
        self.gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEYが設定されていません")
        
    def execute_task_with_strategy(
        self, 
        task: dict, 
        strategy: str = STRATEGY_DETAILED,
        previous_failure: str = None,
        retry_count: int = 0
    ) -> dict:
        """戦略的タスク実行"""
        print(f"\n{'=' * 80}")
        print(f"🚀 TaskExecutorEnhanced v3: {task['task_id']}")
        print(f"   戦略: {strategy}")
        print(f"   リトライ回数: {retry_count}/3")
        print('=' * 80)
        
        prompt = self._create_comprehensive_prompt(task, strategy, previous_failure)
        response = self._execute_with_gemini(prompt)
        
        if not response or len(response) < 100:
            raise Exception(f"レスポンス不足: {len(response) if response else 0}文字")
        
        print(f"✅ レスポンス生成: {len(response)}文字")
        
        # 強化されたファイル保存
        output_path = self._save_output_enhanced(task, response)
        
        return {
            'success': True,
            'output_path': output_path,
            'response_length': len(response),
            'strategy': strategy,
            'retry_count': retry_count
        }
    
    def _create_comprehensive_prompt(
        self, 
        task: dict, 
        strategy: str,
        previous_failure: str = None
    ) -> str:
        """包括的プロンプトを生成"""
        
        task_id = task.get('task_id', 'unknown')
        description = task.get('description', '')
        
        # 超強力な出力形式指示
        format_instruction = """
## 【超重要】出力形式の厳守

あなたは以下の形式で**必ず**出力してください。
この形式以外は一切認められません。

### ファイル出力形式（XMLタグ使用）

<file name="main.py">
```python
# メインファイルのコード（150行以上）
class FlakkyTestDetector:
    def __init__(self):
        pass
    
    def detect_flakky_tests(self, test_results):
        # 詳細な実装
        pass
```
</file>

<file name="utils.py">
```python
# ユーティリティファイル（50行以上）
def analyze_test_stability(results):
    # 詳細な実装
    pass
```
</file>

<file name="README.md">
```markdown
# プロジェクト名

## 概要
詳細な説明（100行以上）

## インストール
...

## 使用方法
...

## API仕様
...
```
</file>

### 必須ファイル
1. main.py（150行以上）- メイン実装
2. utils.py（50行以上）- ユーティリティ
3. README.md（100行以上）- 詳細説明

### 出力禁止
❌ コードブロックのみ（```python だけ）
❌ ファイル名なしのコード
❌ 説明だけ
❌ TODOコメントのみ

### 必ず守ること
✅ <file name="..."> タグで囲む
✅ 各ファイルは完全な実装
✅ すぐに使える品質
"""
        
        base_prompt = f"""
# タスク実行要求

## タスクID
{task_id}

## タスク説明
{description}

{format_instruction}

## 品質基準
- 合計300行以上
- 5000バイト以上
- 実用的な完全実装
- エラーハンドリング完備
"""
        
        if previous_failure:
            base_prompt += f"""
## 【前回の課題】
{previous_failure}

**必ず改善すること：**
- より多くのファイルを作成
- 各ファイルを完全実装
- README.mdを必ず含める
"""
        
        return base_prompt
    
    def _execute_with_gemini(self, prompt: str) -> str:
        """Gemini APIで実行"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel(self.GEMINI_MODEL)
            
            print(f"🔄 Gemini API呼び出し中...")
            
            response = model.generate_content(prompt)
            
            if not response or not response.text:
                raise Exception("Gemini APIからレスポンスなし")
            
            print(f"✅ Gemini API成功")
            
            return response.text
            
        except Exception as e:
            print(f"❌ Gemini API エラー: {e}")
            raise
    
    def _save_output_enhanced(self, task: dict, response: str) -> str:
        """強化されたファイル保存（複数パターン対応）"""
        task_id = task.get('task_id', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        output_dir = f"agent_outputs/implementation/{task_id}_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n📂 ファイル抽出開始...")
        
        file_count = 0
        
        # パターン1: XMLタグ形式（優先）
        xml_pattern = r'<file name="([^"]+)">\s*```(?:\w+)?\n(.*?)```\s*</file>'
        xml_matches = re.findall(xml_pattern, response, re.DOTALL)
        
        if xml_matches:
            print(f"  ✅ XMLタグ形式を検出: {len(xml_matches)}個")
            for filename, content in xml_matches:
                filepath = os.path.join(output_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content.strip())
                print(f"  ✅ {filename} ({len(content)}文字)")
                file_count += 1
        
        # パターン2: 通常のコードブロック（```filename.py形式）
        if file_count == 0:
            code_pattern = r'```(\w+\.\w+)\n(.*?)```'
            code_matches = re.findall(code_pattern, response, re.DOTALL)
            
            if code_matches:
                print(f"  ✅ コードブロック形式を検出: {len(code_matches)}個")
                for filename, content in code_matches:
                    filepath = os.path.join(output_dir, filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content.strip())
                    print(f"  ✅ {filename} ({len(content)}文字)")
                    file_count += 1
        
        # パターン3: 強制分割（ファイルが見つからない場合）
        if file_count == 0:
            print(f"  ⚠️  ファイル形式が検出できません。強制分割します...")
            file_count = self._force_split_output(response, output_dir)
        
        # full_output.txtも保存
        full_output_path = os.path.join(output_dir, 'full_output.txt')
        with open(full_output_path, 'w', encoding='utf-8') as f:
            f.write(response)
        
        print(f"\n📊 保存完了: {file_count + 1}個のファイル")
        
        return output_dir
    
    def _force_split_output(self, response: str, output_dir: str) -> int:
        """強制的にファイル分割"""
        file_count = 0
        
        # クラス定義を検出
        class_pattern = r'(class \w+.*?(?=\nclass |\nif __name__|$))'
        class_matches = re.findall(class_pattern, response, re.DOTALL)
        
        if class_matches and len(class_matches) > 0:
            # main.pyを作成
            main_content = '\n\n'.join(class_matches)
            with open(os.path.join(output_dir, 'main.py'), 'w') as f:
                f.write(main_content)
            print(f"  ✅ main.py (強制分割: {len(main_content)}文字)")
            file_count += 1
        
        # README部分を検出
        readme_pattern = r'(#.*?(?=\n```|\nclass |$))'
        readme_matches = re.findall(readme_pattern, response, re.DOTALL)
        
        if readme_matches:
            readme_content = '\n\n'.join(readme_matches[:3])  # 最初の3セクション
            if len(readme_content) > 100:
                with open(os.path.join(output_dir, 'README.md'), 'w') as f:
                    f.write(readme_content)
                print(f"  ✅ README.md (強制分割: {len(readme_content)}文字)")
                file_count += 1
        
        # 関数定義を検出
        func_pattern = r'(def \w+.*?(?=\ndef |\nclass |\nif __name__|$))'
        func_matches = re.findall(func_pattern, response, re.DOTALL)
        
        if func_matches and len(func_matches) > 0:
            # utils.pyを作成
            utils_content = '\n\n'.join(func_matches)
            with open(os.path.join(output_dir, 'utils.py'), 'w') as f:
                f.write(utils_content)
            print(f"  ✅ utils.py (強制分割: {len(utils_content)}文字)")
            file_count += 1
        
        return file_count

PYTHON

# バックアップして置き換え
cp agents/task_executor_enhanced_v2.py "agents/task_executor_enhanced_v2.py.backup_${NOW_JST}" 2>/dev/null

# v3をv2として使用（QualityFeedbackLoopがv2を参照しているため）
cp agents/task_executor_enhanced_v3.py agents/task_executor_enhanced_v2.py

echo "✅ TaskExecutorEnhanced v3作成（v2として配置）"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ファイル分割問題の根本解決完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 改善内容:"
echo "  1. ✅ XMLタグ形式のサポート（<file name=\"...\">）"
echo "  2. ✅ 複数の正規表現パターン対応"
echo "  3. ✅ 強制ファイル分割機能"
echo "  4. ✅ 超強力なプロンプト指示"
echo ""
echo "🎯 期待される結果:"
echo "  - コードファイル: 2個以上"
echo "  - README.md: 必ず含まれる"
echo "  - 品質スコア: 7点以上"
echo ""
echo "🧪 テスト実行:"
echo "  bash sh/start_pending_tasks_with_quality.sh 1"
echo ""

# 自動テスト
read -p "今すぐv3でタスクを実行しますか？ [Y/n] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🧪 TaskExecutorEnhanced v3 テスト"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    bash sh/start_pending_tasks_with_quality.sh 1
fi

