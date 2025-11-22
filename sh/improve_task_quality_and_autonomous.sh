#!/bin/bash
# タスク生成品質の向上と24時間稼働システムの強化

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 タスク品質向上と24時間稼働強化"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: 高品質タスクテンプレートの作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: 高品質タスクテンプレートの作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

mkdir -p agents/task_templates

cat > agents/task_templates/high_quality_templates.py << 'PYTHON'
"""
高品質タスクテンプレート
既存の優良タスク定義を活用したテンプレート集
"""

from typing import Dict, Any
from datetime import datetime

class HighQualityTaskTemplates:
    """高品質タスクテンプレート"""
    
    @staticmethod
    def get_integration_test_template(goal_id: str, timestamp: str) -> Dict[str, Any]:
        """統合テスト用の高品質テンプレート"""
        return {
            "task_id": f"{goal_id}_統合テスト実行_{timestamp}_01",
            "parent_goal_id": goal_id,
            "description": (
                "F1-F10の統合テストを実行し、全機能が正常に動作することを確認する。"
                "【目的】24時間自律稼働システムの全機能が正しく連携し、期待通りに動作することを保証する。"
                "【作業内容】"
                "1. tests/system_protection/test_core_functions.pyを実行"
                "2. F1（ゴール分解）からF10（健全性チェック）まで全機能をテスト"
                "3. 各機能の存在確認、初期化確認、基本動作確認を実施"
                "4. ナレッジシステム（F4）の読み書きテスト"
                "5. Google Sheets連携の動作確認"
                "【成功基準】"
                "・全テストで85%以上の成功率を達成"
                "・F1-F10の全機能が正常に初期化される"
                "・ナレッジシステムが正常に動作する"
                "・テスト結果レポートが生成される"
                "【コンテキスト】システム保護テストスイートを使用。各機能の最新実装状態を反映。"
            ),
            "required_role": "tester",
            "status": "pending",
            "priority": "high",
            "estimated_time": "30min",
            "dependencies": "",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "batch_id": f"auto_quality_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "detail_file_path": "",
            "blank": "",
            "execution_type": "testing"
        }
    
    @staticmethod
    def get_system_integration_template(goal_id: str, timestamp: str, dep: str) -> Dict[str, Any]:
        """システム連携確認用の高品質テンプレート"""
        return {
            "task_id": f"{goal_id}_システム連携動作確認_{timestamp}_02",
            "parent_goal_id": goal_id,
            "description": (
                "CompleteEngineUltimateを中心としたF1-F10の連携動作を実際に確認する。"
                "【目的】各機能が単独で動作するだけでなく、相互に連携して24時間自律稼働システムとして機能することを検証する。"
                "【作業内容】"
                "1. CompleteEngineUltimateの初期化と全機能の統合確認"
                "2. F1→F2→F3→F4の順次実行フロー確認（タスク分解→実行→評価→蓄積）"
                "3. F6の動的タスク追加機能の動作確認"
                "4. F7の自己修復機能のトリガー確認（意図的なエラー発生）"
                "5. F8の学習サイクル確認（パターン抽出）"
                "6. F9の人間連携機能確認（通知生成）"
                "7. F10の健全性チェック実行"
                "8. 連携フロー図と動作確認レポートをMDファイルで生成"
                "【成功基準】"
                "・CompleteEngineUltimateが全機能を正しく保持している"
                "・F1-F10の連携フローが途切れずに動作する"
                "・エラー時にF7が自動起動する"
                "・学習サイクルが正常に実行される"
                "・詳細な動作確認レポートが生成される"
                "【コンテキスト】agents/complete_engine_ultimate.pyの最新実装を基準とする。"
            ),
            "required_role": "developer",
            "status": "pending",
            "priority": "high",
            "estimated_time": "1h",
            "dependencies": dep,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "batch_id": f"auto_quality_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "detail_file_path": "",
            "blank": "",
            "execution_type": "testing"
        }
    
    @staticmethod
    def get_flaky_test_detection_template(goal_id: str, timestamp: str, dep: str) -> Dict[str, Any]:
        """フラッキーテスト検出用の高品質テンプレート"""
        return {
            "task_id": f"{goal_id}_フラッキーテスト検出設計_{timestamp}_03",
            "parent_goal_id": goal_id,
            "description": (
                "テスト自動化エンジン(agents/efficiency/test_automation_engine.py)に、"
                "フラッキーテスト（結果が不安定なテスト）を自動的に検出し、修正するロジックを設計する。"
                "【目的】テストスイートの信頼性を高め、誤検出による開発効率の低下を防ぐ。"
                "【作業内容】"
                "1. フラッキーテスト検出アルゴリズムの調査と選定"
                "   - テスト実行履歴の統計分析（成功率、実行時間の分散）"
                "   - コードの静的解析（非決定的要素の検出：時刻依存、乱数、並行処理）"
                "   - テストの複数回実行による再現性確認"
                "2. 検出ロジックの詳細設計"
                "   - 履歴データの収集・分析方法"
                "   - フラッキー判定の閾値設定（例：5回中2回以上失敗）"
                "   - 検出フローチャートの作成"
                "3. テスト修正戦略の検討"
                "   - リトライメカニズムの追加"
                "   - 適切な待機時間（sleep）の挿入"
                "   - モックやスタブの活用による外部依存の排除"
                "   - テスト順序の最適化"
                "4. 実装計画の策定"
                "   - 既存のtest_automation_engine.pyへの統合方法"
                "   - データベーススキーマの設計（テスト実行履歴）"
                "   - CI/CDパイプラインとの連携方法"
                "【成功基準】"
                "・フラッキーテストを効果的に検出できるアルゴリズムが選定されている"
                "・検出・修正ロジックの詳細フローチャートが完成している"
                "・実装可能な具体的な設計書が作成されている"
                "・既存のテスト自動化エンジンへの統合計画が明確になっている"
                "【コンテキスト】"
                "agents/efficiency/test_automation_engine.pyの現在の実装を確認し、"
                "既存のテスト実行環境（pytest）との互換性を保つ。"
                "テスト実行履歴はSQLiteまたはGoogle Sheetsに記録する方針。"
            ),
            "required_role": "developer",
            "status": "pending",
            "priority": "high",
            "estimated_time": "2h",
            "dependencies": dep,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "batch_id": f"auto_quality_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "detail_file_path": "",
            "blank": "",
            "execution_type": "design"
        }
    
    @staticmethod
    def get_24h_operation_checklist_template(goal_id: str, timestamp: str, dep: str) -> Dict[str, Any]:
        """24時間稼働チェックリスト用テンプレート"""
        return {
            "task_id": f"{goal_id}_24時間稼働最終確認_{timestamp}_04",
            "parent_goal_id": goal_id,
            "description": (
                "24時間自律稼働システムが本番運用可能な状態であることを最終確認する。"
                "【目的】システムを24時間無人で稼働させても問題が発生しないことを保証する。"
                "【作業内容】"
                "1. 長時間稼働テスト（最低6時間連続）"
                "   - メモリリーク確認"
                "   - CPU使用率の監視"
                "   - ディスク容量の確認"
                "2. エラーハンドリングの検証"
                "   - F7（自己修復）の動作確認"
                "   - 最大3回リトライの動作確認"
                "   - F9（人間通知）の発火確認"
                "3. 学習サイクルの動作確認"
                "   - F8（自己進化）のトリガー確認（6時間/50エラー）"
                "   - ナレッジ蓄積の継続性確認"
                "   - パターン学習の効果測定"
                "4. API使用量の監視"
                "   - Claude APIの使用量計測"
                "   - Google Sheets APIの使用量計測"
                "   - レート制限への対処確認"
                "5. ログ管理の確認"
                "   - ログファイルのローテーション"
                "   - 重要イベントの記録確認"
                "   - エラーログの通知確認"
                "6. 最終チェックリストの作成"
                "   - 起動前チェック項目"
                "   - 稼働中監視項目"
                "   - 停止時確認項目"
                "【成功基準】"
                "・6時間以上の連続稼働が成功する"
                "・エラー時の自動修復が正常に動作する"
                "・学習サイクルが自動実行される"
                "・API使用量が許容範囲内に収まる"
                "・詳細なチェックリストが作成される"
                "【コンテキスト】"
                "sh/run_autonomous_24h_v3.shを使用して長時間稼働テストを実施。"
                "logs/ディレクトリのログを分析し、異常がないことを確認。"
            ),
            "required_role": "developer",
            "status": "pending",
            "priority": "high",
            "estimated_time": "6h",
            "dependencies": dep,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "batch_id": f"auto_quality_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "detail_file_path": "",
            "blank": "",
            "execution_type": "testing"
        }

