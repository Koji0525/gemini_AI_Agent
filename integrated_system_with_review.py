#!/usr/bin/env python3
"""
レビューエージェント統合システム（修正版）
- 正しいメソッド名を使用: review_completed_task()
- エラーハンドリング強化
"""
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import json

from sheets_manager import GoogleSheetsManager
from safe_wordpress_executor import SafeWordPressExecutor as WordPressTaskExecutor
from error_auto_fix_system import auto_fix_system

# レビューエージェントのインポート
try:
    from review_agent import ReviewAgent
    REVIEW_AGENT_AVAILABLE = True
except ImportError:
    REVIEW_AGENT_AVAILABLE = False
    logging.warning("⚠️ レビューエージェントが見つかりません")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegratedSystemWithReview:
    """レビュー統合システム"""
    
    def __init__(self):
        self.spreadsheet_id = '1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s'
        self.sheets = None
        self.wp_executor = None
        self.review_agent = None
    
    async def initialize(self):
        """初期化"""
        logger.info("=" * 80)
        logger.info("🚀 レビュー統合システム 起動")
        logger.info("=" * 80)
        
        try:
            # Google Sheets
            self.sheets = GoogleSheetsManager(spreadsheet_id=self.spreadsheet_id)
            logger.info("✅ Google Sheets 接続")
            
            # WordPress Executor
            self.wp_executor = WordPressTaskExecutor()
            if not await self.wp_executor.initialize():
                return False
            logger.info("✅ WordPress Executor 初期化")
            
            # Review Agent
            if REVIEW_AGENT_AVAILABLE:
                self.review_agent = ReviewAgent()
                logger.info("✅ Review Agent 初期化")
                logger.info(f"📝 利用可能なメソッド:")
                review_methods = [m for m in dir(self.review_agent) if not m.startswith('_')]
                for method in review_methods[:5]:
                    logger.info(f"   - {method}")
            else:
                logger.warning("⚠️ Review Agent 未利用")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 初期化エラー: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def execute_with_review(self, task: dict) -> dict:
        """タスク実行 → エラー修正 → レビュー"""
        task_id = task.get('task_id', 'unknown')
        
        logger.info("\n" + "=" * 80)
        logger.info(f"🎯 タスク実行: {task_id}")
        logger.info("=" * 80)
        
        # 1. タスク実行
        result = await self.wp_executor.create_draft(task)
        
        # 実行結果を詳細にログ
        logger.info(f"📊 実行結果:")
        logger.info(f"   成功: {result.get('success')}")
        if not result.get('success'):
            logger.info(f"   エラー: {result.get('error')}")
        
        # 2. エラーの場合は自動修正
        if not result['success']:
            logger.warning("⚠️ エラー検出 - 自動修正を試行")
            
            fix_result = await auto_fix_system.fix_and_retry(
                task,
                result.get('error', 'Unknown error'),
                self.wp_executor
            )
            
            if not fix_result['success']:
                logger.error("❌ 自動修正失敗")
                return {
                    'success': False,
                    'error': fix_result.get('error'),
                    'status': 'failed',
                    'task_id': task_id
                }
            
            logger.info("✅ 自動修正後に成功")
            result = fix_result
        
        # 3. 成功した場合はレビュー実行
        if result.get('success') and self.review_agent:
            logger.info("\n" + "=" * 80)
            logger.info("👁️ レビュー実行中...")
            logger.info("=" * 80)
            
            try:
                # 出力コンテンツを抽出
                output_content = ""
                if isinstance(result.get('result'), dict):
                    output_content = json.dumps(result['result'], ensure_ascii=False, indent=2)
                elif isinstance(result.get('result'), str):
                    output_content = result['result']
                else:
                    output_content = str(result.get('result', ''))
                
                logger.info(f"📝 レビュー対象コンテンツ（最初の200文字）:")
                logger.info(f"   {output_content[:200]}...")
                
                # 🔧 FIX: 正しいメソッド名を使用
                review_result = await self.review_agent.review_completed_task(
                    task=task,
                    output_content=output_content
                )
                
                logger.info(f"✅ レビュー完了")
                logger.info(f"📊 レビュー結果:")
                
                # レビュー結果の詳細をログ
                if isinstance(review_result, dict):
                    for key, value in review_result.items():
                        if isinstance(value, str) and len(value) > 100:
                            logger.info(f"   {key}: {value[:100]}...")
                        else:
                            logger.info(f"   {key}: {value}")
                
                result['review'] = review_result
                result['status'] = 'reviewed'
                
            except Exception as e:
                logger.error(f"❌ レビューエラー: {e}")
                import traceback
                logger.error(traceback.format_exc())
                
                result['review'] = {
                    'error': str(e),
                    'status': 'review_failed'
                }
                result['status'] = 'complete_without_review'
        else:
            result['status'] = 'complete'
        
        return result
    
    async def run_cycle(self):
        """1サイクル実行"""
        logger.info("\n" + "=" * 80)
        logger.info("🔄 タスク実行サイクル開始")
        logger.info("=" * 80)
        
        try:
            # pending タスクを取得
            all_tasks = await self.sheets.load_tasks_from_sheet()
            
            pending_tasks = [t for t in all_tasks if t.get('status', '').lower() == 'pending']
            
            if not pending_tasks:
                logger.info("ℹ️ 実行可能なタスクがありません")
                return
            
            logger.info(f"📊 {len(pending_tasks)} 件の pending タスク")
            
            # 優先度順にソート
            priority_map = {'high': 3, 'medium': 2, 'low': 1, '': 0}
            pending_tasks.sort(
                key=lambda t: priority_map.get(t.get('priority', '').lower(), 0),
                reverse=True
            )
            
            # タスク実行（最大3タスク）
            executed = 0
            success = 0
            failed = 0
            reviewed = 0
            
            for task in pending_tasks[:3]:
                result = await self.execute_with_review(task)
                executed += 1
                
                # ステータス更新
                task_id = task.get('task_id')
                final_status = result.get('status', 'unknown')
                
                if result.get('success'):
                    success += 1
                    if 'review' in result and not result['review'].get('error'):
                        reviewed += 1
                        final_status = 'reviewed'
                    else:
                        final_status = 'complete'
                    
                    logger.info(f"✅ タスク成功: {task_id} → {final_status}")
                else:
                    failed += 1
                    final_status = 'failed'
                    logger.error(f"❌ タスク失敗: {task_id} → {final_status}")
                
                # Google Sheets のステータス更新
                try:
                    await self.sheets.update_task_status(
                        task_id=task_id,
                        status=final_status
                    )
                except Exception as e:
                    logger.error(f"⚠️ ステータス更新エラー: {e}")
            
            logger.info("\n" + "=" * 80)
            logger.info("🎉 サイクル完了")
            logger.info("=" * 80)
            logger.info(f"📊 実行結果:")
            logger.info(f"   実行: {executed}")
            logger.info(f"   ✅ 成功: {success}")
            logger.info(f"   ❌ 失敗: {failed}")
            logger.info(f"   ��️ レビュー済み: {reviewed}")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ サイクルエラー: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    async def cleanup(self):
        """クリーンアップ"""
        if self.wp_executor:
            await self.wp_executor.cleanup()

async def main():
    system = IntegratedSystemWithReview()
    
    if await system.initialize():
        await system.run_cycle()
    else:
        logger.error("❌ 初期化失敗")
    
    await system.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
