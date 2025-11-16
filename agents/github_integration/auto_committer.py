"""
自動GitHubコミッター
目的: タスク完了後に自動的にGitコミット・プッシュ
安全性: コミット前の検証機能付き
"""
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutoCommitter:
    """自動Git操作クラス"""
    
    def __init__(self, project_root: str = "/workspaces/gemini_AI_Agent"):
        self.project_root = Path(project_root)
        self.branch = self._get_current_branch()
        self.dry_run = False  # Trueにすると実際にはコミットしない
    
    def _get_current_branch(self) -> str:
        """現在のブランチ名を取得"""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return 'main'
    
    def commit_task_results(
        self, 
        task_id: str, 
        task_description: str,
        output_files: List[str],
        quality_score: int = 0
    ) -> Dict[str, any]:
        """
        タスク実行結果を自動コミット
        
        Args:
            task_id: タスクID
            task_description: タスク説明
            output_files: 生成されたファイルのパス一覧
            quality_score: 品質スコア
        
        Returns:
            コミット結果の辞書
        """
        result = {
            'success': False,
            'commit_hash': None,
            'pushed': False,
            'message': ''
        }
        
        try:
            # 1. 変更ファイルを確認
            changed_files = self._get_changed_files()
            if not changed_files:
                logger.info("変更がないため、コミットをスキップします")
                result['message'] = 'No changes to commit'
                return result
            
            logger.info(f"変更されたファイル: {len(changed_files)}件")
            
            # 2. 安全性チェック
            safety_check = self._safety_check(changed_files)
            if not safety_check['safe']:
                logger.warning(f"安全性チェック失敗: {safety_check['reason']}")
                result['message'] = f"Safety check failed: {safety_check['reason']}"
                return result
            
            # 3. コミットメッセージ生成
            commit_message = self._generate_commit_message(
                task_id, task_description, output_files, quality_score
            )
            
            # 4. Git add
            self._git_add(output_files)
            
            # 5. Git commit
            if not self.dry_run:
                commit_hash = self._git_commit(commit_message)
                result['commit_hash'] = commit_hash
                logger.info(f"✅ コミット成功: {commit_hash[:8]}")
            else:
                logger.info(f"[DRY RUN] コミットメッセージ:\n{commit_message}")
                result['commit_hash'] = 'dry_run'
            
            # 6. Git push
            if not self.dry_run:
                push_success = self._git_push()
                result['pushed'] = push_success
                if push_success:
                    logger.info(f"✅ プッシュ成功: {self.branch}")
            else:
                logger.info(f"[DRY RUN] プッシュ先: {self.branch}")
            
            result['success'] = True
            result['message'] = 'Commit and push successful'
            
        except Exception as e:
            logger.error(f"自動コミットエラー: {e}")
            result['message'] = str(e)
        
        return result
    
    def _get_changed_files(self) -> List[str]:
        """変更されたファイルを取得"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            changed_files = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    # フォーマット: " M file.py" or "?? file.py"
                    status = line[:2]
                    filepath = line[3:]
                    changed_files.append(filepath)
            
            return changed_files
        except subprocess.CalledProcessError:
            return []
    
    def _safety_check(self, changed_files: List[str]) -> Dict[str, any]:
        """
        コミット前の安全性チェック
        
        - 機密ファイルが含まれていないか
        - サイズが大きすぎないか
        - 重要な設定ファイルが誤って変更されていないか
        """
        # 機密ファイルパターン
        sensitive_patterns = [
            'service_account.json',
            '.env',
            'secrets.yaml',
            'private_key',
            'credentials'
        ]
        
        # 保護すべき重要ファイル
        protected_files = [
            'configuration/service_account.json',
            '.env'
        ]
        
        for file in changed_files:
            # 機密ファイルチェック
            if any(pattern in file.lower() for pattern in sensitive_patterns):
                return {
                    'safe': False,
                    'reason': f'機密ファイルが含まれています: {file}'
                }
            
            # 保護ファイルチェック
            if file in protected_files:
                return {
                    'safe': False,
                    'reason': f'保護されたファイルが変更されています: {file}'
                }
            
            # ファイルサイズチェック（10MB以上は警告）
            file_path = self.project_root / file
            if file_path.exists() and file_path.stat().st_size > 10 * 1024 * 1024:
                return {
                    'safe': False,
                    'reason': f'ファイルサイズが大きすぎます: {file} ({file_path.stat().st_size / 1024 / 1024:.1f}MB)'
                }
        
        return {'safe': True, 'reason': ''}
    
    def _generate_commit_message(
        self, 
        task_id: str, 
        description: str,
        output_files: List[str],
        quality_score: int
    ) -> str:
        """コミットメッセージを生成"""
        # ファイル数とサイズを集計
        total_files = len(output_files)
        total_size = sum(
            Path(f).stat().st_size 
            for f in output_files 
            if Path(f).exists()
        )
        
        # コミットタイプを判定
        commit_type = 'feat'  # デフォルト
        if 'fix' in description.lower() or 'バグ' in description:
            commit_type = 'fix'
        elif 'test' in description.lower() or 'テスト' in description:
            commit_type = 'test'
        elif 'doc' in description.lower() or 'ドキュメント' in description:
            commit_type = 'docs'
        
        # メッセージ構築
        message_lines = [
            f"{commit_type}: タスク{task_id}完了 - {description[:60]}",
            "",
            f"タスクID: {task_id}",
            f"説明: {description}",
            f"品質スコア: {quality_score}/10",
            "",
            f"生成ファイル: {total_files}件 ({total_size:,} bytes)",
            ""
        ]
        
        # ファイル一覧（最大10件）
        if output_files:
            message_lines.append("変更ファイル:")
            for file in output_files[:10]:
                file_path = Path(file)
                if file_path.exists():
                    size = file_path.stat().st_size
                    message_lines.append(f"  - {file_path.name} ({size:,} bytes)")
            
            if len(output_files) > 10:
                message_lines.append(f"  ... 他{len(output_files) - 10}件")
        
        message_lines.extend([
            "",
            f"自動生成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "[auto-commit by AI Agent]"
        ])
        
        return "\n".join(message_lines)
    
    def _git_add(self, files: List[str]):
        """Git add実行"""
        try:
            # agent_outputs配下のファイルを追加
            subprocess.run(
                ['git', 'add', 'agent_outputs/'],
                cwd=self.project_root,
                check=True
            )
            
            # その他の変更ファイルも追加
            subprocess.run(
                ['git', 'add', '-A'],
                cwd=self.project_root,
                check=True
            )
            
            logger.debug("Git add完了")
        except subprocess.CalledProcessError as e:
            logger.error(f"Git addエラー: {e}")
            raise
    
    def _git_commit(self, message: str) -> str:
        """Git commit実行"""
        try:
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            # コミットハッシュを取得
            hash_result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            return hash_result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Git commitエラー: {e}")
            raise
    
    def _git_push(self) -> bool:
        """Git push実行"""
        try:
            subprocess.run(
                ['git', 'push', 'origin', self.branch],
                cwd=self.project_root,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Git pushエラー: {e}")
            return False


# CLIインターフェース
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("使用方法: python auto_committer.py <task_id> <description>")
        sys.exit(1)
    
    task_id = sys.argv[1]
    description = sys.argv[2]
    
    committer = AutoCommitter()
    committer.dry_run = '--dry-run' in sys.argv
    
    result = committer.commit_task_results(
        task_id=task_id,
        task_description=description,
        output_files=[f"agent_outputs/tasks/task_{task_id}/"],
        quality_score=9
    )
    
    print(f"結果: {result}")
