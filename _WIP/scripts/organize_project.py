#!/usr/bin/env python3
"""
プロジェクト整理スクリプト
ルートディレクトリのファイルを適切なパッケージに移動します
"""

import os
import shutil
from pathlib import Path

# 移動マッピング定義
MOVE_MAPPINGS = {
    # ブラウザ制御関連 → browser_control/
    'browser_control': [
        'browser_controller.py',
        'browser_lifecycle.py',
        'brower_cookie_and_session.py',
        'browser_ai_chat_agent.py',
        'browser_wp_session_manager.py',
        'safe_browser_manager.py',
        'safe_cleanup.py'
    ],
    
    # コアエージェント → core_agents/
    'core_agents': [
        'pm_agent.py',
        'dev_agent.py',
        'dev_agent_acf.py',
        'review_agent.py',
        'fixed_review_agent.py',
        'code_review_agent.py',
        'content_writer_agent.py',
        'design_agent.py',
        'system_integration_agent.py',
        'command_monitor_agent.py',
        'github_agent.py',
        'pm_system_prompts.py',
        'review_agent_prompts.py',
        'review_agent_prompts_ACF.py'
    ],
    
    # 設定管理 → configuration/
    'configuration': [
        'config_hybrid.py',
        'config_utils.py',
        'check_config.py'
    ],
    
    # ツール/ユーティリティ → tools/
    'tools': [
        'sheets_manager.py',
        'cloud_storage_manager.py',
        'error_handler_enhanced.py',
        'compatibility_fix.py',
        'view_stats.py',
        'view_detailed_stats.py'
    ],
    
    # 実行スクリプト → scripts/
    'scripts': [
        'run_multi_agent.py',
        'run_multi_agent_no_sheets.py',
        'wordpress_task_executor.py',
        'wordpress_task_executor_fixed.py',
        'task_executor.py',
        'main_automator.py'
    ],
    
    # テスト関連 → test/
    'test': [
        'test_tasks.py',
        'test_full_integration.py',
        'test_auto_fix_demo.py',
        'test_autonomous_simple.py',
        'test_multiple_errors.py',
        'test_real_bug.py',
        'test_tasks_buggy.py',
        'test_tasks_practical.py',
        'test_tasks_real.py',
        'test_tasks_working.py',
        'example_usage.py',
        'check_review_agent.py',
        'internal_test.py',
        'real_integration_test.py',
        'real_task_test.py',
        'final_integration_test.py',
        'full_autonomous_test.py'
    ],
    
    # アーカイブ（古いバージョン、POC） → archive/
    'archive': [
        'autonomous_system_final.py',
        'autonomous_ma_portal_system.py',
        'autonomous_ma_portal_system_fixed.py',
        'autonomous_agent_system.py',
        'autonomous_agent_system_v2.py',
        'integrated_autonomous_system.py',
        'integrated_autonomous_system_v2.py',
        'integrated_system_fixed.py',
        'complete_fix.py',
        'final_fix.py',
        'final_complete_fix.py',
        'precise_fix.py',
        'fix_all_errors.py',
        'fix_wp_agent.py',
        'fix_wp_agent_v2.py',
        'fix_main_hybrid_fix.py',
        'fix_sheets_auth.py',
        'fix_sheets_header.py',
        'fix_review_agent_ai.py',
        'auto_fix_from_log.py',
        'trigger_auto_fix.py',
        'error_auto_fix_system.py'
    ]
}

def move_files(dry_run=True):
    """
    ファイルを移動
    dry_run=True: 実際には移動せず、何が移動されるかを表示
    dry_run=False: 実際に移動を実行
    """
    root = Path('.')
    moved_count = 0
    skipped_count = 0
    
    print(f"{'=' * 60}")
    print(f"{'DRY RUN MODE - 実際には移動しません' if dry_run else '実際にファイルを移動します'}")
    print(f"{'=' * 60}\n")
    
    for target_dir, files in MOVE_MAPPINGS.items():
        print(f"\n📁 {target_dir}/ への移動:")
        
        for filename in files:
            source = root / filename
            destination = root / target_dir / filename
            
            if source.exists():
                if destination.exists():
                    print(f"  ⚠️  SKIP: {filename} (すでに存在)")
                    skipped_count += 1
                else:
                    if dry_run:
                        print(f"  ➡️  {filename}")
                    else:
                        try:
                            shutil.move(str(source), str(destination))
                            print(f"  ✅ MOVED: {filename}")
                        except Exception as e:
                            print(f"  ❌ ERROR: {filename} - {e}")
                    moved_count += 1
            else:
                # ファイルが存在しない場合は何も表示しない（既に移動済みの可能性）
                pass
    
    print(f"\n{'=' * 60}")
    print(f"📊 統計:")
    print(f"  - 移動予定/移動完了: {moved_count}ファイル")
    print(f"  - スキップ: {skipped_count}ファイル")
    print(f"{'=' * 60}\n")
    
    if dry_run:
        print("💡 これはドライランです。実際に移動するには:")
        print("   python organize_project.py --execute")

if __name__ == '__main__':
    import sys
    
    # --execute オプションがあれば実際に移動、なければドライラン
    dry_run = '--execute' not in sys.argv
    move_files(dry_run=dry_run)
