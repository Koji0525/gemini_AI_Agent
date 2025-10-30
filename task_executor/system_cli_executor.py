"""
system_cli_executor.py - システムCLIタスク専門実行モジュール
WP-CLI、ACF、ファイル操作などのシステムタスクを担当
"""

import asyncio
import subprocess
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

# 設定
from configuration.config_utils import ErrorHandler, config

# データ管理
from tools.sheets_manager import GoogleSheetsManager

# コマンド監視エージェント
try:
    from agents.command_monitor_agent import CommandMonitorAgent

    HAS_COMMAND_MONITOR = True
except ImportError:
    HAS_COMMAND_MONITOR = False
    CommandMonitorAgent = None

logger = logging.getLogger(__name__)


class SystemCLIExecutor:
    """
    システムCLIタスクの専門実行モジュール

    WP-CLI、ACFインポート、ファイル操作、
    インフラコマンド実行を統合管理
    """

    def __init__(self, sheets_manager: GoogleSheetsManager):
        """
        初期化

        Args:
            sheets_manager: GoogleSheetsManagerインスタンス
        """
        self.sheets_manager = sheets_manager

        # コマンド監視エージェント初期化
        if HAS_COMMAND_MONITOR and CommandMonitorAgent:
            try:
                self.command_monitor = CommandMonitorAgent()
                logger.info("✅ CommandMonitorAgent 初期化完了")
            except Exception as e:
                logger.warning(f"⚠️ CommandMonitorAgent 初期化失敗: {e}")
                self.command_monitor = None
        else:
            logger.info("ℹ️ CommandMonitorAgent は利用できません")
            self.command_monitor = None

        # タイムアウト設定
        self.default_timeout = 60.0
        self.long_timeout = 300.0

        # WP-CLI設定
        self.wp_cli_path = self._detect_wp_cli_path()

        logger.info("✅ SystemCLIExecutor 初期化完了")

    def _detect_wp_cli_path(self) -> str:
        """WP-CLIパスを検出"""
        candidates = ["wp", "/usr/local/bin/wp", "/usr/bin/wp", "./wp-cli.phar"]  # PATH内

        for candidate in candidates:
            try:
                result = subprocess.run([candidate, "--version"], capture_output=True, timeout=5)
                if result.returncode == 0:
                    logger.info(f"✅ WP-CLI検出: {candidate}")
                    return candidate
            except:
                continue

        logger.warning("⚠️ WP-CLI未検出 - 'wp'をデフォルト使用")
        return "wp"

    async def execute_cli_task(self, task: Dict) -> Dict:
        """
        CLIタスクを実行

        Args:
            task: タスク情報辞書

        Returns:
            Dict: 実行結果
        """
        task_id = task.get("task_id", "UNKNOWN")

        try:
            logger.info("=" * 60)
            logger.info(f"⚙️ CLIタスク実行開始: {task_id}")
            logger.info("=" * 60)

            # タスクタイプ判定
            cli_type = self._determine_cli_type(task)
            logger.info(f"CLIタイプ: {cli_type}")

            # タイプ別実行
            if cli_type == "wp-cli":
                result = await self._execute_wp_cli_task(task)
            elif cli_type == "acf":
                result = await self._execute_acf_task(task)
            elif cli_type == "file":
                result = await self._execute_file_operation_task(task)
            elif cli_type == "generic":
                result = await self._execute_generic_command_task(task)
            else:
                logger.warning(f"⚠️ 未知のCLIタイプ: {cli_type}")
                result = await self._execute_generic_command_task(task)

            if result.get("success"):
                logger.info(f"✅ CLIタスク {task_id} 完了")
            else:
                logger.error(f"❌ CLIタスク {task_id} 失敗")

            return result

        except Exception as e:
            logger.error(f"❌ CLIタスク {task_id} 実行エラー")
            ErrorHandler.log_error(e, f"SystemCLIExecutor.execute_cli_task({task_id})")
            return {"success": False, "error": str(e)}

    def _determine_cli_type(self, task: Dict) -> str:
        """
        CLIタスクのタイプを判定

        Args:
            task: タスク情報辞書

        Returns:
            str: タスクタイプ ('wp-cli', 'acf', 'file', 'generic')
        """
        description = task.get("description", "").lower()
        command = task.get("command", "").lower()

        # WP-CLIキーワード
        if any(kw in description or kw in command for kw in ["wp ", "wp-cli", "wordpress cli"]):
            return "wp-cli"

        # ACFキーワード
        if any(kw in description or kw in command for kw in ["acf", "advanced custom fields", "acf-json"]):
            return "acf"

        # ファイル操作キーワード
        if any(kw in description for kw in ["ファイル", "コピー", "移動", "削除", "mkdir", "cp", "mv", "rm"]):
            return "file"

        return "generic"

    async def _execute_wp_cli_task(self, task: Dict) -> Dict:
        """
        WP-CLIコマンドを実行

        Args:
            task: タスク情報辞書

        Returns:
            Dict: 実行結果
        """
        try:
            logger.info("🌐 WP-CLIコマンド実行")

            # コマンド構築
            command = task.get("command", "")
            if not command:
                # タスク説明からコマンド抽出を試行
                description = task.get("description", "")
                if "wp " in description:
                    command = description[description.find("wp ") :]
                else:
                    return {"success": False, "error": "WP-CLIコマンドが指定されていません"}

            # WP-CLIパス付加
            if not command.startswith(self.wp_cli_path):
                command = f"{self.wp_cli_path} {command}"

            # 作業ディレクトリ
            wp_path = task.get("wp_path", config.WP_PATH if hasattr(config, "WP_PATH") else None)

            # コマンド監視エージェント使用
            if self.command_monitor:
                result = await self.command_monitor.execute_command(command, cwd=wp_path, timeout=self.default_timeout)
            else:
                # 直接実行（フォールバック）
                result = await self._direct_command_execution(command, cwd=wp_path, timeout=self.default_timeout)

            return result

        except Exception as e:
            logger.error(f"❌ WP-CLI実行エラー: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_acf_task(self, task: Dict) -> Dict:
        """
        ACF関連タスクを実行

        Args:
            task: タスク情報辞書

        Returns:
            Dict: 実行結果
        """
        try:
            logger.info("📦 ACFタスク実行")

            # ACF操作タイプ判定
            description = task.get("description", "").lower()

            if "インポート" in description or "import" in description:
                # ACFインポート
                acf_file = task.get("acf_file", task.get("file_path", ""))

                if not acf_file:
                    return {"success": False, "error": "ACFファイルパスが指定されていません"}

                if self.command_monitor and hasattr(self.command_monitor, "monitor_acf_import_process"):
                    result = await self.command_monitor.monitor_acf_import_process(acf_file)
                else:
                    # WP-CLI経由でインポート
                    command = f"{self.wp_cli_path} acf import {acf_file}"
                    result = await self._direct_command_execution(command, timeout=self.long_timeout)

                return result

            elif "エクスポート" in description or "export" in description:
                # ACFエクスポート
                output_path = task.get("output_path", "./acf-export.json")
                command = f"{self.wp_cli_path} acf export --path={output_path}"

                result = await self._direct_command_execution(command, timeout=self.default_timeout)

                return result

            else:
                return {"success": False, "error": "ACF操作タイプが不明です"}

        except Exception as e:
            logger.error(f"❌ ACFタスク実行エラー: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_file_operation_task(self, task: Dict) -> Dict:
        """
        ファイル操作タスクを実行

        Args:
            task: タスク情報辞書

        Returns:
            Dict: 実行結果
        """
        try:
            logger.info("📁 ファイル操作タスク実行")

            description = task.get("description", "").lower()

            # 操作タイプ判定
            if "コピー" in description or "copy" in description:
                return await self._file_copy(task)
            elif "移動" in description or "move" in description:
                return await self._file_move(task)
            elif "削除" in description or "delete" in description:
                return await self._file_delete(task)
            elif "ディレクトリ作成" in description or "mkdir" in description:
                return await self._directory_create(task)
            else:
                return {"success": False, "error": "ファイル操作タイプが不明です"}

        except Exception as e:
            logger.error(f"❌ ファイル操作エラー: {e}")
            return {"success": False, "error": str(e)}

    async def _file_copy(self, task: Dict) -> Dict:
        """ファイルコピー"""
        import shutil

        source = task.get("source", task.get("source_path", ""))
        dest = task.get("destination", task.get("dest_path", ""))

        if not source or not dest:
            return {"success": False, "error": "コピー元またはコピー先が指定されていません"}

        try:
            shutil.copy2(source, dest)
            logger.info(f"✅ ファイルコピー成功: {source} -> {dest}")
            return {"success": True, "message": f"コピー完了: {source} -> {dest}"}
        except Exception as e:
            return {"success": False, "error": f"コピー失敗: {e}"}

    async def _file_move(self, task: Dict) -> Dict:
        """ファイル移動"""
        import shutil

        source = task.get("source", task.get("source_path", ""))
        dest = task.get("destination", task.get("dest_path", ""))

        if not source or not dest:
            return {"success": False, "error": "移動元または移動先が指定されていません"}

        try:
            shutil.move(source, dest)
            logger.info(f"✅ ファイル移動成功: {source} -> {dest}")
            return {"success": True, "message": f"移動完了: {source} -> {dest}"}
        except Exception as e:
            return {"success": False, "error": f"移動失敗: {e}"}

    async def _file_delete(self, task: Dict) -> Dict:
        """ファイル削除"""
        target = task.get("target", task.get("file_path", ""))

        if not target:
            return {"success": False, "error": "削除対象が指定されていません"}

        try:
            path = Path(target)
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                import shutil

                shutil.rmtree(path)
            else:
                return {"success": False, "error": f"ファイルまたはディレクトリが見つかりません: {target}"}

            logger.info(f"✅ 削除成功: {target}")
            return {"success": True, "message": f"削除完了: {target}"}
        except Exception as e:
            return {"success": False, "error": f"削除失敗: {e}"}

    async def _directory_create(self, task: Dict) -> Dict:
        """ディレクトリ作成"""
        dir_path = task.get("directory", task.get("path", ""))

        if not dir_path:
            return {"success": False, "error": "ディレクトリパスが指定されていません"}

        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ ディレクトリ作成成功: {dir_path}")
            return {"success": True, "message": f"作成完了: {dir_path}"}
        except Exception as e:
            return {"success": False, "error": f"作成失敗: {e}"}

    async def _execute_generic_command_task(self, task: Dict) -> Dict:
        """
        汎用コマンドタスクを実行

        Args:
            task: タスク情報辞書

        Returns:
            Dict: 実行結果
        """
        try:
            logger.info("🔧 汎用コマンド実行")

            command = task.get("command", "")
            if not command:
                return {"success": False, "error": "コマンドが指定されていません"}

            timeout = task.get("timeout", self.default_timeout)
            cwd = task.get("cwd", None)

            # コマンド監視エージェント使用
            if self.command_monitor:
                result = await self.command_monitor.execute_command(command, cwd=cwd, timeout=timeout)
            else:
                result = await self._direct_command_execution(command, cwd=cwd, timeout=timeout)

            return result

        except Exception as e:
            logger.error(f"❌ 汎用コマンド実行エラー: {e}")
            return {"success": False, "error": str(e)}

    async def _direct_command_execution(self, command: str, cwd: Optional[str] = None, timeout: float = 60.0) -> Dict:
        """
        コマンドを直接実行（フォールバック）

        Args:
            command: 実行するコマンド
            cwd: 作業ディレクトリ
            timeout: タイムアウト時間（秒）

        Returns:
            Dict: 実行結果
        """
        try:
            logger.info(f"🔧 コマンド直接実行: {command}")

            process = await asyncio.create_subprocess_shell(
                command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=cwd
            )

            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            except asyncio.TimeoutError:
                process.kill()
                return {"success": False, "error": f"タイムアウト ({timeout}秒)"}

            returncode = process.returncode
            stdout_text = stdout.decode("utf-8") if stdout else ""
            stderr_text = stderr.decode("utf-8") if stderr else ""

            if returncode == 0:
                logger.info(f"✅ コマンド実行成功")
                return {"success": True, "stdout": stdout_text, "stderr": stderr_text, "returncode": returncode}
            else:
                logger.error(f"❌ コマンド実行失敗 (コード: {returncode})")
                return {
                    "success": False,
                    "error": f"コマンド失敗 (コード: {returncode})",
                    "stdout": stdout_text,
                    "stderr": stderr_text,
                    "returncode": returncode,
                }

        except Exception as e:
            logger.error(f"❌ コマンド直接実行エラー: {e}")
            return {"success": False, "error": str(e)}
