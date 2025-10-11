"""
test_tasks.py - 既存タスクのテスト実行用スクリプト（エラー診断強化版）
"""

import logging
import asyncio
import argparse
import inspect
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# 基本インポート
from config_utils import config, ErrorHandler, PathManager
from sheets_manager import GoogleSheetsManager
from browser_controller import BrowserController

# ロガー設定
logger = logging.getLogger(__name__)


class ClassInspector:
    """クラス診断ツール - 引数不一致エラーの根本原因を特定"""
    
    @staticmethod
    def diagnose_class_initialization(class_obj, provided_args: Dict, class_name: str) -> Dict:
        """
        クラス初期化の診断レポートを生成
        
        Args:
            class_obj: 診断対象のクラス
            provided_args: 渡そうとしている引数
            class_name: クラス名（ログ用）
        
        Returns:
            診断レポート
        """
        try:
            # クラスの__init__メソッドのシグネチャを取得
            init_signature = inspect.signature(class_obj.__init__)
            expected_params = list(init_signature.parameters.keys())
            
            # 提供されている引数
            provided_params = list(provided_args.keys())
            
            # 診断レポート
            report = {
                'class_name': class_name,
                'expected_parameters': expected_params,
                'provided_parameters': provided_params,
                'missing_parameters': [],
                'extra_parameters': [],
                'parameter_match': False,
                'diagnosis': '',
                'recommendation': ''
            }
            
            # 期待されるパラメータをチェック
            for expected in expected_params[1:]:  # selfを除外
                if expected not in provided_params:
                    report['missing_parameters'].append(expected)
            
            # 余分なパラメータをチェック
            for provided in provided_params:
                if provided not in expected_params[1:]:  # selfを除外
                    report['extra_parameters'].append(provided)
            
            # 診断結果
            report['parameter_match'] = (len(report['missing_parameters']) == 0 and 
                                       len(report['extra_parameters']) == 0)
            
            # 診断メッセージを構築
            if report['parameter_match']:
                report['diagnosis'] = "✅ パラメータ完全一致"
            else:
                diagnosis_parts = []
                if report['missing_parameters']:
                    diagnosis_parts.append(f"不足パラメータ: {report['missing_parameters']}")
                if report['extra_parameters']:
                    diagnosis_parts.append(f"余分パラメータ: {report['extra_parameters']}")
                report['diagnosis'] = "❌ " + ", ".join(diagnosis_parts)
            
            # 推奨事項
            if not report['parameter_match']:
                report['recommendation'] = (
                    f"修正が必要: {class_name}.__init__() を確認し、"
                    f"期待されるパラメータ: {expected_params[1:]} に合わせて修正してください"
                )
            
            return report
            
        except Exception as e:
            return {
                'class_name': class_name,
                'error': f"診断エラー: {str(e)}",
                'diagnosis': '❌ 診断失敗',
                'recommendation': 'クラス定義を確認してください'
            }


class ArgumentResolver:
    """引数解決クラス - 各エージェントの引数要件に合わせて動的に解決"""
    
    def __init__(self, browser_controller, sheets_manager):
        self.browser = browser_controller
        self.sheets_manager = sheets_manager
        self.argument_profiles = self._build_argument_profiles()
    
    def _build_argument_profiles(self) -> Dict:
        """各エージェントの引数プロファイルを構築"""
        return {
            'DesignAgent': {
                'browser': self.browser,
                'browser_controller': self.browser,
                'output_folder': None
            },
            'DevAgent': {
                'browser': self.browser,
                'browser_controller': self.browser,
                'output_folder': None
            },
            'ContentWriterAgent': {
                'browser': self.browser,
                'browser_controller': self.browser,
                'output_folder': None
            },
            'ReviewAgent': {
                # レビューエージェントは引数なし
            },
            'WordPressAgent': {
                'browser_controller': self.browser,
                'wp_credentials': {}
            },
            'WordPressDevAgent': {
                'browser_controller': self.browser
            },
            'WordPressDesignAgent': {
                'browser_controller': self.browser
            }
        }
    
    def resolve_arguments(self, class_obj, class_name: str) -> Dict:
        """
        クラスの引数要件に基づいて適切な引数を解決
        
        Returns:
            解決された引数の辞書
        """
        try:
            # クラスのシグネチャを取得
            init_signature = inspect.signature(class_obj.__init__)
            expected_params = list(init_signature.parameters.keys())[1:]  # selfを除外
            
            # 引数プロファイルから解決
            resolved_args = {}
            profile = self.argument_profiles.get(class_name, {})
            
            for param in expected_params:
                if param in profile:
                    resolved_args[param] = profile[param]
                else:
                    # デフォルト値の取得を試みる
                    param_obj = init_signature.parameters[param]
                    if param_obj.default != inspect.Parameter.empty:
                        resolved_args[param] = param_obj.default
                    else:
                        logger.warning(f"⚠️ パラメータ '{param}' の解決方法が不明です")
            
            return resolved_args
            
        except Exception as e:
            logger.error(f"❌ 引数解決エラー ({class_name}): {e}")
            return {}


