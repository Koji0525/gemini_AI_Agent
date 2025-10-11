"""
data_models.py - 自律型修正システムのデータモデル定義
ErrorContextModelとバグ修正タスクの構造化データモデル
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ErrorSeverity(str, Enum):
    """エラー深刻度"""
    CRITICAL = "critical"  # システム停止レベル
    HIGH = "high"         # 機能不全
    MEDIUM = "medium"     # 部分的な問題
    LOW = "low"          # 軽微な問題


class ErrorCategory(str, Enum):
    """エラーカテゴリ"""
    IMPORT_ERROR = "import_error"
    ATTRIBUTE_ERROR = "attribute_error"
    TYPE_ERROR = "type_error"
    SYNTAX_ERROR = "syntax_error"
    WP_CLI_ERROR = "wp_cli_error"
    ACF_ERROR = "acf_error"
    RUNTIME_ERROR = "runtime_error"
    UNKNOWN = "unknown"


class CodeLocation(BaseModel):
    """コードの位置情報"""
    file_path: str = Field(..., description="ファイルパス")
    line_number: int = Field(..., description="エラー発生行番号")
    function_name: Optional[str] = Field(None, description="関数名")
    class_name: Optional[str] = Field(None, description="クラス名")
    
    @validator('line_number')
    def validate_line_number(cls, v):
        if v < 1:
            raise ValueError("行番号は1以上である必要があります")
        return v


class StackTraceFrame(BaseModel):
    """スタックトレースのフレーム情報"""
    file_path: str = Field(..., description="ファイルパス")
    line_number: int = Field(..., description="行番号")
    function_name: str = Field(..., description="関数名")
    code_context: Optional[str] = Field(None, description="コード文脈(前後3行)")


class ErrorContextModel(BaseModel):
    """
    エラーコンテキスト - AI修正に必要な全情報を構造化
    
    このモデルは、発生したエラーの詳細情報を保持し、
    AIが適切な修正コードを生成するための入力として使用される
    """
    
    # 基本情報
    error_id: str = Field(..., description="エラーID (task_id + timestamp)")
    timestamp: datetime = Field(default_factory=datetime.now, description="エラー発生時刻")
    task_id: str = Field(..., description="失敗したタスクID")
    agent_name: Optional[str] = Field(None, description="実行中のエージェント名")
    
    # エラー分類
    error_type: str = Field(..., description="Pythonエラー型名 (AttributeError等)")
    error_category: ErrorCategory = Field(ErrorCategory.UNKNOWN, description="エラーカテゴリ")
    severity: ErrorSeverity = Field(ErrorSeverity.MEDIUM, description="深刻度")
    
    # エラー詳細
    error_message: str = Field(..., description="エラーメッセージ")
    full_traceback: str = Field(..., description="完全なスタックトレース")
    stack_frames: List[StackTraceFrame] = Field(default_factory=list, description="構造化スタックトレース")
    
    # コード情報
    error_location: Optional[CodeLocation] = Field(None, description="エラー発生位置")
    problematic_code: Optional[str] = Field(None, description="問題のあるコードスニペット")
    surrounding_code: Optional[str] = Field(None, description="周辺コード(前後10行)")
    
    # 実行コンテキスト
    local_variables: Dict[str, Any] = Field(default_factory=dict, description="ローカル変数の状態")
    global_variables: Dict[str, Any] = Field(default_factory=dict, description="グローバル変数の状態")
    function_arguments: Optional[Dict[str, Any]] = Field(None, description="関数の引数")
    
    # タスク情報
    task_description: Optional[str] = Field(None, description="タスク説明")
    task_parameters: Optional[Dict[str, Any]] = Field(None, description="タスクパラメータ")
    
    # WordPress/ACF固有情報
    wp_context: Optional[Dict[str, Any]] = Field(None, description="WordPressコンテキスト")
    acf_info: Optional[Dict[str, Any]] = Field(None, description="ACF情報")
    
    # 修正試行履歴
    previous_fix_attempts: List[Dict[str, Any]] = Field(default_factory=list, description="過去の修正試行")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @validator('error_category', pre=True, always=True)
    def categorize_error(cls, v, values):
        """エラータイプから自動的にカテゴリを判定"""
        if v != ErrorCategory.UNKNOWN:
            return v
        
        error_type = values.get('error_type', '').lower()
        error_message = values.get('error_message', '').lower()
        
        if 'import' in error_type or 'modulenotfound' in error_type:
            return ErrorCategory.IMPORT_ERROR
        elif 'attributeerror' in error_type:
            return ErrorCategory.ATTRIBUTE_ERROR
        elif 'typeerror' in error_type:
            return ErrorCategory.TYPE_ERROR
        elif 'syntaxerror' in error_type:
            return ErrorCategory.SYNTAX_ERROR
        elif 'wp-cli' in error_message or 'wordpress' in error_message:
            return ErrorCategory.WP_CLI_ERROR
        elif 'acf' in error_message:
            return ErrorCategory.ACF_ERROR
        else:
            return ErrorCategory.RUNTIME_ERROR


class BugFixTask(BaseModel):
    """
    バグ修正タスク - 自律修正ワークフローのタスク定義
    """
    
    task_id: str = Field(..., description="バグ修正タスクID (FIX_BUG_xxx)")
    original_task_id: str = Field(..., description="元のタスクID")
    error_context: ErrorContextModel = Field(..., description="エラーコンテキスト")
    
    # タスク設定
    priority: str = Field("critical", description="優先度 (critical/high/medium/low)")
    required_role: str = Field("quick_fix", description="必要な役割")
    
    # 修正戦略
    fix_strategy: Optional[str] = Field(None, description="修正戦略 (patch/rewrite/refactor)")
    target_files: List[str] = Field(default_factory=list, description="修正対象ファイル")
    
    # AI生成用プロンプト
    fix_prompt: Optional[str] = Field(None, description="AI修正プロンプト")
    
    # 検証要件
    test_command: Optional[str] = Field(None, description="テストコマンド")
    expected_outcome: Optional[str] = Field(None, description="期待される結果")
    
    # ステータス管理
    status: str = Field("pending", description="ステータス (pending/in_progress/testing/success/failed)")
    created_at: datetime = Field(default_factory=datetime.now, description="作成日時")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FixResult(BaseModel):
    """修正結果モデル"""
    
    task_id: str = Field(..., description="バグ修正タスクID")
    success: bool = Field(..., description="修正成功フラグ")
    
    # 修正内容
    modified_files: List[str] = Field(default_factory=list, description="修正されたファイル")
    generated_code: Optional[str] = Field(None, description="AI生成コード")
    patch_content: Optional[str] = Field(None, description="パッチ内容(Diff形式)")
    
    # テスト結果
    test_passed: bool = Field(False, description="テスト成功")
    test_output: Optional[str] = Field(None, description="テスト出力")
    test_errors: List[str] = Field(default_factory=list, description="テストエラー")
    
    # GitHub連携情報
    branch_name: Optional[str] = Field(None, description="作成されたブランチ名")
    commit_hash: Optional[str] = Field(None, description="コミットハッシュ")
    pr_number: Optional[int] = Field(None, description="プルリクエスト番号")
    pr_url: Optional[str] = Field(None, description="プルリクエストURL")
    
    # メタ情報
    execution_time: float = Field(..., description="実行時間(秒)")
    completed_at: datetime = Field(default_factory=datetime.now, description="完了日時")
    error_message: Optional[str] = Field(None, description="エラーメッセージ(失敗時)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TestCaseModel(BaseModel):
    """自動テストケースモデル"""
    
    test_id: str = Field(..., description="テストID")
    test_name: str = Field(..., description="テスト名")
    test_type: str = Field(..., description="テストタイプ (unit/integration/e2e)")
    
    # テスト定義
    test_command: str = Field(..., description="テストコマンド")
    test_file: Optional[str] = Field(None, description="テストファイルパス")
    test_function: Optional[str] = Field(None, description="テスト関数名")
    
    # 期待値
    expected_return_code: int = Field(0, description="期待されるリターンコード")
    expected_output_pattern: Optional[str] = Field(None, description="期待される出力パターン(正規表現)")
    forbidden_patterns: List[str] = Field(default_factory=list, description="禁止パターン(エラー文字列)")
    
    # 実行結果
    last_run: Optional[datetime] = Field(None, description="最終実行日時")
    last_result: Optional[bool] = Field(None, description="最終結果")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }