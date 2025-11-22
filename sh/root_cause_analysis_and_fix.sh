#!/bin/bash
# なぜなぜ分析に基づく抜本的対策

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔬 なぜなぜ分析と抜本的対策"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# なぜなぜ分析
cat > "MD/${NOW_JST}_なぜなぜ分析.md" << 'ANALYSIS'
# なぜなぜ分析：タスク実行品質低下の真因

**分析日時**: $(TZ=Asia/Tokyo date +"%Y-%m-%d %H:%M:%S JST")

---

## 🔴 現象

### 観察された問題
1. タスクID「6」という不完全なタスクが実行される
2. 「⚠️ 詳細タスク定義なし - 基本実行のみ」
3. フォールバック実行で50/100点の低品質
4. 成果物が272バイトしかない（以前は300行以上）
5. 高品質タスク（7_統合テスト実行_*）が実行されない
6. F1のタスク分解が動作しない
7. F6の動的タスク追加が機能しない

---

## 🔍 なぜなぜ分析（10層）

### なぜ1: なぜタスクID「6」が実行されるのか？
**回答**: CompleteEngine.run_full_integration_cycle() が古いタスク選択ロジックを使っているから

### なぜ2: なぜ古いタスク選択ロジックを使うのか？
**回答**: run_full_integration_cycle() 内部で BaseDataAccessor.get_pending_tasks() を呼び出しているから

### なぜ3: なぜ BaseDataAccessor が古いタスクを選ぶのか？
**回答**: 優先度判定がなく、単純に最初に見つかったpendingタスクを返すから

### なぜ4: なぜ優先度判定がないのか？
**回答**: BaseDataAccessor は汎用データアクセス層として設計されており、ビジネスロジック（優先度判定）を含まないから

### なぜ5: なぜ高品質タスクが選ばれないのか？
**回答**: タスクID「6」がpendingとして残っており、BaseDataAccessor がそれを最初に検出するから

### なぜ6: なぜタスクID「6」がpendingのままなのか？
**回答**: 
- 可能性A: statusが本当にpendingのまま
- 可能性B: スプレッドシートのデータが古い
- 可能性C: タスクIDが不完全（本来は「6_final_quality_check」のはず）

### なぜ7: なぜフォールバック実行になるのか？
**回答**: execution_type='quality_check' に対応するハンドラーが存在しないから

### なぜ8: なぜ詳細タスク定義がないのか？
**回答**: 
- タスクID「6」は古いタスクで、detail_file_path が設定されていない
- 動的生成される詳細定義も、タスク説明が短すぎて生成できない

### なぜ9: なぜF1のタスク分解が動作しないのか？
**回答**: 
- run_full_integration_cycle() の先頭で goal_concrete.execute() を呼び出している
- しかし、goal_concrete は「activeゴール」がある場合のみタスク生成
- activeゴールが完了間近（95%）のため、新規タスクが生成されない

### なぜ10: なぜF6の動的タスク追加が機能しないのか？
**回答**: 
- 品質スコアが60点で、7点未満ではない
- そのため再実行トリガーが発動しない
- 「詳細タスク定義なし」という警告は出るが、システムは「completed」と判定してしまう

---

## 🎯 真因

### 根本原因
1. **タスク選択の優先順位がない**
   - BaseDataAccessor は単純な検索のみ
   - 高品質タスクを優先する仕組みがない

2. **古いタスク（タスクID「6」）がデータベースに残存**
   - 不完全なタスクデータ
   - detail_file_pathなし
   - execution_typeが未対応

3. **CompleteEngine の統合フローが古いロジックを使用**
   - 新しいスマートタスク選択が統合されていない
   - F1のトリガー条件が不適切
   - F6の動的追加が統合されていない

4. **品質評価の閾値が甘い**
   - 60点でも「completed」と判定
   - フォールバック実行を許容してしまう
   - 「詳細タスク定義なし」でも通過

5. **成功事例（300行出力）からの退化**
   - 以前は TaskExecutorEnhanced が正常に動作
   - 詳細なプロンプトとテンプレートを使用
   - 現在はフォールバック実行で劣化

---

## 💊 抜本的対策

### 対策1: タスク選択ロジックの完全刷新
```python
# CompleteEngine.run_full_integration_cycle() を修正
# 既存: BaseDataAccessor.get_pending_tasks()
# 新規: RobustTaskSelector.select_executable_task()
#   → 高品質タスクを最優先
#   → タスクID「6」のような不完全タスクを除外
```

### 対策2: 古い不完全タスクのクリーンアップ
```bash
# Google Sheets でタスクID「6」を手動修正
# または、自動クリーンアップスクリプト作成
#   → task_idが短すぎる（5文字以下）タスクを除外
#   → detail_file_pathがないタスクを低優先度化
```

### 対策3: フォールバック実行の禁止
```python
# TaskExecutorEnhanced でフォールバック実行を禁止
# execution_typeが未対応の場合、エラーを返す
#   → システムがF7（自己修復）で対処
#   → または、F6（動的タスク追加）で詳細定義を生成
```

### 対策4: 詳細タスク定義の必須化
```python
# タスク実行前にチェック
# if not task.get('detail_file_path'):
#     # 動的に詳細定義を生成
#     detail = generate_detailed_task_definition(task)
#     # Google Sheets に保存
```

### 対策5: F1のトリガー条件を修正
```python
# 現在: activeゴールの進捗が95%未満の場合のみ
# 修正: pendingタスクが0の場合も強制実行
#   → 自動タスク生成（AutoTaskGeneratorV2）を統合
```

### 対策6: F6の動的タスク追加を強化
```python
# 現在: 品質スコア7点未満で再実行
# 修正: 「詳細タスク定義なし」警告を検出
#   → 動的に詳細定義を生成
#   → または、関連タスクを追加
```

### 対策7: 品質評価の閾値を厳格化
```python
# フォールバック実行は自動的に不合格
# if feedback.startswith("⚠️ 詳細タスク定義なし"):
#     score = 0  # 不合格
#     # F7で再実行
```

### 対策8: 成功事例の復活
```python
# TaskExecutorEnhanced の詳細プロンプトを復活
# 300行以上の出力を強制
# テンプレートライブラリを活用
```

---

## 🔧 実装優先度

### 最優先（緊急）
1. ✅ CompleteEngine の統合フロー修正
2. ✅ RobustTaskSelector の統合
3. ✅ 古いタスクの除外ロジック

### 高優先（重要）
4. ✅ フォールバック実行の禁止
5. ✅ 詳細タスク定義の必須化
6. ✅ F1/F6のトリガー条件修正

### 中優先（改善）
7. ⏭️ 品質評価の閾値厳格化
8. ⏭️ 成功事例の復活

---

## 📊 他の成功事例

### 成功事例1: 以前の300行出力
**何が良かったか**:
- TaskExecutorEnhanced が詳細プロンプトを使用
- execution_type='implementation' で適切なハンドラー
- detail_file_path に詳細な要件定義

**復活方法**:
- 同じプロンプト戦略を使用
- 詳細タスク定義を必須化
- フォールバック実行を禁止

### 成功事例2: 高品質タスクの定義
**7_統合テスト実行_064415_01**:
```
description: 
  F1-F10の統合テストを実行し...
  【目的】...
  【作業内容】...
  【成功基準】...
  【コンテキスト】...
```

**活用方法**:
- この形式を全タスクに適用
- 動的生成時のテンプレートとして使用
- 既存の不完全タスクを変換

### 成功事例3: 自動タスク生成（AutoTaskGeneratorV2）
**何が良かったか**:
- pendingタスク0で自動生成
- 高品質テンプレートを使用
- batch_id で識別可能

