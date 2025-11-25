"""
修正版 Git自動コミット・プッシュスクリプト
バックアップファイルを適切に処理するバージョン
"""

import os
import sys
import subprocess
import logging
from datetime import datetime

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class GitManagerFixed:
    """修正版Gitマネージャー - バックアップファイルを適切に処理"""
    
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.ignored_patterns = [
            'git_cleanup_backup_*',
            '*.backup',
            '_BACKUP/',
            '_ARCHIVE/',
            '__pycache__/',
            '*.pyc',
            '.env',
            '*.log'
        ]
    
    def run_git_command(self, command, check=True):
        """Gitコマンドを実行"""
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                shell=True,
                check=check,
                capture_output=True,
                text=True
            )
            logger.info(f"✅ Gitコマンド成功: {command}")
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Gitコマンド失敗: {command}")
            logger.error(f"エラー出力: {e.stderr}")
            return None
    
    def get_files_to_add(self):
        """追加するファイルを安全に取得（無視パターンを除外）"""
        try:
            # 変更されたファイルを取得
            result = self.run_git_command("git status --porcelain", check=False)
            if not result:
                return []
            
            files = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    status, filepath = line[:2], line[3:]
                    filepath = filepath.strip('"')
                    
                    # 無視パターンに一致しないファイルのみ追加
                    if not self._should_ignore(filepath):
                        files.append(filepath)
            
            logger.info(f"📁 追加対象ファイル: {len(files)}件")
            return files
            
        except Exception as e:
            logger.error(f"ファイルリスト取得エラー: {e}")
            return []
    
    def _should_ignore(self, filepath):
        """ファイルが無視すべきパターンに一致するかチェック"""
        for pattern in self.ignored_patterns:
            if pattern in filepath:
                logger.info(f"⚠️  無視ファイルをスキップ: {filepath} (パターン: {pattern})")
                return True
        return False
    
    def safe_add_files(self):
        """安全にファイルを追加（無視パターンを考慮）"""
        files_to_add = self.get_files_to_add()
        
        if not files_to_add:
            logger.info("ℹ️  追加するファイルがありません")
            return True
        
        # ファイルを個別に追加
        success_count = 0
        for filepath in files_to_add:
            try:
                result = self.run_git_command(f'git add "{filepath}"', check=False)
                if result and result.returncode == 0:
                    success_count += 1
                    logger.info(f"✅ ファイル追加: {filepath}")
                else:
                    logger.warning(f"⚠️  ファイル追加スキップ: {filepath}")
            except Exception as e:
                logger.warning(f"⚠️  ファイル追加エラー（スキップ）: {filepath} - {e}")
        
        logger.info(f"📊 ファイル追加結果: {success_count}/{len(files_to_add)}件成功")
        return success_count > 0
    
    def commit_changes(self, message=None):
        """変更をコミット"""
        if not message:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            message = f"自動コミット - {timestamp}"
        
        result = self.run_git_command(f'git commit -m "{message}"', check=False)
        return result is not None and result.returncode == 0
    
    def push_changes(self):
        """変更をプッシュ"""
        result = self.run_git_command("git push", check=False)
        return result is not None and result.returncode == 0
    
    def get_status(self):
        """現在のGit状態を取得"""
        result = self.run_git_command("git status --porcelain", check=False)
        if result:
            return result.stdout
        return ""
    
    def cleanup_ignored_files(self):
        """無視されているファイルを整理"""
        logger.info("🧹 無視ファイルの整理を開始...")
        
        # 無視されているファイルのリストを取得
        result = self.run_git_command("git ls-files --others --ignored --exclude-standard", check=False)
        if result:
            ignored_files = result.stdout.strip().split('\n')
            if ignored_files and ignored_files[0]:
                logger.info(f"📋 無視ファイル数: {len(ignored_files)}件")
                for filepath in ignored_files[:10]:  # 最初の10件のみ表示
                    logger.info(f"  - {filepath}")
                if len(ignored_files) > 10:
                    logger.info(f"  ... 他 {len(ignored_files) - 10}件")
        
        return True

def main():
    """メイン実行関数"""
    logger.info("🚀 修正版Git自動コミット・プッシュを開始します")
    
    git_manager = GitManagerFixed()
    
    # 1. 無視ファイルの整理
    git_manager.cleanup_ignored_files()
    
    # 2. 現在の状態を確認
    status = git_manager.get_status()
    if not status.strip():
        logger.info("ℹ️  コミットする変更がありません")
        return True
    
    logger.info("📋 変更ファイル一覧:")
    for line in status.split('\n'):
        if line.strip():
            logger.info(f"  {line}")
    
    # 3. 安全にファイルを追加
    if not git_manager.safe_add_files():
        logger.error("❌ ファイル追加に失敗しました")
        return False
    
    # 4. コミット
    commit_message = f"自動コミット - {datetime.now().strftime('%Y%m%d_%H%M%S')} - TaskExecutorV4実装"
    if not git_manager.commit_changes(commit_message):
        logger.error("❌ コミットに失敗しました")
        return False
    
    # 5. プッシュ
    if not git_manager.push_changes():
        logger.error("❌ プッシュに失敗しました")
        return False
    
    logger.info("🎉 Git操作が正常に完了しました")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
