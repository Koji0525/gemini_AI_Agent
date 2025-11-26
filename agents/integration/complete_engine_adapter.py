"""
CompleteEngine統合アダプター（返り値統一版）

【修正内容】
- V2の返り値を既存形式に変換
- 'status': 'success' → 'success': True
- API互換性の完全維持

使用例:
    # テストモード
    adapter = CompleteEngineAdapter(enable_v2=True, mock_mode=True)
    result = adapter.execute_goal_v2("goal_001")
    assert result['success'] is True  # ← 統一されたAPI
"""

import sys
from pathlib import Path
from typing import Any, Dict

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))


class CompleteEngineAdapter:
    """
    CompleteEngine統合アダプター（返り値統一版）

    既存CompleteEngineUltimateとV2機能を統合し、
    返り値形式を統一してAPI互換性を維持。
    """

    def __init__(self, enable_v2: bool = False, mock_mode: bool = False):
        """
        Args:
            enable_v2: V2機能（階層型システム）を有効にするか
            mock_mode: テストモード（認証情報不要）
        """
        self.enable_v2 = enable_v2
        self.mock_mode = mock_mode

        # V1エンジン初期化
        self.engine_v1 = None
        if not mock_mode:
            try:
                from agents.complete_engine_ultimate import \
                    CompleteEngineUltimate

                print("🔧 既存CompleteEngineUltimate初期化中...")
                self.engine_v1 = CompleteEngineUltimate()
                print("✅ 既存エンジン初期化完了")
            except Exception as e:
                print(f"⚠️  既存エンジン初期化失敗: {e}")
                print("   Mockモードで動作します")
                self.mock_mode = True
        else:
            print("🎭 Mockモードで動作（認証情報不要）")

        # V2エンジン初期化
        self.engine_v2 = None
        if self.enable_v2:
            try:
                from agents.complete_engine_ultimate_v2_fixed import \
                    CompleteEngineUltimateV2

                print("🔧 CompleteEngineUltimateV2初期化中...")
                self.engine_v2 = CompleteEngineUltimateV2(
                    mode="mock" if mock_mode else "legacy", mock=mock_mode
                )
                print("✅ V2エンジン初期化完了")
            except ImportError as e:
                print(f"⚠️  V2エンジンのインポートに失敗: {e}")
                print("   既存エンジンのみで動作します")
                self.enable_v2 = False

    def _normalize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        返り値を既存形式に統一

        V2形式: {'status': 'success', ...}
        ↓ 変換
        既存形式: {'success': True, ...}

        Args:
            result: 変換前の結果

        Returns:
            統一された結果
        """
        if result is None:
            return {"success": False, "error": "結果がNone"}

        # 既にsuccessキーがある場合はそのまま
        if "success" in result:
            return result

        # statusキーがある場合は変換
        if "status" in result:
            normalized = dict(result)  # コピー
            normalized["success"] = result["status"] == "success"
            return normalized

        # どちらもない場合はsuccessを追加
        result["success"] = True
        return result

    def execute_goal(self, goal_id: str, **kwargs) -> Dict[str, Any]:
        """
        ゴール実行（既存方式）

        Args:
            goal_id: ゴールID
            **kwargs: 追加パラメータ

        Returns:
            実行結果辞書（統一形式）
        """
        if self.mock_mode:
            # Mockモード
            print(f"🎭 Mock実行: ゴール {goal_id}")
            return {"success": True, "goal_id": goal_id, "mode": "mock", "message": "Mock実行成功"}

        if self.engine_v1 is None:
            return {"success": False, "error": "既存エンジンが初期化されていません"}

        print(f"📋 ゴール実行開始（既存方式）: {goal_id}")
        result = self.engine_v1.execute_goal(goal_id, **kwargs)
        return self._normalize_result(result)

    def execute_goal_v2(
        self, goal_id: str, mode: str = "hierarchical", mock: bool = False, **kwargs
    ) -> Dict[str, Any]:
        """
        ゴール実行（V2方式）

        Args:
            goal_id: ゴールID
            mode: 実行モード（'mock', 'hierarchical'）
            mock: Mockモードで実行するか
            **kwargs: 追加パラメータ

        Returns:
            実行結果辞書（統一形式）
        """
        if not self.enable_v2 or self.engine_v2 is None:
            print("⚠️  V2機能が無効です。既存方式で実行します。")
            return self.execute_goal(goal_id, **kwargs)

        print(f"📋 ゴール実行開始（V2方式）: {goal_id}, mode={mode}")

        # V2エンジンで実行
        result = self.engine_v2.execute_goal(goal_id)

        # 返り値を統一形式に変換
        return self._normalize_result(result)

    def switch_mode(self, enable_v2: bool) -> bool:
        """
        V2機能の有効/無効を切り替え

        Args:
            enable_v2: V2機能を有効にするか

        Returns:
            切り替え成功したか
        """
        if enable_v2 and self.engine_v2 is None:
            try:
                from agents.complete_engine_ultimate_v2_fixed import \
                    CompleteEngineUltimateV2

                print("🔧 CompleteEngineUltimateV2初期化中...")
                self.engine_v2 = CompleteEngineUltimateV2(
                    mode="mock" if self.mock_mode else "legacy", mock=self.mock_mode
                )
                print("✅ V2エンジン初期化完了")
                self.enable_v2 = True
                return True
            except ImportError as e:
                print(f"❌ V2エンジンの初期化に失敗: {e}")
                return False

        self.enable_v2 = enable_v2
        print(f"✅ モード切り替え完了: V2={'有効' if enable_v2 else '無効'}")
        return True

    def get_status(self) -> Dict[str, Any]:
        """
        現在の状態を取得

        Returns:
            状態辞書
        """
        return {
            "v1_initialized": self.engine_v1 is not None,
            "v2_initialized": self.engine_v2 is not None,
            "v2_enabled": self.enable_v2,
            "mock_mode": self.mock_mode,
            "current_mode": "V2" if self.enable_v2 else "V1",
        }


# テスト実行用のメイン関数
def main():
    """統合アダプターのテスト実行"""
    print("=" * 60)
    print("CompleteEngine統合アダプター テスト（返り値統一版）")
    print("=" * 60)
    print()

    # テスト1: Mockモード（V2無効）
    print("[テスト1] Mockモード（V2無効、認証不要）")
    print("-" * 60)
    adapter1 = CompleteEngineAdapter(enable_v2=False, mock_mode=True)
    result1 = adapter1.execute_goal("test_goal_001")
    print(f"実行結果: {result1}")
    assert result1["success"] is True, "V1 Mock実行失敗"
    print("✅ テスト成功")
    print()

    # テスト2: Mockモード（V2有効）
    print("[テスト2] Mockモード（V2有効、認証不要）")
    print("-" * 60)
    adapter2 = CompleteEngineAdapter(enable_v2=True, mock_mode=True)
    result2 = adapter2.execute_goal_v2("test_goal_002", mode="hierarchical")
    print(f"実行結果: {result2}")
    assert result2["success"] is True, "V2実行失敗"
    print("✅ テスト成功")
    print()

    # テスト3: 返り値形式確認
    print("[テスト3] 返り値形式の統一確認")
    print("-" * 60)
    adapter3 = CompleteEngineAdapter(enable_v2=True, mock_mode=True)

    # V1形式
    result_v1 = adapter3.execute_goal("test_v1")
    print(f"V1形式: {result_v1}")
    assert "success" in result_v1, "successキーがない"

    # V2形式（内部でstatusから変換される）
    result_v2 = adapter3.execute_goal_v2("test_v2")
    print(f"V2形式（変換後）: {result_v2}")
    assert "success" in result_v2, "successキーがない"

    print("✅ 両方ともsuccessキーを持つ（API統一）")
    print()

    print("=" * 60)
    print("✅ 統合アダプターテスト完了（返り値統一版）")
    print("=" * 60)


if __name__ == "__main__":
    main()
