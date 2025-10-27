"""
WordPress開発統合エージェント
既存の専門エージェントを統合して使用
"""

from typing import Dict, Any


class WordPressDevAgent:
    """
    WordPress開発タスクを統合管理するエージェント
    各専門エージェントへのルーティングを行う
    """

    def __init__(self, wp_page):
        """
        初期化

        Args:
            wp_page: WordPress管理画面のPageオブジェクト
        """
        self.wp_page = wp_page

        # 遅延インポート（循環参照回避）
        from .wp_cpt_agent import WordPressCPTAgent
        from .wp_acf_agent import WordPressACFAgent
        from .wp_requirements_agent import WordPressRequirementsAgent

        self.cpt_agent = WordPressCPTAgent(wp_page, "agent_outputs/wordpress/cpt")
        self.acf_agent = WordPressACFAgent(wp_page, "agent_outputs/wordpress/acf")
        self.requirements_agent = WordPressRequirementsAgent()

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        タスクを実行（専門エージェントに振り分け）

        Args:
            task: タスク辞書

        Returns:
            dict: 実行結果
        """
        description = task.get("Description", "") + task.get("Title", "")
        description_lower = description.lower()

        try:
            # タスク内容に応じて適切なエージェントに振り分け
            if any(
                keyword in description_lower
                for keyword in ["cpt", "custom post type", "カスタム投稿"]
            ):
                print("📝 CPTエージェントで処理中...")
                result = await self.cpt_agent.create_cpt_from_description(description)
                return {"status": "success", "output": result}

            elif any(
                keyword in description_lower
                for keyword in ["acf", "advanced custom fields", "カスタムフィールド"]
            ):
                print("📝 ACFエージェントで処理中...")
                result = await self.acf_agent.configure_acf_from_description(
                    description
                )
                return {"status": "success", "output": result}

            elif any(
                keyword in description_lower
                for keyword in ["要件", "requirements", "仕様"]
            ):
                print("📝 要件定義エージェントで処理中...")
                result = (
                    await self.requirements_agent.create_requirements_from_description(
                        description
                    )
                )
                return {"status": "success", "output": result}

            else:
                # 一般的なWordPressタスク
                result = f"""WordPress開発タスクを受け付けました

タスクID: {task.get('TaskID')}
タスク内容: {description}

このタスクは以下のいずれかのキーワードを含めると自動実行できます：
- CPT/カスタム投稿タイプ → CPTエージェント
- ACF/カスタムフィールド → ACFエージェント  
- 要件/仕様 → 要件定義エージェント

現在は手動で実行するか、タスク説明を更新してください。
"""
                return {"status": "pending", "output": result}

        except Exception as e:
            error_msg = f"WordPressタスク実行エラー: {e}"
            print(f"❌ {error_msg}")
            import traceback

            traceback.print_exc()
            return {"status": "error", "output": error_msg}
