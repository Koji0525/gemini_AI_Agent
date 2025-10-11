"""
ConfigValidator - 設定検証とバリデーションエージェント

設定ファイルの構文チェック、APIキーの有効性確認、環境変数の検証、
依存関係の確認、設定の推奨値提案を提供する。
"""

import os
import json
import yaml
import re
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """検証レベル"""
    ERROR = "error"  # 致命的なエラー
    WARNING = "warning"  # 警告
    INFO = "info"  # 情報
    SUCCESS = "success"  # 成功


@dataclass
class ValidationResult:
    """検証結果"""
    level: ValidationLevel
    category: str
    message: str
    field: Optional[str] = None
    expected: Optional[Any] = None
    actual: Optional[Any] = None
    suggestion: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level.value,
            "category": self.category,
            "message": self.message,
            "field": self.field,
            "expected": self.expected,
            "actual": self.actual,
            "suggestion": self.suggestion
        }


@dataclass
class ConfigSchema:
    """設定スキーマ定義"""
    required_fields: Set[str]
    optional_fields: Set[str]
    field_types: Dict[str, type]
    field_validators: Dict[str, Any]  # カスタムバリデータ
    recommended_values: Dict[str, Any]
    
    def get_all_fields(self) -> Set[str]:
        return self.required_fields | self.optional_fields


