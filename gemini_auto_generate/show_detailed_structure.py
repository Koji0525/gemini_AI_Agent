#!/usr/bin/env python3
"""
📁 詳細なファイル構造表示 - 全ファイルを含む
"""

import os
import glob

def show_detailed_structure():
    print("📁 gemini_auto_generate 詳細ファイル構造")
    print("=" * 70)
    
    base_dir = "."
    
    # すべてのファイルを収集
    all_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, base_dir)
            all_files.append(rel_path)
    
    # ファイルタイプ別に分類
    file_categories = {
        '🐍 Pythonファイル': [],
        '📁 設定ファイル': [],
        '📊 データファイル': [],
        '📝 ドキュメント': [],
        '🔧 その他': []
    }
    
    for file_path in sorted(all_files):
        if file_path.endswith('.py'):
            file_categories['🐍 Pythonファイル'].append(file_path)
        elif any(file_path.endswith(ext) for ext in ['.json', '.yaml', '.yml', '.ini', '.cfg', '.conf']):
            file_categories['📁 設定ファイル'].append(file_path)
        elif any(file_path.endswith(ext) for ext in ['.csv', '.txt', '.md', '.log']):
            file_categories['📊 データファイル'].append(file_path)
        elif any(file_path.endswith(ext) for ext in ['.md', '.rst', '.txt']):
            file_categories['📝 ドキュメント'].append(file_path)
        else:
            file_categories['🔧 その他'].append(file_path)
    
    # 各カテゴリを表示
    total_files = 0
    for category, files in file_categories.items():
        if files:
            print(f"\n{category} ({len(files)}個):")
            for file_path in files:
                emoji = get_file_emoji(os.path.basename(file_path))
                print(f"   {emoji} {file_path}")
            total_files += len(files)
    
    print(f"\n📊 総ファイル数: {total_files}個")
    
    # システム概要
    print(f"\n🎯 システム概要:")
    print(f"   • メイン実行ファイル: {len([f for f in file_categories['🐍 Pythonファイル'] if not '/' in f])}個")
    print(f"   • タスク実行モジュール: {len([f for f in file_categories['🐍 Pythonファイル'] if 'task_executor' in f])}個")
    print(f"   • 設定ファイル: {len(file_categories['📁 設定ファイル'])}個")
    print(f"   • ユーティリティスクリプト: {len([f for f in file_categories['🐍 Pythonファイル'] if 'scripts' in f])}個")

def get_file_emoji(filename):
    """ファイル名に基づいて絵文字を返す"""
    emoji_map = {
        'run_multi_agent.py': '🏃‍♂️',
        'pm_agent.py': '👑',
        'pm_system_prompts.py': '👑',
        'task_executor.py': '⚙️',
        'task_executor_content.py': '📝',
        'task_executor_ma.py': '🔍',
        'content_task_executor.py': '📝',
        'config_loader.py': '⚙️',
        '__init__.py': '📁',
        'run_quick_poc.py': '🎯',
        'run_poc_simple.py': '🎯',
        'run_complete_poc.py': '🎯',
        'show_detailed_structure.py': '📁',
        'sync_settings.py': '⚙️',
        '.gitignore': '🔧',
        'README.md': '📖'
    }
    return emoji_map.get(filename, '📄')

if __name__ == "__main__":
    show_detailed_structure()
