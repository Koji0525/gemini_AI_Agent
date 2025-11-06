"""
成功事例の自動ナレッジ登録ツール
v1.15.0 - 2025-11-06

【機能】
- テスト成功時に自動的にナレッジベースに登録
- 成功パターンを蓄積して学習効率を向上
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class AutoKnowledgeRegister:
    """成功事例の自動ナレッジ登録"""

    def __init__(self, knowledge_dir: str = "mvp_v4/knowledge/learned"):
        """初期化"""
        self.knowledge_dir = Path(knowledge_dir)
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_file = self.knowledge_dir / "auto_registered_knowledge.json"

        # 既存ナレッジを読み込み
        self.knowledge_base = self._load_knowledge()

    def _load_knowledge(self) -> List[Dict]:
        """既存ナレッジを読み込み"""
        if self.knowledge_file.exists():
            try:
                with open(self.knowledge_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("knowledge_base", [])
            except Exception as e:
                print(f"⚠️ ナレッジ読み込みエラー: {e}")
        return []

    def _save_knowledge(self):
        """ナレッジを保存"""
        try:
            data = {
                "knowledge_base": self.knowledge_base,
                "total_entries": len(self.knowledge_base),
                "last_updated": datetime.now().isoformat(),
            }

            with open(self.knowledge_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"✅ ナレッジ保存完了: {self.knowledge_file}")
            return True
        except Exception as e:
            print(f"❌ ナレッジ保存エラー: {e}")
            return False

    def register_success(
        self,
        title: str,
        category: str,
        scenario: str,
        solution: str,
        context: Dict = None,
        importance: str = "中",
    ) -> bool:
        """
        成功事例を登録

        Args:
            title: タイトル
            category: カテゴリ
            scenario: シナリオ（何が起きたか）
            solution: 解決策
            context: コンテキスト情報
            importance: 重要度

        Returns:
            登録成功したかどうか
        """
        try:
            entry = {
                "title": title,
                "category": category,
                "scenario": scenario,
                "solution": solution,
                "context": context or {},
                "importance": importance,
                "timestamp": datetime.now().isoformat(),
                "auto_registered": True,
            }

            self.knowledge_base.append(entry)

            if self._save_knowledge():
                print(f"✅ 成功事例登録: {title}")
                return True
            else:
                return False

        except Exception as e:
            print(f"❌ 登録エラー: {e}")
            return False

    def get_statistics(self) -> Dict:
        """統計情報を取得"""
        total = len(self.knowledge_base)

        # カテゴリ別集計
        categories = {}
        for entry in self.knowledge_base:
            cat = entry.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "total_entries": total,
            "categories": categories,
            "last_updated": (
                max([e.get("timestamp", "") for e in self.knowledge_base]) if total > 0 else None
            ),
        }


# 使用例
if __name__ == "__main__":
    register = AutoKnowledgeRegister()

    # テスト用の成功事例を登録
    register.register_success(
        title="TestingAgent 正常動作確認",
        category="テスト/自動化",
        scenario="TestingAgentが構文チェック・スタイルチェック・テストケース生成を正常に実行",
        solution="PEP 8準拠のコードで構文チェック・スタイルチェックともに合格。テストケースも自動生成成功",
        context={
            "agent": "TestingAgent",
            "test_types": ["syntax", "style", "unit"],
            "pass_rate": 100.0,
        },
        importance="高",
    )

    # 統計表示
    stats = register.get_statistics()
    print(f"\n📊 ナレッジ統計:")
    print(f"  総登録数: {stats['total_entries']}")
    print(f"  カテゴリ: {stats['categories']}")
