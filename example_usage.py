# example_usage.py
"""
ハイブリッド型自律コード修正システムの使用例
"""

import asyncio
import logging
from pathlib import Path

# エージェントのインポート
from hybrid_fix_orchestrator import HybridFixOrchestrator, FixStrategy
from local_fix_agent import LocalFixAgent
from cloud_fix_agent import CloudFixAgent
from error_classifier import ErrorClassifier
from wp_tester_agent import WPTesterAgent
from github_agent import GitHubAgent
from patch_manager import PatchManager
from cloud_storage_manager import CloudStorageManager

# データモデル
from data_models import (
    BugFixTask,
    ErrorContextModel,
    ErrorSeverity,
    ErrorCategory,
    create_bug_fix_task_from_exception
)

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# ========================================
# 例1: 基本的な使用方法
# ========================================

async def example_1_basic_usage():
    """基本的な自動修正の例"""
    
    logger.info("=" * 80)
    logger.info("例1: 基本的な自動修正")
    logger.info("=" * 80)
    
    # コマンドモニター（仮）
    class DummyCommandMonitor:
        async def execute_command(self, cmd):
            return {"success": True, "stdout": ""}
    
    cmd_monitor = DummyCommandMonitor()
    
    # エージェント初期化
    local_agent = LocalFixAgent(
        command_monitor=cmd_monitor,
        use_local_ai=False  # まずはルールベースのみ
    )
    
    cloud_agent = CloudFixAgent(
        command_monitor=cmd_monitor,
        api_provider="openai",
        model_name="gpt-4o"
    )
    
    classifier = ErrorClassifier()
    
    # オーケストレーター初期化
    orchestrator = HybridFixOrchestrator(
        local_agent=local_agent,
        cloud_agent=cloud_agent,
        error_classifier=classifier,
        default_strategy=FixStrategy.ADAPTIVE
    )
    
    # エラーコンテキスト作成
    error_context = ErrorContextModel(
        error_type="AttributeError",
        error_message="'NoneType' object has no attribute 'get'",
        severity=ErrorSeverity.HIGH,
        error_category=ErrorCategory.RUNTIME,
        file_path="wp_agent.py",
        line_number=42,
        surrounding_code="""
def process_data(self, data):
    result = self.fetch_config()
    value = result.get('key')  # ← エラー発生箇所
    return value
""",
        full_traceback="""
Traceback (most recent call last):
  File "wp_agent.py", line 42, in process_data
    value = result.get('key')
AttributeError: 'NoneType' object has no attribute 'get'
"""
    )
    
    # バグ修正タスク作成
    task = BugFixTask(
        task_id="Example-1-AttributeError-Fix",
        error_context=error_context,
        target_files=["wp_agent.py"],
        priority=8,
        run_tests=False,  # この例ではテストをスキップ
        create_pr=False
    )
    
    # 修正実行
    result = await orchestrator.execute_fix_task(task)
    
    # 結果表示
    print("\n" + "=" * 80)
    print("🔧 修正結果")
    print("=" * 80)
    print(f"成功: {result.success}")
    print(f"修正ファイル: {result.modified_files}")
    print(f"信頼度: {result.confidence_score:.1%}")
    print(f"実行時間: {result.execution_time:.2f}秒")
    print(f"使用エージェント: {result.agent_used}")
    
    if result.success:
        print(f"\n📝 修正理由:\n{result.reasoning}")
    else:
        print(f"\n❌ エラー: {result.error_message}")
    
    # 統計表示
    orchestrator.print_stats()


# ========================================
# 例2: 例外からの自動修正
# ========================================

async def example_2_exception_handling():
    """実行時例外からの自動修正"""
    
    logger.info("=" * 80)
    logger.info("例2: 例外からの自動修正")
    logger.info("=" * 80)
    
    # 擬似的なコード実行
    try:
        # エラーが発生するコード
        data = None
        result = data.get('key')  # AttributeError発生
    
    except Exception as e:
        logger.info(f"例外を捕捉: {type(e).__name__}: {e}")
        
        # 例外からタスクを自動生成
        task = create_bug_fix_task_from_exception(
            task_id="Example-2-Auto-Generated",
            exception=e,
            file_path="example_code.py",
            line_number=10
        )
        
        # オーケストレーター初期化（簡易版）
        # ... (エージェント初期化は省略)
        
        logger.info(f"✅ バグ修正タスク自動生成: {task.task_id}")
        logger.info(f"   エラータイプ: {task.error_context.error_type}")
        logger.info(f"   重要度: {task.error_context.severity.value}")


# ========================================
# 例3: 複数戦略の比較
# ========================================

async def example_3_strategy_comparison():
    """異なる戦略の比較"""
    
    logger.info("=" * 80)
    logger.info("例3: 複数戦略の比較")
    logger.info("=" * 80)
    
    # ... (初期化は省略)
    
    strategies = [
        FixStrategy.LOCAL_ONLY,
        FixStrategy.CLOUD_ONLY,
        FixStrategy.LOCAL_FIRST,
        FixStrategy.PARALLEL
    ]
    
    results = {}
    
    for strategy in strategies:
        logger.info(f"\n📊 戦略テスト: {strategy.value}")
        
        # タスク作成（同じエラーコンテキスト）
        # task = ... (省略)
        
        # 戦略を指定して実行
        # result = await orchestrator.execute_fix_task(task, strategy=strategy)
        
        # results[strategy.value] = result
    
    # 結果比較
    print("\n" + "=" * 80)
    print("📊 戦略別比較")
    print("=" * 80)
    print(f"{'戦略':<20} {'成功':<10} {'実行時間':<15} {'信頼度':<10}")
    print("-" * 80)
    
    for strategy_name, result in results.items():
        print(
            f"{strategy_name:<20} "
            f"{'✅' if result.success else '❌':<10} "
            f"{result.execution_time:.2f}秒{'':<8} "
            f"{result.confidence_score:.1%}"
        )


