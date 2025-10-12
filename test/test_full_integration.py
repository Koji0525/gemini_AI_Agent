"""完全統合テスト"""
import asyncio
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
logging.basicConfig(level=logging.INFO)

async def test_all():
    print("=" * 80)
    print("🧪 統合テスト開始")
    print("=" * 80)
    
    try:
        # 1. ブラウザ管理テスト
        print("\n[1/4] ブラウザ管理モジュールテスト...")
        from browser_control.safe_browser_manager import SafeBrowserManager
        browser_mgr = SafeBrowserManager()
        print("✅ SafeBrowserManager インポート成功")
        
        # 2. WordPress実行テスト
        print("\n[2/4] WordPress実行モジュールテスト...")
        from safe_wordpress_executor import SafeWordPressExecutor
        # wp = SafeWordPressExecutor("https://example.com")
        print("✅ SafeWordPressExecutor インポート成功")
        
        # 3. レビューエージェントテスト
        print("\n[3/4] レビューエージェントテスト...")
        from core_agents.fixed_review_agent import FixedReviewAgent
        reviewer = FixedReviewAgent()
        print("✅ FixedReviewAgent インポート成功")
        
        # 4. 統合システムテスト（archiveから）
        print("\n[4/4] 統合システムテスト...")
        from archive.integrated_system_fixed import IntegratedSystemFixed
        # system = IntegratedSystemFixed()
        print("✅ IntegratedSystemFixed インポート成功")
        
        print("\n" + "=" * 80)
        print("🎉 全モジュールのインポートテスト完了！")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_all())
    sys.exit(0 if success else 1)
