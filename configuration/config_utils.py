import logging
import uuid
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import time

# config_utils.py の SmartLogFormatter クラスを修正


class SmartLogFormatter(logging.Formatter):
    """スマートなログフォーマッタ - 短縮識別版"""

    # クラス変数として状態を保持
    _message_count = 0
    _last_timestamp_display = 0
    _last_date_display = ""
    _lock = False

    # エージェント別の絵文字マッピング（短縮版）
    AGENT_EMOJIS = {
        # 🏃‍♂️ 実行系
        "run_multi_agent": "🚀 multi-agent",
        "__main__": "🏁 main",
        # 👑 PM系
        "pm_agent": "👑 pm-agent",
        "pm_system_prompts": "📋 pm-prompts",
        # ⚙️ タスク実行系
        "task_executor": "⚙️ task-exec",
        "task_executor_content": "📝 task-content",
        "task_executor_ma": "🔍 task-ma",
        "task_coordinator": "🎯 task-coord",
        "content_task_executor": "📄 content-exec",
        "system_cli_executor": "💻 cli-exec",
        "workflow_executor": "🔄 workflow",
        "test_tasks": "🧪 test-tasks",
        # 🎨 デザイン系
        "design_agent": "🎨 design",
        "ui_agent": "📱 ui",
        # 💻 開発系
        "dev_agent": "💻 dev",
        "dev_agent_acf": "🔌 dev-acf",
        # ✅ レビュー系
        "review_agent": "✅ review",
        "review_agent_prompts": "📋 review-prompts",
        "review_agent_prompts_ACF": "🔧 review-acf",
        # 🕷️ ブラウザ制御系
        "browser_controller": "🕷️ browser",
        "browser_cookie_and_session": "🍪 cookie-session",
        "browser_lifecycle": "🔁 browser-life",
        "browser_ai_chat_agent": "🤖 browser-ai",
        "browser_wp_session_manager": "🌐 wp-session",
        # 📊 データ連携系
        "sheets_manager": "📊 sheets-mgr",
        # 🔧 ユーティリティ系
        "config_utils": "⚙️ config",
        "command_monitor_agent": "👁️ monitor",
        "compatibility_fix": "🔧 compat-fix",
        "quick_fix": "⚡ quick-fix",
        "error_handler_enhanced": "🚨 error-handler",
        # ✍️ コンテンツライター系
        "base_writer": "✍️ writer-base",
        "ja_writer_agent": "🗾 ja-writer",
        "en_writer_agent": "🔠 en-writer",
        "ru_writer_agent": "🇷🇺 ru-writer",
        "uz_writer_agent": "🇺🇿 uz-writer",
        "zh_writer_agent": "🇨🇳 zh-writer",
        "ko_writer_agent": "🇰🇷 ko-writer",
        "tr_writer_agent": "🇹🇷 tr-writer",
        # 🆕 M&A専門エージェント
        "ma_executor": "💼 ma-exec",
        "ma_requirements": "📋 ma-req",
        "ma_data_migration": "🔄 ma-migrate",
        "ma_api_integration": "🔗 ma-api",
        # 🌐 WordPress系
        "wp_agent": "🌐 wp-agent",
        "wp_auth": "🔐 wp-auth",
        "wp_post_editor": "📝 wp-editor",
        "wp_post_creator": "🆕 wp-creator",
        "wp_plugin_manager": "🔌 wp-plugin",
        "wp_settings_manager": "⚙️ wp-config",
        "wp_design": "🎨 wp-design",
        "wp_dev": "🔧 wp-dev",
        "wp_tester": "🧪 wp-test",
        "wp_utils": "🛠️ wp-utils",
    }

    def format(self, record):
        # 再帰呼び出し防止
        if SmartLogFormatter._lock:
            return super().format(record)

        SmartLogFormatter._lock = True
        try:
            # メッセージカウント
            SmartLogFormatter._message_count += 1
            current_time = time.time()

            # エージェント識別
            agent_name = record.name
            # モジュール名から短縮名を取得
            if "." in agent_name:
                agent_short = agent_name.split(".")[-1]  # 最後の部分
            else:
                agent_short = agent_name

            # エージェント絵文字を取得
            agent_display = self.AGENT_EMOJIS.get(agent_short, f"📋 {agent_short[:6]}")

            # レベル別の絵文字と色（エラーを強調）
            level_info = {
                "INFO": ("💬", ""),
                "WARNING": ("⚠️", "WARN"),
                "ERROR": ("❌", "ERROR"),
                "DEBUG": ("🐛", "DEBUG"),
                "CRITICAL": ("💥", "CRITICAL"),
            }

            level_emoji, level_prefix = level_info.get(record.levelname, ("📝", ""))

            # メッセージ
            message = record.getMessage()

            # タイムスタンプ判定
            current_date = time.strftime("%Y-%m-%d")
            show_date = SmartLogFormatter._last_date_display != current_date
            show_timestamp = (
                SmartLogFormatter._message_count % 50 == 1
                or current_time - SmartLogFormatter._last_timestamp_display > 600
                or show_date
            )

            # フォーマット構築
            parts = []

            # タイムスタンプ
            if show_date:
                SmartLogFormatter._last_date_display = current_date
                SmartLogFormatter._last_timestamp_display = current_time
                timestamp = time.strftime("%Y-%m-%d %H:%M")
                parts.append(f"🕒 {timestamp}")
            elif show_timestamp:
                SmartLogFormatter._last_timestamp_display = current_time
                timestamp = time.strftime("%H:%M")
                parts.append(f"🕒 {timestamp}")

            # エージェント名（常に表示）
            parts.append(agent_display)

            # レベル（エラー/警告時は強調）
            if level_prefix:
                # エラーレベルの場合は赤色で表示（ターミナルで色付け）
                if record.levelname in ["ERROR", "CRITICAL"]:
                    parts.append(f"{level_emoji} \033[91m{level_prefix}\033[0m")  # 赤色
                elif record.levelname == "WARNING":
                    parts.append(f"{level_emoji} \033[93m{level_prefix}\033[0m")  # 黄色
                else:
                    parts.append(f"{level_emoji} {level_prefix}")
            else:
                parts.append(level_emoji)

            # メッセージ
            parts.append(message)

            # 結合
            result = " ".join(parts)

            return result

        finally:
            SmartLogFormatter._lock = False


