"""
ナレッジ参照・蓄積機能強化モジュール
既存システムを破壊せず、機能を追加する
"""

import re
import sys
from typing import Any, Dict, List, Optional

# プロジェクトルートをパスに追加
sys.path.append("/workspaces/gemini_AI_Agent")

try:
    from knowledge_system.simple_knowledge_wrapper import \
        SimpleKnowledgeWrapper

    KNOWLEDGE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ ナレッジシステム利用不可: {e}")
    KNOWLEDGE_AVAILABLE = False


class KnowledgeEnhancer:
    """ナレッジ参照・蓄積機能を強化するクラス"""

    def __init__(self, knowledge_wrapper: Optional[Any] = None):
        """既存のナレッジラッパーを使用または新規作成"""
        self.enhancement_enabled = KNOWLEDGE_AVAILABLE

        if KNOWLEDGE_AVAILABLE:
            self.km = knowledge_wrapper or SimpleKnowledgeWrapper()
            print("✅ ナレッジエンハンサー初期化完了")
        else:
            self.km = None
            print("⚠️ ナレッジエンハンサー: 簡易モード")

    def search_relevant_knowledge(
        self, task_description: str, max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        タスクに関連するナレッジを検索
        """
        if not self.enhancement_enabled or not self.km:
            return []

        try:
            # キーワード抽出
            keywords = self._extract_keywords(task_description)

            # ナレッジ検索
            results = []
            for keyword in keywords[:3]:  # 上位3キーワードで検索
                search_results = self.km.search_knowledge(keyword, limit=max_results)
                if search_results:
                    results.extend(search_results)

            # 重複除去とスコア順ソート
            unique_results = self._deduplicate_results(results)
            return unique_results[:max_results]

        except Exception as e:
            print(f"⚠️ ナレッジ検索エラー: {e}")
            return []

    def save_task_knowledge(
        self, task_data: Dict[str, Any], execution_result: Dict[str, Any]
    ) -> bool:
        """
        タスク実行結果をナレッジとして保存
        """
        if not self.enhancement_enabled or not self.km:
            return False

        try:
            # ナレッジエントリ作成
            title = f"タスク実行: {task_data.get('description', '未知のタスク')[:50]}..."
            content = self._create_knowledge_content(task_data, execution_result)
            category = "task_execution"
            tags = self._generate_tags(task_data, execution_result)

            # ナレッジ保存
            success = self.km.add_knowledge(
                title=title, content=content, category=category, tags=tags
            )

            if success:
                print(f"💾 タスクナレッジを保存: {title}")
            else:
                print(f"⚠️ タスクナレッジ保存失敗: {title}")

            return success

        except Exception as e:
            print(f"⚠️ ナレッジ保存エラー: {e}")
            return False

    def enhance_task_with_knowledge(self, task_description: str) -> Dict[str, Any]:
        """
        ナレッジでタスクを強化
        """
        relevant_knowledge = self.search_relevant_knowledge(task_description)

        enhancement = {
            "original_task": task_description,
            "relevant_knowledge_count": len(relevant_knowledge),
            "knowledge_entries": relevant_knowledge,
            "suggestions": self._generate_suggestions(relevant_knowledge),
            "warnings": self._generate_warnings(relevant_knowledge),
            "enhancement_enabled": self.enhancement_enabled,
        }

        return enhancement

    def _extract_keywords(self, text: str) -> List[str]:
        """テキストからキーワードを抽出"""
        if not text:
            return []

        # ストップワード
        stop_words = {
            "する",
            "こと",
            "ため",
            "これ",
            "それ",
            "の",
            "を",
            "に",
            "は",
            "が",
            "と",
            "て",
            "で",
            "です",
            "ます",
        }

        # 単語分割（簡易版）
        words = re.findall(r"[\\w\\u4e00-\\u9fff]+", text)

        # ストップワード除去とフィルタリング
        keywords = [word for word in words if word not in stop_words and len(word) > 1]

        return keywords

    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """検索結果の重複除去"""
        if not results:
            return []

        seen = set()
        unique_results = []

        for result in results:
            result_id = result.get("id") or result.get("title", "") + result.get("content", "")
            if result_id not in seen:
                seen.add(result_id)
                unique_results.append(result)

        return unique_results

    def _create_knowledge_content(self, task_data: Dict, execution_result: Dict) -> str:
        """ナレッジコンテンツを作成"""
        content_parts = []

        # タスク情報
        content_parts.append(f"タスクID: {task_data.get('task_id', '不明')}")
        content_parts.append(f"説明: {task_data.get('description', '不明')}")
        content_parts.append(f"ステータス: {execution_result.get('status', '不明')}")

        # 実行結果
        if execution_result.get("output_summary"):
            content_parts.append(f"実行結果: {execution_result['output_summary']}")

        # エラー情報
        if execution_result.get("error_type"):
            content_parts.append(f"エラー種別: {execution_result['error_type']}")
            content_parts.append(f"修正内容: {execution_result.get('fix_applied', 'なし')}")

        # 品質評価
        if execution_result.get("Quality_Score"):
            content_parts.append(f"品質スコア: {execution_result['Quality_Score']}")
            content_parts.append(f"品質説明: {execution_result.get('Quality_description', 'なし')}")

        return "\\n".join(content_parts)

    def _generate_tags(self, task_data: Dict, execution_result: Dict) -> str:
        """タグを生成"""
        tags = []

        # タスク種別
        description = task_data.get("description", "")
        if "修正" in description:
            tags.append("bug_fix")
        if "追加" in description or "実装" in description:
            tags.append("feature")
        if "テスト" in description:
            tags.append("test")
        if "リファクタ" in description:
            tags.append("refactor")

        # 実行結果
        if execution_result.get("status") == "completed":
            tags.append("success")
        else:
            tags.append("failure")

        # エージェント種別
        agent_role = execution_result.get("agent_role", "")
        if agent_role:
            tags.append(f"agent:{agent_role}")

        return ",".join(tags)

    def _generate_suggestions(self, knowledge_entries: List[Dict]) -> List[str]:
        """関連ナレッジから提案を生成"""
        suggestions = []

        for entry in knowledge_entries[:2]:  # 上位2件のみ
            content = entry.get("content", "")
            title = entry.get("title", "")

            # 成功パターンからの提案
            if "成功" in title or "completed" in content.lower():
                suggestions.append(f"成功パターン参考: {title}")
            # 失敗パターンからの警告
            elif "失敗" in title or "error" in content.lower():
                suggestions.append(f"失敗パターン注意: {title}")

        return suggestions

    def _generate_warnings(self, knowledge_entries: List[Dict]) -> List[str]:
        """関連ナレッジから警告を生成"""
        warnings = []

        for entry in knowledge_entries:
            content = entry.get("content", "")

            # エラー関連の警告
            error_patterns = ["エラー", "error", "失敗", "修正必要", "bug", "例外"]
            if any(pattern in content.lower() for pattern in error_patterns):
                warnings.append(f"過去のエラー参考: {entry.get('title', '')}")

        return warnings[:2]  # 最大2件


# 簡易テスト
if __name__ == "__main__":
    print("🧪 ナレッジエンハンサー動作テスト")

    enhancer = KnowledgeEnhancer()

    # テストタスク
    test_task = "ファイルの読み込み処理を修正する"
    enhancement = enhancer.enhance_task_with_knowledge(test_task)

    print(f"元タスク: {enhancement['original_task']}")
    print(f"ナレッジ機能: {'有効' if enhancement['enhancement_enabled'] else '無効'}")
    print(f"関連ナレッジ数: {enhancement['relevant_knowledge_count']}")
    print(f"提案: {enhancement['suggestions']}")
    print(f"警告: {enhancement['warnings']}")
