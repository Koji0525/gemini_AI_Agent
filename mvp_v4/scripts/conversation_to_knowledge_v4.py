#!/usr/bin/env python3
"""
新しいシンプルフォーマット対応ナレッジ抽出器 - コピペ途切れ防止版
"""
import re
import json
import os
from datetime import datetime


class ConversationKnowledgeExtractorV4:
    def __init__(self):
        self.knowledge_file = "mvp_v4/knowledge/learned/conversation_knowledge_v4.json"
        os.makedirs(os.path.dirname(self.knowledge_file), exist_ok=True)

    def extract_from_simple_format(self, text):
        """新しいシンプルフォーマットからナレッジを抽出"""
        try:
            print("🔍 新しいフォーマットでナレッジを抽出中...")

            # シンプルな正規表現パターン - コピペ途切れに強い
            patterns = {
                "title": r"タイトル:\s*(.+)",
                "category": r"カテゴリ:\s*(.+)",
                "priority": r"重要度:\s*(.+)",
                "scenario": r"何が起きた:\s*(.+)",
                "environment": r"環境:\s*(.+)",
                "root_cause": r"根本原因:\s*(.+)",
                "solution_approach": r"解決手法:\s*(.+)",
                "success_rate": r"成功率:\s*(\d+)%",
            }

            knowledge = {"metadata": {}, "content": {}}

            # 基本フィールドの抽出
            for key, pattern in patterns.items():
                match = re.search(pattern, text)
                if match:
                    if key in ["title", "category", "priority"]:
                        knowledge["metadata"][key] = match.group(1).strip()
                    else:
                        knowledge["content"][key] = match.group(1).strip()

            # リスト形式のフィールド抽出
            direct_causes = re.findall(
                r"(\d+)\.\s*(.+)",
                (
                    re.search(r"直接原因:\s*(.*?)(?=【解決策】)", text, re.DOTALL).group(1)
                    if re.search(r"直接原因:\s*(.*?)(?=【解決策】)", text, re.DOTALL)
                    else ""
                ),
            )
            knowledge["content"]["direct_causes"] = [cause[1] for cause in direct_causes]

            learnings = re.findall(
                r"(\d+)\.\s*(.+)",
                (
                    re.search(r"【学び】\s*(.*?)(?=【予防策】)", text, re.DOTALL).group(1)
                    if re.search(r"【学び】\s*(.*?)(?=【予防策】)", text, re.DOTALL)
                    else ""
                ),
            )
            knowledge["content"]["learnings"] = [learn[1] for learn in learnings]

            prevention = re.findall(
                r"-\s*(.+)",
                (
                    re.search(r"【予防策】\s*(.*?)(?=成功率)", text, re.DOTALL).group(1)
                    if re.search(r"【予防策】\s*(.*?)(?=成功率)", text, re.DOTALL)
                    else ""
                ),
            )
            knowledge["content"]["prevention"] = prevention

            # コード例の抽出（複数行対応）
            code_match = re.search(r"実装例:\s*(.+?)(?=【学び】)", text, re.DOTALL)
            if code_match:
                knowledge["content"]["code_examples"] = code_match.group(1).strip()

            # 必須フィールドチェック
            if not knowledge["content"].get("scenario"):
                print("❌ '何が起きた' フィールドが見つかりません")
                return None

            if not knowledge["content"].get("root_cause"):
                print("❌ '根本原因' フィールドが見つかりません")
                return None

            print("✅ ナレッジ抽出成功")
            return self._format_final_knowledge(knowledge)

        except Exception as e:
            print(f"❌ 抽出エラー: {e}")
            import traceback

            traceback.print_exc()
            return None

    def _format_final_knowledge(self, extracted):
        """最終ナレッジ形式に変換"""
        return {
            "scenario": extracted["content"].get("scenario", ""),
            "cause": f"根本原因: {extracted['content'].get('root_cause', '')}",
            "solution": self._build_solution_text(extracted),
            "learnings": extracted["content"].get("learnings", []),
            "prevention": extracted["content"].get("prevention", []),
            "success_rate": int(extracted["content"].get("success_rate", 0)),
            "metadata": {
                "title": extracted["metadata"].get("title", ""),
                "category": extracted["metadata"].get("category", ""),
                "priority": extracted["metadata"].get("priority", "medium"),
                "environment": extracted["content"].get("environment", ""),
                "format_version": "v4_simple",
                "timestamp": datetime.now().isoformat(),
            },
        }

    def _build_solution_text(self, extracted):
        """解決策テキストを構築"""
        solution_parts = []

        if extracted["content"].get("solution_approach"):
            solution_parts.append(f"解決手法: {extracted['content']['solution_approach']}")

        if extracted["content"].get("direct_causes"):
            solution_parts.append("直接原因:")
            for i, cause in enumerate(extracted["content"]["direct_causes"], 1):
                solution_parts.append(f"  {i}. {cause}")

        if extracted["content"].get("code_examples"):
            solution_parts.append("実装例:")
            solution_parts.append(extracted["content"]["code_examples"])

        return "\n".join(solution_parts)

    def save_knowledge(self, knowledge):
        """ナレッジを保存"""
        try:
            # 既存のナレッジを読み込み
            existing_knowledge = []
            if os.path.exists(self.knowledge_file):
                with open(self.knowledge_file, "r", encoding="utf-8") as f:
                    existing_knowledge = json.load(f)

            # 新しいナレッジを追加
            existing_knowledge.append(knowledge)

            # 保存
            with open(self.knowledge_file, "w", encoding="utf-8") as f:
                json.dump(existing_knowledge, f, ensure_ascii=False, indent=2)

            print(f"💾 ナレッジを保存しました: {self.knowledge_file}")
            return True

        except Exception as e:
            print(f"❌ 保存エラー: {e}")
            return False


def main():
    """コマンドラインからの実行用"""
    import sys

    extractor = ConversationKnowledgeExtractorV4()

    if len(sys.argv) > 1:
        # ファイルから読み込み
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            content = f.read()
    else:
        # 標準入力から読み込み
        print("ナレッジ内容を入力してください（Ctrl+Dで終了）:")
        content = sys.stdin.read()

    knowledge = extractor.extract_from_simple_format(content)
    if knowledge:
        extractor.save_knowledge(knowledge)
        print("✅ ナレッジ登録完了！")
        return True
    else:
        print("❌ ナレッジ登録失敗")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
