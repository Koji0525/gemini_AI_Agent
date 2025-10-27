#!/usr/bin/env python3
"""Goal Breakdown Agent - project_goalをpm_tasksに分解"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
os.environ['DISPLAY'] = ':1'

from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import get_config


class GoalBreakdownAgent:
    """目標をタスクに分解するエージェント"""
    
    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets = sheets_manager
        self.config = get_config()
    
    def get_active_goals(self) -> List[Dict[str, Any]]:
        """activeステータスの目標を取得"""
        spreadsheet = self.sheets.gc.open_by_key(self.config.get("SPREADSHEET_ID"))
        goal_sheet = spreadsheet.worksheet('project_goal')
        
        headers = goal_sheet.row_values(1)
        all_values = goal_sheet.get_all_values()
        data_rows = all_values[1:]
        
        active_goals = []
        for row in data_rows:
            if len(row) > 2 and row[2] == 'active':
                active_goals.append({
                    'goal_id': row[0] if len(row) > 0 else 'N/A',
                    'goal_description': row[1] if len(row) > 1 else 'N/A',
                    'status': row[2] if len(row) > 2 else 'N/A',
                    'created_at': row[3] if len(row) > 3 else 'N/A'
                })
        
        return active_goals
    
    def breakdown_goal_4_ma_portal(self) -> List[Dict[str, Any]]:
        """
        目標4（M&Aポータルサイト）を具体的なタスクに分解
        
        Returns:
            タスクのリスト
        """
        tasks = [
            # フェーズ1: 基礎構築（高優先度）
            {
                'title': '【要件定義】M&Aポータルサイトの機能、非機能要件定義書作成',
                'description': '目標4の詳細な要件定義ドキュメントを作成。カスタム投稿タイプ、カスタムフィールド、検索機能、ユーザー権限、セキュリティ要件を明確化。',
                'required_role': 'dev',
                'priority': 'high',
                'estimated_hours': 4,
                'execution_type': 'gemini',
                'acceptance_criteria': '要件定義書（.md形式）が完成し、開発可能な状態になっていること'
            },
            {
                'title': '【Custom Post Type】M&A案件カスタム投稿タイプ作成（Polylang対応必須）',
                'description': 'register_post_type()で\'ma_case\'投稿タイプを作成。title、editor、custom-fieldsをサポート。Polylangで多言語対応を有効化。',
                'required_role': 'dev',
                'priority': 'high',
                'estimated_hours': 2,
                'execution_type': 'wordpress',
                'acceptance_criteria': 'ma_case投稿タイプが管理画面に表示され、投稿作成可能なこと'
            },
            {
                'title': '【タクソノミー】業種カテゴリ作成（Polylang対応）',
                'description': 'register_taxonomy()で\'ma_industry\'タクソノミーを作成。階層構造（製造業>自動車部品など）をサポート。',
                'required_role': 'dev',
                'priority': 'high',
                'estimated_hours': 2,
                'execution_type': 'gemini',
                'acceptance_criteria': '業種カテゴリが管理画面で設定可能で、案件に紐付けできること'
            },
            {
                'title': '【タクソノミー】地域カテゴリ作成（Polylang対応）',
                'description': 'register_taxonomy()で\'ma_region\'タクソノミーを作成。都道府県ベースの分類。',
                'required_role': 'dev',
                'priority': 'high',
                'estimated_hours': 2,
                'execution_type': 'gemini',
                'acceptance_criteria': '地域カテゴリが管理画面で設定可能で、案件に紐付けできること'
            },
            {
                'title': '【ACF設定】M&A案件基本情報フィールドグループ作成',
                'description': 'ACF Proで基本情報フィールドグループを作成：案件ID、M&Aスキーム、希望価格、売上高、営業利益、従業員数、設立年、事業内容。',
                'required_role': 'dev',
                'priority': 'high',
                'estimated_hours': 3,
                'execution_type': 'wordpress',
                'acceptance_criteria': 'ACFフィールドが投稿編集画面に表示され、データ入力可能なこと'
            },
            {
                'title': '【FacetWP】案件絞り込み検索機能設定',
                'description': 'FacetWPで絞り込み検索を実装：業種、地域、価格帯、M&Aスキームでのフィルタリング。Ajax対応で高速検索。',
                'required_role': 'dev',
                'priority': 'high',
                'estimated_hours': 4,
                'execution_type': 'wordpress',
                'acceptance_criteria': '検索フォームから複数条件で絞り込みができ、結果が即座に表示されること'
            },
            {
                'title': '【テーマカスタマイズ】案件一覧ページのテンプレートファイル（archive-ma_case.php）作成とFacetWP統合',
                'description': 'archive-ma_case.phpテンプレート作成。FacetWP検索フォーム配置、カード形式の案件一覧表示、ページネーション実装。',
                'required_role': 'dev',
                'priority': 'high',
                'estimated_hours': 5,
                'execution_type': 'wordpress',
                'acceptance_criteria': '案件一覧ページが正しく表示され、検索・絞り込みが動作すること'
            },
            
            # フェーズ2: 機能強化（中優先度）
            {
                'title': '【UI設計】M&A案件一覧/検索フォームのワイヤーフレームと画面デザイン作成',
                'description': 'Figmaでワイヤーフレーム作成。検索フォーム配置、案件カードデザイン、レスポンシブ対応。',
                'required_role': 'design',
                'priority': 'medium',
                'estimated_hours': 4,
                'execution_type': 'gemini',
                'acceptance_criteria': 'ワイヤーフレームと画面デザインが完成し、開発チームに共有されていること'
            },
            {
                'title': '【User Role Editor】提携パートナー専用ロールの作成と権限設定',
                'description': 'add_role()で\'ma_partner\'ロールを作成。自分の案件のみ編集可能、管理者承認が必要な権限設定。',
                'required_role': 'dev',
                'priority': 'medium',
                'estimated_hours': 3,
                'execution_type': 'gemini',
                'acceptance_criteria': 'パートナーロールが作成され、適切な権限制御が機能していること'
            },
            {
                'title': '【Polylang設定】日本語と英語の言語登録、カスタム投稿タイプとタクソノミーの有効化',
                'description': 'Polylangで日本語・英語を設定。ma_case、ma_industry、ma_regionを翻訳可能に設定。',
                'required_role': 'dev',
                'priority': 'medium',
                'estimated_hours': 2,
                'execution_type': 'wordpress',
                'acceptance_criteria': '言語切り替えが機能し、投稿タイプとタクソノミーが翻訳可能なこと'
            },
            
            # フェーズ3: セキュリティ・最適化（中優先度）
            {
                'title': '【セキュリティ】Wordfence Securityの基本設定（ファイアウォール、スキャン）',
                'description': 'Wordfence Securityをインストール・有効化。ファイアウォール設定、マルウェアスキャン設定、ログイン試行制限。',
                'required_role': 'dev',
                'priority': 'medium',
                'estimated_hours': 2,
                'execution_type': 'gemini',
                'acceptance_criteria': 'Wordfenceが正常に動作し、セキュリティスキャンが実行可能なこと'
            },
            {
                'title': '【キャッシュ】WP Rocketのキャッシュ有効化、ファイル最適化、CDN設定',
                'description': 'WP Rocketでページキャッシュ有効化。CSS/JS/画像の最適化設定。CloudflareなどのCDN連携。',
                'required_role': 'dev',
                'priority': 'medium',
                'estimated_hours': 2,
                'execution_type': 'wordpress',
                'acceptance_criteria': 'ページ読み込み速度が改善され、PageSpeed Insightsスコアが80以上'
            },
            {
                'title': '【検索】パフォーマンス測定（検索レスポンス、メタクエリ最適化、インデックス検討）',
                'description': '検索機能のパフォーマンステスト。Query Monitorでメタクエリを分析。必要に応じてDBインデックス追加。',
                'required_role': 'dev',
                'priority': 'medium',
                'estimated_hours': 3,
                'execution_type': 'gemini',
                'acceptance_criteria': '検索レスポンスが2秒以内、ボトルネックが特定・改善されていること'
            },
            {
                'title': '【セキュリティ】Two Factor Authenticationの設定と管理者へのMFA必須化',
                'description': 'Two Factor Authenticationプラグイン導入。管理者・パートナー向けにMFA（多要素認証）を強制。',
                'required_role': 'dev',
                'priority': 'medium',
                'estimated_hours': 2,
                'execution_type': 'gemini',
                'acceptance_criteria': '管理者ログイン時にMFAが必須となり、正常に動作すること'
            },
            {
                'title': '【レビュー】統合テスト（検索、権限、セキュリティ、パフォーマンス）とリリース判定',
                'description': '全機能の統合テスト実施。検索機能、ユーザー権限、セキュリティ、パフォーマンスを検証。不具合リスト作成。',
                'required_role': 'review',
                'priority': 'medium',
                'estimated_hours': 4,
                'execution_type': 'gemini',
                'acceptance_criteria': 'テスト結果レポートが完成し、リリース可否が判定されていること'
            }
        ]
        
        return tasks
    
    async def register_tasks_to_pm_tasks(
        self, 
        goal_id: str, 
        tasks: List[Dict[str, Any]]
    ) -> bool:
        """タスクをpm_tasksシートに登録"""
        from agents.pm_agent.task_registration import TaskRegistrationAgent
        
        registration = TaskRegistrationAgent(self.sheets)
        success = await registration.register_tasks(goal_id, tasks)
        
        return success
    
    async def execute_goal_breakdown(self, goal_id: str = "4") -> Dict[str, Any]:
        """
        目標を分解してpm_tasksに登録
        
        Args:
            goal_id: 目標ID（デフォルト: 4）
        
        Returns:
            実行結果
        """
        print("="*70)
        print(f"🎯 目標{goal_id}の分解開始")
        print("="*70)
        print()
        
        # アクティブな目標を確認
        active_goals = self.get_active_goals()
        target_goal = next((g for g in active_goals if g['goal_id'] == goal_id), None)
        
        if not target_goal:
            print(f"❌ 目標{goal_id}が見つからないか、activeステータスではありません")
            return {'status': 'error', 'message': 'Goal not found or not active'}
        
        print(f"【目標情報】")
        print(f"ID: {target_goal['goal_id']}")
        print(f"説明: {target_goal['goal_description'][:100]}...")
        print(f"ステータス: {target_goal['status']}")
        print()
        
        # タスクに分解
        print("【タスク分解】")
        print("-"*70)
        tasks = self.breakdown_goal_4_ma_portal()
        print(f"✅ {len(tasks)}個のタスクを生成しました")
        print()
        
        for i, task in enumerate(tasks[:5], 1):
            print(f"{i}. {task['title']}")
            print(f"   担当: {task['required_role']} | 優先度: {task['priority']} | 推定: {task['estimated_hours']}h")
        
        if len(tasks) > 5:
            print(f"... 他 {len(tasks) - 5}件")
        print()
        
        # pm_tasksに登録
        print("【pm_tasksシートに登録】")
        print("-"*70)
        success = await self.register_tasks_to_pm_tasks(goal_id, tasks)
        
        if success:
            print("✅ 登録成功")
            return {
                'status': 'success',
                'goal_id': goal_id,
                'tasks_generated': len(tasks)
            }
        else:
            print("❌ 登録失敗")
            return {
                'status': 'error',
                'message': 'Failed to register tasks'
            }


# ==
# メイン実行
# ==
async def main():
    print("\n")
    
    config = get_config()
    sheets = GoogleSheetsManager(
        spreadsheet_id=config.get("SPREADSHEET_ID"),
        service_account_file=config.get("SERVICE_ACCOUNT_FILE")
    )
    
    agent = GoalBreakdownAgent(sheets)
    
    # 目標4を分解
    result = await agent.execute_goal_breakdown(goal_id="4")
    
    print("\n" + "="*70)
    print("📊 実行結果")
    print("="*70)
    print(f"ステータス: {result.get('status')}")
    if result.get('status') == 'success':
        print(f"生成タスク数: {result.get('tasks_generated')}件")
        print("\n次のステップ:")
        print("  python3 run_pm_tasks_adaptive.py --max-tasks 15")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
