#!/usr/bin/env python3
"""
プロジェクト構造可視化ツール
フォルダとファイルを見やすく表示

v1.0 - 初回実装
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


class ProjectStructureVisualizer:
    """プロジェクト構造を可視化するクラス"""
    
    # ファイルタイプ別の絵文字
    FILE_ICONS = {
        '.py': '🐍',
        '.md': '📝',
        '.txt': '��',
        '.json': '⚙️',
        '.yaml': '⚙️',
        '.yml': '⚙️',
        '.sh': '🔧',
        '.js': '💛',
        '.html': '🌐',
        '.css': '🎨',
        '.php': '🐘',
        '.sql': '🗄️',
        '.env': '🔐',
        '.gitignore': '��',
        '.dockerignore': '🚫',
    }
    
    # 特殊ファイル名のアイコン
    SPECIAL_FILES = {
        '__init__.py': '📦',
        'README.md': '📚',
        'requirements.txt': '📋',
        'Dockerfile': '🐳',
        'docker-compose.yml': '🐳',
        '.gitignore': '🚫',
        'package.json': '📦',
    }
    
    # 特殊フォルダのアイコン
    FOLDER_ICONS = {
        'agents': '🤖',
        'tools': '🔨',
        'configuration': '⚙️',
        'browser_control': '🌐',
        'scripts': '📜',
        'docs': '📚',
        'tests': '🧪',
        'logs': '📊',
        '_WIP': '🚧',
        '_BACKUP': '💾',
        '_ARCHIVE': '📦',
        'agent_outputs': '📤',
        '.git': '🔀',
        '__pycache__': '🗑️',
        'node_modules': '📦',
    }
    
    # 除外するディレクトリ
    EXCLUDE_DIRS = {
        '__pycache__',
        '.git',
        'node_modules',
        '.pytest_cache',
        '.mypy_cache',
        '.ruff_cache',
        'htmlcov',
        '.coverage',
        'dist',
        'build',
        '*.egg-info',
    }
    
    # 除外するファイル
    EXCLUDE_FILES = {
        '.DS_Store',
        'Thumbs.db',
        '*.pyc',
        '*.pyo',
        '*.swp',
    }
    
    def __init__(self, root_path: str = '.', max_depth: int = 4):
        """
        初期化
        
        Args:
            root_path: ルートパス
            max_depth: 最大深度
        """
        self.root_path = Path(root_path).resolve()
        self.max_depth = max_depth
        self.stats = defaultdict(int)
    
    def should_exclude(self, path: Path) -> bool:
        """パスを除外すべきか判定"""
        name = path.name
        
        # 除外ディレクトリ
        if path.is_dir() and name in self.EXCLUDE_DIRS:
            return True
        
        # 除外ファイル
        if path.is_file() and name in self.EXCLUDE_FILES:
            return True
        
        # パターンマッチ
        if name.startswith('.') and name not in ['.env', '.gitignore']:
            return True
        
        return False
    
    def get_icon(self, path: Path) -> str:
        """パスに応じたアイコンを取得"""
        if path.is_dir():
            return self.FOLDER_ICONS.get(path.name, '📁')
        
        # 特殊ファイル名
        if path.name in self.SPECIAL_FILES:
            return self.SPECIAL_FILES[path.name]
        
        # 拡張子
        suffix = path.suffix.lower()
        return self.FILE_ICONS.get(suffix, '📄')
    
    def get_file_size(self, path: Path) -> str:
        """ファイルサイズを人間が読みやすい形式で取得"""
        if not path.is_file():
            return ''
        
        size = path.stat().st_size
        
        if size < 1024:
            return f'{size}B'
        elif size < 1024 * 1024:
            return f'{size/1024:.1f}KB'
        elif size < 1024 * 1024 * 1024:
            return f'{size/(1024*1024):.1f}MB'
        else:
            return f'{size/(1024*1024*1024):.1f}GB'
    
    def count_lines(self, path: Path) -> int:
        """ファイルの行数をカウント"""
        if not path.is_file():
            return 0
        
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return len(f.readlines())
        except:
            return 0
    
    def visualize_tree(self, path: Path = None, prefix: str = '', depth: int = 0):
        """ツリー構造を表示"""
        if path is None:
            path = self.root_path
        
        if depth > self.max_depth:
            return
        
        if self.should_exclude(path):
            return
        
        # アイコンとファイル情報
        icon = self.get_icon(path)
        name = path.name
        
        if path.is_file():
            size = self.get_file_size(path)
            lines = self.count_lines(path)
            
            # Pythonファイルの場合は行数も表示
            if path.suffix == '.py' and lines > 0:
                info = f'({size}, {lines}行)'
            else:
                info = f'({size})' if size else ''
            
            print(f'{prefix}{icon} {name} {info}')
            
            # 統計
            self.stats['total_files'] += 1
            if path.suffix == '.py':
                self.stats['python_files'] += 1
                self.stats['total_lines'] += lines
        
        elif path.is_dir():
            print(f'{prefix}{icon} {name}/')
            self.stats['total_dirs'] += 1
            
            # サブディレクトリとファイルを取得
            try:
                items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
                
                for i, item in enumerate(items):
                    is_last = i == len(items) - 1
                    
                    # プレフィックス作成
                    if is_last:
                        new_prefix = prefix + '└── '
                        child_prefix = prefix + '    '
                    else:
                        new_prefix = prefix + '├── '
                        child_prefix = prefix + '│   '
                    
                    # 再帰的に表示
                    if item.is_dir():
                        print(f'{new_prefix}{self.get_icon(item)} {item.name}/')
                        self.visualize_tree(item, child_prefix, depth + 1)
                    else:
                        if not self.should_exclude(item):
                            size = self.get_file_size(item)
                            lines = self.count_lines(item)
                            
                            if item.suffix == '.py' and lines > 0:
                                info = f'({size}, {lines}行)'
                            else:
                                info = f'({size})' if size else ''
                            
                            print(f'{new_prefix}{self.get_icon(item)} {item.name} {info}')
                            
                            self.stats['total_files'] += 1
                            if item.suffix == '.py':
                                self.stats['python_files'] += 1
                                self.stats['total_lines'] += lines
            
            except PermissionError:
                print(f'{prefix}[アクセス権限なし]')
    
    def show_statistics(self):
        """統計情報を表示"""
        print('\n' + '=' * 80)
        print('📊 プロジェクト統計')
        print('=' * 80)
        print(f'📁 ディレクトリ数: {self.stats["total_dirs"]}')
        print(f'📄 ファイル数: {self.stats["total_files"]}')
        print(f'🐍 Pythonファイル数: {self.stats["python_files"]}')
        print(f'📝 総行数: {self.stats["total_lines"]:,}')
        
        if self.stats['python_files'] > 0:
            avg_lines = self.stats['total_lines'] / self.stats['python_files']
            print(f'📈 平均行数/ファイル: {avg_lines:.1f}')
    
    def show_important_directories(self):
        """重要なディレクトリの説明"""
        print('\n' + '=' * 80)
        print('�� 重要なディレクトリの説明')
        print('=' * 80)
        
        important_dirs = {
            'agents': 'エージェント（WordPress、コンテンツ生成など）',
            'tools': 'ツール（SheetsManager、BrowserControllerなど）',
            'configuration': '設定ファイル（ConfigLoader、.envなど）',
            'scripts': '実行可能スクリプト',
            'docs': 'ドキュメント',
            '_WIP': '作業中のファイル',
            'agent_outputs': 'エージェントの出力結果',
        }
        
        for dir_name, description in important_dirs.items():
            dir_path = self.root_path / dir_name
            if dir_path.exists():
                icon = self.FOLDER_ICONS.get(dir_name, '📁')
                print(f'{icon} {dir_name:20s} → {description}')


def main():
    """メイン関数"""
    print('╔════════════════════════════════════════════════════════════════════════════╗')
    print('║              🎨 Gemini AI Agent プロジェクト構造                         ║')
    print('╚════════════════════════════════════════════════════════════════════════════╝')
    print()
    
    # プロジェクトルート
    project_root = Path('/workspaces/gemini_AI_Agent')
    
    # 可視化実行
    visualizer = ProjectStructureVisualizer(project_root, max_depth=3)
    
    print(f'📂 プロジェクトルート: {project_root}')
    print('=' * 80)
    print()
    
    visualizer.visualize_tree()
    visualizer.show_statistics()
    visualizer.show_important_directories()
    
    print('\n' + '=' * 80)
    print('✅ 可視化完了')
    print('=' * 80)


if __name__ == '__main__':
    main()
