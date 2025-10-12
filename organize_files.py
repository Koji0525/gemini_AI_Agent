#!/usr/bin/env python3
"""
不要ファイルを安全に整理するツール
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

class FileOrganizer:
    """ファイルを整理"""
    
    def __init__(self):
        self.root = Path(".")
        self.archive_dir = Path("_archive_unused")
        
    def create_backup(self):
        """バックアップディレクトリ作成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.archive_dir / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir
    
    def move_to_archive(self, files, reason="unused"):
        """ファイルをアーカイブに移動"""
        if not files:
            print("移動するファイルがありません")
            return
        
        backup_dir = self.create_backup()
        reason_dir = backup_dir / reason
        reason_dir.mkdir(exist_ok=True)
        
        print(f"\n�� {len(files)} ファイルを {reason_dir} に移動中...")
        
        moved = 0
        for file in files:
            try:
                file_path = Path(file)
                if file_path.exists():
                    # 相対パス構造を保持
                    relative = file_path.relative_to(self.root)
                    dest = reason_dir / relative
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    
                    shutil.move(str(file_path), str(dest))
                    print(f"  ✅ {file} → {dest}")
                    moved += 1
            except Exception as e:
                print(f"  ❌ エラー: {file} - {e}")
        
        print(f"\n✅ {moved}/{len(files)} ファイルを移動しました")
        
        # 移動リストを保存
        list_file = backup_dir / f"{reason}_files.txt"
        with open(list_file, 'w', encoding='utf-8') as f:
            for file in files:
                f.write(f"{file}\n")
        
        print(f"📝 移動リストを {list_file} に保存しました")
    
    def organize_by_report(self, report_file='dependency_report.json'):
        """依存関係レポートに基づいて整理"""
        import json
        
        if not Path(report_file).exists():
            print(f"❌ {report_file} が見つかりません")
            print("先に find_active_files.py を実行してください")
            return
        
        with open(report_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        unused_files = report.get('unused_files', [])
        
        print(f"🗑️ 使われていないファイル: {len(unused_files)} 件")
        
        if unused_files:
            print("\n移動するファイル一覧:")
            for file in unused_files[:10]:
                print(f"  - {file}")
            if len(unused_files) > 10:
                print(f"  ... 他 {len(unused_files) - 10} ファイル")
            
            response = input("\nこれらのファイルをアーカイブに移動しますか？ (yes/no): ")
            if response.lower() in ['yes', 'y']:
                self.move_to_archive(unused_files, reason="unused")
            else:
                print("キャンセルしました")
        else:
            print("✅ 移動するファイルはありません")

if __name__ == "__main__":
    organizer = FileOrganizer()
    organizer.organize_by_report()