def setup_optimized_logging(logger_name=None):
    """最適化されたログ設定（エージェント識別強化版）"""

    # ルートロガー
    logger = logging.getLogger(logger_name) if logger_name else logging.getLogger()
    logger.setLevel(logging.INFO)  # ← INFO を DEBUG に変更

    # 既存のハンドラをクリア
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # コンソールハンドラ（エージェント識別強化）
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(SmartLogFormatter())

    # ファイルハンドラ（詳細ログ）
    file_handler = logging.FileHandler("gemini_automation.log", encoding="utf-8")
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)

    # ハンドラ追加
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


# グローバルで実行
setup_optimized_logging()


class Config:
    """設定クラス"""

    SPREADSHEET_ID = "1qpMLT9HKlPT9qY17fpqOkSIbehKH77wZ8bA1yfPSO_s"
    DOWNLOAD_IMAGE_FOLDER: Optional[str] = None
    DOWNLOAD_TEXT_FOLDER: Optional[str] = None
    SERVICE_ACCOUNT_FILE: Optional[str] = None
    COOKIES_FILE: Optional[str] = None
    BROWSER_DATA_DIR: Optional[str] = None
    GENERATION_MODE: Optional[str] = None
    TEXT_FORMAT: Optional[str] = None
    SERVICE_TYPE: Optional[str] = None
    AGENT_OUTPUT_FOLDER = None
    MAX_ITERATIONS = 3
    DRIVE_TEXT_FOLDER_ID = "16QVK_-z8JVmhLQuLVprOx9_DnoNc4eUc"
    DRIVE_IMAGE_FOLDER_ID = "1jkuMH1UNeBvNNvrz8iVidyVMmtmYrHiS"

    BROWSER_CONFIG = {
        "headless": False,
        "slow_mo": 800,
        "args": [
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            # ⚠️ --single-process を削除（Windowsで不安定なため）
        ],
        "timeout": 60000,
    }

    def __init__(self):
        self.WP_COOKIES_FILE = os.environ.get(
            "WP_COOKIES_FILE", os.path.join(Path.home(), "Documents", "gemini_auto_generate", "wordpress_cookies.json")
        )

        # クッキー有効期限（デフォルト30日）
        self.WP_COOKIE_EXPIRY_DAYS = int(os.environ.get("WP_COOKIE_EXPIRY_DAYS", "30"))

    VIEWPORT_SIZE = {"width": 1024, "height": 768}
    PAGE_TIMEOUT = 60000
    IMAGE_GENERATION_TIMEOUT = 180
    TEXT_GENERATION_TIMEOUT = 120

    GOOGLE_SHEETS_SCOPE = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive.readonly",
    ]


class FileNameGenerator:
    """ファイル名生成"""

    @staticmethod
    def generate_unique_filename(index: int, extension: str = ".png", mode: str = "image") -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]

        if mode == "text":
            prefix = "gemini_text"
            ext = ".txt"
        else:
            prefix = "gemini_image"
            ext = extension

        return f"{prefix}_{index:03d}_{timestamp}_{unique_id}{ext}"

    @staticmethod
    def validate_filename(filename: str) -> bool:
        try:
            invalid_chars = '<>:"/\\|?*'
            return not any(char in filename for char in invalid_chars)
        except:
            return False


class ErrorHandler:
    """エラーハンドリング"""

    @staticmethod
    def log_error(error: Exception, context: str = "") -> None:
        logger = logging.getLogger(__name__)
        logger.error(f"{context}: {str(error)}")

    @staticmethod
    def handle_missing_attribute_error(obj, attr_name: str, default_value=None):
        logger = logging.getLogger(__name__)
        if not hasattr(obj, attr_name):
            logger.warning(f"属性 '{attr_name}' が見つかりません。デフォルト値を使用")
            setattr(obj, attr_name, default_value)
        return getattr(obj, attr_name)


class PathManager:
    """パス管理"""

    @staticmethod
    def ensure_directory_exists(path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_safe_path(base_path: str) -> Path:
        path = Path(base_path)
        PathManager.ensure_directory_exists(path)
        return path


config = Config()