PYTHON

echo "✅ 高品質テンプレート作成: agents/task_templates/high_quality_templates.py"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: auto_task_generatorの改良（高品質版）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: auto_task_generatorの改良（高品質版）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > agents/auto_task_generator_v2.py << 'PYTHON'
"""
自動タスク生成エージェント v2（高品質版）
既存の優良タスク定義を活用した高品質タスク生成
"""

import sys
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.task_templates.high_quality_templates import HighQualityTaskTemplates

class AutoTaskGeneratorV2:
    """自動タスク生成エージェント v2（高品質版）"""
    
    def __init__(self, sheets_manager=None):
        self.sheets = sheets_manager
        self.templates = HighQualityTaskTemplates()
        
    def check_pending_tasks(self) -> int:
        """pendingタスクの数を確認"""
        try:
            result = self.sheets.service.spreadsheets().values().get(
                spreadsheetId=self.sheets.spreadsheet_id,
                range="pm_tasks!A2:Z1000"
            ).execute()
            
            values = result.get('values', [])
            pending_count = sum(1 for row in values if len(row) > 4 and row[4] == 'pending')
            
            print(f"📋 pendingタスク: {pending_count}個")
            return pending_count
            
        except Exception as e:
            print(f"⚠️  タスク確認エラー: {e}")
            return -1
    
    def generate_high_quality_tasks(self, goal_id: str = "7") -> List[Dict[str, Any]]:
        """高品質タスクを生成"""
        timestamp = datetime.now().strftime('%H%M%S')
        
        # タスク1: 統合テスト
        task1 = self.templates.get_integration_test_template(goal_id, timestamp)
        
        # タスク2: システム連携確認（タスク1に依存）
        task2 = self.templates.get_system_integration_template(
            goal_id, timestamp, task1["task_id"]
        )
        
        # タスク3: フラッキーテスト検出設計（タスク2に依存）
        task3 = self.templates.get_flaky_test_detection_template(
            goal_id, timestamp, task2["task_id"]
        )
        
        # タスク4: 24時間稼働最終確認（タスク3に依存）
        task4 = self.templates.get_24h_operation_checklist_template(
            goal_id, timestamp, task3["task_id"]
        )
        
        return [task1, task2, task3, task4]
    
    def add_tasks_to_sheet(self, tasks: List[Dict[str, Any]]) -> bool:
        """タスクをGoogle Sheetsに追加"""
        try:
            for task in tasks:
                row_data = [
                    task["task_id"],
                    task["parent_goal_id"],
                    task["description"],
                    task["required_role"],
                    task["status"],
                    task["priority"],
                    task["estimated_time"],
                    task["dependencies"],
                    task["created_at"],
                    task["batch_id"],
                    task["detail_file_path"],
                    task["blank"],
                    task["execution_type"]
                ]
                
                self.sheets.service.spreadsheets().values().append(
                    spreadsheetId=self.sheets.spreadsheet_id,
                    range="pm_tasks!A:M",
                    valueInputOption="RAW",
                    body={"values": [row_data]}
                ).execute()
                
                print(f"  ✅ 高品質タスク追加: {task['task_id']}")
            
            print(f"\n✅ {len(tasks)}個の高品質タスクを追加しました")
            return True
            
        except Exception as e:
            print(f"❌ タスク追加エラー: {e}")
            return False
    
    def auto_generate_if_needed(self) -> Dict[str, Any]:
        """必要に応じて高品質タスクを自動生成"""
        print("━" * 60)
        print("🤖 自動タスク生成チェック（高品質版 v2）")
        print("━" * 60)
        print()
        
        pending_count = self.check_pending_tasks()
        
        if pending_count < 0:
            print("\n⚠️  タスク確認に失敗しました。")
            return {"generated": False, "error": "タスク確認失敗"}
        
        if pending_count == 0:
            print("\n📋 pendingタスクが0個です。")
            print("🔧 高品質タスクを自動生成します...")
            print()
            
            tasks = self.generate_high_quality_tasks()
            
            print("【生成する高品質タスク】")
            for i, task in enumerate(tasks, 1):
                print(f"\n  {i}. {task['task_id']}")
                print(f"     タイプ: {task['execution_type']}")
                print(f"     時間: {task['estimated_time']}")
                print(f"     依存: {task['dependencies'] or 'なし'}")
                desc_lines = task['description'].split('\n')
                print(f"     説明: {desc_lines[0][:60]}...")
            
            print()
            success = self.add_tasks_to_sheet(tasks)
            
            if success:
                print("✅ 高品質タスク自動生成完了")
                print("📝 これらのタスクは既存システムで自動実行されます")
            
            return {
                "generated": True,
                "task_count": len(tasks),
                "success": success,
                "tasks": [t["task_id"] for t in tasks],
                "quality": "high"
            }
            
        else:
            print(f"\n📋 {pending_count}個のpendingタスクが存在します。")
            print("⏭️  タスク自動生成はスキップします。")
            return {
                "generated": False,
                "pending_count": pending_count
            }

