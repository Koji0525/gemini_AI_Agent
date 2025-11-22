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

