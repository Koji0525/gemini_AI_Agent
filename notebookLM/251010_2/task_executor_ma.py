"""
task_executor_ma.py
M&A/企業検索専用のタスク実行モジュール（完全版）
task_executor.pyから分離
"""
import logging
from typing import Dict, Optional
from config_utils import ErrorHandler

logger = logging.getLogger(__name__)


class MATaskExecutor:
    """M&A/企業検索タスク専用の実行クラス"""
    
    def __init__(self, agents: Dict):
        self.agents = agents
        logger.info("MATaskExecutor initialized")
    
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
    
    async def _execute_ma_case_post(self, task: Dict) -> Dict:
        """M&A案件投稿タスクを実行"""
        logger.info("【M&A案件投稿】")
        
        wp_agent = self.agents.get('wordpress')
        if not wp_agent:
            return {
                'success': False,
                'error': 'WordPressエージェントが登録されていません'
            }
        
        parameters = task.get('parameters', {})
        
        # タスクパラメータを構築
        task_params = {
            'post_type': 'ma_case',
            'post_title': parameters.get('post_title', '新規M&A案件'),
            'post_content': parameters.get('post_content', ''),
            'acf_fields': parameters.get('acf_fields', {}),
            'polylang_lang': parameters.get('polylang_lang', 'ja'),
            'post_status': parameters.get('post_status', 'draft')
        }
        
        # WordPressエージェントで実行
        if hasattr(wp_agent, 'create_ma_case_post'):
            result = await wp_agent.create_ma_case_post(task_params)
        else:
            logger.warning("create_ma_case_post メソッドが見つかりません")
            # フォールバック: 通常の投稿作成
            result = await wp_agent.process_task(task)
        
        return result
    
    async def _execute_search_setup(self, task: Dict) -> Dict:
        """検索機能設定タスクを実行"""
        logger.info("【検索機能設定】")
        
        plugin_agent = self.agents.get('plugin')
        if not plugin_agent:
            return {
                'success': False,
                'error': 'プラグインエージェントが登録されていません'
            }
        
        parameters = task.get('parameters', {})
        
        # FacetWP設定タスクとして実行
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
                    'source': 'cf/desired_price',
                    'min': 0,
                    'max': 1000000000,
                    'step': 10000000
                },
                {
                    'name': '地域フィルター',
                    'type': 'dropdown',
                    'source': 'tax/region'
                }
            ])
        }
        
        # プラグインエージェントで実行
        if hasattr(plugin_agent, 'configure_facetwp'):
            result = await plugin_agent.configure_facetwp(task_params)
        else:
            logger.warning("configure_facetwp メソッドが見つかりません")
            result = await plugin_agent.change_plugin_settings(None, task)
        
        return result
    
    async def _execute_user_role_setup(self, task: Dict) -> Dict:
        """ユーザーロール設定タスクを実行"""
        logger.info("【ユーザーロール設定】")
        
        plugin_agent = self.agents.get('plugin')
        if not plugin_agent:
            return {
                'success': False,
                'error': 'プラグインエージェントが登録されていません'
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