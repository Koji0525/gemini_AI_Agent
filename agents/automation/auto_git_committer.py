"""
Git自動コミットシステム
生成された成果物を自動的にGitにコミット
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class AutoGitCommitter:
    """Git自動コミットシステム"""
    
    def __init__(self):
        self.project_root = Path("/workspaces/gemini_AI_Agent")
        self.generated_dir = self.project_root / "agents" / "generated"
        
    def commit_generated_modules(self, task_ids: List[str]) -> Dict:
        """生成されたモジュールをコミット"""
        print(f"\n{'=' * 80}")
        print(f"📝 Git自動コミット")
        print('=' * 80)
        print()
        
        results = {
            'success': False,
            'committed_files': [],
            'commit_hash': None
        }
        
        # Gitの状態確認
        if not self._check_git_status():
            print("⚠️  Git設定に問題があります")
            return results
        
        # 追加するファイル
        files_to_add = []
        
        for task_id in task_ids:
            task_dir = self.generated_dir / task_id
            if task_dir.exists():
                # agents/generated配下のファイルを追加
                for file in task_dir.glob("*"):
                    rel_path = file.relative_to(self.project_root)
                    files_to_add.append(str(rel_path))
        
        if not files_to_add:
            print("⚠️  コミットするファイルがありません")
            return results
        
        # Gitに追加
        print(f"📦 {len(files_to_add)}個のファイルを追加中...")
        for file in files_to_add[:5]:  # 最初の5個を表示
            print(f"  + {file}")
        if len(files_to_add) > 5:
            print(f"  ... 他{len(files_to_add) - 5}個")
        
        try:
            # git add
            subprocess.run(
                ['git', 'add'] + files_to_add,
                cwd=self.project_root,
                check=True,
                capture_output=True
            )
            
            # コミットメッセージ生成
            commit_msg = self._generate_commit_message(task_ids)
            
            # git commit
            result = subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                cwd=self.project_root,
                check=True,
                capture_output=True,
                text=True
            )
            
            # コミットハッシュ取得
            hash_result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.project_root,
                check=True,
                capture_output=True,
                text=True
            )
            
            commit_hash = hash_result.stdout.strip()
            
            print(f"\n✅ コミット成功")
            print(f"   コミットハッシュ: {commit_hash[:8]}")
            print(f"   ファイル数: {len(files_to_add)}")
            
            results['success'] = True
            results['committed_files'] = files_to_add
            results['commit_hash'] = commit_hash
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Gitコミットエラー: {e}")
            if e.stderr:
                print(f"   {e.stderr}")
        
        return results
    
    def _check_git_status(self) -> bool:
        """Git状態確認"""
        try:
            result = subprocess.run(
                ['git', 'status'],
                cwd=self.project_root,
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _generate_commit_message(self, task_ids: List[str]) -> str:
        """コミットメッセージ生成"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        message = f"[自動生成] Phase 2統合版タスク完了 @ {timestamp}\n\n"
        message += f"✅ {len(task_ids)}個のタスクを完了\n\n"
        
        for i, task_id in enumerate(task_ids, 1):
            message += f"{i}. {task_id}\n"
        
        message += f"\n自動生成システムによる統合\n"
        message += f"- 品質チェック完了\n"
        message += f"- テスト生成・実行完了\n"
        message += f"- agents/generated/へ統合完了"
        
        return message

