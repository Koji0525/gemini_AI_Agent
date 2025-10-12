# config_hybrid.py
"""
ハイブリッド型自律コード修正システム - 設定ファイル
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class HybridFixConfig:
    """ハイブリッド修正システムの設定"""
    
    # ========================================
    # 基本設定
    # ========================================
    
    # 実行モード
    run_mode: str = field(
        default_factory=lambda: os.getenv("RUN_MODE", "local")
    )  # local, cloud, hybrid
    
    # デフォルト修正戦略
    default_strategy: str = field(
        default_factory=lambda: os.getenv("DEFAULT_STRATEGY", "ADAPTIVE")
    )  # LOCAL_ONLY, CLOUD_ONLY, LOCAL_FIRST, CLOUD_FIRST, PARALLEL, ADAPTIVE
    
    # ========================================
    # ローカルエージェント設定
    # ========================================
    
    # ローカルAI使用フラグ
    use_local_ai: bool = field(
        default_factory=lambda: os.getenv("USE_LOCAL_AI", "true").lower() == "true"
    )
    
    # ローカル修正タイムアウト（秒）
    local_timeout: int = field(
        default_factory=lambda: int(os.getenv("LOCAL_TIMEOUT", "30"))
    )
    
    # ========================================
    # クラウドエージェント設定
    # ========================================
    
    # クラウドプロバイダー
    cloud_provider: str = field(
        default_factory=lambda: os.getenv("CLOUD_PROVIDER", "openai")
    )  # openai, anthropic, google
    
    # クラウドモデル名
    cloud_model: str = field(
        default_factory=lambda: os.getenv("CLOUD_MODEL", "gpt-4o")
    )
    
    # クラウド修正タイムアウト（秒）
    cloud_timeout: int = field(
        default_factory=lambda: int(os.getenv("CLOUD_TIMEOUT", "120"))
    )
    
    # APIキー
    openai_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY")
    )
    
    anthropic_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY")
    )
    
    google_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("GOOGLE_API_KEY")
    )
    
    # ========================================
    # テスト設定
    # ========================================
    
    # 自動テスト有効化
    enable_auto_tests: bool = field(
        default_factory=lambda: os.getenv("ENABLE_AUTO_TESTS", "true").lower() == "true"
    )
    
    # WordPressパス
    wp_path: str = field(
        default_factory=lambda: os.getenv("WP_PATH", "/var/www/html")
    )
    
    # テストタイムアウト（秒）
    test_timeout: int = field(
        default_factory=lambda: int(os.getenv("TEST_TIMEOUT", "60"))
    )
    
    # ========================================
    # GitHub設定
    # ========================================
    
    # 自動PR作成有効化
    enable_auto_pr: bool = field(
        default_factory=lambda: os.getenv("ENABLE_AUTO_PR", "false").lower() == "true"
    )
    
    # GitHubトークン
    github_token: Optional[str] = field(
        default_factory=lambda: os.getenv("GITHUB_TOKEN")
    )
    
    # リポジトリパス
    repo_path: str = field(
        default_factory=lambda: os.getenv("REPO_PATH", ".")
    )
    
    # リポジトリオーナー
    repo_owner: Optional[str] = field(
        default_factory=lambda: os.getenv("REPO_OWNER")
    )
    
    # リポジトリ名
    repo_name: Optional[str] = field(
        default_factory=lambda: os.getenv("REPO_NAME")
    )
    
    # PRの自動マージ
    github_auto_merge: bool = field(
        default_factory=lambda: os.getenv("GITHUB_AUTO_MERGE", "false").lower() == "true"
    )
    
    # ========================================
    # ストレージ設定
    # ========================================
    
    # ストレージプロバイダー
    storage_provider: str = field(
        default_factory=lambda: os.getenv("STORAGE_PROVIDER", "local")
    )  # local, gcs, s3, azure
    
    # ストレージバケット名
    storage_bucket: Optional[str] = field(
        default_factory=lambda: os.getenv("STORAGE_BUCKET")
    )
    
    # 自動同期
    auto_sync_storage: bool = field(
        default_factory=lambda: os.getenv("AUTO_SYNC_STORAGE", "true").lower() == "true"
    )
    
    # ========================================
    # バックアップ設定
    # ========================================
    
    # バックアップディレクトリ
    backup_dir: str = field(
        default_factory=lambda: os.getenv("BACKUP_DIR", "./backups")
    )
    
    # 最大バックアップ数
    max_backups: int = field(
        default_factory=lambda: int(os.getenv("MAX_BACKUPS", "10"))
    )
    
    # バックアップ保持日数
    backup_retention_days: int = field(
        default_factory=lambda: int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
    )
    
    # ========================================
    # リトライ設定
    # ========================================
    
    # 最大リトライ回数
    max_retry_count: int = field(
        default_factory=lambda: int(os.getenv("MAX_RETRY_COUNT", "3"))
    )
    
    # リトライ間隔（秒）
    retry_delay: int = field(
        default_factory=lambda: int(os.getenv("RETRY_DELAY", "5"))
    )
    
    # ========================================
    # ログ設定
    # ========================================
    
    # ログレベル
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO")
    )
    
    # ログファイル
    log_file: Optional[str] = field(
        default_factory=lambda: os.getenv("LOG_FILE", "./logs/hybrid_fix.log")
    )
    
    # ログローテーション
    log_rotation: str = field(
        default_factory=lambda: os.getenv("LOG_ROTATION", "10 MB")
    )
    
    # ========================================
    # パフォーマンス設定
    # ========================================
    
    # 並列実行の最大数
    max_parallel_fixes: int = field(
        default_factory=lambda: int(os.getenv("MAX_PARALLEL_FIXES", "3"))
    )
    
    # キャッシュ有効化
    enable_cache: bool = field(
        default_factory=lambda: os.getenv("ENABLE_CACHE", "true").lower() == "true"
    )
    
    # キャッシュTTL（秒）
    cache_ttl: int = field(
        default_factory=lambda: int(os.getenv("CACHE_TTL", "3600"))
    )
    
    # ========================================
    # 通知設定
    # ========================================
    
    # Slack通知
    enable_slack_notifications: bool = field(
        default_factory=lambda: os.getenv("ENABLE_SLACK_NOTIFICATIONS", "false").lower() == "true"
    )
    
    slack_webhook_url: Optional[str] = field(
        default_factory=lambda: os.getenv("SLACK_WEBHOOK_URL")
    )
    
    # メール通知
    enable_email_notifications: bool = field(
        default_factory=lambda: os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "false").lower() == "true"
    )
    
    email_recipients: str = field(
        default_factory=lambda: os.getenv("EMAIL_RECIPIENTS", "")
    )
    
    # ========================================
    # ヘルスチェック設定
    # ========================================
    
    # ヘルスチェック間隔（秒）
    health_check_interval: int = field(
        default_factory=lambda: int(os.getenv("HEALTH_CHECK_INTERVAL", "60"))
    )
    
    # メトリクス収集
    enable_metrics: bool = field(
        default_factory=lambda: os.getenv("ENABLE_METRICS", "true").lower() == "true"
    )
    
    # ========================================
    # デバッグ設定
    # ========================================
    
    # デバッグモード
    debug_mode: bool = field(
        default_factory=lambda: os.getenv("DEBUG_MODE", "false").lower() == "true"
    )
    
    # 詳細ログ
    verbose_logging: bool = field(
        default_factory=lambda: os.getenv("VERBOSE_LOGGING", "false").lower() == "true"
    )
    
    # ドライラン（実際の修正を適用しない）
    dry_run: bool = field(
        default_factory=lambda: os.getenv("DRY_RUN", "false").lower() == "true"
    )
    
    def __post_init__(self):
        """初期化後の処理"""
        # ディレクトリを作成
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)
        
        if self.log_file:
            Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> bool:
        """設定を検証"""
        errors = []
        
        # 戦略の検証
        valid_strategies = [
            "LOCAL_ONLY", "CLOUD_ONLY", "LOCAL_FIRST", 
            "CLOUD_FIRST", "PARALLEL", "ADAPTIVE"
        ]
        if self.default_strategy not in valid_strategies:
            errors.append(f"Invalid strategy: {self.default_strategy}")
        
        # クラウドプロバイダーの検証
        valid_providers = ["openai", "anthropic", "google"]
        if self.cloud_provider not in valid_providers:
            errors.append(f"Invalid cloud provider: {self.cloud_provider}")
        
        # APIキーの検証
        if self.cloud_provider == "openai" and not self.openai_api_key:
            errors.append("OpenAI API key is required")
        
        if self.cloud_provider == "anthropic" and not self.anthropic_api_key:
            errors.append("Anthropic API key is required")
        
        if self.cloud_provider == "google" and not self.google_api_key:
            errors.append("Google API key is required")
        
        # GitHub設定の検証
        if self.enable_auto_pr:
            if not self.github_token:
                errors.append("GitHub token is required for auto PR")
            if not self.repo_owner or not self.repo_name:
                errors.append("GitHub repo owner and name are required for auto PR")
        
        # ストレージ設定の検証
        valid_storage_providers = ["local", "gcs", "s3", "azure"]
        if self.storage_provider not in valid_storage_providers:
            errors.append(f"Invalid storage provider: {self.storage_provider}")
        
        if self.storage_provider != "local" and not self.storage_bucket:
            errors.append(f"Storage bucket is required for {self.storage_provider}")
        
        if errors:
            for error in errors:
                print(f"❌ 設定エラー: {error}")
            return False
        
        return True
    
    def print_config(self):
        """設定を表示"""
        print("\n" + "=" * 80)
        print("⚙️  ハイブリッド修正システム 設定")
        print("=" * 80)
        print(f"実行モード: {self.run_mode}")
        print(f"デフォルト戦略: {self.default_strategy}")
        print(f"\n【ローカルエージェント】")
        print(f"  ローカルAI: {'有効' if self.use_local_ai else '無効'}")
        print(f"  タイムアウト: {self.local_timeout}秒")
        print(f"\n【クラウドエージェント】")
        print(f"  プロバイダー: {self.cloud_provider}")
        print(f"  モデル: {self.cloud_model}")
        print(f"  タイムアウト: {self.cloud_timeout}秒")
        print(f"\n【テスト】")
        print(f"  自動テスト: {'有効' if self.enable_auto_tests else '無効'}")
        print(f"  WPパス: {self.wp_path}")
        print(f"\n【GitHub】")
        print(f"  自動PR: {'有効' if self.enable_auto_pr else '無効'}")
        if self.enable_auto_pr:
            print(f"  リポジトリ: {self.repo_owner}/{self.repo_name}")
        print(f"\n【ストレージ】")
        print(f"  プロバイダー: {self.storage_provider}")
        if self.storage_provider != "local":
            print(f"  バケット: {self.storage_bucket}")
        print(f"\n【バックアップ】")
        print(f"  ディレクトリ: {self.backup_dir}")
        print(f"  最大保持数: {self.max_backups}")
        print(f"\n【その他】")
        print(f"  デバッグモード: {'有効' if self.debug_mode else '無効'}")
        print(f"  ドライラン: {'有効' if self.dry_run else '無効'}")
        print("=" * 80 + "\n")
    
    @classmethod
    def from_env_file(cls, env_file: str = ".env"):
        """環境変数ファイルから設定を読み込み"""
        if Path(env_file).exists():
            from dotenv import load_dotenv
            load_dotenv(env_file)
        
        return cls()
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            key: getattr(self, key)
            for key in self.__dataclass_fields__.keys()
        }


# ========================================
# プリセット設定
# ========================================

class DevelopmentConfig(HybridFixConfig):
    """開発環境用設定"""
    
    def __init__(self):
        super().__init__()
        self.run_mode = "local"
        self.default_strategy = "LOCAL_FIRST"
        self.use_local_ai = True
        self.enable_auto_pr = False
        self.debug_mode = True
        self.verbose_logging = True
        self.dry_run = True


class ProductionConfig(HybridFixConfig):
    """本番環境用設定"""
    
    def __init__(self):
        super().__init__()
        self.run_mode = "hybrid"
        self.default_strategy = "ADAPTIVE"
        self.use_local_ai = True
        self.enable_auto_tests = True
        self.enable_auto_pr = True
        self.storage_provider = "gcs"
        self.debug_mode = False
        self.dry_run = False


class CloudOnlyConfig(HybridFixConfig):
    """クラウドのみの設定"""
    
    def __init__(self):
        super().__init__()
        self.run_mode = "cloud"
        self.default_strategy = "CLOUD_ONLY"
        self.use_local_ai = False
        self.enable_auto_tests = True
        self.enable_auto_pr = True


# ========================================
# 設定ファクトリー
# ========================================

def get_config(env: str = "development") -> HybridFixConfig:
    """
    環境に応じた設定を取得
    
    Args:
        env: 環境名 (development, production, cloud_only)
        
    Returns:
        HybridFixConfig: 設定オブジェクト
    """
    configs = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "cloud_only": CloudOnlyConfig
    }
    
    config_class = configs.get(env, HybridFixConfig)
    config = config_class()
    
    # 環境変数から追加で読み込み
    if os.getenv("CONFIG_FROM_ENV", "false").lower() == "true":
        config = HybridFixConfig.from_env_file()
    
    return config


if __name__ == "__main__":
    # テスト実行
    config = get_config("development")
    
    print("設定の検証中...")
    if config.validate():
        print("✅ 設定は有効です")
        config.print_config()
    else:
        print("❌ 設定に問題があります")