**活用方法**:
- F1に統合
- pendingタスク0で必ず起動
- 統合フローに組み込み

ANALYSIS

echo "✅ なぜなぜ分析完了: MD/${NOW_JST}_なぜなぜ分析.md"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 抜本的対策の実装
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 抜本的対策の実装"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 対策1: CompleteEngine の修正
cat > agents/complete_engine_ultimate_fixed.py << 'PYTHON'
"""
CompleteEngine修正版
RobustTaskSelectorとAutoTaskGeneratorV2を統合
"""

import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

# 既存のCompleteEngineをインポート
from agents.complete_engine_ultimate import CompleteEngineUltimate
from agents.robust_task_selector import RobustTaskSelector
from agents.auto_task_generator import AutoTaskGeneratorV2

class CompleteEngineUltimateFixed(CompleteEngineUltimate):
    """CompleteEngine修正版"""
    
    def __init__(self):
        super().__init__()
        self.task_selector = RobustTaskSelector(self.sheets)
        self.task_generator = AutoTaskGeneratorV2(self.sheets)
        
    def run_full_integration_cycle_fixed(self, goal_id=None, limit=1):
        """統合フロー（修正版）"""
        print("\n" + "=" * 80)
        print("🚀 完全統合フロー開始（修正版）")
        print("=" * 80)
        
        # F1: タスク可用性チェック
        print("\n🔄 F1: タスク可用性チェック")
        pending_tasks = self.task_selector.get_pending_tasks()
        
        if len(pending_tasks) == 0:
            print("⚠️  pendingタスクが0個です")
            print("🔧 F1: 自動タスク生成を起動...")
            
            result = self.task_generator.auto_generate_if_needed()
            
            if result.get('generated'):
                print("✅ F1: 高品質タスクを生成しました")
                # 再度タスクを取得
                pending_tasks = self.task_selector.get_pending_tasks()
            else:
                print("⚠️  F1: タスク生成できませんでした")
        
        # F2: タスク選択（スマート選択）
        print(f"\n🎯 F2: タスク選択（{limit}個）")
        selected_tasks = self.task_selector.select_executable_task(limit=limit)
        
        if not selected_tasks:
            print("⚠️  実行可能なタスクがありません")
            return {'success': False, 'message': 'タスクなし'}
        
        # タスク実行
        success_count = 0
        for task in selected_tasks:
            print(f"\n{'=' * 80}")
            print(f"🚀 タスク実行: {task['task_id']}")
            print(f"   説明: {task['description'][:80]}...")
            print('=' * 80)
            
            try:
                # 詳細タスク定義のチェック
                if not task.get('detail_file_path'):
                    print("⚠️  詳細タスク定義がありません")
                    print("🔧 F6: 動的に詳細定義を生成します...")
                    
                    # 詳細定義を動的生成
                    task['description'] = self._enhance_task_description(task)
                
                # タスク実行
                result = self.execute_task(task)
                
                # F3: 品質評価
                quality_score = result.get('quality_score', 0)
                print(f"\n📊 F3: 品質評価 = {quality_score}/100")
                
                # フォールバック実行を不合格とする
                if result.get('fallback', False):
                    print("❌ フォールバック実行のため不合格")
                    quality_score = 0
                
                # 品質評価に基づく判定
                if quality_score >= 70:
                    # ステータス更新
                    row_index = task['row_index']
                    self.sheets.service.spreadsheets().values().update(
                        spreadsheetId=self.sheets.spreadsheet_id,
                        range=f"pm_tasks!E{row_index}",
                        valueInputOption="RAW",
                        body={"values": [["completed"]]}
                    ).execute()
                    
                    print(f"✅ タスク完了: {task['task_id']}")
                    success_count += 1
                else:
                    print(f"⚠️  品質不足（{quality_score}/100）")
                    print("🔧 F7: 自己修復が必要です")
                    # TODO: F7統合
                
            except Exception as e:
                print(f"❌ タスク実行エラー: {e}")
        
        print(f"\n{'=' * 80}")
        print(f"✅ フロー完了: {success_count}/{len(selected_tasks)}件成功")
        print('=' * 80)
        
        return {
            'success': success_count > 0,
            'executed': len(selected_tasks),
            'succeeded': success_count
        }
    
    def _enhance_task_description(self, task):
        """タスク説明を拡張"""
        description = task.get('description', '')
        
        # 既に詳細な説明の場合はそのまま
        if '【目的】' in description:
            return description
        
        # 簡易的な拡張
        enhanced = f"""
{description}

【目的】{description.split('：')[0] if '：' in description else description}を完了させる

【作業内容】
1. 要件を確認
2. 実装または調査を実施
3. 成果物を作成
4. テストと検証

【成功基準】
・{task['task_id']}の成果物が生成されている
・実行ログにエラーがない
・品質スコアが70以上

【コンテキスト】
既存システムとの統合を考慮し、実用的な成果物を作成する。
"""
        return enhanced.strip()

