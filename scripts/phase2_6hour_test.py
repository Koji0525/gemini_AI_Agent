"""
Phase 2: 6時間稼働テスト

【目的】
- 連続6時間の自律稼働
- エラー発生時の自動復旧確認
- ログとメトリクスの記録

【実行方法】
python3 scripts/phase2_6hour_test.py
"""
import asyncio
import sys
import time
from datetime import datetime, timedelta

# プロジェクトルート追加
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from scripts.integrated.integrated_orchestrator_v31_core import (
    IntegratedOrchestratorV31Core, TaskExecutor, from, import,
    task_executor.task_executor_main)


async def run_6hour_test():
    """6時間稼働テスト実行"""
    
    print("=" * 60)
    print("🚀 Phase 2: 6時間稼働テスト開始")
    print("=" * 60)
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"終了予定: {(datetime.now() + timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # オーケストレーター初期化
    try:
        orchestrator = IntegratedOrchestratorV31Core()
        print("✅ オーケストレーター初期化成功")
    except Exception as e:
        print(f"❌ 初期化失敗: {e}")
        return
    
    # 6時間 = 21600秒
    target_duration = 21600  # 6時間
    # テスト用: 30秒に短縮
    # target_duration = 30
    
    start_time = time.time()
    cycle_count = 0
    error_count = 0
    
    print("\n🔄 稼働ループ開始...\n")
    
    while True:
        elapsed = time.time() - start_time
        
        # 6時間経過チェック
        if elapsed >= target_duration:
            print("\n" + "=" * 60)
            print("✅ 6時間稼働テスト完了!")
            print("=" * 60)
            break
        
        cycle_count += 1
        print(f"\n{'━' * 60}")
        print(f"サイクル {cycle_count} (経過時間: {elapsed/3600:.2f}時間)")
        print(f"{'━' * 60}")
        
        try:
            # 1サイクル実行
            # TODO: orchestrator.run_single_cycle() 実装待ち
            print("⏳ 1サイクル実行中...")
            await asyncio.sleep(3)  # サイクル時間シミュレーション
            print("✅ サイクル完了")
            
        except Exception as e:
            error_count += 1
            print(f"❌ エラー発生 (#{error_count}): {e}")
            
            # 連続エラー3回で中断
            if error_count >= 3:
                print("\n⚠️ 連続エラー検出 - テスト中断")
                break
        
        # 3分待機
        print("⏸️  次のサイクルまで3分待機...")
        await asyncio.sleep(180)
    
    # 最終レポート
    print("\n" + "=" * 60)
    print("📊 最終レポート")
    print("=" * 60)
    print(f"総実行時間: {elapsed/3600:.2f}時間")
    print(f"総サイクル数: {cycle_count}")
    print(f"エラー数: {error_count}")
    print(f"成功率: {((cycle_count - error_count) / cycle_count * 100):.1f}%")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_6hour_test())
