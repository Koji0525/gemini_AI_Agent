#!/usr/bin/env python3
"""
WPAgentLogger - WordPressエージェント用ロガー
task_execution_logシートへの記録機能（修正版）

v1.1 - task_execution_logシートに正しく記録
運用ルール準拠: 1ファイル1000行以下、PEP 8準拠
"""

import sys
import gspread
from typing import Dict, Any
from datetime import datetime

sys.path.insert(0, '/workspaces/gemini_AI_Agent')
from tools.sheets_manager import GoogleSheetsManager


class WPAgentLogger:
    """WordPressエージェント用の汎用ロガー"""
    
    def __init__(self, sheets_manager: GoogleSheetsManager):
        """
        初期化（依存性注入）
        
        Args:
            sheets_manager: GoogleSheetsManagerインスタンス
        """
        self.sheets_manager = sheets_manager
    
    async def _write_to_task_execution_log(self, log_data: Dict[str, Any]) -> bool:
        """
        task_execution_logシートに直接書き込み
        
        Args:
            log_data: ログデータ
            
        Returns:
            bool: 成功した場合True
        """
        try:
            # クライアントとシートの取得
            self.sheets_manager._ensure_client()
            sheet = self.sheets_manager.gc.open_by_key(self.sheets_manager.spreadsheet_id)
            
            # task_execution_logシートを取得または作成
            try:
                log_sheet = sheet.worksheet("task_execution_log")
            except gspread.exceptions.WorksheetNotFound:
                print("⚠️  task_execution_logシートが存在しないため作成します")
                log_sheet = sheet.add_worksheet(title="task_execution_log", rows=1000, cols=10)
                
                # ヘッダー行を設定
                headers = [
                    "log_id", "task_id", "task_description", "timestamp",
                    "agent_role", "output_summary", "output_data", "status",
                    "Quality_Score", "Quality_description"
                ]
                log_sheet.append_row(headers)
            
            # 次のlog_idを取得
            all_values = log_sheet.get_all_values()
            next_log_id = len(all_values)  # ヘッダー含む行数 = 次のID
            
            # データ行を作成
            row = [
                next_log_id,
                log_data.get("task_id", ""),
                log_data.get("task_description", ""),
                log_data.get("timestamp", ""),
                log_data.get("agent_role", ""),
                log_data.get("output_summary", ""),
                log_data.get("output_data", ""),
                log_data.get("status", ""),
                log_data.get("Quality_Score", ""),
                log_data.get("Quality_description", "")
            ]
            
            # 行を追加
            log_sheet.append_row(row)
            
            print(f"✅ task_execution_logシート 行{next_log_id} に記録完了")
            return True
            
        except Exception as e:
            print(f"❌ task_execution_logへの書き込みエラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def log_cpt_creation(self, result: Dict[str, Any], spec: Any) -> bool:
        """
        CPT作成結果をログに記録
        
        Args:
            result: create_cpt()の実行結果
            spec: CPTSpecification
            
        Returns:
            bool: 記録成功した場合True
        """
        print("\n📊 task_execution_logシートに記録中...")
        
        try:
            timestamp = datetime.now().isoformat()
            
            # Quality Score計算
            quality_score = 10 if result["success"] else 1
            
            # status判定
            status = "completed" if result["success"] else "failed"
            
            # output_summary生成（100文字以内）
            if result["success"]:
                summary = f"カスタム投稿タイプ '{spec.post_type}' のPHPコード生成成功。{spec.plural_name}。"
            else:
                summary = f"カスタム投稿タイプ '{spec.post_type}' の作成失敗。{result.get('message', '')}"
            
            summary = summary[:100]
            
            # Quality_description生成
            if result["success"]:
                quality_description = (
                    f"カスタム投稿タイプ '{spec.post_type}' のregister_post_type()コードを生成。"
                    f"投稿タイプ名: {spec.plural_name}。"
                    f"サポート機能: {', '.join(spec.supports)}。"
                    f"アーカイブページ: {'あり' if spec.has_archive else 'なし'}。"
                    f"階層構造: {'あり' if spec.hierarchical else 'なし'}。"
                )
            else:
                quality_description = f"カスタム投稿タイプの作成に失敗: {result.get('message', '不明なエラー')}"
            
            # ログデータ構築（task_execution_log形式）
            log_data = {
                "task_id": int(datetime.now().timestamp()),
                "task_description": f"カスタム投稿タイプ作成: {spec.plural_name}",
                "timestamp": timestamp,
                "agent_role": "WPCPTAgent",
                "output_summary": summary,
                "output_data": result.get("filepath", ""),
                "status": status,
                "Quality_Score": quality_score,
                "Quality_description": quality_description
            }
            
            # task_execution_logシートに記録
            success = await self._write_to_task_execution_log(log_data)
            
            if success:
                print("✅ task_execution_logシートへの記録完了")
            else:
                print("⚠️  task_execution_logシートへの記録失敗")
            
            return success
            
        except Exception as e:
            print(f"❌ ログ記録エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def log_taxonomy_creation(self, result: Dict[str, Any], spec: Any) -> bool:
        """
        タクソノミー作成結果をログに記録
        
        Args:
            result: create_taxonomy()の実行結果
            spec: TaxonomySpecification
            
        Returns:
            bool: 記録成功した場合True
        """
        print("\n📊 task_execution_logシートに記録中...")
        
        try:
            timestamp = datetime.now().isoformat()
            
            # Quality Score計算
            quality_score = 10 if result["success"] else 1
            
            # status判定
            status = "completed" if result["success"] else "failed"
            
            # output_summary生成（100文字以内）
            tax_type = "階層型" if spec.hierarchical else "非階層型"
            if result["success"]:
                summary = f"カスタムタクソノミー '{spec.taxonomy}' ({tax_type}) のPHPコード生成成功。"
            else:
                summary = f"カスタムタクソノミー '{spec.taxonomy}' の作成失敗。{result.get('message', '')}"
            
            summary = summary[:100]
            
            # Quality_description生成
            if result["success"]:
                quality_description = (
                    f"カスタムタクソノミー '{spec.taxonomy}' のregister_taxonomy()コードを生成。"
                    f"タクソノミー名: {spec.plural_name}。"
                    f"タイプ: {tax_type}。"
                    f"対象投稿タイプ: {', '.join(spec.post_types)}。"
                )
            else:
                quality_description = f"カスタムタクソノミーの作成に失敗: {result.get('message', '不明なエラー')}"
            
            # ログデータ構築（task_execution_log形式）
            log_data = {
                "task_id": int(datetime.now().timestamp()),
                "task_description": f"カスタムタクソノミー作成: {spec.plural_name}",
                "timestamp": timestamp,
                "agent_role": "WPTaxonomyAgent",
                "output_summary": summary,
                "output_data": result.get("filepath", ""),
                "status": status,
                "Quality_Score": quality_score,
                "Quality_description": quality_description
            }
            
            # task_execution_logシートに記録
            success = await self._write_to_task_execution_log(log_data)
            
            if success:
                print("✅ task_execution_logシートへの記録完了")
            else:
                print("⚠️  task_execution_logシートへの記録失敗")
            
            return success
            
        except Exception as e:
            print(f"❌ ログ記録エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
