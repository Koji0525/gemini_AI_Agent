#!/usr/bin/env python3
"""
🗂️ 古いバージョンファイル自動アーカイブツール

【アーカイブルール】
✅ 最新バージョン（最大のバージョン番号）: 残す
✅ 本番版（バージョン番号なし）: 残す
❌ それ以外の古いバージョン: アーカイブへ移動

例:
  script_v14_production_ready.py  → 残す（最新）
  script.py                       → 残す（本番版）
  script_v01_hub.py ~ v13.py      → アーカイブ
"""

import re
import shutil
from pathlib import Path
from datetime import datetime

class VersionArchiver:
    """バージョンファイルのアーカイブ管理"""
    
    def __init__(self, archive_dir: str = None):
        self.project_root = Path.cwd()
        
        if archive_dir is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archive_dir = f"_ARCHIVE/{timestamp}_version_cleanup"
        
        self.archive_dir = self.project_root / archive_dir
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        self.exclude_dirs = {'_WIP', '_ARCHIVE', '_BACKUP', '__pycache__', '.git'}
    
    def analyze_duplicates(self) -> dict:
        """重複ファイルを分析"""
        file_groups = {}
        
        for py_file in self.project_root.rglob('*.py'):
            # 除外ディレクトリをスキップ
            if any(excluded in py_file.parts for excluded in self.exclude_dirs):
                continue
            
            if py_file.name == '__init__.py':
                continue
            
            # ベース名を取得
            base_name = self._get_base_name(py_file.name)
            
            if base_name not in file_groups:
                file_groups[base_name] = []
            
            file_groups[base_name].append(py_file)
        
        # 重複のみ抽出
        duplicates = {k: v for k, v in file_groups.items() if len(v) > 1}
        
        return duplicates
    
    def archive_old_versions(self, dry_run: bool = False):
        """古いバージョンをアーカイブ"""
        duplicates = self.analyze_duplicates()
        
        if not duplicates:
            print("✅ 重複ファイルなし")
            return
        
        print(f"🔍 重複グループ数: {len(duplicates)}")
        print()
        
        total_archived = 0
        
        for base_name, files in sorted(duplicates.items()):
            print(f"📂 {base_name}:")
            
            # ファイルを分類
            production_file = None  # バージョン番号なし
            latest_version_file = None  # 最大バージョン番号
            old_files = []  # アーカイブ対象
            
            max_version = -1
            
            for f in files:
                version = self._extract_version(f.name)
                
                if version is None:
                    # バージョン番号なし = 本番版
                    production_file = f
                    print(f"   ✅ 本番版: {f.relative_to(self.project_root)}")
                else:
                    if version > max_version:
                        if latest_version_file:
                            old_files.append(latest_version_file)
                        latest_version_file = f
                        max_version = version
                    else:
                        old_files.append(f)
            
            # 最新バージョンを表示
            if latest_version_file:
                print(f"   ✅ 最新版: {latest_version_file.relative_to(self.project_root)}")
            
            # アーカイブ対象を表示＆移動
            if old_files:
                print(f"   🗑️  アーカイブ対象: {len(old_files)}件")
                
                for old_file in old_files:
                    rel_path = old_file.relative_to(self.project_root)
                    print(f"      - {rel_path}")
                    
                    if not dry_run:
                        # アーカイブ先のディレクトリ構造を維持
                        dest = self.archive_dir / rel_path
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(old_file), str(dest))
                    
                    total_archived += 1
            
            print()
        
        if dry_run:
            print(f"🔍 ドライラン完了: {total_archived}件がアーカイブ対象")
        else:
            print(f"✅ アーカイブ完了: {total_archived}件を移動")
            print(f"📂 アーカイブ先: {self.archive_dir}")
    
    def _get_base_name(self, filename: str) -> str:
        """バージョン番号を除いたベース名を取得"""
        # task_executor_v04_feature.py → task_executor
        base = re.sub(r'_v\d+.*\.py$', '', filename)
        base = re.sub(r'\.py$', '', base)
        return base if base else filename
    
    def _extract_version(self, filename: str) -> int:
        """ファイル名からバージョン番号を抽出"""
        match = re.search(r'_v(\d+)', filename)
        return int(match.group(1)) if match else None

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='🗂️ 古いバージョンファイル自動アーカイブツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # ドライラン（実際には移動しない）
  python3 tools/archive_old_versions.py --dry-run
  
  # 実行（古いバージョンをアーカイブへ移動）
  python3 tools/archive_old_versions.py
  
  # カスタムアーカイブ先
  python3 tools/archive_old_versions.py --archive-dir _ARCHIVE/custom
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='ドライラン（実際には移動しない）'
    )
    
    parser.add_argument(
        '--archive-dir',
        help='アーカイブ先ディレクトリ（省略時は自動生成）'
    )
    
    args = parser.parse_args()
    
    archiver = VersionArchiver(args.archive_dir)
    archiver.archive_old_versions(dry_run=args.dry_run)

if __name__ == "__main__":
    main()
