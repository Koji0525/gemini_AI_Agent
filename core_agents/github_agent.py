# github_agent.py
"""
GitHub連携エージェント
Git操作とプルリクエストの自動作成
"""

import asyncio
import logging
import os
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class GitHubAgent:
    """
    GitHub連携エージェント
    
    機能:
    - Git操作（ブランチ作成、コミット、プッシュ）
    - プルリクエストの自動作成
    - コミットメッセージの自動生成
    - GitHub API連携
    """
    
    def __init__(
        self,
        repo_path: str = ".",
        github_token: Optional[str] = None,
        repo_owner: Optional[str] = None,
        repo_name: Optional[str] = None
    ):
        """
        初期化
        
        Args:
            repo_path: リポジトリのパス
            github_token: GitHub Personal Access Token
            repo_owner: リポジトリオーナー
            repo_name: リポジトリ名
        """
        self.repo_path = Path(repo_path)
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        
        # GitHub APIクライアント（オプション）
        self.github_api = None
        if self.github_token:
            self._init_github_api()
        
        # 統計情報
        self.stats = {
            "total_commits": 0,
            "total_prs": 0,
            "successful_prs": 0,
            "failed_prs": 0
        }
        
        logger.info(f"✅ GitHubAgent 初期化完了 (repo={repo_path})")
    
    def _init_github_api(self):
        """GitHub APIクライアントを初期化"""
        try:
            from github import Github
            self.github_api = Github(self.github_token)
            logger.info("✅ GitHub API クライアント初期化完了")
        except ImportError:
            logger.warning("⚠️ PyGithub がインストールされていません。API機能は利用できません。")
            self.github_api = None
    
    async def create_fix_branch_and_commit(
        self,
        task_id: str,
        modified_files: List[str],
        commit_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        修正用ブランチを作成してコミット
        
        Args:
            task_id: タスクID
            modified_files: 修正されたファイルのリスト
            commit_message: コミットメッセージ（省略時は自動生成）
            
        Returns:
            Dict: 実行結果
        """
        try:
            logger.info("=" * 60)
            logger.info(f"🌿 修正ブランチ作成 & コミット: {task_id}")
            logger.info("=" * 60)
            
            # ブランチ名を生成
            branch_name = self._generate_branch_name(task_id)
            
            # 現在のブランチを保存
            current_branch = await self._get_current_branch()
            logger.info(f"📍 現在のブランチ: {current_branch}")
            
            # 新しいブランチを作成
            create_result = await self._create_branch(branch_name)
            if not create_result["success"]:
                return create_result
            
            logger.info(f"🌿 ブランチ作成成功: {branch_name}")
            
            # ファイルをステージング
            stage_result = await self._stage_files(modified_files)
            if not stage_result["success"]:
                await self._checkout_branch(current_branch)
                return stage_result
            
            # コミットメッセージを生成
            if not commit_message:
                commit_message = self._generate_commit_message(task_id, modified_files)
            
            # コミット
            commit_result = await self._commit(commit_message)
            if not commit_result["success"]:
                await self._checkout_branch(current_branch)
                return commit_result
            
            self.stats["total_commits"] += 1
            logger.info(f"✅ コミット成功: {commit_result['commit_hash']}")
            
            return {
                "success": True,
                "branch_name": branch_name,
                "commit_hash": commit_result["commit_hash"],
                "original_branch": current_branch,
                "commit_message": commit_message
            }
            
        except Exception as e:
            logger.error(f"💥 ブランチ作成/コミットエラー: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def push_and_create_pr(
        self,
        branch_name: str,
        pr_title: Optional[str] = None,
        pr_body: Optional[str] = None,
        base_branch: str = "main"
    ) -> Dict[str, Any]:
        """
        ブランチをプッシュしてプルリクエストを作成
        
        Args:
            branch_name: ブランチ名
            pr_title: PRタイトル（省略時は自動生成）
            pr_body: PR本文（省略時は自動生成）
            base_branch: マージ先ブランチ
            
        Returns:
            Dict: 実行結果
        """
        try:
            logger.info("=" * 60)
            logger.info(f"🚀 プッシュ & PR作成: {branch_name}")
            logger.info("=" * 60)
            
            self.stats["total_prs"] += 1
            
            # プッシュ
            push_result = await self._push_branch(branch_name)
            if not push_result["success"]:
                self.stats["failed_prs"] += 1
                return push_result
            
            logger.info(f"✅ プッシュ成功: {branch_name}")
            
            # プルリクエスト作成
            if self.github_api and self.repo_owner and self.repo_name:
                # GitHub API経由
                pr_result = await self._create_pr_via_api(
                    branch_name,
                    pr_title,
                    pr_body,
                    base_branch
                )
            else:
                # GitHub CLI経由
                pr_result = await self._create_pr_via_cli(
                    branch_name,
                    pr_title,
                    pr_body,
                    base_branch
                )
            
            if pr_result["success"]:
                self.stats["successful_prs"] += 1
                logger.info(f"✅ PR作成成功: {pr_result['pr_url']}")
            else:
                self.stats["failed_prs"] += 1
            
            return pr_result
            
        except Exception as e:
            logger.error(f"💥 プッシュ/PR作成エラー: {e}", exc_info=True)
            self.stats["failed_prs"] += 1
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_full_fix_workflow(
        self,
        task_id: str,
        modified_files: List[str],
        fix_description: str,
        base_branch: str = "main"
    ) -> Dict[str, Any]:
        """
        完全な修正ワークフローを実行
        
        Args:
            task_id: タスクID
            modified_files: 修正されたファイル
            fix_description: 修正内容の説明
            base_branch: マージ先ブランチ
            
        Returns:
            Dict: 実行結果
        """
        try:
            logger.info("🔄 完全な修正ワークフロー開始")
            
            # 1. ブランチ作成 & コミット
            commit_result = await self.create_fix_branch_and_commit(
                task_id,
                modified_files
            )
            
            if not commit_result["success"]:
                return commit_result
            
            branch_name = commit_result["branch_name"]
            
            # 2. プッシュ & PR作成
            pr_title = f"🔧 Fix: {task_id}"
            pr_body = self._generate_pr_body(
                task_id,
                modified_files,
                fix_description,
                commit_result["commit_hash"]
            )
            
            pr_result = await self.push_and_create_pr(
                branch_name,
                pr_title,
                pr_body,
                base_branch
            )
            
            if pr_result["success"]:
                logger.info("=" * 60)
                logger.info("✅ 完全な修正ワークフロー成功")
                logger.info(f"📋 PR URL: {pr_result['pr_url']}")
                logger.info("=" * 60)
            
            return {
                **pr_result,
                "branch_name": branch_name,
                "commit_hash": commit_result["commit_hash"],
                "original_branch": commit_result["original_branch"]
            }
            
        except Exception as e:
            logger.error(f"💥 ワークフローエラー: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================
    # Git操作関数
    # ========================================
    
    async def _run_git_command(self, *args) -> Dict[str, Any]:
        """Gitコマンドを実行"""
        try:
            cmd = ["git", "-C", str(self.repo_path)] + list(args)
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            stdout_text = stdout.decode('utf-8').strip()
            stderr_text = stderr.decode('utf-8').strip()
            
            success = process.returncode == 0
            
            if not success:
                logger.error(f"❌ Git コマンドエラー: {' '.join(args)}")
                logger.error(f"   stderr: {stderr_text}")
            
            return {
                "success": success,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "returncode": process.returncode
            }
            
        except Exception as e:
            logger.error(f"❌ Git コマンド実行エラー: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_current_branch(self) -> str:
        """現在のブランチ名を取得"""
        result = await self._run_git_command("branch", "--show-current")
        return result.get("stdout", "main")
    
    async def _create_branch(self, branch_name: str) -> Dict[str, Any]:
        """新しいブランチを作成してチェックアウト"""
        result = await self._run_git_command("checkout", "-b", branch_name)
        return result
    
    async def _checkout_branch(self, branch_name: str) -> Dict[str, Any]:
        """ブランチをチェックアウト"""
        result = await self._run_git_command("checkout", branch_name)
        return result
    
    async def _stage_files(self, files: List[str]) -> Dict[str, Any]:
        """ファイルをステージング"""
        for file in files:
            result = await self._run_git_command("add", file)
            if not result["success"]:
                return result
        
        return {"success": True}
    
    async def _commit(self, message: str) -> Dict[str, Any]:
        """コミットを作成"""
        result = await self._run_git_command("commit", "-m", message)
        
        if result["success"]:
            # コミットハッシュを取得
            hash_result = await self._run_git_command("rev-parse", "HEAD")
            result["commit_hash"] = hash_result.get("stdout", "")[:8]
        
        return result
    
    async def _push_branch(self, branch_name: str) -> Dict[str, Any]:
        """ブランチをリモートにプッシュ"""
        result = await self._run_git_command(
            "push",
            "-u",
            "origin",
            branch_name
        )
        return result
    
    # ========================================
    # PR作成関数
    # ========================================
    
    async def _create_pr_via_api(
        self,
        branch_name: str,
        pr_title: Optional[str],
        pr_body: Optional[str],
        base_branch: str
    ) -> Dict[str, Any]:
        """GitHub API経由でPRを作成"""
        try:
            if not self.github_api:
                return {
                    "success": False,
                    "error": "GitHub API client not initialized"
                }
            
            repo = self.github_api.get_repo(f"{self.repo_owner}/{self.repo_name}")
            
            pr = await asyncio.to_thread(
                repo.create_pull,
                title=pr_title or f"Auto-fix: {branch_name}",
                body=pr_body or "Automated bug fix",
                head=branch_name,
                base=base_branch
            )
            
            return {
                "success": True,
                "pr_number": pr.number,
                "pr_url": pr.html_url
            }
            
        except Exception as e:
            logger.error(f"❌ GitHub API PR作成エラー: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_pr_via_cli(
        self,
        branch_name: str,
        pr_title: Optional[str],
        pr_body: Optional[str],
        base_branch: str
    ) -> Dict[str, Any]:
        """GitHub CLI経由でPRを作成"""
        try:
            cmd = [
                "gh", "pr", "create",
                "--base", base_branch,
                "--head", branch_name,
                "--title", pr_title or f"Auto-fix: {branch_name}",
                "--body", pr_body or "Automated bug fix"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.repo_path
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                pr_url = stdout.decode('utf-8').strip()
                return {
                    "success": True,
                    "pr_url": pr_url
                }
            else:
                return {
                    "success": False,
                    "error": stderr.decode('utf-8').strip()
                }
                
        except Exception as e:
            logger.error(f"❌ GitHub CLI PR作成エラー: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================
    # ユーティリティ
    # ========================================
    
    def _generate_branch_name(self, task_id: str) -> str:
        """ブランチ名を生成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_task_id = task_id.replace(" ", "_").replace("/", "-")
        return f"auto-fix/{safe_task_id}_{timestamp}"
    
    def _generate_commit_message(
        self,
        task_id: str,
        modified_files: List[str]
    ) -> str:
        """コミットメッセージを自動生成"""
        file_list = "\n".join(f"  - {f}" for f in modified_files[:5])
        
        if len(modified_files) > 5:
            file_list += f"\n  ... and {len(modified_files) - 5} more files"
        
        return f"""🔧 Auto-fix: {task_id}

Modified files:
{file_list}

Generated by: HybridFixOrchestrator
Timestamp: {datetime.now().isoformat()}
"""
    
    def _generate_pr_body(
        self,
        task_id: str,
        modified_files: List[str],
        fix_description: str,
        commit_hash: str
    ) -> str:
        """PR本文を自動生成"""
        file_list = "\n".join(f"- `{f}`" for f in modified_files)
        
        return f"""## 🔧 自動修正: {task_id}

### 📝 修正内容
{fix_description}

### 📂 変更されたファイル
{file_list}

### 🤖 自動生成情報
- **コミットハッシュ**: `{commit_hash}`
- **生成日時**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **生成エージェント**: HybridFixOrchestrator

### ✅ チェックリスト
- [ ] コードレビュー完了
- [ ] テスト実行確認
- [ ] ドキュメント更新（必要な場合）

---
*このPRは自動生成されました。マージ前に必ずレビューしてください。*
"""
    
    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        pr_success_rate = 0.0
        if self.stats["total_prs"] > 0:
            pr_success_rate = self.stats["successful_prs"] / self.stats["total_prs"]
        
        return {
            **self.stats,
            "pr_success_rate": pr_success_rate
        }