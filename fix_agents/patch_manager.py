# patch_manager.py
"""
パッチマネージャー
コードパッチの安全な適用と管理
"""

import asyncio
import logging
import difflib
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class PatchStrategy(Enum):
    """パッチ適用戦略"""

    REPLACE = "replace"  # ファイル全体を置換
    DIFF = "diff"  # 差分パッチを適用
    MERGE = "merge"  # マージ
    SAFE_INSERT = "safe_insert"  # 安全な挿入


class PatchManager:
    """
    パッチマネージャー

    機能:
    - 安全なコードパッチ適用
    - バックアップ管理
    - 差分生成
    - ロールバック機能
    - パッチ検証
    """

    def __init__(self, backup_dir: str = "./backups/patches", max_backups: int = 10):
        """
        初期化

        Args:
            backup_dir: バックアップディレクトリ
            max_backups: 保持する最大バックアップ数
        """
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups

        # バックアップディレクトリ作成
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # パッチ履歴
        self.patch_history = []

        # 統計情報
        self.stats = {"total_patches": 0, "successful_patches": 0, "failed_patches": 0, "rollbacks": 0}

        logger.info(f"✅ PatchManager 初期化完了 (backup_dir={backup_dir})")

    async def apply_patch(
        self, file_path: str, new_content: str, strategy: PatchStrategy = PatchStrategy.REPLACE, verify: bool = True
    ) -> Dict[str, Any]:
        """
        パッチを適用

        Args:
            file_path: 対象ファイルパス
            new_content: 新しい内容
            strategy: 適用戦略
            verify: 適用前の検証フラグ

        Returns:
            Dict: 適用結果
        """
        start_time = datetime.now()
        file_path_obj = Path(file_path)

        try:
            logger.info("=" * 60)
            logger.info(f"🔧 パッチ適用開始: {file_path}")
            logger.info(f"📊 戦略: {strategy.value}")
            logger.info("=" * 60)

            self.stats["total_patches"] += 1

            # ファイルが存在しない場合
            if not file_path_obj.exists():
                logger.warning(f"⚠️ ファイルが存在しません: {file_path}")
                return await self._create_new_file(file_path, new_content)

            # 現在の内容を読み込み
            old_content = await asyncio.to_thread(file_path_obj.read_text, encoding="utf-8")

            # 変更がない場合
            if old_content == new_content:
                logger.info("ℹ️ 内容に変更はありません")
                return {"success": True, "changed": False, "message": "No changes"}

            # 検証
            if verify:
                validation_result = await self._validate_patch(old_content, new_content)

                if not validation_result["valid"]:
                    self.stats["failed_patches"] += 1
                    return {"success": False, "error": f"Validation failed: {validation_result['reason']}"}

            # バックアップ作成
            backup_path = await self._create_backup(file_path, old_content)
            logger.info(f"💾 バックアップ作成: {backup_path}")

            # 戦略に応じてパッチ適用
            if strategy == PatchStrategy.REPLACE:
                apply_result = await self._apply_replace(file_path_obj, new_content)

            elif strategy == PatchStrategy.DIFF:
                apply_result = await self._apply_diff(file_path_obj, old_content, new_content)

            elif strategy == PatchStrategy.MERGE:
                apply_result = await self._apply_merge(file_path_obj, old_content, new_content)

            elif strategy == PatchStrategy.SAFE_INSERT:
                apply_result = await self._apply_safe_insert(file_path_obj, old_content, new_content)

            else:
                self.stats["failed_patches"] += 1
                return {"success": False, "error": f"Unsupported strategy: {strategy}"}

            if apply_result["success"]:
                self.stats["successful_patches"] += 1

                # 差分情報を生成
                diff = self._generate_diff(old_content, new_content)

                # 履歴に追加
                self.patch_history.append(
                    {
                        "file_path": file_path,
                        "timestamp": datetime.now().isoformat(),
                        "strategy": strategy.value,
                        "backup_path": str(backup_path),
                        "success": True,
                    }
                )

                execution_time = (datetime.now() - start_time).total_seconds()

                logger.info(f"✅ パッチ適用成功: {file_path} ({execution_time:.2f}秒)")

                return {
                    "success": True,
                    "changed": True,
                    "backup_path": str(backup_path),
                    "diff": diff,
                    "execution_time": execution_time,
                }

            else:
                self.stats["failed_patches"] += 1

                # ロールバック
                await self._rollback_from_backup(file_path, backup_path)

                return apply_result

        except Exception as e:
            logger.error(f"💥 パッチ適用エラー: {e}", exc_info=True)
            self.stats["failed_patches"] += 1

            return {"success": False, "error": str(e)}

    async def rollback(self, file_path: str, backup_path: Optional[str] = None) -> Dict[str, Any]:
        """
        パッチをロールバック

        Args:
            file_path: 対象ファイル
            backup_path: バックアップパス（省略時は最新）

        Returns:
            Dict: ロールバック結果
        """
        try:
            logger.info(f"♻️ ロールバック開始: {file_path}")

            if not backup_path:
                # 最新のバックアップを検索
                backup_path = await self._find_latest_backup(file_path)

            if not backup_path:
                return {"success": False, "error": "No backup found"}

            backup_path_obj = Path(backup_path)

            if not backup_path_obj.exists():
                return {"success": False, "error": f"Backup not found: {backup_path}"}

            # バックアップから復元
            result = await self._rollback_from_backup(file_path, backup_path_obj)

            if result["success"]:
                self.stats["rollbacks"] += 1
                logger.info(f"✅ ロールバック成功: {file_path}")

            return result

        except Exception as e:
            logger.error(f"💥 ロールバックエラー: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    # ========================================
    # パッチ適用戦略
    # ========================================

    async def _apply_replace(self, file_path: Path, new_content: str) -> Dict[str, Any]:
        """ファイル全体を置換"""
        try:
            await asyncio.to_thread(file_path.write_text, new_content, encoding="utf-8")

            return {"success": True}

        except Exception as e:
            logger.error(f"❌ 置換エラー: {e}")
            return {"success": False, "error": str(e)}

    async def _apply_diff(self, file_path: Path, old_content: str, new_content: str) -> Dict[str, Any]:
        """差分パッチを適用"""
        try:
            # unified diffを生成
            diff = list(
                difflib.unified_diff(
                    old_content.splitlines(keepends=True),
                    new_content.splitlines(keepends=True),
                    fromfile=str(file_path),
                    tofile=str(file_path),
                )
            )

            if not diff:
                return {"success": True, "message": "No differences"}

            # 新しい内容を適用（実際にはunified diffの適用ロジックが必要）
            # 簡易版として全置換
            await asyncio.to_thread(file_path.write_text, new_content, encoding="utf-8")

            return {"success": True, "diff_lines": len(diff)}

        except Exception as e:
            logger.error(f"❌ 差分適用エラー: {e}")
            return {"success": False, "error": str(e)}

    async def _apply_merge(self, file_path: Path, old_content: str, new_content: str) -> Dict[str, Any]:
        """マージ適用（3-way merge的な処理）"""
        try:
            # 簡易版: 行単位でマージ
            old_lines = old_content.splitlines()
            new_lines = new_content.splitlines()

            merged_lines = []

            # SequenceMatcherでマッチング
            matcher = difflib.SequenceMatcher(None, old_lines, new_lines)

            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == "equal":
                    merged_lines.extend(old_lines[i1:i2])
                elif tag == "replace":
                    merged_lines.extend(new_lines[j1:j2])
                elif tag == "delete":
                    pass  # 削除
                elif tag == "insert":
                    merged_lines.extend(new_lines[j1:j2])

            merged_content = "\n".join(merged_lines)

            await asyncio.to_thread(file_path.write_text, merged_content, encoding="utf-8")

            return {"success": True}

        except Exception as e:
            logger.error(f"❌ マージエラー: {e}")
            return {"success": False, "error": str(e)}

    async def _apply_safe_insert(self, file_path: Path, old_content: str, new_content: str) -> Dict[str, Any]:
        """安全な挿入（既存コードを保護）"""
        try:
            # 既存の内容の終わりに追加
            combined_content = old_content + "\n\n# Auto-generated patch\n" + new_content

            await asyncio.to_thread(file_path.write_text, combined_content, encoding="utf-8")

            return {"success": True}

        except Exception as e:
            logger.error(f"❌ 安全挿入エラー: {e}")
            return {"success": False, "error": str(e)}

    # ========================================
    # 検証
    # ========================================

    async def _validate_patch(self, old_content: str, new_content: str) -> Dict[str, Any]:
        """パッチを検証"""
        try:
            # 基本的な構文チェック（Pythonの場合）
            try:
                compile(new_content, "<string>", "exec")
            except SyntaxError as e:
                return {"valid": False, "reason": f"Syntax error: {e}"}

            # サイズチェック
            size_diff = len(new_content) - len(old_content)
            if abs(size_diff) > len(old_content) * 2:  # 2倍以上の変更
                logger.warning(f"⚠️ 大幅なサイズ変更: {size_diff}文字")

            # インデントチェック
            if "\t" in new_content and "    " in new_content:
                logger.warning("⚠️ タブとスペースが混在しています")

            return {"valid": True}

        except Exception as e:
            logger.error(f"❌ 検証エラー: {e}")
            return {"valid": False, "reason": str(e)}

    # ========================================
    # バックアップ管理
    # ========================================

    async def _create_backup(self, file_path: str, content: str) -> Path:
        """バックアップを作成"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = Path(file_path).name

            # ハッシュを生成（ファイル識別用）
            content_hash = hashlib.md5(content.encode()).hexdigest()[:8]

            backup_filename = f"{file_name}_{timestamp}_{content_hash}.bak"
            backup_path = self.backup_dir / backup_filename

            await asyncio.to_thread(backup_path.write_text, content, encoding="utf-8")

            # 古いバックアップを削除
            await self._cleanup_old_backups(file_name)

            return backup_path

        except Exception as e:
            logger.error(f"❌ バックアップ作成エラー: {e}")
            raise

    async def _rollback_from_backup(self, file_path: str, backup_path: Path) -> Dict[str, Any]:
        """バックアップから復元"""
        try:
            content = await asyncio.to_thread(backup_path.read_text, encoding="utf-8")

            file_path_obj = Path(file_path)
            await asyncio.to_thread(file_path_obj.write_text, content, encoding="utf-8")

            logger.info(f"♻️ 復元成功: {file_path} ← {backup_path}")

            return {"success": True}

        except Exception as e:
            logger.error(f"❌ 復元エラー: {e}")
            return {"success": False, "error": str(e)}

    async def _find_latest_backup(self, file_path: str) -> Optional[str]:
        """最新のバックアップを検索"""
        try:
            file_name = Path(file_path).name

            # ファイル名でフィルタリング
            backups = list(self.backup_dir.glob(f"{file_name}_*.bak"))

            if not backups:
                return None

            # 最新のものを取得（タイムスタンプでソート）
            latest_backup = max(backups, key=lambda p: p.stat().st_mtime)

            return str(latest_backup)

        except Exception as e:
            logger.error(f"❌ バックアップ検索エラー: {e}")
            return None

    async def _cleanup_old_backups(self, file_name: str):
        """古いバックアップを削除"""
        try:
            backups = sorted(self.backup_dir.glob(f"{file_name}_*.bak"), key=lambda p: p.stat().st_mtime, reverse=True)

            # 上限を超えたバックアップを削除
            for backup in backups[self.max_backups :]:
                await asyncio.to_thread(backup.unlink)
                logger.debug(f"🗑️ 古いバックアップを削除: {backup}")

        except Exception as e:
            logger.warning(f"⚠️ バックアップクリーンアップエラー: {e}")

    async def _create_new_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """新しいファイルを作成"""
        try:
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)

            await asyncio.to_thread(file_path_obj.write_text, content, encoding="utf-8")

            logger.info(f"✅ 新規ファイル作成: {file_path}")

            self.stats["successful_patches"] += 1

            return {"success": True, "new_file": True}

        except Exception as e:
            logger.error(f"❌ ファイル作成エラー: {e}")
            self.stats["failed_patches"] += 1

            return {"success": False, "error": str(e)}

    # ========================================
    # ユーティリティ
    # ========================================

    def _generate_diff(self, old_content: str, new_content: str) -> str:
        """差分を生成"""
        diff = difflib.unified_diff(
            old_content.splitlines(keepends=True), new_content.splitlines(keepends=True), lineterm=""
        )

        return "".join(diff)

    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        success_rate = 0.0
        if self.stats["total_patches"] > 0:
            success_rate = self.stats["successful_patches"] / self.stats["total_patches"]

        return {**self.stats, "success_rate": success_rate}