class ConfigValidatorAgent:
    """
    設定検証とバリデーションエージェント
    
    主な機能:
    1. 設定ファイルの構文チェック
    2. APIキーの有効性確認
    3. 環境変数の検証
    4. 依存関係の確認
    5. 設定の推奨値提案
    """
    
    def __init__(self):
        self.validation_results: List[ValidationResult] = []
        
        # 設定スキーマの定義
        self.schemas = {
            "browser": self._define_browser_schema(),
            "ai": self._define_ai_schema(),
            "wordpress": self._define_wordpress_schema(),
            "system": self._define_system_schema()
        }
        
        logger.info("ConfigValidatorAgent initialized")
    
    def _define_browser_schema(self) -> ConfigSchema:
        """ブラウザ設定スキーマ"""
        return ConfigSchema(
            required_fields={"headless", "user_data_dir"},
            optional_fields={"window_size", "disable_gpu", "no_sandbox"},
            field_types={
                "headless": bool,
                "user_data_dir": str,
                "window_size": tuple,
                "disable_gpu": bool,
                "no_sandbox": bool
            },
            field_validators={
                "window_size": lambda v: len(v) == 2 and all(isinstance(x, int) for x in v)
            },
            recommended_values={
                "headless": True,  # クラウド環境では推奨
                "window_size": (1920, 1080)
            }
        )
    
    def _define_ai_schema(self) -> ConfigSchema:
        """AI設定スキーマ"""
        return ConfigSchema(
            required_fields={"provider", "model", "api_key"},
            optional_fields={"temperature", "max_tokens", "timeout"},
            field_types={
                "provider": str,
                "model": str,
                "api_key": str,
                "temperature": float,
                "max_tokens": int,
                "timeout": int
            },
            field_validators={
                "provider": lambda v: v in ["openai", "anthropic", "google", "deepseek"],
                "temperature": lambda v: 0.0 <= v <= 2.0,
                "max_tokens": lambda v: v > 0
            },
            recommended_values={
                "temperature": 0.7,
                "max_tokens": 4000,
                "timeout": 60
            }
        )
    
    def _define_wordpress_schema(self) -> ConfigSchema:
        """WordPress設定スキーマ"""
        return ConfigSchema(
            required_fields={"url", "username", "password"},
            optional_fields={"wp_cli_path", "ssh_host", "ssh_user"},
            field_types={
                "url": str,
                "username": str,
                "password": str,
                "wp_cli_path": str,
                "ssh_host": str,
                "ssh_user": str
            },
            field_validators={
                "url": lambda v: v.startswith("http://") or v.startswith("https://")
            },
            recommended_values={}
        )
    
    def _define_system_schema(self) -> ConfigSchema:
        """システム設定スキーマ"""
        return ConfigSchema(
            required_fields={"run_mode"},
            optional_fields={"log_level", "max_retries", "timeout"},
            field_types={
                "run_mode": str,
                "log_level": str,
                "max_retries": int,
                "timeout": int
            },
            field_validators={
                "run_mode": lambda v: v in ["local", "cloud"],
                "log_level": lambda v: v in ["DEBUG", "INFO", "WARNING", "ERROR"]
            },
            recommended_values={
                "log_level": "INFO",
                "max_retries": 3,
                "timeout": 300
            }
        )
    
    def validate_config_file(self, filepath: str) -> List[ValidationResult]:
        """
        設定ファイルを検証
        
        Args:
            filepath: 設定ファイルパス
        
        Returns:
            検証結果のリスト
        """
        self.validation_results = []
        
        # ファイルの存在確認
        if not os.path.exists(filepath):
            self.validation_results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                category="file",
                message=f"Configuration file not found: {filepath}",
                suggestion="Create the configuration file or check the path"
            ))
            return self.validation_results
        
        # ファイル形式の判定と読み込み
        try:
            config_data = self._load_config_file(filepath)
        except Exception as e:
            self.validation_results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                category="syntax",
                message=f"Failed to parse configuration file: {str(e)}",
                suggestion="Check file syntax (JSON/YAML format)"
            ))
            return self.validation_results
        
        # 各カテゴリの設定を検証
        for category, schema in self.schemas.items():
            if category in config_data:
                self._validate_category(category, config_data[category], schema)
            else:
                self.validation_results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    category=category,
                    message=f"Category '{category}' not found in configuration",
                    suggestion=f"Consider adding '{category}' configuration"
                ))
        
        return self.validation_results
    
    def _load_config_file(self, filepath: str) -> Dict[str, Any]:
        """設定ファイルを読み込む"""
        suffix = Path(filepath).suffix.lower()
        
        with open(filepath, 'r', encoding='utf-8') as f:
            if suffix == '.json':
                return json.load(f)
            elif suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            elif suffix == '.py':
                # Python設定ファイルの簡易読み込み
                # 注意: 実行は危険なので、変数定義のみをパース
                content = f.read()
                config = {}
                # 簡易パーサー（実際にはastモジュールを使うべき）
                for line in content.split('\n'):
                    if '=' in line and not line.strip().startswith('#'):
                        try:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = eval(value.strip())
                            config[key] = value
                        except:
                            pass
                return config
            else:
                raise ValueError(f"Unsupported file format: {suffix}")
    
    def _validate_category(self, 
                          category: str,
                          config: Dict[str, Any],
                          schema: ConfigSchema):
        """カテゴリ設定を検証"""
        # 必須フィールドのチェック
        for field in schema.required_fields:
            if field not in config:
                self.validation_results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    category=category,
                    field=field,
                    message=f"Required field '{field}' is missing",
                    suggestion=f"Add '{field}' to the configuration"
                ))
        
        # フィールドの型チェック
        for field, value in config.items():
            if field in schema.field_types:
                expected_type = schema.field_types[field]
                if not isinstance(value, expected_type):
                    self.validation_results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        category=category,
                        field=field,
                        message=f"Field '{field}' has wrong type",
                        expected=expected_type.__name__,
                        actual=type(value).__name__,
                        suggestion=f"Change type to {expected_type.__name__}"
                    ))
            
            # カスタムバリデータのチェック
            if field in schema.field_validators:
                validator = schema.field_validators[field]
                try:
                    if not validator(value):
                        self.validation_results.append(ValidationResult(
                            level=ValidationLevel.ERROR,
                            category=category,
                            field=field,
                            message=f"Field '{field}' failed validation",
                            actual=value,
                            suggestion="Check the value against requirements"
                        ))
                except Exception as e:
                    self.validation_results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        category=category,
                        field=field,
                        message=f"Validation error for '{field}': {str(e)}",
                        actual=value
                    ))
        
        # 推奨値のチェック
        for field, recommended in schema.recommended_values.items():
            if field in config and config[field] != recommended:
                self.validation_results.append(ValidationResult(
                    level=ValidationLevel.INFO,
                    category=category,
                    field=field,
                    message=f"Field '{field}' differs from recommended value",
                    expected=recommended,
                    actual=config[field],
                    suggestion=f"Consider using recommended value: {recommended}"
                ))
    
    def validate_api_keys(self, config: Dict[str, Any]) -> List[ValidationResult]:
        """
        APIキーの有効性を確認
        
        Args:
            config: 設定データ
        
        Returns:
            検証結果のリスト
        """
        results = []
        
        # OpenAI APIキー
        if "ai" in config and "api_key" in config["ai"]:
            api_key = config["ai"]["api_key"]
            provider = config["ai"].get("provider", "")
            
            if provider == "openai":
                is_valid, message = self._test_openai_key(api_key)
                results.append(ValidationResult(
                    level=ValidationLevel.SUCCESS if is_valid else ValidationLevel.ERROR,
                    category="api_key",
                    field="openai_api_key",
                    message=message,
                    suggestion="Check your API key in the OpenAI dashboard" if not is_valid else None
                ))
            elif provider == "anthropic":
                is_valid, message = self._test_anthropic_key(api_key)
                results.append(ValidationResult(
                    level=ValidationLevel.SUCCESS if is_valid else ValidationLevel.ERROR,
                    category="api_key",
                    field="anthropic_api_key",
                    message=message,
                    suggestion="Check your API key in the Anthropic console" if not is_valid else None
                ))
        
        return results
    
    def _test_openai_key(self, api_key: str) -> Tuple[bool, str]:
        """OpenAI APIキーをテスト"""
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(
                "https://api.openai.com/v1/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "OpenAI API key is valid"
            elif response.status_code == 401:
                return False, "OpenAI API key is invalid"
            else:
                return False, f"OpenAI API returned status {response.status_code}"
        except Exception as e:
            return False, f"Failed to test OpenAI API key: {str(e)}"
    
    def _test_anthropic_key(self, api_key: str) -> Tuple[bool, str]:
        """Anthropic APIキーをテスト"""
        try:
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            # 簡易的なテストリクエスト
            payload = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hi"}]
            }
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "Anthropic API key is valid"
            elif response.status_code == 401:
                return False, "Anthropic API key is invalid"
            else:
                return False, f"Anthropic API returned status {response.status_code}"
        except Exception as e:
            return False, f"Failed to test Anthropic API key: {str(e)}"
    
    def validate_environment_variables(self, 
                                      required_vars: List[str]) -> List[ValidationResult]:
        """
        環境変数を検証
        
        Args:
            required_vars: 必須環境変数のリスト
        
        Returns:
            検証結果のリスト
        """
        results = []
        
        for var_name in required_vars:
            value = os.getenv(var_name)
            
            if value is None:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    category="environment",
                    field=var_name,
                    message=f"Required environment variable '{var_name}' is not set",
                    suggestion=f"Set {var_name} in your environment"
                ))
            elif not value.strip():
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    category="environment",
                    field=var_name,
                    message=f"Environment variable '{var_name}' is empty",
                    suggestion=f"Provide a value for {var_name}"
                ))
            else:
                results.append(ValidationResult(
                    level=ValidationLevel.SUCCESS,
                    category="environment",
                    field=var_name,
                    message=f"Environment variable '{var_name}' is set"
                ))
        
        return results
    
    def validate_dependencies(self, 
                            requirements_file: str = "requirements.txt") -> List[ValidationResult]:
        """
        依存関係を検証
        
        Args:
            requirements_file: requirements.txtのパス
        
        Returns:
            検証結果のリスト
        """
        results = []
        
        if not os.path.exists(requirements_file):
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                category="dependencies",
                message=f"Requirements file not found: {requirements_file}",
                suggestion="Create a requirements.txt file"
            ))
            return results
        
        # requirements.txtを読み込む
        with open(requirements_file, 'r', encoding='utf-8') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # 各パッケージの存在を確認
        for req in requirements:
            # バージョン指定を分離
            package_name = re.split(r'[<>=!]', req)[0].strip()
            
            try:
                __import__(package_name.replace('-', '_'))
                results.append(ValidationResult(
                    level=ValidationLevel.SUCCESS,
                    category="dependencies",
                    field=package_name,
                    message=f"Package '{package_name}' is installed"
                ))
            except ImportError:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    category="dependencies",
                    field=package_name,
                    message=f"Package '{package_name}' is not installed",
                    suggestion=f"Run: pip install {req}"
                ))
        
        return results
    
    def check_directory_structure(self, 
                                 base_dir: str,
                                 required_dirs: List[str]) -> List[ValidationResult]:
        """
        必要なディレクトリ構造を検証
        
        Args:
            base_dir: ベースディレクトリ
            required_dirs: 必須ディレクトリのリスト
        
        Returns:
            検証結果のリスト
        """
        results = []
        base_path = Path(base_dir)
        
        for dir_name in required_dirs:
            dir_path = base_path / dir_name
            
            if not dir_path.exists():
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    category="directory_structure",
                    field=dir_name,
                    message=f"Required directory not found: {dir_name}",
                    suggestion=f"Create directory: mkdir {dir_path}"
                ))
            elif not dir_path.is_dir():
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    category="directory_structure",
                    field=dir_name,
                    message=f"Path exists but is not a directory: {dir_name}",
                    suggestion=f"Remove file and create directory: {dir_path}"
                ))
            else:
                results.append(ValidationResult(
                    level=ValidationLevel.SUCCESS,
                    category="directory_structure",
                    field=dir_name,
                    message=f"Directory exists: {dir_name}"
                ))
        
        return results
    
    def validate_network_connectivity(self, 
                                    urls: List[str]) -> List[ValidationResult]:
        """
        ネットワーク接続性を検証
        
        Args:
            urls: テストするURLのリスト
        
        Returns:
            検証結果のリスト
        """
        results = []
        
        for url in urls:
            try:
                response = requests.head(url, timeout=5, allow_redirects=True)
                
                if response.status_code < 400:
                    results.append(ValidationResult(
                        level=ValidationLevel.SUCCESS,
                        category="network",
                        field=url,
                        message=f"URL is accessible: {url}"
                    ))
                else:
                    results.append(ValidationResult(
                        level=ValidationLevel.WARNING,
                        category="network",
                        field=url,
                        message=f"URL returned status {response.status_code}: {url}",
                        suggestion="Check if the service is running"
                    ))
            except requests.exceptions.Timeout:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    category="network",
                    field=url,
                    message=f"Connection timeout: {url}",
                    suggestion="Check network connectivity or firewall settings"
                ))
            except requests.exceptions.ConnectionError:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    category="network",
                    field=url,
                    message=f"Connection failed: {url}",
                    suggestion="Check if the service is running and accessible"
                ))
            except Exception as e:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    category="network",
                    field=url,
                    message=f"Network error for {url}: {str(e)}"
                ))
        
        return results
    
    def validate_file_permissions(self, 
                                 files: List[str],
                                 required_permissions: str = "rw") -> List[ValidationResult]:
        """
        ファイルパーミッションを検証
        
        Args:
            files: チェックするファイルのリスト
            required_permissions: 必要なパーミッション ('r', 'w', 'x' の組み合わせ)
        
        Returns:
            検証結果のリスト
        """
        results = []
        
        for filepath in files:
            if not os.path.exists(filepath):
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    category="permissions",
                    field=filepath,
                    message=f"File not found: {filepath}",
                    suggestion=f"Create the file: {filepath}"
                ))
                continue
            
            has_read = os.access(filepath, os.R_OK)
            has_write = os.access(filepath, os.W_OK)
            has_execute = os.access(filepath, os.X_OK)
            
            missing = []
            if 'r' in required_permissions and not has_read:
                missing.append('read')
            if 'w' in required_permissions and not has_write:
                missing.append('write')
            if 'x' in required_permissions and not has_execute:
                missing.append('execute')
            
            if missing:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    category="permissions",
                    field=filepath,
                    message=f"Insufficient permissions for {filepath}: missing {', '.join(missing)}",
                    suggestion=f"Grant {', '.join(missing)} permission to the file"
                ))
            else:
                results.append(ValidationResult(
                    level=ValidationLevel.SUCCESS,
                    category="permissions",
                    field=filepath,
                    message=f"File has correct permissions: {filepath}"
                ))
        
        return results
    
    def generate_validation_report(self, 
                                  results: List[ValidationResult]) -> Dict[str, Any]:
        """
        検証レポートを生成
        
        Args:
            results: 検証結果のリスト
        
        Returns:
            レポートデータ
        """
        errors = [r for r in results if r.level == ValidationLevel.ERROR]
        warnings = [r for r in results if r.level == ValidationLevel.WARNING]
        info = [r for r in results if r.level == ValidationLevel.INFO]
        success = [r for r in results if r.level == ValidationLevel.SUCCESS]
        
        # カテゴリ別集計
        by_category = {}
        for result in results:
            if result.category not in by_category:
                by_category[result.category] = {
                    "errors": 0,
                    "warnings": 0,
                    "info": 0,
                    "success": 0
                }
            by_category[result.category][result.level.value + "s"] += 1
        
        return {
            "summary": {
                "total": len(results),
                "errors": len(errors),
                "warnings": len(warnings),
                "info": len(info),
                "success": len(success),
                "is_valid": len(errors) == 0
            },
            "by_category": by_category,
            "details": {
                "errors": [r.to_dict() for r in errors],
                "warnings": [r.to_dict() for r in warnings],
                "info": [r.to_dict() for r in info]
            },
            "generated_at": datetime.now().isoformat()
        }
    
    def auto_fix_config(self, 
                       config: Dict[str, Any],
                       validation_results: List[ValidationResult]) -> Tuple[Dict[str, Any], List[str]]:
        """
        設定を自動修正（可能な範囲で）
        
        Args:
            config: 設定データ
            validation_results: 検証結果
        
        Returns:
            (修正された設定, 適用された修正のリスト)
        """
        fixed_config = config.copy()
        applied_fixes = []
        
        for result in validation_results:
            # 推奨値の適用
            if result.level == ValidationLevel.INFO and result.expected is not None:
                category = result.category
                field = result.field
                
                if category in fixed_config and field:
                    fixed_config[category][field] = result.expected
                    applied_fixes.append(
                        f"Applied recommended value for {category}.{field}: {result.expected}"
                    )
            
            # 不足フィールドの追加（推奨値がある場合）
            if result.level == ValidationLevel.ERROR and "missing" in result.message.lower():
                category = result.category
                field = result.field
                
                if category in self.schemas:
                    schema = self.schemas[category]
                    if field in schema.recommended_values:
                        if category not in fixed_config:
                            fixed_config[category] = {}
                        
                        fixed_config[category][field] = schema.recommended_values[field]
                        applied_fixes.append(
                            f"Added missing field {category}.{field} with recommended value"
                        )
        
        return fixed_config, applied_fixes
    
    def export_validation_report(self, 
                               results: List[ValidationResult],
                               filepath: str):
        """
        検証レポートをファイルにエクスポート
        
        Args:
            results: 検証結果
            filepath: 出力ファイルパス
        """
        report = self.generate_validation_report(results)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Validation report exported to {filepath}")
    
    def get_summary(self, results: List[ValidationResult]) -> str:
        """
        検証結果のサマリーテキストを生成
        
        Args:
            results: 検証結果
        
        Returns:
            サマリーテキスト
        """
        errors = sum(1 for r in results if r.level == ValidationLevel.ERROR)
        warnings = sum(1 for r in results if r.level == ValidationLevel.WARNING)
        success = sum(1 for r in results if r.level == ValidationLevel.SUCCESS)
        
        if errors == 0 and warnings == 0:
            return f"✅ All validations passed ({success} checks)"
        elif errors == 0:
            return f"⚠️  Validation passed with {warnings} warnings"
        else:
            return f"❌ Validation failed with {errors} errors and {warnings} warnings"


