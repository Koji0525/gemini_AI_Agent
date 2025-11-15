"""簡易版3周実行スクリプト"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from agents.complete_engine_ultimate_integrated import CompleteEngineUltimateIntegrated as CompleteEngineUltimate
from datetime import datetime


def main():
    """3周実行"""
    print("="*80)
    print("🔄 3周実行開始")
    print("="*80)
    
    try:
        # エンジン初期化
        engine = CompleteEngineUltimate()
        
        for cycle in range(1, 4):
            print("")
            print("="*80)
            print(f"🔄 サイクル {cycle}/3")
            print("="*80)
            
            try:
                # フロー実行（1サイクルあたり2タスク）
                engine.run_complete_flow(execute_count=2)
                
                print("")
                print(f"✅ サイクル{cycle}完了")
                
            except Exception as e:
                print(f"❌ サイクル{cycle}エラー: {e}")
                import traceback
                traceback.print_exc()
        
        print("")
        print("="*80)
        print("✅ 全3サイクル完了")
        print("="*80)
        
    except Exception as e:
        print(f"❌ 初期化エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
