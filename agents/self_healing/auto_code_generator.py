#!/usr/bin/env python3
"""
AutoCodeGenerator: 自動コード生成器

ナレッジベースから学習した修正パターンを基に、
修正コードを自動生成する。
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re
import json


class CodeTemplate:
    """コードテンプレート"""

    def __init__(
        self,
        template_id: str,
        name: str,
        template_code: str,
        parameters: List[str],
        description: str,
        applicable_errors: List[str],
    ):
        self.template_id = template_id
        self.name = name
        self.template_code = template_code
        self.parameters = parameters
        self.description = description
        self.applicable_errors = applicable_errors

    def render(self, **kwargs) -> str:
        """テンプレートをレンダリング"""
        code = self.template_code

        # パラメータを置換
        for param, value in kwargs.items():
            placeholder = f"{{{param}}}"
            if placeholder in code:
                code = code.replace(placeholder, str(value))

        return code

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "template_id": self.template_id,
            "name": self.name,
            "template_code": self.template_code,
            "parameters": self.parameters,
            "description": self.description,
            "applicable_errors": self.applicable_errors,
        }


class GeneratedCode:
    """生成されたコード"""

    def __init__(
        self,
        code_id: str,
        source_template: str,
        generated_code: str,
        target_file: str,
        confidence: float,
        explanation: str,
        test_required: bool = True,
    ):
        self.code_id = code_id
        self.source_template = source_template
        self.generated_code = generated_code
        self.target_file = target_file
        self.confidence = confidence
        self.explanation = explanation
        self.test_required = test_required
        self.created_at = datetime.now()

        # テスト結果
        self.tested = False
        self.test_passed = False
        self.test_result: Optional[Dict[str, Any]] = None

    def mark_tested(self, passed: bool, result: Dict[str, Any]):
        """テスト結果を記録"""
        self.tested = True
        self.test_passed = passed
        self.test_result = result

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "code_id": self.code_id,
            "source_template": self.source_template,
            "generated_code": self.generated_code,
            "target_file": self.target_file,
            "confidence": self.confidence,
            "explanation": self.explanation,
            "test_required": self.test_required,
            "tested": self.tested,
            "test_passed": self.test_passed,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


class AutoCodeGenerator:
    """自動コード生成器"""

    def __init__(self, kb_manager=None):
        """
        初期化

        Args:
            kb_manager: KnowledgeBaseManager
        """
        self.kb_manager = kb_manager

        # ビルトインテンプレート
        self.templates = self._load_builtin_templates()

        print("✅ AutoCodeGenerator初期化完了")
        print(f"   ビルトインテンプレート: {len(self.templates)}個")

    def _load_builtin_templates(self) -> List[CodeTemplate]:
        """ビルトインテンプレートを読み込み"""
        templates = []

        # 1. タイムアウト延長テンプレート
        templates.append(
            CodeTemplate(
                template_id="TIMEOUT_EXTEND",
                name="タイムアウト延長",
                template_code="""
# タイムアウトを{timeout}秒に延長
config['{config_key}'] = {timeout}

# タイムアウト処理の改善
try:
    result = await asyncio.wait_for(
        {function_call},
        timeout={timeout}
    )
except asyncio.TimeoutError:
    print(f"タイムアウト({timeout}秒)が発生しました")
    # フォールバック処理
    result = None
""",
                parameters=["timeout", "config_key", "function_call"],
                description="タイムアウトを延長し、エラーハンドリングを追加",
                applicable_errors=["TimeoutError", "asyncio.TimeoutError"],
            )
        )

        # 2. リトライロジック追加テンプレート
        templates.append(
            CodeTemplate(
                template_id="ADD_RETRY",
                name="リトライロジック追加",
                template_code="""
# リトライロジック追加
max_retries = {max_retries}
retry_delay = {retry_delay}

for attempt in range(max_retries):
    try:
        result = {function_call}
        break  # 成功したら抜ける
    except {error_type} as e:
        if attempt < max_retries - 1:
            print(f"リトライ {attempt + 1}/{max_retries}: {{e}}")
            await asyncio.sleep(retry_delay * (attempt + 1))
        else:
            print(f"最大リトライ回数に達しました")
            raise
""",
                parameters=["max_retries", "retry_delay", "function_call", "error_type"],
                description="指数バックオフを使用したリトライロジック",
                applicable_errors=["NetworkError", "ConnectionError", "APIError"],
            )
        )

        # 3. エラーハンドリング追加テンプレート
        templates.append(
            CodeTemplate(
                template_id="ADD_ERROR_HANDLING",
                name="エラーハンドリング追加",
                template_code="""
