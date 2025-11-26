#!/usr/bin/env python3
"""
CompleteEngineUltimate V2
階層型アーキテクチャ統合版

既存CompleteEngineUltimateを継承し、階層型モードを追加
既存機能は完全保護

Google Docstring形式
"""
import logging
import sys
from pathlib import Path
from typing import Dict

# プロジェクトルート追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.complete_engine_ultimate import CompleteEngineUltimate
from agents.hierarchy.executive_manager import ExecutiveManager
from agents.hierarchy.messaging import MessageBus

logger = logging.getLogger(__name__)


class CompleteEngineUltimateV2(CompleteEngineUltimate):
    """
    CompleteEngineUltimate V2
    階層型アーキテクチャ対応版

    モード:
        - legacy: 既存動作（デフォルト）
        - hierarchical: 階層型実行

    Attributes:
        mode (str): 実行モード
        executive (ExecutiveManager): Executive Manager（階層型のみ）
        message_bus (MessageBus): メッセージバス（階層型のみ）
    """

    def __init__(self, mode: str = "legacy", sheets_manager=None, browser_controller=None):
        """
        初期化

        Args:
            mode (str): 実行モード ('legacy' or 'hierarchical')
            sheets_manager: GoogleSheetsManager
            browser_controller: BrowserController
        """
        # 既存初期化（完全保護）
        super().__init__(sheets_manager, browser_controller)

        self.mode = mode
        self.executive = None
        self.message_bus = None

        # 階層型モード初期化
        if mode == "hierarchical":
            self._init_hierarchical_mode()

        logger.info(f"CompleteEngineUltimateV2 初期化完了 (mode={mode})")

    def _init_hierarchical_mode(self):
        """階層型モードの初期化"""
        try:
            self.message_bus = MessageBus()
            self.executive = ExecutiveManager(
                executive_id="exec_001",
                goal_id="placeholder",  # execute_goal で設定
                sheets_manager=self.sheets,
                message_bus=self.message_bus,
            )
            logger.info("✅ 階層型モード初期化成功")
        except Exception as e:
            logger.error(f"❌ 階層型モード初期化失敗: {e}")
            raise

    def execute_goal(self, goal_id: str, count: int = 1) -> Dict:
        """
        ゴール実行（モード切り替え対応）

        Args:
            goal_id (str): ゴールID
            count (int): 実行回数

        Returns:
            Dict: 実行結果
        """
        if self.mode == "legacy":
            # 既存動作（完全保護）
            logger.info(f"Legacy モードで実行: goal_id={goal_id}")
            return super().execute_goal(goal_id, count)

        elif self.mode == "hierarchical":
            # 階層型実行
            logger.info(f"Hierarchical モードで実行: goal_id={goal_id}")
            return self._execute_hierarchical(goal_id, count)

        else:
            raise ValueError(f"未知のモード: {self.mode}")

    def _execute_hierarchical(self, goal_id: str, count: int) -> Dict:
        """
        階層型実行

        Args:
            goal_id (str): ゴールID
            count (int): 実行回数

        Returns:
            Dict: 実行結果
        """
        try:
            # Executive にゴール設定
            self.executive.goal_id = goal_id

            # チーム編成
            teams = self.executive.organize_teams()
            logger.info(f"チーム編成完了: {len(teams)}チーム")

            # 各チームにミッション割り当て
            for team_id, mission in teams.items():
                self.executive.assign_mission(team_id, mission)

            # 実行監視（簡易版）
            # TODO: 完全な監視ループ実装

            return {
                "status": "success",
                "mode": "hierarchical",
                "goal_id": goal_id,
                "teams": len(teams),
                "message": "階層型実行完了",
            }

        except Exception as e:
            logger.error(f"階層型実行失敗: {e}")
            return {"status": "error", "mode": "hierarchical", "error": str(e)}

    def get_mode(self) -> str:
        """現在のモードを取得"""
        return self.mode

    def switch_mode(self, new_mode: str):
        """
        モード切り替え

        Args:
            new_mode (str): 新しいモード
        """
        if new_mode not in ["legacy", "hierarchical"]:
            raise ValueError(f"無効なモード: {new_mode}")

        old_mode = self.mode
        self.mode = new_mode

        # 階層型に切り替える場合
        if new_mode == "hierarchical" and self.executive is None:
            self._init_hierarchical_mode()

        logger.info(f"モード切り替え: {old_mode} → {new_mode}")


# テスト実行
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("CompleteEngineUltimateV2 テスト")
    print("=" * 60)

    # 1. Legacyモードテスト
    print("\n[1/3] Legacy モードテスト")
    try:
        engine_legacy = CompleteEngineUltimateV2(mode="legacy")
        print(f"   モード: {engine_legacy.get_mode()}")
        print("   ✅ Legacy モード初期化成功")
    except Exception as e:
        print(f"   ❌ エラー: {e}")

    # 2. Hierarchicalモードテスト
    print("\n[2/3] Hierarchical モードテスト")
    try:
        engine_hier = CompleteEngineUltimateV2(mode="hierarchical")
        print(f"   モード: {engine_hier.get_mode()}")
        print(f"   Executive: {engine_hier.executive is not None}")
        print(f"   MessageBus: {engine_hier.message_bus is not None}")
        print("   ✅ Hierarchical モード初期化成功")
    except Exception as e:
        print(f"   ❌ エラー: {e}")

    # 3. モード切り替えテスト
    print("\n[3/3] モード切り替えテスト")
    try:
        engine = CompleteEngineUltimateV2(mode="legacy")
        print(f"   初期モード: {engine.get_mode()}")

        engine.switch_mode("hierarchical")
        print(f"   切替後: {engine.get_mode()}")

        engine.switch_mode("legacy")
        print(f"   切替後: {engine.get_mode()}")

        print("   ✅ モード切り替え成功")
    except Exception as e:
        print(f"   ❌ エラー: {e}")

    print("\n✅ CompleteEngineUltimateV2 テスト完了")
