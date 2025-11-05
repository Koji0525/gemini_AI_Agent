"""
error_handler_enhanced.py - 自律修正システム用エラーハンドラ
スタックトレース捕捉、構造化、バグ修正タスク生成機能を提供
"""

import logging
import traceback
import sys
import inspect
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# データモデル定義
class ErrorSeverity(Enum):
    """エラーの深刻度"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """エラーカテゴリ"""

    SYNTAX = "syntax"
    IMPORT = "import"
    RUNTIME = "runtime"
    LOGIC = "logic"
    DESIGN = "design"
    PERFORMANCE = "performance"
    SECURITY = "security"
    UNKNOWN = "unknown"


@dataclass
class CodeLocation:
    """コード位置情報"""

    file_path: str
    line_number: int
    function_name: Optional[str] = None
    class_name: Optional[str] = None


@dataclass
class StackTraceFrame:
    """スタックトレースフレーム"""

    file_path: str
    line_number: int
    function_name: str
    code_context: Optional[str] = None
    local_variables: Optional[Dict[str, Any]] = None


@dataclass
class ErrorContextModel:
    """エラーコンテキストモデル"""

    error_id: str
    timestamp: datetime
    task_id: str
    agent_name: Optional[str] = None
    error_type: str = "UnknownError"
    error_message: Optional[str] = None
    full_traceback: Optional[str] = None
    stack_frames: List[StackTraceFrame] = field(default_factory=list)
    error_location: Optional[CodeLocation] = None
    problematic_code: Optional[str] = None
    surrounding_code: Optional[str] = None
    local_variables: Dict[str, Any] = field(default_factory=dict)
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    task_description: Optional[str] = None
    task_parameters: Optional[Dict[str, Any]] = None


@dataclass
class BugFixTask:
    """バグ修正タスク"""

    task_id: str
    original_task_id: str
    error_context: ErrorContextModel
    priority: str = "medium"
    required_role: str = "quick_fix"
    target_files: List[str] = field(default_factory=list)
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    assigned_agent: Optional[str] = None


class EnhancedErrorHandler:
    """
    強化版エラーハンドラ - 自律修正システム用

    機能:
    1. エラー情報の詳細な捕捉
    2. スタックトレースの構造化
    3. エラーコンテキストの構築
    4. バグ修正タスクの自動生成
    """

    def __init__(self):
        """初期化"""
        # メモリバッファ(最新100件のエラーを保持)
        self.error_buffer: List[ErrorContextModel] = []
        self.max_buffer_size = 100

        # エラーカウンタ
        self.error_counter = 0

        logger.info("✅ EnhancedErrorHandler 初期化完了")

    def capture_error(
        self,
        exception: Exception,
        task_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        task_context: Optional[Dict[str, Any]] = None,
    ) -> ErrorContextModel:
        """
        エラーを捕捉して構造化されたコンテキストを生成

        Args:
            exception: 捕捉された例外
            task_id: 実行中のタスクID
            agent_name: 実行中のエージェント名
            task_context: タスクコンテキスト情報

        Returns:
            ErrorContextModel: 構造化されたエラーコンテキスト
        """
        try:
            # エラーIDを生成
            self.error_counter += 1
            error_id = f"ERROR_{task_id or 'UNKNOWN'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.error_counter}"

            # エラー型とメッセージ
            error_type = type(exception).__name__
            error_message = str(exception)

            # スタックトレースの取得
            exc_type, exc_value, exc_tb = sys.exc_info()
            full_traceback = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))

            # スタックフレームの構造化
            stack_frames = self._extract_stack_frames(exc_tb) if exc_tb else []

            # エラー発生位置の特定
            error_location = self._extract_error_location(exc_tb) if exc_tb else None

            # 問題のあるコードスニペットを取得
            problematic_code, surrounding_code = self._extract_code_snippets(
                error_location.file_path if error_location else None,
                error_location.line_number if error_location else None,
            )

            # ローカル変数の取得
            local_vars = self._extract_local_variables(exc_tb) if exc_tb else {}

            # 深刻度を判定
            severity = self._determine_severity(error_type, error_message)

            # ErrorContextModelを構築
            error_context = ErrorContextModel(
                error_id=error_id,
                timestamp=datetime.now(),
                task_id=task_id or "UNKNOWN",
                agent_name=agent_name,
                error_type=error_type,
                error_message=error_message,
                full_traceback=full_traceback,
                stack_frames=stack_frames,
                error_location=error_location,
                problematic_code=problematic_code,
                surrounding_code=surrounding_code,
                local_variables=local_vars,
                severity=severity,
                task_description=task_context.get("description") if task_context else None,
                task_parameters=task_context.get("parameters") if task_context else None,
            )

            # バッファに追加
            self._add_to_buffer(error_context)

            # ログ出力
            logger.error(f"❌ エラー捕捉: {error_id}")
            logger.error(f"   タイプ: {error_type}")
            logger.error(f"   メッセージ: {error_message}")
            logger.error(f"   深刻度: {severity.value}")

            if error_location:
                logger.error(f"   場所: {error_location.file_path}:{error_location.line_number}")

            return error_context

        except Exception as e:
            logger.error(f"💥 エラー捕捉中にエラー: {e}")
            # フォールバック: 最小限のエラーコンテキスト
            return self._create_minimal_error_context(exception, task_id, agent_name)

    def _extract_stack_frames(self, traceback_obj) -> List[StackTraceFrame]:
        """スタックトレースからフレーム情報を抽出"""
        frames = []

        try:
            tb_list = traceback.extract_tb(traceback_obj)

            for frame_summary in tb_list:
                # コード文脈を取得(前後1行)
                code_context = self._get_code_context(
                    frame_summary.filename, frame_summary.lineno, context_lines=1
                )

                frame = StackTraceFrame(
                    file_path=frame_summary.filename,
                    line_number=frame_summary.lineno,
                    function_name=frame_summary.name,
                    code_context=code_context,
                )
                frames.append(frame)

        except Exception as e:
            logger.warning(f"⚠️ スタックフレーム抽出エラー: {e}")

        return frames

    def _extract_error_location(self, traceback_obj) -> Optional[CodeLocation]:
        """エラー発生位置を抽出"""
        try:
            tb_list = traceback.extract_tb(traceback_obj)

            if not tb_list:
                return None

            # 最後のフレーム(エラー発生箇所)を取得
            last_frame = tb_list[-1]

            return CodeLocation(
                file_path=last_frame.filename,
                line_number=last_frame.lineno,
                function_name=last_frame.name,
            )

        except Exception as e:
            logger.warning(f"⚠️ エラー位置抽出エラー: {e}")
            return None

    def _extract_code_snippets(
        self, file_path: Optional[str], line_number: Optional[int]
    ) -> Tuple[Optional[str], Optional[str]]:
        """問題のあるコードと周辺コードを抽出"""
        if not file_path or not line_number:
            return None, None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # 問題のある行(1行)
            if 1 <= line_number <= len(lines):
                problematic_code = lines[line_number - 1].rstrip()
            else:
                problematic_code = None

            # 周辺コード(前後10行)
            start_line = max(0, line_number - 11)
            end_line = min(len(lines), line_number + 10)
            surrounding_lines = lines[start_line:end_line]

            # 行番号付きで整形
            surrounding_code = "\n".join(
                [
                    f"{start_line + i + 1:4d} | {line.rstrip()}"
                    for i, line in enumerate(surrounding_lines)
                ]
            )

            return problematic_code, surrounding_code

        except Exception as e:
            logger.warning(f"⚠️ コードスニペット抽出エラー: {e}")
            return None, None

    def _get_code_context(
        self, file_path: str, line_number: int, context_lines: int = 1
    ) -> Optional[str]:
        """指定行の前後のコードコンテキストを取得"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            start = max(0, line_number - context_lines - 1)
            end = min(len(lines), line_number + context_lines)

            context = "".join(lines[start:end])
            return context.strip()

        except:
            return None

    def _extract_local_variables(self, traceback_obj) -> Dict[str, Any]:
        """ローカル変数の状態を抽出(安全に)"""
        local_vars = {}

        try:
            frame = traceback_obj.tb_frame

            for var_name, var_value in frame.f_locals.items():
                try:
                    # シリアライズ可能な値のみ保存
                    if isinstance(var_value, (str, int, float, bool, type(None))):
                        local_vars[var_name] = var_value
                    elif isinstance(var_value, (list, tuple, dict)):
                        # 複雑な構造は文字列表現に変換
                        local_vars[var_name] = str(var_value)[:200]  # 最大200文字
                    else:
                        local_vars[var_name] = f"<{type(var_value).__name__} object>"
                except:
                    local_vars[var_name] = "<unprintable>"

        except Exception as e:
            logger.warning(f"⚠️ ローカル変数抽出エラー: {e}")

        return local_vars

    def _determine_severity(self, error_type: str, error_message: str) -> ErrorSeverity:
        """エラーの深刻度を判定"""
        error_lower = (error_type + error_message).lower()

        # CRITICAL: システム停止レベル
        if any(
            kw in error_lower
            for kw in [
                "systemerror",
                "memoryerror",
                "recursionerror",
                "keyboardinterrupt",
                "syntaxerror",
            ]
        ):
            return ErrorSeverity.CRITICAL

        # HIGH: 機能不全
        if any(
            kw in error_lower
            for kw in ["attributeerror", "importerror", "modulenotfound", "typeerror", "valueerror"]
        ):
            return ErrorSeverity.HIGH

        # MEDIUM: 部分的な問題
        if any(kw in error_lower for kw in ["keyerror", "indexerror", "filenotfounderror"]):
            return ErrorSeverity.MEDIUM

        # LOW: 軽微な問題
        return ErrorSeverity.LOW

    def _add_to_buffer(self, error_context: ErrorContextModel):
        """エラーコンテキストをバッファに追加"""
        self.error_buffer.append(error_context)

        # バッファサイズ制限
        if len(self.error_buffer) > self.max_buffer_size:
            self.error_buffer.pop(0)  # 最古のエラーを削除

    def _create_minimal_error_context(
        self, exception: Exception, task_id: Optional[str], agent_name: Optional[str]
    ) -> ErrorContextModel:
        """最小限のエラーコンテキストを作成(フォールバック)"""
        return ErrorContextModel(
            error_id=f"ERROR_MINIMAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            task_id=task_id or "UNKNOWN",
            agent_name=agent_name,
            error_type=type(exception).__name__,
            error_message=str(exception),
            full_traceback=traceback.format_exc(),
            severity=ErrorSeverity.MEDIUM,
        )

    def get_recent_errors(self, count: int = 10) -> List[ErrorContextModel]:
        """最近のエラーを取得"""
        return self.error_buffer[-count:]

    def get_error_by_id(self, error_id: str) -> Optional[ErrorContextModel]:
        """IDでエラーを検索"""
        for error in reversed(self.error_buffer):
            if error.error_id == error_id:
                return error
        return None

    def clear_buffer(self):
        """バッファをクリア"""
        self.error_buffer.clear()
        logger.info("🧹 エラーバッファをクリアしました")


