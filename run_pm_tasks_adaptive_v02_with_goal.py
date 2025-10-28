"""
完全修正版pm_tasks処理システム - ステータス管理統合版
- BrowserController対応
- ログ記録（品質スコア）
- レビュー機能
- ステータス自動更新（pending→in_progress→completed/failed）
"""

import asyncio
import sys
import argparse
from pathlib import Path
from datetime import datetime

from typing import Optional, Dict, Any, List
from tools.task_dependency_manager import TaskDependencyManager

sys.path.insert(0, str(Path(__file__).parent))


def determine_execution_type(task: dict) -> str:
    """
    改善版：タスクの実行タイプを判定

    優先順位:
    1. ExecutionType列が設定されている → それを使用
    2. プレフィックス判定（【WP】【設計】など）
    3. 動詞パターン認識
    4. キーワードマッチ（従来方式）
    """
    # 1. ExecutionType列（最優先）
    exec_type = task.get("ExecutionType", "").lower()
    if exec_type in ["wordpress", "gemini"]:
        return exec_type

    description = task.get("Description", "") + " " + task.get("Title", "")

    # 2. プレフィックス判定
    if any(prefix in description for prefix in ["【WP", "【ワードプレス", "【WordPress"]):
        return "wordpress"
    if any(prefix in description for prefix in ["【設計】", "【分析】", "【調査】", "【計画】"]):
        return "gemini"

    # 3. 動詞パターン認識（WordPress操作を示す動詞）
    wp_action_verbs = [
        "設定",
        "実装",
        "追加",
        "変更",
        "修正",
        "更新",
        "インストール",
        "有効化",
        "無効化",
        "削除",
        "作成する（WordPress",
        "登録する",
        "公開する",
    ]

    gemini_action_verbs = [
        "設計書",
        "仕様書",
        "要件定義",
        "分析レポート",
        "提案書",
        "まとめ",
        "調査",
        "比較",
        "作成して（ください）",
        "書いて",
        "考えて",
    ]

    # WordPress動詞チェック
    for verb in wp_action_verbs:
        if verb in description:
            # さらにWordPressキーワードがあるか確認
            wp_keywords = [
                "WordPress",
                "wp-",
                "functions.php",
                "プラグイン",
                "ACF",
                "CPT",
                "カスタム投稿",
                "カスタムフィールド",
            ]
            if any(kw in description for kw in wp_keywords):
                return "wordpress"

    # Gemini動詞チェック
    for verb in gemini_action_verbs:
        if verb in description:
            return "gemini"

    # 4. 従来のキーワードマッチ（フォールバック）
    wp_keywords_strong = [
        "function.php",
        "functions.php",
        "プラグイン設定",
        "プラグインをインストール",
        "wp-admin",
        "WordPress管理画面",
    ]

    for keyword in wp_keywords_strong:
        if keyword.lower() in description.lower():
            return "wordpress"

    # デフォルトはGemini
    return "gemini"


def has_wordpress_tasks(tasks: list) -> bool:
    """タスクリストにWordPress系タスクが含まれているか確認"""
    return any(determine_execution_type(task) == "wordpress" for task in tasks)


async def initialize_wordpress_session(browser):
    """WordPress セッションを初期化"""
    try:
        from browser_control.browser_wp_session_manager import WPSessionManager
        from wordpress.wp_auth import WordPressAuth
        from configuration.config_loader import get_config, config

        print("🌐 WordPress セッション初期化中...")

        # WordPress設定を取得
        wp_url = get_config("WP_URL")
        wp_user = get_config("WP_USER")
        wp_pass = get_config("WP_PASS")

        # WPSessionManagerを初期化
        wp_cookies_file = Path("wordpress_cookies.json")
        wp_session = WPSessionManager(browser.context, wp_cookies_file)

        # WordPress認証モジュール
        wp_auth = WordPressAuth(browser, wp_url, wp_user, wp_pass)

        # セッション初期化
        success = await wp_session.initialize_wp_session(auth_module=wp_auth)

        if success:
            print("✅ WordPress セッション初期化成功")
            return wp_session
        else:
            print("⚠️ WordPress セッション初期化失敗")
            return None

    except Exception as e:
        print(f"❌ WordPress 初期化エラー: {e}")
        import traceback

        traceback.print_exc()
        return None


