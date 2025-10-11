# data_models.py
"""
データモデル定義（拡張版）
ハイブリッド自律修正システム用
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


# ========================================
# Enum定義
# ========================================

class ErrorSeverity(str, Enum):
    """エラー深刻度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """エラーカテゴリ"""
    SYNTAX = "syntax"
    IMPORT = "import"
    RUNTIME = "runtime"
    LOGIC = "logic"
    DESIGN = "design"
    PERFORMANCE = "performance"
    SECURITY = "security"
    UNKNOWN = "unknown"


class TaskStatus(str, Enum):
    """タスクステータス"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class FixStrategy(str, Enum):
    """修正戦略"""
    LOCAL_ONLY = "local_only"
    CLOUD_ONLY = "cloud_only"
    LOCAL_FIRST = "local_first"
    CLOUD_FIRST = "cloud_first"
    PARALLEL = "parallel"
    ADAPTIVE = "adaptive"


# ========================================
# エラー関連モデル
# ========================================

class ErrorContextModel(BaseModel):
    """エラーコンテキスト"""
    error_type: str = Field(..., description="エラータイプ")
    error_message: str = Field(..., description="エラーメッセージ")
    severity: ErrorSeverity = Field(ErrorSeverity.MEDIUM, description="深刻度")
    error_category: ErrorCategory = Field(ErrorCategory.UNKNOWN, description="カテゴリ")
    
    file_path: Optional[str] = Field(None, description="エラー発生ファイル")
    line_number: Optional[int] = Field(None, description="行番号")
    
    full_traceback: Optional[str] = Field(None, description="完全なトレースバック")
    surrounding_code: Optional[str] = Field(None, description="周辺コード")
    local_variables: Optional[Dict[str, Any]] = Field(None, description="ローカル変数")
    
    context_info: Optional[Dict[str, Any]] = Field(None, description="追加コンテキスト")
    timestamp: datetime = Field(default_factory=datetime.now, description="発生時刻")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error_type": "AttributeError",
                "error_message": "'NoneType' object has no attribute 'get'",
                "severity": "high",
                "error_category": "runtime",
                "file_path": "wp_agent.py",
                "line_number": 42
            }
        }


class ErrorClassification(BaseModel):
    """エラー分類結果"""
    error_type: str
    category: str
    complexity: str
    complexity_score: float
    confidence: float
    recommended_strategy: str
    factors: List[str] = Field(default_factory=list)


# ========================================
# タスク関連モデル
# ========================================

class BugFixTask(BaseModel):
    """バグ修正タスク"""
    task_id: str = Field(..., description="タスクID")
    error_context: ErrorContextModel = Field(..., description="エラーコンテキスト")
    target_files: List[str] = Field(default_factory=list, description="対象ファイル")
    
    priority: int = Field(5, description="優先度（1-10）")
    run_tests: bool = Field(True, description="テスト実行フラグ")
    create_pr: bool = Field(False, description="PR作成フラグ")
    
    fix_strategy: Optional[FixStrategy] = Field(None, description="修正戦略")
    timeout: int = Field(300, description="タイムアウト（秒）")
    
    metadata: Dict[str, Any] = Field(default_factory=dict, description="メタデータ")
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "Task-54-Fix",
                "target_files": ["wp_agent.py"],
                "priority": 8,
                "run_tests": True
            }
        }


class Task(BaseModel):
    """汎用タスク"""
    task_id: str
    task_type: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    
    priority: int = 5
    assigned_agent: Optional[str] = None
    
    dependencies: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ========================================
# 修正結果関連モデル
# ========================================

class FixResult(BaseModel):
    """修正結果"""
    task_id: str = Field(..., description="タスクID")
    success: bool = Field(..., description="成功フラグ")
    
    modified_files: List[str] = Field(default_factory=list, description="修正されたファイル")
    generated_code: str = Field("", description="生成されたコード")
    
    test_passed: bool = Field(False, description="テスト合格フラグ")
    execution_time: float = Field(0.0, description="実行時間（秒）")
    
    confidence_score: float = Field(0.0, description="信頼度スコア（0-1）")
    reasoning: str = Field("", description="修正理由")
    
    backup_path: Optional[str] = Field(None, description="バックアップパス")
    pr_url: Optional[str] = Field(None, description="プルリクエストURL")
    
    error_message: Optional[str] = Field(None, description="エラーメッセージ")
    warnings: List[str] = Field(default_factory=list, description="警告リスト")
    
    metadata: Dict[str, Any] = Field(default_factory=dict, description="メタデータ")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # エージェント情報
    agent_used: Optional[str] = Field(None, description="使用されたエージェント")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "Task-54-Fix",
                "success": True,
                "modified_files": ["wp_agent.py"],
                "test_passed": True,
                "execution_time": 12.5,
                "confidence_score": 0.92
            }
        }


class TestResult(BaseModel):
    """テスト結果"""
    task_id: str
    passed: bool
    
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    
    execution_time: float = 0.0
    
    test_details: List[Dict[str, Any]] = Field(default_factory=list)
    error: Optional[str] = None
    
    timestamp: datetime = Field(default_factory=datetime.now)


# ========================================
# Git/GitHub関連モデル
# ========================================

class CommitInfo(BaseModel):
    """コミット情報"""
    commit_hash: str
    branch_name: str
    commit_message: str
    author: str = "AutoFixAgent"
    timestamp: datetime = Field(default_factory=datetime.now)
    
    modified_files: List[str] = Field(default_factory=list)


class PullRequestInfo(BaseModel):
    """プルリクエスト情報"""
    pr_number: Optional[int] = None
    pr_url: str
    title: str
    body: str
    
    base_branch: str = "main"
    head_branch: str
    
    status: str = "open"
    created_at: datetime = Field(default_factory=datetime.now)


# ========================================
# 統計情報モデル
# ========================================

class AgentStats(BaseModel):
    """エージェント統計情報"""
    agent_name: str
    
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    
    success_rate: float = 0.0
    
    additional_metrics: Dict[str, Any] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.now)


class SystemStats(BaseModel):
    """システム全体の統計"""
    total_fixes: int = 0
    successful_fixes: int = 0
    failed_fixes: int = 0
    
    local_fixes: int = 0
    cloud_fixes: int = 0
    hybrid_fixes: int = 0
    
    total_tests: int = 0
    passed_tests: int = 0
    
    total_prs: int = 0
    merged_prs: int = 0
    
    uptime_seconds: float = 0.0
    
    agent_stats: Dict[str, AgentStats] = Field(default_factory=dict)
    
    last_updated: datetime = Field(default_factory=datetime.now)


# ========================================
# AI応答モデル
# ========================================

class AIFixResponse(BaseModel):
    """AI修正応答"""
    analysis: str = Field(..., description="エラー分析")
    root_cause: str = Field(..., description="根本原因")
    fix_strategy: str = Field(..., description="修正戦略")
    
    modified_files: Dict[str, str] = Field(..., description="ファイルパス: コード")
    
    confidence: float = Field(..., ge=0.0, le=1.0, description="信頼度")
    reasoning: str = Field(..., description="修正理由")
    
    test_suggestions: List[str] = Field(default_factory=list)
    potential_side_effects: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "analysis": "AttributeError due to None value",
                "root_cause": "Missing null check",
                "fix_strategy": "Add defensive programming",
                "modified_files": {
                    "wp_agent.py": "def method():\n    if obj is not None:\n        ..."
                },
                "confidence": 0.95,
                "reasoning": "Added null check to prevent AttributeError"
            }
        }


# ========================================
# 設定モデル
# ========================================

class HybridFixConfig(BaseModel):
    """ハイブリッド修正設定"""
    default_strategy: FixStrategy = FixStrategy.ADAPTIVE
    
    local_timeout: int = 30
    cloud_timeout: int = 120
    
    enable_auto_tests: bool = True
    enable_auto_pr: bool = False
    
    max_retry_count: int = 3
    
    cloud_provider: str = "openai"
    cloud_model: str = "gpt-4o"
    
    github_auto_merge: bool = False
    
    backup_retention_days: int = 30


# ========================================
# ユーティリティ関数
# ========================================

def create_bug_fix_task_from_exception(
    task_id: str,
    exception: Exception,
    file_path: str,
    line_number: int,
    **kwargs
) -> BugFixTask:
    """例外からバグ修正タスクを作成"""
    import traceback
    
    error_context = ErrorContextModel(
        error_type=type(exception).__name__,
        error_message=str(exception),
        file_path=file_path,
        line_number=line_number,
        full_traceback=traceback.format_exc(),
        **kwargs
    )
    
    return BugFixTask(
        task_id=task_id,
        error_context=error_context,
        target_files=[file_path]
    )


def create_fix_result_success(
    task_id: str,
    modified_files: List[str],
    generated_code: str,
    **kwargs
) -> FixResult:
    """成功結果を作成"""
    return FixResult(
        task_id=task_id,
        success=True,
        modified_files=modified_files,
        generated_code=generated_code,
        test_passed=True,
        **kwargs
    )


def create_fix_result_failure(
    task_id: str,
    error_message: str,
    **kwargs
) -> FixResult:
    """失敗結果を作成"""
    return FixResult(
        task_id=task_id,
        success=False,
        error_message=error_message,
        **kwargs
    )