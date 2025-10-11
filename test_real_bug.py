import asyncio
from main_hybrid_fix import HybridFixSystem, HybridFixConfig

async def test_real_bug_fix():
    """実際のバグを修正するテスト"""
    
    # システム初期化
    config = HybridFixConfig()
    system = HybridFixSystem(config=config)
    await system.initialize()
    
    # 実際に存在するファイルのエラーを修正
    test_files = [
        "task_executor/task_executor_content.py",
        "agents/content_agent.py",
        "browser_controller.py"
    ]
    
    print("=" * 80)
    print("🔍 プロジェクトファイルの自動チェック＆修正")
    print("=" * 80)
    
    for file_path in test_files:
        try:
            # ファイルをインポートして実行
            print(f"\n📋 {file_path} をチェック中...")
            # 実際の処理
        except Exception as e:
            print(f"❌ エラー検出: {type(e).__name__}")
            
            # 自動修正を実行
            result = await system.handle_error(
                error=e,
                task_id=f"Fix-{file_path}",
                file_path=file_path,
                context={"source": "auto_scan"}
            )
            
            if result['success']:
                print(f"✅ 自動修正成功！")
            else:
                print(f"⚠️ 手動修正が必要")
    
    # 統計表示
    system.print_system_stats()

asyncio.run(test_real_bug_fix())
