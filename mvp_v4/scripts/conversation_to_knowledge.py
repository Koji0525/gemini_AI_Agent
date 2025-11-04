"""
会話ナレッジ抽出システム
Claudeとの会話から構造化ナレッジを自動生成

【Frugal AI戦略】
- 人間の暗黙知を形式知化
- 開発プロセス自体が学習データ
- 会話 = 最高品質のトラブルシューティング集
"""

import json
import re
from datetime import datetime
from typing import Dict


class ConversationKnowledgeExtractor:
    """会話からナレッジを抽出"""

    def __init__(self):
        self.extracted_knowledge = []

    def extract_from_report(self, report_text: str) -> Dict:
        """
        標準フォーマットのレポートからナレッジ抽出

        【変更理由】
        何が起きた: ユーザーが提案した標準フォーマット
        原因: 構造化された情報が最も抽出しやすい
        狙い: フォーマットに従うだけで自動ナレッジ化
        """
        knowledge = {
            "id": f"CONV_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "task_type": "",
            "scenario": "",
            "best_practice": "",
            "code_example": "",
            "success_rate": 0.0,
            "avg_execution_time": 0.0,
            "conditions": [],
            "avoid_patterns": [],
            "error_fixes": {},
        }

        # タスク名抽出
        task_match = re.search(r"\*\*タスク名\*\*:\s*(.+)", report_text)
        if task_match:
            knowledge["scenario"] = task_match.group(1).strip()

        # タスクタイプ抽出（タスクIDから推測）
        task_id_match = re.search(r"\*\*タスクID\*\*:\s*(\w+)_", report_text)
        if task_id_match:
            knowledge["task_type"] = task_id_match.group(1).lower()

        # ベストプラクティス抽出
        best_practice_match = re.search(
            r"\*\*ベストプラクティス\*\*:\s*(.+?)(?=\n-|\n\*\*|$)", report_text, re.DOTALL
        )
        if best_practice_match:
            knowledge["best_practice"] = best_practice_match.group(1).strip()

        # エラー修正方法抽出
        error_fixes = {}
        error_blocks = re.findall(
            r"- エラー:\s*(\w+)\n- 原因:\s*(.+?)\n.*?- 方法:\s*(.+?)(?=\n-|\n\*\*|$)",
            report_text,
            re.DOTALL,
        )

        for error_type, cause, solution in error_blocks:
            error_fixes[error_type.strip()] = solution.strip()

        if error_fixes:
            knowledge["error_fixes"] = error_fixes

        # 成功率抽出
        success_rate_match = re.search(r"成功率:\s*(\d+)%", report_text)
        if success_rate_match:
            knowledge["success_rate"] = float(success_rate_match.group(1)) / 100

        return knowledge

    def extract_from_error_log(self, error_text: str, solution_text: str) -> Dict:
        """
        エラーログと解決策からナレッジ抽出

        【変更理由】
        何が起きた: 今日のModuleNotFoundErrorのような実例
        原因: 開発中の実エラーが最良の学習素材
        狙い: エラー→解決のペアを自動ナレッジ化
        """
        knowledge = {
            "id": f"ERROR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "task_type": "troubleshooting",
            "scenario": "",
            "best_practice": "",
            "code_example": "",
            "success_rate": 1.0,  # 解決済みのため
            "avg_execution_time": 0.0,
            "conditions": [],
            "avoid_patterns": [],
            "error_fixes": {},
        }

        # エラータイプ抽出
        error_type_match = re.search(r"(\w+Error):", error_text)
        if error_type_match:
            error_type = error_type_match.group(1)
            knowledge["scenario"] = f"{error_type}の解決"

            # シンプルなエラーメッセージ抽出
            error_msg_match = re.search(rf"{error_type}:\s*(.+?)(?=\n|$)", error_text)
            if error_msg_match:
                error_msg_match.group(1).strip()

                # 解決策抽出（「何が起きた」「原因」「狙い」パターン）
                solution_parts = {"what": "", "cause": "", "goal": ""}

                what_match = re.search(
                    r"何が起きた:\s*(.+?)(?=原因:|狙い:|$)", solution_text, re.DOTALL
                )
                if what_match:
                    solution_parts["what"] = what_match.group(1).strip()

                cause_match = re.search(r"原因:\s*(.+?)(?=狙い:|$)", solution_text, re.DOTALL)
                if cause_match:
                    solution_parts["cause"] = cause_match.group(1).strip()

                goal_match = re.search(r"狙い:\s*(.+?)$", solution_text, re.DOTALL)
                if goal_match:
                    solution_parts["goal"] = goal_match.group(1).strip()

                # ベストプラクティス生成
                if solution_parts["goal"]:
                    knowledge["best_practice"] = solution_parts["goal"]

                # エラー修正方法
                knowledge["error_fixes"][error_type] = solution_parts["goal"]

                # 避けるべきパターン
                if solution_parts["cause"]:
                    knowledge["avoid_patterns"] = [solution_parts["cause"]]

        return knowledge

    def save_knowledge(
        self,
        knowledge: Dict,
        output_file: str = "mvp_v4/knowledge/learned/conversation_knowledge.json",
    ):
        """ナレッジをJSONファイルに保存"""
        import os

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # 既存ファイルがあれば読み込み
        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"knowledge_base": []}

        # 新しいナレッジを追加
        data["knowledge_base"].append(knowledge)

        # 保存
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ ナレッジ保存: {output_file}")
        print(f"   ID: {knowledge['id']}")
        print(f"   シナリオ: {knowledge['scenario']}")


# テスト実行
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🧪 会話ナレッジ抽出テスト")
    print("=" * 70 + "\n")

    extractor = ConversationKnowledgeExtractor()

    # 例1: 今日のModuleNotFoundErrorをナレッジ化
    error_log = """
    ModuleNotFoundError: No module named 'llama_index.vector_stores'
    """

    solution = """
    何が起きた: llama_index.vector_storesが見つからない
    原因: LlamaIndex v0.10+でモジュールが分離された
    狙い: 必要な拡張パッケージを個別インストール
         → pip install llama-index-vector-stores-chroma
    """

    knowledge1 = extractor.extract_from_error_log(error_log, solution)
    extractor.save_knowledge(knowledge1)

    print("\n✅ テスト完了")
