#!/usr/bin/env python3
"""
KnowledgeBaseManager: 統合ナレッジベース管理

全ての実行ログを統合し、パターンを抽出して学習データを蓄積する。
AIがAIを進化させる自己強化ループの中核。
"""
import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
import json
from collections import defaultdict


class KnowledgePattern:
    """抽出されたパターン"""

    def __init__(
        self,
        pattern_type: str,  # success_pattern / failure_pattern / fix_recipe
        description: str,
        context: Dict[str, Any],
        source_logs: List[str],
    ):
        self.pattern_type = pattern_type
        self.description = description
        self.context = context
        self.source_logs = source_logs
        self.success_rate = 0.0
        self.usage_count = 0
        self.effectiveness_score = 0
        self.related_errors = []
        self.applicable_conditions = {}
        self.code_snippet = ""
        self.learning_tags = []
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換（Google Sheets保存用）"""
        return {
            "knowledge_id": f"KB_{self.timestamp.strftime('%Y%m%d_%H%M%S')}",
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "knowledge_type": self.pattern_type,
            "pattern_description": self.description,
            "context": json.dumps(self.context, ensure_ascii=False),
            "source_logs": json.dumps(self.source_logs, ensure_ascii=False),
            "success_rate": str(self.success_rate),
            "usage_count": str(self.usage_count),
            "effectiveness_score": str(self.effectiveness_score),
            "related_errors": json.dumps(self.related_errors, ensure_ascii=False),
            "applicable_conditions": json.dumps(self.applicable_conditions, ensure_ascii=False),
            "code_snippet": self.code_snippet,
            "learning_tags": ",".join(self.learning_tags),
        }

    def to_row(self, headers: List[str]) -> List[str]:
        """Google Sheets行形式に変換"""
        data = self.to_dict()
        return [str(data.get(h, "")) for h in headers]


class KnowledgeBaseManager:
    """統合ナレッジベース管理システム"""

    KB_SHEET = "knowledge_base"
    PATTERN_SHEET = "learning_patterns"
    RECIPE_SHEET = "success_recipes"

    def __init__(self, sheets_manager):
        """
        初期化

        Args:
            sheets_manager: GoogleSheetsManagerインスタンス
        """
        self.sheets_manager = sheets_manager
        #
        self.spreadsheet_id = sheets_manager.spreadsheet_id

        print("✅ KnowledgeBaseManager初期化完了")

    def _get_sheet(self, sheet_name: str):
        """シートを取得（GoogleSheetsManagerの新インターフェース対応）"""
        try:
            # GoogleSheetsManagerのget_dataメソッドを使用
            self.sheets.get_data(sheet_name)
            # シート自体が必要な場合は、clientを使用
            if hasattr(self.sheets, "client") and self.sheets.client:
                return self.sheets.client.open_by_key(self.sheets.spreadsheet_id).worksheet(
                    sheet_name
                )
            return None
        except Exception as e:
            logger.warning(f"シート取得失敗: {sheet_name} - {e}")
            return None
        except Exception as e:
            print(f"⚠️ シート取得エラー ({sheet_name}): {e}")
            return None

    async def mine_patterns_from_logs(self) -> List[KnowledgePattern]:
        """
        既存のログからパターンをマイニング

        統合するログ:
        - task_execution_log
        - retry_log
        - context_log
        - feedback_queue

        Returns:
            抽出されたパターンのリスト
        """
        patterns = []

        print("🔍 ログからパターンをマイニング中...")

        # 1. 成功パターンの抽出
        success_patterns = await self._extract_success_patterns()
        patterns.extend(success_patterns)
        print(f"   ✅ 成功パターン: {len(success_patterns)}件")

        # 2. 失敗パターンの抽出
        failure_patterns = await self._extract_failure_patterns()
        patterns.extend(failure_patterns)
        print(f"   ✅ 失敗パターン: {len(failure_patterns)}件")

        # 3. 修正レシピの抽出
        fix_recipes = await self._extract_fix_recipes()
        patterns.extend(fix_recipes)
        print(f"   ✅ 修正レシピ: {len(fix_recipes)}件")

        return patterns

    async def _extract_success_patterns(self) -> List[KnowledgePattern]:
        """成功パターンを抽出"""
        try:
            sheet = self._get_sheet("task_execution_log")
            if not sheet:
                return []

            records = sheet.get_all_records()

            # 成功タスクをグループ化
            success_groups = defaultdict(list)
            for record in records:
                if (
                    record.get("status") == "completed"
                    and float(record.get("quality_score", 0)) >= 8
                ):
                    task_type = record.get("execution_type", "unknown")
                    success_groups[task_type].append(record)

            patterns = []
            for task_type, successes in success_groups.items():
                if len(successes) >= 3:  # 3回以上成功したパターンのみ
                    pattern = KnowledgePattern(
                        pattern_type="success_pattern",
                        description=f"{task_type}タスクの成功パターン（{len(successes)}回成功）",
                        context={"task_type": task_type, "success_count": len(successes)},
                        source_logs=[str(r.get("log_id", "")) for r in successes[:5]],  # 最初の5件
                    )
                    pattern.success_rate = 100.0
                    pattern.usage_count = len(successes)
                    pattern.effectiveness_score = min(100, len(successes) * 10)
                    pattern.learning_tags = [task_type, "success", "high_quality"]
                    patterns.append(pattern)

            return patterns

        except Exception as e:
            print(f"⚠️ 成功パターン抽出エラー: {e}")
            return []

    async def _extract_failure_patterns(self) -> List[KnowledgePattern]:
        """失敗パターンを抽出"""
        try:
            sheet = self._get_sheet("retry_log")
            if not sheet:
                return []

            records = sheet.get_all_records()

            # エラータイプごとにグループ化
            failure_groups = defaultdict(list)
            for record in records:
                success_str = str(record.get("success", "True")).lower()
                if success_str in ["false", "0", "no"]:
                    error_type = record.get("error_type", "unknown")
                    failure_groups[error_type].append(record)

            patterns = []
            for error_type, failures in failure_groups.items():
                if len(failures) >= 2:  # 2回以上発生した失敗パターン
                    pattern = KnowledgePattern(
                        pattern_type="failure_pattern",
                        description=f"{error_type}エラーの発生パターン（{len(failures)}回発生）",
                        context={"error_type": error_type, "occurrence": len(failures)},
                        source_logs=[str(r.get("log_id", "")) for r in failures[:5]],
                    )
                    pattern.related_errors = [error_type]
                    pattern.learning_tags = [error_type, "failure", "requires_attention"]
                    patterns.append(pattern)

            return patterns

        except Exception as e:
            print(f"⚠️ 失敗パターン抽出エラー: {e}")
            return []

    async def _extract_fix_recipes(self) -> List[KnowledgePattern]:
        """修正レシピを抽出（context_logから）"""
        try:
            sheet = self._get_sheet("context_log")
            if not sheet:
                return []

            records = sheet.get_all_records()

            patterns = []
            for record in records:
                pattern_name = record.get("pattern_name", "")
                if pattern_name:
                    pattern = KnowledgePattern(
                        pattern_type="fix_recipe",
                        description=record.get("modification_purpose", "修正レシピ"),
                        context={
                            "error_type": record.get("error_type"),
                            "decision_process": record.get("decision_process"),
                            "expected_result": record.get("expected_result"),
                        },
                        source_logs=[record.get("log_id", "")],
                    )
                    pattern.code_snippet = pattern_name

                    # システム状態をJSONパース
                    try:
                        pattern.applicable_conditions = json.loads(record.get("system_state", "{}"))
                    except:
                        pattern.applicable_conditions = {}

                    tags = record.get("learning_tags", "")
                    pattern.learning_tags = tags.split(",") if tags else []
                    patterns.append(pattern)

            return patterns

        except Exception as e:
            print(f"⚠️ 修正レシピ抽出エラー: {e}")
            return []

    async def save_pattern(self, pattern: KnowledgePattern) -> bool:
        """
        パターンをナレッジベースに保存

        Args:
            pattern: 保存するパターン

        Returns:
            成功時True
        """
        try:
            sheet = self._get_sheet(self.KB_SHEET)
            if not sheet:
                return False

            # ヘッダーを取得
            headers = sheet.row_values(1)

            # パターンを行形式に変換
            row = pattern.to_row(headers)

            # 追加
            sheet.append_rows(row)

            print(f"✅ パターン保存: {pattern.description[:50]}...")
            return True

        except Exception as e:
            print(f"❌ パターン保存エラー: {e}")
            return False

    def search_similar_knowledge(
        self, query_context: Dict[str, Any], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        類似のナレッジを検索

        Args:
            query_context: 検索クエリのコンテキスト
            limit: 返す結果の最大数

        Returns:
            類似ナレッジのリスト
        """
        try:
            sheet = self._get_sheet(self.KB_SHEET)
            if not sheet:
                return []

            records = sheet.get_all_records()

            # 簡易的な類似度計算
            scored_records = []
            for record in records:
                score = self._calculate_similarity(query_context, record)
                scored_records.append((score, record))

            # スコア順にソート
            scored_records.sort(key=lambda x: x[0], reverse=True)

            return [r[1] for r in scored_records[:limit]]

        except Exception as e:
            print(f"⚠️ ナレッジ検索エラー: {e}")
            return []

    def _calculate_similarity(self, query: Dict[str, Any], record: Dict[str, Any]) -> float:
        """簡易的な類似度計算"""
        score = 0.0

        # エラータイプが一致
        try:
            related_errors = json.loads(record.get("related_errors", "[]"))
            if query.get("error_type") in related_errors:
                score += 0.5
        except:
            pass

        # タスクタイプが一致
        try:
            context = json.loads(record.get("context", "{}"))
            if query.get("task_type") == context.get("task_type"):
                score += 0.3
        except:
            pass

        # 有効性スコアを考慮
        try:
            effectiveness = float(record.get("effectiveness_score", 0))
            score += (effectiveness / 100) * 0.2
        except:
            pass

        return score

    def get_statistics(self) -> Dict[str, Any]:
        """ナレッジベースの統計情報を取得"""
        try:
            sheet = self._get_sheet(self.KB_SHEET)
            if not sheet:
                return {}

            records = sheet.get_all_records()

            # タイプ別集計
            type_counts = defaultdict(int)
            for record in records:
                knowledge_type = record.get("knowledge_type", "unknown")
                type_counts[knowledge_type] += 1

            return {
                "total_knowledge": len(records),
                "success_patterns": type_counts.get("success_pattern", 0),
                "failure_patterns": type_counts.get("failure_pattern", 0),
                "fix_recipes": type_counts.get("fix_recipe", 0),
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

        except Exception as e:
            print(f"⚠️ 統計情報取得エラー: {e}")
            return {}

    async def search_relevant_knowledge(self, task_type=None, keywords=None):
        """
        タスクタイプとキーワードから類似ナレッジを検索

        Args:
            task_type: タスクの種類（例: "design", "wordpress", "review"）
            keywords: 検索キーワードのリスト

        Returns:
            dict: 最も関連性の高いナレッジ（スコア順）
        """
        if keywords is None:
            keywords = []

        try:
            # knowledge_baseから全データを取得
            all_knowledge = await self.sheets.read_range("knowledge_base", "A2:F1500")

            matches = []
            for row in all_knowledge:
                if not row or len(row) < 3:
                    continue

                # 列の取得
                kb_id = row[0] if len(row) > 0 else ""
                kb_timestamp = row[1] if len(row) > 1 else ""
                kb_type = row[2] if len(row) > 2 else ""
                row[3] if len(row) > 3 else ""
                kb_pattern = row[4] if len(row) > 4 else ""
                kb_context = row[5] if len(row) > 5 else ""

                # スコア計算
                score = 0

                # タスクタイプの一致（重み: 10点）
                if task_type and task_type.lower() in kb_type.lower():
                    score += 10

                # キーワードの一致（各5点）
                for keyword in keywords:
                    if keyword and keyword.lower() in kb_context.lower():
                        score += 5
                    if keyword and keyword.lower() in kb_pattern.lower():
                        score += 3

                if score > 0:
                    matches.append(
                        {
                            "knowledge_id": kb_id,
                            "timestamp": kb_timestamp,
                            "knowledge_type": kb_type,
                            "pattern_name": kb_pattern,
                            "context": kb_context,
                            "score": score,
                        }
                    )

            # スコア順にソート
            matches.sort(key=lambda x: x["score"], reverse=True)

            # 最も関連性の高いものを返す
            if matches:
                print(f"📚 ナレッジ検索: {len(matches)}件ヒット、最高スコア: {matches[0]['score']}")
                return matches[0]
            else:
                print("📚 ナレッジ検索: 該当なし")
                return None

        except Exception as e:
            print(f"⚠️  ナレッジ検索エラー: {e}")
            return None

    async def update(self, patterns):
        """パターンからナレッジを更新"""
        print(f"🧠 ナレッジベース更新: {len(patterns)}個のパターンを処理")

        try:
            if not patterns:
                print("⚠️ 更新するパターンがありません")
                return True

            updated_count = 0
            for pattern in patterns:
                if await self._process_pattern(pattern):
                    updated_count += 1

            print(f"✅ ナレッジベース更新完了: {updated_count}/{len(patterns)}個のパターンを処理")
            return True

        except Exception as e:
            print(f"❌ ナレッジベース更新エラー: {e}")
            return False

    async def _process_pattern(self, pattern):
        """個々のパターンを処理"""
        try:
            pattern_type = pattern.get("type", "unknown")

            if pattern_type == "error":
                return await self._add_error_pattern(pattern)
            elif pattern_type == "success":
                return await self._add_success_pattern(pattern)
            else:
                print(f"⚠️ 未知のパターンタイプ: {pattern_type}")
                return False

        except Exception as e:
            print(f"❌ パターン処理エラー: {e}")
            return False

    async def _add_error_pattern(self, pattern):
        """エラーパターンを追加"""
        try:
            # 簡易的なエラーパターン登録
            error_data = {
                "pattern": pattern.get("pattern", ""),
                "suggested_fix": pattern.get("suggested_fix", ""),
                "frequency": pattern.get("frequency", 1),
                "context": pattern.get("context", {}),
            }

            print(f"📝 エラーパターン登録: {error_data['pattern']}")
            return True

        except Exception as e:
            print(f"❌ エラーパターン追加エラー: {e}")
            return False

    async def _add_success_pattern(self, pattern):
        """成功パターンを追加"""
        try:
            # 簡易的な成功パターン登録
            success_data = {
                "pattern": pattern.get("pattern", ""),
                "best_practice": pattern.get("best_practice", ""),
                "frequency": pattern.get("frequency", 1),
                "context": pattern.get("context", {}),
            }

            print(f"📝 成功パターン登録: {success_data['pattern']}")
            return True

        except Exception as e:
            print(f"❌ 成功パターン追加エラー: {e}")
            return False
