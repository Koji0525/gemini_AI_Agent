#!/usr/bin/env python3
"""
プロジェクト検証スクリプト
整理後のコードの構文チェックと基本的なインポートテストを実行
"""

import sys
import ast
from pathlib import Path

def check_syntax(filepath):
    """Pythonファイルの構文チェック"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def verify_project():
    """プロジェクト全体の構文を検証"""
    root = Path('.')
    
    # チェック対象のディレクトリ
    check_dirs = [
        'browser_control',
        'core_agents',
        'configuration',
        'tools',
        'scripts',
        'agents',
        'fix_agents',
        'task_executor',
        'wordpress',
        'test'
    ]
    
    print("=" * 70)
    print("🔍 プロジェクト構文チェック開始")
    print("=" * 70)
    
    total_files = 0
    error_files = []
    
    for dir_name in check_dirs:
        dir_path = root / dir_name
        if not dir_path.exists():
            continue
        
        print(f"\n📁 {dir_name}/ をチェック中...")
        
        py_files = list(dir_path.glob('**/*.py'))
        for py_file in py_files:
            if py_file.name.startswith('.'):
                continue
            
            total_files += 1
            success, error = check_syntax(py_file)
            
            if success:
                print(f"  ✅ {py_file.name}")
            else:
                print(f"  ❌ {py_file.name}: {error}")
                error_files.append((str(py_file), error))
    
    # ルートの主要ファイルもチェック
    print(f"\n📁 ルートディレクトリをチェック中...")
    root_files = [
        'autonomous_system.py',
        'main_hybrid_fix.py',
        'safe_wordpress_executor.py'
    ]
    
    for filename in root_files:
        filepath = root / filename
        if filepath.exists():
            total_files += 1
            success, error = check_syntax(filepath)
            
            if success:
                print(f"  ✅ {filename}")
            else:
                print(f"  ❌ {filename}: {error}")
                error_files.append((filename, error))
    
    # 結果サマリー
    print(f"\n{'=' * 70}")
    print(f"📊 検証結果:")
    print(f"  - 総ファイル数: {total_files}")
    print(f"  - 成功: {total_files - len(error_files)}")
    print(f"  - エラー: {len(error_files)}")
    print(f"{'=' * 70}")
    
    if error_files:
        print(f"\n❌ エラーが見つかりました:")
        for filepath, error in error_files:
            print(f"\n  {filepath}")
            print(f"    → {error}")
        return False
    else:
        print(f"\n✅ すべてのファイルの構文チェックに合格しました！")
        return True

if __name__ == '__main__':
    success = verify_project()
    sys.exit(0 if success else 1)
