#!/usr/bin/env python3
"""
📦 File Version Manager v2.0（機能拡張版）

【v2.0 変更の理由】
何が起きた:
- --promote オプションがなくてエラー
- 重複チェックで不要なディレクトリも検索

原因:
- promote機能が未実装
- 除外ディレクトリの指定ができない

狙い:
- バージョンファイルを本番に昇格
- 除外ディレクトリを指定可能
- 使いやすさ向上

【新機能】
✅ --promote: バージョンファイルを本番版に昇格
✅ --exclude-dirs: 除外ディレクトリ指定
✅ --quick-backup: クイックバックアップ（1コマンド）
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime
import subprocess

class FileVersionManager:
    """ファイルバージョン管理ツール"""
    
    # デフォルト除外ディレクトリ
    DEFAULT_EXCLUDE_DIRS = {
        '_WIP', '_ARCHIVE', '_BACKUP', '__pycache__', 
        '.git', 'node_modules', 'venv', '.venv'
    }
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.backup_dir = self.project_root / '_BACKUP'
    
    def backup_file(self, file_path: str, reason: str):
        """ファイルをバックアップ"""
        source = Path(file_path)
        
        if not source.exists():
            print(f"❌ ファイルが見つかりません: {file_path}")
            return False
        
        # タイムスタンプディレクトリ作成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_subdir = self.backup_dir / f"{timestamp}_{reason.replace(' ', '_')}"
        backup_subdir.mkdir(parents=True, exist_ok=True)
        
        # バックアップ先パス
        dest = backup_subdir / source.name
        
        # コピー
        shutil.copy2(source, dest)
        print(f"✅ バックアップ完了: {dest}")
        
        return True
    
    def promote_version(self, source_path: str, target_path: str):
        """
        バージョンファイルを本番版に昇格
        
        例: 
            source: scripts/task_executor_v04_feature.py
            target: scripts/task_executor.py
        """
        source = Path(source_path)
        target = Path(target_path)
        
        if not source.exists():
            print(f"❌ ソースファイルが見つかりません: {source_path}")
            return False
        
        # 既存ファイルがあればバックアップ
        if target.exists():
            reason = f"promote_from_{source.stem}"
            print(f"📦 既存ファイルをバックアップ中...")
            self.backup_file(str(target), reason)
        
        # コピー
        shutil.copy2(source, target)
        print(f"✅ 昇格完了: {source.name} → {target.name}")
        
        return True
    
    def check_duplicates(self, exclude_dirs: set = None):
        """
        重複ファイルをチェック（.pyファイルのみ、除外ディレクトリ対応）
        
        Args:
            exclude_dirs: 除外するディレクトリ名のセット
        """
        if exclude_dirs is None:
            exclude_dirs = self.DEFAULT_EXCLUDE_DIRS
        
        print("🔍 重複ファイルチェック開始...")
        print(f"📂 除外ディレクトリ: {', '.join(sorted(exclude_dirs))}")
        
        # ファイル名でグループ化（.pyのみ、__init__.py除外）
        file_groups = {}
        
        for py_file in self.project_root.rglob('*.py'):
            # 除外ディレクトリをスキップ
            if any(excluded in py_file.parts for excluded in exclude_dirs):
                continue
            
            # __init__.py は除外
            if py_file.name == '__init__.py':
                continue
            
            # ベース名でグループ化（バージョン番号を除去）
            base_name = self._get_base_name(py_file.name)
            
            if base_name not in file_groups:
                file_groups[base_name] = []
            
            file_groups[base_name].append(py_file)
        
        # 重複を報告
        duplicates_found = False
        
        for base_name, files in file_groups.items():
            if len(files) > 1:
                duplicates_found = True
                print(f"\n⚠️  重複発見: {base_name}")
                for f in sorted(files):
                    rel_path = f.relative_to(self.project_root)
                    print(f"   - {rel_path}")
        
        if not duplicates_found:
            print("\n✅ 重複ファイルなし")
        
        return duplicates_found
    
    def _get_base_name(self, filename: str) -> str:
        """バージョン番号を除いたベース名を取得"""
        import re
        # task_executor_v04_feature.py → task_executor
        base = re.sub(r'_v\d+.*\.py$', '', filename)
        return base if base else filename
    
    def quick_backup(self, file_path: str, reason: str):
        """クイックバックアップ（1コマンド）"""
        return self.backup_file(file_path, reason)

def main():
    parser = argparse.ArgumentParser(
        description='📦 File Version Manager v2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # バックアップ
  python3 tools/file_version_manager.py --backup script.py --reason "機能追加前"
  
  # クイックバックアップ（短縮形）
  python3 tools/file_version_manager.py script.py "機能追加前"
  
  # バージョン昇格
  python3 tools/file_version_manager.py --promote script_v04.py --to script.py
  
  # 重複チェック（デフォルト除外）
  python3 tools/file_version_manager.py --check-duplicates
  
  # 重複チェック（カスタム除外）
  python3 tools/file_version_manager.py --check-duplicates --exclude-dirs _WIP _TEST
        """
    )
    
    parser.add_argument('--backup', help='バックアップするファイル')
    parser.add_argument('--reason', help='バックアップの理由')
    parser.add_argument('--promote', help='昇格するバージョンファイル')
    parser.add_argument('--to', dest='target', help='昇格先のファイル名')
    parser.add_argument('--check-duplicates', action='store_true', help='重複チェック')
    parser.add_argument('--exclude-dirs', nargs='*', help='除外ディレクトリ')
    parser.add_argument('--quick', nargs=2, metavar=('BASE', 'FEATURE'), help='クイック作成')
    
    # クイックバックアップ用（位置引数）
    parser.add_argument('file', nargs='?', help='ファイルパス（クイックバックアップ用）')
    parser.add_argument('quick_reason', nargs='?', help='理由（クイックバックアップ用）')
    
    args = parser.parse_args()
    
    manager = FileVersionManager()
    
    # クイックバックアップ（位置引数）
    if args.file and args.quick_reason:
        return 0 if manager.quick_backup(args.file, args.quick_reason) else 1
    
    # 通常のバックアップ
    if args.backup and args.reason:
        return 0 if manager.backup_file(args.backup, args.reason) else 1
    
    # 昇格
    if args.promote and args.target:
        return 0 if manager.promote_version(args.promote, args.target) else 1
    
    # 重複チェック
    if args.check_duplicates:
        exclude = set(args.exclude_dirs) if args.exclude_dirs else None
        manager.check_duplicates(exclude)
        return 0
    
    parser.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(main())
