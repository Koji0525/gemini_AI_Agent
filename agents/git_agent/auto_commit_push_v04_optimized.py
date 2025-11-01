#!/usr/bin/env python3
"""
🚀 Git自動コミット＆プッシュツール v4.1（削除ファイル対応）

【v4.1 変更の理由】
何が起きた:
- 削除されたファイルの構文チェックでエラー
- FileNotFoundError が発生

原因:
- git diff --name-only は削除ファイルも含む
- 存在しないファイルを py_compile でチェック

狙い:
- 存在するファイルのみチェック
- 削除ファイルはスキップ
- エラーなく動作
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

class OptimizedGitTool:
    """最適化されたGitツール（削除ファイル対応）"""
    
    def __init__(self, commit_message: str = None):
        self.commit_message = commit_message or f"🔄 Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        self.project_root = Path.cwd()
    
    def run(self) -> int:
        """メイン実行"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🚀 Git自動コミット＆プッシュツール v4.1")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # STEP 1: 変更ファイルの検出
        changed_files = self._get_changed_files()
        
        if not changed_files:
            print("\n✅ 変更なし。コミット不要です。")
            return 0
        
        print(f"\n📋 変更ファイル数: {len(changed_files)}")
        for f in changed_files[:10]:
            status = "🗑️ 削除" if not Path(f).exists() else "📝 変更/追加"
            print(f"   {status}: {f}")
        if len(changed_files) > 10:
            print(f"   ... 他 {len(changed_files) - 10} 件")
        
        # STEP 2: 存在するPythonファイルのみチェック
        python_files = [
            f for f in changed_files 
            if f.endswith('.py') and Path(f).exists()
        ]
        
        if python_files:
            print(f"\n🔍 STEP 2: 変更されたPythonファイルのチェック（{len(python_files)}件）")
            
            for py_file in python_files:
                result = subprocess.run(
                    ['python3', '-m', 'py_compile', py_file],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    print(f"❌ 構文エラー: {py_file}")
                    print(result.stderr)
                    print("\n⚠️ 構文エラーを修正してから再実行してください")
                    return 1
                else:
                    print(f"✅ {py_file}")
        else:
            print("\n⏭️  STEP 2: チェック対象のPythonファイルなし")
        
        # STEP 3: Git操作
        print("\n📦 STEP 3: Git操作")
        print("=" * 70)
        
        try:
            # ステージング
            print("📝 ステージング中...")
            subprocess.run(['git', 'add', '-A'], check=True)
            
            # コミット
            print("💾 コミット中...")
            result = subprocess.run(
                ['git', 'commit', '-m', self.commit_message],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                if 'nothing to commit' in result.stdout:
                    print("✅ コミット済み（変更なし）")
                else:
                    print(f"❌ コミットエラー: {result.stderr}")
                    return 1
            else:
                print("✅ コミット成功")
            
            # プッシュ
            print("🚀 プッシュ中...")
            subprocess.run(['git', 'push'], check=True)
            print("✅ プッシュ成功")
            
            print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("✅ Git操作完了")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            return 0
        
        except subprocess.CalledProcessError as e:
            print(f"❌ Git操作失敗: {e}")
            return 1
    
    def _get_changed_files(self) -> list:
        """変更されたファイルを取得"""
        changed = set()
        
        # 1. 変更されたファイル（git diff）
        result = subprocess.run(
            ['git', 'diff', '--name-only'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            changed.update(result.stdout.strip().split('\n'))
        
        # 2. ステージングされたファイル
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            changed.update(result.stdout.strip().split('\n'))
        
        # 3. 未追跡のファイル
        result = subprocess.run(
            ['git', 'ls-files', '--others', '--exclude-standard'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            changed.update(result.stdout.strip().split('\n'))
        
        # 空文字列を除外
        return [f for f in changed if f]

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='🚀 Git自動コミット＆プッシュツール v4.1',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'message',
        nargs='?',
        help='コミットメッセージ（省略可）'
    )
    
    args = parser.parse_args()
    
    tool = OptimizedGitTool(args.message)
    sys.exit(tool.run())

if __name__ == "__main__":
    main()
