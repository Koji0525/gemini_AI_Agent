"""
会話ログから自動でナレッジを抽出してSQLiteに登録
"""

import hashlib
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from knowledge_system.core_agents.knowledge_manager import KnowledgeManager


class SimpleKnowledgeExtractor:
    """シンプルなナレッジ抽出器"""

    def __init__(self, knowledge_manager: KnowledgeManager):
        self.km = knowledge_manager

    def extract_from_text(self, text: str) -> List[Dict[str, Any]]:
        """テキストからナレッジを抽出"""
        knowledges = []

        # パターン1: 問題→解決策
        problem_solution_pattern = (
            r"(?:問題|エラー|課題)[：:](.*?)(?:解決|対処|修正)[：:](.*?)(?:\n|$)"
        )
        matches = re.finditer(problem_solution_pattern, text, re.DOTALL)

        for match in matches:
            problem = match.group(1).strip()[:200]
            solution = match.group(2).strip()[:200]

            if len(problem) > 10 and len(solution) > 10:
                knowledges.append(
                    {
                        "scenario": problem,
                        "solution": solution,
                        "confidence": 0.7,
                        "success_rate": 0.8,
                        "category": "自動抽出",
                        "source_system": "auto_extractor",
                    }
                )

        # パターン2: ✅成功パターン
        success_pattern = r"✅(.*?)(?:\n|$)"
        for match in re.finditer(success_pattern, text):
            content = match.group(1).strip()
            if len(content) > 15:
                knowledges.append(
                    {
                        "scenario": content,
                        "solution": "実行成功",
                        "confidence": 0.6,
                        "success_rate": 0.9,
                        "category": "成功パターン",
                        "source_system": "auto_extractor",
                    }
                )

        # パターン3: 学び・教訓
        learning_pattern = r"(?:学び|教訓|ポイント)[：:](.*?)(?:\n|$)"
        for match in re.finditer(learning_pattern, text):
            content = match.group(1).strip()
            if len(content) > 15:
                knowledges.append(
                    {
                        "scenario": content,
                        "solution": "今後の参考",
                        "confidence": 0.5,
                        "success_rate": 0.7,
                        "category": "学び",
                        "source_system": "auto_extractor",
                    }
                )

        return knowledges

    def register_from_md_files(self, md_directory: Path) -> int:
        """MDファイルからナレッジを一括登録"""
        total_registered = 0
        md_files = list(md_directory.glob("*.md"))

        print(f"📁 {len(md_files)}個のMDファイルを検出")

        for md_file in md_files[:10]:  # 最初の10ファイルのみ
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    text = f.read()

                knowledges = self.extract_from_text(text)

                for knowledge in knowledges:
                    # 重複チェック（シナリオのハッシュ）
                    scenario_hash = hashlib.md5(knowledge["scenario"].encode()).hexdigest()
                    knowledge["id"] = f"AUTO_{scenario_hash[:12]}"

                    try:
                        self.km.register_knowledge(knowledge)
                        total_registered += 1
                    except:
                        pass  # 重複エラーはスキップ

                if knowledges:
                    print(f"  ✅ {md_file.name}: {len(knowledges)}件")

            except Exception:
                print(f"  ⚠️ {md_file.name}: エラー")

        return total_registered


def main():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🤖 自動ナレッジ抽出・登録")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # 設定読み込み
    config_path = project_root / "knowledge_system/configuration/knowledge_config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # ナレッジマネージャー初期化
    db_path = project_root / config["database"]["path"]
    index_path = project_root / config["vector_search"]["index_path"]
    model_name = config["vector_search"]["model_name"]

    km = KnowledgeManager(str(db_path), str(index_path), model_name)
    extractor = SimpleKnowledgeExtractor(km)

    # MDディレクトリからナレッジ抽出
    md_dir = project_root / "MD"
    if md_dir.exists():
        count = extractor.register_from_md_files(md_dir)
        print(f"\n✅ {count}件のナレッジを登録")

    # ベクトルインデックス保存
    km.save_vector_index()

    # 統計表示
    stats = km.get_stats()
    print(f"\n📊 総ナレッジ数: {stats['total_knowledge']}")
    print(f"🔍 ベクトルインデックス: {stats['vector_index_size']}")


if __name__ == "__main__":
    main()
