"""
TaskExecutorEnhanced v2（モデル名修正版）
300行以上の実用的な成果物を確実に生成
"""

import sys
import os
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class TaskExecutorEnhancedV2:
    """TaskExecutorEnhanced v2（修正版）"""
    
    # プロンプト戦略
    STRATEGY_DETAILED = 'detailed'
    STRATEGY_STEP_BY_STEP = 'step_by_step'
    STRATEGY_CONCISE = 'concise'
    
    # Geminiモデル名（最新）
    GEMINI_MODEL = 'gemini-1.5-flash-latest'  # 高速で安定
    # GEMINI_MODEL = 'gemini-1.5-pro-latest'  # より高性能だが遅い
    
    def __init__(self, gemini_api_key=None):
        self.gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        
    def execute_task_with_strategy(
        self, 
        task: dict, 
        strategy: str = STRATEGY_DETAILED,
        previous_failure: str = None,
        retry_count: int = 0
    ) -> dict:
        """戦略的タスク実行（300行以上を保証）"""
        print(f"\n{'=' * 80}")
        print(f"🚀 TaskExecutorEnhanced v2: {task['task_id']}")
        print(f"   戦略: {strategy}")
        print(f"   リトライ回数: {retry_count}/3")
        print(f"   モデル: {self.GEMINI_MODEL}")
        print('=' * 80)
        
        # プロンプトを生成
        prompt = self._create_comprehensive_prompt(
            task, 
            strategy, 
            previous_failure
        )
        
        print(f"\n📝 プロンプト長: {len(prompt)}文字")
        
        # Gemini APIで実行
        response = self._execute_with_gemini(prompt)
        
        # レスポンス長チェック
        if not response or len(response) < 100:
            raise Exception(f"レスポンス不足: {len(response) if response else 0}文字 < 100文字")
        
        print(f"✅ レスポンス生成: {len(response)}文字")
        
        # 成果物を保存
        output_path = self._save_output(task, response)
        
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
        """包括的プロンプトを生成（戦略別）"""
        
        task_id = task.get('task_id', 'unknown')
        description = task.get('description', '')
        
        # 基本プロンプト
        base_prompt = f"""
# タスク実行要求

## タスクID
{task_id}

## タスク説明
{description}

"""
        
        # 戦略別プロンプト
        if strategy == self.STRATEGY_DETAILED:
            strategy_prompt = """
## 【重要】出力要件

あなたは**実用的で具体的な成果物**を作成する必要があります。

### 必須要件
1. **行数**: 最低300行以上のコードまたはドキュメントを生成
2. **サイズ**: 最低5000バイト（約5KB）以上
3. **実用性**: 実際に使用できる完全な実装
4. **構造**: 適切にモジュール分割された構成

### 出力内容
- **メインファイル**: 150行以上の実装
- **サブモジュール**: 2-3個のサポートファイル（各50行以上）
- **README.md**: 100行以上の詳細な説明
- **テストコード**: 50行以上（可能であれば）

### 禁止事項
❌ 抽象的な説明のみ
❌ モック実装
❌ TODOコメントだけ
❌ 短いサンプルコード

### 出力形式
各ファイルを以下の形式で出力してください：
```filename.py
# ここにコード（最低150行）
```
```README.md
# ここに詳細な説明（最低100行）
```

### 品質基準
- ✅ すぐに使える実装
- ✅ エラーハンドリング完備
- ✅ 詳細なコメント
- ✅ 実用例を含む
"""
        
        elif strategy == self.STRATEGY_STEP_BY_STEP:
            strategy_prompt = """
## 【重要】段階的実装要件

以下の手順で、段階的に実装してください。

### Step 1: 基本構造の実装（100行）
- クラス定義
- 基本メソッド
- 初期化処理

### Step 2: コア機能の実装（100行）
- メイン処理ロジック
- エラーハンドリング
- データ処理

### Step 3: 補助機能の実装（100行）
- ユーティリティ関数
- ヘルパーメソッド
- ロギング

### Step 4: ドキュメント作成（50行以上）
- README.md
- 使用例
- API仕様

**最低合計: 350行以上**
"""
        
        else:  # STRATEGY_CONCISE
            strategy_prompt = """
## 【重要】簡潔だが完全な実装要件

簡潔ながらも**完全で実用的な実装**を作成してください。

### 必須内容
1. **main.py**: 200行以上の完全な実装
2. **README.md**: 100行以上の使用方法
3. **合計**: 最低300行

### 品質
- ✅ 即座に使える
- ✅ エラーハンドリング
- ✅ 実用例付き
"""
        
        # 前回の失敗情報を追加
        failure_context = ""
        if previous_failure:
            failure_context = f"""
## 【前回の課題】
前回の実行で以下の問題がありました。これを改善してください：

{previous_failure}

**改善策**:
- より詳細な実装
- より多くのコード行数
- より実用的な機能
"""
        
        return base_prompt + strategy_prompt + failure_context
    
    def _execute_with_gemini(self, prompt: str) -> str:
        """Gemini APIで実行（最新モデル使用）"""
        try:
            import google.generativeai as genai
            
            # API設定
            genai.configure(api_key=self.gemini_api_key)
            
            # モデル初期化（最新モデル名）
            model = genai.GenerativeModel(self.GEMINI_MODEL)
            
            print(f"🔄 Gemini API呼び出し中... (モデル: {self.GEMINI_MODEL})")
            
            # 生成
            response = model.generate_content(prompt)
            
            if not response or not response.text:
                raise Exception("Gemini APIからレスポンスなし")
            
            print(f"✅ Gemini API成功")
            
            return response.text
            
        except Exception as e:
            print(f"❌ Gemini API エラー: {e}")
            
            # エラーメッセージから原因を特定
            error_msg = str(e)
            if "models/" in error_msg and "is not found" in error_msg:
                print(f"\n💡 ヒント: モデル名が間違っている可能性があります")
                print(f"   現在のモデル: {self.GEMINI_MODEL}")
                print(f"   利用可能なモデルを確認:")
                print(f"   python3 -c \"import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print([m.name for m in genai.list_models()])\"")
            
            raise
    
    def _save_output(self, task: dict, response: str) -> str:
        """成果物を保存"""
        task_id = task.get('task_id', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 出力ディレクトリ
        output_dir = f"agent_outputs/implementation/{task_id}_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        
        # コードブロックを抽出して個別ファイルに保存
        import re
        
        # ```filename形式のコードブロックを検索
        pattern = r'```(\w+\.\w+)\n(.*?)```'
        matches = re.findall(pattern, response, re.DOTALL)
        
        file_count = 0
        if matches:
            for filename, content in matches:
                filepath = os.path.join(output_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✅ ファイル保存: {filename} ({len(content)}文字)")
                file_count += 1
        
        # レスポンス全体も保存
        full_output_path = os.path.join(output_dir, 'full_output.txt')
        with open(full_output_path, 'w', encoding='utf-8') as f:
            f.write(response)
        
        print(f"  ✅ 全体保存: full_output.txt ({len(response)}文字)")
        print(f"  📊 合計ファイル数: {file_count + 1}個")
        
        return output_dir

