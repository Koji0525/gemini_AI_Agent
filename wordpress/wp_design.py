# wp_design.py
"""
WordPress設計・開発タスク実行モジュール
task_executor.py の WordPress 専用メソッドを提供
"""

import asyncio
import logging
from typing import Dict, Any, Optional

# ロガーの設定
logger = logging.getLogger(__name__)

# グローバルフラグ（実際の実装では適切に設定されるべき）
HAS_TASK_ROUTER = False
HAS_ENHANCED_HANDLER = False

# ダミークラス定義（実際の実装では適切なクラスをインポート）
class EnhancedErrorHandler:
    @staticmethod
    async def timeout_wrapper(coro, timeout, context):
        return await asyncio.wait_for(coro, timeout=timeout)
    
    @staticmethod
    def log_error_with_context(e, context):
        logger.error(f"{context}: {e}")

class ErrorHandler:
    @staticmethod
    def log_error(e, context):
        logger.error(f"{context}: {e}")

class TaskRouter:
    @staticmethod
    def determine_task_type(task):
        return task.get('task_type', 'default')

# グローバルインスタンス
task_router = TaskRouter() if HAS_TASK_ROUTER else None


class WordPressTaskExecutor:
    """
    WordPress専用タスク実行クラス
    """
    
    def __init__(self, agents=None, ma_executor=None, content_executor=None, review_agent=None):
        """初期化"""
        self.agents = agents or {}
        self.ma_executor = ma_executor
        self.content_executor = content_executor
        self.review_agent = review_agent
        
        logger.info("✅ WordPressTaskExecutor 初期化完了")
    
    async def execute_task(self, task: Dict) -> bool:
        """単一タスクを実行（WordPress専用エージェント対応版）"""
        task_id = task.get('task_id', 'UNKNOWN')
        
        try:
            # ============================================================
            # === パート1: タスク開始ヘッダー表示 ===
            # ============================================================
            print("\n" + "📷"*40)
            print("=" * 80)
            print(f"🎯 タスク開始: {task_id}")
            print("=" * 80)
            print(f"📝 内容: {task['description'][:70]}...")
            print(f"👤 担当エージェント: {task['required_role'].upper()}")
            
            print("=" * 80)
            print("📷"*40 + "\n")
            
            logger.info(f"タスク {task_id} 実行開始")
            
            # タスクのステータスを'in_progress'に更新
            try:
                await self.update_task_status(task, 'in_progress')
            except Exception as e:
                logger.warning(f"⚠️ ステータス更新失敗（続行）: {e}")
            
            # ============================================================
            # === パート2: タスクタイプ判定とタイムアウト設定 ===
            # ============================================================
            role = task['required_role'].lower()
            
            # タイムアウトマップ
            timeout_map = {
                'ma': 300.0,
                'content': 240.0,
                'review': 180.0,
                'wordpress': 300.0,
                'wp_design': 300.0,  # WordPress設計
                'wp_dev': 300.0,     # WordPress開発
                'default': 180.0
            }
            
            # タスクタイプを取得
            task_type = 'default'
            if HAS_TASK_ROUTER and task_router:
                try:
                    task_type = task_router.determine_task_type(task)
                    logger.info(f"📊 タスクタイプ判定: {task_type}")
                except Exception as e:
                    logger.warning(f"⚠️ タスクタイプ判定失敗、デフォルト処理: {e}")
            
            task_timeout = timeout_map.get(task_type, timeout_map.get(role, 180.0))
            
            # ============================================================
            # === パート3: タスク実行（エージェント振り分け） ===
            # ============================================================
            result = None
            
            try:
                # --- 3-1: WordPress専用エージェント判定（最優先） ---
                if role == 'wp_design':
                    logger.info("="*60)
                    logger.info("🎨 WordPress設計AIエージェント実行中")
                    logger.info("="*60)
                    task_coro = self._execute_wp_design_task(task)
                
                elif role == 'wp_dev':
                    logger.info("="*60)
                    logger.info("💻 WordPress開発AIエージェント実行中")
                    logger.info("="*60)
                    task_coro = self._execute_wp_dev_task(task)
                
                # --- 3-2: タスクタイプベースの分岐 ---
                elif task_type == 'ma' and self.ma_executor:
                    logger.info("="*60)
                    logger.info("📊 M&A/企業検索タスクとして処理")
                    logger.info("="*60)
                    task_coro = self.ma_executor.execute_ma_task(task)
                
                elif task_type == 'content' and self.content_executor:
                    logger.info("="*60)
                    logger.info("✏️ 記事生成タスクとして処理")
                    logger.info("="*60)
                    task_coro = self.content_executor.execute_writer_task(task, role)
                
                elif task_type == 'review':
                    logger.info("="*60)
                    logger.info("✅ レビュータスクとして処理")
                    logger.info("="*60)
                    task_coro = self._execute_review_task(task)
                
                # --- 3-3: デフォルトのロール分岐 ---
                else:
                    logger.info("="*60)
                    logger.info(f"📋 デフォルトタスク ({role}) として処理")
                    logger.info("="*60)
                    
                    if role == 'design':
                        task_coro = self._execute_design_task(task)
                    elif role == 'dev':
                        task_coro = self._execute_dev_task(task)
                    elif role == 'ui':
                        task_coro = self._execute_ui_task(task)
                    elif role == 'wordpress':
                        task_coro = self._execute_wordpress_task(task)
                    elif role == 'plugin':
                        task_coro = self._execute_plugin_task(task)
                    else:
                        # 未登録エージェント
                        agent = self.agents.get(role)
                        if not agent:
                            logger.warning(f"担当エージェント '{role}' が見つかりません - スキップします")
                            await self.update_task_status(task, 'skipped', error=f"エージェント未登録")
                            return False
                        task_coro = agent.process_task(task)
                
                # --- 3-4: タイムアウト付きで実行 ---
                if HAS_ENHANCED_HANDLER:
                    result = await EnhancedErrorHandler.timeout_wrapper(
                        task_coro,
                        timeout=task_timeout,
                        context=f"タスク {task_id} 実行"
                    )
                else:
                    result = await asyncio.wait_for(task_coro, timeout=task_timeout)
            
            # ============================================================
            # === パート4: タイムアウトエラーハンドリング ===
            # ============================================================
            except asyncio.TimeoutError:
                logger.error("="*60)
                logger.error(f"⏱️ タスク {task_id} タイムアウト（{task_timeout}秒）")
                logger.error("="*60)
                
                await self.update_task_status(
                    task, 
                    'failed', 
                    error=f'タイムアウト（{task_timeout}秒）'
                )
                
                print("\n" + "📷"*40)
                print("=" * 80)
                print(f"⏱️ タスクタイムアウト: {task_id}")
                print(f"制限時間: {task_timeout}秒")
                print("=" * 80)
                print("📷"*40 + "\n")
                
                return False
            
            # ============================================================
            # === パート5: 一般的な例外ハンドリング ===
            # ============================================================
            except Exception as e:
                logger.error("="*60)
                logger.error(f"❌ タスク {task_id} 実行中に例外発生")
                logger.error(f"エラー: {str(e)}")
                logger.error("="*60)
                
                if HAS_ENHANCED_HANDLER:
                    EnhancedErrorHandler.log_error_with_context(
                        e, 
                        f"タスク {task_id} 実行"
                    )
                
                await self.update_task_status(task, 'failed', error=str(e))
                
                print("\n" + "📷"*40)
                print("=" * 80)
                print(f"💥 タスク例外: {task_id}")
                print(f"例外: {str(e)}")
                print("=" * 80)
                print("📷"*40 + "\n")
                
                return False
            
            # ============================================================
            # === パート6: 実行結果の処理（成功時） ===
            # ============================================================
            if result and result.get('success'):
                logger.info("="*60)
                logger.info(f"✅ タスク {task_id} 実行成功")
                logger.info("="*60)
                
                # --- 6-1: 結果保存 ---
                try:
                    await self.update_task_status(task, 'completed')
                    await self.save_task_output(task, result)
                except Exception as e:
                    logger.warning(f"⚠️ 結果保存失敗（タスク自体は成功）: {e}")
                
                # --- 6-2: レビューAIでチェック ---
                if self.review_agent and role != 'review' and task_type != 'review':
                    try:
                        logger.info("="*60)
                        logger.info("✅ レビューAIでチェックを開始")
                        logger.info("="*60)
                        
                        if HAS_ENHANCED_HANDLER:
                            await EnhancedErrorHandler.timeout_wrapper(
                                self.perform_review_and_add_tasks(task, result),
                                timeout=120.0,
                                context=f"レビュー（タスク {task_id}）"
                            )
                        else:
                            await asyncio.wait_for(
                                self.perform_review_and_add_tasks(task, result),
                                timeout=120.0
                            )
                    except Exception as e:
                        logger.warning(f"⚠️ レビュー失敗（無視）: {e}")
                
                # --- 6-3: 成功メッセージ表示 ---
                print("\n" + "📷"*40)
                print("=" * 80)
                print(f"✅ タスク完了: {task_id}")
                print(f"タイプ: {task_type.upper()}")
                print(f"ステータス: 成功")
                print("=" * 80)
                print("📷"*40 + "\n")
                
                return True
            
            # ============================================================
            # === パート7: 実行結果の処理（失敗時） ===
            # ============================================================
            else:
                error_msg = result.get('error', '不明') if result else '結果なし'
                logger.error("="*60)
                logger.error(f"❌ タスク {task_id} 実行失敗")
                logger.error(f"エラー: {error_msg}")
                logger.error("="*60)
                
                await self.update_task_status(task, 'failed', error=error_msg)
                
                print("\n" + "📷"*40)
                print("=" * 80)
                print(f"❌ タスク失敗: {task_id}")
                print(f"タイプ: {task_type.upper()}")
                print(f"エラー: {error_msg}")
                print("=" * 80)
                print("📷"*40 + "\n")
                
                return False
        
        # ============================================================
        # === パート8: 最外層の例外ハンドリング ===
        # ============================================================
        except Exception as e:
            logger.error(f"❌ タスク {task_id} 処理全体で予期しないエラー")
            
            if HAS_ENHANCED_HANDLER:
                EnhancedErrorHandler.log_error_with_context(
                    e, 
                    f"タスク {task_id} 全体処理"
                )
            else:
                ErrorHandler.log_error(e, f"タスク {task_id} 実行")
            
            try:
                await self.update_task_status(task, 'failed', error=str(e))
            except:
                pass
            
            print("\n" + "📷"*40)
            print("=" * 80)
            print(f"💥 タスク重大エラー: {task_id}")
            print(f"例外: {str(e)}")
            print("=" * 80)
            print("📷"*40 + "\n")
            
            return False

    async def _execute_wp_design_task(self, task: Dict) -> Dict:
        """WordPress設計タスクを実行"""
        logger.info("┌" + "─"*58 + "┐")
        logger.info("│ 🎨 WordPress設計AIエージェント実行中")
        logger.info("├" + "─"*58 + "┤")
        logger.info(f"│ タスク: {task.get('description', 'N/A')[:50]}")
        logger.info("└" + "─"*58 + "┘")
        
        try:
            # === パート1: エージェント取得 ===
            agent = self.agents.get('wp_design')
            if not agent:
                logger.error("❌ WordPress設計AIエージェントが登録されていません")
                return {
                    'success': False,
                    'error': 'wp_design エージェントが登録されていません'
                }

            # === パート2: タスク実行 ===
            result = await agent.process_task(task)
            
            # === パート3: 結果ログ出力 ===
            if result.get('success'):
                logger.info("✅ WordPress設計AI: タスク完了")
            else:
                logger.error(f"❌ WordPress設計AI: 失敗 - {result.get('error', '不明')}")
            
            return result
            
        except Exception as e:
            ErrorHandler.log_error(e, "WordPress設計タスク実行")
            logger.error(f"❌ WordPress設計AIエージェント: 例外発生 - {str(e)}")
            return {
                'success': False,
                'error': f'WordPress設計タスク実行エラー: {str(e)}'
            }

    async def _execute_wp_dev_task(self, task: Dict) -> Dict:
        """WordPress開発タスクを実行"""
        logger.info("┌" + "─"*58 + "┐")
        logger.info("│ 💻 WordPress開発AIエージェント実行中")
        logger.info("├" + "─"*58 + "┤")
        logger.info(f"│ タスク: {task.get('description', 'N/A')[:50]}")
        logger.info("└" + "─"*58 + "┘")
        
        try:
            # === パート1: エージェント取得 ===
            agent = self.agents.get('wp_dev')
            if not agent:
                logger.error("❌ WordPress開発AIエージェントが登録されていません")
                return {
                    'success': False,
                    'error': 'wp_dev エージェントが登録されていません'
                }
            
            # === パート2: タスク実行 ===
            result = await agent.process_task(task)
            
            # === パート3: 結果ログ出力 ===
            if result.get('success'):
                logger.info("✅ WordPress開発AI: タスク完了")
            else:
                logger.error(f"❌ WordPress開発AI: 失敗 - {result.get('error', '不明')}")
            
            return result
            
        except Exception as e:
            ErrorHandler.log_error(e, "WordPress開発タスク実行")
            logger.error(f"❌ WordPress開発AIエージェント: 例外発生 - {str(e)}")
            return {
                'success': False,
                'error': f'WordPress開発タスク実行エラー: {str(e)}'
            }

    # スタブメソッド（実際の実装では適切に定義）
    async def update_task_status(self, task: Dict, status: str, error: Optional[str] = None):
        """タスクステータスを更新"""
        logger.info(f"タスク {task.get('task_id')} ステータスを {status} に更新")
        if error:
            logger.info(f"エラー: {error}")

    async def save_task_output(self, task: Dict, result: Dict):
        """タスク出力を保存"""
        logger.info(f"タスク {task.get('task_id')} の結果を保存")

    async def perform_review_and_add_tasks(self, task: Dict, result: Dict):
        """レビューを実行してタスクを追加"""
        logger.info(f"タスク {task.get('task_id')} のレビューを実行")

    async def _execute_review_task(self, task: Dict) -> Dict:
        """レビュータスクを実行"""
        return {'success': True}

    async def _execute_design_task(self, task: Dict) -> Dict:
        """デザインタスクを実行"""
        return {'success': True}

    async def _execute_dev_task(self, task: Dict) -> Dict:
        """開発タスクを実行"""
        return {'success': True}

    async def _execute_ui_task(self, task: Dict) -> Dict:
        """UIタスクを実行"""
        return {'success': True}

    async def _execute_wordpress_task(self, task: Dict) -> Dict:
        """WordPressタスクを実行"""
        return {'success': True}

    async def _execute_plugin_task(self, task: Dict) -> Dict:
        """プラグインタスクを実行"""
        return {'success': True}


# 使用例
async def main():
    """テスト用のメイン関数"""
    executor = WordPressTaskExecutor()
    
    # テストタスク
    test_task = {
        'task_id': 'TEST_001',
        'description': 'WordPressサイトのデザイン作成',
        'required_role': 'wp_design'
    }
    
    result = await executor.execute_task(test_task)
    print(f"タスク実行結果: {result}")


if __name__ == "__main__":
    # テスト実行
    asyncio.run(main())