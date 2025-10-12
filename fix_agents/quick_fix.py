#!/usr/bin/env python3
"""
クイック修正スクリプト - インポートエラーを自動修正
使い方: python quick_fix.py
"""

import os
import re
from pathlib import Path
import shutil
from datetime import datetime


def create_backup(file_path: Path) -> Path:
    """ファイルのバックアップを作成"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.with_suffix(f'.backup_{timestamp}{file_path.suffix}')
    shutil.copy2(file_path, backup_path)
    print(f"✅ バックアップ作成: {backup_path}")
    return backup_path


def fix_wp_plugin_manager(base_dir: Path) -> bool:
    """wp_plugin_manager.py のインポートエラーを修正"""
    file_path = base_dir / "wordpress" / "wp_plugin_manager.py"
    
    if not file_path.exists():
        print(f"⚠️ ファイルが見つかりません: {file_path}")
        return False
    
    print(f"\n🔧 修正中: {file_path}")
    
    # バックアップ作成
    create_backup(file_path)
    
    # ファイルを読み込み
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 既に修正済みかチェック
    if 'from typing import' in content and 'List' in content:
        print("✅ 既に修正済みです")
        return True
    
    # インポート文を探す
    import_pattern = r'^(import logging\s*\n)'
    
    # 新しいインポート文
    new_imports = '''import logging
import asyncio
from typing import Dict, List, Optional, Any
from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

'''
    
    # 置換
    if re.search(import_pattern, content, re.MULTILINE):
        content = re.sub(import_pattern, new_imports, content, count=1, flags=re.MULTILINE)
        print("✅ インポート文を追加しました")
    else:
        # パターンが見つからない場合は先頭に追加
        lines = content.split('\n')
        # docstring の後に挿入
        insert_index = 0
        for i, line in enumerate(lines):
            if '"""' in line or "'''" in line:
                # docstringの終わりを探す
                for j in range(i+1, len(lines)):
                    if '"""' in lines[j] or "'''" in lines[j]:
                        insert_index = j + 1
                        break
                break
        
        if insert_index == 0:
            insert_index = 1  # ファイルの最初の行の後
        
        lines.insert(insert_index, '\n' + new_imports.strip())
        content = '\n'.join(lines)
        print("✅ インポート文を先頭に追加しました")
    
    # ファイルに書き込み
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ wp_plugin_manager.py の修正完了")
    return True


def fix_wordpress_init(base_dir: Path) -> bool:
    """wordpress/__init__.py のインポートエラーを修正"""
    file_path = base_dir / "wordpress" / "__init__.py"
    
    if not file_path.exists():
        print(f"⚠️ ファイルが見つかりません: {file_path}")
        return False
    
    print(f"\n🔧 チェック中: {file_path}")
    
    # ファイルを読み込み
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # エラーハンドリングが必要か確認
    needs_fix = False
    
    if 'from .wp_agent import WordPressAgent' in content:
        if 'try:' not in content:
            needs_fix = True
    
    if not needs_fix:
        print("✅ 修正不要です")
        return True
    
    # バックアップ作成
    create_backup(file_path)
    
    # エラーハンドリング付きインポートに変更
    new_content = '''"""
WordPress パッケージ
"""

try:
    from .wp_agent import WordPressAgent
    from .wp_utils import WordPressConfig, task_router
    __all__ = ['WordPressAgent', 'WordPressConfig', 'task_router']
except ImportError as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ WordPress モジュールのインポート失敗: {e}")
    WordPressAgent = None
    WordPressConfig = None
    task_router = None
    __all__ = []
'''
    
    # ファイルに書き込み
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ wordpress/__init__.py の修正完了")
    return True


def check_all_typing_imports(base_dir: Path) -> list:
    """全Pythonファイルの typing インポートをチェック"""
    print("\n🔍 全ファイルのチェック中...")
    
    issues = []
    
    for py_file in base_dir.rglob("*.py"):
        if 'venv' in str(py_file) or '__pycache__' in str(py_file):
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # List, Dict などを使っているがインポートしていない
            if ('List[' in content or 'Dict[' in content or 
                'Optional[' in content or 'Tuple[' in content):
                if 'from typing import' not in content:
                    issues.append(str(py_file))
        except Exception as e:
            print(f"⚠️ {py_file} の読み込みエラー: {e}")
    
    return issues


