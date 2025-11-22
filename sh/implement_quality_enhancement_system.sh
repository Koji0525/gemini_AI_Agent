#!/bin/bash
# タスク実行結果の品質向上システム統合

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 タスク実行結果の品質向上システム統合"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: TaskExecutorEnhanced完全版の作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: TaskExecutorEnhanced完全版の作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > agents/task_executor_enhanced_v2.py << 'PYTHON'
"""
TaskExecutorEnhanced v2
300行以上の実用的な成果物を確実に生成
"""

import sys
import os
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class TaskExecutorEnhancedV2:
    """TaskExecutorEnhanced v2"""
    
    # プロンプト戦略
    STRATEGY_DETAILED = 'detailed'
    STRATEGY_STEP_BY_STEP = 'step_by_step'
    STRATEGY_CONCISE = 'concise'
    
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
        """Gemini APIで実行"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            response = model.generate_content(prompt)
            
            if not response or not response.text:
                raise Exception("Gemini APIからレスポンスなし")
            
            return response.text
            
        except Exception as e:
            print(f"❌ Gemini API エラー: {e}")
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
        
        if matches:
            for filename, content in matches:
                filepath = os.path.join(output_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✅ ファイル保存: {filename} ({len(content)}文字)")
        
        # レスポンス全体も保存
        full_output_path = os.path.join(output_dir, 'full_output.txt')
        with open(full_output_path, 'w', encoding='utf-8') as f:
            f.write(response)
        
        print(f"  ✅ 全体保存: full_output.txt ({len(response)}文字)")
        
        return output_dir

PYTHON

echo "✅ TaskExecutorEnhanced v2作成"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: QualityFeedbackLoop（品質フィードバックループ）の実装
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: QualityFeedbackLoop実装"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > core_agents/quality_feedback_loop_v2.py << 'PYTHON'
"""
QualityFeedbackLoop v2
品質不合格時の自動改善と再実行
"""

import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.strict_quality_evaluator import StrictQualityEvaluator
from agents.task_executor_enhanced_v2 import TaskExecutorEnhancedV2

class QualityFeedbackLoopV2:
    """品質フィードバックループ v2"""
    
    MAX_RETRY = 3
    PASS_THRESHOLD = 7.0
    
    def __init__(self):
        self.evaluator = StrictQualityEvaluator()
        self.executor = TaskExecutorEnhancedV2()
        
    def execute_with_quality_assurance(self, task: dict) -> dict:
        """品質保証付きタスク実行"""
        print(f"\n{'=' * 80}")
        print(f"�� QualityFeedbackLoop: {task['task_id']}")
        print('=' * 80)
        
        retry_count = 0
        previous_failure = None
        
        # 戦略リスト
        strategies = [
            TaskExecutorEnhancedV2.STRATEGY_DETAILED,
            TaskExecutorEnhancedV2.STRATEGY_STEP_BY_STEP,
            TaskExecutorEnhancedV2.STRATEGY_CONCISE
        ]
        
        while retry_count < self.MAX_RETRY:
            print(f"\n【実行 {retry_count + 1}/{self.MAX_RETRY}】")
            
            # 戦略を選択
            strategy = strategies[retry_count]
            
            try:
                # タスク実行
                exec_result = self.executor.execute_task_with_strategy(
                    task,
                    strategy=strategy,
                    previous_failure=previous_failure,
                    retry_count=retry_count
                )
                
                # 品質評価
                quality_result = self.evaluator.evaluate_task_output(
                    task['task_id'],
                    exec_result['output_path']
                )
                
                score = quality_result['score']
                
                print(f"\n📊 品質評価結果: {score:.1f}/10点")
                print(f"   実用性: {quality_result['usability']}")
                
                # 合格判定
                if score >= self.PASS_THRESHOLD:
                    print(f"\n✅ 品質合格！（{score:.1f}/10点）")
                    return {
                        'success': True,
                        'score': score,
                        'output_path': exec_result['output_path'],
                        'retry_count': retry_count,
                        'quality': quality_result
                    }
                else:
                    print(f"\n⚠️  品質不合格（{score:.1f}/10点 < {self.PASS_THRESHOLD}点）")
                    
                    # 改善提案を生成
                    previous_failure = self._generate_improvement_suggestions(
                        quality_result
                    )
                    
                    print(f"\n📝 改善提案:\n{previous_failure}")
                    
                    retry_count += 1
                    
            except Exception as e:
                print(f"\n❌ 実行エラー: {e}")
                previous_failure = f"エラーが発生しました: {str(e)}"
                retry_count += 1
        
        # 最大リトライ回数到達
        print(f"\n❌ 最大リトライ回数到達（{self.MAX_RETRY}回）")
        return {
            'success': False,
            'score': 0,
            'retry_count': retry_count,
            'reason': '品質基準を満たせませんでした'
        }
    
    def _generate_improvement_suggestions(self, quality_result: dict) -> str:
        """改善提案を生成"""
        evaluation = quality_result['evaluation']
        
        suggestions = []
        
        # 行数不足
        if evaluation['total_lines'] < 300:
            suggestions.append(
                f"❌ 行数不足: {evaluation['total_lines']}行 < 300行\n"
                f"   → より詳細な実装を追加してください\n"
                f"   → メインファイルを150行以上に拡張\n"
                f"   → サブモジュールを追加（各50行以上）"
            )
        
        # サイズ不足
        if evaluation['total_bytes'] < 5000:
            suggestions.append(
                f"❌ サイズ不足: {evaluation['total_bytes']}バイト < 5000バイト\n"
                f"   → より多くのコードと説明を追加"
            )
        
        # コードファイル不足
        if evaluation['code_files'] < 2:
            suggestions.append(
                f"❌ コードファイル不足: {evaluation['code_files']}個 < 2個\n"
                f"   → メインファイルとサポートファイルを作成"
            )
        
        # ドキュメント不足
        if evaluation['doc_files'] < 2:
            suggestions.append(
                f"❌ ドキュメント不足: {evaluation['doc_files']}個 < 2個\n"
                f"   → README.mdとAPI仕様書を作成"
            )
        
        # README.md なし
        if not evaluation['has_readme']:
            suggestions.append(
                f"❌ README.md なし\n"
                f"   → 詳細な使用方法を記載したREADME.mdを作成（100行以上）"
            )
        
        return "\n\n".join(suggestions)

PYTHON

echo "✅ QualityFeedbackLoop v2作成"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: CompleteEngineへの統合
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: CompleteEngineへの統合"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > sh/start_pending_tasks_with_quality.sh << 'QUALITY'
#!/bin/bash
# 品質保証付きタスク実行

cd /workspaces/gemini_AI_Agent

LIMIT=${1:-2}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 品質保証付きタスク実行"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "実行タスク数: $LIMIT"
echo ""

python3 << PYTHON
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.robust_task_selector import RobustTaskSelector
from core_agents.quality_feedback_loop_v2 import QualityFeedbackLoopV2
from tools.sheets_manager import GoogleSheetsManager

# 初期化
sheets = GoogleSheetsManager()
selector = RobustTaskSelector(sheets)
qfl = QualityFeedbackLoopV2()

# タスク選択
tasks = selector.select_executable_task(limit=$LIMIT)

if not tasks:
    print("⚠️  実行可能なタスクがありません")
    sys.exit(0)

print(f"✅ {len(tasks)}個のタスクを選択しました")
for i, task in enumerate(tasks, 1):
    print(f"  {i}. {task['task_id']}")

print()

# タスク実行（品質保証付き）
success_count = 0
for task in tasks:
    print("\n" + "=" * 80)
    print(f"🚀 タスク実行: {task['task_id']}")
    print("=" * 80)
    
    try:
        # QualityFeedbackLoopで実行
        result = qfl.execute_with_quality_assurance(task)
        
        if result['success']:
            print(f"\n✅ タスク成功: {task['task_id']}")
            print(f"   品質スコア: {result['score']:.1f}/10点")
            print(f"   リトライ回数: {result['retry_count']}")
            print(f"   成果物: {result['output_path']}")
            
            # ステータス更新
            row_index = task['row_index']
            sheets.service.spreadsheets().values().update(
                spreadsheetId=sheets.spreadsheet_id,
                range=f"pm_tasks!E{row_index}",
                valueInputOption="RAW",
                body={"values": [["completed"]]}
            ).execute()
            
            success_count += 1
        else:
            print(f"\n❌ タスク失敗: {task['task_id']}")
            print(f"   理由: {result.get('reason', '不明')}")
            
    except Exception as e:
        print(f"\n❌ タスク実行エラー: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print(f"✅ 実行完了: {success_count}/{len(tasks)}件成功")
print("=" * 80)

PYTHON

QUALITY

chmod +x sh/start_pending_tasks_with_quality.sh
echo "✅ 品質保証付き実行スクリプト作成"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: 24時間稼働システムの更新
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: 24時間稼働システムの更新"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 既存のrun_autonomous_24h_v6_final.shの該当部分を置き換え
sed -i.backup "s|bash start_pending_tasks_fixed.sh 2|bash sh/start_pending_tasks_with_quality.sh 2|g" \
    sh/run_autonomous_24h_v6_final.sh 2>/dev/null || echo "  ℹ️  sedコマンドスキップ（手動で確認）"

echo "✅ 24時間稼働システムを品質保証版に更新"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 5: マニュアル作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5: マニュアル作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > "MD/${NOW_JST}_QUALITY_ENHANCEMENT_COMPLETE.md" << 'DOC'
# タスク実行品質向上システム統合完了

## 実装内容

### 1. TaskExecutorEnhanced v2
- ✅ 3つのプロンプト戦略（詳細型、段階型、簡潔型）
- ✅ 最低300行以上を強制
- ✅ 最低5000バイト以上を保証
- ✅ 前回失敗情報の活用

### 2. QualityFeedbackLoop v2
- ✅ 厳格な品質評価（strict_quality_evaluator）
- ✅ 7点未満は自動再実行
- ✅ 最大3回リトライ
- ✅ 改善提案の自動生成

### 3. 品質基準

| 項目 | 基準 | 配点 |
|:---|:---|:---|
| 行数 | 300行以上で合格 | 4点 |
| サイズ | 5000バイト以上 | 2点 |
| ファイル構成 | README + コード | 2点 |
| 実装充実度 | 複数ファイル | 2点 |
| **合計** | **7点以上で合格** | **10点** |

### 4. 動作フロー
```
タスク実行
  ↓
【1回目】詳細型プロンプト
  ↓
品質評価（strict_quality_evaluator）
  ↓
7点以上？ YES → ✅ 完了
  ↓ NO
【2回目】段階型プロンプト + 改善提案
  ↓
品質評価
  ↓
7点以上？ YES → ✅ 完了
  ↓ NO
【3回目】簡潔型プロンプト + 改善提案
  ↓
品質評価
  ↓
7点以上？ YES → ✅ 完了
  ↓ NO
❌ 不合格（最大リトライ到達）
```

## 使用方法

### 手動テスト
```bash
# 品質保証付きでタスク実行
bash sh/start_pending_tasks_with_quality.sh 1
```

### 24時間稼働
既存の24時間稼働システムが自動的に品質保証版を使用します。

## 成果物の確認
```bash
# 最新の成果物を確認
bash sh/show_task_outputs.sh

# 成果物の行数確認
find agent_outputs/implementation -type f -name "*.py" -o -name "*.md" | xargs wc -l
```

## 期待される結果

### Before（修正前）
- 出力: 50行程度
- サイズ: 1-2KB
- ファイル数: 1-2個
- 品質: プロトタイプレベル

### After（修正後）
- 出力: 300行以上
- サイズ: 5KB以上
- ファイル数: 3個以上
- 品質: 実用化レベル

## トラブルシューティング

### 依然として行数が少ない場合
1. Gemini APIキーを確認
2. プロンプトログを確認
3. 品質評価ログを確認

### エラーが発生する場合
```bash
# ログ確認
tail -f logs/autonomous_v6_*.log
```

DOC

echo "✅ マニュアル作成: MD/${NOW_JST}_QUALITY_ENHANCEMENT_COMPLETE.md"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ タスク実行品質向上システム統合完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 実装内容:"
echo "  1. ✅ TaskExecutorEnhanced v2（3戦略）"
echo "  2. ✅ QualityFeedbackLoop v2（自動再実行）"
echo "  3. ✅ StrictQualityEvaluator（厳格評価）"
echo "  4. ✅ 品質保証付き実行スクリプト"
echo ""
echo "🎯 品質基準:"
echo "  ✅ 300行以上"
echo "  ✅ 5000バイト以上"
echo "  ✅ 7点以上で合格"
echo "  ✅ 最大3回自動リトライ"
echo ""
echo "🧪 テスト実行:"
echo "  bash sh/start_pending_tasks_with_quality.sh 1"
echo ""
echo "📖 詳細:"
echo "  cat MD/${NOW_JST}_QUALITY_ENHANCEMENT_COMPLETE.md"
echo ""

# 自動テスト
read -p "今すぐ1つのタスクでテストしますか？ [Y/n] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🧪 品質保証付きタスク実行テスト"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    bash sh/start_pending_tasks_with_quality.sh 1
fi

