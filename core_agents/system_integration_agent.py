# system_integration_agent.py
"""
システム統合エージェント
既存のMATaskExecutorとハイブリッド修正システムを統合
"""

import asyncio
import logging
import inspect
import traceback
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime

from data_models import ErrorContextModel, BugFixTask, create_bug_fix_task_from_exception

logger = logging.getLogger(__name__)


class SystemIntegrationAgent:
    """
    システム統合エージェント
    
    機能:
    - 既存システムへのエラーフック設置
    - エラー自動検出とルーティング
    - 修正後のタスク再実行
    - システム間の状態同期
    """
    
    def __init__(
        self,
        ma_task_executor=None,
        hybrid_fix_system=None,
        auto_fix_enabled: bool = True,
        auto_retry_enabled: bool = True,
        max_retry_attempts: int = 3
    ):
        """
        初期化
        
        Args:
            ma_task_executor: MATaskExecutor（既存システム）
            hybrid_fix_system: HybridFixSystem（新システム）
            auto_fix_enabled: 自動修正有効フラグ
            auto_retry_enabled: 自動リトライ有効フラグ
            max_retry_attempts: 最大リトライ回数
        """
        self.ma_executor = ma_task_executor
        self.hybrid_system = hybrid_fix_system
        self.auto_fix_enabled = auto_fix_enabled
        self.auto_retry_enabled = auto_retry_enabled
        self.max_retry_attempts = max_retry_attempts
        
        # エラーフックのレジストリ
        self.error_hooks = {}
        
        # 統計情報
        self.stats = {
            "total_errors_caught": 0,
            "auto_fixed_errors": 0,
            "retry_successes": 0,
            "integration_failures": 0
        }
        
        # エラー発生履歴
        self.error_history = []
        
        logger.info("✅ SystemIntegrationAgent 初期化完了")
    
    async def integrate_with_ma_executor(self):
        """MATaskExecutorと統合"""
        try:
            logger.info("🔗 MATaskExecutorとの統合開始")
            
            if not self.ma_executor:
                logger.warning("⚠️ MATaskExecutorが設定されていません")
                return False
            
            # 1. エラーハンドラーを注入
            self._inject_error_handlers()
            
            # 2. タスク実行メソッドをラップ
            self._wrap_task_execution_methods()
            
            # 3. コンポーネントのエラーハンドラーを設置
            self._setup_component_error_handlers()
            
            logger.info("✅ MATaskExecutorとの統合完了")
            return True
            
        except Exception as e:
            logger.error(f"❌ 統合エラー: {e}", exc_info=True)
            return False
    
    def _inject_error_handlers(self):
        """エラーハンドラーを注入"""
        try:
            # MATaskExecutorのメソッドをラップ
            if hasattr(self.ma_executor, 'execute_task'):
                original_execute = self.ma_executor.execute_task
                self.ma_executor.execute_task = self._wrap_with_error_handler(
                    original_execute,
                    "execute_task"
                )
                logger.info("✅ execute_taskメソッドをラップしました")
            
            # 他の重要なメソッドも同様にラップ
            methods_to_wrap = [
                'process_task',
                'run_single_task',
                '_execute_with_retry'
            ]
            
            for method_name in methods_to_wrap:
                if hasattr(self.ma_executor, method_name):
                    original_method = getattr(self.ma_executor, method_name)
                    wrapped_method = self._wrap_with_error_handler(
                        original_method,
                        method_name
                    )
                    setattr(self.ma_executor, method_name, wrapped_method)
                    logger.info(f"✅ {method_name}メソッドをラップしました")
            
        except Exception as e:
            logger.error(f"❌ エラーハンドラー注入失敗: {e}")
    
    def _wrap_with_error_handler(
        self,
        original_method: Callable,
        method_name: str
    ) -> Callable:
        """メソッドをエラーハンドラーでラップ"""
        
        @wraps(original_method)
        async def wrapper(*args, **kwargs):
            retry_count = 0
            last_error = None
            
            while retry_count <= self.max_retry_attempts:
                try:
                    # 元のメソッドを実行
                    if inspect.iscoroutinefunction(original_method):
                        result = await original_method(*args, **kwargs)
                    else:
                        result = original_method(*args, **kwargs)
                    
                    # 成功したらリトライカウントをリセット
                    if retry_count > 0:
                        self.stats["retry_successes"] += 1
                        logger.info(f"✅ リトライ成功: {method_name} (試行{retry_count + 1}回目)")
                    
                    return result
                
                except Exception as e:
                    last_error = e
                    self.stats["total_errors_caught"] += 1
                    
                    logger.error(
                        f"❌ エラー捕捉: {method_name} "
                        f"(試行{retry_count + 1}/{self.max_retry_attempts + 1})"
                    )
                    logger.error(f"   エラー: {type(e).__name__}: {str(e)}")
                    
                    # タスク情報を取得
                    task_id = self._extract_task_id(args, kwargs)
                    file_path = self._extract_file_path(e)
                    
                    # エラー履歴に記録
                    self.error_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "method": method_name,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "task_id": task_id,
                        "retry_count": retry_count
                    })
                    
                    # 自動修正を試行
                    if self.auto_fix_enabled and self.hybrid_system:
                        fix_result = await self._attempt_auto_fix(
                            error=e,
                            task_id=task_id,
                            method_name=method_name,
                            file_path=file_path
                        )
                        
                        if fix_result and fix_result.get("success"):
                            self.stats["auto_fixed_errors"] += 1
                            logger.info(f"✅ 自動修正成功: {task_id}")
                            
                            # 自動リトライが有効な場合、修正後に再実行
                            if self.auto_retry_enabled:
                                retry_count += 1
                                logger.info(f"🔄 タスク再実行: {task_id} (試行{retry_count + 1}回目)")
                                await asyncio.sleep(2)  # 少し待機
                                continue
                    
                    # リトライ判定
                    if retry_count < self.max_retry_attempts and self.auto_retry_enabled:
                        retry_count += 1
                        logger.warning(f"🔄 リトライ: {method_name} (試行{retry_count + 1}回目)")
                        await asyncio.sleep(5)  # リトライ前に待機
                    else:
                        # リトライ上限到達
                        logger.error(f"❌ リトライ上限到達: {method_name}")
                        raise
            
            # すべてのリトライが失敗
            if last_error:
                raise last_error
        
        return wrapper
    
    async def _attempt_auto_fix(
        self,
        error: Exception,
        task_id: str,
        method_name: str,
        file_path: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """自動修正を試行"""
        try:
            logger.info(f"🔧 自動修正を試行: {task_id}")
            
            if not self.hybrid_system:
                logger.warning("⚠️ HybridFixSystemが設定されていません")
                return None
            
            # ファイルパスの推定
            if not file_path:
                file_path = self._infer_file_path(method_name)
            
            # コンテキスト情報を収集
            context = {
                "method_name": method_name,
                "task_id": task_id,
                "auto_fix_attempt": True
            }
            
            # HybridFixSystemのhandle_errorを呼び出し
            fix_result = await self.hybrid_system.handle_error(
                error=error,
                task_id=task_id,
                file_path=file_path,
                context=context
            )
            
            return fix_result
            
        except Exception as e:
            logger.error(f"❌ 自動修正試行エラー: {e}")
            self.stats["integration_failures"] += 1
            return None
    
    def _wrap_task_execution_methods(self):
        """タスク実行メソッドをラップ"""
        try:
            # WordPressAgent, PluginAgent等のエージェントメソッドもラップ
            agents_to_wrap = [
                'wp_agent',
                'plugin_agent',
                'content_writer',
                'acf_agent',
                'cpt_agent'
            ]
            
            for agent_name in agents_to_wrap:
                if hasattr(self.ma_executor, agent_name):
                    agent = getattr(self.ma_executor, agent_name)
                    if agent:
                        self._wrap_agent_methods(agent, agent_name)
            
        except Exception as e:
            logger.error(f"❌ タスク実行メソッドラップエラー: {e}")
    
    def _wrap_agent_methods(self, agent, agent_name: str):
        """エージェントのメソッドをラップ"""
        try:
            # 主要なメソッドを特定
            method_names = [
                name for name in dir(agent)
                if not name.startswith('_') and callable(getattr(agent, name))
            ]
            
            for method_name in method_names[:5]:  # 最初の5つのみ（例）
                try:
                    original_method = getattr(agent, method_name)
                    wrapped_method = self._wrap_with_error_handler(
                        original_method,
                        f"{agent_name}.{method_name}"
                    )
                    setattr(agent, method_name, wrapped_method)
                except:
                    pass  # ラップできないメソッドはスキップ
            
            logger.info(f"✅ {agent_name}のメソッドをラップしました")
            
        except Exception as e:
            logger.warning(f"⚠️ {agent_name}のラップ失敗: {e}")
    
    def _setup_component_error_handlers(self):
        """コンポーネントのエラーハンドラーを設置"""
        try:
            # CommandMonitorAgentのエラーハンドラー
            if hasattr(self.ma_executor, 'cmd_monitor'):
                cmd_monitor = self.ma_executor.cmd_monitor
                if cmd_monitor and hasattr(cmd_monitor, 'execute_command'):
                    original_execute = cmd_monitor.execute_command
                    cmd_monitor.execute_command = self._wrap_with_error_handler(
                        original_execute,
                        "cmd_monitor.execute_command"
                    )
                    logger.info("✅ CommandMonitorAgentのエラーハンドラーを設置")
            
        except Exception as e:
            logger.warning(f"⚠️ コンポーネントエラーハンドラー設置失敗: {e}")
    
    # ========================================
    # ユーティリティ
    # ========================================
    
    def _extract_task_id(self, args: tuple, kwargs: dict) -> str:
        """引数からタスクIDを抽出"""
        # argsから抽出を試みる
        for arg in args:
            if isinstance(arg, dict) and 'task_id' in arg:
                return arg['task_id']
            if isinstance(arg, str) and arg.startswith('Task'):
                return arg
        
        # kwargsから抽出を試みる
        if 'task_id' in kwargs:
            return kwargs['task_id']
        if 'task' in kwargs and isinstance(kwargs['task'], dict):
            return kwargs['task'].get('task_id', 'Unknown')
        
        return f"Unknown-{datetime.now().strftime('%H%M%S')}"
    
    def _extract_file_path(self, error: Exception) -> Optional[str]:
        """エラーからファイルパスを抽出"""
        try:
            tb = traceback.extract_tb(error.__traceback__)
            if tb:
                # 最後のフレームからファイルパスを取得
                return tb[-1].filename
        except:
            pass
        
        return None
    
    def _infer_file_path(self, method_name: str) -> str:
        """メソッド名からファイルパスを推定"""
        # メソッド名からファイル名を推定
        if 'wp_agent' in method_name:
            return 'wordpress/wp_agent.py'
        elif 'plugin' in method_name:
            return 'wordpress/wp_plugin_manager.py'
        elif 'content' in method_name:
            return 'content_writers/base_writer.py'
        elif 'acf' in method_name:
            return 'wordpress/wp_dev/wp_acf_agent.py'
        elif 'cpt' in method_name:
            return 'wordpress/wp_dev/wp_cpt_agent.py'
        else:
            return 'task_executor/task_executor_ma.py'
    
    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        auto_fix_rate = 0.0
        if self.stats["total_errors_caught"] > 0:
            auto_fix_rate = (
                self.stats["auto_fixed_errors"] / 
                self.stats["total_errors_caught"]
            )
        
        return {
            **self.stats,
            "auto_fix_rate": auto_fix_rate,
            "recent_errors": self.error_history[-10:]  # 直近10件
        }
    
    def print_stats(self):
        """統計情報を表示"""
        stats = self.get_stats()
        
        print("\n" + "=" * 80)
        print("📊 システム統合エージェント 統計情報")
        print("=" * 80)
        print(f"捕捉エラー総数: {stats['total_errors_caught']}")
        print(f"自動修正成功: {stats['auto_fixed_errors']}")
        print(f"自動修正率: {stats['auto_fix_rate']:.1%}")
        print(f"リトライ成功: {stats['retry_successes']}")
        print(f"統合失敗: {stats['integration_failures']}")
        
        if stats['recent_errors']:
            print("\n最近のエラー:")
            for err in stats['recent_errors'][-5:]:
                print(f"  - {err['timestamp']}: {err['error_type']} in {err['method']}")
        
        print("=" * 80 + "\n")