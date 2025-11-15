#!/usr/bin/env python3
"""ステータス更新フローの詳細トレース"""

import inspect
from agents.complete_engine_ultimate import CompleteEngineUltimate

def trace_status_update():
    print("🔍 CompleteEngineUltimate のステータス更新メソッド調査")
    
    # クラスの全メソッドを調査
    methods = [m for m in dir(CompleteEngineUltimate) if not m.startswith('_')]
    print(f"公開メソッド数: {len(methods)}")
    print(f"メソッド一覧: {methods}")
    
    # ステータス更新関連のメソッドを詳細調査
    status_methods = [m for m in methods if 'status' in m.lower() or 'update' in m.lower()]
    print(f"ステータス関連メソッド: {status_methods}")
    
    # _update_task_status メソッドの存在確認
    if hasattr(CompleteEngineUltimate, '_update_task_status'):
        method = getattr(CompleteEngineUltimate, '_update_task_status')
        print(f"\n📋 _update_task_status メソッド:")
        print(f"  ソースファイル: {inspect.getfile(method)}")
        print(f"  行番号: {inspect.getsourcelines(method)[1]}")
        
        # ソースコード表示
        lines = inspect.getsourcelines(method)[0]
        print(f"  実装 (最初の10行):")
        for i, line in enumerate(lines[:10]):
            print(f"    {i+1}: {line.rstrip()}")
    else:
        print("❌ _update_task_status メソッドが見つかりません")
    
    # execute_task メソッドの確認
    if hasattr(CompleteEngineUltimate, 'execute_task'):
        method = getattr(CompleteEngineUltimate, 'execute_task')
        print(f"\n📋 execute_task メソッドのステータス更新部分:")
        lines = inspect.getsourcelines(method)[0]
        
        # ステータス更新に関連する行を検索
        status_lines = []
        for i, line in enumerate(lines):
            if 'status' in line.lower() or 'completed' in line.lower() or 'update' in line.lower():
                status_lines.append((i, line.rstrip()))
        
        print(f"  関連行数: {len(status_lines)}")
        for line_num, line in status_lines[:15]:  # 最初の15行まで表示
            print(f"    {line_num+1}: {line}")

if __name__ == "__main__":
    trace_status_flow()
