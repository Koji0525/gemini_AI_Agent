# task_executor_ma.py
# M&A/企業検索専用のタスク実行モジュール（完全版）

import asyncio
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime
from configuration.config_utils import ErrorHandler

logger = logging.getLogger(__name__)


class MATaskExecutor:
    """M&A/企業検索タスク専用の実行クラス（依存関係注入対応版）"""

    def __init__(self, sheets_manager, browser, max_iterations: int = 30, 
                 wp_agent=None, plugin_agent=None):
        """
        MATaskExecutorの初期化（緩和版 - 必須チェックを削除）
    
        Args:
            sheets_manager: Google Sheetsマネージャー
            browser: ブラウザコントローラー
            max_iterations: 最大イテレーション数
            wp_agent: WordPressエージェント（後で設定可能）
            plugin_agent: プラグインエージェント（後で設定可能）
        """
        # === パート1: 基本プロパティの設定 ===
        self.sheets_manager = sheets_manager
        self.browser = browser
        self.max_iterations = max_iterations
        self.agents = {}  # エージェント辞書を空で初期化
        self.review_agent = None
    
        # === パート2: エージェントの設定（必須チェックを削除）===
        self.wp_agent = wp_agent
        self.plugin_agent = plugin_agent
    
        # === パート3: 遅延初期化フラグ ===
        self._initialized = False
    
        logger.info(f"✅ MATaskExecutor 基本初期化完了 (max_iterations={max_iterations})")
        logger.info(f"   - wp_agent: {'✅ 設定済み' if wp_agent else '⚠️ 未設定（後で設定可能）'}")
        logger.info(f"   - plugin_agent: {'✅ 設定済み' if plugin_agent else '⚠️ 未設定（後で設定可能）'}")

    def set_wordpress_agent(self, wp_agent):
        """WordPressエージェントを後から設定"""
        if not wp_agent:
            logger.error("❌ 設定するWordPressエージェントがNoneです")
            return False
    
        self.wp_agent = wp_agent
        self.agents['wordpress'] = wp_agent
        logger.info("✅ WordPressエージェントを後から設定しました")
    
        # プラグインマネージャーも自動登録
        if hasattr(wp_agent, 'plugin_manager') and wp_agent.plugin_manager:
            self.plugin_agent = wp_agent.plugin_manager
            self.agents['plugin'] = wp_agent.plugin_manager
            logger.info("✅ プラグインマネージャーを自動登録しました")
    
        self._initialized = True
        return True

    def set_plugin_agent(self, plugin_agent):
        """プラグインエージェントを後から設定"""
        if not plugin_agent:
            logger.error("❌ 設定するプラグインエージェントがNoneです")
            return False
    
        self.plugin_agent = plugin_agent
        self.agents['plugin'] = plugin_agent
        logger.info("✅ プラグインエージェントを後から設定しました")
        return True

    def ensure_agents_ready(self):
        """エージェントが準備できているか確認"""
        if not self.wp_agent:
            logger.error("❌ WordPressエージェントがまだ設定されていません")
            return False
        return True
    
    def _register_core_agents(self):
        """コアエージェントを自動登録"""
        # WordPressエージェント登録
        self.agents['wordpress'] = self.wp_agent
        logger.info("✅ WordPressエージェントを登録しました")
        
        # プラグインエージェント登録（存在する場合）
        if self.plugin_agent:
            self.agents['plugin'] = self.plugin_agent
            logger.info("✅ プラグインエージェントを登録しました")
        elif hasattr(self.wp_agent, 'plugin_manager') and self.wp_agent.plugin_manager:
            self.agents['plugin'] = self.wp_agent.plugin_manager
            logger.info("✅ WordPressエージェントからプラグインマネージャーを登録しました")
        else:
            logger.warning("⚠️ プラグインエージェントが見つかりませんでした")
            
    # === 追加メソッド: エージェント登録機能 ===
    def register_agent(self, agent_name: str, agent):
        """エージェントを登録"""
        self.agents[agent_name] = agent
        logger.info(f"✅ エージェント '{agent_name}' を登録しました")
    
    def register_review_agent(self, review_agent):
        """レビューエージェントを登録"""
        self.review_agent = review_agent
        self.agents['review'] = review_agent
        logger.info("✅ レビューエージェントを登録しました")
    
    # ========================================
    # ✅ ここに追加: タスク読み込みメソッド（互換性のため）
    # ========================================
    async def load_pending_tasks(self):
        """
        保留中のタスクを読み込む
        
        Returns:
            List[Dict]: pendingステータスのタスクリスト
        """
        try:
            logger.info("📋 保留中のタスクを読み込み中...")
            tasks = await self.sheets_manager.load_tasks_from_sheet('pm_tasks')
            
            if not tasks:
                logger.info("🔭 pm_tasksシートにタスクがありません")
                return []
            
            # statusが'pending'のタスクのみをフィルタ
            pending_tasks = [
                task for task in tasks 
                if task.get('status', '').lower() == 'pending'
            ]
            
            logger.info(f"📊 保留中のタスク: {len(pending_tasks)}件")
            return pending_tasks
            
        except Exception as e:
            logger.error(f"❌ タスク読み込みエラー: {e}")
            return []
    
    # ========================================
    # ✅ ここに追加: タスク実行メソッド（互換性のため）
    # ========================================
    async def execute_task(self, task: Dict) -> bool:
        """
        タスクを実行（基本的な実装）
        
        Args:
            task: タスク情報辞書
            
        Returns:
            bool: 実行成功フラグ
        """
        task_id = task.get('task_id', 'UNKNOWN')
        
        try:
            logger.info(f"🎯 タスク実行開始: {task_id}")
            
            # M&Aタスクとして実行
            result = await self.execute_ma_task(task)
            
            if result and result.get('success'):
                logger.info(f"✅ タスク完了: {task_id}")
                return True
            else:
                error = result.get('error', '不明') if result else '結果なし'
                logger.error(f"❌ タスク失敗: {error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ タスク実行エラー: {e}")
            return False
    
    # ========================================
    # ✅ ここに追加: 全タスク実行メソッド（互換性のため）
    # ========================================
    async def run_all_tasks(self, auto_continue: bool = True, enable_review: bool = True) -> Dict[str, Any]:
        """
        全タスクを一括実行
        
        Args:
            auto_continue: 自動継続フラグ
            enable_review: レビュー有効化フラグ
            
        Returns:
            Dict: 実行結果サマリー
        """
        from datetime import datetime
        
        logger.info("\n" + "="*80)
        logger.info("🚀 全タスク実行を開始します")
        logger.info("="*80 + "\n")
        
        summary = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'results': [],
            'start_time': datetime.now(),
            'end_time': None
        }
        
        try:
            # 保留中のタスクを読み込み
            pending_tasks = await self.load_pending_tasks()
            
            if not pending_tasks:
                logger.info("🔭 実行すべきタスクがありません")
                summary['end_time'] = datetime.now()
                return summary
            
            summary['total'] = len(pending_tasks)
            logger.info(f"📊 実行対象タスク: {summary['total']}件\n")
            
            # タスクを順番に実行
            for index, task in enumerate(pending_tasks, 1):
                task_id = task.get('task_id', 'UNKNOWN')
                
                logger.info(f"\n{'─'*80}")
                logger.info(f"📌 タスク {index}/{summary['total']}: {task_id}")
                logger.info(f"{'─'*80}")
                
                try:
                    success = await self.execute_task(task)
                    
                    task_result = {
                        'task_id': task_id,
                        'success': success,
                        'index': index,
                        'timestamp': datetime.now()
                    }
                    summary['results'].append(task_result)
                    
                    if success:
                        summary['success'] += 1
                        logger.info(f"✅ タスク {task_id} 成功 ({index}/{summary['total']})")
                    else:
                        summary['failed'] += 1
                        logger.warning(f"⚠️ タスク {task_id} 失敗 ({index}/{summary['total']})")
                    
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    summary['failed'] += 1
                    logger.error(f"❌ タスク {task_id} エラー: {e}")
            
            summary['end_time'] = datetime.now()
            elapsed_time = (summary['end_time'] - summary['start_time']).total_seconds()
            
            logger.info("\n" + "="*80)
            logger.info("📊 全タスク実行完了")
            logger.info("="*80)
            logger.info(f"  総タスク数:   {summary['total']:>3}件")
            logger.info(f"  ✅ 成功:      {summary['success']:>3}件")
            logger.info(f"  ❌ 失敗:      {summary['failed']:>3}件")
            logger.info(f"  ⏱️  実行時間:  {elapsed_time:.2f}秒")
            logger.info("="*80 + "\n")
            
            if summary['total'] > 0:
                success_rate = (summary['success'] / summary['total']) * 100
                logger.info(f"📈 成功率: {success_rate:.1f}%")
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ 全タスク実行エラー: {e}")
            summary['end_time'] = datetime.now()
            return summary

    async def execute_ma_task(self, task: Dict) -> Dict:
        """
        M&A関連タスクを実行
    
        タスクの内容を解析して、適切なメソッドに振り分ける
        """
        try:
            # === パート1: 実行開始ヘッダー ===
            logger.info("="*60)
            logger.info("📊 M&A案件処理タスク実行")
            logger.info("="*60)
        
            # === パート2: タスク内容の解析 ===
            description = task.get('description', '').lower()
            parameters = task.get('parameters', {})
        
            # === パート3: パラメータベースの判定（最も確実）===
            if 'cpt_slug' in parameters or 'cpt_labels' in parameters:
                logger.info("→ Custom Post Type作成タスクと判定")
                return await self._execute_cpt_creation(task)
        
            elif 'acf_field_group_name' in parameters or 'acf_fields' in parameters:
                logger.info("→ ACF設定タスクと判定")
                return await self._execute_acf_setup(task)
        
            elif 'taxonomy_slug' in parameters or 'taxonomy_labels' in parameters:
                logger.info("→ タクソノミー作成タスクと判定")
                return await self._execute_taxonomy_creation(task)
        
            elif 'facets' in parameters or 'facetwp' in description:
                logger.info("→ 検索機能設定タスクと判定")
                return await self._execute_search_setup(task)
        
            elif 'role_slug' in parameters or 'role_name' in parameters:
                logger.info("→ ユーザーロール設定タスクと判定")
                return await self._execute_user_role_setup(task)
        
            # === パート4: キーワードベースの判定 ===
            elif 'custom post type' in description or 'カスタム投稿タイプ' in description:
                logger.info("→ Custom Post Type作成タスクと判定（キーワード）")
                return await self._execute_cpt_creation(task)
        
            elif 'acf' in description or 'カスタムフィールド' in description:
                logger.info("→ ACF設定タスクと判定（キーワード）")
                return await self._execute_acf_setup(task)
        
            elif 'taxonomy' in description or 'タクソノミー' in description:
                logger.info("→ タクソノミー作成タスクと判定（キーワード）")
                return await self._execute_taxonomy_creation(task)
        
            elif 'm&a案件' in description or 'ma_case' in description:
                logger.info("→ M&A案件投稿タスクと判定")
                return await self._execute_ma_case_post(task)
        
            elif '検索' in description or 'search' in description:
                logger.info("→ 検索機能設定タスクと判定")
                return await self._execute_search_setup(task)
        
            elif 'user role' in description or 'ユーザーロール' in description:
                logger.info("→ ユーザーロール設定タスクと判定")
                return await self._execute_user_role_setup(task)
        
            else:
                # === パート5: デフォルト処理 ===
                logger.info("→ 汎用WordPressタスクとして処理")
                wp_agent = self.agents.get('wordpress')
                if wp_agent:
                    return await wp_agent.process_task(task)
                else:
                    return {
                        'success': False,
                        'error': 'WordPressエージェントが登録されていません'
                    }
    
        except Exception as e:
            # === パート6: 例外処理 ===
            ErrorHandler.log_error(e, "M&Aタスク実行")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute_cpt_creation(self, task: Dict) -> Dict:
        """Custom Post Type作成タスクを実行"""
        logger.info("【Custom Post Type作成】")
        
        wp_agent = self.agents.get('wordpress')
        if not wp_agent:
            return {
                'success': False,
                'error': 'WordPressエージェントが登録されていません'
            }
        
        parameters = task.get('parameters', {})
        
        # タスクパラメータを構築
        task_params = {
            'cpt_slug': parameters.get('cpt_slug', 'ma_case'),
            'cpt_labels': parameters.get('cpt_labels', {
                'singular': 'M&A案件',
                'plural': 'M&A案件一覧'
            }),
            'cpt_supports': parameters.get('cpt_supports', ['title', 'editor', 'thumbnail', 'custom-fields']),
            'cpt_settings': parameters.get('cpt_settings', {
                'public': True,
                'has_archive': True,
                'show_in_rest': True,
                'menu_icon': 'dashicons-portfolio'
            })
        }
        
        # WordPressエージェントで実行
        if hasattr(wp_agent, 'configure_custom_post_type'):
            result = await wp_agent.configure_custom_post_type(task_params)
        else:
            logger.warning("configure_custom_post_type メソッドが見つかりません")
            result = await wp_agent.process_task(task)
        
        return result
    
    async def _execute_acf_setup(self, task: Dict) -> Dict:
        """ACFフィールド設定タスクを実行"""
        logger.info("【ACFフィールド設定】")
        
        wp_agent = self.agents.get('wordpress')
        if not wp_agent:
            return {
                'success': False,
                'error': 'WordPressエージェントが登録されていません'
            }
        
        parameters = task.get('parameters', {})
        
        # タスクパラメータを構築
        task_params = {
            'acf_field_group_name': parameters.get('acf_field_group_name', 'M&A案件基本情報'),
            'acf_fields': parameters.get('acf_fields', [
                {'name': 'case_id', 'type': 'text', 'label': '案件ID'},
                {'name': 'ma_scheme', 'type': 'select', 'label': 'M&Aスキーム'},
                {'name': 'desired_price', 'type': 'number', 'label': '希望価格'},
                {'name': 'industry_category', 'type': 'taxonomy', 'label': '業種'},
                {'name': 'region', 'type': 'taxonomy', 'label': '地域'},
                {'name': 'established_year', 'type': 'number', 'label': '設立年'},
                {'name': 'employees', 'type': 'number', 'label': '従業員数'},
            ]),
            'acf_location_rules': parameters.get('acf_location_rules', {
                'post_type': 'ma_case'
            })
        }
        
        # WordPressエージェントで実行
        if hasattr(wp_agent, 'configure_acf_fields'):
            result = await wp_agent.configure_acf_fields(task_params)
        else:
            logger.warning("configure_acf_fields メソッドが見つかりません")
            result = await wp_agent.process_task(task)
        
        return result
    
    async def _execute_taxonomy_creation(self, task: Dict) -> Dict:
        """カスタムタクソノミー作成タスクを実行"""
        logger.info("【カスタムタクソノミー作成】")
        
        wp_agent = self.agents.get('wordpress')
        if not wp_agent:
            return {
                'success': False,
                'error': 'WordPressエージェントが登録されていません'
            }
        
        parameters = task.get('parameters', {})
        
        # タスクパラメータを構築
        task_params = {
            'taxonomy_slug': parameters.get('taxonomy_slug', 'industry_category'),
            'taxonomy_labels': parameters.get('taxonomy_labels', {
                'singular': '業種',
                'plural': '業種一覧'
            }),
            'taxonomy_post_types': parameters.get('taxonomy_post_types', ['ma_case']),
            'taxonomy_hierarchical': parameters.get('taxonomy_hierarchical', True)
        }
        
        # WordPressエージェントで実行
        if hasattr(wp_agent, 'configure_custom_taxonomy'):
            result = await wp_agent.configure_custom_taxonomy(task_params)
        else:
            logger.warning("configure_custom_taxonomy メソッドが見つかりません")
            result = await wp_agent.process_task(task)
        
        return result
    
    # === 修正: M&A案件投稿メソッド ===
    async def _execute_ma_case_post(self, task: Dict) -> Dict:
        """M&A案件投稿タスクを実行（完全修正版）"""
        logger.info("【M&A案件投稿】")

        # === パート1: 複数の方法でWordPressエージェントを取得 ===
        wp_agent = None
        
        # 方法1: 直接属性から取得
        if hasattr(self, 'wp_agent') and self.wp_agent:
            wp_agent = self.wp_agent
            logger.info("✅ wp_agent 属性から取得")
        
        # 方法2: agents辞書から取得
        elif 'wordpress' in self.agents and self.agents['wordpress']:
            wp_agent = self.agents['wordpress']
            logger.info("✅ agents辞書から取得")
        
        # 方法3: フォールバック - 登録済みエージェントから検索
        else:
            logger.error("❌ WordPressエージェントが見つかりません。登録状況:")
            for agent_name, agent_instance in self.agents.items():
                logger.error(f"  - {agent_name}: {agent_instance}")
            
            return {
                'success': False,
                'error': 'WordPressエージェントが登録されていません。以下のエージェントのみ登録されています: ' + 
                        ', '.join(self.agents.keys())
            }

        if not wp_agent:
            logger.error("❌ WordPressエージェントの取得に失敗")
            return {
                'success': False,
                'error': 'WordPressエージェントの取得に失敗しました'
            }

        # === パート2: タスクパラメータの構築 ===
        parameters = task.get('parameters', {})
        
        task_params = {
            'post_type': 'ma_case',
            'post_title': parameters.get('post_title', '新規M&A案件'),
            'post_content': parameters.get('post_content', ''),
            'acf_fields': parameters.get('acf_fields', {}),
            'polylang_lang': parameters.get('polylang_lang', 'ja'),
            'post_status': parameters.get('post_status', 'draft')
        }
        
        # === パート3: WordPressエージェントで実行 ===
        try:
            logger.info(f"📝 WordPressエージェントでタスク実行: {task_params['post_title']}")
            
            if hasattr(wp_agent, 'create_ma_case_post'):
                result = await wp_agent.create_ma_case_post(task_params)
            else:
                logger.warning("⚠️ create_ma_case_post メソッドが見つからないため、process_task を使用")
                modified_task = task.copy()
                modified_task['parameters'] = task_params
                result = await wp_agent.process_task(modified_task)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ M&A案件投稿実行エラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute_search_setup(self, task: Dict) -> Dict:
        """検索機能設定タスクを実行（完全修正版）"""
        logger.info("【検索機能設定】")

        # === パート1: 複数の方法でプラグインエージェントを取得 ===
        plugin_agent = None
        
        # 方法1: 直接属性から取得
        if hasattr(self, 'plugin_agent') and self.plugin_agent:
            plugin_agent = self.plugin_agent
            logger.info("✅ plugin_agent 属性から取得")
        
        # 方法2: agents辞書から取得
        elif 'plugin' in self.agents and self.agents['plugin']:
            plugin_agent = self.agents['plugin']
            logger.info("✅ agents辞書から取得")
        
        # 方法3: WordPressエージェントから取得
        elif hasattr(self, 'wp_agent') and self.wp_agent and hasattr(self.wp_agent, 'plugin_manager'):
            plugin_agent = self.wp_agent.plugin_manager
            logger.info("✅ WordPressエージェントからplugin_managerを取得")
        
        # 方法4: フォールバック
        else:
            logger.error("❌ プラグインエージェントが見つかりません。代替方法を試行...")
            
            # WordPressエージェントで直接処理を試みる
            if hasattr(self, 'wp_agent') and self.wp_agent:
                logger.info("🔧 WordPressエージェントで直接処理")
                return await self.wp_agent.process_task(task)
            else:
                logger.error("❌ 代替方法も失敗")
                return {
                    'success': False,
                    'error': 'プラグインエージェントが見つかりません。WordPressエージェントも利用できません。'
                }

        if not plugin_agent:
            logger.error("❌ プラグインエージェントの取得に失敗")
            return {
                'success': False,
                'error': 'プラグインエージェントの取得に失敗しました'
            }

        # === パート2: タスク実行 ===
        parameters = task.get('parameters', {})
        
        task_params = {
            'plugin_name': 'facetwp',
            'action': 'configure',
            'facets': parameters.get('facets', [
                {
                    'name': '業種フィルター',
                    'type': 'checkboxes',
                    'source': 'tax/industry_category'
                },
                {
                    'name': '価格帯フィルター', 
                    'type': 'slider',
                    'source': 'cf/desired_price'
                }
            ])
        }
        
        try:
            logger.info("🔧 プラグインエージェントで設定実行")
            
            if hasattr(plugin_agent, 'configure_facetwp'):
                result = await plugin_agent.configure_facetwp(task_params)
            else:
                logger.warning("⚠️ configure_facetwp メソッドが見つからないため、change_plugin_settings を使用")
                result = await plugin_agent.change_plugin_settings(None, task)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 検索機能設定実行エラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute_user_role_setup(self, task: Dict) -> Dict:
        """ユーザーロール設定タスクを実行"""
        logger.info("【ユーザーロール設定】")
    
        # === パート1: プラグインエージェント取得（フォールバック付き） ===
        plugin_agent = self.agents.get('plugin')
    
        # プラグインエージェントがない場合、WordPressエージェントから取得を試みる
        if not plugin_agent:
            logger.warning("⚠️ plugin エージェントが直接登録されていません")
        
            wp_agent = self.agents.get('wordpress')
            if wp_agent and hasattr(wp_agent, 'plugin_manager'):
                plugin_agent = wp_agent.plugin_manager
                logger.info("✅ WordPressエージェントからplugin_managerを取得しました")
            else:
                logger.error("❌ プラグインエージェントが見つかりません")
                return {
                    'success': False,
                    'error': 'プラグインエージェントが登録されていません。WordPressエージェントを確認してください。'
                }
        
        parameters = task.get('parameters', {})
        
        # User Role Editor設定タスクとして実行
        task_params = {
            'plugin_name': 'user-role-editor',
            'action': 'configure',
            'role_slug': parameters.get('role_slug', 'ma_partner'),
            'role_name': parameters.get('role_name', '提携パートナー'),
            'capabilities': parameters.get('capabilities', {
                'read': True,
                'edit_posts': True,
                'delete_posts': True,
                'edit_published_posts': True,
                'publish_posts': False
            })
        }
        
        # プラグインエージェントで実行
        if hasattr(plugin_agent, 'configure_user_roles'):
            result = await plugin_agent.configure_user_roles(None, task_params)
        else:
            logger.warning("configure_user_roles メソッドが見つかりません")
            result = await plugin_agent.change_plugin_settings(None, task)
        
        return result
    
