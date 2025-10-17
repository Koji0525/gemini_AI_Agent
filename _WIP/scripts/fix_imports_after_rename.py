#!/usr/bin/env python3
"""
リネーム後のインポート文を自動修正
enhanced_browser_controller → browser_controller
"""

from pathlib import Path
import re

def fix_imports():
    print("🔧 インポート文自動修正")
    print("=" * 70)
    
    # 修正対象ファイル
    files_to_fix = [
        "scripts/task_executor.py",
        "core_agents/design_agent.py",
        "core_agents/dev_agent.py",
        "core_agents/review_agent.py",
        "_WIP/test_browser_setup.py",
        "_WIP/test_browser_agent_integration.py",
        "_WIP/test_design_agent_browser.py",
        "_WIP/test_dev_agent_browser.py",
        "_WIP/test_review_agent_fixed.py",
        "_WIP/test_all_agents_browser.py",
        "_WIP/test_task_executor_integration.py",
        "_WIP/test_task_executor_debug.py"
    ]
    
    # 置換パターン
    old_import = "from browser_control.enhanced_browser_controller import"
    new_import = "from browser_control.browser_controller import"
    
    fixed_count = 0
    
    for file_path_str in files_to_fix:
        file_path = Path(file_path_str)
        
        if not file_path.exists():
            print(f"⚠️ スキップ（不在）: {file_path}")
            continue
        
        # 読み込み
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 置換が必要か確認
        if old_import in content:
            new_content = content.replace(old_import, new_import)
            
            # 保存
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ 修正: {file_path}")
            fixed_count += 1
        else:
            print(f"   問題なし: {file_path}")
    
    print("\n" + "=" * 70)
    print(f"✅ インポート修正完了！（{fixed_count}ファイル）")
    
    return fixed_count > 0

if __name__ == "__main__":
    fix_imports()