def main():
    """メイン実行"""
    from tools.sheets_manager import GoogleSheetsManager
    
    print("🚀 自動タスク生成エージェント v2（高品質版）起動")
    print()
    
    try:
        sheets = GoogleSheetsManager()
        generator = AutoTaskGeneratorV2(sheets)
        
        result = generator.auto_generate_if_needed()
        
        print()
        print("━" * 60)
        print("📊 実行結果")
        print("━" * 60)
        
        if result.get("generated"):
            print(f"  ✅ タスク自動生成: 成功")
            print(f"  📝 生成タスク数: {result.get('task_count')}個")
            print(f"  ⭐ 品質: {result.get('quality', 'standard').upper()}")
            
            if result.get("tasks"):
                print("\n  【生成されたタスクID】")
                for task_id in result.get("tasks"):
                    print(f"    - {task_id}")
            
            print("\n  🎯 次のアクション:")
            print("    bash start_pending_tasks.sh --limit 4")
            
        elif result.get("error"):
            print(f"  ⚠️  エラー: {result['error']}")
            
        else:
            print(f"  ⏭️  タスク自動生成: スキップ")
            if "pending_count" in result:
                print(f"  📋 既存pending: {result['pending_count']}個")
        
        print()
        return 0
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

PYTHON

echo "✅ 高品質版作成: agents/auto_task_generator_v2.py"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: 既存のauto_task_generatorを置き換え
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: 既存のauto_task_generatorを置き換え"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cp agents/auto_task_generator.py "agents/auto_task_generator.py.backup_${NOW_JST}_old"
cp agents/auto_task_generator_v2.py agents/auto_task_generator.py

echo "✅ 高品質版に置き換え完了"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: 動作確認
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: 動作確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 agents/auto_task_generator.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ タスク品質向上完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 改善内容:"
echo "  1. ✅ 高品質タスクテンプレート作成"
echo "  2. ✅ 詳細な【目的】【作業内容】【成功基準】【コンテキスト】"
echo "  3. ✅ タスク間の依存関係を明確化"
echo "  4. ✅ 実行可能な具体的なタスク定義"
echo ""
echo "📝 生成されるタスク:"
echo "  1. 統合テスト実行（F1-F10検証）"
echo "  2. システム連携動作確認（連携フロー）"
echo "  3. フラッキーテスト検出設計（テスト信頼性向上）"
echo "  4. 24時間稼働最終確認（長時間稼働テスト）"
echo ""
echo "🎯 次のステップ:"
echo "  bash start_pending_tasks.sh --limit 4"
echo ""

