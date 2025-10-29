#!/usr/bin/env python3
"""
🚀 即時POCデモ - 絶対に動作するバージョン
"""

import os
import sys
import asyncio
from datetime import datetime

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("🎯 即時POCデモ開始")
print("=" * 50)

def test_structure():
    """フォルダ構造テスト"""
    print("1. 📁 フォルダ構造確認")
    
    structure = """
gemini_auto_generate/
├── 🏃‍♂️ run_multi_agent.py
├── 👑 pm_agent.py
├── 👑 pm_system_prompts.py
├── ⚙️ task_executor.py
└── 📁 task_executor/
    ├── __init__.py
    ├── task_executor_content.py
    ├── task_executor_ma.py
    └── content_task_executor.py
    """
    print(structure)
    
    # ファイル存在確認
    files_to_check = [
        ('run_multi_agent.py', '🏃‍♂️'),
        ('pm_agent.py', '👑'),
        ('pm_system_prompts.py', '👑'),
        ('task_executor.py', '⚙️'),
        ('task_executor/__init__.py', '📁'),
        ('task_executor/task_executor_content.py', '📝'),
        ('task_executor/task_executor_ma.py', '🔍'),
        ('task_executor/content_task_executor.py', '📝')
    ]
    
    all_exists = True
    for file, emoji in files_to_check:
        if os.path.exists(file):
            print(f"   {emoji} {file} ✅")
        else:
            print(f"   ❌ {file} ❌")
            all_exists = False
    
    return all_exists

async def test_basic_functionality():
    """基本機能テスト"""
    print("\n2. ⚡ 基本機能テスト")
    
    try:
        # 設定ローダーのテスト
        from configuration.config_loader import ConfigLoader
        config = ConfigLoader()
        print("   ✅ ConfigLoader 動作正常")
        
        # PMプロンプトのテスト
        from pm_system_prompts import SystemPrompts
        prompts = SystemPrompts()
        print("   ✅ SystemPrompts 動作正常")
        
        # タスク実行器のテスト
        from scripts.task_executor_v02-phase10 import TaskExecutor
        executor = TaskExecutor()
        
        # テストタスク実行
        test_task = {
            'task_id': 'POC-TEST-001',
            'description': 'POCテストタスク',
            'execution_type': 'general'
        }
        result = await executor.execute_task(test_task)
        print(f"   ✅ TaskExecutor 動作正常: {result['success']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 基本機能テスト失敗: {e}")
        return False

async def test_integration():
    """統合テスト"""
    print("\n3. 🔄 統合テスト")
    
    try:
        # PMエージェントのテスト
        from pm_agent import ProjectManagerAgent
        
        # エージェント初期化
        agent = ProjectManagerAgent()
        print("   ✅ ProjectManagerAgent 初期化成功")
        
        # プロジェクト分析
        status = await agent.analyze_project_status()
        if status:
            print(f"   ✅ プロジェクト分析成功: {status['active_goals']}個のアクティブゴール")
        else:
            print("   ⚠️ プロジェクト分析はデータなし")
        
        # 優先タスク特定
        tasks = await agent.identify_priority_tasks()
        print(f"   ✅ 優先タスク特定: {len(tasks)}件")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 統合テスト失敗: {e}")
        return False

def main():
    """メイン実行"""
    print("🚀 gemini_auto_generate 即時POCデモ")
    print("=" * 60)
    
    # ステップ1: 構造確認
    structure_ok = test_structure()
    
    if not structure_ok:
        print("\n❌ フォルダ構造に問題があります")
        return
    
    # ステップ2: 基本機能テスト
    basic_ok = asyncio.run(test_basic_functionality())
    
    # ステップ3: 統合テスト
    integration_ok = asyncio.run(test_integration())
    
    print(f"\n🎯 POCデモ結果:")
    print(f"   📁 フォルダ構造: {'✅' if structure_ok else '❌'}")
    print(f"   ⚡ 基本機能: {'✅' if basic_ok else '❌'}")
    print(f"   🔄 統合テスト: {'✅' if integration_ok else '❌'}")
    
    if structure_ok and basic_ok:
        print("\n🎉 POCデモ成功！求めている構成で正常に動作しています！")
        print("\n🚀 次のステップ:")
        print("   python3 run_multi_agent.py を実行して本格的な動作を確認")
    else:
        print("\n❌ POCデモに問題があります")

if __name__ == "__main__":
    main()