def validate_ma_task(self, task: Dict) -> tuple[bool, Optional[str]]:
    """
    M&Aタスクのパラメータを検証
        
    Returns:
        (valid: bool, error_message: Optional[str])
    """
    try:
        parameters = task.get('parameters', {})
            
        # === パート1: Custom Post Type作成の検証 ===
        if 'cpt_slug' in parameters:
            if not parameters['cpt_slug']:
                return False, "cpt_slugが空です"
            if not parameters['cpt_slug'].replace('_', '').isalnum():
                return False, "cpt_slugは英数字とアンダースコアのみ使用可能です"
            
        # === パート2: ACF設定の検証 ===
        if 'acf_field_group_name' in parameters:
            if not parameters['acf_field_group_name']:
                return False, "acf_field_group_nameが空です"
                
            acf_fields = parameters.get('acf_fields', [])
            if not isinstance(acf_fields, list):
                return False, "acf_fieldsはリスト形式である必要があります"
                
            for field in acf_fields:
                if 'name' not in field or 'type' not in field:
                    return False, "ACFフィールドにはnameとtypeが必要です"
            
        # === パート3: タクソノミー作成の検証 ===
        if 'taxonomy_slug' in parameters:
            if not parameters['taxonomy_slug']:
                return False, "taxonomy_slugが空です"
            if not parameters['taxonomy_slug'].replace('_', '').isalnum():
                return False, "taxonomy_slugは英数字とアンダースコアのみ使用可能です"
            
        # === パート4: 検証成功 ===
        return True, None
            
    except Exception as e:
        # === パート5: 検証中の例外処理 ===
        return False, f"検証エラー: {str(e)}"