# 堅牢なエラーハンドリング
try:
    {function_call}
except {error_type} as e:
    print(f"エラー発生: {{e}}")
    
    # エラーをログに記録
    logger.error(f"{error_type}: {{e}}")
    
    # {fallback_description}
    {fallback_code}
except Exception as e:
    print(f"予期しないエラー: {{e}}")
    logger.exception("Unexpected error")
    raise
""",
                parameters=["function_call", "error_type", "fallback_description", "fallback_code"],
                description="包括的なエラーハンドリングとフォールバック",
                applicable_errors=["Exception", "RuntimeError"],
            )
        )

        # 4. レート制限対応テンプレート
        templates.append(
            CodeTemplate(
                template_id="RATE_LIMIT_HANDLING",
                name="レート制限対応",
                template_code="""
# レート制限対応
from datetime import datetime, timedelta
import asyncio

class RateLimiter:
    def __init__(self, max_calls={max_calls}, time_window={time_window}):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    async def wait_if_needed(self):
        now = datetime.now()
        
        # 古い呼び出しを削除
        self.calls = [t for t in self.calls if now - t < timedelta(seconds=self.time_window)]
        
        # 制限に達している場合は待機
        if len(self.calls) >= self.max_calls:
            wait_time = (self.calls[0] + timedelta(seconds=self.time_window) - now).total_seconds()
            if wait_time > 0:
                print(f"レート制限: {{wait_time:.1f}}秒待機")
                await asyncio.sleep(wait_time + 0.1)
        
        self.calls.append(now)

rate_limiter = RateLimiter(max_calls={max_calls}, time_window={time_window})
await rate_limiter.wait_if_needed()
{function_call}
""",
                parameters=["max_calls", "time_window", "function_call"],
                description="API呼び出しのレート制限対応",
                applicable_errors=["RateLimitError", "QuotaExceededError"],
            )
        )

        # 5. 設定値調整テンプレート
        templates.append(
            CodeTemplate(
                template_id="CONFIG_ADJUSTMENT",
                name="設定値調整",
                template_code="""
# 設定値の調整
config.update({{
    '{config_key_1}': {value_1},
    '{config_key_2}': {value_2},
}})

print(f"設定を調整しました:")
print(f"  {config_key_1}: {{config['{config_key_1}']}}")
print(f"  {config_key_2}: {{config['{config_key_2}']}}")

