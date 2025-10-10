"""
task_executor パッケージ初期化モジュール
タスク実行の専門モジュールを統合管理

ファイル名: task_executor/tas__init__.py
使用方法: from task_executor.tas__init__ import *
"""

# 既存モジュール（変更不要）
try:
    from .task_executor_content import ContentTaskExecutor as LegacyContentExecutor
    HAS_LEGACY_CONTENT = True
except ImportError:
    HAS_LEGACY_CONTENT = False
    LegacyContentExecutor = None

try:
    from .task_executor_ma import MATaskExecutor as LegacyMAExecutor
    HAS_LEGACY_MA = True
except ImportError:
    HAS_LEGACY_MA = False
    LegacyMAExecutor = None

# 新規モジュール
try:
    from .content_task_executor import ContentTaskExecutor
    HAS_CONTENT_EXECUTOR = True
except ImportError:
    HAS_CONTENT_EXECUTOR = False
    ContentTaskExecutor = None

try:
    from .system_cli_executor import SystemCLIExecutor
    HAS_CLI_EXECUTOR = True
except ImportError:
    HAS_CLI_EXECUTOR = False
    SystemCLIExecutor = None

try:
    from .task_coordinator import TaskCoordinator
    HAS_COORDINATOR = True
except ImportError:
    HAS_COORDINATOR = False
    TaskCoordinator = None

try:
    from .workflow_executor import WorkflowExecutor
    HAS_WORKFLOW_EXECUTOR = True
except ImportError:
    HAS_WORKFLOW_EXECUTOR = False
    WorkflowExecutor = None

# パッケージ情報
__version__ = '2.0.0'
__all__ = [
    # 既存
    'LegacyContentExecutor',
    'LegacyMAExecutor',
    # 新規
    'ContentTaskExecutor',
    'SystemCLIExecutor',
    'TaskCoordinator',
    'WorkflowExecutor',
    # フラグ
    'HAS_LEGACY_CONTENT',
    'HAS_LEGACY_MA',
    'HAS_CONTENT_EXECUTOR',
    'HAS_CLI_EXECUTOR',
    'HAS_COORDINATOR',
    'HAS_WORKFLOW_EXECUTOR'
]

# 利用可能モジュールのログ出力
import logging
logger = logging.getLogger(__name__)

logger.info("=" * 60)
logger.info("📦 task_executor パッケージ初期化 (tas__init__)")
logger.info("=" * 60)

if HAS_LEGACY_CONTENT:
    logger.info("✅ 既存 task_executor_content 利用可能")
else:
    logger.info("⚠️ task_executor_content 未検出")

if HAS_LEGACY_MA:
    logger.info("✅ 既存 task_executor_ma 利用可能")
else:
    logger.info("⚠️ task_executor_ma 未検出")

if HAS_CONTENT_EXECUTOR:
    logger.info("✅ 新規 ContentTaskExecutor 利用可能")
else:
    logger.info("ℹ️ ContentTaskExecutor 未配置（オプション）")

if HAS_CLI_EXECUTOR:
    logger.info("✅ 新規 SystemCLIExecutor 利用可能")
else:
    logger.info("ℹ️ SystemCLIExecutor 未配置（オプション）")

if HAS_COORDINATOR:
    logger.info("✅ 新規 TaskCoordinator 利用可能")
else:
    logger.info("ℹ️ TaskCoordinator 未配置（オプション）")

if HAS_WORKFLOW_EXECUTOR:
    logger.info("✅ 新規 WorkflowExecutor 利用可能")
else:
    logger.info("ℹ️ WorkflowExecutor 未配置（オプション）")

logger.info("=" * 60)


# ========================================
# 便利関数: パッケージモジュールを一括インポート
# ========================================

def load_all_modules():
    """
    利用可能な全モジュールを辞書形式で返す
    
    Returns:
        Dict: モジュール名をキー、モジュールオブジェクトを値とする辞書
    """
    modules = {}
    
    if HAS_LEGACY_CONTENT:
        modules['legacy_content'] = LegacyContentExecutor
    if HAS_LEGACY_MA:
        modules['legacy_ma'] = LegacyMAExecutor
    if HAS_CONTENT_EXECUTOR:
        modules['content'] = ContentTaskExecutor
    if HAS_CLI_EXECUTOR:
        modules['cli'] = SystemCLIExecutor
    if HAS_COORDINATOR:
        modules['coordinator'] = TaskCoordinator
    if HAS_WORKFLOW_EXECUTOR:
        modules['workflow'] = WorkflowExecutor
    
    return modules


def get_available_modules():
    """
    利用可能なモジュールのリストを返す
    
    Returns:
        List[str]: 利用可能なモジュール名のリスト
    """
    available = []
    
    if HAS_LEGACY_CONTENT:
        available.append('legacy_content')
    if HAS_LEGACY_MA:
        available.append('legacy_ma')
    if HAS_CONTENT_EXECUTOR:
        available.append('content')
    if HAS_CLI_EXECUTOR:
        available.append('cli')
    if HAS_COORDINATOR:
        available.append('coordinator')
    if HAS_WORKFLOW_EXECUTOR:
        available.append('workflow')
    
    return available


def print_module_status():
    """
    モジュールの利用可能状況をコンソールに出力
    """
    print("\n" + "=" * 60)
    print("📦 task_executor パッケージモジュール状況")
    print("=" * 60)
    
    modules_status = [
        ("既存 task_executor_content", HAS_LEGACY_CONTENT),
        ("既存 task_executor_ma", HAS_LEGACY_MA),
        ("新規 ContentTaskExecutor", HAS_CONTENT_EXECUTOR),
        ("新規 SystemCLIExecutor", HAS_CLI_EXECUTOR),
        ("新規 TaskCoordinator", HAS_COORDINATOR),
        ("新規 WorkflowExecutor", HAS_WORKFLOW_EXECUTOR)
    ]
    
    for name, available in modules_status:
        status = "✅ 利用可能" if available else "❌ 未配置"
        print(f"{name}: {status}")
    
    print("=" * 60 + "\n")