# 使用例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    validator = ConfigValidatorAgent()
    
    # テスト用の設定
    test_config = {
        "browser": {
            "headless": False,
            "user_data_dir": "./user_data",
            "window_size": (1920, 1080)
        },
        "ai": {
            "provider": "openai",
            "model": "gpt-4",
            "api_key": "sk-test-key",
            "temperature": 0.7
        },
        "wordpress": {
            "url": "https://example.com",
            "username": "admin"
            # password が不足（エラー）
        },
        "system": {
            "run_mode": "local",
            "log_level": "INFO"
        }
    }
    
    # 設定をファイルに保存
    config_file = "test_config.json"
    with open(config_file, 'w') as f:
        json.dump(test_config, f, indent=2)
    
    # 設定ファイルを検証
    print("\n=== Validating Configuration File ===")
    results = validator.validate_config_file(config_file)
    
    for result in results:
        print(f"[{result.level.value.upper()}] {result.category}: {result.message}")
        if result.suggestion:
            print(f"  💡 {result.suggestion}")
    
    # 環境変数を検証
    print("\n=== Validating Environment Variables ===")
    env_results = validator.validate_environment_variables([
        "OPENAI_API_KEY",
        "WP_USERNAME",
        "WP_PASSWORD"
    ])
    
    for result in env_results:
        print(f"[{result.level.value.upper()}] {result.field}: {result.message}")
    
    # 依存関係を検証（実際のrequirements.txtがある場合）
    # dep_results = validator.validate_dependencies()
    
    # レポートを生成
    print("\n=== Validation Report ===")
    all_results = results + env_results
    report = validator.generate_validation_report(all_results)
    print(json.dumps(report["summary"], indent=2))
    
    # サマリー
    print("\n" + validator.get_summary(all_results))
    
    # 自動修正
    print("\n=== Auto-fixing Configuration ===")
    fixed_config, applied_fixes = validator.auto_fix_config(test_config, results)
    
    for fix in applied_fixes:
        print(f"✓ {fix}")
    
    # クリーンアップ
    os.remove(config_file)
