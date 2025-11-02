#!/usr/bin/env python3
"""
ExecutionController - 実行制御の統一管理
再利用可能な実行モード制御パターン
"""
import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ExecutionModeType(Enum):
    """実行モードの種類"""
    PRODUCTION = "production"      # 本番
    TEST = "test"                  # テスト
    DEBUG = "debug"                # デバッグ
    DRY_RUN = "dry_run"           # ドライラン


@dataclass
class ExecutionMode:
    """
    実行モード設定
    
    全コンポーネントで共有される実行モード情報
    Single Source of Truth として機能
    """
    mode: ExecutionModeType
    max_cycles: Optional[int] = None
    wait_interval: int = 3600  # デフォルト1時間
    enable_learning: bool = True
    enable_retry: bool = True
    debug_verbose: bool = False
    
    @classmethod
    def from_env(cls) -> 'ExecutionMode':
        """環境変数から実行モードを生成"""
        # モード判定
        if os.getenv('TEST_MODE', '').lower() == 'true':
            mode = ExecutionModeType.TEST
            wait_interval = 1  # テストは1秒
        elif os.getenv('DEBUG_MODE', '').lower() == 'true':
            mode = ExecutionModeType.DEBUG
            wait_interval = 60  # デバッグは1分
        elif os.getenv('DRY_RUN', '').lower() == 'true':
            mode = ExecutionModeType.DRY_RUN
            wait_interval = 0  # ドライランは即時
        else:
            mode = ExecutionModeType.PRODUCTION
            wait_interval = 3600  # 本番は1時間
        
        # MAX_CYCLES
        max_cycles_str = os.getenv('MAX_CYCLES', '')
        max_cycles = int(max_cycles_str) if max_cycles_str else None
        
        return cls(
            mode=mode,
            max_cycles=max_cycles,
            wait_interval=wait_interval,
            debug_verbose=(mode == ExecutionModeType.DEBUG)
        )
    
    def is_test(self) -> bool:
        """テストモードか？"""
        return self.mode == ExecutionModeType.TEST
    
    def is_production(self) -> bool:
        """本番モードか？"""
        return self.mode == ExecutionModeType.PRODUCTION
    
    def should_wait(self) -> bool:
        """待機すべきか？"""
        return self.wait_interval > 0 and not self.is_test()


class CycleManager:
    """
    サイクル実行の制御管理
    
    サイクル数のカウント、継続判定、待機時間管理を担当
    """
    
    def __init__(self, execution_mode: ExecutionMode):
        self.mode = execution_mode
        self.cycle_count = 0
        logger.info(f"🔧 CycleManager初期化: mode={self.mode.mode.value}, "
                   f"max_cycles={self.mode.max_cycles}, "
                   f"wait_interval={self.mode.wait_interval}s")
    
    def increment_cycle(self):
        """サイクルカウントをインクリメント"""
        self.cycle_count += 1
    
    def should_continue(self) -> bool:
        """サイクルを継続すべきか？"""
        if self.mode.max_cycles is None:
            return True
        return self.cycle_count < self.mode.max_cycles
    
    def should_wait_after_cycle(self) -> bool:
        """サイクル後に待機すべきか？"""
        # まだ継続する必要がある場合のみ待機
        return self.should_continue() and self.mode.should_wait()
    
    def get_wait_time(self) -> int:
        """待機時間を取得（秒）"""
        return self.mode.wait_interval if self.should_wait_after_cycle() else 0
    
    def get_status(self) -> Dict[str, Any]:
        """現在の状態を取得"""
        return {
            'cycle_count': self.cycle_count,
            'max_cycles': self.mode.max_cycles,
            'should_continue': self.should_continue(),
            'wait_time': self.get_wait_time(),
            'mode': self.mode.mode.value
        }


class ExecutionController:
    """
    実行制御の統一コントローラ
    
    全コンポーネントに対する実行制御を提供
    """
    
    def __init__(self, execution_mode: Optional[ExecutionMode] = None):
        self.mode = execution_mode or ExecutionMode.from_env()
        self.cycle_manager = CycleManager(self.mode)
        
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("🎮 ExecutionController初期化")
        logger.info(f"   モード: {self.mode.mode.value}")
        logger.info(f"   最大サイクル: {self.mode.max_cycles or '無制限'}")
        logger.info(f"   待機間隔: {self.mode.wait_interval}秒")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    async def execute_cycle(self, cycle_func, *args, **kwargs):
        """
        サイクル実行の汎用メソッド
        
        Args:
            cycle_func: 実行する関数
            *args, **kwargs: cycle_funcに渡す引数
        
        Returns:
            実行結果
        """
        self.cycle_manager.increment_cycle()
        
        logger.info(f"{'='*60}")
        logger.info(f"🔄 サイクル {self.cycle_manager.cycle_count} 開始")
        logger.info(f"{'='*60}")
        
        result = await cycle_func(*args, **kwargs)
        
        return result
    
    def get_orchestrator_params(self) -> Dict[str, Any]:
        """Orchestrator用のパラメータを取得"""
        return {
            'single_cycle': True,  # 常に1サイクルのみ実行
            'max_duration_minutes': 60 if self.mode.is_production() else 5,
            'debug_mode': self.mode.debug_verbose
        }


# 使用例とテスト
if __name__ == "__main__":
    # テストモードで実行
    os.environ['TEST_MODE'] = 'true'
    os.environ['MAX_CYCLES'] = '3'
    
    controller = ExecutionController()
    
    print("\n【実行モード情報】")
    print(f"モード: {controller.mode.mode.value}")
    print(f"テストモード: {controller.mode.is_test()}")
    print(f"待機すべき: {controller.mode.should_wait()}")
    
    print("\n【サイクル管理】")
    for i in range(5):
        controller.cycle_manager.increment_cycle()
        status = controller.cycle_manager.get_status()
        print(f"サイクル {i+1}: {status}")
