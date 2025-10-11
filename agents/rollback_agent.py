"""
RollbackAgent - 高度なロールバック管理エージェント

修正が失敗した際の安全装置として、複数ファイルの一括ロールバック、
時系列でのロールバック、影響分析、自動ロールバック判定を提供する。
"""

import os
import shutil
import hashlib
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import subprocess

logger = logging.getLogger(__name__)


class RollbackScope(Enum):
    """ロールバックスコープ"""
    SINGLE_FILE = "single_file"
    RELATED_FILES = "related_files"
    ENTIRE_COMMIT = "entire_commit"
    TIME_RANGE = "time_range"


class RollbackReason(Enum):
    """ロールバック理由"""
    TEST_FAILURE = "test_failure"
    RUNTIME_ERROR = "runtime_error"
    MANUAL_REQUEST = "manual_request"
    AUTO_DETECTION = "auto_detection"
    DEPENDENCY_ISSUE = "dependency_issue"


@dataclass
class FileSnapshot:
    """ファイルスナップショット"""
    file_path: str
    content: str
    content_hash: str
    timestamp: datetime
    backup_path: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "content_hash": self.content_hash,
            "timestamp": self.timestamp.isoformat(),
            "backup_path": self.backup_path,
            "metadata": self.metadata
        }


@dataclass
class RollbackPoint:
    """ロールバックポイント"""
    id: str
    timestamp: datetime
    snapshots: List[FileSnapshot]
    commit_hash: Optional[str] = None
    description: str = ""
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "snapshots": [s.to_dict() for s in self.snapshots],
            "commit_hash": self.commit_hash,
            "description": self.description,
            "tags": self.tags
        }


@dataclass
class RollbackResult:
    """ロールバック結果"""
    success: bool
    rollback_point_id: str
    files_restored: List[str]
    files_failed: List[str]
    reason: RollbackReason
    timestamp: datetime
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "rollback_point_id": self.rollback_point_id,
            "files_restored": self.files_restored,
            "files_failed": self.files_failed,
            "reason": self.reason.value,
            "timestamp": self.timestamp.isoformat(),
            "error_message": self.error_message
        }