# 調整後の実行
{function_call}
""",
                parameters=["config_key_1", "value_1", "config_key_2", "value_2", "function_call"],
                description="設定値を最適化",
                applicable_errors=["ConfigurationError", "ParameterError"],
            )
        )

        return templates

    def find_applicable_templates(self, error_type: str, context: Dict[str, Any]) -> List[CodeTemplate]:
        """
        適用可能なテンプレートを検索

        Args:
            error_type: エラータイプ
            context: コンテキスト情報

        Returns:
            適用可能なテンプレートのリスト
        """
        applicable = []

        for template in self.templates:
            # エラータイプが一致するか
            if any(err in error_type or error_type in err for err in template.applicable_errors):
                applicable.append(template)

        return applicable

    def generate_code_from_knowledge(
        self, error_type: str, error_message: str, context: Dict[str, Any]
    ) -> List[GeneratedCode]:
        """
        ナレッジベースから修正コードを生成

        Args:
            error_type: エラータイプ
            error_message: エラーメッセージ
            context: コンテキスト情報

        Returns:
            生成されたコードのリスト
        """
        print("\n" + "=" * 70)
        print("🔧 コード生成開始")
        print("=" * 70)
        print(f"エラータイプ: {error_type}")
        print(f"エラーメッセージ: {error_message[:100]}...")

        generated_codes = []

        # 1. ナレッジベースから修正レシピを検索
        if self.kb_manager:
            fix_recipes = self.kb_manager.search_similar_knowledge(
                {"knowledge_type": "fix_recipe", "error_type": error_type}, limit=3
            )

            print(f"\n📚 修正レシピ発見: {len(fix_recipes)}件")

            # ナレッジベースからコード生成
            for recipe in fix_recipes:
                code = self._generate_from_recipe(recipe, context)
                if code:
                    generated_codes.append(code)

        # 2. テンプレートからコード生成
        applicable_templates = self.find_applicable_templates(error_type, context)

        print(f"🎨 適用可能なテンプレート: {len(applicable_templates)}件")

        for template in applicable_templates:
            code = self._generate_from_template(template, error_type, context)
            if code:
                generated_codes.append(code)

        # 信頼度順にソート
        generated_codes.sort(key=lambda c: c.confidence, reverse=True)

        print(f"\n✅ {len(generated_codes)}件のコードを生成")

        return generated_codes

    def _generate_from_recipe(self, recipe: Dict[str, Any], context: Dict[str, Any]) -> Optional[GeneratedCode]:
        """修正レシピからコード生成"""
        try:
            code_snippet = recipe.get("code_snippet", "")

            if not code_snippet:
                return None

            # 信頼度計算
            effectiveness = float(recipe.get("effectiveness_score", 0)) / 100
            usage_count = int(recipe.get("usage_count", 0))

            confidence = min(effectiveness + (usage_count / 20), 1.0)

            code_id = f"RECIPE_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            return GeneratedCode(
                code_id=code_id,
                source_template=recipe.get("pattern_name", "Unknown"),
                generated_code=code_snippet,
                target_file=context.get("target_file", "unknown.py"),
                confidence=confidence,
                explanation=recipe.get("pattern_description", "ナレッジベースからの修正"),
                test_required=True,
            )

        except Exception as e:
            print(f"⚠️ レシピからのコード生成エラー: {e}")
            return None

    def _generate_from_template(
        self, template: CodeTemplate, error_type: str, context: Dict[str, Any]
    ) -> Optional[GeneratedCode]:
        """テンプレートからコード生成"""
        try:
            # パラメータを推測
            params = self._infer_parameters(template, error_type, context)

            # コード生成
            code = template.render(**params)

            # 信頼度計算（テンプレートベースは中程度）
            confidence = 0.6

            code_id = f"TEMPLATE_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            return GeneratedCode(
                code_id=code_id,
                source_template=template.name,
                generated_code=code,
                target_file=context.get("target_file", "unknown.py"),
                confidence=confidence,
                explanation=f"テンプレート「{template.name}」を適用: {template.description}",
                test_required=True,
            )

        except Exception as e:
            print(f"⚠️ テンプレートからのコード生成エラー: {e}")
            return None

    def _infer_parameters(self, template: CodeTemplate, error_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """テンプレートのパラメータを推測"""
        params = {}

        # テンプレートIDに応じたデフォルト値
        if template.template_id == "TIMEOUT_EXTEND":
            params["timeout"] = 60
            params["config_key"] = "TIMEOUT"
            params["function_call"] = "task_function()"

        elif template.template_id == "ADD_RETRY":
            params["max_retries"] = 3
            params["retry_delay"] = 2
            params["function_call"] = "task_function()"
            params["error_type"] = error_type

        elif template.template_id == "ADD_ERROR_HANDLING":
            params["function_call"] = "task_function()"
            params["error_type"] = error_type
            params["fallback_description"] = "デフォルト値を返す"
            params["fallback_code"] = "return None"

        elif template.template_id == "RATE_LIMIT_HANDLING":
            params["max_calls"] = 50
            params["time_window"] = 60
            params["function_call"] = "api_call()"

        elif template.template_id == "CONFIG_ADJUSTMENT":
            params["config_key_1"] = "timeout"
            params["value_1"] = 60
            params["config_key_2"] = "max_retries"
            params["value_2"] = 3
            params["function_call"] = "task_function()"

        # コンテキストからパラメータを上書き
        if "parameters" in context:
            params.update(context["parameters"])

        return params

    def format_code_report(self, generated_codes: List[GeneratedCode]) -> str:
        """生成コードレポートをフォーマット"""
        report = []
        report.append("=" * 70)
        report.append("🔧 自動生成コードレポート")
        report.append("=" * 70)
        report.append(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"生成コード数: {len(generated_codes)}件")
        report.append("")

        for i, code in enumerate(generated_codes, 1):
            report.append(f"\n{i}. {code.source_template}")
            report.append("-" * 70)
            report.append(f"信頼度: {code.confidence:.0%}")
            report.append(f"対象ファイル: {code.target_file}")
            report.append(f"\n説明:")
            report.append(f"  {code.explanation}")
            report.append(f"\n生成コード:")
            report.append("```python")
            report.append(code.generated_code)
            report.append("```")

            if code.test_required:
                report.append("\n⚠️ テスト必須")

        report.append("\n" + "=" * 70)

        return "\n".join(report)


if __name__ == "__main__":
    # 簡易テスト
    generator = AutoCodeGenerator()
    print(f"テンプレート数: {len(generator.templates)}")