async def execute_wordpress_task(task, wp_session):
    """
    WordPressタスクを実行

    Args:
        task: タスク辞書
        wp_session: WPSessionManager インスタンス

    Returns:
        str: 実行結果（テキスト）
    """
    try:
        print()
        print("🌐 WordPressタスク実行中...")

        if not wp_session or not wp_session.wp_page:
            return "❌ WordPressセッションが初期化されていません"

        # タスクの説明から何をするか判定
        description = task.get("Description", "") + task.get("Title", "")

        # CPT作成タスク
        if "Custom Post Type" in description or "CPT" in description or "カスタム投稿タイプ" in description:
            from wordpress.wp_dev.wp_cpt_agent import WordPressCPTAgent

            cpt_agent = WordPressCPTAgent(wp_session.wp_page, output_folder="agent_outputs/wordpress")

            print("📝 CPT作成エージェントを実行中...")
            result = await cpt_agent.execute({"task_id": task.get("task_id"), "description": description})
            return result

        # ACF設定タスク
        elif "ACF" in description or "Advanced Custom Fields" in description:
            from wordpress.wp_dev.wp_acf_agent import WordPressACFAgent

            acf_agent = WordPressACFAgent(wp_session.wp_page, output_folder="agent_outputs/wordpress")

            print("📝 ACF設定エージェントを実行中...")
            result = await acf_agent.execute({"task_id": task.get("task_id"), "description": description})
            return result

        # 一般的なWordPressタスク
        else:
            from wordpress.wp_dev.wp_dev_agent import WordPressDevAgent

            wp_dev = WordPressDevAgent(wp_session.wp_page)

            print("📝 WordPress Dev エージェントを実行中...")
            task_result = await wp_dev.execute(task)
            return task_result.get("output", "タスク実行完了")

    except Exception as e:
        error_msg = f"❌ WordPressタスク実行エラー: {e}"
        print(error_msg)
        import traceback

        traceback.print_exc()
        return error_msg


