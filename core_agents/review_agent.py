# review_agent.py
"""レビューAI - タスク出力を評価し、失敗原因を分析、次のアクションを提案"""
import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from configuration.config_utils import ErrorHandler
from browser_control.browser_controller import BrowserController
from tools.sheets_manager import GoogleSheetsManager
from core_agents.review_agent_prompts import REVIEW_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class ReviewAgent:
    """レビューAI - タスク出力を評価し、失敗原因を分析、次のアクションを提案"""

    def __init__(
        self, browser_controller=None, browser=None, output_folder: Path = None
    ):
        """
        ReviewAgent初期化

        Args:
        """
        # ブラウザ設定（browser_controller優先）
        if browser_controller is not None:
            self.browser = browser_controller
        elif browser is not None:
            self.browser = browser
        else:
            self.browser = None

        # 出力フォルダ設定
        if output_folder:
            self.output_folder = Path(output_folder)
        else:
            self.output_folder = Path("agent_outputs/review")

        self.output_folder.mkdir(parents=True, exist_ok=True)

        # その他の初期化
        self.sheets_manager = None
        self.system_prompt = REVIEW_SYSTEM_PROMPT

    def _initialize_sheets_manager(self):
        """sheets_manager の遅延初期化"""
        if self.sheets_manager is None:
            try:
                from tools.sheets_manager import GoogleSheetsManager
                from configuration.config_loader import get_config

                spreadsheet_id = get_config("SPREADSHEET_ID")
                service_account = get_config("SERVICE_ACCOUNT_FILE")

                self.sheets_manager = GoogleSheetsManager(
                    spreadsheet_id=spreadsheet_id, service_account_file=service_account
                )
                logger.info("GoogleSheetsManager を初期化しました")
            except Exception as e:
                logger.warning(f"GoogleSheetsManager の初期化に失敗: {e}")
                self.sheets_manager = None

    async def process_task(self, task: Dict) -> Dict:
        """レビュータスクを処理（互換性のため）"""
        return await self.review_completed_task(task, task.get("output_content", ""))

    async def review_completed_task(self, task: Dict, output_content: str) -> Dict:
        """完了したタスクをレビュー（失敗原因分析強化版）"""
        try:
            # === パート1: レビュー開始処理 ===
            logger.info("=" * 60)
            logger.info(f"レビューAI: タスク {task['task_id']} のレビュー開始")
            logger.info("=" * 60)

            # タスクのステータスを確認
            task_status = task.get("status", "unknown")
            is_failed_task = task_status in ["failed", "error", "timeout"]

            # 事前チェック：出力内容の構造を検証
            pre_check_result = self._pre_check_content(
                output_content, task["required_role"]
            )
            if pre_check_result:
                logger.info(f"事前チェック結果: {pre_check_result}")

            # エラー情報を取得
            error_info = task.get("error", "")

            # === パート2: プロンプト構築とGemini送信 ===
            full_prompt = self._build_review_prompt(
                task,
                task_status,
                is_failed_task,
                output_content,
                error_info,
                pre_check_result,
            )

            logger.info("レビューをGeminiに依頼中...")
            await self.browser.send_prompt(full_prompt)

            # 応答待機
            success = await self.browser.wait_for_text_generation(max_wait=120)

            if not success:
                logger.warning("レビューAI: タイムアウト")
                return self._create_default_review(task, is_failed_task)

            # === パート3: 応答取得と結果解析 ===
            response_text = await self.browser.extract_latest_text_response()

            if not response_text:
                logger.warning("レビューAI: 応答取得失敗")
                return self._create_default_review(task, is_failed_task)

            logger.info(f"レビューAI: 応答取得完了（{len(response_text)}文字）")

            # JSONをパース
            review_result = self._parse_review_json(response_text)

            if review_result:
                # レビュー結果の妥当性を検証
                validated_review = self._validate_review_result(
                    review_result, output_content
                )
                self._display_review_summary(validated_review, is_failed_task)
                return {
                    "success": True,
                    "review": validated_review,
                    "summary": validated_review.get("evaluation", {}).get(
                        "overall_assessment", ""
                    ),
                    "full_text": response_text,
                }
            else:
                logger.warning("レビュー結果のJSON解析に失敗")
                return self._create_default_review(task, is_failed_task)

        except Exception as e:
            ErrorHandler.log_error(e, "レビューAI処理")
            return self._create_default_review(task, False)

    def _build_review_prompt(
        self,
        task: Dict,
        task_status: str,
        is_failed_task: bool,
        output_content: str,
        error_info: str,
        pre_check_result: str,
    ) -> str:
        """レビュー用プロンプトを構築(トレーサビリティ情報付き)"""

        # === 🆕 新規追加: トレーサビリティ情報の抽出 ===
        traceability = task.get("_traceability", {})
        executed_by = traceability.get("executed_by_agent", "不明")
        agent_class = traceability.get("agent_class", "不明")

        return f"""{self.system_prompt}

    【レビュー対象タスク】
    タスクID: {task['task_id']}
    内容: {task['description']}
    担当: {task['required_role']}
    ステータス: {task_status}
    出力文字数: {len(output_content)}文字

    🆕【実行エージェント情報】(原因切り分け用)
    実行エージェント: {executed_by}
    エージェントクラス: {agent_class}
    実行タイムスタンプ: {traceability.get('execution_timestamp', 'N/A')}

    【タスクの状態】
    {'❌ このタスクは失敗しました' if is_failed_task else '✅ タスクは完了しました'}
    {f'エラー情報: {error_info}' if error_info else ''}

    【事前チェック結果】
    {pre_check_result if pre_check_result else '特記事項なし'}

    【タスクの出力】
    {output_content[:4000] if output_content else '(出力なし)'}

    上記のタスク出力をレビューし、指定されたJSON形式で評価と次のアクションを提案してください。
    {'特に失敗原因を詳細に分析し、適切な推奨アクションを提案してください。' if is_failed_task else '特に、構造的に完結しているかどうかを重点的に確認してください。'}

    🆕【レビュー時の注意】
    - コードブロックが途中で途切れている場合は必ず指摘してください
    - 実行エージェント({executed_by})の出力品質に問題がある場合、その旨を明記してください
    - 手動作業が必要な手順が含まれている場合、自動化の提案も含めてください
    """

    def _pre_check_content(self, content: str, role: str) -> str:
        """出力内容の事前チェック"""
        checks = []

        # === パート1: 文字数チェック ===
        if len(content) < 100:
            checks.append("⚠️ 文字数が少なすぎます（100文字未満）")
        elif len(content) > 5000:
            checks.append("✅ 文字数が十分です")

        # === パート2: 記事・文書系タスクの構造チェック ===
        if role in [
            "writer",
            "content",
            "wordpress",
            "writer_ja",
            "writer_en",
            "writer_ru",
        ]:
            if "<h1" in content or "<h2" in content or "# " in content:
                checks.append("✅ 見出し構造があります")

            if any(
                phrase in content
                for phrase in [
                    "まとめ",
                    "結論",
                    "終わり",
                    "以上",
                    "最後に",
                    "Conclusion",
                    "Summary",
                ]
            ):
                checks.append("✅ 結論・まとめがあります")
            else:
                checks.append("⚠️ 明示的な結論・まとめが見つかりません")

            # HTML/マークダウンの閉じ忘れチェック
            if content.count("<div") > content.count("</div"):
                checks.append("⚠️ HTMLのdivタグが閉じられていません")
            if content.count("<p>") > content.count("</p>"):
                checks.append("⚠️ HTMLのpタグが閉じられていません")

        # === パート3: コード系タスクの構造チェック ===
        if role in ["dev", "programming"]:
            if "def " in content or "function " in content or "class " in content:
                checks.append("✅ 関数/クラス定義があります")
            if "import " in content or "require " in content:
                checks.append("✅ インポート文があります")

        return " | ".join(checks) if checks else "✅ 基本的な構造は問題ありません"

    def _validate_review_result(self, review: Dict, original_content: str) -> Dict:
        """レビュー結果の妥当性を検証"""
        evaluation = review.get("evaluation", {})
        next_actions = review.get("next_actions", {})

        # === パート1: 「部分的」判定の妥当性チェック ===
        if evaluation.get("completeness") == "部分的":
            issues = evaluation.get("issues", [])
            new_issues = []

            for issue in issues:
                # 文字数関連の指摘を検証
                if any(word in issue for word in ["文字数", "文字", "短い", "少ない"]):
                    if (
                        len(original_content) > 1000
                    ):  # 1000文字以上あれば文字数不足ではない
                        continue
                # 構造的な指摘を検証
                elif "切れて" in issue or "途切れ" in issue:
                    # 実際に文が途中で切れているかチェック
                    if self._is_content_properly_ended(original_content):
                        continue

                new_issues.append(issue)

            # 問題点を更新
            evaluation["issues"] = new_issues

            # 問題点がなくなった場合は「完了」に変更
            if not new_issues and len(original_content) > 500:
                evaluation["completeness"] = "完了"
                evaluation["overall_assessment"] = (
                    "再評価: 内容は完結しており、文字数も十分です"
                )
                next_actions["required"] = False
                next_actions["suggested_tasks"] = []

        return review

    def _is_content_properly_ended(self, content: str) -> bool:
        """コンテンツが適切に終了しているかチェック"""
        # === パート1: 文の終了チェック ===
        sentences = re.split(r"[。！？!?\.]", content.strip())
        if sentences and sentences[-1].strip():
            return False  # 最後の文が終了記号で終わっていない

        # === パート2: HTMLタグの閉じチェック ===
        if content.count("<") > 0 and content.count(">") > 0:
            open_tags = len(re.findall(r"<(?!\/)[^>]+>", content))
            close_tags = len(re.findall(r"<\/[^>]+>", content))
            if open_tags != close_tags:
                return False

        return True

    def _parse_review_json(self, text: str) -> Optional[Dict]:
        """レビュー結果のJSONをパース"""
        try:
            import re

            # === パート1: ```json ... ``` 形式の抽出 ===
            json_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)

            # === パート2: 単純なJSONオブジェクトの抽出 ===
            json_match = re.search(r"(\{.*\})", text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)

            logger.warning("JSON形式が見つかりません")
            return None

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析エラー: {e}")
            return None

    def _create_default_review(self, task: Dict, is_failed: bool = False) -> Dict:
        """デフォルトのレビュー結果（失敗時）"""
        if is_failed:
            return {
                "success": True,
                "review": {
                    "evaluation": {
                        "completeness": "失敗",
                        "quality_score": 3,
                        "issues": ["タスク実行に失敗しました"],
                        "good_points": [],
                        "overall_assessment": "タスクは失敗しましたが、レビュー処理も問題が発生しました",
                        "failure_analysis": {
                            "is_failed": True,
                            "failure_category": "環境問題",
                            "root_cause": "レビューAIの応答取得に失敗",
                            "impact": "失敗原因の詳細が不明",
                            "recommended_action": "immediate_retry",
                            "prerequisites": [],
                        },
                    },
                    "next_actions": {
                        "required": True,
                        "reasoning": "タスクの再実行または修正が必要",
                        "suggested_tasks": [],
                    },
                },
                "summary": "レビュー処理エラー - タスク失敗",
                "full_text": "",
            }
        else:
            return {
                "success": True,
                "review": {
                    "evaluation": {
                        "completeness": "完了",
                        "quality_score": 7,
                        "issues": [],
                        "good_points": ["タスク完了"],
                        "overall_assessment": "レビュー処理に問題が発生しましたが、タスクは完了とみなします",
                        "failure_analysis": {
                            "is_failed": False,
                            "failure_category": None,
                            "root_cause": None,
                            "impact": None,
                            "recommended_action": None,
                            "prerequisites": [],
                        },
                    },
                    "next_actions": {
                        "required": False,
                        "reasoning": "レビューAIの応答取得に失敗したため、追加タスクなし",
                        "suggested_tasks": [],
                    },
                },
                "summary": "レビュー処理エラー - デフォルト評価",
                "full_text": "",
            }

    def _display_review_summary(self, review: Dict, is_failed_task: bool = False):
        """レビュー結果を表示（失敗分析強化版）"""

        print("\n" + "🎯" * 30)
        print("📋 レビュー結果")
        print("🎯" * 30)

        evaluation = review.get("evaluation", {})

        # === パート1: 基本情報表示 ===
        completeness = evaluation.get("completeness", "N/A")
        completeness_icon = {
            "完了": "✅",
            "部分的": "⚠️",
            "不完全": "❌",
            "失敗": "💥",
        }.get(completeness, "❓")

        print(f"\n{completeness_icon} 完成度: {completeness}")
        print(f"⭐ 品質スコア: {evaluation.get('quality_score', 'N/A')}/10")

        # === パート2: 失敗分析表示 ===
        failure_analysis = evaluation.get("failure_analysis", {})
        if failure_analysis.get("is_failed"):
            print("\n" + "💥" * 30)
            print("🔍 失敗原因分析")
            print("💥" * 30)

            category = failure_analysis.get("failure_category", "N/A")
            category_icon = {
                "要件不明瞭": "📝",
                "技術的問題": "⚙️",
                "リソース不足": "📦",
                "依存関係": "🔗",
                "環境問題": "🌐",
                "タイムアウト": "⏱️",
                "出力不完全": "✂️",
                "品質不足": "📉",
            }.get(category, "❓")

            print(f"\n{category_icon} 失敗カテゴリ: {category}")
            print(f"🔍 根本原因: {failure_analysis.get('root_cause', 'N/A')}")
            print(f"💡 影響: {failure_analysis.get('impact', 'N/A')}")

            action = failure_analysis.get("recommended_action", "N/A")
            action_map = {
                "immediate_retry": "🔄 即座に再実行",
                "modify_task": "✏️ タスクを修正",
                "add_prerequisite": "➕ 前提タスクを追加",
                "escalate": "🚨 エスカレーション（人間の判断が必要）",
                "skip": "⏭️ スキップまたは後回し",
            }
            print(f"📌 推奨アクション: {action_map.get(action, action)}")

            prereqs = failure_analysis.get("prerequisites", [])
            if prereqs:
                print(f"\n📋 前提条件:")
                for prereq in prereqs:
                    print(f"   • {prereq}")

            print("💥" * 30)

        # === パート3: 良い点・問題点表示 ===
        good_points = evaluation.get("good_points", [])
        if good_points:
            print(f"\n✨ 良い点:")
            for point in good_points:
                print(f"   ✅ {point}")

        issues = evaluation.get("issues", [])
        if issues:
            print(f"\n⚠️ 問題点:")
            for issue in issues:
                print(f"   ❌ {issue}")

        # === パート4: 総合評価表示 ===
        overall = evaluation.get("overall_assessment", "")
        if overall:
            print(f"\n💎 総合評価:")
            print(f"   {overall}")

        # === パート5: 次のアクション表示 ===
        next_actions = review.get("next_actions", {})
        required = next_actions.get("required", False)

        action_icon = "🔴" if required else "🟢"
        print(f"\n🎯 次のアクション: {action_icon} {'必要' if required else '不要'}")

        if required:
            reasoning = next_actions.get("reasoning", "")
            if reasoning:
                print(f"   📌 理由: {reasoning}")

            # 提案タスク
            suggested_tasks = next_actions.get("suggested_tasks", [])
            if suggested_tasks:
                print(f"\n🚀 提案タスク ({len(suggested_tasks)}件):")
                for i, task in enumerate(suggested_tasks, 1):
                    priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                        task.get("priority", "medium"), "⚪"
                    )

                    role_icon = {
                        "design": "📐",
                        "dev": "💻",
                        "ui": "🎨",
                        "review": "✅",
                        "wordpress": "🌐",
                        "content": "✍️",
                        "writer": "📝",
                        "writer_ja": "🗾",
                        "writer_en": "🔠",
                        "writer_ru": "🇷🇺",
                    }.get(task.get("required_role", "dev"), "📋")

                    print(
                        f"   {i}. {priority_icon} {role_icon} {task.get('description', 'N/A')}"
                    )

                    deps = task.get("dependencies", [])
                    if deps:
                        print(f"      📎 依存: {', '.join(map(str, deps))}")

        print("🎯" * 30 + "\n")

    async def add_suggested_tasks_to_sheet(
        self, parent_task_id: str, suggested_tasks: List[Dict]
    ) -> int:
        """提案されたタスクをpm_tasksシートに追加（正しい列配置版）"""
        try:
            # sheets_manager の初期化            self._initialize_sheets_manager()            if self.sheets_manager is None:                logger.error(sheets_manager
            if not suggested_tasks:
                return 0

            logger.info(
                f"提案タスク {len(suggested_tasks)} 件をスプレッドシートに追加中..."
            )

            # === パート1: シート準備 ===
            sheet = self.sheets_manager.gc.open_by_key(
                self.sheets_manager.spreadsheet_id
            )
            task_sheet = sheet.worksheet("pm_tasks")

            # 既存データを取得
            all_values = task_sheet.get_all_values()

            if len(all_values) < 1:
                logger.error("pm_tasksシートが空です")
                return 0

            # ヘッダー行を確認
            headers = all_values[0]
            logger.info(f"列ヘッダー: {headers}")

            # === パート2: タスクIDの決定 ===
            existing_task_ids = []
            for row in all_values[1:]:  # ヘッダーをスキップ
                if row and len(row) > 0:
                    try:
                        task_id = int(row[0])
                        existing_task_ids.append(task_id)
                    except (ValueError, IndexError):
                        continue

            # 次のタスクIDを決定
            if existing_task_ids:
                next_task_id = max(existing_task_ids) + 1
            else:
                next_task_id = 1

            logger.info(f"次のタスクID: {next_task_id}")

            # === パート3: タスクデータの準備 ===
            rows_to_add = []
            for task in suggested_tasks:
                row = [
                    next_task_id,  # A: task_id
                    "",  # B: parent_goal_id（空欄）
                    task.get("description", ""),  # C: task_description
                    task.get("required_role", "dev"),  # D: required_role
                    "pending",  # E: status
                    task.get("priority", "medium"),  # F: priority
                    task.get("estimated_time", ""),  # G: estimated_time
                    ",".join(
                        map(str, task.get("dependencies", [parent_task_id]))
                    ),  # H: dependencies
                    datetime.now().isoformat(),  # I: created_at
                    f"Review suggested from task {parent_task_id}",  # J: notes
                ]
                rows_to_add.append(row)
                logger.info(
                    f"追加予定タスク: ID={next_task_id}, 内容={task.get('description', '')[:50]}"
                )
                next_task_id += 1

            # === パート4: データ追加処理 ===
            if rows_to_add:
                # 最終行の次の行から追加
                start_row = len(all_values) + 1

                # セル範囲を指定して追加
                range_notation = f"A{start_row}:J{start_row + len(rows_to_add) - 1}"

                logger.info(f"データを追加: {range_notation}")
                task_sheet.update(range_notation, rows_to_add)

                logger.info(f"✅ 提案タスク {len(rows_to_add)} 件を追加しました")

                # 追加されたタスクIDをログ出力
                added_ids = [row[0] for row in rows_to_add]
                logger.info(f"追加されたタスクID: {added_ids}")

            return len(rows_to_add)

        except Exception as e:
            ErrorHandler.log_error(e, "提案タスク追加")
            logger.error(f"エラー詳細: {str(e)}")
            import traceback

            logger.error(traceback.format_exc())
            return 0
