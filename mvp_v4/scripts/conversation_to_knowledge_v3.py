"""
会話ナレッジ抽出システム v3.0
最も柔軟な抽出ロジック
"""

import json
import re
from datetime import datetime
from typing import Dict, Optional


class ConversationKnowledgeExtractorV3:
    """超柔軟な抽出エンジン"""

    def __init__(self):
        self.knowledge_hashes = set()

    def extract_from_simple_format(self, text: str) -> Optional[Dict]:
        """
        シンプルな1行形式から抽出

        例:
        何が起きた: エラー内容
        原因: 原因説明
        狙い: 解決方法
        成功率: 95%
        """
        knowledge = {
            "id": f"CONV_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "task_type": "general",
            "scenario": "",
            "best_practice": "",
            "code_example": "",
            "success_rate": 0.0,
            "created_at": datetime.now().isoformat(),
        }

        # 各行を解析
        lines = text.strip().split("\n")

        for line in lines:
            line = line.strip()

            # 何が起きた
            if line.startswith("何が起きた"):
                knowledge["scenario"] = line.split(":", 1)[1].strip() if ":" in line else ""

            # 原因
            elif line.startswith("原因"):
                cause = line.split(":", 1)[1].strip() if ":" in line else ""
                knowledge["avoid_patterns"] = [cause] if cause else []

            # 狙い
            elif line.startswith("狙い"):
                knowledge["best_practice"] = line.split(":", 1)[1].strip() if ":" in line else ""

            # 成功率
            elif "成功率" in line:
                match = re.search(r"(\d+)%", line)
                if match:
                    knowledge["success_rate"] = float(match.group(1)) / 100

        # コード例抽出
        code_match = re.search(r"```(?:bash|python|javascript)?\n(.+?)\n```", text, re.DOTALL)
        if code_match:
            knowledge["code_example"] = code_match.group(1).strip()

        return knowledge if knowledge["scenario"] else None

    def calculate_simple_score(self, knowledge: Dict) -> float:
        """簡易品質スコア（より寛容）"""
        score = 0.0

        if knowledge.get("scenario"):
            score += 3.0
        if knowledge.get("best_practice"):
            score += 3.0
        if knowledge.get("code_example"):
            score += 2.0
        if knowledge.get("success_rate", 0) > 0:
            score += 2.0

        return score

    def save_knowledge(
        self,
        knowledge: Dict,
        output_file: str = "mvp_v4/knowledge/learned/conversation_knowledge_v3.json",
    ):
        """保存（品質チェック緩め）"""
        import os

        score = self.calculate_simple_score(knowledge)
        knowledge["quality_score"] = score

        print(f"\n📊 品質スコア: {score}/10")

        # 5点以上で保存（v2より寛容）
        if score < 5.0:
            print(f"⚠️ 品質基準未達（5点以上必要）")
            print(f"   シナリオとベストプラクティスは必須です")
            return False

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"knowledge_base": []}

        data["knowledge_base"].append(knowledge)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ ナレッジ保存完了")
        print(f"   シナリオ: {knowledge['scenario']}")

        return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("�� v3.0テスト（最も柔軟）")
    print("=" * 70)

    extractor = ConversationKnowledgeExtractorV3()

    text = """
何が起きた: ModuleNotFoundError
原因: パッケージ分離
狙い: 個別インストール
成功率: 100%
    """

    kb = extractor.extract_from_simple_format(text)
    if kb:
        extractor.save_knowledge(kb)

    print("\n✅ テスト完了")