async def log_to_sheet(
    task_id,
    task_description,
    agent_role,
    output_summary,
    output_file_path,
    status="completed",
    quality_score=None,
    quality_description=None,
):
    """task_execution_logシートにログを記録（品質スコア対応）"""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        from configuration.config_loader import get_config, config

        creds = Credentials.from_service_account_file(
            "configuration/service_account.json",
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(get_config("SPREADSHEET_ID"))
        log_sheet = spreadsheet.worksheet("task_execution_log")

        # 最新のlog_idを取得
        all_values = log_sheet.get_all_values()
        if len(all_values) > 1:
            last_log_id = int(all_values[-1][0]) if all_values[-1][0] else 0
        else:
            last_log_id = 0

        new_log_id = last_log_id + 1
        timestamp = datetime.now().isoformat()

        # 新しい行を追加
        new_row = [
            new_log_id,
            task_id,
            task_description,
            timestamp,
            agent_role,
            output_summary,
            str(output_file_path),
            status,
            quality_score if quality_score else "",
            quality_description if quality_description else "",
            "",
        ]

        log_sheet.append_row(new_row)
        print(f"✅ ログをシートに記録: log_id={new_log_id}")
        if quality_score:
            pass  # 品質スコア表示は review_agent.py に任せる
        return True

    except Exception as e:
        print(f"⚠️ ログ記録エラー: {e}")
        return False


async def main():
    """メイン実行関数"""
    try:
        from configuration.config_loader import get_config, config

        # config変数はそのまま使用可能

        print("============================================================")
        print("🚀 pm_tasks処理システム - ステータス管理統合版")
        print("============================================================")

        from browser_control.browser_controller import BrowserController
        from tools.pm_tasks_loader import PMTasksLoader
        from core_agents.review_agent import ReviewAgent

        print("🔄 コンポーネント初期化中...")

        tasks_loader = PMTasksLoader()
        print("✅ PMTasksLoader初期化成功")

        # Phase 2: TaskDependencyManager初期化
        from tools.sheets_manager import GoogleSheetsManager as SheetsManager

        sheets_manager = SheetsManager(
            spreadsheet_id=config.get("SPREADSHEET_ID"), service_account_file=config.get("SERVICE_ACCOUNT_FILE")
        )
        dependency_manager = TaskDependencyManager(sheets_manager)
        print("✅ TaskDependencyManager初期化完了")

        parser = argparse.ArgumentParser()
        parser.add_argument("--max-tasks", type=int, default=1, help="処理する最大タスク数")
        parser.add_argument(
            "--status",
            type=str,
            default="pending",
            help="ステータスフィルター（デフォルト: pending）",
        )
        parser.add_argument("--skip-review", action="store_true", help="レビューをスキップ")
        parser.add_argument("--dry-run", action="store_true", help="実際には実行せず、処理内容のみ表示")
        parser.add_argument("--goal-id", type=str, help="特定のゴールIDのタスクのみ実行")
        args = parser.parse_args()

        print(f"🔄 タスク読み込み中（最大{args.max_tasks}タスク、ステータス: {args.status}）...")
        tasks = tasks_loader.load_tasks(max_tasks=args.max_tasks, status_filter=args.status)

        # goal-idフィルタ
        if args.goal_id:
            tasks = [t for t in tasks if str(t.get("parent_goal_id", "")) == str(args.goal_id)]
            print(f"🎯 目標{args.goal_id}のタスクに絞り込み: {len(tasks)}件")

        if not tasks:
            print(f"⚠️ ステータス '{args.status}' のタスクがありません")
            return

        print(f"✅ タスク読み込み成功: {len(tasks)} タスク")
        print()

        async with BrowserController(download_folder="./downloads") as browser:
            print("✅ BrowserController初期化完了")

            # レビューエージェント初期化
            review_agent = ReviewAgent(browser_controller=browser)
            print("✅ ReviewAgent初期化完了")

            print("�� Geminiに接続中...")
            logged_in = await browser.navigate_to_gemini()

            # === WordPress セッション初期化（必要な場合のみ）===
            wp_session = None
            if has_wordpress_tasks(tasks):
                print()
                print("=" * 70)
                print("🌐 WordPress タスクが検出されました")
                print("=" * 70)
                wp_session = await initialize_wordpress_session(browser)
                if not wp_session:
                    print("⚠️ WordPress セッション初期化失敗")
                    print("   WordPress系タスクは実行できません")
                print()

            if not logged_in:
                print("❌ Gemini接続失敗")
                return

            print("✅ Gemini接続成功")
            print()

            for idx, task in enumerate(tasks, 1):
                print("=" * 70)
                print(f"📝 タスク {idx}/{len(tasks)}")
                print("=" * 70)
                task_id = task.get("TaskID", f"task_{idx}")
                print(f"  TaskID     : {task_id}")
                print(f"  Agent      : {task.get('Agent', 'N/A')}")
                print(f"  Status     : {task.get('Status', 'N/A')}")
                print(f"  Title      : {task.get('Title', 'N/A')[:80]}")
                print(f"  Dependencies: {task.get('Dependencies', 'なし')}")

                # ============================================================
                # Phase 2: 依存関係チェックと前タスク結果の取得
                # ============================================================
                dependencies_str = task.get("Dependencies", "")
                dependencies = dependency_manager.parse_dependencies(dependencies_str)

                dep_result = await dependency_manager.check_and_get_dependencies(
                    task_id=task_id, dependencies=dependencies, min_quality_score=7.0
                )

                # 警告がある場合は表示
                if dep_result["warnings"]:
                    print()
                    print("⚠️ 依存関係の警告:")
                    for warning in dep_result["warnings"]:
                        print(f"   - {warning}")

                # サマリー表示
                print(f"📊 依存関係: {dep_result['summary']}")
                print()
                # ============================================================

                # === 実行タイプ判定 ===
                execution_type = determine_execution_type(task)
                print(f"  ExecutionType: {execution_type}")
                print()
                print()

                # ステータスを in_progress に更新
                print(f"🔄 ステータスを in_progress に更新中...")
                tasks_loader.update_task_status(task_id, "in_progress")

                agent_role = task.get("Agent", "general")

                if agent_role == "design":
                    role_instruction = (
                        "あなたは設計専門のエージェントです。技術選定、アーキテクチャ設計、要件定義を担当します。"
                    )
                elif agent_role == "dev":
                    role_instruction = "あなたは開発専門のエージェントです。コード実装、テスト、デプロイを担当します。"
                elif agent_role == "review":
                    role_instruction = "あなたはレビュー専門のエージェントです。品質チェック、改善提案を担当します。"
                elif agent_role == "ui":
                    role_instruction = (
                        "あなたはUI/UX専門のエージェントです。ワイヤーフレーム作成、デザイン仕様を担当します。"
                    )
                else:
                    role_instruction = "あなたは汎用エージェントです。"

                prompt_base = f"""
{role_instruction}

【タスクID】
{task_id}

【タスク内容】
{task.get('Title', '')}

【詳細説明】
{task.get('Description', task.get('Title', ''))}

【依存タスク】
{task.get('Dependencies', 'なし')}

【指示】
上記のタスクを実行し、具体的で実用的な成果物を出力してください。
- 設計タスクの場合: 設計書や仕様書の形式で
- 開発タスクの場合: コードや実装手順で
- レビュータスクの場合: チェック結果と改善提案で

出力は構造化され、実務で使える形式にしてください。
"""

                # Phase 2: コンテキスト付きプロンプト生成
                if dep_result["context_tasks"]:
                    prompt = dependency_manager.build_context_prompt(
                        base_prompt=prompt_base, context_tasks=dep_result["context_tasks"], max_context_length=3000
                    )
                    print("✅ コンテキスト付きプロンプトで実行")
                else:
                    prompt = prompt_base
                    print("ℹ️ コンテキストなしで実行")

                # === ルーティング分岐 ===
                if execution_type == "wordpress":
                    # WordPress処理
                    print("🌐 WordPress タスクとして実行します")
                    try:
                        if wp_session:
                            response = await execute_wordpress_task(task, wp_session)
                            task_success = bool(response and "❌" not in response)
                        else:
                            error_message = "WordPressセッションが初期化されていません"
                            raise Exception(error_message)
                    except Exception as e:
                        print(f"❌ WordPressタスク実行エラー: {e}")
                        error_message = str(e)
                        task_success = False

                else:
                    # Gemini処理（既存コード）
                    print("🤖 Gemini タスクとして実行します")
                task_success = False
                response = None
                error_message = None

                try:
                    print("💬 タスク実行中...")
                    await browser.send_prompt(prompt)

                    print("⏳ レスポンス生成待機中（最大60秒）...")
                    generation_success = await browser.wait_for_text_generation(max_wait=60)

                    if not generation_success:
                        print("⚠️ レスポンス生成タイムアウト")
                        error_message = "Response generation timeout"
                        raise Exception(error_message)

                    print("📥 レスポンス取得中...")
                    response = await browser.extract_latest_text_response()

                    if response:
                        print(f"✅ レスポンス取得成功: {len(response)}文字")
                        task_success = True
                    else:
                        print("❌ レスポンス取得失敗")
                        error_message = "Failed to extract response"
                        raise Exception(error_message)

                except Exception as e:
                    print(f"❌ タスク実行エラー: {e}")
                    error_message = str(e)
                    task_success = False

                # ステータス更新
                final_status = "completed" if task_success else "failed"
                print(f"🔄 ステータスを {final_status} に更新中...")
                tasks_loader.update_task_status(task_id, final_status)

                if task_success and response:
                    print()
                    print("📄 レスポンス（最初の300文字）:")
                    print("-" * 70)
                    print(response[:300] + "..." if len(response) > 300 else response)
                    print("-" * 70)
                    print()

                    # 結果を保存
                    output_dir = Path("agent_outputs/tasks")
                    output_dir.mkdir(parents=True, exist_ok=True)

                    output_file = output_dir / f"task_{task_id}_{agent_role}_output.txt"

                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(f"タスクID: {task_id}\n")
                        f.write(f"担当エージェント: {agent_role}\n")
                        f.write(f"タスク内容: {task.get('Title', '')}\n")
                        f.write(f"\n{'='*70}\n")
                        f.write(f"実行結果:\n")
                        f.write(f"{'='*70}\n\n")
                        f.write(response)

                    print(f"💾 出力を保存: {output_file}")

                    # レビュー実行
                    quality_score = None
                    quality_description = None

                    if not args.skip_review:
                        print()
                        print("=" * 70)
                        print("🔍 レビュー実行中...")
                        print("=" * 70)

                        review_task = {
                            "task_id": task_id,
                            "description": task.get("Description", task.get("Title", "")),
                            "required_role": agent_role,
                            "status": final_status,
                        }

                        review_result = await review_agent.review_completed_task(review_task, response)

                        if review_result.get("success"):
                            review_data = review_result.get("review", {})
                            evaluation = review_data.get("evaluation", {})

                            if "quality_score" in evaluation:
                                quality_score = evaluation["quality_score"]
                            elif "overall_score" in evaluation:
                                quality_score = evaluation["overall_score"]

                            quality_description = evaluation.get("overall_assessment", review_result.get("summary", ""))

                            print(f"✅ レビュー完了")
                            if quality_score:
                                pass  # 品質スコア表示は review_agent.py に任せる
                            if quality_description:
                                preview = (
                                    quality_description[:100] + "..."
                                    if len(quality_description) > 100
                                    else quality_description
                                )
                                print(f"   評価: {preview}")
                        else:
                            print("⚠️ レビュー実行に失敗しました")

                    # ログをシートに記録
                    print()
                    print("📝 実行ログをシートに記録中...")
                    task_description = task.get("Description", task.get("Title", ""))
                    output_summary = response[:200] + "..." if len(response) > 200 else response

                    await log_to_sheet(
                        task_id=task_id,
                        task_description=task_description,
                        agent_role=agent_role,
                        output_summary=output_summary,
                        output_file_path=output_file.absolute(),
                        status=final_status,
                        quality_score=quality_score,
                        quality_description=quality_description,
                    )

                    print(f"✅ タスク {idx} 完了")
                else:
                    # 失敗した場合もログ記録
                    print()
                    print("📝 失敗ログをシートに記録中...")
                    await log_to_sheet(
                        task_id=task_id,
                        task_description=task.get("Description", task.get("Title", "")),
                        agent_role=agent_role,
                        output_summary=f"タスク実行失敗: {error_message}",
                        output_file_path="N/A",
                        status="failed",
                        quality_score=0,
                        quality_description=f"実行失敗: {error_message}",
                    )
                    print(f"❌ タスク {idx} 失敗")

                print()

                if idx < len(tasks):
                    print("⏳ 次のタスクまで3秒待機...")
                    await asyncio.sleep(3)

        print("=" * 70)
        print("🎉 すべてのタスク処理完了")
        print("=" * 70)
        print(f"📁 出力ディレクトリ: agent_outputs/tasks/")
        print(f"📊 ログ: task_execution_log シート")
        print(f"📝 ステータス: pm_tasks シート")

    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによる中断")
        sys.exit(0)
    except Exception as e:
        print(f"💥 システムエラー: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
