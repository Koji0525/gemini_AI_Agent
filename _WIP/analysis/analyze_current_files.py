#!/usr/bin/env python3
"""
プロジェクト全体のファイル分析
どこにどれだけファイルがあるか確認
"""

from pathlib import Path
from collections import defaultdict
import os

def analyze_project():
    print("📊 プロジェクトファイル分析")
    print("=" * 70)
    
    # カウント用
    total_files = 0
    dir_file_count = defaultdict(int)
    file_types = defaultdict(int)
    large_dirs = []
    
    # 除外ディレクトリ
    exclude_dirs = {'.git', 'node_modules', '.venv', 'venv', 'None'}
    
    # 1. 全ファイルをスキャン
    print("\n🔍 スキャン中...")
    for root, dirs, files in os.walk('.'):
        # 除外ディレクトリをスキップ
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        # パスを正規化
        rel_path = os.path.relpath(root, '.')
        if rel_path == '.':
            rel_path = 'ROOT'
        
        # ファイル数カウント
        file_count = len(files)
        if file_count > 0:
            dir_file_count[rel_path] = file_count
            total_files += file_count
            
            # 10ファイル以上のディレクトリを記録
            if file_count >= 10:
                large_dirs.append((rel_path, file_count))
            
            # ファイルタイプカウント
            for file in files:
                ext = Path(file).suffix or 'no_extension'
                file_types[ext] += 1
    
    # 2. 結果表示
    print("\n" + "=" * 70)
    print(f"📊 総ファイル数: {total_files}")
    print("=" * 70)
    
    # 3. ファイルタイプ別
    print("\n📋 ファイルタイプ別:")
    sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)
    for ext, count in sorted_types[:15]:
        print(f"  {ext:20} : {count:4} ファイル")
    
    # 4. 大量ファイルのディレクトリ
    print("\n🚨 ファイル数が多いディレクトリ（10個以上）:")
    large_dirs.sort(key=lambda x: x[1], reverse=True)
    for dir_path, count in large_dirs[:20]:
        print(f"  {count:4} ファイル : {dir_path}")
    
    # 5. ROOT直下のファイル
    print("\n📁 プロジェクトルート直下のファイル:")
    root_files = [f for f in os.listdir('.') if os.path.isfile(f)]
    print(f"  総数: {len(root_files)} ファイル")
    
    # 拡張子別
    root_types = defaultdict(list)
    for f in root_files:
        ext = Path(f).suffix or 'no_extension'
        root_types[ext].append(f)
    
    for ext, files in sorted(root_types.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n  {ext} ({len(files)}個):")
        for f in files[:10]:  # 最初の10個だけ表示
            print(f"    - {f}")
        if len(files) > 10:
            print(f"    ... 他{len(files)-10}個")
    
    # 6. 疑わしいファイル/フォルダ
    print("\n⚠️ 整理候補（疑わしいファイル）:")
    
    suspicious_patterns = [
        ('__pycache__', '__pycache__ディレクトリ'),
        ('*.pyc', 'Pythonキャッシュファイル'),
        ('*.backup', 'バックアップファイル'),
        ('*_backup*', 'バックアップファイル'),
        ('*.old', '古いファイル'),
        ('*.tmp', '一時ファイル'),
        ('*.log', 'ログファイル（logs/以外）'),
    ]
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        rel_path = os.path.relpath(root, '.')
        
        # __pycache__
        if '__pycache__' in dirs:
            print(f"  🗑️ {rel_path}/__pycache__/")
        
        # 疑わしいファイル
        for file in files:
            if any(p in file for p in ['backup', 'old', 'tmp', '.pyc']):
                if rel_path == '.':
                    print(f"  🗑️ ROOT/{file}")
                else:
                    print(f"  🗑️ {rel_path}/{file}")
    
    # 7. 整理推奨
    print("\n" + "=" * 70)
    print("💡 整理推奨:")
    print("=" * 70)
    print("""
1. __pycache__/ フォルダを削除
2. *.pyc ファイルを削除
3. ROOT直下の不要ファイルを整理
4. バックアップファイルを _BACKUP/ に移動
5. 古いファイルを _ARCHIVE/ に移動
6. logs/以外のログファイルを移動
    """)

if __name__ == "__main__":
    analyze_project()