# ========================================
# 例4: GitHub連携付き完全ワークフロー
# ========================================

async def example_4_full_workflow_with_github():
    """GitHub連携を含む完全なワークフロー"""
    
    logger.info("=" * 80)
    logger.info("例4: GitHub連携付き完全ワークフロー")
    logger.info("=" * 80)
    
    # ... (エージェント初期化)
    
    # GitHubエージェント追加
    github_agent = GitHubAgent(
        repo_path=".",
        repo_owner="your-org",
        repo_name="your-repo"
    )
    
    # テスターエージェント追加
    wp_tester = WPTesterAgent(
        command_monitor=None,  # 仮
        wp_path="/var/www/html"
    )
    
    # タスク作成（テスト & PR作成を有効化）
    # task = BugFixTask(
    #     task_id="Example-4-Full-Workflow",
    #     error_context=...,
    #     target_files=["wp_agent.py"],
    #     run_tests=True,
    #     create_pr=True
    # )
    
    # 修正実行
    # result = await orchestrator.execute_fix_task(task)
    
    # if result.success:
    #     # GitHub PR作成
    #     pr_result = await github_agent.create_full_fix_workflow(
    #         task_id=task.task_id,
    #         modified_files=result.modified_files,
    #         fix_description=result.reasoning
    #     )
    #     
    #     if pr_result["success"]:
    #         logger.info(f"✅ PR作成成功: {pr_result['pr_url']}")


# ========================================
# 例5: クラウドストレージ連携
# ========================================

async def example_5_cloud_storage():
    """クラウドストレージとの連携"""
    
    logger.info("=" * 80)
    logger.info("例5: クラウドストレージ連携")
    logger.info("=" * 80)
    
    # ストレージマネージャー初期化
    storage = CloudStorageManager(
        provider="gcs",  # or "s3", "azure"
        bucket_name="your-bucket",
        auto_sync=True
    )
    
    # クッキーファイルの読み込み（クラウドから）
    try:
        cookies = await storage.read_file("session/cookies.json")
        logger.info(f"✅ クッキー読み込み成功（{len(cookies)}バイト）")
    except Exception as e:
        logger.error(f"❌ クッキー読み込み失敗: {e}")
    
    # 修正結果の保存（クラウドへ）
    fix_result_json = '{"success": true, "modified_files": ["wp_agent.py"]}'
    
    try:
        await storage.write_file(
            "fix_results/example_5.json",
            fix_result_json
        )
        logger.info("✅ 修正結果をクラウドに保存")
    except Exception as e:
        logger.error(f"❌ 保存失敗: {e}")
    
    # 統計表示
    stats = storage.get_stats()
    print(f"\n📊 ストレージ統計:")
    print(f"   アップロード: {stats['uploads']}回")
    print(f"   ダウンロード: {stats['downloads']}回")
    print(f"   キャッシュヒット率: {stats['cache_hit_rate']:.1%}")


# ========================================
# 例6: パッチ管理の高度な使用
# ========================================

async def example_6_advanced_patching():
    """パッチ管理の高度な使用例"""
    
    logger.info("=" * 80)
    logger.info("例6: 高度なパッチ管理")
    logger.info("=" * 80)
    
    patch_manager = PatchManager(
        backup_dir="./backups/patches",
        max_backups=10
    )
    
    # 安全な修正適用
    original_code = """
def fetch_config(self):
    return self.config_data
"""
    
    fixed_code = """
def fetch_config(self):
    if self.config_data is None:
        self.config_data = self._load_config()
    return self.config_data
"""
    
    # 検証付きパッチ適用
    result = await patch_manager.apply_patch(
        file_path="wp_agent.py",
        new_content=fixed_code,
        strategy=PatchStrategy.REPLACE,
        verify=True  # 構文チェックを実行
    )
    
    if result["success"]:
        logger.info("✅ パッチ適用成功")
        logger.info(f"   バックアップ: {result['backup_path']}")
        
        # 差分表示
        if result.get("diff"):
            print("\n📋 変更内容:")
            print(result["diff"])
    
    # ロールバックのテスト
    # rollback_result = await patch_manager.rollback("wp_agent.py")
    
    # 統計
    stats = patch_manager.get_stats()
    print(f"\n📊 パッチ統計:")
    print(f"   成功率: {stats['success_rate']:.1%}")
    print(f"   ロールバック: {stats['rollbacks']}回")


# ========================================
# メイン実行
# ========================================

async def main():
    """すべての例を実行"""
    
    print("\n" + "🚀 " * 20)
    print("   ハイブリッド型自律コード修正システム - 使用例")
    print("🚀 " * 20 + "\n")
    
    # 例1: 基本的な使用方法
    await example_1_basic_usage()
    
    # 例2: 例外からの自動修正
    await example_2_exception_handling()
    
    # 例3: 複数戦略の比較
    # await example_3_strategy_comparison()
    
    # 例4: GitHub連携付き完全ワークフロー
    # await example_4_full_workflow_with_github()
    
    # 例5: クラウドストレージ連携
    # await example_5_cloud_storage()
    
    # 例6: パッチ管理の高度な使用
    # await example_6_advanced_patching()
    
    print("\n" + "✅ " * 20)
    print("   すべての例が完了しました")
    print("✅ " * 20 + "\n")


if __name__ == "__main__":
    # Windows環境の場合
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # 実行
    asyncio.run(main())