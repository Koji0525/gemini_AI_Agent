#!/usr/bin/env python3
"""
保護ファイルチェッカー

目的: 既存の保護ファイルが意図せず変更されていないかチェック
使用タイミング: Git commit前、CI/CD
"""
import sys
import subprocess
from pathlib import Path
from typing import List, Dict

PROJECT_ROOT = Path(__file__).parent.parent.parent

# 保護ファイルリスト（変更禁止）
PROTECTED_FILES = [
    'agents/complete_engine_ultimate.py',
    'tools/sheets_manager.py',
    'tools/safe_sheets_wrapper.py',
    'knowledge_system/core_agents/knowledge_manager.py',
    'tools/base_data_accessor.py',
    'agents/task_execution/high_quality_executor_v8.py',
    'agents/quality_evaluation/quality_evaluator.py',
    'agents/self_healing/self_healing_agent.py',
]

def check_git_changes() -> List[str]:
    """Gitでステージングされた変更を確認"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', '--cached'],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        
        if result.returncode == 0:
            return result.stdout.strip().split('\n')
        else:
            # Gitリポジトリでない場合など
            return []
    except:
        return []

def check_protected_files() -> Dict:
    """保護ファイルが変更されていないか確認"""
    changed_files = check_git_changes()
    
    # 保護ファイルの変更を検出
    protected_changed = []
    for changed in changed_files:
        if changed in PROTECTED_FILES:
            protected_changed.append(changed)
    
    return {
        'all_changed': changed_files,
        'protected_changed': protected_changed,
        'has_violation': len(protected_changed) > 0
    }

def main():
    """メイン処理"""
    print("="*60)
    print("🔒 保護ファイルチェック")
    print("="*60)
    
    result = check_protected_files()
    
    print(f"\n📊 チェック結果:")
    print(f"   変更ファイル数: {len(result['all_changed'])}")
    print(f"   保護ファイル変更: {len(result['protected_changed'])}")
    
    if result['has_violation']:
        print(f"\n❌ 以下の保護ファイルが変更されています：")
        for f in result['protected_changed']:
            print(f"   - {f}")
        
        print(f"\n⚠️  保護ファイルの変更は禁止されています。")
        print(f"   新機能は拡張ファイルで実装してください。")
        print(f"\n例:")
        print(f"   ❌ tools/sheets_manager.py を編集")
        print(f"   ✅ tools/sheets_manager_enhanced.py を新規作成")
        
        return 1
    else:
        print(f"\n✅ 保護ファイルへの変更はありません")
        return 0

if __name__ == '__main__':
    sys.exit(main())