class RollbackAgent:
    """
    高度なロールバック管理エージェント
    
    主な機能:
    1. 複数ファイルの一括ロールバック
    2. 時系列でのロールバック
    3. 特定のコミットへのロールバック
    4. ロールバック前の影響分析
    5. 自動ロールバック判定
    """
    
    def __init__(self, 
                 backup_dir: str = ".rollback_backup",
                 max_snapshots: int = 100,
                 auto_rollback_enabled: bool = True):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_snapshots = max_snapshots
        self.auto_rollback_enabled = auto_rollback_enabled
        
        # ロールバックポイントの管理
        self.rollback_points: Dict[str, RollbackPoint] = {}
        self.rollback_history: List[RollbackResult] = []
        
        # メタデータファイル
        self.metadata_file = self.backup_dir / "rollback_metadata.json"
        
        # 起動時にメタデータを読み込む
        self._load_metadata()
        
        logger.info(f"RollbackAgent initialized (backup_dir={backup_dir})")
    
    def create_snapshot(self, 
                       file_paths: List[str],
                       description: str = "",
                       tags: List[str] = None) -> str:
        """
        ファイルのスナップショットを作成
        
        Args:
            file_paths: バックアップするファイルパスのリスト
            description: スナップショットの説明
            tags: タグのリスト
        
        Returns:
            作成されたロールバックポイントのID
        """
        snapshot_id = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        snapshots = []
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                continue
            
            try:
                # ファイル内容を読み込む
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # ハッシュを計算
                content_hash = hashlib.sha256(content.encode()).hexdigest()
                
                # バックアップファイルパスを生成
                backup_path = self.backup_dir / f"{snapshot_id}_{Path(file_path).name}"
                
                # バックアップファイルに保存
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # スナップショットを作成
                snapshot = FileSnapshot(
                    file_path=file_path,
                    content=content,
                    content_hash=content_hash,
                    timestamp=datetime.now(),
                    backup_path=str(backup_path),
                    metadata={
                        "file_size": len(content),
                        "line_count": content.count('\n') + 1
                    }
                )
                snapshots.append(snapshot)
                
                logger.debug(f"Created snapshot for {file_path}")
                
            except Exception as e:
                logger.error(f"Failed to create snapshot for {file_path}: {e}")
        
        # Git コミットハッシュを取得（可能なら）
        commit_hash = self._get_current_commit_hash()
        
        # ロールバックポイントを作成
        rollback_point = RollbackPoint(
            id=snapshot_id,
            timestamp=datetime.now(),
            snapshots=snapshots,
            commit_hash=commit_hash,
            description=description,
            tags=tags or []
        )
        
        # 保存
        self.rollback_points[snapshot_id] = rollback_point
        self._save_metadata()
        
        # 古いスナップショットを削除
        self._cleanup_old_snapshots()
        
        logger.info(f"Created rollback point: {snapshot_id} ({len(snapshots)} files)")
        
        return snapshot_id
    
    def rollback(self, 
                rollback_point_id: str,
                reason: RollbackReason = RollbackReason.MANUAL_REQUEST,
                dry_run: bool = False) -> RollbackResult:
        """
        指定されたロールバックポイントまで復元
        
        Args:
            rollback_point_id: ロールバックポイントID
            reason: ロールバック理由
            dry_run: True の場合、実際には復元せずに影響を分析
        
        Returns:
            ロールバック結果
        """
        if rollback_point_id not in self.rollback_points:
            return RollbackResult(
                success=False,
                rollback_point_id=rollback_point_id,
                files_restored=[],
                files_failed=[],
                reason=reason,
                timestamp=datetime.now(),
                error_message=f"Rollback point not found: {rollback_point_id}"
            )
        
        rollback_point = self.rollback_points[rollback_point_id]
        files_restored = []
        files_failed = []
        
        logger.info(f"Starting rollback to {rollback_point_id} (dry_run={dry_run})")
        
        for snapshot in rollback_point.snapshots:
            try:
                if dry_run:
                    # ドライランモード: 影響分析のみ
                    if os.path.exists(snapshot.file_path):
                        with open(snapshot.file_path, 'r', encoding='utf-8') as f:
                            current_content = f.read()
                        
                        if current_content != snapshot.content:
                            files_restored.append(snapshot.file_path)
                            logger.debug(f"[DRY RUN] Would restore: {snapshot.file_path}")
                    else:
                        files_failed.append(snapshot.file_path)
                        logger.warning(f"[DRY RUN] File not found: {snapshot.file_path}")
                else:
                    # 実際にファイルを復元
                    # まず現在の状態をバックアップ
                    if os.path.exists(snapshot.file_path):
                        self._create_emergency_backup(snapshot.file_path)
                    
                    # 親ディレクトリを作成
                    Path(snapshot.file_path).parent.mkdir(parents=True, exist_ok=True)
                    
                    # ファイルを復元
                    with open(snapshot.file_path, 'w', encoding='utf-8') as f:
                        f.write(snapshot.content)
                    
                    files_restored.append(snapshot.file_path)
                    logger.info(f"Restored: {snapshot.file_path}")
                    
            except Exception as e:
                files_failed.append(snapshot.file_path)
                logger.error(f"Failed to restore {snapshot.file_path}: {e}")
        
        # 結果を作成
        result = RollbackResult(
            success=len(files_failed) == 0,
            rollback_point_id=rollback_point_id,
            files_restored=files_restored,
            files_failed=files_failed,
            reason=reason,
            timestamp=datetime.now(),
            error_message=None if len(files_failed) == 0 else f"{len(files_failed)} files failed"
        )
        
        # 履歴に記録
        if not dry_run:
            self.rollback_history.append(result)
            self._save_metadata()
        
        logger.info(f"Rollback completed: {len(files_restored)} restored, {len(files_failed)} failed")
        
        return result
    
    def rollback_by_time(self, 
                        target_time: datetime,
                        reason: RollbackReason = RollbackReason.MANUAL_REQUEST) -> RollbackResult:
        """
        指定された時刻に最も近いロールバックポイントまで復元
        
        Args:
            target_time: 目標時刻
            reason: ロールバック理由
        
        Returns:
            ロールバック結果
        """
        if not self.rollback_points:
            return RollbackResult(
                success=False,
                rollback_point_id="",
                files_restored=[],
                files_failed=[],
                reason=reason,
                timestamp=datetime.now(),
                error_message="No rollback points available"
            )
        
        # 最も近いロールバックポイントを見つける
        closest_point = min(
            self.rollback_points.values(),
            key=lambda p: abs((p.timestamp - target_time).total_seconds())
        )
        
        logger.info(f"Rolling back to closest point: {closest_point.id} "
                   f"(target={target_time}, actual={closest_point.timestamp})")
        
        return self.rollback(closest_point.id, reason)
    
    def rollback_by_commit(self, 
                          commit_hash: str,
                          reason: RollbackReason = RollbackReason.MANUAL_REQUEST) -> RollbackResult:
        """
        指定されたコミットのロールバックポイントまで復元
        
        Args:
            commit_hash: Git コミットハッシュ
            reason: ロールバック理由
        
        Returns:
            ロールバック結果
        """
        # コミットハッシュが一致するロールバックポイントを検索
        matching_points = [
            p for p in self.rollback_points.values()
            if p.commit_hash and p.commit_hash.startswith(commit_hash)
        ]
        
        if not matching_points:
            return RollbackResult(
                success=False,
                rollback_point_id="",
                files_restored=[],
                files_failed=[],
                reason=reason,
                timestamp=datetime.now(),
                error_message=f"No rollback point found for commit: {commit_hash}"
            )
        
        # 最新のものを使用
        target_point = max(matching_points, key=lambda p: p.timestamp)
        
        logger.info(f"Rolling back to commit {commit_hash}: {target_point.id}")
        
        return self.rollback(target_point.id, reason)
    
    def analyze_impact(self, rollback_point_id: str) -> Dict[str, Any]:
        """
        ロールバックの影響を分析
        
        Args:
            rollback_point_id: ロールバックポイントID
        
        Returns:
            影響分析結果
        """
        result = self.rollback(rollback_point_id, dry_run=True)
        
        if not result.success:
            return {
                "error": result.error_message,
                "can_rollback": False
            }
        
        rollback_point = self.rollback_points[rollback_point_id]
        
        # 変更の詳細を分析
        changes = []
        for snapshot in rollback_point.snapshots:
            if not os.path.exists(snapshot.file_path):
                changes.append({
                    "file": snapshot.file_path,
                    "type": "missing",
                    "description": "File will be restored from backup"
                })
                continue
            
            try:
                with open(snapshot.file_path, 'r', encoding='utf-8') as f:
                    current_content = f.read()
                
                if current_content != snapshot.content:
                    current_lines = current_content.count('\n') + 1
                    snapshot_lines = snapshot.content.count('\n') + 1
                    
                    changes.append({
                        "file": snapshot.file_path,
                        "type": "modified",
                        "current_lines": current_lines,
                        "rollback_lines": snapshot_lines,
                        "line_diff": snapshot_lines - current_lines
                    })
                    
            except Exception as e:
                changes.append({
                    "file": snapshot.file_path,
                    "type": "error",
                    "description": str(e)
                })
        
        return {
            "can_rollback": True,
            "rollback_point_id": rollback_point_id,
            "timestamp": rollback_point.timestamp.isoformat(),
            "files_affected": len(rollback_point.snapshots),
            "files_to_restore": len(result.files_restored),
            "changes": changes
        }
    
    def should_auto_rollback(self, 
                           error_context: Dict[str, Any],
                           test_results: Dict[str, Any]) -> bool:
        """
        自動ロールバックが必要かを判定
        
        Args:
            error_context: エラーコンテキスト
            test_results: テスト結果
        
        Returns:
            True if auto rollback should be performed
        """
        if not self.auto_rollback_enabled:
            return False
        
        # クリティカルなエラータイプ
        critical_errors = [
            'SyntaxError',
            'ImportError',
            'ModuleNotFoundError',
            'AttributeError'
        ]
        
        error_type = error_context.get('error_type', '')
        
        # クリティカルエラーの場合
        if error_type in critical_errors:
            logger.warning(f"Critical error detected: {error_type}")
            return True
        
        # テストが大量に失敗している場合
        if test_results:
            failed = test_results.get('failed', 0)
            total = test_results.get('total', 0)
            
            if total > 0 and failed / total > 0.5:  # 50%以上失敗
                logger.warning(f"High test failure rate: {failed}/{total}")
                return True
        
        return False
    
    def list_rollback_points(self, 
                            tags: List[str] = None,
                            limit: int = 10) -> List[Dict[str, Any]]:
        """
        ロールバックポイント一覧を取得
        
        Args:
            tags: フィルタリング用タグ
            limit: 最大取得数
        
        Returns:
            ロールバックポイントのリスト
        """
        points = list(self.rollback_points.values())
        
        # タグでフィルタリング
        if tags:
            points = [p for p in points if any(tag in p.tags for tag in tags)]
        
        # 時刻でソート（新しい順）
        points.sort(key=lambda p: p.timestamp, reverse=True)
        
        # 制限を適用
        points = points[:limit]
        
        return [
            {
                "id": p.id,
                "timestamp": p.timestamp.isoformat(),
                "files_count": len(p.snapshots),
                "description": p.description,
                "tags": p.tags,
                "commit_hash": p.commit_hash
            }
            for p in points
        ]
    
    def delete_rollback_point(self, rollback_point_id: str) -> bool:
        """ロールバックポイントを削除"""
        if rollback_point_id not in self.rollback_points:
            return False
        
        rollback_point = self.rollback_points[rollback_point_id]
        
        # バックアップファイルを削除
        for snapshot in rollback_point.snapshots:
            try:
                if os.path.exists(snapshot.backup_path):
                    os.remove(snapshot.backup_path)
            except Exception as e:
                logger.warning(f"Failed to delete backup file: {e}")
        
        # ロールバックポイントを削除
        del self.rollback_points[rollback_point_id]
        self._save_metadata()
        
        logger.info(f"Deleted rollback point: {rollback_point_id}")
        
        return True
    
    def _get_current_commit_hash(self) -> Optional[str]:
        """現在の Git コミットハッシュを取得"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.debug(f"Failed to get git commit hash: {e}")
        
        return None
    
    def _create_emergency_backup(self, file_path: str):
        """緊急バックアップを作成"""
        emergency_backup = self.backup_dir / f"emergency_{Path(file_path).name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, emergency_backup)
        logger.debug(f"Created emergency backup: {emergency_backup}")
    
    def _cleanup_old_snapshots(self):
        """古いスナップショットを削除"""
        if len(self.rollback_points) <= self.max_snapshots:
            return
        
        # 古い順にソート
        sorted_points = sorted(
            self.rollback_points.values(),
            key=lambda p: p.timestamp
        )
        
        # 削除する数を計算
        to_delete = len(sorted_points) - self.max_snapshots
        
        for point in sorted_points[:to_delete]:
            self.delete_rollback_point(point.id)
        
        logger.info(f"Cleaned up {to_delete} old snapshots")
    
    def _save_metadata(self):
        """メタデータをファイルに保存"""
        metadata = {
            "rollback_points": {
                point_id: point.to_dict()
                for point_id, point in self.rollback_points.items()
            },
            "rollback_history": [
                result.to_dict()
                for result in self.rollback_history[-100:]  # 最新100件のみ
            ]
        }
        
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def _load_metadata(self):
        """メタデータをファイルから読み込む"""
        if not self.metadata_file.exists():
            return
        
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # ロールバックポイントを復元
            for point_id, point_data in metadata.get("rollback_points", {}).items():
                snapshots = [
                    FileSnapshot(
                        file_path=s["file_path"],
                        content="",  # 内容はバックアップファイルから読み込む
                        content_hash=s["content_hash"],
                        timestamp=datetime.fromisoformat(s["timestamp"]),
                        backup_path=s["backup_path"],
                        metadata=s.get("metadata", {})
                    )
                    for s in point_data["snapshots"]
                ]
                
                rollback_point = RollbackPoint(
                    id=point_data["id"],
                    timestamp=datetime.fromisoformat(point_data["timestamp"]),
                    snapshots=snapshots,
                    commit_hash=point_data.get("commit_hash"),
                    description=point_data.get("description", ""),
                    tags=point_data.get("tags", [])
                )
                
                self.rollback_points[point_id] = rollback_point
            
            logger.info(f"Loaded {len(self.rollback_points)} rollback points from metadata")
            
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")


# 使用例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    agent = RollbackAgent(backup_dir=".test_rollback")
    
    # テストファイルを作成
    test_file = "test_file.py"
    with open(test_file, 'w') as f:
        f.write("# Version 1\nprint('Hello')")
    
    # スナップショットを作成
    snapshot_id = agent.create_snapshot(
        [test_file],
        description="Initial version",
        tags=["test", "initial"]
    )
    
    # ファイルを変更
    with open(test_file, 'w') as f:
        f.write("# Version 2\nprint('Hello World')")
    
    # 影響分析
    impact = agent.analyze_impact(snapshot_id)
    print(f"\nImpact Analysis:\n{json.dumps(impact, indent=2)}")
    
    # ロールバック
    result = agent.rollback(snapshot_id)
    print(f"\nRollback Result:\n{json.dumps(result.to_dict(), indent=2)}")
    
    # ロールバックポイント一覧
    points = agent.list_rollback_points()
    print(f"\nRollback Points:\n{json.dumps(points, indent=2)}")
    
    # クリーンアップ
    os.remove(test_file)
