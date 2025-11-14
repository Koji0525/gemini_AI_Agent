"""F0: ゴールの具体化エージェント（SMART変換）"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from datetime import datetime
from typing import Any, Dict, List, Tuple

from tools.base_data_accessor import BaseDataAccessor


class GoalConcreteAgent:
    """ゴール具体化エージェント（F0）

    SMARTフレームワークを用いてゴールを具体化します：
    - Specific: 具体的
    - Measurable: 測定可能
    - Achievable: 達成可能
    - Relevant: 関連性
    - Time-bound: 時間制約
    """

    def __init__(self):
        """初期化"""
        self.accessor = BaseDataAccessor()
        self.output_dir = Path("/workspaces/gemini_AI_Agent/agent_outputs/goal")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print("✅ GoalConcreteAgent 初期化完了")

    def is_goal_concretized(self, goal_id: str) -> Tuple[bool, str]:
        """ゴールが既に具体化されているか確認

        Args:
            goal_id: ゴールID

        Returns:
            (具体化済みか, 最新ファイルパス)
        """
        # goal_id_*_v*.json のファイルを探す
        pattern = f"{goal_id}_*.json"
        files = list(self.output_dir.glob(pattern))

        if not files:
            return False, ""

        # 最新ファイルを取得
        latest_file = max(files, key=lambda f: f.stat().st_mtime)

        # ファイル内容確認
        try:
            with open(latest_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # SMART5項目が全て埋まっているか
            smart_complete = all(
                data.get("smart", {}).get(key)
                for key in ["specific", "measurable", "achievable", "relevant", "time_bound"]
            )

            return smart_complete, str(latest_file)

        except Exception as e:
            print(f"⚠️ ファイル読み込みエラー: {e}")
            return False, ""

    def start_goal_concretization(self, goal_id: str, goal_description: str) -> Dict[str, Any]:
        """ゴールの具体化プロセス開始

        Args:
            goal_id: ゴールID
            goal_description: ゴール説明（抽象的）

        Returns:
            具体化結果
        """
        print("\n" + "=" * 80)
        print(f"🎯 F0: ゴールの具体化開始 - {goal_id}")
        print("=" * 80)

        # 既に具体化済みか確認
        is_concrete, concrete_file = self.is_goal_concretized(goal_id)

        if is_concrete:
            print(f"✅ 既に具体化済み: {concrete_file}")

            # ファイル読み込み
            with open(concrete_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            return {
                "success": True,
                "status": "already_concrete",
                "concrete_goal": data.get("concrete_goal", goal_description),
                "file_path": concrete_file,
                "data": data,
            }

        # 具体化プロセス開始
        print(f"\n元のゴール: {goal_description}\n")

        # SMART質問リスト
        smart_questions = self._generate_smart_questions(goal_description)

        # 対話ログ
        conversation_log = {
            "goal_id": goal_id,
            "original_goal": goal_description,
            "timestamp": datetime.now().isoformat(),
            "conversation": [],
            "smart": {},
        }

        # 各SMART項目について質問
        print("【SMART具体化プロセス】")

        for step, (key, question) in enumerate(smart_questions.items(), 1):
            print(f"\nステップ{step}: {key}")
            print(f"質問: {question}")

            # 自動回答生成（AI実装時は実際の対話に）
            answer = self._auto_answer_smart(key, goal_description)
            print(f"回答: {answer}")

            conversation_log["conversation"].append(
                {"step": step, "category": key, "question": question, "answer": answer}
            )

            conversation_log["smart"][key] = answer

        # 具体化されたゴール生成
        concrete_goal = self._generate_concrete_goal(conversation_log["smart"])
        conversation_log["concrete_goal"] = concrete_goal

        print(f"\n【具体化されたゴール】")
        print(f"{concrete_goal}\n")

        # ファイル保存
        file_name = f"{goal_id}_{datetime.now().strftime('%Y%m%d')}_v0.json"
        file_path = self.output_dir / file_name

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(conversation_log, f, ensure_ascii=False, indent=2)

        print(f"✅ 具体化ログ保存: {file_path}")

        return {
            "success": True,
            "status": "newly_concrete",
            "concrete_goal": concrete_goal,
            "file_path": str(file_path),
            "data": conversation_log,
        }

    def ask_final_questions(self, goal_id: str, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """最終段階での追加質問

        Args:
            goal_id: ゴールID
            tasks: 生成されたタスクリスト

        Returns:
            質問結果
        """
        print("\n" + "=" * 80)
        print(f"❓ F0: 最終確認質問 - {goal_id}")
        print("=" * 80)

        # 既存ファイル確認
        _, latest_file = self.is_goal_concretized(goal_id)

        if not latest_file:
            print("⚠️ 具体化ファイルが見つかりません")
            return {"success": False}

        # バージョン番号取得
        import re

        match = re.search(r"_v(\d+)", latest_file)
        version = int(match.group(1)) + 1 if match else 1

        # 質問内容生成
        questions = [
            "生成されたタスクに不足はありませんか？",
            "優先順位は適切ですか？",
            "依存関係は正しいですか？",
            "追加で必要なタスクはありますか？",
        ]

        question_log = {
            "goal_id": goal_id,
            "timestamp": datetime.now().isoformat(),
            "version": version,
            "type": "question",
            "tasks_count": len(tasks),
            "questions": [],
        }

        print(f"\n生成タスク数: {len(tasks)}個\n")

        for i, question in enumerate(questions, 1):
            print(f"{i}. {question}")

            # 自動回答（AI実装時は実際の対話に）
            answer = "特に問題ありません" if i <= 3 else "追加タスクなし"
            print(f"   → {answer}\n")

            question_log["questions"].append({"question": question, "answer": answer})

        # ファイル保存
        file_name = f"{goal_id}_{datetime.now().strftime('%Y%m%d')}_v{version}_question.json"
        file_path = self.output_dir / file_name

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(question_log, f, ensure_ascii=False, indent=2)

        print(f"✅ 質問ログ保存: {file_path}")

        return {"success": True, "file_path": str(file_path), "data": question_log}

    def _generate_smart_questions(self, goal_description: str) -> Dict[str, str]:
        """SMART質問リスト生成"""
        return {
            "specific": f"「{goal_description[:50]}...」を、より具体的に表現すると何ですか？（何を、どのように）",
            "measurable": "その目標の達成度は、どのように測定できますか？（数値目標、指標）",
            "achievable": "この目標は、どのような手段で達成可能ですか？（必要なリソース、技術）",
            "relevant": "この目標を達成することで、どのような効果が得られますか？（ビジネス価値、影響）",
            "time_bound": "この目標は、いつまでに達成しますか？（期限、マイルストーン）",
        }

    def _auto_answer_smart(self, key: str, goal_description: str) -> str:
        """SMART自動回答生成（簡易版）"""
        # 実際のAI実装時は、対話型に置き換え

        templates = {
            "specific": f"{goal_description}の機能を実装し、動作可能な状態にする",
            "measurable": "動作テスト成功、品質スコア70点以上",
            "achievable": "既存システムとの連携、段階的な実装により達成可能",
            "relevant": "システムの完成度向上、自律稼働の実現に貢献",
            "time_bound": "2週間以内に実装完了",
        }

        return templates.get(key, "未設定")

    def _generate_concrete_goal(self, smart: Dict[str, str]) -> str:
        """SMART項目から具体的なゴールを生成"""
        return (
            f"{smart.get('specific', '')}を、"
            f"{smart.get('measurable', '')}の基準で、"
            f"{smart.get('achievable', '')}により、"
            f"{smart.get('relevant', '')}を実現し、"
            f"{smart.get('time_bound', '')}に達成する"
        )


if __name__ == "__main__":
    # テスト実行
    agent = GoalConcreteAgent()

    # テストゴール
    test_goal = "githubの開発で開発加速するためのツールを開発したい"

    result = agent.start_goal_concretization(goal_id="6", goal_description=test_goal)

    print("\n" + "=" * 80)
    print("テスト結果:")
    print(f"  成功: {result['success']}")
    print(f"  ステータス: {result['status']}")
    print(f"  具体化ゴール: {result['concrete_goal']}")
