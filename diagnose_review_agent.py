#!/usr/bin/env python3
"""ReviewAgentの詳細診断"""
import inspect
from pathlib import Path

def diagnose_review_agent():
    print("🔍 ReviewAgent詳細診断")
    print("=" * 70)
    
    try:
        # インポート
        from core_agents.review_agent import ReviewAgent
        
        # 1. __init__のシグネチャ確認
        print("\n📋 1. __init__シグネチャ")
        sig = inspect.signature(ReviewAgent.__init__)
        params = list(sig.parameters.keys())
        print(f"   引数: {params}")
        
        # 2. __init__のソースコード確認
        print("\n📋 2. __init__ソースコード（最初の20行）")
        try:
            source = inspect.getsource(ReviewAgent.__init__)
            lines = source.split('\n')[:20]
            for i, line in enumerate(lines, 1):
                print(f"   {i:2}: {line}")
        except:
            print("   ⚠️ ソースコード取得失敗")
        
        # 3. クラス属性確認
        print("\n📋 3. ReviewAgentクラス属性")
        instance_test = ReviewAgent()
        attrs = [attr for attr in dir(instance_test) if not attr.startswith('_')]
        print(f"   主要属性: {attrs[:10]}")
        
        # 4. browserアトリビュート確認
        print("\n�� 4. browser属性の確認")
        has_browser = hasattr(instance_test, 'browser')
        print(f"   has browser: {has_browser}")
        if has_browser:
            print(f"   browser value: {instance_test.browser}")
        
        print("\n" + "=" * 70)
        print("診断完了")
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_review_agent()
