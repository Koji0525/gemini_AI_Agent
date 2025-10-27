#!/usr/bin/env python3
"""
完全自動化Git統合ワークフロー
STEP 1-9を一括実行
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import yaml
import re
from datetime import datetime

class AutoCommitPushAgent:
    def __init__(self, config_path: str = "configs/git_workflows/auto_workflow_config.yaml"):
        self.project_root = Path(__file__).parent.parent.parent
        self.config = self._load_config(config_path)
        self.errors: Dict[str, List] = {}
        self.staged_files: List[Path] = []
        self.test_command: Optional[str] = None
        
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
            'excluded_dirs': ['_WIP', '_BACKUP', '_ARCHIVE', '__pycache__', '.git', 'node_modules', 'venv'],
            'excluded_files': ['*.pyc', '*.log', '*.tmp', '.DS_Store'],
            'secret_patterns': [
                'service_account.json',
                '**/service_account.json',
                '**/*_key.json',
                '**/*.pem',
                '**/credentials.json'
            ],
            'quality_gates': {
                'cleanup': True,
                'list': True,
                'compile': True,
                'linter': False,  # 警告のみ
                'formatter': False,  # 今回はスキップ
                'test': True,
                'security_check': True,
                'duplicate_check': True
            },
            'auto_fix': False
        }
    
    def _print_step(self, step_num: int, title: str):
        """ステップヘッダー表示"""
        print("\n" + "="*70)
        print(f"STEP {step_num}: {title}")
        print("="*70)
    
    # STEP 1: CLEANUP
    def step1_cleanup(self) -> bool:
        """一時ファイルを_WIPに移動"""
        self._print_step(1, "CLEANUP - 一時ファイル整理")
        
        temp_patterns = ['test_*.py', 'tmp_*.py', 'debug_*.py', '*_test.py', 'temp_*.py']
        moved_files = []
        
        for pattern in temp_patterns:
            for file in self.project_root.rglob(pattern):
                # 除外ディレクトリチェック
                if any(excluded in str(file) for excluded in self.config['excluded_dirs']):
                    continue
                
                dest = self.project_root / '_WIP' / file.name
                try:
                    file.rename(dest)
                    moved_files.append(file.name)
                except Exception as e:
                    print(f"⚠️  {file.name} 移動失敗: {e}")
        
        if moved_files:
            print(f"✅ {len(moved_files)}個のファイルを_WIPに移動")
        else:
            print("✅ 移動すべき一時ファイルなし")
        
        return True
    
    # STEP 2: LIST
    def step2_list(self) -> bool:
        """コミット対象をリスト"""
        self._print_step(2, "LIST - コミット対象の列挙")
        
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        files = []
        for line in result.stdout.splitlines():
            if line:
                filepath = line[3:]
                
                # 除外チェック
                if any(excluded in filepath for excluded in self.config['excluded_dirs']):
                    continue
                
                full_path = self.project_root / filepath
                if full_path.exists() and full_path.suffix == '.py':
                    files.append(full_path)
        
        self.staged_files = files
        print(f"📋 コミット対象: {len(files)}ファイル")
        
        if len(files) > 10:
            print("   （最初の10ファイルのみ表示）")
            for f in files[:10]:
                print(f"   ✅ {f.relative_to(self.project_root)}")
            print(f"   ... 他 {len(files)-10}ファイル")
        else:
            for f in files:
                print(f"   ✅ {f.relative_to(self.project_root)}")
        
        return len(files) > 0
    
    # STEP 3: QUALITY GATE - セキュリティチェック
    def step3_security_check(self) -> bool:
        """認証ファイルの検出（Gitの追跡対象のみ）"""
        self._print_step(3, "SECURITY CHECK - 認証ファイル検出")
        
        # Gitの追跡対象ファイルを取得
        result = subprocess.run(
            ['git', 'ls-files'],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        tracked_files = set(result.stdout.splitlines())
        
        # 認証ファイルパターンとマッチするか確認
        secret_files = []
        for pattern in self.config['secret_patterns']:
            for file in self.project_root.glob(pattern):
                rel_path = str(file.relative_to(self.project_root))
                # Gitの追跡対象かつ除外ディレクトリでない
                if rel_path in tracked_files and not any(excluded in rel_path for excluded in self.config['excluded_dirs']):
                    secret_files.append(file)
        
        if secret_files:
            print("❌ 認証ファイルがGitの追跡対象に含まれています:")
            for f in secret_files:
                print(f"   ❌ {f.relative_to(self.project_root)}")
            
            print("\n対処法:")
            print("   1. git rm --cached <ファイル名> で追跡解除")
            print("   2. .gitignoreに追加")
            print("   3. 認証情報を無効化")
            
            return False
        
        print("✅ 認証ファイルなし（Gitの追跡対象）")
        return True
    
    # STEP 3: 重複メソッドチェック
    def step3_duplicate_check(self) -> bool:
        """重複メソッドを検出"""
        self._print_step(3, "DUPLICATE CHECK - 重複メソッド検出")
        
        def find_duplicate_methods(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except:
                return {}
            
            from collections import defaultdict
            methods = defaultdict(list)
            current_class = None
            
            for i, line in enumerate(lines, 1):
                if re.match(r'^\s*class\s+\w+', line):
                    match = re.search(r'class\s+(\w+)', line)
                    if match:
                        current_class = match.group(1)
                
                if re.match(r'^\s*(async\s+)?def\s+\w+', line):
                    match = re.search(r'def\s+(\w+)', line)
                    if match and current_class:
                        method_name = match.group(1)
                        if not method_name.startswith('_') or method_name == 'execute':
                            methods[f"{current_class}.{method_name}"].append(i)
            
            return {k: v for k, v in methods.items() if len(v) > 1}
        
        duplicates_found = {}
        for py_file in self.staged_files:
            dups = find_duplicate_methods(py_file)
            if dups:
                duplicates_found[py_file] = dups
        
        if duplicates_found:
            print("❌ 重複メソッドが検出されました:")
            for filepath, dups in duplicates_found.items():
                print(f"   ❌ {filepath.relative_to(self.project_root)}")
                for method_name, line_numbers in dups.items():
                    print(f"      - {method_name}: 行 {line_numbers}")
            
            return False
        
        print("✅ 重複メソッドなし")
        return True
    
    # STEP 3: コンパイルチェック
    def step3_compile_check(self) -> bool:
        """全ファイルの構文チェック"""
        self._print_step(3, "COMPILE CHECK - 構文チェック")
        
        errors = []
        for file in self.staged_files:
            result = subprocess.run(
                ['python3', '-m', 'py_compile', str(file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                errors.append((file, result.stderr))
        
        if errors:
            print(f"❌ {len(errors)}個のファイルに構文エラー:")
            for file, error in errors[:5]:  # 最初の5つのみ表示
                print(f"   ❌ {file.relative_to(self.project_root)}")
                print(f"      {error[:100]}")
            
            if len(errors) > 5:
                print(f"   ... 他 {len(errors)-5}個のエラー")
            
            return False
        
        print(f"✅ {len(self.staged_files)}個のファイルが構文OK")
        return True
    
    # STEP 5: TEST
    def step5_test(self) -> bool:
        """開発プログラムのテスト実行"""
        self._print_step(5, "TEST - 開発プログラムのテスト")
        
        print("📝 開発したプログラムのテストコマンドを入力してください")
        print("   例: DISPLAY=:1 python3 agents/pm_agent/automation.py")
        print("   例: python3 scripts/test_integration.py")
        print("   スキップする場合は Enter のみ押してください")
        print()
        
        test_command = input("テストコマンド: ").strip()
        
        if not test_command:
            print("⚠️  テストをスキップしました")
            return True
        
        print(f"\n🧪 テスト実行: {test_command}")
        print("-"*70)
        
        # テスト実行
        result = subprocess.run(
            test_command,
            shell=True,
            cwd=self.project_root,
            capture_output=False  # 出力を直接表示
        )
        
        print("-"*70)
        
        if result.returncode != 0:
            print(f"\n❌ テスト失敗（終了コード: {result.returncode}）")
            response = input("\nテスト失敗を無視してコミットしますか？ (y/N): ").strip().lower()
            return response == 'y'
        
        print("\n✅ テスト成功")
        return True
    
    # STEP 6: FINAL CLEANUP
    def step6_cleanup(self) -> bool:
        """不要ファイル削除"""
        self._print_step(6, "FINAL CLEANUP - 不要ファイル削除")
        
        patterns = ['**/__pycache__', '**/*.pyc', '**/*.log', '**/*.tmp']
        removed_count = 0
        
        for pattern in patterns:
            for file in self.project_root.glob(pattern):
                if any(excluded in str(file) for excluded in self.config['excluded_dirs']):
                    continue
                
                try:
                    if file.is_dir():
                        import shutil
                        shutil.rmtree(file)
                    else:
                        file.unlink()
                    removed_count += 1
                except Exception:
                    pass
        
        print(f"✅ {removed_count}個の不要ファイルを削除")
        return True
    
    # STEP 8: .gitignore更新
    def step8_update_gitignore(self) -> bool:
        """必要な除外ルールを.gitignoreに追加"""
        self._print_step(8, "UPDATE .gitignore")
        
        gitignore_path = self.project_root / '.gitignore'
        
        required_patterns = [
            '# 認証情報（絶対にコミットしない）',
            'service_account.json',
            '**/service_account.json',
            '**/*_key.json',
            '**/*.pem',
            '**/credentials.json',
            '',
            '# 実行時生成ファイル',
            '__pycache__/',
            '*.pyc',
            '*.log',
            '*.tmp',
            'logs/',
            'agent_outputs/',
        ]
        
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                existing = f.read()
        else:
            existing = ''
        
        added = []
        for pattern in required_patterns:
            if pattern and pattern not in existing:
                added.append(pattern)
        
        if added:
            with open(gitignore_path, 'a', encoding='utf-8') as f:
                f.write('\n' + '\n'.join(added) + '\n')
            print(f"✅ .gitignoreに{len(added)}個のパターンを追加")
        else:
            print("✅ .gitignoreは最新")
        
        return True
    
    # STEP 9: README更新
    def step9_update_readme(self) -> bool:
        """README更新（対話式）"""
        self._print_step(9, "UPDATE README")
        
        readme_path = self.project_root / 'README.md'
        
        if not readme_path.exists():
            print("⚠️  README.mdが見つかりません")
            return True
        
        print("📝 READMEに追加する内容を入力してください")
        print("   例: ### v1.4.1 新機能")
        print("   例: - ✅ PM Agent自動化完了")
        print("   スキップする場合は Enter のみ押してください")
        print()
        
        readme_content = input("README更新内容（複数行の場合は ; で区切る）: ").strip()
        
        if not readme_content:
            print("⚠️  README更新をスキップしました")
            return True
        
        # 複数行対応
        lines = readme_content.split(';')
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            existing = f.read()
        
        # 変更履歴セクションを探す
        if '## 📝 変更履歴' in existing:
            # 変更履歴セクションの直後に追加
            parts = existing.split('## 📝 変更履歴')
            
            # 最初のセクション（### vX.X.X）の前に追加
            changelog_part = parts[1]
            if '###' in changelog_part:
                first_section_idx = changelog_part.index('###')
                updated_changelog = changelog_part[:first_section_idx] + '\n'.join(lines) + '\n\n' + changelog_part[first_section_idx:]
            else:
                updated_changelog = '\n' + '\n'.join(lines) + '\n' + changelog_part
            
            new_readme = parts[0] + '## 📝 変更履歴' + updated_changelog
        else:
            # 変更履歴セクションがない場合は末尾に追加
            new_readme = existing + '\n\n## 📝 変更履歴\n\n' + '\n'.join(lines) + '\n'
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(new_readme)
        
        print(f"✅ READMEを更新しました")
        return True

    # STEP 10: COMMIT & PUSH
    def step10_commit_and_push(self, message: str, push: bool = True) -> bool:
        """コミット＆プッシュ"""
        self._print_step(9, "COMMIT & PUSH")
        
        # ステージング（削除ファイルを含む）
        subprocess.run(['git', 'add', '-A'], cwd=self.project_root)
        
        print(f"📝 コミットメッセージ: {message}")
        
        # コミット
        result = subprocess.run(
            ['git', 'commit', '-m', message],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            if 'nothing to commit' in result.stdout:
                print("✅ コミットする変更なし")
            else:
                print(f"❌ コミット失敗: {result.stderr}")
                return False
        else:
            print("✅ コミット成功")
        
        if not push:
            return True
        
        # プッシュ
        print("\n🚀 プッシュ中...")
        branch = subprocess.run(
            ['git', 'branch', '--show-current'],
            cwd=self.project_root,
            capture_output=True,
            text=True
        ).stdout.strip()
        
        result = subprocess.run(
            ['git', 'push', 'origin', branch],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ プッシュ失敗:")
            print(result.stderr)
            
            # Push Protection検出
            if 'secret' in result.stderr.lower() or 'GH013' in result.stderr:
                print("\n⚠️  GitHub Push Protectionが発動しました")
                print("   認証ファイルが検出されています")
                print("   git filter-branchで履歴から削除が必要です")
            
            return False
        
        print(f"✅ プッシュ成功: {branch}")
        return True
    
    def run(self, commit_message: str, auto_push: bool = True) -> bool:
        """フルワークフロー実行"""
        print("\n" + "="*70)
        print("🤖 完全自動化Git統合ワークフロー")
        print("="*70)
        print(f"⏰ 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 実行フロー
        steps = [
            ("CLEANUP", self.step1_cleanup, True),
            ("LIST", self.step2_list, True),
            ("SECURITY CHECK", self.step3_security_check, True),
            ("DUPLICATE CHECK", self.step3_duplicate_check, self.config['quality_gates']['duplicate_check']),
            ("COMPILE CHECK", self.step3_compile_check, True),
            ("TEST", self.step5_test, self.config['quality_gates']['test']),
            ("FINAL CLEANUP", self.step6_cleanup, True),
            ("UPDATE .gitignore", self.step8_update_gitignore, True),
            ("UPDATE README", self.step9_update_readme, True),
        ]
        
        for step_name, step_func, enabled in steps:
            if not enabled:
                print(f"\n⚠️  {step_name}はスキップされました")
                continue
            
            try:
                if not step_func():
                    print(f"\n❌ {step_name}でエラー発生 - ワークフロー中断")
                    return False
            except Exception as e:
                print(f"\n❌ {step_name}で例外発生: {e}")
                return False
        
        # 最後にコミット＆プッシュ
        if not self.step10_commit_and_push(commit_message, auto_push):
            return False
        
        print("\n" + "="*70)
        print("🎉 完全自動化ワークフロー完了！")
        print("="*70)
        print(f"⏰ 終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='完全自動化Git統合ワークフロー')
    parser.add_argument('message', help='コミットメッセージ')
    parser.add_argument('--no-push', action='store_true', help='プッシュしない')
    parser.add_argument('--config', help='設定ファイルパス')
    
    args = parser.parse_args()
    
    agent = AutoCommitPushAgent(args.config) if args.config else AutoCommitPushAgent()
    success = agent.run(args.message, not args.no_push)
    
    sys.exit(0 if success else 1)
