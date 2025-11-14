"""人間との会話システム"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from datetime import datetime
from typing import Any, Dict, List, Optional


class HumanConversation:
    """人間との会話を管理するシステム

    会話の方法：
    1. 質問をJSONファイルに書き出す
    2. 人間が回答を同じファイルに追記
    3. システムが回答を読み取る
    """

    def __init__(self):
        self.conversation_dir = Path("/workspaces/gemini_AI_Agent/conversations")
        self.conversation_dir.mkdir(exist_ok=True)
        print("✅ HumanConversation 初期化完了")

    def ask_question(
        self,
        question: str,
        context: Dict[str, Any] = None,
        options: List[str] = None,
        priority: str = "normal",
    ) -> str:
        """人間に質問する

        Args:
            question: 質問内容
            context: 文脈情報
            options: 選択肢（あれば）
            priority: 優先度（low/normal/high/urgent）

        Returns:
            質問ID
        """
        question_id = f"q_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        question_data = {
            "question_id": question_id,
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "context": context or {},
            "options": options or [],
            "priority": priority,
            "status": "waiting",  # waiting/answered/cancelled
            "answer": None,
            "answered_at": None,
        }

        # ファイルに保存
        file_path = self.conversation_dir / f"{question_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(question_data, f, ensure_ascii=False, indent=2)

        # 表示用ファイル作成
        display_file = self.conversation_dir / f"{question_id}_PLEASE_ANSWER.txt"
        with open(display_file, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("🤖 AIからの質問\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"質問ID: {question_id}\n")
            f.write(f"優先度: {priority}\n")
            f.write(f"日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            if context:
                f.write("【背景情報】\n")
                for key, value in context.items():
                    f.write(f"  {key}: {value}\n")
                f.write("\n")

            f.write("【質問】\n")
            f.write(f"{question}\n\n")

            if options:
                f.write("【選択肢】\n")
                for i, opt in enumerate(options, 1):
                    f.write(f"  {i}. {opt}\n")
                f.write("\n")

            f.write("=" * 80 + "\n")
            f.write("回答方法:\n")
            f.write("=" * 80 + "\n")
            f.write(f"1. このファイルと同じ名前のJSONファイルを開く:\n")
            f.write(f"   {question_id}.json\n\n")
            f.write(f"2. 'answer'フィールドに回答を記入:\n")
            f.write(f'   "answer": "ここに回答を記入"\n\n')
            f.write(f"3. 'status'を'answered'に変更:\n")
            f.write(f'   "status": "answered"\n\n')
            f.write(f"4. ファイルを保存\n\n")
            f.write(f"または、簡単な方法:\n")
            f.write(f"  python3 /workspaces/gemini_AI_Agent/answer_question.py {question_id}\n")

        print(f"\n{'='*80}")
        print(f"💬 人間への質問を作成しました")
        print(f"{'='*80}")
        print(f"質問ID: {question_id}")
        print(f"優先度: {priority}")
        print(f"\n【質問】")
        print(f"{question}")
        if options:
            print(f"\n【選択肢】")
            for i, opt in enumerate(options, 1):
                print(f"  {i}. {opt}")
        print(f"\n回答ファイル: {display_file}")
        print(f"{'='*80}\n")

        return question_id

    def check_answer(self, question_id: str) -> Optional[Dict[str, Any]]:
        """回答を確認

        Args:
            question_id: 質問ID

        Returns:
            回答データ（未回答ならNone）
        """
        file_path = self.conversation_dir / f"{question_id}.json"

        if not file_path.exists():
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if data.get("status") == "answered" and data.get("answer"):
            return data

        return None

    def wait_for_answer(self, question_id: str, timeout: Optional[int] = None) -> Optional[str]:
        """回答を待つ

        Args:
            question_id: 質問ID
            timeout: タイムアウト秒数（Noneなら無限に待つ）

        Returns:
            回答内容
        """
        import time

        start_time = time.time()

        print(f"⏳ 回答を待っています... (質問ID: {question_id})")

        while True:
            answer_data = self.check_answer(question_id)

            if answer_data:
                print(f"✅ 回答を受信しました！")
                return answer_data["answer"]

            if timeout and (time.time() - start_time) > timeout:
                print(f"⏰ タイムアウト")
                return None

            time.sleep(5)  # 5秒ごとにチェック

    def get_pending_questions(self) -> List[Dict[str, Any]]:
        """未回答の質問一覧"""
        pending = []

        for file_path in self.conversation_dir.glob("q_*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if data.get("status") == "waiting":
                pending.append(data)

        return pending


if __name__ == "__main__":
    conv = HumanConversation()

    # テスト質問
    question_id = conv.ask_question(
        question="ゴール6の開発において、どの機能を最優先で実装すべきですか？",
        context={"goal_id": "6", "goal": "GitHub開発効率化ツール", "current_progress": "0%"},
        options=[
            "AIによる自動コード生成",
            "リアルタイムエラー検出",
            "Git操作の自動化",
            "開発時間のトラッキング",
        ],
        priority="high",
    )

    print(f"\n次のステップ:")
    print(f"  python3 /workspaces/gemini_AI_Agent/answer_question.py {question_id}")
