#!/usr/bin/env python3
"""
新規作成モジュールの段階的テスト
"""
import asyncio
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

async def test_safe_browser_manager():
    """Test 1: SafeBrowserManager"""
    print("\n" + "=" * 70)
    print("🧪 Test 1/5: SafeBrowserManager")
    print("=" * 70)
    
    try:
        from browser_control.safe_browser_manager import SafeBrowserManager
        
        print("  📦 インポート成功")
        
        # クラスのインスタンス化テスト
        manager = SafeBrowserManager()
        print("  ✅ インスタンス化成功")
        
        # メソッドの存在確認
        methods = ['get_controller', 'cleanup', '__enter__', '__exit__']
        for method in methods:
            if hasattr(manager, method):
                print(f"  ✅ メソッド '{method}' 存在")
            else:
                print(f"  ⚠️  メソッド '{method}' が見つかりません")
        
        return True
        
    except Exception as e:
        print(f"  ❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_fixed_review_agent():
    """Test 2: FixedReviewAgent"""
    print("\n" + "=" * 70)
    print("🧪 Test 2/5: FixedReviewAgent")
    print("=" * 70)
    
    try:
        from core_agents.fixed_review_agent import FixedReviewAgent
        
        print("  �� インポート成功")
        
        # クラスのインスタンス化テスト
        agent = FixedReviewAgent()
        print("  ✅ インスタンス化成功")
        
        # メソッドの存在確認
        methods = ['initialize', 'review_task', 'run_tests']
        for method in methods:
            if hasattr(agent, method):
                print(f"  ✅ メソッド '{method}' 存在")
            else:
                print(f"  ⚠️  メソッド '{method}' が見つかりません")
        
        return True
        
    except Exception as e:
        print(f"  ❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_safe_wordpress_executor():
    """Test 3: SafeWordPressExecutor"""
    print("\n" + "=" * 70)
    print("🧪 Test 3/5: SafeWordPressExecutor")
    print("=" * 70)
    
    try:
        from safe_wordpress_executor import SafeWordPressExecutor
        
        print("  📦 インポート成功")
        
        # クラスのインスタンス化テスト（URLは必須）
        executor = SafeWordPressExecutor("https://example.com")
        print("  ✅ インスタンス化成功")
        
        # メソッドの存在確認
        methods = ['initialize', 'execute_task', 'cleanup']
        for method in methods:
            if hasattr(executor, method):
                print(f"  ✅ メソッド '{method}' 存在")
            else:
                print(f"  ⚠️  メソッド '{method}' が見つかりません")
        
        return True
        
    except Exception as e:
        print(f"  ❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_integrated_system_fixed():
    """Test 4: IntegratedSystemFixed"""
    print("\n" + "=" * 70)
    print("🧪 Test 4/5: IntegratedSystemFixed")
    print("=" * 70)
    
    try:
        from archive.integrated_system_fixed import IntegratedSystemFixed
        
        print("  📦 インポート成功")
        
        # クラスのインスタンス化テスト
        system = IntegratedSystemFixed()
        print("  ✅ インスタンス化成功")
        
        # メソッドの存在確認
        methods = ['initialize', 'run_cycle', 'cleanup']
        for method in methods:
            if hasattr(system, method):
                print(f"  ✅ メソッド '{method}' 存在")
            else:
                print(f"  ⚠️  メソッド '{method}' が見つかりません")
        
        return True
        
    except Exception as e:
        print(f"  ❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_full_integration_module():
    """Test 5: test_full_integration モジュール"""
    print("\n" + "=" * 70)
    print("🧪 Test 5/5: test_full_integration モジュール")
    print("=" * 70)
    
    try:
        from test import test_full_integration
        
        print("  📦 モジュールインポート成功")
        
        # test_all 関数の存在確認
        if hasattr(test_full_integration, 'test_all'):
            print("  ✅ 'test_all' 関数存在")
        else:
            print("  ⚠️  'test_all' 関数が見つかりません")
        
        return True
        
    except Exception as e:
        print(f"  ❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """全テストを実行"""
    print("\n" + "=" * 70)
    print("🚀 新規作成モジュールの動作確認テスト")
    print("=" * 70)
    
    results = []
    
    # 各テストを順番に実行
    tests = [
        ("SafeBrowserManager", test_safe_browser_manager),
        ("FixedReviewAgent", test_fixed_review_agent),
        ("SafeWordPressExecutor", test_safe_wordpress_executor),
        ("IntegratedSystemFixed", test_integrated_system_fixed),
        ("test_full_integration", test_full_integration_module),
    ]
    
    for name, test_func in tests:
        result = await test_func()
        results.append((name, result))
        await asyncio.sleep(0.5)  # 少し待機
    
    # 結果サマリー
    print("\n" + "=" * 70)
    print("📊 テスト結果サマリー")
    print("=" * 70)
    
    success_count = 0
    for name, result in results:
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"  {status}: {name}")
        if result:
            success_count += 1
    
    print(f"\n総合結果: {success_count}/{len(results)} テスト成功")
    
    if success_count == len(results):
        print("\n🎉 全テスト合格！実際の動作テストに進めます")
        print("\n次のステップ:")
        print("  python test/test_full_integration.py")
        return 0
    else:
        print("\n⚠️  一部のテストが失敗しました。修正が必要です。")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
