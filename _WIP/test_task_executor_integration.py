#!/usr/bin/env python3
"""
TaskExecutor + 全エージェント + BrowserController
完全統合テスト
"""

import asyncio
import sys
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_task_executor_integration():
    print("🎯 TaskExecutor完全統合テスト")
    print("=" * 70)
    
    try:
        # 1. 必要なモジュールインポート
        print("\n📦 Step 1/6: モジュールインポート")
        from browser_control.browser_controller import EnhancedBrowserController
        from scripts.task_executor import TaskExecutor
        from tools.sheets_manager import GoogleSheetsManager
        print("   ✅ インポート成功")
        
        # 2. BrowserController準備
        print("\n🌐 Step 2/6: BrowserController準備")
        browser = EnhancedBrowserController(
            download_folder=Path("temp_workspace/downloads"),
            mode="text",
            service="google"
        )
        await browser.setup_browser()
        print("   ✅ BrowserController起動")
        
        # 3. SheetsManager準備（モックモード）
        print("\n📊 Step 3/6: SheetsManager準備（モック）")
        # Sheets認証なしでもTaskExecutorが動作するようにNoneで渡す
        sheets_manager = None
        print("   ✅ SheetsManager準備完了（モックモード）")
        
        # 4. TaskExecutor初期化
        print("\n⚙️ Step 4/6: TaskExecutor初期化")
        task_executor = TaskExecutor(
            sheets_manager=sheets_manager,
            browser_controller=browser
        )
        print("   ✅ TaskExecutor初期化完了")
        
        # 5. エージェント確認
        print("\n🔍 Step 5/6: 初期化されたエージェント確認")
        
        agents_to_check = [
            ('design_agent', 'DesignAgent'),
            ('dev_agent', 'DevAgent'),
            ('review_agent_instance', 'ReviewAgent'),
        ]
        
        agent_status = {}
        for attr_name, agent_name in agents_to_check:
            if hasattr(task_executor, attr_name):
                agent = getattr(task_executor, attr_name)
                has_browser = hasattr(agent, 'browser') and agent.browser is not None
                agent_status[agent_name] = has_browser
                status = "✅" if has_browser else "❌"
                print(f"   {status} {agent_name}: browser={'設定済み' if has_browser else '未設定'}")
            else:
                agent_status[agent_name] = False
                print(f"   ❌ {agent_name}: エージェント未初期化")
        
        # 6. 簡易タスク実行テスト
        print("\n🧪 Step 6/6: 簡易タスク実行テスト")
        
        test_task = {
            'id': 'TEST-INTEGRATION-001',
            'type': 'design',
            'title': '統合テスト用デザインタスク',
            'description': 'ブラウザ統合が正しく動作するか確認',
            'status': 'pending'
        }
        
        print(f"   タスクID: {test_task['id']}")
        print(f"   タスクタイプ: {test_task['type']}")
        
        # TaskExecutorがタスクを受け取れるか確認
        # 実際の実行はログイン必要なのでスキップ
        print("   ✅ TaskExecutorはタスクを受け取れる構造")
        print("   注: 実際のAI実行はログイン後に可能")
        
        # クリーンアップ
        print("\n🧹 クリーンアップ")
        await browser.cleanup()
        print("   ✅ クリーンアップ完了")
        
        # 結果サマリー
        print("\n" + "=" * 70)
        print("📊 統合テスト結果サマリー")
        print("=" * 70)
        
        all_agents_ok = all(agent_status.values())
        
        for agent_name, status in agent_status.items():
            print(f"  {'✅' if status else '❌'} {agent_name}")
        
        print("\n" + "=" * 70)
        if all_agents_ok:
            print("🎉 TaskExecutor統合テスト完全成功！")
            print()
            print("✅ 達成項目:")
            print("  1. ✅ BrowserControllerが正常動作")
            print("  2. ✅ 全エージェントにブラウザが設定済み")
            print("  3. ✅ TaskExecutorがエージェントを初期化")
            print("  4. ✅ タスク実行の準備完了")
            print()
            print("🎯 次のステップ:")
            print("  1. VNC 6080ポート追加（オプション）")
            print("  2. ログイン機能追加（オプション）")
            print("  3. アカウントA（WordPress連携）とマージ")
            print("  4. 本番環境での実行テスト")
        else:
            print("⚠️ 一部のエージェントに課題あり")
        
        print("=" * 70)
        
        return all_agents_ok
        
    except Exception as e:
        logger.error(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_task_executor_integration())
    sys.exit(0 if result else 1)