class TaskExecutorResolver:
    """TaskExecutorの動的解決クラス"""
    
    @staticmethod
    def resolve_executor():
        """利用可能なTaskExecutorを解決"""
        executor_candidates = [
            ('task_executor.task_executor_ma', 'MATaskExecutor', 'M&A'),
            ('task_executor.content_task_executor', 'ContentTaskExecutor', 'コンテンツ'),
            ('task_executor.task_coordinator', 'TaskCoordinator', 'コーディネーター'),
        ]
        
        for module_path, class_name, executor_type in executor_candidates:
            try:
                module = __import__(module_path, fromlist=[class_name])
                executor_class = getattr(module, class_name)
                logger.info(f"🏁 main ✅ INFO {executor_type} Executor をインポート: {class_name}")
                return executor_class
            except (ImportError, AttributeError) as e:
                logger.debug(f"🏁 main 🐛 DEBUG ⚠️ {module_path}.{class_name} インポート失敗: {e}")
        
        logger.error("🏁 main ❌ ERROR 利用可能なTaskExecutorクラスが見つかりません")
        return None


class AgentInitializer:
    """エージェント初期化専用クラス（診断機能強化版）"""
    
    def __init__(self, browser_controller: BrowserController, sheets_manager: GoogleSheetsManager):
        self.browser = browser_controller
        self.sheets_manager = sheets_manager
        self.agents = {}
        self.argument_resolver = ArgumentResolver(browser_controller, sheets_manager)
        self.diagnostic_reports = {}
    
    async def initialize_all_agents(self, settings: Dict) -> Dict[str, any]:
        """
        全エージェントを初期化（診断機能付き）
        """
        logger.info("=" * 60)
        logger.info("🤖 エージェント初期化開始（診断モード）")
        logger.info("=" * 60)
        
        # 診断レポート用
        initialization_summary = {
            'total_agents': 0,
            'successful': 0,
            'failed': 0,
            'diagnostic_details': []
        }
        
        # 各エージェントを順次初期化
        agents_to_initialize = [
            ('design', self._init_design_agent),
            ('dev', self._init_dev_agent),
            ('review', self._init_review_agent),
            ('content_writer', self._init_content_writer_agent),
            ('wordpress', lambda: self._init_wordpress_agent(settings)),
            ('wp_dev', self._init_wp_dev_agent),
            ('wp_design', self._init_wp_design_agent),
        ]
        
        for agent_name, init_func in agents_to_initialize:
            initialization_summary['total_agents'] += 1
            success = await init_func()
            if success:
                initialization_summary['successful'] += 1
            else:
                initialization_summary['failed'] += 1
        
        # 診断サマリーを表示
        self._display_diagnostic_summary(initialization_summary)
        
        logger.info("=" * 60)
        logger.info(f"✅ エージェント初期化完了: {len(self.agents)}個")
        logger.info("=" * 60)
        
        return self.agents
    
    def _display_diagnostic_summary(self, summary: Dict):
        """診断サマリーを表示"""
        logger.info("\n" + "=" * 60)
        logger.info("🔍 エージェント初期化診断サマリー")
        logger.info("=" * 60)
        logger.info(f"総エージェント数: {summary['total_agents']}")
        logger.info(f"✅ 成功: {summary['successful']}")
        logger.info(f"❌ 失敗: {summary['failed']}")
        logger.info(f"📊 成功率: {summary['successful']/summary['total_agents']*100:.1f}%")
        
        # 診断詳細を表示
        if hasattr(self, 'diagnostic_reports') and self.diagnostic_reports:
            logger.info("\n📋 詳細診断レポート:")
            for agent_name, report in self.diagnostic_reports.items():
                status = "✅" if report.get('success', False) else "❌"
                logger.info(f"  {status} {agent_name}: {report.get('diagnosis', 'N/A')}")
        
        logger.info("=" * 60)
    
    async def _init_design_agent(self) -> bool:
        """設計エージェント初期化（診断付き）"""
        return await self._initialize_agent_with_diagnosis(
            'design', 'DesignAgent', 'design_agent'
        )
    
    async def _init_dev_agent(self) -> bool:
        """開発エージェント初期化（診断付き）"""
        return await self._initialize_agent_with_diagnosis(
            'dev', 'DevAgent', 'dev_agent'
        )
    
    async def _init_review_agent(self) -> bool:
        """レビューエージェント初期化（診断付き）"""
        return await self._initialize_agent_with_diagnosis(
            'review', 'ReviewAgent', 'review_agent'
        )
    
    async def _init_content_writer_agent(self) -> bool:
        """コンテンツライターエージェント初期化（診断付き）"""
        return await self._initialize_agent_with_diagnosis(
            'content_writer', 'ContentWriterAgent', 'content_writer_agent'
        )
    
    async def _init_wordpress_agent(self, settings: Dict) -> bool:
        """WordPressエージェント初期化（診断付き）"""
        try:
            from wordpress.wp_agent import WordPressAgent
            
            # WordPress認証情報を構築
            wp_credentials = {
                'wp_url': settings.get('wp_url', '').strip(),
                'wp_user': settings.get('wp_user', '').strip(),
                'wp_pass': settings.get('wp_pass', '').strip()
            }
            
            # 引数を解決
            resolved_args = self.argument_resolver.resolve_arguments(WordPressAgent, 'WordPressAgent')
            resolved_args['wp_credentials'] = wp_credentials
            
            # 診断レポート
            diagnostic_report = ClassInspector.diagnose_class_initialization(
                WordPressAgent, resolved_args, 'WordPressAgent'
            )
            
            logger.info(f"🔍 WordPressAgent 診断: {diagnostic_report['diagnosis']}")
            
            if not diagnostic_report['parameter_match']:
                logger.warning(f"⚠️ パラメータ不一致: {diagnostic_report['recommendation']}")
            
            # エージェント初期化
            agent = WordPressAgent(**resolved_args)
            agent.sheets_manager = self.sheets_manager
            
            # WordPressセッション初期化
            if all([wp_credentials['wp_url'], wp_credentials['wp_user'], wp_credentials['wp_pass']]):
                try:
                    await agent.initialize_wp_session()
                    logger.info("🌐 wp-agent ✅ INFO WordPressセッション初期化完了")
                except Exception as session_error:
                    logger.warning(f"🌐 wp-agent ⚠️ WARN セッション初期化失敗: {session_error}")
            
            self.agents['wordpress'] = agent
            
            # 診断レポートを保存
            self.diagnostic_reports['wordpress'] = {
                'success': True,
                'diagnosis': diagnostic_report['diagnosis'],
                'details': diagnostic_report
            }
            
            logger.info("🌐 wp-agent ✅ INFO WordPressAgent初期化完了")
            return True
            
        except Exception as e:
            logger.error(f"🌐 wp-agent ❌ ERROR 初期化エラー: {e}")
            self.diagnostic_reports['wordpress'] = {
                'success': False,
                'error': str(e),
                'diagnosis': '❌ 初期化失敗'
            }
            return False
    
    async def _init_wp_dev_agent(self) -> bool:
        """WordPress開発エージェント初期化（診断付き）"""
        return await self._initialize_agent_with_diagnosis(
            'wp_dev', 'WordPressDevAgent', 'wordpress.wp_dev'
        )
    
    async def _init_wp_design_agent(self) -> bool:
        """WordPress設計エージェント初期化（診断付き）"""
        return await self._initialize_agent_with_diagnosis(
            'wp_design', 'WordPressDesignAgent', 'wordpress.wp_design'
        )
    
    async def _initialize_agent_with_diagnosis(self, agent_key: str, class_name: str, module_path: str) -> bool:
        """
        エージェント初期化の統一メソッド（診断機能付き）
        """
        try:
            # モジュールの動的インポート
            module = __import__(module_path, fromlist=[class_name])
            agent_class = getattr(module, class_name)
            
            # 引数の解決
            resolved_args = self.argument_resolver.resolve_arguments(agent_class, class_name)
            
            # 診断レポートの生成
            diagnostic_report = ClassInspector.diagnose_class_initialization(
                agent_class, resolved_args, class_name
            )
            
            logger.info(f"🔍 {class_name} 診断: {diagnostic_report['diagnosis']}")
            
            # パラメータ不一致の警告
            if not diagnostic_report['parameter_match']:
                logger.warning(f"⚠️ {class_name} パラメータ不一致:")
                logger.warning(f"   期待: {diagnostic_report['expected_parameters']}")
                logger.warning(f"   提供: {diagnostic_report['provided_parameters']}")
                logger.warning(f"   推奨: {diagnostic_report['recommendation']}")
            
            # エージェントの初期化
            agent = agent_class(**resolved_args)
            
            # sheets_managerの設定（可能な場合）
            if hasattr(agent, 'sheets_manager'):
                agent.sheets_manager = self.sheets_manager
            
            self.agents[agent_key] = agent
            
            # 診断レポートを保存
            self.diagnostic_reports[agent_key] = {
                'success': True,
                'diagnosis': diagnostic_report['diagnosis'],
                'details': diagnostic_report
            }
            
            logger.info(f"✅ {agent_key} ✅ INFO {class_name}初期化完了")
            return True
            
        except ImportError as e:
            logger.warning(f"⚠️ {agent_key} ⚠️ WARN インポート失敗: {e}")
            self.diagnostic_reports[agent_key] = {
                'success': False,
                'error': f"インポート失敗: {str(e)}",
                'diagnosis': '❌ モジュール未見つかり'
            }
            return False
        except Exception as e:
            logger.error(f"❌ {agent_key} ❌ ERROR 初期化エラー: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            self.diagnostic_reports[agent_key] = {
                'success': False,
                'error': str(e),
                'diagnosis': '❌ 初期化失敗',
                'traceback': traceback.format_exc()
            }
            return False


