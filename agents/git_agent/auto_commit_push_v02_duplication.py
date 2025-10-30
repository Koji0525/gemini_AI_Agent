#!/usr/bin/env python3
"""
Git自動コミット＆プッシュツール（重複チェック改善版）
変更理由: __init__.py等とバックアップディレクトリを除外
"""

import subprocess
import sys
from pathlib import Path
from collections import defaultdict

# 重複チェックから除外するファイル名
EXCLUDE_FILES = {
    '__init__.py',      # Pythonパッケージの標準ファイル
    '.gitignore',       # Git設定ファイル
    'README.md',        # 各ディレクトリのREADME（実質的な重複は少ないが念のため）
}

# 除外するディレクトリ（これらの配下は完全に無視）
EXCLUDE_DIRECTORIES = {
    '__pycache__',
    '.git',
    'node_modules',
    '.venv',
    'venv',
    '_ARCHIVE',         # アーカイブディレクトリ
    '_BACKUP',          # バックアップディレクトリ
    '_WIP',             # 作業中ディレクトリ
    '.pytest_cache',
    '.mypy_cache',
}

def check_duplicates():
    """
    プロジェクト内の重複ファイル名をチェック
    （標準ファイルとバックアップディレクトリは除外）
    """
    print("\n" + "=" * 70)
    print("🔍 重複ファイル名チェック（標準ファイル・バックアップ除外版）")
    print("=" * 70)
    
    project_root = Path.cwd()
    file_map = defaultdict(list)
    
    # すべてのファイルを収集
    for file_path in project_root.rglob("*"):
        # ディレクトリをスキップ
        if file_path.is_dir():
            continue
        
        # 除外ディレクトリ内のファイルをスキップ
        path_parts = file_path.parts
        if any(exclude_dir in path_parts for exclude_dir in EXCLUDE_DIRECTORIES):
            continue
        
        # ファイル名を取得
        file_name = file_path.name
        
        # 除外対象ファイルをスキップ
        if file_name in EXCLUDE_FILES:
            continue
        
        # コンパイル済みファイルをスキップ
        if file_name.endswith(('.pyc', '.pyo', '.pyd')):
            continue
        
        # 対象ファイル（.py, .sh, .md など）
        if file_name.endswith(('.py', '.sh', '.md', '.json', '.yaml', '.yml')):
            relative_path = file_path.relative_to(project_root)
            file_map[file_name].append(str(relative_path))
    
    # 重複を検出
    duplicates = {name: paths for name, paths in file_map.items() if len(paths) > 1}
    
    if duplicates:
        print(f"❌ {len(duplicates)}個の重複ファイルが検出されました:")
        for file_name, paths in sorted(duplicates.items()):
            print(f"\n📄 {file_name} ({len(paths)}個)")
            for path in sorted(paths):
                print(f"   - {path}")
        
        print("\n" + "=" * 70)
        print("⚠️  対処法:")
        print("   1. ファイル名を変更して重複を解消する")
        print("   2. 不要なファイルを_ARCHIVE/に移動する")
        print("   3. 最新版をメインディレクトリに配置し、旧版を_BACKUP/に移動する")
        print("=" * 70)
        print("⚠️  重複ファイル名を無視して続行します\n")
        
        return False
    else:
        print("✅ 重複ファイルは検出されませんでした")
        print("=" * 70 + "\n")
        return True

def git_add_commit_push(commit_message):
    """Git操作を実行"""
    try:
        # git add
        print("📝 変更をステージング中...")
        subprocess.run(["git", "add", "."], check=True)
        
        # git commit
        print("💾 コミット中...")
        result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            if "nothing to commit" in result.stdout:
                print("✅ コミット対象の変更がありません")
                return True
            else:
                print(f"❌ コミットエラー: {result.stderr}")
                return False
        
        print("✅ コミット完了")
        
        # git push
        print("�� プッシュ中...")
        subprocess.run(["git", "push"], check=True)
        print("✅ プッシュ完了")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git操作エラー: {e}")
        return False

def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("❌ 使用方法: python3 auto_commit_push_v02_duplication.py 'コミットメッセージ'")
        sys.exit(1)
    
    commit_message = sys.argv[1]
    
    print("🚀 Git自動コミット＆プッシュツール（改善版）")
    print("=" * 70)
    
    # 重複チェック（__init__.py、_ARCHIVE、_BACKUP等を除外）
    check_duplicates()
    
    # Git操作実行
    print("\n" + "=" * 70)
    print("📦 Git操作を実行")
    print("=" * 70)
    
    if git_add_commit_push(commit_message):
        print("\n🎉 コミットプッシュは完了！")
    else:
        print("\n❌ コミットプッシュに失敗しました")
        sys.exit(1)

if __name__ == "__main__":
    main()
