#!/usr/bin/env python3
"""
Git Commit Agent - 自動品質チェック＋コミット
STEP 1-8に対応
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict
import yaml

class CommitAgent:
    def __init__(self, config_path: str = "configs/git_workflows/commit_config.yaml"):
        self.project_root = Path(__file__).parent.parent.parent
        self.config = self._load_config(config_path)
        self.staged_files: List[Path] = []
        self.quality_report: Dict = {}
        
    def _load_config(self, config_path: str) -> dict:
        """設定ファイル読み込み"""
        full_path = self.project_root / config_path
        if not full_path.exists():
            return self._default_config()
        
        with open(full_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _default_config(self) -> dict:
        """デフォルト設定"""
        return {
            'excluded_dirs': ['_WIP', '_BACKUP', '_ARCHIVE', '__pycache__', '.git'],
            'excluded_files': ['*.pyc', '*.log', '*.tmp'],
            'quality_gates': {
                'compile_check': True,
                'linter': True,
                'formatter': True,
                'manual_review': False
            },
            'auto_fix': True,
            'min_quality_score': 7.0
        }
    
    # STEP 1: CLEANUP
    def cleanup_workspace(self) -> bool:
        """一時ファイルを_WIP/に移動"""
        print("\n" + "="*70)
        print("STEP 1: CLEANUP - 一時ファイルの整理")
        print("="*70)
        
        temp_patterns = ['test_*.py', 'tmp_*.py', 'debug_*.py', '*_test.py']
        moved_files = []
        
        for pattern in temp_patterns:
            for file in self.project_root.rglob(pattern):
                if '_WIP' not in str(file) and '_BACKUP' not in str(file):
                    dest = self.project_root / '_WIP' / file.name
                    try:
                        file.rename(dest)
                        moved_files.append(file.name)
                    except Exception as e:
                        print(f"⚠️  {file.name} 移動失敗: {e}")
        
        if moved_files:
            print(f"✅ {len(moved_files)}個のファイルを_WIPに移動")
            for f in moved_files:
                print(f"   - {f}")
        else:
            print("✅ 移動すべき一時ファイルなし")
        
        return True
    
    # STEP 2: LIST
    def list_commit_targets(self) -> List[Path]:
        """コミット対象ファイルをリスト"""
        print("\n" + "="*70)
        print("STEP 2: LIST - コミット対象の列挙")
        print("="*70)
        
        # git statusで変更ファイルを取得
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        files = []
        for line in result.stdout.splitlines():
            if line:
                status = line[:2]
                filepath = line[3:]
                
                # 除外ディレクトリチェック
                if any(excluded in filepath for excluded in self.config['excluded_dirs']):
                    continue
                
                full_path = self.project_root / filepath
                if full_path.exists() and full_path.suffix == '.py':
                    files.append(full_path)
        
        print(f"📋 コミット対象: {len(files)}ファイル")
        for f in files:
            print(f"   ✅ {f.relative_to(self.project_root)}")
        
        self.staged_files = files
        return files
    
    # STEP 3: QUALITY GATE - Compile Check
    def compile_check(self) -> Tuple[bool, List[str]]:
        """構文チェック"""
        print("\n" + "="*70)
        print("STEP 3: QUALITY GATE - コンパイルチェック")
        print("="*70)
        
        errors = []
        for file in self.staged_files:
            result = subprocess.run(
                ['python3', '-m', 'py_compile', str(file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                errors.append(f"{file.name}: {result.stderr}")
                print(f"   ❌ {file.name}: 構文エラー")
            else:
                print(f"   ✅ {file.name}")
        
        if errors:
            print(f"\n❌ {len(errors)}個のファイルに構文エラー")
            return False, errors
        
        print("\n✅ すべてのファイルが構文OK")
        return True, []
    
    # STEP 3: QUALITY GATE - Linter
    def linter_check(self) -> Tuple[bool, Dict]:
        """Linterチェック（flake8）"""
        print("\n" + "="*70)
        print("STEP 3: QUALITY GATE - Linterチェック")
        print("="*70)
        
        # flake8インストール確認
        try:
            subprocess.run(['flake8', '--version'], capture_output=True, check=True)
        except:
            print("⚠️  flake8未インストール - スキップ")
            return True, {}
        
        issues = {}
        for file in self.staged_files:
            result = subprocess.run(
                ['flake8', '--max-line-length=120', '--extend-ignore=E203,W503', str(file)],
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                issues[file.name] = result.stdout
                print(f"   ⚠️  {file.name}: {len(result.stdout.splitlines())}個の警告")
            else:
                print(f"   ✅ {file.name}")
        
        if issues:
            print(f"\n⚠️  {len(issues)}個のファイルに警告あり")
            return False, issues
        
        print("\n✅ Linterチェック通過")
        return True, {}
    
    # STEP 4: Formatter
    def format_code(self) -> bool:
        """コード自動整形（Black）"""
        print("\n" + "="*70)
        print("STEP 4: FORMATTER - コード自動整形")
        print("="*70)
        
        # Blackインストール確認
        try:
            subprocess.run(['black', '--version'], capture_output=True, check=True)
        except:
            print("⚠️  Black未インストール - スキップ")
            return True
        
        for file in self.staged_files:
            result = subprocess.run(
                ['black', '--line-length=120', str(file)],
                capture_output=True,
                text=True
            )
            
            if 'reformatted' in result.stdout:
                print(f"   🔧 {file.name}: 整形完了")
            else:
                print(f"   ✅ {file.name}: 整形不要")
        
        print("\n✅ コード整形完了")
        return True
    
    # STEP 6: FINAL CLEANUP
    def final_cleanup(self) -> bool:
        """不要ファイル削除"""
        print("\n" + "="*70)
        print("STEP 6: FINAL CLEANUP - 不要ファイル削除")
        print("="*70)
        
        patterns = ['**/__pycache__', '**/*.pyc', '**/*.log', '**/*.tmp']
        removed_count = 0
        
        for pattern in patterns:
            for file in self.project_root.glob(pattern):
                try:
                    if file.is_dir():
                        import shutil
                        shutil.rmtree(file)
                    else:
                        file.unlink()
                    removed_count += 1
                except Exception as e:
                    pass
        
        print(f"✅ {removed_count}個の不要ファイルを削除")
        return True
    
    # STEP 8: COMMIT
    def commit(self, message: str, skip_hooks: bool = False) -> bool:
        """Git commit実行"""
        print("\n" + "="*70)
        print("STEP 8: COMMIT")
        print("="*70)
        
        # ファイルをstaging
        for file in self.staged_files:
            subprocess.run(['git', 'add', str(file)], cwd=self.project_root)
        
        print(f"📝 コミットメッセージ: {message}")
        
        # コミット実行
        cmd = ['git', 'commit', '-m', message]
        if skip_hooks:
            cmd.append('--no-verify')
        
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ コミット成功")
            return True
        else:
            print(f"❌ コミット失敗: {result.stderr}")
            return False
    
    def run(self, commit_message: str) -> bool:
        """フルフロー実行"""
        print("\n🤖 Git Commit Agent 開始")
        print("="*70)
        
        # STEP 1-8を順番に実行
        steps = [
            ("CLEANUP", self.cleanup_workspace),
            ("LIST", self.list_commit_targets),
            ("COMPILE", lambda: self.compile_check()[0]),
            ("LINTER", lambda: self.linter_check()[0] if self.config['quality_gates']['linter'] else True),
            ("FORMATTER", self.format_code if self.config['quality_gates']['formatter'] else lambda: True),
            ("FINAL CLEANUP", self.final_cleanup),
        ]
        
        for step_name, step_func in steps:
            try:
                if not step_func():
                    print(f"\n❌ {step_name}でエラー発生")
                    return False
            except Exception as e:
                print(f"\n❌ {step_name}で例外発生: {e}")
                return False
        
        # 最後にコミット
        return self.commit(commit_message)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python3 commit_agent.py 'コミットメッセージ'")
        sys.exit(1)
    
    agent = CommitAgent()
    success = agent.run(sys.argv[1])
    sys.exit(0 if success else 1)
