"""
完全修正版pm_tasks処理システム - BrowserController対応版
"""

import asyncio
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


async def main():
    """メイン実行関数"""
    try:
        # 設定読み込み
        from configuration.config_loader import get_config

        config = get_config()

        print("============================================================")
        print("🚀 pm_tasks処理システム - マルチエージェント連携テスト")
        print("============================================================")

        # コンポーネント初期化
        from browser_control.browser_controller import BrowserController
        from tools.pm_tasks_loader import PMTasksLoader

        print("🔄 コンポーネント初期化中...")

        # タスクローダー
        tasks_loader = PMTasksLoader()
        print("✅ PMTasksLoader初期化成功")

        # コマンドライン引数
        parser = argparse.ArgumentParser()
        parser.add_argument("--max-tasks", type=int, default=1, help="処理する最大タスク数")
        parser.add_argument("--status", type=str, default=None, help="ステータスフィルター")
        args = parser.parse_args()

        # タスク読み込み
        print(f"🔄 タスク読み込み中（最大{args.max_tasks}タスク）...")
        tasks = tasks_loader.load_tasks(max_tasks=args.max_tasks, status_filter=args.status)

        if not tasks:
            print("⚠️ 処理するタスクがありません")
            return

        print(f"✅ タスク読み込み成功: {len(tasks)} タスク")
        print()

        # BrowserController を使ってタスク実行
        async with BrowserController(download_folder="./downloads") as browser:
            print("✅ BrowserController初期化完了")

            # Gemini接続
            print("🌐 Geminiに接続中...")
            logged_in = await browser.navigate_to_gemini()

            if not logged_in:
                print("❌ Gemini接続失敗")
                return

            print("✅ Gemini接続成功")
            print()

            # 各タスクを処理
            for idx, task in enumerate(tasks, 1):
                print("=" * 70)
                print(f"📝 タスク {idx}/{len(tasks)}")
                print("=" * 70)
                print(f"  TaskID     : {task.get('TaskID', 'N/A')}")
                print(f"  Agent      : {task.get('Agent', 'N/A')}")
                print(f"  Status     : {task.get('Status', 'N/A')}")
                print(f"  Title      : {task.get('Title', 'N/A')[:80]}")
                print(f"  Dependencies: {task.get('Dependencies', 'なし')}")
                print()

                # エージェント役割に応じたプロンプト
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

                # タスク実行プロンプト
                prompt = f"""
{role_instruction}

【タスクID】
{task.get('TaskID', 'N/A')}

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

                print("💬 タスク実行中...")
                await browser.send_prompt(prompt)

                # レスポンス待機
                print("⏳ レスポンス生成待機中（最大60秒）...")
                generation_success = await browser.wait_for_text_generation(max_wait=60)

                if not generation_success:
                    print("⚠️ レスポンス生成タイムアウト")
                    continue

                # レスポンス取得
                print("📥 レスポンス取得中...")
                response = await browser.extract_latest_text_response()

                if response:
                    print(f"✅ レスポンス取得成功: {len(response)}文字")

                    # レスポンスのプレビュー
                    print()
                    print("📄 レスポンス（最初の300文字）:")
                    print("-" * 70)
                    print(response[:300] + "..." if len(response) > 300 else response)
                    print("-" * 70)
                    print()

                    # 結果を保存
                    output_dir = Path("agent_outputs/tasks")
                    output_dir.mkdir(parents=True, exist_ok=True)

                    task_id = task.get("TaskID", f"task_{idx}")
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
                    print(f"✅ タスク {idx} 完了")
                else:
                    print("❌ レスポンス取得失敗")

                print()

                # 複数タスクの場合は少し待機
                if idx < len(tasks):
                    print("⏳ 次のタスクまで3秒待機...")
                    await asyncio.sleep(3)

        print("=" * 70)
        print("🎉 すべてのタスク処理完了")
        print("=" * 70)
        print(f"📁 出力ディレクトリ: agent_outputs/tasks/")

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
