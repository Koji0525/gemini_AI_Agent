"""CompleteEngineUltimate統合版（TaskExecutorEnhanced統合）"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from datetime import timedelta, timezone

from agents.complete_engine_ultimate import \
    CompleteEngineUltimate as BaseEngine
from agents.task_executor_enhanced import TaskExecutorEnhanced

JST = timezone(timedelta(hours=9))


class CompleteEngineUltimateIntegrated(BaseEngine):
    """TaskExecutorEnhancedを統合したCompleteEngineUltimate"""

    def __init__(self):
        super().__init__()
        self.task_executor = TaskExecutorEnhanced()
        print("✅ TaskExecutorEnhanced統合版初期化")

    def _generate_default_task_detail(self, task: dict) -> dict:
        """タスク情報から詳細定義を動的生成"""

        task_id = task.get("task_id", "unknown")
        description = task.get("description", "")
        execution_type = task.get("execution_type", "implementation")

        # タスクタイプの判定
        task_type = execution_type if execution_type else "implementation"

        # デフォルトの詳細定義を生成
        detailed_task = {
            "task_id": task_id,
            "title": description.split(":")[0] if ":" in description else description[:50],
            "description": description,
            "purpose": f"{description}を完了させる",
            "acceptance_criteria": [
                f"{task_id}の成果物が生成されている",
                "実行ログにエラーがない",
                "品質スコアが60以上",
            ],
            "expected_outputs": [
                f"agent_outputs/{task_type}/{task_id}/README.md",
                f"agent_outputs/{task_type}/{task_id}/output.txt",
            ],
            "verification_steps": [
                f"ls agent_outputs/{task_type}/{task_id}/",
                f"cat agent_outputs/{task_type}/{task_id}/README.md",
            ],
            "role": task.get("required_role", "developer"),
            "time": task.get("estimated_time", "1h"),
            "type": task_type,
        }

        # タスク説明から成功条件を推測
        if "セットアップ" in description or "setup" in description.lower():
            detailed_task["acceptance_criteria"] = [
                "プロジェクトディレクトリが作成されている",
                "必要なファイル構造が整っている",
                "README.mdに基本情報が記載されている",
            ]
            detailed_task["expected_outputs"] = [
                f"agent_outputs/setup/{task_id}/project/src/__init__.py",
                f"agent_outputs/setup/{task_id}/project/requirements.txt",
                f"agent_outputs/setup/{task_id}/project/README.md",
            ]
        elif "CLI" in description or "コマンド" in description:
            detailed_task["acceptance_criteria"] = [
                "CLIスクリプトが作成されている",
                "ヘルプ機能が実装されている",
                "基本コマンドが動作する",
            ]
            detailed_task["expected_outputs"] = [
                f"agent_outputs/implementation/{task_id}/cli.py",
                f"agent_outputs/implementation/{task_id}/README.md",
            ]
        elif "API" in description or "統合" in description:
            detailed_task["acceptance_criteria"] = [
                "APIクライアントが実装されている",
                "認証処理が動作する",
                "エラーハンドリングがある",
            ]
            detailed_task["expected_outputs"] = [
                f"agent_outputs/implementation/{task_id}/api_client.py",
                f"agent_outputs/implementation/{task_id}/config.json",
                f"agent_outputs/implementation/{task_id}/README.md",
            ]

        return detailed_task

    def execute_task(self, task: dict) -> dict:
        """タスクを実行（TaskExecutorEnhanced使用）- 正しいメソッド名"""

        task_id = task.get("task_id", "unknown")
        description = task.get("description", "")

        print(f"\n{'='*80}")
        print(f"🚀 タスク実行: {task_id}")
        print(f"   説明: {description[:70]}...")
        print(f"{'='*80}")

        try:
            # 詳細タスク定義の読み込み
            detail_path = task.get("detail_file_path", "")
            detailed_task = None

            if detail_path and Path(detail_path).exists():
                print(f"📋 詳細タスク定義を読み込み: {Path(detail_path).name}")

                try:
                    with open(detail_path, "r", encoding="utf-8") as f:
                        detailed_tasks = json.load(f)

                    # 該当タスクを探す
                    for dt in detailed_tasks:
                        if dt.get("task_id") == task_id:
                            detailed_task = dt
                            break
                except Exception as e:
                    print(f"⚠️ 詳細タスク定義の読み込みエラー: {e}")

            # detail_file_pathがない、または読み込み失敗時は動的生成
            if not detailed_task:
                print("📝 タスク情報から詳細定義を動的生成")
                detailed_task = self._generate_default_task_detail(task)

            # 詳細情報表示
            print(f"\n📌 目的: {detailed_task.get('purpose', 'N/A')}")

            ac = detailed_task.get("acceptance_criteria", [])
            if ac:
                print(f"\n✅ 成功条件 ({len(ac)}個):")
                for i, criteria in enumerate(ac, 1):
                    print(f"   {i}. {criteria}")

            outputs = detailed_task.get("expected_outputs", [])
            if outputs:
                print(f"\n📦 期待する成果物 ({len(outputs)}個):")
                for output in outputs[:5]:
                    if isinstance(output, str):
                        print(f"   - {output}")
                    elif isinstance(output, dict):
                        print(f"   - {output.get('name', output.get('path', 'N/A'))}")

            print(f"\n{'='*80}")
            print("⚙️ タスク実行中...")
            print(f"{'='*80}\n")

            # TaskExecutorEnhancedで実行
            result = self.task_executor.execute_task(detailed_task)

            # 結果表示
            print(f"\n{'='*80}")
            print("📊 実行結果")
            print(f"{'='*80}")
            print(f"ステータス: {result.get('status', 'unknown')}")
            print(f"品質スコア: {result.get('quality_score', 0)}/100")
            print(f"実行時間: {result.get('execution_time', 0):.2f}秒")

            output_path = result.get("output_path", "")
            if output_path:
                print(f"\n📂 成果物の場所:")
                print(f"   {output_path}")

                # 実際のファイル確認
                full_path = Path("/workspaces/gemini_AI_Agent") / output_path
                if full_path.exists():
                    print(f"\n📄 生成ファイル:")
                    for item in sorted(full_path.rglob("*")):
                        if item.is_file():
                            rel_path = item.relative_to(full_path)
                            size = item.stat().st_size
                            print(f"   - {rel_path} ({size} bytes)")

                generated = result.get("generated_files", [])
                if generated and not full_path.exists():
                    print(f"\n📄 生成予定ファイル ({len(generated)}個):")
                    for f in generated[:10]:
                        print(f"   - {f}")

            feedback = result.get("feedback", "")
            if feedback:
                print(f"\n💬 フィードバック:")
                for line in feedback.split("\n"):
                    if line.strip():
                        print(f"   {line}")

            verification = result.get("verification", [])
            if verification:
                print(f"\n✓ 検証結果:")
                for v in verification:
                    print(f"   - {v.get('step', 'N/A')}: {v.get('status', 'N/A')}")

            print(f"\n{'='*80}")
            print("✅ タスク実行完了")
            print(f"{'='*80}\n")

            return result

        except Exception as e:
            print(f"\n❌ タスク実行エラー: {e}")
            import traceback

            traceback.print_exc()

            return {
                "status": "failed",
                "quality_score": 0,
                "execution_time": 0,
                "error": str(e),
                "feedback": f"エラー: {e}",
            }


if __name__ == "__main__":
    # テスト
    from tools.base_data_accessor import BaseDataAccessor

    print("\n" + "=" * 80)
    print("🧪 統合版エンジンのテスト")
    print("=" * 80)

    accessor = BaseDataAccessor()
    tasks = accessor.read_sheet_as_dicts(
        "pm_tasks", filter_func=lambda t: t.get("status") == "pending"
    )

    if tasks:
        print(f"\n{len(tasks)}個のpendingタスクが見つかりました")
        print(f"\n最初のタスクを実行:")
        print(f"  {tasks[0].get('task_id')}: {tasks[0].get('description', '')[:50]}")

        engine = CompleteEngineUltimateIntegrated()

        # 最初のタスクを実行
        result = engine.execute_task(tasks[0])

        print("\n" + "=" * 80)
        print("✅ テスト完了")
        print("=" * 80)
        print(f"\n結果:")
        print(f"  ステータス: {result.get('status')}")
        print(f"  品質: {result.get('quality_score')}")
        print(f"  出力: {result.get('output_path', 'N/A')}")
    else:
        print("\n⚠️ pendingタスクが見つかりません")



    def _get_output_path(self, task_id, description):
        """親クラスのメソッドをオーバーライド - 詳細版auto_logsを生成"""
        print("🔍 DEBUG: 子クラスの_get_output_pathが呼ばれました！")
        print(f"  task_id: {task_id}")
        print(f"  description: {description[:50]}...")
        # TaskExecutorEnhancedの実行結果から出力パスを推測
        task_type = "implementation"  # デフォルト
        
        # task_idからタスクタイプを推測
        if "_setup_" in task_id:
            task_type = "setup"
        elif "_test_" in task_id:
            task_type = "test"
        elif "_documentation_" in task_id:
            task_type = "documentation"
        elif "_implementation_" in task_id:
            task_type = "implementation"
        
        # TaskExecutorEnhancedが生成した成果物ディレクトリを探す
        from datetime import datetime
        output_base = Path("agent_outputs") / task_type
        
        # 最新のタスクIDに一致するディレクトリを探す
        output_path = ""
        if output_base.exists():
            matching_dirs = sorted(
                [d for d in output_base.iterdir() if d.is_dir() and d.name.startswith(task_id)],
                key=lambda d: d.stat().st_mtime,
                reverse=True
            )
            if matching_dirs:
                output_path = str(matching_dirs[0].relative_to(Path(".")))
                print(f"  📂 成果物ディレクトリ発見: {output_path}")
        
        # 詳細版auto_logsを生成
        return self._create_detailed_auto_log(task_id, description, output_path)

    def _create_detailed_auto_log(self, task_id: str, description: str, output_path: str) -> str:
        """詳細版auto_logsを生成（execution.logの内容を統合）"""
        
        from datetime import datetime
        
        # 安全なファイル名生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_task_id = task_id.replace("/", "_").replace("\\", "_").replace(":", "_")[:50]
        filename = f"{safe_task_id}_{timestamp}.txt"
        
        # 出力ディレクトリ
        auto_logs_dir = Path("agent_outputs") / "auto_logs"
        auto_logs_dir.mkdir(parents=True, exist_ok=True)
        auto_log_path = auto_logs_dir / filename
        
        # execution.logを読み込み
        execution_log_content = ""
        generated_files = []
        
        if output_path:
            # output_pathからexecution.logを探す
            output_dir = Path("/workspaces/gemini_AI_Agent") / output_path
            execution_log = output_dir / "execution.log"
            
            if execution_log.exists():
                try:
                    execution_log_content = execution_log.read_text(encoding='utf-8')
                    print(f"  📄 execution.log読み込み成功 ({execution_log.stat().st_size} bytes)")
                except Exception as e:
                    print(f"  ⚠️ execution.log読み込みエラー: {e}")
            
            # 成果物リストを生成
            if output_dir.exists():
                for item in sorted(output_dir.rglob("*")):
                    if item.is_file() and item.name != "execution.log":
                        rel_path = item.relative_to(output_dir)
                        size = item.stat().st_size
                        generated_files.append(f"   - {rel_path} ({size} bytes)")
        
        # 詳細コンテンツ生成
        content_parts = [
            f"タスク実行完了: {task_id}",
            f"説明: {description}",
            f"実行日時: {datetime.now().isoformat()}",
            "",
            "※このファイルは自動生成されました",
        ]
        
        # execution.logの内容を統合
        if execution_log_content:
            content_parts.extend([
                "",
                "="*80,
                "📊 実行結果",
                "="*80,
                execution_log_content
            ])
        
        # 成果物リストを追加
        if generated_files:
            content_parts.extend([
                "",
                f"📂 成果物の場所:",
                f"   {output_path}",
                f"📄 生成ファイル:",
                *generated_files
            ])
        
        # ファイルに書き込み
        detailed_content = "\n".join(content_parts)
        
        try:
            with open(auto_log_path, "w", encoding="utf-8") as f:
                f.write(detailed_content)
            print(f"✅ 詳細auto_log作成: {auto_log_path.name} ({len(detailed_content)} bytes)")
            return str(auto_log_path)
        except Exception as e:
            print(f"❌ auto_log作成エラー: {e}")
            return f"error_{filename}"

