#!/usr/bin/env python3
"""
会話ログからナレッジ抽出 v4.0
- 複数行形式自動対応
- フォーマット自動修正
- 品質スコア算出
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

sys.path.append(str(Path(__file__).parent.parent.parent))

from mvp_v4.scripts.knowledge_format_validator import KnowledgeFormatValidator


class ConversationKnowledgeExtractorV4:
    """会話ログからナレッジを抽出（v4: 自動フォーマット修正対応）"""

    def __init__(self, output_dir: str = "mvp_v4/knowledge/learned"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_file = self.output_dir / "conversation_knowledge_v3.json"
        self.validator = KnowledgeFormatValidator()

    def extract_from_simple_format(self, text: str, auto_fix: bool = True) -> Optional[Dict]:
        """
        シンプル形式から抽出（v4: 自動修正機能付き）

        Args:
            text: 入力テキスト
            auto_fix: True=自動修正を適用, False=そのまま処理
        """
        # 自動修正を適用
        if auto_fix:
            text, logs = self.validator.auto_fix(text)
            for log in logs:
                print(f"  {log}")

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
                knowledge["context"] = line.split(":", 1)[1].strip() if ":" in line else ""

            # 狙い
            elif line.startswith("狙い"):
                knowledge["best_practice"] = line.split(":", 1)[1].strip() if ":" in line else ""

            # 成功率
            elif line.startswith("成功率"):
                try:
                    rate_str = line.split(":", 1)[1].strip().replace("%", "")
                    knowledge["success_rate"] = float(rate_str) / 100.0
                except:
                    knowledge["success_rate"] = 0.0

            # コード例
            elif line.startswith("```"):
                knowledge["code_example"] += line + "\n"

            # 教訓
            elif line.startswith("教訓"):
                knowledge["lessons_learned"] = line.split(":", 1)[1].strip() if ":" in line else ""

        # 品質スコア算出
        quality_score = self._calculate_quality_score(knowledge)
        knowledge["quality_score"] = quality_score

        # 必須フィールドチェック
        if not knowledge["scenario"] or not knowledge["best_practice"]:
            print(f"⚠️  必須フィールド不足")
            return None

        return knowledge

    def _calculate_quality_score(self, knowledge: Dict) -> int:
        """品質スコア算出（v4）"""
        score = 0

        # 基本項目（各2点）
        if knowledge.get("scenario"):
            score += 2
        if knowledge.get("best_practice"):
            score += 2
        if knowledge.get("context"):
            score += 1

        # 詳細度（各1点）
        if knowledge.get("code_example"):
            score += 2
        if knowledge.get("lessons_learned"):
            score += 1
        if knowledge.get("success_rate", 0) > 0:
            score += 1

        # 内容の充実度
        if len(knowledge.get("scenario", "")) > 20:
            score += 1
        if len(knowledge.get("best_practice", "")) > 30:
            score += 1

        return min(score, 10)

    def save_knowledge(self, knowledge: Dict) -> bool:
        """ナレッジを保存（品質スコア6点以上）"""
        if knowledge.get("quality_score", 0) < 6:
            print(f"⚠️  品質スコア不足: {knowledge.get('quality_score', 0)}/10")
            return False

        # 既存データを読み込み
        if self.output_file.exists():
            with open(self.output_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"knowledge_base": []}

        # 重複チェック
        for existing in data["knowledge_base"]:
            if existing.get("scenario") == knowledge.get("scenario"):
                print(f"⚠️  重複のためスキップ")
                return False

        # 追加
        data["knowledge_base"].append(knowledge)

        # 保存
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ ナレッジ保存成功 (品質スコア: {knowledge['quality_score']}/10)")
        print(f"📚 総件数: {len(data['knowledge_base'])}件")
        return True


# テスト実行
if __name__ == "__main__":
    extractor = ConversationKnowledgeExtractorV4()

    # テストケース1: 複数行形式
    test_multi_line = """
何が起きた:
ナレッジベース最速自動起動を実装

原因:
毎回フル初期化していたため起動に5秒かかっていた

狙い:
ChromaDB存在チェックのみで0.5秒以内に起動完了

成功率: 98%

教訓:
- 初回のみバックグラウンド初期化
- キャッシュ活用で2回目以降は即座完了
"""

    print("=" * 70)
    print("🧪 テスト1: 複数行形式")
    print("=" * 70)
    kb = extractor.extract_from_simple_format(test_multi_line)
    if kb:
        print(f"✅ 抽出成功: {kb['scenario']}")

    # テストケース2: 1行形式
    test_single_line = """
何が起きた: ナレッジ抽出が複数行形式で失敗
原因: extract_from_simple_formatが1行形式のみ対応
狙い: 自動フォーマット修正機能を追加
成功率: 100%
"""

    print("\n" + "=" * 70)
    print("🧪 テスト2: 1行形式")
    print("=" * 70)
    kb = extractor.extract_from_simple_format(test_single_line)
    if kb:
        print(f"✅ 抽出成功: {kb['scenario']}")
