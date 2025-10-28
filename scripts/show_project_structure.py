#!/usr/bin/env python3
"""
プロジェクト構造可視化ツール（カスタマイズ版）
フォルダとファイルを見やすく表示

v1.1 - カスタマイズ設定セクション追加
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                         📝 カスタマイズ設定                                ║
# ╚════════════════════════════════════════════════════════════════════════════╝

# 【重要】ここを編集すれば簡単にカスタマイズできます

# 表示対象の拡張子（空リストの場合は全ファイル表示）
TARGET_EXTENSIONS = ['.py']  # Pythonファイルのみ
# 例: TARGET_EXTENSIONS = ['.py', '.js', '.html']  # 複数指定
# 例: TARGET_EXTENSIONS = []  # すべてのファイル

# 除外するディレクトリ
CUSTOM_EXCLUDE_DIRS = {
    '_ARCHIVE',      # アーカイブフォルダ
    '_BACKUP',       # バックアップフォルダ
    '_WIP',          # 作業中フォルダ
    '__pycache__',   # Pythonキャッシュ
    '.git',          # Gitフォルダ
    'node_modules',  # Node.jsモジュール
    '.pytest_cache', # Pytestキャッシュ
    '.mypy_cache',   # Mypyキャッシュ
    '.ruff_cache',   # Ruffキャッシュ
}

# 除外するファイル名
CUSTOM_EXCLUDE_FILES = {
    '.DS_Store',
    'Thumbs.db',
    '*.pyc',
    '*.pyo',
    '*.swp',
}

# ツリー表示の最大深度
MAX_DEPTH = 4  # デフォルト: 4階層まで

# ファイルサイズを表示するか
SHOW_FILE_SIZE = True

# 行数を表示するか（Pythonファイルのみ）
SHOW_LINE_COUNT = True

# ╚════════════════════════════════════════════════════════════════════════════╝


class ProjectStructureVisualizer:
    """プロジェクト構造を可視化するクラス"""
    
    # ファイルタイプ別の絵文字
    FILE_ICONS = {
        '.py': '🐍',
        '.md': '📝',
        '.txt': '📄',
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
        '.gitignore': '🚫',
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
    
    def __init__(self, root_path: str = '.', 
                 target_extensions: List[str] = None,
                 exclude_dirs: Set[str] = None,
                 exclude_files: Set[str] = None,
                 max_depth: int = MAX_DEPTH,
                 show_file_size: bool = SHOW_FILE_SIZE,
                 show_line_count: bool = SHOW_LINE_COUNT):
        """
        初期化
        
        Args:
            root_path: ルートパス
            target_extensions: 対象拡張子リスト（Noneの場合は全ファイル）
            exclude_dirs: 除外ディレクトリ
            exclude_files: 除外ファイル
            max_depth: 最大深度
            show_file_size: ファイルサイズ表示
            show_line_count: 行数表示
        """
        self.root_path = Path(root_path).resolve()
        self.target_extensions = target_extensions or []
        self.exclude_dirs = exclude_dirs or CUSTOM_EXCLUDE_DIRS
        self.exclude_files = exclude_files or CUSTOM_EXCLUDE_FILES
        self.max_depth = max_depth
        self.show_file_size = show_file_size
        self.show_line_count = show_line_count
        self.stats = defaultdict(int)
    
    def should_exclude_dir(self, path: Path) -> bool:
        """ディレクトリを除外すべきか判定"""
        name = path.name
        
        # 除外リストに含まれる
        if name in self.exclude_dirs:
            return True
        
        # 隠しディレクトリ（.envなどは除く）
        if name.startswith('.') and name not in ['.github']:
            return True
        
        return False
    
    def should_exclude_file(self, path: Path) -> bool:
        """ファイルを除外すべきか判定"""
        name = path.name
        
        # 除外リストに含まれる
        if name in self.exclude_files:
            return True
        
        # 拡張子フィルタ
        if self.target_extensions:
            if path.suffix.lower() not in self.target_extensions:
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
        if not path.is_file() or not self.show_file_size:
            return ''
        
        try:
            size = path.stat().st_size
            
            if size < 1024:
                return f'{size}B'
            elif size < 1024 * 1024:
                return f'{size/1024:.1f}KB'
            elif size < 1024 * 1024 * 1024:
                return f'{size/(1024*1024):.1f}MB'
            else:
                return f'{size/(1024*1024*1024):.1f}GB'
        except:
            return ''
    
    def count_lines(self, path: Path) -> int:
        """ファイルの行数をカウント"""
        if not path.is_file() or not self.show_line_count:
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
        
        # ディレクトリの除外判定
        if path.is_dir() and self.should_exclude_dir(path):
            return
        
        # ファイルの除外判定
        if path.is_file() and self.should_exclude_file(path):
            return
        
        # アイコンとファイル情報
        icon = self.get_icon(path)
        name = path.name
        
        if path.is_file():
            size = self.get_file_size(path)
            lines = self.count_lines(path)
            
            # 情報の構築
            info_parts = []
            if size:
                info_parts.append(size)
            if lines > 0:
                info_parts.append(f'{lines}行')
            
            info = f"({', '.join(info_parts)})" if info_parts else ''
            
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
                
                # 除外後のアイテムのみ
                valid_items = []
                for item in items:
                    if item.is_dir() and not self.should_exclude_dir(item):
                        valid_items.append(item)
                    elif item.is_file() and not self.should_exclude_file(item):
                        valid_items.append(item)
                
                for i, item in enumerate(valid_items):
                    is_last = i == len(valid_items) - 1
                    
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
                        size = self.get_file_size(item)
                        lines = self.count_lines(item)
                        
                        info_parts = []
                        if size:
                            info_parts.append(size)
                        if lines > 0:
                            info_parts.append(f'{lines}行')
                        
                        info = f"({', '.join(info_parts)})" if info_parts else ''
                        
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
        
        if self.target_extensions:
            ext_str = ', '.join(self.target_extensions)
            print(f'🎯 対象拡張子: {ext_str}')
        
        if '.py' in self.target_extensions or not self.target_extensions:
            print(f'🐍 Pythonファイル数: {self.stats["python_files"]}')
            if self.show_line_count:
                print(f'📝 総行数: {self.stats["total_lines"]:,}')
                
                if self.stats['python_files'] > 0:
                    avg_lines = self.stats['total_lines'] / self.stats['python_files']
                    print(f'📈 平均行数/ファイル: {avg_lines:.1f}')
    
    def show_settings(self):
        """現在の設定を表示"""
        print('\n' + '=' * 80)
        print('⚙️  現在の設定')
        print('=' * 80)
        print(f'最大深度: {self.max_depth}')
        print(f'対象拡張子: {", ".join(self.target_extensions) if self.target_extensions else "すべて"}')
        print(f'除外ディレクトリ数: {len(self.exclude_dirs)}')
        print(f'  → {", ".join(sorted(list(self.exclude_dirs)[:5]))}...')
        print(f'ファイルサイズ表示: {"ON" if self.show_file_size else "OFF"}')
        print(f'行数表示: {"ON" if self.show_line_count else "OFF"}')
    
    def show_important_directories(self):
        """重要なディレクトリの説明"""
        print('\n' + '=' * 80)
        print('📚 重要なディレクトリの説明')
        print('=' * 80)
        
        important_dirs = {
            'agents': 'エージェント（WordPress、コンテンツ生成など）',
            'tools': 'ツール（SheetsManager、BrowserControllerなど）',
            'configuration': '設定ファイル（ConfigLoader、.envなど）',
            'scripts': '実行可能スクリプト',
            'docs': 'ドキュメント',
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
    visualizer = ProjectStructureVisualizer(
        project_root,
        target_extensions=TARGET_EXTENSIONS,
        exclude_dirs=CUSTOM_EXCLUDE_DIRS,
        max_depth=MAX_DEPTH,
        show_file_size=SHOW_FILE_SIZE,
        show_line_count=SHOW_LINE_COUNT
    )
    
    print(f'📂 プロジェクトルート: {project_root}')
    print('=' * 80)
    print()
    
    visualizer.visualize_tree()
    visualizer.show_statistics()
    visualizer.show_settings()
    visualizer.show_important_directories()
    
    print('\n' + '=' * 80)
    print('✅ 可視化完了')
    print('=' * 80)
    print('\n💡 ヒント: スクリプトの先頭のカスタマイズ設定セクションを編集すれば')
    print('   表示内容を簡単に変更できます！')


if __name__ == '__main__':
    main()
