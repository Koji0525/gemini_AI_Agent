#!/usr/bin/env python3
"""
インポートパス自動修正スクリプト
ファイル移動後のインポート文を自動的に修正します
"""

import os
import re
from pathlib import Path

# 移動マッピング（モジュール名 → 新しいパッケージパス）
IMPORT_MAPPINGS = {
    # browser_control/ に移動したモジュール
    'browser_controller': 'browser_control.browser_controller',
    'browser_lifecycle': 'browser_control.browser_lifecycle',
    'brower_cookie_and_session': 'browser_control.brower_cookie_and_session',
    'browser_ai_chat_agent': 'browser_control.browser_ai_chat_agent',
    'browser_wp_session_manager': 'browser_control.browser_wp_session_manager',
    'safe_browser_manager': 'browser_control.safe_browser_manager',
    'safe_cleanup': 'browser_control.safe_cleanup',
    
    # core_agents/ に移動したモジュール
    'pm_agent': 'core_agents.pm_agent',
    'dev_agent': 'core_agents.dev_agent',
    'dev_agent_acf': 'core_agents.dev_agent_acf',
    'review_agent': 'core_agents.review_agent',
    'fixed_review_agent': 'core_agents.fixed_review_agent',
    'code_review_agent': 'core_agents.code_review_agent',
    'content_writer_agent': 'core_agents.content_writer_agent',
    'design_agent': 'core_agents.design_agent',
    'system_integration_agent': 'core_agents.system_integration_agent',
    'command_monitor_agent': 'core_agents.command_monitor_agent',
    'github_agent': 'core_agents.github_agent',
    'pm_system_prompts': 'core_agents.pm_system_prompts',
    'review_agent_prompts': 'core_agents.review_agent_prompts',
    'review_agent_prompts_ACF': 'core_agents.review_agent_prompts_ACF',
    
    # configuration/ に移動したモジュール
    'config_hybrid': 'configuration.config_hybrid',
    'config_utils': 'configuration.config_utils',
    'check_config': 'configuration.check_config',
    
    # tools/ に移動したモジュール
    'sheets_manager': 'tools.sheets_manager',
    'cloud_storage_manager': 'tools.cloud_storage_manager',
    'error_handler_enhanced': 'tools.error_handler_enhanced',
    'compatibility_fix': 'tools.compatibility_fix',
    'view_stats': 'tools.view_stats',
    'view_detailed_stats': 'tools.view_detailed_stats',
    
    # scripts/ に移動したモジュール
    'run_multi_agent': 'scripts.run_multi_agent',
    'task_executor': 'scripts.task_executor',
    'wordpress_task_executor': 'scripts.wordpress_task_executor',
    'main_automator': 'scripts.main_automator',
}

def fix_imports_in_file(filepath, dry_run=True):
    """
    単一ファイル内のインポート文を修正
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        modified = False
        changes = []
        
        # パターン1: from module import ...
        for old_module, new_module in IMPORT_MAPPINGS.items():
            # from module import X
            pattern1 = rf'\bfrom\s+{re.escape(old_module)}\s+import\s+'
            if re.search(pattern1, content):
                new_content = re.sub(pattern1, f'from {new_module} import ', content)
                if new_content != content:
                    changes.append(f"  📝 from {old_module} → from {new_module}")
                    content = new_content
                    modified = True
            
            # import module (as alias)
            pattern2 = rf'\bimport\s+{re.escape(old_module)}(\s+as\s+\w+)?'
            if re.search(pattern2, content):
                def replace_import(match):
                    alias = match.group(1) if match.group(1) else ''
                    return f'import {new_module}{alias}'
                
                new_content = re.sub(pattern2, replace_import, content)
                if new_content != content:
                    changes.append(f"  📝 import {old_module} → import {new_module}")
                    content = new_content
                    modified = True
        
        if modified:
            print(f"\n✏️  {filepath}")
            for change in changes:
                print(change)
            
            if not dry_run:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✅ 保存しました")
        
        return modified
    
    except Exception as e:
        print(f"❌ エラー: {filepath} - {e}")
        return False

def scan_and_fix_imports(dry_run=True):
    """
    プロジェクト全体をスキャンしてインポートを修正
    """
    root = Path('.')
    
    # 修正対象のディレクトリとファイル
    target_paths = [
        root,  # ルートディレクトリ
        root / 'agents',
        root / 'fix_agents',
        root / 'task_executor',
        root / 'wordpress',
        root / 'wordpress' / 'wp_dev',
        root / 'content_writers',
        root / 'data_models',
        root / 'test',
        root / 'scripts',
        root / 'browser_control',
        root / 'core_agents',
        root / 'configuration',
        root / 'tools',
    ]
    
    print(f"{'=' * 70}")
    print(f"{'DRY RUN MODE - 実際には修正しません' if dry_run else '実際にファイルを修正します'}")
    print(f"{'=' * 70}")
    
    modified_count = 0
    
    for target_path in target_paths:
        if not target_path.exists():
            continue
        
        # .pyファイルを再帰的に検索
        if target_path.is_dir():
            py_files = list(target_path.glob('*.py'))
            for subdir in target_path.iterdir():
                if subdir.is_dir() and not subdir.name.startswith('.'):
                    py_files.extend(subdir.glob('*.py'))
        else:
            py_files = [target_path]
        
        for py_file in py_files:
            if py_file.name.startswith('.'):
                continue
            if fix_imports_in_file(py_file, dry_run):
                modified_count += 1
    
    print(f"\n{'=' * 70}")
    print(f"📊 統計: {modified_count} ファイルを修正しました")
    print(f"{'=' * 70}")
    
    if dry_run:
        print("\n💡 これはドライランです。実際に修正するには:")
        print("   python fix_imports.py --execute")

if __name__ == '__main__':
    import sys
    dry_run = '--execute' not in sys.argv
    scan_and_fix_imports(dry_run=dry_run)
