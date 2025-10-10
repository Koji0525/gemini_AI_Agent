"""
task_executor.py - タスク実行コントローラー（完全版）
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# ===== 設定とユーティリティ =====
from config_utils import ErrorHandler, config

# ===== データ管理 =====
from sheets_manager import GoogleSheetsManager

# ===== エラーハンドラー（オプション） =====
try:
    from error_handler_enhanced import (
        EnhancedErrorHandler,
        TaskErrorHandler
    )
    HAS_ENHANCED_HANDLER = True
except ImportError:
    HAS_ENHANCED_HANDLER = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ error_handler_enhanced未検出（標準エラーハンドラー使用）")

# ===== 分離モジュール =====
try:
    from task_executor_content import ContentTaskExecutor
    from task_executor_ma import MATaskExecutor
    HAS_SPECIALIZED_EXECUTORS = True
except ImportError:
    HAS_SPECIALIZED_EXECUTORS = False
    ContentTaskExecutor = None
    MATaskExecutor = None

# ===== WordPress連携（オプション） =====
try:
    from wordpress.wp_utils import task_router
    HAS_TASK_ROUTER = True
except ImportError:
    HAS_TASK_ROUTER = False
    task_router = None

logger = logging.getLogger(__name__)


class TaskExecutor:
    """タスク実行コントローラー(エラーハンドリング強化版)"""
    
    def __init__(
        self, 
        sheets_manager: GoogleSheetsManager, 
        browser_controller=None, 
        max_iterations: int = None
    ):
        """
        初期化
        
        Args:
            sheets_manager: GoogleSheetsManager インスタンス
            browser_controller: BrowserController インスタンス(オプション)
            max_iterations: 最大反復回数
        """
        self.sheets_manager = sheets_manager
        self.browser = browser_controller
        self.agents = {}
        self.review_agent = None
        
        if max_iterations is None:
            self.max_iterations = config.MAX_ITERATIONS
        else:
            self.max_iterations = max_iterations
        
        self.current_iteration = 0
        
        logger.info(f"TaskExecutor: 最大反復回数 = {self.max_iterations}")
        
        # エージェントを自動初期化
        self._initialize_agents()
        
        # === 分離モジュール初期化 ===
        if HAS_SPECIALIZED_EXECUTORS and ContentTaskExecutor and MATaskExecutor:
            try:
                # 記事生成専用エグゼキュータ
                self.content_executor = ContentTaskExecutor(self.agents)
                logger.info("✅ ContentTaskExecutor 初期化完了")
                
                # M&A専用エグゼキュータ
                self.ma_executor = MATaskExecutor(self.agents)
                logger.info("✅ MATaskExecutor 初期化完了")
                
                logger.info("="*60)
                logger.info("分離モジュール初期化完了")
                logger.info("  - ContentTaskExecutor (記事生成専用)")
                logger.info("  - MATaskExecutor (M&A/企業検索専用)")
                logger.info("="*60)
            except Exception as e:
                logger.warning(f"⚠️ 分離モジュール初期化失敗: {e}")
                self.content_executor = None
                self.ma_executor = None
        else:
            logger.warning("⚠️ 分離モジュールが利用できません")
            self.content_executor = None
            self.ma_executor = None
        
        # === ⭐ WordPress開発専用エージェント初期化 ===
        # ⚠️ 重要: このブロックは __init__ メソッド内に配置する
        # ⚠️ インデント: クラスメソッド内なので先頭から8スペース
        logger.info("\n" + "="*60)
        logger.info("🔧 WordPress開発エージェント初期化中...")
        logger.info("="*60)
        
        # WordPress開発エージェント (wp_dev) の初期化
        self.wp_dev_agent = None
        try:
            # wordpress/wp_dev.py から WordPressDevAgent をインポート
            from wordpress.wp_dev import WordPressDevAgent
            
            # ブラウザコントローラーが利用可能な場合のみ初期化
            if self.browser:
                self.wp_dev_agent = WordPressDevAgent(self.browser)
                # シートマネージャーを共有
                if hasattr(self.wp_dev_agent, 'sheets_manager'):
                    self.wp_dev_agent.sheets_manager = self.sheets_manager
                
                # エージェント登録
                self.agents['wp_dev'] = self.wp_dev_agent
                logger.info("✅ WordPressDevAgent (wp_dev) 登録完了")
            else:
                logger.warning("⚠️ ブラウザコントローラー未初期化のため wp_dev スキップ")
                
        except ImportError as e:
            logger.warning(f"⚠️ wordpress/wp_dev.py のインポート失敗: {e}")
            logger.info("💡 WordPress開発タスクは標準 dev エージェントで処理されます")
        except Exception as e:
            logger.warning(f"⚠️ wp_dev エージェント初期化エラー: {e}")
        
        # WordPress設計エージェント (wp_design) の初期化
        self.wp_design_agent = None
        try:
            from wordpress.wp_design import WordPressDesignAgent
            
            if self.browser:
                self.wp_design_agent = WordPressDesignAgent(self.browser)
                if hasattr(self.wp_design_agent, 'sheets_manager'):
                    self.wp_design_agent.sheets_manager = self.sheets_manager
                
                self.agents['wp_design'] = self.wp_design_agent
                logger.info("✅ WordPressDesignAgent (wp_design) 登録完了")
            else:
                logger.warning("⚠️ ブラウザコントローラー未初期化のため wp_design スキップ")
                
        except ImportError as e:
            logger.warning(f"⚠️ wordpress/wp_design.py のインポート失敗: {e}")
            logger.info("💡 WordPress設計タスクは標準 design エージェントで処理されます")
        except Exception as e:
            logger.warning(f"⚠️ wp_design エージェント初期化エラー: {e}")
        
        logger.info("="*60)
        logger.info("WordPress専用エージェント初期化完了")
        if self.wp_dev_agent:
            logger.info("  - WordPressDevAgent (カスタム開発)")
        if self.wp_design_agent:
            logger.info("  - WordPressDesignAgent (テーマ/CSS)")
        logger.info("="*60)
    
    # ⬇️ ここから次のメソッド（__init__ の外側）
    def _initialize_agents(self):
        """エージェントの自動初期化"""
        logger.info("エージェントを初期化中...")
        # エージェントは外部から register_agent() で登録される
        logger.info("エージェント初期化完了")
    
    def _initialize_agents(self):
        """エージェントの自動初期化"""
        logger.info("エージェントを初期化中...")
        # エージェントは外部から register_agent() で登録される
        logger.info("エージェント初期化完了")
    
    def register_agent(self, role: str, agent):
        """エージェントを登録"""
        self.agents[role] = agent
        logger.info(f"エージェント '{role}' を登録しました")
    
    def register_review_agent(self, review_agent):
        """レビューエージェントを登録"""
        self.review_agent = review_agent
        logger.info("レビューエージェントを登録しました")
    

    async def load_pending_tasks(self) -> List[Dict]:
        """保留中のタスクを読み込む（エラーハンドリング強化版）"""
        try:
            logger.info("📋 保留中のタスクを読み込み中...")
            tasks = await self.sheets_manager.load_tasks_from_sheet('pm_tasks')
            
            if not tasks:
                logger.info("📭 pm_tasksシートにタスクがありません")
                return []
            
            # statusが'pending'のタスクのみをフィルタ
            pending_tasks = [
                task for task in tasks 
                if task.get('status', '').lower() == 'pending'
            ]
            
            logger.info(f"📊 保留中のタスク: {len(pending_tasks)}件")
            
            # デバッグ情報
            if pending_tasks:
                for i, task in enumerate(pending_tasks[:3]):  # 最初の3件を表示
                    logger.info(f"  {i+1}. {task.get('description', '')[:60]}...")
                if len(pending_tasks) > 3:
                    logger.info(f"  ... 他 {len(pending_tasks)-3}件")
            
            return pending_tasks
            
        except Exception as e:
            logger.error(f"❌ タスク読み込みエラー: {e}")
            return []
    
    async def update_task_status(self, task: Dict, status: str, error_message: str = None) -> bool:
        """タスクステータスを更新（非同期エラー修正版）"""
        try:
            task_id = task.get('task_id')
            
            if error_message:
                logger.info(f"タスク {task_id} ステータス更新: {status} - エラー: {error_message}")
            else:
                logger.info(f"タスク {task_id} ステータス更新: {status}")
            
            # 非同期関数かどうかを確認して適切に呼び出す
            update_method = self.sheets_manager.update_task_status
            
            import inspect
            if inspect.iscoroutinefunction(update_method):
                # 非同期メソッドの場合
                result = await update_method(task_id, status)
            else:
                # 同期メソッドの場合
                result = update_method(task_id, status)
            
            # 結果がNoneの場合のデフォルト処理
            if result is None:
                logger.warning(f"⚠️ ステータス更新の結果がNoneです - タスク {task_id}")
                return True  # 失敗ではないのでTrueを返す
                
            return bool(result)
            
        except Exception as e:
            logger.warning(f"⚠️ ステータス更新失敗（続行）: {e}")
            return False
    
    async def save_task_output(self, task: Dict, result: Dict):
        """タスクの出力を保存"""
        try:
            task_id = task.get('task_id', 'UNKNOWN')
            logger.info(f"タスク {task_id} の出力を保存中...")
            
            output_data = {
                'task_id': task_id,
                'summary': result.get('summary', ''),
                'full_text': result.get('full_text', ''),
                'screenshot': result.get('screenshot', ''),
                'timestamp': datetime.now().isoformat()
            }
            
            await self.sheets_manager.save_task_output(output_data)
            logger.info("✅ 出力保存完了")
            
        except Exception as e:
            logger.warning(f"⚠️ 出力保存失敗（無視）: {e}")
            
            # === パート2: タスクタイプ判定 ===
            task_type = 'default'
            if HAS_TASK_ROUTER and task_router:
                try:
                    task_type = task_router.determine_task_type(task)
                    logger.info(f"📊 タスクタイプ判定: {task_type}")
                    print(f"🔍 タスクタイプ: {task_type.upper()}")
                except Exception as e:
                    logger.warning(f"⚠️ タスクタイプ判定失敗、デフォルト処理: {e}")
            
            print("=" * 80)
            print("🔷"*40 + "\n")
            
            logger.info(f"タスク {task_id} 実行開始")
            
            # === パート3: タスクステータス更新（実行中）===
            try:
                await self.update_task_status(task, 'in_progress')
            except Exception as e:
                logger.warning(f"⚠️ ステータス更新失敗（続行）: {e}")
            
            # === パート4: 担当エージェント取得 ===
            role = task['required_role'].lower()
            
            # === パート5: タスクタイムアウト設定 ===
            timeout_map = {
                'ma': 300.0,
                'content': 240.0,
                'review': 180.0,
                'wordpress': 300.0,
                'wp_dev': 300.0,
                'wp_design': 300.0,
                'default': 180.0
            }
            task_timeout = timeout_map.get(task_type, 180.0)
            
            # === パート6: タスク実行（タイムアウト付き）===
            result = None
            
            try:
                # タスク実行のコルーチンを作成
                if task_type == 'ma' and self.ma_executor:
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
                
                # === wp_dev と wp_design の処理 ===
                elif role == 'wp_dev':
                    logger.info("="*60)
                    logger.info("🔧 WordPress開発タスクとして処理")
                    logger.info("="*60)
                    
                    # 優先順位1: 専用 wp_dev エージェント
                    agent = self.agents.get('wp_dev')
                    if agent:
                        logger.info("✅ 専用 WordPressDevAgent を使用")
                        task_coro = agent.process_task(task)
                    else:
                        # 優先順位2: 標準 dev エージェントにフォールバック
                        fallback_agent = self.agents.get('dev')
                        if fallback_agent:
                            logger.info("🔄 wp_dev エージェントが見つかりません - dev エージェントにフォールバック")
                            
                            # タスクの説明を確認して要件定義タスクか判定
                            description = task.get('description', '').lower()
                            if any(keyword in description for keyword in ['要件定義', '設計書', '仕様書']):
                                # 要件定義タスクの場合: dev エージェントで処理
                                logger.info("📋 要件定義タスクとして処理")
                                task_coro = fallback_agent.process_task(task)
                            else:
                                # その他のWordPress開発タスク: wordpress エージェントで処理
                                logger.info("🌐 WordPress実装タスクとして処理")
                                task_coro = self._execute_wordpress_task(task)
                        else:
                            # 優先順位3: wordpress エージェント
                            wp_agent = self.agents.get('wordpress')
                            if wp_agent:
                                logger.info("🌐 WordPress汎用エージェントで処理")
                                task_coro = wp_agent.process_task(task)
                            else:
                                logger.error("❌ wp_dev, dev, wordpress エージェントがすべて見つかりません")
                                return {
                                    'success': False, 
                                    'error': 'WordPress開発タスクを処理できるエージェントが登録されていません'
                                }
                
                elif role == 'wp_design':
                    logger.info("="*60)
                    logger.info("🎨 WordPress設計タスクとして処理")
                    logger.info("="*60)
                    
                    # 優先順位1: 専用 wp_design エージェント
                    agent = self.agents.get('wp_design')
                    if agent:
                        logger.info("✅ 専用 WordPressDesignAgent を使用")
                        task_coro = agent.process_task(task)
                    else:
                        # 優先順位2: 標準 design エージェントにフォールバック
                        fallback_agent = self.agents.get('design')
                        if fallback_agent:
                            logger.warning("⚠️ wp_design エージェントが見つかりません - design エージェントにフォールバック")
                            task_coro = fallback_agent.process_task(task)
                        else:
                            logger.error("❌ wp_design および design エージェントが見つかりません")
                            return {
                                'success': False,
                                'error': 'WordPress設計タスクを処理できるエージェントが登録されていません'
                            }
                
                else:
                    # === パート7: デフォルトタスク処理 ===
                    logger.info("="*60)
                    logger.info(f"📋 デフォルトタスク ({role}) として処理")
                    logger.info("="*60)
                    
                    # 従来のロジック
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
                            await self.update_task_status(task, 'skipped')
                            return False
                        task_coro = agent.process_task(task)
                
                # === パート8: タイムアウト付き実行 ===
                if HAS_ENHANCED_HANDLER:
                    result = await EnhancedErrorHandler.timeout_wrapper(
                        task_coro,
                        timeout=task_timeout,
                        context=f"タスク {task_id} 実行"
                    )
                else:
                    result = await asyncio.wait_for(task_coro, timeout=task_timeout)
            
            except asyncio.TimeoutError:
                # === パート9: タイムアウト処理 ===
                logger.error("="*60)
                logger.error(f"⏱️ タスク {task_id} タイムアウト（{task_timeout}秒）")
                logger.error("="*60)
                
                await self.update_task_status(task, 'failed')
                
                print("\n" + "🔷"*40)
                print("=" * 80)
                print(f"⏱️ タスクタイムアウト: {task_id}")
                print(f"制限時間: {task_timeout}秒")
                print("=" * 80)
                print("🔷"*40 + "\n")
                
                return False
            
            except Exception as e:
                # === パート10: 実行時例外処理 ===
                logger.error("="*60)
                logger.error(f"❌ タスク {task_id} 実行中に例外発生")
                logger.error(f"エラー: {str(e)}")
                logger.error("="*60)
                
                if HAS_ENHANCED_HANDLER:
                    EnhancedErrorHandler.log_error_with_context(
                        e, 
                        f"タスク {task_id} 実行"
                    )
                
                await self.update_task_status(task, 'failed')
                
                print("\n" + "🔷"*40)
                print("=" * 80)
                print(f"💥 タスク例外: {task_id}")
                print(f"例外: {str(e)}")
                print("=" * 80)
                print("🔷"*40 + "\n")
                
                return False

            # === パート11: 実行結果の処理 ===
            if result and result.get('success'):
                # === 成功時の処理 ===
                logger.info("="*60)
                logger.info(f"✅ タスク {task_id} 実行成功")
                logger.info("="*60)

                # === 🆕 新規追加: トレーサビリティ情報の記録 ===
                result['_traceability'] = {
                    'task_id': task_id,
                    'executed_by_agent': role,
                    'task_type': task_type,
                    'execution_timestamp': datetime.now().isoformat(),
                    'agent_class': agent.__class__.__name__ if 'agent' in locals() else 'N/A',
                    'output_file': result.get('output_file', 'N/A'),
                    'task_description': task.get('description', '')[:100]
                }

                logger.info(f"📋 トレーサビリティ: エージェント={role}, タスクタイプ={task_type}")

                try:
                    await self.update_task_status(task, 'completed')
                    await self.save_task_output(task, result)
                except Exception as e:
                    logger.warning(f"⚠️ 結果保存失敗(タスク自体は成功): {e}")
                
                # === パート12: レビューAIによるチェック ===
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
                
                print("\n" + "🔷"*40)
                print("=" * 80)
                print(f"✅ タスク完了: {task_id}")
                print(f"タイプ: {task_type.upper()}")
                print(f"ステータス: 成功")
                print("=" * 80)
                print("🔷"*40 + "\n")
                
                return True
            else:
                # === 失敗時の処理 ===
                error_msg = result.get('error', '不明') if result else '結果なし'
                logger.error("="*60)
                logger.error(f"❌ タスク {task_id} 実行失敗")
                logger.error(f"エラー: {error_msg}")
                logger.error("="*60)
                
                await self.update_task_status(task, 'failed')
                
                print("\n" + "🔷"*40)
                print("=" * 80)
                print(f"❌ タスク失敗: {task_id}")
                print(f"タイプ: {task_type.upper()}")
                print(f"エラー: {error_msg}")
                print("=" * 80)
                print("🔷"*40 + "\n")
                
                return False
        
        except Exception as e:
            # === パート13: 全体例外処理 ===
            logger.error(f"❌ タスク {task_id} 処理全体で予期しないエラー")
            
            if HAS_ENHANCED_HANDLER:
                EnhancedErrorHandler.log_error_with_context(
                    e, 
                    f"タスク {task_id} 全体処理"
                )
            else:
                ErrorHandler.log_error(e, f"タスク {task_id} 実行")
            
            try:
                await self.update_task_status(task, 'failed')
            except:
                pass
            
            print("\n" + "🔷"*40)
            print("=" * 80)
            print(f"💥 タスク重大エラー: {task_id}")
            print(f"例外: {str(e)}")
            print("=" * 80)
            print("🔷"*40 + "\n")
            
            return False
    

    def _create_task_coroutine(self, task: Dict, role: str, task_type: str):
        """タスクコルーチンを作成（安全なメソッド呼び出し）"""
        try:
            if task_type == 'ma' and self.ma_executor:
                logger.info("="*60)
                logger.info("📊 M&A/企業検索タスクとして処理")
                logger.info("="*60)
                return self.ma_executor.execute_ma_task(task)
            
            elif task_type == 'content' and self.content_executor:
                logger.info("="*60)
                logger.info("✏️ 記事生成タスクとして処理")
                logger.info("="*60)
                return self.content_executor.execute_writer_task(task, role)
            
            elif task_type == 'review':
                logger.info("="*60)
                logger.info("✅ レビュータスクとして処理")
                logger.info("="*60)
                return self._execute_review_task(task)
            
            # === wp_dev と wp_design の処理 ===
            elif role == 'wp_dev':
                logger.info("="*60)
                logger.info("🔧 WordPress開発タスクとして処理")
                logger.info("="*60)
                agent = self.agents.get('wp_dev')
                if agent:
                    return agent.process_task(task)
                else:
                    # dev エージェントを優先フォールバックとして使用
                    fallback_agent = self.agents.get('dev')
                    if fallback_agent:
                        logger.info("🔄 wp_dev エージェントが見つかりません - dev エージェントにフォールバック")
                        return fallback_agent.process_task(task)
                    else:
                        logger.error("❌ wp_dev エージェントも dev エージェントも見つかりません")
                        return None
            
            elif role == 'wp_design':
                logger.info("="*60)
                logger.info("🎨 WordPress設計タスクとして処理")
                logger.info("="*60)
                agent = self.agents.get('wp_design')
                if agent:
                    return agent.process_task(task)
                else:
                    logger.warning("⚠️ wp_design エージェントが見つかりません - 通常処理にフォールバック")
                    return self._execute_design_task(task)
            
            else:
                # === デフォルトタスク処理 ===
                logger.info("="*60)
                logger.info(f"📋 デフォルトタスク ({role}) として処理")
                logger.info("="*60)
                
                # 従来のロジック（安全なメソッド呼び出し）
                if role == 'design':
                    return self._execute_design_task(task)
                elif role == 'dev':
                    return self._execute_dev_task(task)
                elif role == 'ui':
                    return self._execute_ui_task(task)
                elif role == 'wordpress':
                    return self._execute_wordpress_task(task)
                elif role == 'plugin':
                    return self._execute_plugin_task(task)
                else:
                    # 未登録エージェント
                    agent = self.agents.get(role)
                    if not agent:
                        logger.warning(f"担当エージェント '{role}' が見つかりません")
                        return None
                    return agent.process_task(task)
                    
        except Exception as e:
            logger.error(f"❌ タスクコルーチン作成エラー: {e}")
            return None
    
    def _extract_missing_method_name(self, error_msg: str) -> str:
        """エラーメッセージから不足しているメソッド名を抽出"""
        try:
            # エラーメッセージ例: "'BrowserController' object has no attribute '_wait_for_generation_complete'"
            import re
            match = re.search(r"has no attribute '([^']+)'", error_msg)
            if match:
                return match.group(1)
            return "unknown_method"
        except:
            return "unknown_method"
    
    def _get_available_browser_methods(self) -> str:
        """利用可能なBrowserControllerメソッドの一覧を取得"""
        if not self.browser:
            return "ブラウザコントローラーが初期化されていません"
        
        try:
            methods = [method for method in dir(self.browser) 
                      if not method.startswith('_') or method in ['_wait_for_generation_complete']]
            return ', '.join(sorted(methods))
        except:
            return "メソッド一覧取得失敗"
    
    async def _validate_output_quality(self, task: Dict, result: Dict) -> Dict:
        """アウトプット品質を検証"""
        try:
            task_description = task.get('description', '').lower()
            output_text = result.get('full_text', '')
            
            # 1. タスクタイプと出力の一致性チェック
            if self._is_documentation_task(task_description) and self._is_code_output(output_text):
                return {
                    'valid': False,
                    'message': 'タスクは文書作成ですが、コードが出力されました（アウトプットミスマッチ）'
                }
            
            # 2. 出力完全性チェック
            if self._is_incomplete_output(output_text):
                return {
                    'valid': False,
                    'message': '出力が不完全です（コードブロックや文書が途切れています）'
                }
            
            # 3. 最小文字数チェック
            if len(output_text.strip()) < 100:
                return {
                    'valid': False,
                    'message': f'出力が短すぎます（{len(output_text)}文字）'
                }
            
            return {'valid': True, 'message': '品質検証合格'}
            
        except Exception as e:
            logger.warning(f"⚠️ 品質検証エラー: {e}")
            return {'valid': True, 'message': '品質検証スキップ'}  # エラー時は通過
    
    async def _execute_design_task(self, task: Dict) -> Dict:
        """設計タスクを実行"""
        agent = self.agents.get('design')
        if not agent:
            return {'success': False, 'error': 'デザインエージェントが登録されていません'}
        return await agent.process_task(task)

    async def _execute_dev_task(self, task: Dict) -> Dict:
        """開発タスクを実行"""
        agent = self.agents.get('dev')
        if not agent:
            return {'success': False, 'error': '開発エージェントが登録されていません'}
        
        try:
            # === パート: ブラウザ操作のエラーハンドリング強化 ===
            if not self.browser:
                return {'success': False, 'error': 'ブラウザコントローラーが初期化されていません'}
            
            # タスク実行前にブラウザ状態を確認
            if not await self.browser._is_browser_alive():
                logger.error("❌ ブラウザが応答しません")
                return {'success': False, 'error': 'ブラウザがクラッシュまたは応答不可'}
            
            # エージェントにブラウザコントローラーを設定（もし必要なら）
            if hasattr(agent, 'browser_controller'):
                agent.browser_controller = self.browser
            
            # タスク実行
            result = await agent.process_task(task)
            
            # === パート: 応答待機処理の改善 ===
            # 必要に応じて待機処理を追加（例: 特定のタスクタイプの場合）
            task_description = task.get('description', '').lower()
            if any(keyword in task_description for keyword in ['生成', '作成', '書き出し', 'export']):
                try:
                    # 新しい統合メソッドを使用
                    if hasattr(self.browser, 'send_prompt_and_wait'):
                        # 既にプロンプト送信済みの場合は待機のみ
                        await self.browser.wait_for_text_generation(180)
                    else:
                        # 後方互換性のためのフォールバック
                        await self.browser._wait_for_generation_complete(180)
                except Exception as e:
                    logger.warning(f"⚠️ 応答待機中にエラー（続行）: {e}")
            
            return result
            
        except Exception as e:
            ErrorHandler.log_error(e, "開発タスク実行")
            return {'success': False, 'error': f'開発タスク実行エラー: {str(e)}'}
    
    async def _execute_ui_task(self, task: Dict) -> Dict:
        """UIタスクを実行"""
        agent = self.agents.get('ui')
        if not agent:
            return {'success': False, 'error': 'UIエージェントが登録されていません'}
        return await agent.process_task(task)

    async def _execute_wordpress_task(self, task: Dict) -> Dict:
        """WordPressタスクを実行"""
        try:
            # === パート1: 実行開始ヘッダー ===
            logger.info("┌" + "─"*58 + "┐")
            logger.info("│ 🌐 WordPress AIエージェント実行中")
            logger.info("├" + "─"*58 + "┤")
            logger.info(f"│ アクション: {task.get('post_action', 'N/A')}")
            logger.info(f"│ 言語: {task.get('language', 'N/A')}")
            logger.info(f"│ Polylang: {task.get('polylang_lang', 'N/A')}")
            logger.info("└" + "─"*58 + "┘")
            
            # === パート2: M&A関連タスクの再判定 ===
            if HAS_TASK_ROUTER and task_router and task_router.is_ma_task(task):
                logger.info("📊 M&A関連タスクとして再振り分け")
                if self.ma_executor:
                    return await self.ma_executor.execute_ma_task(task)
            
            # === パート3: パラメータのデフォルト設定 ===
            if 'post_action' not in task:
                task['post_action'] = 'edit'
            if 'polylang_lang' not in task:
                task['polylang_lang'] = 'ja'
            
            # === パート4: エージェント取得と実行 ===
            agent = self.agents.get('wordpress')
            if not agent:
                logger.error("❌ WordPress AIエージェントが登録されていません")
                return {
                    'success': False,
                    'error': 'wordpress エージェントが登録されていません'
                }
            
            # === パート: ブラウザ状態チェック追加 ===
            if self.browser:
                # ブラウザ生存確認
                if not await self.browser._is_browser_alive():
                    logger.error("❌ ブラウザが応答しません - WordPressタスク実行不可")
                    return {
                        'success': False,
                        'error': 'ブラウザがクラッシュまたは応答不可'
                    }
                
                # エージェントにブラウザコントローラーを設定
                if hasattr(agent, 'browser_controller'):
                    agent.browser_controller = self.browser
            
            result = await agent.process_task(task)
            
            # === パート5: 結果の処理 ===
            if result.get('success'):
                logger.info("✅ WordPress AI: タスク完了")
            else:
                logger.error(f"❌ WordPress AI: 失敗 - {result.get('error', '不明')}")
            
            return result
            
        except Exception as e:
            # === パート6: 例外処理 ===
            ErrorHandler.log_error(e, "WordPressタスク実行")
            logger.error(f"❌ WordPress AIエージェント: 例外発生 - {str(e)}")
            return {
                'success': False,
                'error': f'WordPressタスク実行エラー: {str(e)}'
            }    

    async def _execute_wp_dev_task(self, task: Dict) -> Dict:
        """
        WordPress開発タスクを実行
        
        カスタム投稿タイプ(CPT)、Advanced Custom Fields(ACF)、
        カスタムタクソノミーなど、WordPress開発専用のタスクを処理
        
        Args:
            task: タスク情報辞書
            
        Returns:
            実行結果辞書
        """
        try:
            # === パート1: 実行開始ヘッダー ===
            logger.info("┌" + "─"*58 + "┐")
            logger.info("│ 🔧 WordPress開発AIエージェント実行中")
            logger.info("├" + "─"*58 + "┤")
            logger.info(f"│ タスク: {task.get('description', 'N/A')[:50]}")
            logger.info("└" + "─"*58 + "┘")
            
            # === パート2: エージェント取得 ===
            agent = self.agents.get('wp_dev')
            if not agent:
                # フォールバック: 標準 dev エージェント
                agent = self.agents.get('dev')
                if not agent:
                    logger.error("❌ WordPress開発AIエージェントが登録されていません")
                    return {
                        'success': False,
                        'error': 'wp_dev および dev エージェントが登録されていません'
                    }
                logger.info("🔄 標準 dev エージェントで代替処理")
            
            # === パート3: タスク実行 ===
            result = await agent.process_task(task)
            
            # === パート4: 結果の処理 ===
            if result.get('success'):
                logger.info("✅ WordPress開発AI: タスク完了")
            else:
                logger.error(f"❌ WordPress開発AI: 失敗 - {result.get('error', '不明')}")
            
            return result
            
        except Exception as e:
            # === パート5: 例外処理 ===
            ErrorHandler.log_error(e, "WordPress開発タスク実行")
            logger.error(f"❌ WordPress開発AIエージェント: 例外発生 - {str(e)}")
            return {
                'success': False,
                'error': f'WordPress開発タスク実行エラー: {str(e)}'
            }
    
    def _is_documentation_task(self, description: str) -> bool:
        """文書作成タスクか判定"""
        doc_keywords = ['要件定義', '設計書', '仕様書', '計画書', 'ドキュメント']
        return any(keyword in description for keyword in doc_keywords)

    def _is_code_output(self, output: str) -> bool:
        """コード出力か判定"""
        code_indicators = ['<?php', 'function', 'class', 'def ', 'import ', 'export ']
        return any(indicator in output for indicator in code_indicators)

    def _is_incomplete_output(self, output: str) -> bool:
        """出力が不完全かチェック"""
        # コードブロックの不完全性チェック
        if '```' in output and output.count('```') % 2 != 0:
            return True
    
        # PHPコードの不完全性チェック
        if '<?php' in output and '?>' not in output:
            return True
    
        # マークダウンの見出しが閉じられていない
        lines = output.split('\n')
        heading_lines = [line for line in lines if line.startswith('#')]
        if heading_lines and not lines[-1].strip():
            return True
    
        return False
    
    async def _execute_plugin_task(self, task: Dict) -> Dict:
        """プラグインタスクを実行"""
        agent = self.agents.get('plugin')
        if not agent:
            return {'success': False, 'error': 'プラグインエージェントが登録されていません'}
        return await agent.process_task(task)
    
    async def _execute_review_task(self, task: Dict) -> Dict:
        """レビュータスクを実行"""
        if not self.review_agent:
            return {'success': False, 'error': 'レビューエージェントが登録されていません'}
        
        try:
            review_target_id = task.get('review_target_task_id')
            if not review_target_id:
                return {'success': False, 'error': 'レビュー対象タスクIDが指定されていません'}
            
            # レビュー実行
            result = await self.review_agent.review_task(review_target_id)
            return result
            
        except Exception as e:
            ErrorHandler.log_error(e, "レビュータスク実行")
            return {'success': False, 'error': str(e)}
    
    async def perform_review_and_add_tasks(self, task: Dict, result: Dict):
        """タスク完了後のレビューと追加タスク生成"""
        try:
            # === パート1: レビュー開始 ===
            logger.info(f"\nタスク {task['task_id']} のレビューを開始...")
            
            # === パート2: レビュー対象コンテンツの準備 ===
            output_content = result.get('full_text', result.get('summary', ''))
            task['output_content'] = output_content
            
            # === パート3: レビュー実行 ===
            review_result = await self.review_agent.review_completed_task(task, output_content)
            
            if not review_result.get('success'):
                logger.warning("レビューに失敗しました")
                return
            
            # === パート4: レビュー結果の解析 ===
            review_data = review_result.get('review', {})
            next_actions = review_data.get('next_actions', {})
            
            if next_actions.get('required'):
                suggested_tasks = next_actions.get('suggested_tasks', [])
                
                if suggested_tasks:
                    print(f"\n提案タスク: {len(suggested_tasks)}件")
                    
                    # === パート5: ユーザーインタラクションループ ===
                    while True:
                        choice = input("\n提案タスクをどうしますか?\n"
                                    "(y)追加 / (n)スキップ / (v)確認 / (e)編集 / (m)手動入力 / (c)キャンセル: ").lower()
                        
                        # === パート6: 選択肢の処理 ===
                        if choice == 'y':
                            # タスク追加
                            added_count = await self.review_agent.add_suggested_tasks_to_sheet(
                                task['task_id'], 
                                suggested_tasks
                            )
                            print(f"{added_count}件のタスクを追加しました")
                            logger.info(f"{added_count}件のタスクを追加しました")
                            break
                        
                        elif choice == 'n':
                            # スキップ
                            print("タスク追加をスキップしました")
                            break
                        
                        elif choice == 'v':
                            # 確認表示
                            if self.content_executor:
                                self.content_executor.display_suggested_tasks(suggested_tasks)
                            else:
                                self._display_suggested_tasks(suggested_tasks)
                            continue
                        
                        elif choice == 'e':
                            # 編集
                            if self.content_executor:
                                edited_tasks = await self.content_executor.edit_suggested_tasks(suggested_tasks)
                            else:
                                edited_tasks = await self._edit_suggested_tasks(suggested_tasks)
                            
                            if edited_tasks:
                                confirm = input(f"編集後のタスク {len(edited_tasks)} 件を追加しますか? (y/n): ").lower()
                                if confirm == 'y':
                                    added_count = await self.review_agent.add_suggested_tasks_to_sheet(
                                        task['task_id'], 
                                        edited_tasks
                                    )
                                    print(f"{added_count}件のタスクを追加しました")
                                    break
                            continue
                        
                        elif choice == 'm':
                            # 手動入力
                            if self.content_executor:
                                manual_tasks = await self.content_executor.create_manual_tasks()
                            else:
                                manual_tasks = await self._create_manual_tasks()
                            
                            if manual_tasks:
                                confirm = input(f"手動入力したタスク {len(manual_tasks)} 件を追加しますか? (y/n): ").lower()
                                if confirm == 'y':
                                    added_count = await self.review_agent.add_suggested_tasks_to_sheet(
                                        task['task_id'], 
                                        manual_tasks
                                    )
                                    print(f"{added_count}件のタスクを追加しました")
                                    break
                            continue
                        
                        elif choice == 'c':
                            # キャンセル
                            print("タスク追加をキャンセルしました")
                            break
                        
                        else:
                            # 不正な入力
                            print("不正な入力です。y, n, v, e, m, c のいずれかを入力してください。")
                            continue
                else:
                    logger.info("レビュー結果: 追加タスク不要")
            else:
                logger.info("レビュー結果: 追加タスク不要")
        
        except Exception as e:
            # === パート7: レビュー処理全体の例外処理 ===
            ErrorHandler.log_error(e, "レビューとタスク追加")
    
    def _display_suggested_tasks(self, tasks: List[Dict]):
        """提案タスクを表示（フォールバック）"""
        print("\n" + "="*60)
        print("提案されたタスク:")
        print("="*60)
        for i, task in enumerate(tasks, 1):
            print(f"\n{i}. {task.get('description', 'N/A')}")
            print(f"   担当: {task.get('required_role', 'N/A')}")
            print(f"   優先度: {task.get('priority', 'medium')}")
        print("="*60)
    
    async def _edit_suggested_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """提案タスクを編集（フォールバック）"""
        print("\n編集機能は利用できません")
        return tasks
    
    async def _create_manual_tasks(self) -> List[Dict]:
        """手動タスク作成（フォールバック）"""
        print("\n手動作成機能は利用できません")
        return []
    
    # ========================================
    # タスク実行のメインディスパッチャー
    # ========================================
    
    async def execute_task(self, task: Dict) -> bool:
        """
        個別タスクを実行（メインディスパッチャー）
        
        このメソッドは、タスクの役割（required_role）に基づいて、
        適切なエージェントまたは実行メソッドに処理を振り分けます。
        
        Args:
            task: タスク情報の辞書
                - task_id: タスクID
                - description: タスク説明
                - required_role: 担当エージェントの役割
                - priority: 優先度
                - status: ステータス
                
        Returns:
            bool: タスク実行成功時 True、失敗時 False
        """
        task_id = task.get('task_id', 'UNKNOWN')
        
        try:
            # タスクがシートに存在するか最終確認
            task_exists = await self.sheets_manager.verify_task_exists(task_id)
            if not task_exists:
                logger.error(f"❌ タスク {task_id} はデータソースに存在しません - 実行をスキップ")
                return False
        except Exception as e:
            logger.warning(f"⚠️ タスク検証エラー（続行）: {e}")
        
        try:
            # === パート1: タスク実行開始ヘッダー ===
            logger.info("="*60)
            logger.info(f"📋 タスク実行開始: {task_id}")
            logger.info(f"説明: {task.get('description', 'N/A')[:80]}")
            logger.info(f"担当: {task.get('required_role', 'N/A')}")
            logger.info("="*60)
            logger.info(f"🔍 タスク {task_id} の健全性チェック中...")
            
            print("=" * 80)
            print("🔷"*40 + "\n")
            
            logger.info(f"タスク {task_id} 実行開始")
            
            # === パート2: タスクタイプ判定 ===
            task_type = 'default'
            if HAS_TASK_ROUTER and task_router:
                try:
                    task_type = task_router.determine_task_type(task)
                    logger.info(f"📊 タスクタイプ判定: {task_type}")
                    print(f"🔍 タスクタイプ: {task_type.upper()}")
                except Exception as e:
                    logger.warning(f"⚠️ タスクタイプ判定失敗、デフォルト処理: {e}")
            
            print("=" * 80)
            print("🔷"*40 + "\n")
            
            logger.info(f"タスク {task_id} 実行開始")
            
            # === パート3: タスクステータス更新（実行中）===
            try:
                await self.update_task_status(task, 'in_progress')
            except Exception as e:
                logger.warning(f"⚠️ ステータス更新失敗（続行）: {e}")
            
            # === パート4: 担当エージェント取得 ===
            role = task['required_role'].lower()
            
            # === パート5: タスクタイムアウト設定 ===
            timeout_map = {
                'ma': 300.0,
                'content': 240.0,
                'review': 180.0,
                'wordpress': 300.0,
                'wp_dev': 300.0,
                'wp_design': 300.0,
                'default': 180.0
            }
            task_timeout = timeout_map.get(task_type, 180.0)
            
            # === パート6: タスク実行（タイムアウト付き）===
            result = None
            
            try:
                # タスク実行のコルーチンを作成
                if task_type == 'ma' and self.ma_executor:
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
                
                # === wp_dev と wp_design の処理 ===
                elif role == 'wp_dev':
                    logger.info("="*60)
                    logger.info("🔧 WordPress開発タスクとして処理")
                    logger.info("="*60)
                    agent = self.agents.get('wp_dev')
                    if agent:
                        task_coro = agent.process_task(task)
                    else:
                        # dev エージェントを優先フォールバックとして使用
                        fallback_agent = self.agents.get('dev')
                        if fallback_agent:
                            logger.info("🔄 wp_dev エージェントが見つかりません - dev エージェントにフォールバック")
                            # タスクの説明を確認して要件定義タスクか判定
                            description = task.get('description', '').lower()
                            if any(keyword in description for keyword in ['要件定義', '設計書', '仕様書']):
                                # 要件定義タスクの場合
                                task_coro = fallback_agent.process_task(task)
                            else:
                                # その他のWordPress開発タスク
                                task_coro = self._execute_wordpress_task(task)
                        else:
                            logger.error("❌ wp_dev エージェントも dev エージェントも見つかりません")
                            return {
                                'success': False, 
                                'error': 'wp_dev および dev エージェントが登録されていません'
                            }
                
                elif role == 'wp_design':
                    logger.info("="*60)
                    logger.info("🎨 WordPress設計タスクとして処理")
                    logger.info("="*60)
                    agent = self.agents.get('wp_design')
                    if agent:
                        task_coro = agent.process_task(task)
                    else:
                        logger.warning("⚠️ wp_design エージェントが見つかりません - 通常処理にフォールバック")
                        task_coro = self._execute_design_task(task)
                
                else:
                    # === パート7: デフォルトタスク処理 ===
                    logger.info("="*60)
                    logger.info(f"📋 デフォルトタスク ({role}) として処理")
                    logger.info("="*60)
                    
                    # 従来のロジック
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
                            await self.update_task_status(task, 'skipped')
                            return False
                        task_coro = agent.process_task(task)
                
                # === パート8: タイムアウト付き実行 ===
                if HAS_ENHANCED_HANDLER:
                    result = await EnhancedErrorHandler.timeout_wrapper(
                        task_coro,
                        timeout=task_timeout,
                        context=f"タスク {task_id} 実行"
                    )
                else:
                    result = await asyncio.wait_for(task_coro, timeout=task_timeout)
            
            except asyncio.TimeoutError:
                # === パート9: タイムアウト処理 ===
                logger.error("="*60)
                logger.error(f"⏱️ タスク {task_id} タイムアウト（{task_timeout}秒）")
                logger.error("="*60)
                
                await self.update_task_status(task, 'failed')
                
                print("\n" + "🔷"*40)
                print("=" * 80)
                print(f"⏱️ タスクタイムアウト: {task_id}")
                print(f"制限時間: {task_timeout}秒")
                print("=" * 80)
                print("🔷"*40 + "\n")
                
                return False
            
            except Exception as e:
                # === パート10: 実行時例外処理 ===
                logger.error("="*60)
                logger.error(f"❌ タスク {task_id} 実行中に例外発生")
                logger.error(f"エラー: {str(e)}")
                logger.error("="*60)
                
                if HAS_ENHANCED_HANDLER:
                    EnhancedErrorHandler.log_error_with_context(
                        e, 
                        f"タスク {task_id} 実行"
                    )
                
                await self.update_task_status(task, 'failed')
                
                print("\n" + "🔷"*40)
                print("=" * 80)
                print(f"💥 タスク例外: {task_id}")
                print(f"例外: {str(e)}")
                print("=" * 80)
                print("🔷"*40 + "\n")
                
                return False
            
            # === パート11: 実行結果の処理 ===
            if result and result.get('success'):
                # === 成功時の処理 ===
                logger.info("="*60)
                logger.info(f"✅ タスク {task_id} 実行成功")
                logger.info("="*60)
                
                try:
                    await self.update_task_status(task, 'completed')
                    await self.save_task_output(task, result)
                except Exception as e:
                    logger.warning(f"⚠️ 結果保存失敗（タスク自体は成功）: {e}")
                
                # === パート12: レビューAIによるチェック ===
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
                
                print("\n" + "🔷"*40)
                print("=" * 80)
                print(f"✅ タスク完了: {task_id}")
                print(f"タイプ: {task_type.upper()}")
                print(f"ステータス: 成功")
                print("=" * 80)
                print("🔷"*40 + "\n")
                
                return True
            else:
                # === 失敗時の処理 ===
                error_msg = result.get('error', '不明') if result else '結果なし'
                logger.error("="*60)
                logger.error(f"❌ タスク {task_id} 実行失敗")
                logger.error(f"エラー: {error_msg}")
                logger.error("="*60)
                
                await self.update_task_status(task, 'failed')
                
                print("\n" + "🔷"*40)
                print("=" * 80)
                print(f"❌ タスク失敗: {task_id}")
                print(f"タイプ: {task_type.upper()}")
                print(f"エラー: {error_msg}")
                print("=" * 80)
                print("🔷"*40 + "\n")
                
                return False
        
        except Exception as e:
            # === パート13: 全体例外処理 ===
            logger.error(f"❌ タスク {task_id} 処理全体で予期しないエラー")
            
            if HAS_ENHANCED_HANDLER:
                EnhancedErrorHandler.log_error_with_context(
                    e, 
                    f"タスク {task_id} 全体処理"
                )
            else:
                ErrorHandler.log_error(e, f"タスク {task_id} 実行")
            
            try:
                await self.update_task_status(task, 'failed')
            except:
                pass
            
            print("\n" + "🔷"*40)
            print("=" * 80)
            print(f"💥 タスク重大エラー: {task_id}")
            print(f"例外: {str(e)}")
            print("=" * 80)
            print("🔷"*40 + "\n")
            
            return False
    
    async def run_all_tasks(self, auto_continue: bool = False, enable_review: bool = True):
        """
        全タスクを実行（エラーハンドリング強化版）
        """
        try:
            # === パート1: 実行開始ヘッダー ===
            logger.info("="*60)
            logger.info("タスク実行開始")
            logger.info("="*60)
            
            # === パート2: 変数初期化 ===
            iteration = 0
            tasks_executed = 0
            tasks_success = 0
            tasks_failed = 0
            failed_tasks_list = []
            
            # === パート3: メインループ（最大反復回数まで）===
            while iteration < self.max_iterations:
                iteration += 1
                
                logger.info(f"\n{'='*60}")
                logger.info(f"反復 {iteration}/{self.max_iterations}")
                logger.info(f"{'='*60}")
                
                try:
                    # === パート4: 保留中タスクの読み込み ===
                    pending_tasks = await self.load_pending_tasks()
                    
                    if not pending_tasks:
                        logger.info("✅ 全タスク完了または保留タスクなし")
                        break
                    
                    logger.info(f"📋 実行予定タスク: {len(pending_tasks)}件")
                    
                    # === パート5: タスク実行ループ ===
                    for task in pending_tasks:
                        task_id = task.get('task_id', 'UNKNOWN')
                        
                        try:
                            logger.info(f"\n{'─'*60}")
                            logger.info(f"タスク実行: {task_id}")
                            logger.info(f"{'─'*60}")
                            
                            tasks_executed += 1
                            
                            # === パート6: 個別タスク実行 ===
                            success = await self.execute_task(task)
                            
                            if success:
                                tasks_success += 1
                                logger.info(f"✅ タスク {task_id} 成功")
                            else:
                                tasks_failed += 1
                                failed_tasks_list.append({
                                    'task_id': task_id,
                                    'description': task.get('description', 'N/A')
                                })
                                logger.error(f"❌ タスク {task_id} 失敗")
                            
                            # === パート7: ユーザー確認（自動続行でない場合）===
                            if not auto_continue:
                                continue_task = input(
                                    f"\n次のタスクに進みますか? "
                                    f"(y/n/a=以降全て実行): "
                                ).lower()
                                
                                if continue_task == 'n':
                                    logger.info("ユーザーによる中断")
                                    return
                                elif continue_task == 'a':
                                    auto_continue = True
                                    logger.info("自動実行モードに切り替え")
                            
                            await asyncio.sleep(2)
                            
                        except KeyboardInterrupt:
                            logger.warning("⏸️ ユーザーによる中断")
                            raise
                        
                        except Exception as e:
                            # === パート8: 個別タスクエラー処理 ===
                            tasks_failed += 1
                            failed_tasks_list.append({
                                'task_id': task_id,
                                'description': task.get('description', 'N/A'),
                                'error': str(e)
                            })
                            
                            logger.error(f"❌ タスク {task_id} で予期しないエラー")
                            
                            if HAS_ENHANCED_HANDLER:
                                EnhancedErrorHandler.log_error_with_context(
                                    e,
                                    f"タスク {task_id} 実行中"
                                )
                            
                            if not auto_continue:
                                cont = input(
                                    f"\n⚠️ エラーが発生しました。続行しますか? (y/n): "
                                ).lower()
                                if cont != 'y':
                                    logger.info("ユーザーによる中断")
                                    break
                
                except Exception as e:
                    # === パート9: 反復全体のエラー処理 ===
                    logger.error(f"❌ 反復 {iteration} 全体でエラー発生")
                    
                    if HAS_ENHANCED_HANDLER:
                        EnhancedErrorHandler.log_error_with_context(
                            e,
                            f"反復 {iteration}"
                        )
                    
                    if "critical" in str(e).lower():
                        logger.error("💥 致命的エラー検出 - 実行中断")
                        raise
                    
                    logger.warning("⚠️ 非致命的エラー - 次の反復へ")
                    continue
            
            # === パート10: 最終レポート出力 ===
            self._print_execution_report(
                tasks_executed,
                tasks_success,
                tasks_failed,
                failed_tasks_list
            )
            
        except KeyboardInterrupt:
            logger.warning("\n⏸️ ユーザーによる中断")
            raise
        
        except Exception as e:
            # === パート11: 全体例外処理 ===
            logger.error("❌ タスク実行全体で重大エラー")
            
            if HAS_ENHANCED_HANDLER:
                EnhancedErrorHandler.log_error_with_context(
                    e,
                    "タスク実行全体"
                )
            raise
    
    async def _safe_update_task_status(self, task: Dict, status: str, error_message: str = None) -> bool:
        """安全なタスクステータス更新（例外を確実にキャッチ）"""
        try:
            task_id = task.get('task_id', 'UNKNOWN')
            
            # タスク存在確認
            task_exists = await self.sheets_manager.verify_task_exists(task_id)
            if not task_exists:
                logger.warning(f"⚠️ タスク {task_id} は存在しないためステータス更新をスキップ")
                return False
                
            if error_message:
                logger.info(f"タスク {task_id} ステータス更新: {status} - エラー: {error_message}")
            else:
                logger.info(f"タスク {task_id} ステータス更新: {status}")
                
            # 非同期関数かどうかを動的に判定
            update_method = self.sheets_manager.update_task_status
                
            import inspect
            if inspect.iscoroutinefunction(update_method):
                # 非同期メソッドの場合
                result = await update_method(task_id, status)
            else:
                # 同期メソッドの場合
                result = update_method(task_id, status)
                
            # 結果の型チェックと変換
            if result is None:
                logger.warning(f"⚠️ タスク {task_id} ステータス更新の結果がNoneです")
                return True  # Noneは失敗ではないとみなす
                    
            if isinstance(result, bool):
                return result
            else:
                logger.warning(f"⚠️ タスク {task_id} ステータス更新の戻り値がboolではありません: {type(result)}")
                # 数値や文字列をboolに変換
                return bool(result)
                    
        except Exception as e:
            logger.error(f"❌ タスク {task_id} ステータス更新で例外発生: {e}")
            # 重要なのは処理を継続すること
            return False