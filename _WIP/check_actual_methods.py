#!/usr/bin/env python3
"""
実際に実装されているメソッドを確認
"""
import inspect
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def get_class_methods(cls):
    """クラスの公開メソッドを取得"""
    methods = []
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if not name.startswith('_'):
            methods.append(name)
    return sorted(methods)

def main():
    print("=" * 70)
    print("🔍 実装メソッドの確認")
    print("=" * 70)
    
    modules = [
        ("browser_control.safe_browser_manager", "SafeBrowserManager"),
        ("core_agents.fixed_review_agent", "FixedReviewAgent"),
        ("safe_wordpress_executor", "SafeWordPressExecutor"),
        ("archive.integrated_system_fixed", "IntegratedSystemFixed"),
    ]
    
    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            methods = get_class_methods(cls)
            
            print(f"\n📦 {class_name}")
            print(f"   モジュール: {module_name}")
            print(f"   公開メソッド数: {len(methods)}")
            print(f"   メソッド一覧:")
            for method in methods:
                print(f"     - {method}()")
                
        except Exception as e:
            print(f"\n❌ {class_name}: {e}")

if __name__ == "__main__":
    main()