class TaskTester:
    """既存タスクのテスト実行用クラス（診断機能強化版）"""
    
    def __init__(self, spreadsheet_id: str, service_account_file: str = None):
        self.spreadsheet_id = spreadsheet_id
        self.service_account_file = service_account_file
        self.sheets_manager = None
        self.browser = None
        self.task_executor = None
        self.agent_initializer = None
    
    async def initialize(self):
        """システム初期化（診断モード）"""
        try:
            logger.info("=" * 60)
            logger.info("🚀 タスクテスター初期化中（診断モード）...")
            logger.info("=" * 60)
            
            # 1. Google Sheets接続
            await self._initialize_sheets()
            
            # 2. 設定読み込み
            settings = await self._load_settings()
            
            # 3. ブラウザ初期化
            await self._initialize_browser(settings)
            
            # 4. エージェント初期化（診断機能付き）
            await self._initialize_agents(settings)
            
            # 5. TaskExecutor初期化
            await self._initialize_task_executor()
            
            # 6. エージェント登録
            await self._register_agents_to_executor()
            
            logger.info("=" * 60)
            logger.info("✅ システム初期化完了")
            logger.info("=" * 60)
            return True
        
        except Exception as e:
            ErrorHandler.log_error(e, "🏁 main システム初期化")
            return False
    
    async def _initialize_sheets(self):
        """Google Sheets初期化"""
        logger.info("📊 Google Sheets接続中...")
        self.sheets_manager = GoogleSheetsManager(
            self.spreadsheet_id,
            self.service_account_file
        )
    
    async def _load_settings(self):
        """設定読み込み"""
        pc_id = self.sheets_manager.get_current_pc_id()
        settings = self.sheets_manager.load_pc_settings(pc_id)
        
        logger.info(f"⚙️ config ✅ INFO PC設定読み込み完了: {pc_id}")
        return settings
    
    async def _initialize_browser(self, settings: Dict):
        """ブラウザ初期化"""
        logger.info("🌐 browser ✅ INFO ブラウザ初期化中...")
        
        # 出力フォルダ設定
        download_folder = self._setup_download_folder(settings)
        
        # ブラウザ設定
        config.BROWSER_DATA_DIR = settings.get('browser_data_dir')
        config.COOKIES_FILE = settings.get('cookies_file')
        config.GENERATION_MODE = 'text'
        config.SERVICE_TYPE = 'google'
        
        # ブラウザ起動
        self.browser = BrowserController(
            download_folder,
            mode='text',
            service='google'
        )
        await self.browser.setup_browser()
        await self.browser.navigate_to_gemini()
        
        logger.info("🌐 browser ✅ INFO ブラウザ初期化完了")
    
    def _setup_download_folder(self, settings: Dict) -> Path:
        """ダウンロードフォルダ設定"""
        agent_output = settings.get('agent_output_folder')
        
        if not agent_output or agent_output.startswith('http'):
            download_folder = Path.home() / "Documents" / "gemini_auto_generate" / "agent_outputs"
            download_folder.mkdir(exist_ok=True, parents=True)
            return download_folder
        else:
            return PathManager.get_safe_path(agent_output)
    
    async def _initialize_agents(self, settings: Dict):
        """エージェント初期化（診断機能付き）"""
        logger.info("🤖 エージェント初期化開始（診断モード）...")
        
        # AgentInitializerを使用して診断付きで初期化
        self.agent_initializer = AgentInitializer(self.browser, self.sheets_manager)
        agents = await self.agent_initializer.initialize_all_agents(settings)
        
        logger.info(f"✅ エージェント初期化完了: {len(agents)}個")
    
    async def _initialize_task_executor(self):
        """TaskExecutor初期化"""
        logger.info("⚙️ config ✅ INFO タスク実行エンジン初期化中...")
        
        executor_class = TaskExecutorResolver.resolve_executor()
        if not executor_class:
            raise ImportError("利用可能なTaskExecutorが見つかりません")
        
        logger.info(f"🏁 main ✅ INFO 使用するExecutor: {executor_class.__name__}")
        
        # Executorの種別判定
        is_ma_executor = 'MATaskExecutor' in executor_class.__name__
        
        # 基本パラメータ
        init_params = {
            'sheets_manager': self.sheets_manager,
            'browser': self.browser,
            'max_iterations': 30
        }
        
        # MATaskExecutor用の追加パラメータ
        if is_ma_executor:
            wp_agent = self.agent_initializer.agents.get('wordpress')
            init_params.update({
                'wp_agent': wp_agent,
                'plugin_agent': None
            })
        
        self.task_executor = executor_class(**init_params)
        logger.info(f"⚙️ config ✅ INFO {executor_class.__name__} 初期化完了")
    
    async def _register_agents_to_executor(self):
        """エージェント登録"""
        if not self.task_executor or not self.agent_initializer:
            return
        
        registration_map = {
            'design': ['design'],
            'dev': ['dev'],
            'review': ['review'],
            'content_writer': ['writer', 'content'],
            'wordpress': ['wordpress'],
            'wp_dev': ['wp_dev'],
            'wp_design': ['wp_design'],
        }
        
        for agent_name, executor_keys in registration_map.items():
            agent_instance = self.agent_initializer.agents.get(agent_name)
            if not agent_instance:
                continue
            
            for key in executor_keys:
                try:
                    self.task_executor.register_agent(key, agent_instance)
                    logger.info(f"✅ {key} エージェント登録完了")
                except Exception as e:
                    logger.error(f"❌ {key} エージェント登録失敗: {e}")
        
        # レビューエージェントの特別登録
        review_agent = self.agent_initializer.agents.get('review')
        if review_agent and hasattr(self.task_executor, 'register_review_agent'):
            self.task_executor.register_review_agent(review_agent)
            logger.info("✅ レビューエージェントを特別登録")

    # 既存のテストメソッドは変更なし
    async def test_tasks_by_role(self, role: str, auto: bool = False):
        """特定の役割のタスクをテスト実行"""
        # 実装は変更なし...

    async def test_all_pending_tasks(self, auto: bool = False):
        """全てのpendingタスクをテスト実行"""
        # 実装は変更なし...

    async def cleanup(self):
        """クリーンアップ"""
        if self.browser:
            await self.browser.cleanup()


async def main():
    """メイン関数"""
    # 実装は変更なし...
    pass


if __name__ == "__main__":
    asyncio.run(main())