class TaskErrorHandler:
    """
    タスク実行用エラーハンドラ - バグ修正タスク生成機能付き
    """

    def __init__(self, error_handler: EnhancedErrorHandler):
        """
        初期化

        Args:
            error_handler: EnhancedErrorHandlerインスタンス
        """
        self.error_handler = error_handler
        self.bug_fix_tasks: List[BugFixTask] = []

        logger.info("✅ TaskErrorHandler 初期化完了")

    def handle_task_error(
        self,
        exception: Exception,
        task: Dict[str, Any],
        agent_name: Optional[str] = None,
        auto_generate_fix_task: bool = True,
    ) -> Optional[BugFixTask]:
        """
        タスク実行エラーを処理し、必要に応じてバグ修正タスクを生成

        Args:
            exception: 捕捉された例外
            task: 失敗したタスク情報
            agent_name: エージェント名
            auto_generate_fix_task: バグ修正タスク自動生成フラグ

        Returns:
            BugFixTask: 生成されたバグ修正タスク(生成しない場合はNone)
        """
        try:
            task_id = task.get("task_id", "UNKNOWN")

            # エラーコンテキストを捕捉
            error_context = self.error_handler.capture_error(
                exception=exception, task_id=task_id, agent_name=agent_name, task_context=task
            )

            # 自動修正が不要な場合は終了
            if not auto_generate_fix_task:
                return None

            # 致命的なエラーのみバグ修正タスクを生成
            if error_context.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
                bug_fix_task = self._generate_bug_fix_task(error_context, task)
                self.bug_fix_tasks.append(bug_fix_task)

                logger.info(f"🔧 バグ修正タスク生成: {bug_fix_task.task_id}")
                return bug_fix_task

            return None

        except Exception as e:
            logger.error(f"💥 タスクエラーハンドリング中にエラー: {e}")
            return None

    def _generate_bug_fix_task(
        self, error_context: ErrorContextModel, original_task: Dict[str, Any]
    ) -> BugFixTask:
        """バグ修正タスクを生成"""

        # バグ修正タスクIDを生成
        fix_task_id = f"FIX_BUG_{error_context.task_id}_{datetime.now().strftime('%H%M%S')}"

        # 修正対象ファイルを特定
        target_files = []
        if error_context.error_location:
            target_files.append(error_context.error_location.file_path)

        bug_fix_task = BugFixTask(
            task_id=fix_task_id,
            original_task_id=error_context.task_id,
            error_context=error_context,
            priority="critical" if error_context.severity == ErrorSeverity.CRITICAL else "high",
            required_role="quick_fix",
            target_files=target_files,
            status="pending",
        )

        return bug_fix_task

    def get_pending_fix_tasks(self) -> List[BugFixTask]:
        """未処理のバグ修正タスクを取得"""
        return [task for task in self.bug_fix_tasks if task.status == "pending"]

    def get_all_fix_tasks(self) -> List[BugFixTask]:
        """全バグ修正タスクを取得"""
        return self.bug_fix_tasks.copy()


# 使用例
if __name__ == "__main__":
    # テスト用のエラーハンドラ
    error_handler = EnhancedErrorHandler()
    task_handler = TaskErrorHandler(error_handler)

    # テスト用の例外
    try:
        # 意図的にエラーを発生
        result = 1 / 0
    except Exception as e:
        # エラーを捕捉
        error_context = error_handler.capture_error(
            exception=e,
            task_id="TEST_TASK_001",
            agent_name="TestAgent",
            task_context={"description": "テストタスク", "parameters": {"param1": "value1"}},
        )

        print(f"捕捉されたエラー: {error_context.error_type}")
        print(f"エラーメッセージ: {error_context.error_message}")
        print(f"深刻度: {error_context.severity.value}")

        # バグ修正タスク生成
        bug_task = task_handler.handle_task_error(
            exception=e,
            task={"task_id": "TEST_TASK_001", "description": "テストタスク"},
            agent_name="TestAgent",
        )

        if bug_task:
            print(f"生成された修正タスク: {bug_task.task_id}")
