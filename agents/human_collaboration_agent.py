"""F9: 人間連携エージェント（会話機能統合版）"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Any, Dict, List, Optional

from tools.base_data_accessor import BaseDataAccessor
from tools.human_conversation import HumanConversation


class HumanCollaborationAgent:
    """人間連携エージェント（F9）

    機能：
    - 人間への質問・回答受信
    - 判断が必要な場面での確認
    - フィードバック収集
    """

    def __init__(self):
        """初期化"""
        self.accessor = BaseDataAccessor()
        self.conversation = HumanConversation()
        print("✅ HumanCollaborationAgent 初期化完了")

    def request_decision(
        self,
        context: str,
        options: List[str],
        priority: str = "normal",
        timeout: Optional[int] = None,
    ) -> Optional[str]:
        """人間に判断を依頼

        Args:
            context: 判断が必要な状況
            options: 選択肢
            priority: 優先度
            timeout: タイムアウト秒数

        Returns:
            選択された回答
        """
        print(f"\n{'='*80}")
        print(f"🤝 人間への判断依頼")
        print(f"{'='*80}")

        question_id = self.conversation.ask_question(
            question=f"判断をお願いします: {context}", options=options, priority=priority
        )

        if timeout:
            print(f"⏳ {timeout}秒間回答を待ちます...")
            answer = self.conversation.wait_for_answer(question_id, timeout)
        else:
            print(f"💡 回答は任意のタイミングで可能です（question_id: {question_id}）")
            answer = None

        return answer

    def request_feedback(self, task_id: str, result: Dict[str, Any]) -> Optional[str]:
        """タスク結果へのフィードバックを依頼

        Args:
            task_id: タスクID
            result: タスク実行結果

        Returns:
            フィードバック内容
        """
        print(f"\n{'='*80}")
        print(f"📝 フィードバック依頼")
        print(f"{'='*80}")

        question_id = self.conversation.ask_question(
            question=f"タスク {task_id} の結果についてフィードバックをお願いします",
            context={
                "task_id": task_id,
                "status": result.get("status"),
                "output_length": len(result.get("output", "")),
            },
            options=["良好 - このまま進める", "要改善 - 修正が必要", "不十分 - やり直し"],
            priority="normal",
        )

        return question_id

    def request_goal_clarification(self, goal_id: str, goal_description: str) -> Optional[str]:
        """ゴールの明確化を依頼

        Args:
            goal_id: ゴールID
            goal_description: ゴール説明

        Returns:
            質問ID
        """
        print(f"\n{'='*80}")
        print(f"🎯 ゴール明確化依頼")
        print(f"{'='*80}")

        question_id = self.conversation.ask_question(
            question=f"ゴール{goal_id}について、より具体的な要件を教えてください",
            context={"goal_id": goal_id, "current_description": goal_description},
            priority="high",
        )

        return question_id

    def request_priority_setting(self, tasks: List[Dict[str, Any]]) -> Optional[str]:
        """タスクの優先順位設定を依頼

        Args:
            tasks: タスクリスト

        Returns:
            質問ID
        """
        print(f"\n{'='*80}")
        print(f"🔢 優先順位設定依頼")
        print(f"{'='*80}")

        task_summaries = [
            f"{t.get('task_id')}: {t.get('description', '')[:50]}..." for t in tasks[:5]
        ]

        question_id = self.conversation.ask_question(
            question=f"以下のタスクの優先順位を教えてください:\n" + "\n".join(task_summaries),
            context={"total_tasks": len(tasks)},
            priority="normal",
        )

        return question_id

    def check_pending_questions(self) -> List[Dict[str, Any]]:
        """未回答の質問を確認

        Returns:
            未回答の質問リスト
        """
        pending = self.conversation.get_pending_questions()

        if pending:
            print(f"\n⚠️ 未回答の質問: {len(pending)}件")
            for q in pending:
                print(f"  - {q['question_id']}: {q['question'][:60]}...")

        return pending

    def collaborate_on_task(self, task: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """タスク実行での人間連携

        Args:
            task: タスク情報
            result: 実行結果

        Returns:
            連携結果
        """
        # 低品質の場合にフィードバックを依頼
        quality_score = result.get("quality_score", 0)

        if quality_score < 60:
            print(f"\n⚠️ 品質スコアが低い（{quality_score}点）")

            feedback_id = self.request_feedback(task_id=task.get("task_id"), result=result)

            return {
                "collaboration_triggered": True,
                "reason": "low_quality",
                "feedback_question_id": feedback_id,
            }

        return {"collaboration_triggered": False}


if __name__ == "__main__":
    # テスト
    agent = HumanCollaborationAgent()

    # 判断依頼テスト
    print("\n【テスト1: 判断依頼】")
    question_id = agent.request_decision(
        context="ゴール6の実装方法",
        options=[
            "Python CLIツールとして実装",
            "Webアプリケーションとして実装",
            "VS Code拡張として実装",
        ],
        priority="high",
    )

    # 未回答確認
    print("\n【テスト2: 未回答確認】")
    agent.check_pending_questions()
