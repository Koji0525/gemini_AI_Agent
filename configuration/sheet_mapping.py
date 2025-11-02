"""
sheet_mapping.py

スプレッドシートのシート名マッピング定義

【変更の理由】
- コード内のシート名と実際のシート名が不一致
- 既存のシート構造を尊重しつつ、コードを統一
- 将来の拡張性を考慮した設計
"""

from typing import Dict


class SheetMapping:
    """シート名マッピング管理"""

    # コード内で使用する論理名 → 実際のシート名
    SHEET_NAMES: Dict[str, str] = {
        # ============================================================
        # プロジェクト管理系
        # ============================================================
        "pm_goals": "project_goal",  # 目標管理
        "pm_tasks": "pm_tasks",  # タスク管理
        "pm_task_queue": "pm_task_queue",  # タスクキュー
        # ============================================================
        # 実行ログ系
        # ============================================================
        "task_execution_log": "task_execution_log",  # タスク実行ログ
        "execution_history": "history",  # 実行履歴
        "retry_history": "retry_history",  # リトライ履歴
        "retry_log": "retry_log",  # リトライログ
        # ============================================================
        # エラー管理系
        # ============================================================
        "error_log": "error_analysis",  # エラーログ
        "conversation_errors": "conversation_errors",  # 会話エラー
        # ============================================================
        # 設定・制御系
        # ============================================================
        "control_flags": "setting",  # 制御フラグ
        "project_metadata": "project_metadata",  # プロジェクトメタデータ
        # ============================================================
        # ダッシュボード・監視系
        # ============================================================
        "progress_dashboard": "progress_dashboard",  # 進捗ダッシュボード
        "protected_dashboard": "protected_dashboard",  # 保護ダッシュボード
        # ============================================================
        # ナレッジベース・学習系
        # ============================================================
        "knowledge_base": "knowledge_base",  # ナレッジベース
        "learning_patterns": "learning_patterns",  # 学習パターン
        "learned_patterns": "learned_patterns",  # 学習済みパターン
        "success_recipes": "success_recipes",  # 成功レシピ
        # ============================================================
        # その他
        # ============================================================
        "task_outputs": "task_outputs",  # タスク出力
        "context_log": "context_log",  # コンテキストログ
        "agent_registry": "agent_registry",  # エージェント登録
        "dev_rules": "dev_rules",  # 開発ルール
        "rule_history": "rule_history",  # ルール履歴
    }

    @classmethod
    def get(cls, logical_name: str, default: str = None) -> str:
        """
        論理名から実際のシート名を取得

        Args:
            logical_name: コード内で使用する論理名
            default: シート名が見つからない場合のデフォルト値

        Returns:
            実際のシート名
        """
        return cls.SHEET_NAMES.get(logical_name, default or logical_name)

    @classmethod
    def exists(cls, logical_name: str) -> bool:
        """論理名が定義されているか確認"""
        return logical_name in cls.SHEET_NAMES

    @classmethod
    def reverse_lookup(cls, actual_name: str) -> str:
        """実際のシート名から論理名を逆引き"""
        for logical, actual in cls.SHEET_NAMES.items():
            if actual == actual_name:
                return logical
        return actual_name


def main():
    """テスト実行"""
    print("=" * 60)
    print("📊 シートマッピング定義")
    print("=" * 60)

    mapping = SheetMapping()

    # テストケース
    test_cases = [
        "pm_goals",
        "control_flags",
        "error_log",
        "execution_history",
    ]

    print("\n【論理名 → 実際のシート名】")
    for logical in test_cases:
        actual = mapping.get(logical)
        print(f"  {logical:20s} → {actual}")

    print("\n【実際のシート名 → 論理名（逆引き）】")
    for logical in test_cases:
        actual = mapping.get(logical)
        reverse = mapping.reverse_lookup(actual)
        print(f"  {actual:20s} → {reverse}")

    print("=" * 60)


if __name__ == "__main__":
    main()
