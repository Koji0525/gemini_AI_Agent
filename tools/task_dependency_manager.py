"""
タスク依存関係マネージャー v2 - 柔軟実行方式
Phase 2: タスク連携機能の中核

特徴:
- 依存タスクに問題があっても実行継続
- 削除済みタスクは無視
- 未完了タスクは無視
- 品質の高い結果（≧7）だけを活用
- すべての問題は警告として記録
"""

import logging
from typing import List, Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class TaskDependencyManager:
    """
    柔軟な依存関係管理
    運用ルール4.7準拠: 依存関係の判断とデータ取得のみに特化
    """

    def __init__(self, sheets_manager):
        """
        Args:
            sheets_manager: Google Sheets操作用マネージャー（外部から注入）
        """
        self.sheets_manager = sheets_manager

    def parse_dependencies(self, dependencies_str: str) -> List[str]:
        """
        Dependencies列の文字列を解析してTaskIDリストに変換

        Args:
            dependencies_str: "1,2,3" または "4, 6" のような文字列

        Returns:
            ["1", "2", "3"] のようなリスト
        """
        if not dependencies_str or dependencies_str.strip() == "":
            return []

        # カンマで分割して空白を削除
        task_ids = [tid.strip() for tid in dependencies_str.split(",")]
        # 空文字列を除外
        task_ids = [tid for tid in task_ids if tid]

        logger.info(f"📋 依存関係解析: '{dependencies_str}' → {task_ids}")
        return task_ids

    async def check_and_get_dependencies(
        self, task_id: str, dependencies: List[str], min_quality_score: float = 7.0
    ) -> Dict[str, Any]:
        """
        依存関係をチェックし、利用可能な結果を取得（柔軟実行方式）

        Args:
            task_id: チェック対象のタスクID
            dependencies: 依存タスクIDのリスト
            min_quality_score: 最低品質スコア（デフォルト: 7.0）

        Returns:
            {
                "can_execute": True,  # 常にTrue（柔軟実行）
                "context_tasks": {    # コンテキストに含める結果
                    "4": {
                        "output": "タスク4の結果...",
                        "quality_score": 9.0,
                        "agent": "design"
                    }
                },
                "warnings": [         # 警告リスト
                    "TaskID=102は削除済みまたは存在しません",
                    "TaskID=9は未完了です"
                ],
                "summary": "4件中2件の依存タスク結果を取得"
            }
        """
        if not dependencies:
            logger.info(f"✅ TaskID={task_id}: 依存タスクなし")
            return {
                "can_execute": True,
                "context_tasks": {},
                "warnings": [],
                "summary": "依存タスクなし",
            }

        logger.info(f"🔍 TaskID={task_id}: 依存タスク {dependencies} をチェック中...")

        context_tasks = {}
        warnings = []

        try:
            # === Level 1: pm_tasksから全タスクを読み込む ===
            all_tasks = await self.sheets_manager.load_tasks_from_sheet("pm_tasks")
            task_map = {str(t.get("task_id", "")): t for t in all_tasks}

            # === Level 2 & 3: 各依存タスクをチェック ===
            for dep_id in dependencies:
                # Level 1: 存在チェック
                if dep_id not in task_map:
                    warning = f"TaskID={dep_id}は削除済みまたは存在しません"
                    warnings.append(warning)
                    logger.warning(f"⚠️ {warning}")
                    continue

                dep_task = task_map[dep_id]
                status = dep_task.get("status", "").lower()

                # Level 2: ステータスチェック
                if status != "completed":
                    warning = f"TaskID={dep_id}は未完了です（Status: {status}）"
                    warnings.append(warning)
                    logger.warning(f"⚠️ {warning}")
                    continue

                # Level 3: 品質チェックと結果取得
                try:
                    result = await self._get_task_result(dep_id, min_quality_score)

                    if result:
                        context_tasks[dep_id] = result
                        logger.info(
                            f"✅ TaskID={dep_id}: 結果取得成功（品質: {result['quality_score']}/10）"
                        )
                    else:
                        warning = f"TaskID={dep_id}は品質スコア<{min_quality_score}のため除外"
                        warnings.append(warning)
                        logger.warning(f"⚠️ {warning}")

                except Exception as e:
                    warning = f"TaskID={dep_id}の結果取得エラー: {str(e)}"
                    warnings.append(warning)
                    logger.error(f"❌ {warning}")

            # === サマリー作成 ===
            total = len(dependencies)
            success = len(context_tasks)
            summary = f"{total}件中{success}件の依存タスク結果を取得"

            if context_tasks:
                logger.info(f"✅ {summary}")
            else:
                logger.warning(
                    f"⚠️ 依存タスクの結果が取得できませんでした。コンテキストなしで実行します。"
                )

            return {
                "can_execute": True,  # 常にTrue（柔軟実行）
                "context_tasks": context_tasks,
                "warnings": warnings,
                "summary": summary,
            }

        except Exception as e:
            logger.error(f"❌ 依存関係チェックエラー: {e}")
            return {
                "can_execute": True,  # エラーでも実行継続
                "context_tasks": {},
                "warnings": [f"依存関係チェック中にエラー: {str(e)}"],
                "summary": "エラーのためコンテキストなしで実行",
            }

    async def _get_task_result(
        self, task_id: str, min_quality_score: float
    ) -> Optional[Dict[str, Any]]:
        """
        task_execution_logから指定タスクの結果を取得（品質フィルタ付き）
        GitHubファイルからの完全版取得もサポート

        Args:
            task_id: タスクID
            min_quality_score: 最低品質スコア

        Returns:
            {
                "output": "タスクの出力...",
                "quality_score": 9.0,
                "agent": "design",
                "execution_type": "gemini"
            }
            品質スコアが低い場合はNone
        """
        try:
            self.sheets_manager._ensure_client()
            sheet = self.sheets_manager.gc.open_by_key(self.sheets_manager.spreadsheet_id)
            log_sheet = sheet.worksheet("task_execution_log")

            all_data = log_sheet.get_all_values()

            if len(all_data) <= 1:
                return None

            headers = all_data[0]

            # 該当タスクの最新ログを検索（逆順）
            matching_row = None
            for row in reversed(all_data[1:]):
                if len(row) > 1 and str(row[1]).strip() == str(task_id):
                    matching_row = row
                    break

            if not matching_row:
                logger.warning(f"⚠️ TaskID={task_id}のログが見つかりません")
                return None

            # 品質スコアを取得（I列 = index 8）
            quality_score_str = matching_row[8].strip() if len(matching_row) > 8 else "0"
            try:
                quality_score = float(quality_score_str) if quality_score_str else 0.0
            except ValueError:
                quality_score = 0.0

            # 品質スコアでフィルタ
            if quality_score < min_quality_score:
                logger.info(f"⚠️ TaskID={task_id}: 品質スコア {quality_score} < {min_quality_score}")
                return None

            # Output列を取得（G列 = index 6）
            output = matching_row[6] if len(matching_row) > 6 else ""

            # GitHubファイルへの参照がある場合、完全版を取得
            if "[GitHub]" in output:
                output = await self._get_github_output(output) or output

            return {
                "output": output,
                "quality_score": quality_score,
                "agent": matching_row[4] if len(matching_row) > 4 else "",  # E列
                "execution_type": matching_row[5] if len(matching_row) > 5 else "",  # F列
            }

        except Exception as e:
            logger.error(f"❌ TaskID={task_id}の結果取得エラー: {e}")
            return None

    async def _get_github_output(self, output_with_link: str) -> Optional[str]:
        """
        GitHub参照リンクから完全な出力を取得

        Args:
            output_with_link: "[GitHub] agent_outputs/..." を含む文字列

        Returns:
            ファイルの完全な内容、またはNone
        """
        try:
            # GitHubパスを抽出
            github_path = None
            for line in output_with_link.split("\n"):
                if "[GitHub]" in line:
                    github_path = line.replace("[GitHub]", "").strip()
                    break

            if not github_path:
                return None

            # ファイルを読み込み
            full_path = Path(github_path)
            if full_path.exists():
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                logger.info(f"📥 GitHubから完全版を取得: {github_path} ({len(content)}文字)")
                return content
            else:
                logger.warning(f"⚠️ GitHubファイルが見つかりません: {github_path}")
                return None

        except Exception as e:
            logger.error(f"❌ GitHub出力取得エラー: {e}")
            return None

    def build_context_prompt(
        self,
        base_prompt: str,
        context_tasks: Dict[str, Dict[str, Any]],
        max_context_length: int = 3000,
    ) -> str:
        """
        依存タスクの結果を含むコンテキスト付きプロンプトを生成

        Args:
            base_prompt: 元のタスク説明
            context_tasks: check_and_get_dependencies()の"context_tasks"
            max_context_length: 各タスクの出力の最大長（デフォルト: 3000文字）

        Returns:
            コンテキスト付きプロンプト
        """
        if not context_tasks:
            return base_prompt

        # コンテキスト部分を構築
        context_parts = ["=" * 70]
        context_parts.append("【前タスクの結果（参考情報）】")
        context_parts.append("=" * 70)

        for task_id, result in sorted(context_tasks.items()):
            quality = result["quality_score"]
            output = result["output"]
            agent = result.get("agent", "N/A")

            # 長い出力は省略
            if len(output) > max_context_length:
                output = output[:max_context_length] + f"\n\n...(省略: 全{len(output)}文字)"

            context_parts.append(f"\n--- TaskID={task_id} の結果 ---")
            context_parts.append(f"担当Agent: {agent}")
            context_parts.append(f"品質スコア: {quality}/10")
            context_parts.append("-" * 70)
            context_parts.append(output)
            context_parts.append("")

        context_parts.append("=" * 70)
        context_parts.append("【今回のタスク】")
        context_parts.append("=" * 70)
        context_parts.append(base_prompt)

        enhanced_prompt = "\n".join(context_parts)

        logger.info(
            f"✅ コンテキスト付きプロンプト生成完了"
            f"（{len(context_tasks)}件の前タスク結果を含む）"
        )

        return enhanced_prompt

    def get_execution_order(self, tasks: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        タスクを依存関係に基づいてグループ化

        Returns:
            実行順序のグループリスト
            例: [[task1, task2], [task3], [task4, task5]]
                 → グループ1とグループ2は並列実行可能
        """
        if not tasks:
            return []

        # 簡易版: 依存関係がないタスクから順に実行
        # TODO: 本格的な依存解決は後日実装

        # 依存関係を持たないタスク
        no_deps = [t for t in tasks if not t.get("dependencies") or t.get("dependencies") == ""]

        # 依存関係を持つタスク
        with_deps = [t for t in tasks if t.get("dependencies") and t.get("dependencies") != ""]

        # 現時点では2グループに分割（シンプル版）
        execution_groups = []
        if no_deps:
            execution_groups.append(no_deps)
        if with_deps:
            execution_groups.append(with_deps)

        return execution_groups
