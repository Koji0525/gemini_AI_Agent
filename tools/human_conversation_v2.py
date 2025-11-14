"""改善版人間との会話システム（段階的質問 + 自由記入）"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from datetime import datetime
from typing import Any, Dict, List, Optional


class HumanConversationV2:
    """改善版人間との会話システム

    改善点：
    1. 段階的な質問（複数の質問を連続で）
    2. 選択肢 + 自由記入の両方対応
    3. 回答に基づいて次の質問を生成
    4. より具体的な情報を引き出す
    """

    def __init__(self):
        self.conversation_dir = Path("/workspaces/gemini_AI_Agent/conversations")
        self.conversation_dir.mkdir(exist_ok=True)
        print("✅ HumanConversationV2 初期化完了")

    def start_conversation_flow(
        self, topic: str, initial_questions: List[Dict[str, Any]], context: Dict[str, Any] = None
    ) -> str:
        """会話フローを開始

        Args:
            topic: 会話のトピック
            initial_questions: 初期質問リスト
            context: 文脈情報

        Returns:
            会話ID
        """
        conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        conversation_data = {
            "conversation_id": conversation_id,
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "context": context or {},
            "questions": initial_questions,
            "current_question_index": 0,
            "answers": {},
            "status": "in_progress",  # in_progress/completed/cancelled
            "completed_at": None,
        }

        # ファイルに保存
        file_path = self.conversation_dir / f"{conversation_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(conversation_data, f, ensure_ascii=False, indent=2)

        # 表示用ファイル作成
        self._create_display_file(conversation_data)

        print(f"\n{'='*80}")
        print(f"💬 会話フロー開始: {topic}")
        print(f"{'='*80}")
        print(f"会話ID: {conversation_id}")
        print(f"質問数: {len(initial_questions)}個")
        print(f"\n回答方法:")
        print(f"  python3 /workspaces/gemini_AI_Agent/answer_conversation.py {conversation_id}")
        print(f"{'='*80}\n")

        return conversation_id

    def _create_display_file(self, conversation_data: Dict[str, Any]):
        """表示用ファイル作成"""
        conv_id = conversation_data["conversation_id"]
        current_index = conversation_data["current_question_index"]
        questions = conversation_data["questions"]

        if current_index >= len(questions):
            return  # 全質問完了

        current_q = questions[current_index]

        display_file = self.conversation_dir / f"{conv_id}_Q{current_index+1}_PLEASE_ANSWER.txt"

        with open(display_file, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write(f"🤖 質問 {current_index+1}/{len(questions)}\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"会話ID: {conv_id}\n")
            f.write(f"トピック: {conversation_data['topic']}\n\n")

            if conversation_data.get("context"):
                f.write("【背景情報】\n")
                for key, value in conversation_data["context"].items():
                    f.write(f"  {key}: {value}\n")
                f.write("\n")

            f.write("【質問】\n")
            f.write(f"{current_q['question']}\n\n")

            if current_q.get("options"):
                f.write("【選択肢】\n")
                for i, opt in enumerate(current_q["options"], 1):
                    f.write(f"  {i}. {opt}\n")
                f.write("\n")

            if current_q.get("allow_free_input", True):
                f.write("💡 選択肢以外の自由な回答も可能です\n\n")

            if current_q.get("examples"):
                f.write("【回答例】\n")
                for example in current_q["examples"]:
                    f.write(f"  - {example}\n")
                f.write("\n")

            f.write("=" * 80 + "\n")
            f.write("回答方法:\n")
            f.write("=" * 80 + "\n")
            f.write(f"  python3 /workspaces/gemini_AI_Agent/answer_conversation.py {conv_id}\n")

    def submit_answer(self, conversation_id: str, answer: str) -> Dict[str, Any]:
        """回答を送信

        Args:
            conversation_id: 会話ID
            answer: 回答内容

        Returns:
            更新された会話データ
        """
        file_path = self.conversation_dir / f"{conversation_id}.json"

        if not file_path.exists():
            return {"success": False, "error": "会話が見つかりません"}

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        current_index = data["current_question_index"]
        questions = data["questions"]

        if current_index >= len(questions):
            return {"success": False, "error": "全ての質問が完了しています"}

        current_q = questions[current_index]

        # 回答を記録
        data["answers"][current_q["id"]] = {
            "question": current_q["question"],
            "answer": answer,
            "answered_at": datetime.now().isoformat(),
        }

        # 次の質問へ
        data["current_question_index"] += 1

        # 全質問完了チェック
        if data["current_question_index"] >= len(questions):
            data["status"] = "completed"
            data["completed_at"] = datetime.now().isoformat()
            print(f"\n✅ 全質問完了！")
        else:
            print(f"\n✅ 質問 {current_index+1}/{len(questions)} 完了")
            print(f"   次: 質問 {data['current_question_index']+1}/{len(questions)}")

        # 保存
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # 古い表示ファイル削除
        old_display = (
            self.conversation_dir / f"{conversation_id}_Q{current_index+1}_PLEASE_ANSWER.txt"
        )
        if old_display.exists():
            old_display.unlink()

        # 次の質問の表示ファイル作成
        if data["status"] == "in_progress":
            self._create_display_file(data)

        return {
            "success": True,
            "status": data["status"],
            "progress": f"{data['current_question_index']}/{len(questions)}",
            "data": data,
        }

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """会話データ取得"""
        file_path = self.conversation_dir / f"{conversation_id}.json"

        if not file_path.exists():
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_active_conversations(self) -> List[Dict[str, Any]]:
        """進行中の会話を取得"""
        active = []

        for file_path in self.conversation_dir.glob("conv_*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if data.get("status") == "in_progress":
                active.append(data)

        return active


if __name__ == "__main__":
    conv = HumanConversationV2()

    # テスト: ゴール6の詳細な質問フロー
    questions = [
        {
            "id": "q1_implementation",
            "question": "どの実装方法が最適ですか？",
            "options": [
                "Python CLIツール（シンプル、すぐ使える）",
                "VS Code拡張（統合環境、高機能）",
                "Webアプリ（ブラウザで使える、チーム共有）",
            ],
            "allow_free_input": True,
            "examples": ["Python CLIツールで、後でVS Code拡張も作る"],
        },
        {
            "id": "q2_priority_feature",
            "question": "最優先で実装すべき機能は何ですか？",
            "options": [
                "AIによる自動コード生成",
                "リアルタイムエラー検出",
                "Git操作の自動化",
                "開発時間のトラッキング",
            ],
            "allow_free_input": True,
            "examples": ["AIコード生成を最優先、次にエラー検出"],
        },
        {
            "id": "q3_target_language",
            "question": "どのプログラミング言語をサポートしますか？",
            "options": ["Python", "JavaScript/TypeScript", "Go", "複数言語"],
            "allow_free_input": True,
            "examples": ["Python優先、後でTypeScriptも"],
        },
        {
            "id": "q4_api_choice",
            "question": "どのAI APIを使用しますか？",
            "options": [
                "Claude API (Anthropic)",
                "OpenAI GPT-4",
                "Gemini",
                "複数のAPIを組み合わせ",
            ],
            "allow_free_input": True,
            "examples": ["Claude APIをメインに、必要に応じてGPT-4も"],
        },
        {
            "id": "q5_output_format",
            "question": "生成されたコードをどのように出力しますか？",
            "options": [
                "ファイルに直接書き込み",
                "クリップボードにコピー",
                "エディタに挿入",
                "プレビュー後に選択",
            ],
            "allow_free_input": True,
        },
        {
            "id": "q6_testing",
            "question": "自動テストは必要ですか？",
            "options": [
                "はい、自動テスト生成も含める",
                "いいえ、コード生成のみ",
                "オプション機能として",
            ],
            "allow_free_input": True,
        },
        {
            "id": "q7_deadline",
            "question": "各フェーズの期限はどうしますか？",
            "options": [],
            "allow_free_input": True,
            "examples": [
                "MVP: 3日、機能追加: 7日、テスト: 10日、公開: 14日",
                "できるだけ早く（品質重視）",
            ],
        },
    ]

    conv_id = conv.start_conversation_flow(
        topic="ゴール6: GitHub開発効率化ツールの詳細設計",
        initial_questions=questions,
        context={"goal_id": "6", "goal": "GitHub開発を10倍加速するツール開発"},
    )

    print(f"\n次のステップ:")
    print(f"  python3 /workspaces/gemini_AI_Agent/answer_conversation.py {conv_id}")