def fix_task_executor_imports(base_dir: Path) -> bool:
    """task_executor.py のインポートエラーを修正"""
    file_path = base_dir / "task_executor.py"
    
    if not file_path.exists():
        print(f"⚠️ ファイルが見つかりません: {file_path}")
        return False
    
    print(f"\n🔧 修正中: {file_path}")
    
    # バックアップ作成
    create_backup(file_path)
    
    # ファイルを読み込み
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 既に修正済みかチェック
    if 'from tools.sheets_manager import GoogleSheetsManager' in content:
        print("✅ 既に修正済みです")
        return True
    
    # 正しいインポート順序
    correct_imports = '''"""
Task Executor - タスク実行コントローラー
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# ===== 設定とユーティリティ =====
from configuration.config_utils import ErrorHandler, config

# ===== データ管理 =====
from tools.sheets_manager import GoogleSheetsManager

# ===== エラーハンドラー（オプション） =====
try:
    from tools.error_handler_enhanced import (
        EnhancedErrorHandler,
        TaskErrorHandler
    )
    HAS_ENHANCED_HANDLER = True
except ImportError:
    HAS_ENHANCED_HANDLER = False
    import warnings
    warnings.warn("⚠️ error_handler_enhanced未検出（標準エラーハンドラー使用）")

# ===== 分離モジュール =====
try:
    from task_executor_content import ContentTaskExecutor
    from task_executor_ma import MATaskExecutor
    HAS_SPECIALIZED_EXECUTORS = True
except ImportError:
    HAS_SPECIALIZED_EXECUTORS = False
    import warnings
    warnings.warn("⚠️ task_executor_content/ma が見つかりません")

# ===== WordPress連携（オプション） =====
try:
    from wordpress.wp_utils import task_router
    HAS_TASK_ROUTER = True
except ImportError:
    HAS_TASK_ROUTER = False
    task_router = None
    import warnings
    warnings.warn("⚠️ wordpress.wp_utils.task_router が見つかりません")

logger = logging.getLogger(__name__)


'''
    
    # 既存のインポート部分を探して置き換え
    # クラス定義の前までを置き換える
    class_pattern = r'class TaskExecutor:'
    class_match = re.search(class_pattern, content)
    
    if class_match:
        # クラス定義以降を保持
        class_and_rest = content[class_match.start():]
        # 新しいインポート + クラス定義以降
        new_content = correct_imports + class_and_rest
    else:
        print("⚠️ TaskExecutor クラスが見つかりません")
        return False
    
    # ファイルに書き込み
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ task_executor.py のインポート修正完了")
    return True


def main():
    """メイン処理"""
    print("="*60)
    print("🔧 クイック修正スクリプト v2")
    print("="*60)
    
    # カレントディレクトリを取得
    base_dir = Path.cwd()
    print(f"\n📁 作業ディレクトリ: {base_dir}")
    
    # 修正実行
    success_count = 0
    
    # 1. wp_plugin_manager.py の修正
    if fix_wp_plugin_manager(base_dir):
        success_count += 1
    
    # 2. wordpress/__init__.py の修正
    if fix_wordpress_init(base_dir):
        success_count += 1
    
    # 3. task_executor.py の修正（新規追加）
    if fix_task_executor_imports(base_dir):
        success_count += 1
    
    # 4. その他のファイルをチェック
    issues = check_all_typing_imports(base_dir)
    
    if issues:
        print(f"\n⚠️ 追加で修正が必要な可能性のあるファイル: {len(issues)}件")
        for issue_file in issues[:10]:  # 最初の10件のみ表示
            print(f"  - {issue_file}")
        
        if len(issues) > 10:
            print(f"  ... 他 {len(issues) - 10} 件")
    
    # 結果サマリー
    print("\n" + "="*60)
    print("📊 修正完了")
    print("="*60)
    print(f"✅ 修正成功: {success_count} ファイル")
    
    if issues:
        print(f"⚠️ 要確認: {len(issues)} ファイル")
        print("\n💡 ヒント: 各ファイルで以下を追加してください:")
        print("   from typing import Dict, List, Optional, Any")
    
    print("\n🎉 修正完了！")
    print("次のコマンドで実行してください:")
    print("   python run_multi_agent.py --auto")


if __name__ == "__main__":
    main()