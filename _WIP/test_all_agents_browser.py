#!/usr/bin/env python3
"""全エージェント + BrowserController 統合テスト（修正版）"""
import asyncio
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_all_agents():
    print("🎯 全エージェント統合テスト")
    print("=" * 70)
    
    results = {}
    
    try:
        from browser_control.browser_controller import EnhancedBrowserController
        from core_agents.design_agent import DesignAgent
        from core_agents.dev_agent import DevAgent
        from core_agents.review_agent import ReviewAgent
        
        # BrowserController準備
        print("\n📦 BrowserController準備")
        browser = EnhancedBrowserController(
            download_folder=Path("temp_workspace/downloads"),
            mode="text",
            service="google"
        )
        await browser.setup_browser()
        print("   ✅ BrowserController起動")
        
        # 各エージェントテスト（全て browser_controller で統一）
        agents = [
            ("DesignAgent", DesignAgent, {
                "browser_controller": browser,
                "output_folder": Path("agent_outputs/design")
            }),
            ("DevAgent", DevAgent, {
                "browser_controller": browser,
                "output_folder": Path("agent_outputs/dev")
            }),
            ("ReviewAgent", ReviewAgent, {
                "browser_controller": browser,  # ← 修正: browserからbrowser_controllerに変更
                "output_folder": Path("agent_outputs/review")
            })
        ]
        
        for agent_name, AgentClass, kwargs in agents:
            print(f"\n🧪 {agent_name} テスト")
            try:
                agent = AgentClass(**kwargs)
                
                # ブラウザ属性確認
                browser_attr = agent.browser if hasattr(agent, 'browser') else None
                
                if browser_attr is None:
                    results[agent_name] = False
                    print(f"   ❌ ブラウザ未設定（browser is None）")
                    continue
                
                # メソッド確認
                required_methods = [
                    'send_prompt',
                    'wait_for_text_generation',
                    'extract_latest_text_response'
                ]
                
                method_results = []
                for method in required_methods:
                    has_method = (
                        hasattr(browser_attr, method) and 
                        callable(getattr(browser_attr, method))
                    )
                    method_results.append(has_method)
                    status = "✅" if has_method else "❌"
                    print(f"   {status} {method}")
                
                results[agent_name] = all(method_results)
                    
            except Exception as e:
                results[agent_name] = False
                print(f"   ❌ エラー: {e}")
                import traceback
                traceback.print_exc()
        
        await browser.cleanup()
        
        # 結果サマリー
        print("\n" + "=" * 70)
        print("📊 テスト結果サマリー")
        print("=" * 70)
        for agent_name, result in results.items():
            print(f"  {'✅' if result else '❌'} {agent_name}")
        
        all_passed = all(results.values())
        print("\n" + "=" * 70)
        if all_passed:
            print("🎉🎉🎉 全エージェント統合テスト完全成功！ 🎉��🎉")
            print()
            print("次のステップ:")
            print("  1. ✅ TaskExecutorとの統合")
            print("  2. ✅ 実際のタスク実行テスト")
            print("  3. ✅ アカウントA（WordPress連携）とマージ準備")
        else:
            print("⚠️ 一部のエージェントに課題あり")
        print("=" * 70)
        
        return all_passed
        
    except Exception as e:
        logger.error(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_all_agents())
    sys.exit(0 if result else 1)
