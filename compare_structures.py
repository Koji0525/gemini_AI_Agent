#!/usr/bin/env python3
"""
添付リストと現在の構造を比較
"""

# 添付リストのファイル（POC_STRUCTURE）
POC_FILES = """
analyze_project_structure.py
autonomous_agent_system.py
autonomous_ma_portal_system.py
autonomous_ma_portal_system_fixed.py
autonomous_system.py
autonomous_system_final.py
auto_fix_from_log.py
brower_cookie_and_session.py
browser_ai_chat_agent.py
browser_controller.py
browser_lifecycle.py
browser_wp_session_manager.py
check_config.py
check_review_agent.py
check_task_progress.py
cloud_storage_manager.py
code_review_agent.py
command_monitor_agent.py
compatibility_fix.py
complete_fix.py
config_hybrid.py
config_utils.py
content_writer_agent.py
continuous_monitor.py
continuous_pm_tasks_monitor.py
continuous_system_with_review.py
continuous_task_monitor.py
create_active_system_map.py
create_draft_with_creator.py
create_wordpress_draft.py
design_agent.py
dev_agent.py
dev_agent_acf.py
edit_post_with_editor.py
error_auto_fix_system.py
error_handler_enhanced.py
example_usage.py
final_complete_fix.py
final_fix.py
find_active_files.py
fixed_review_agent.py
fix_all_errors.py
fix_main_hybrid_fix.py
fix_review_agent_ai.py
fix_sheets_auth.py
fix_sheets_header.py
fix_wp_agent.py
fix_wp_agent_v2.py
github_agent.py
identify_backup_files.py
integrated_autonomous_system.py
integrated_autonomous_system_v2.py
integrated_system_fixed.py
integrated_system_with_review.py
integrated_task_manager.py
integrated_task_manager_v2.py
main_automator.py
main_hybrid_fix.py
organize_files.py
pm_agent.py
pm_system_prompts.py
precise_fix.py
review_agent.py
review_agent_prompts.py
review_agent_prompts_ACF.py
run_multi_agent.py
run_multi_agent_no_sheets.py
safe_browser_manager.py
safe_cleanup.py
safe_wordpress_executor.py
sheets_manager.py
system_integration_agent.py
task_executor.py
task_manager_with_sheets.py
task_manager_wordpress.py
test_auto_fix_demo.py
test_full_integration.py
test_multiple_errors.py
test_real_bug.py
test_tasks.py
test_tasks_buggy.py
test_tasks_practical.py
test_tasks_real.py
test_tasks_working.py
trigger_auto_fix.py
view_detailed_stats.py
view_stats.py
wordpress_task_executor.py
wordpress_task_executor_fixed.py
""".strip().split('\n')

import json
from pathlib import Path

def find_all_py_files():
    """現在のプロジェクトの全Pythonファイルを取得"""
    current_files = set()
    
    root = Path('.')
    exclude_dirs = {
        '.git', '__pycache__', 'venv', '.vscode', 
        'node_modules', 'browser_data', 'backups'
    }
    
    # ルートのファイル
    for file in root.glob('*.py'):
        current_files.add(file.name)
    
    # 各パッケージ内のファイル（相対パスで）
    for item in root.iterdir():
        if item.is_dir() and item.name not in exclude_dirs:
            for py_file in item.rglob('*.py'):
                # パッケージ名/ファイル名 の形式
                rel_path = py_file.relative_to(root)
                # ルートレベルのファイル名だけを追加
                if '/' in str(rel_path):
                    current_files.add(py_file.name)
                else:
                    current_files.add(str(rel_path))
    
    return current_files

def main():
    print("🔍 ファイル比較を開始...")
    
    poc_set = set(POC_FILES)
    current_set = find_all_py_files()
    
    # POCにあって現在にないファイル
    missing = poc_set - current_set
    
    # 現在にあってPOCにないファイル（新規作成）
    new_files = current_set - poc_set
    
    print("\n" + "=" * 70)
    print("📊 比較結果")
    print("=" * 70)
    
    if missing:
        print(f"\n❌ POCにあってGitHubにないファイル ({len(missing)}個):")
        for file in sorted(missing):
            print(f"  - {file}")
    else:
        print("\n✅ POCの全ファイルがGitHubに存在します")
    
    if new_files:
        print(f"\n✨ 新規作成されたファイル ({len(new_files)}個):")
        for file in sorted(new_files)[:20]:  # 最初の20個
            print(f"  - {file}")
        if len(new_files) > 20:
            print(f"  ... and {len(new_files) - 20} more")
    
    print(f"\n📈 統計:")
    print(f"  - POCファイル数: {len(poc_set)}")
    print(f"  - 現在のファイル数: {len(current_set)}")
    print(f"  - 不足: {len(missing)}")
    print(f"  - 新規: {len(new_files)}")

if __name__ == '__main__':
    main()
