"""
F5-F6をCompleteEngineに統合するスクリプト
既存のCompleteEngineを変更せずに機能を追加
"""

import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.complete_engine_ultimate import CompleteEngineUltimate
from agents.f5_f6_integration import F5F6Integration

def integrate_f5_f6():
    """F5-F6をCompleteEngineに統合"""
    print("━" * 60)
    print("🔧 F5-F6統合スクリプト実行")
    print("━" * 60)
    print()
    
    try:
        # CompleteEngine初期化
        print("  🔧 CompleteEngine初期化中...")
        engine = CompleteEngineUltimate()
        
        # F5-F6統合
        print("  🔧 F5-F6統合中...")
        integration = F5F6Integration(
            sheets_manager=getattr(engine, 'sheets', None),
            pm_agent=getattr(engine, 'pm_agent', None)
        )
        integration.integrate_to_engine(engine)
        
        # 統合確認
        print("\n【統合確認】")
        f5_integrated = hasattr(engine, 'show_progress')
        f6_integrated = hasattr(engine, 'add_dynamic_task')
        
        print(f"  {'✅' if f5_integrated else '❌'} F5: show_progress()")
        print(f"  {'✅' if f6_integrated else '❌'} F6: add_dynamic_task()")
        
        if f5_integrated and f6_integrated:
            print("\n✅ F5-F6統合成功")
            
            # テスト実行
            print("\n【テスト実行】")
            
            # F5テスト
            print("  F5: 進捗サマリー取得")
            summary = engine.get_progress_summary()
            print(f"    {summary}")
            
            return True
        else:
            print("\n❌ 統合失敗")
            return False
            
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = integrate_f5_f6()
    sys.exit(0 if success else 1)