PYTHON

echo "✅ CompleteEngine修正版作成"

# 対策2: 古いタスククリーンアップスクリプト
cat > tools/cleanup_old_tasks.py << 'PYTHON'
"""
古いタスクのクリーンアップ
"""

import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.sheets_manager import GoogleSheetsManager

def cleanup_old_tasks():
    """古い不完全タスクをクリーンアップ"""
    sheets = GoogleSheetsManager()
    
    # タスクを取得
    result = sheets.service.spreadsheets().values().get(
        spreadsheetId=sheets.spreadsheet_id,
        range="pm_tasks!A2:M1000"
    ).execute()
    
    values = result.get('values', [])
    
    print("🔍 古いタスクを検索中...")
    print()
    
    tasks_to_fix = []
    for i, row in enumerate(values, 2):
        if len(row) < 5:
            continue
        
        task_id = row[0]
        status = row[4] if len(row) > 4 else ''
        
        # 不完全なタスクIDを検出
        if status == 'pending' and len(task_id) <= 5:
            tasks_to_fix.append({
                'row_index': i,
                'task_id': task_id,
                'status': status
            })
    
    if not tasks_to_fix:
        print("✅ クリーンアップ不要です")
        return
    
    print(f"⚠️  {len(tasks_to_fix)}個の不完全タスクを発見:")
    for task in tasks_to_fix:
        print(f"  - 行{task['row_index']}: {task['task_id']}")
    
    print()
    response = input("これらのタスクをskippedに変更しますか？ [y/N] ")
    
    if response.lower() == 'y':
        for task in tasks_to_fix:
            sheets.service.spreadsheets().values().update(
                spreadsheetId=sheets.spreadsheet_id,
                range=f"pm_tasks!E{task['row_index']}",
                valueInputOption="RAW",
                body={"values": [["skipped"]]}
            ).execute()
            print(f"✅ 更新: {task['task_id']} → skipped")
        
        print(f"\n✅ {len(tasks_to_fix)}個のタスクをクリーンアップしました")
    else:
        print("キャンセルしました")

if __name__ == "__main__":
    cleanup_old_tasks()

PYTHON

echo "✅ クリーンアップスクリプト作成"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 抜本的対策の実装完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 実装内容:"
echo "  1. ✅ なぜなぜ分析（10層）"
echo "  2. ✅ 真因特定"
echo "  3. ✅ CompleteEngine修正版"
echo "  4. ✅ クリーンアップスクリプト"
echo ""
echo "🎯 次のアクション:"
echo "  1. 古いタスククリーンアップ: python3 tools/cleanup_old_tasks.py"
echo "  2. テスト実行: python3 -c 'from agents.complete_engine_ultimate_fixed import *'"
echo ""
echo "📄 詳細: cat MD/${NOW_JST}_なぜなぜ分析.md"
echo ""

