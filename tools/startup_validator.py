#!/usr/bin/env python3
"""
システム起動時の自動検証ツール
すべてのコンポーネントが正常に動作するか確認
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def run_startup_validation():
    """起動時の検証を実行"""
    print("🔧 システム起動検証を開始...")

    validation_steps = [
        ("スプレッドシート接続", validate_sheets_connection),
        ("シート整合性", validate_sheets_integrity),
        ("テンプレートシステム", validate_templates),
        ("AI生成システム", validate_ai_generation),
        ("ナレッジベース", validate_knowledge_base),
    ]

    results = []
    for step_name, validator_func in validation_steps:
        print(f"  🔍 {step_name}...")
        try:
            success, message = validator_func()
            results.append((step_name, success, message))
        except Exception as e:
            results.append((step_name, False, f"検証エラー: {e}"))

    # 結果表示
    print("\n📊 起動検証結果:")
    print("=" * 50)

    all_passed = True
    for step_name, success, message in results:
        status_icon = "✅" if success else "❌"
        print(f"  {status_icon} {step_name}: {message}")
        if not success:
            all_passed = False

    print("=" * 50)

    if all_passed:
        print("🎉 すべての検証が成功しました - システム正常起動")
        return True
    else:
        print("⚠️ 一部の検証が失敗しました - 修正が必要です")
        return False


def validate_sheets_connection():
    """スプレッドシート接続検証"""
    try:
        from browser_control.sheets_manager import GoogleSheetsManager

        sheets = GoogleSheetsManager()

        # 簡単な読み取りテスト
        test_data = sheets.read_range("project_goal!A1:Z1")
        return True, "接続正常"
    except Exception as e:
        return False, f"接続エラー: {e}"


def validate_sheets_integrity():
    """シート整合性検証"""
    try:
        from tools.sheet_validator import SheetValidator

        validator = SheetValidator()
        is_valid = validator.validate_all_sheets()
        return is_valid, "整合性確認完了"
    except Exception as e:
        return False, f"整合性検証エラー: {e}"


def validate_templates():
    """テンプレートシステム検証"""
    try:
        templates_dir = Path("/workspaces/gemini_AI_Agent/agents/templates")
        template_files = list(templates_dir.rglob("*.py"))

        if len(template_files) >= 6:  # 主要テンプレート数
            return True, f"{len(template_files)}個のテンプレート確認"
        else:
            return False, f"テンプレート数不足: {len(template_files)}個"
    except Exception as e:
        return False, f"テンプレート検証エラー: {e}"


def validate_ai_generation():
    """AI生成システム検証"""
    try:
        from agents.ai_driven_generator import AICodeGenerator

        generator = AICodeGenerator()
        test_result = generator.generate_code("テスト用の簡単な関数")

        if test_result["quality_score"] > 0:
            return True, "AI生成器動作正常"
        else:
            return False, "AI生成器の品質スコアが0"
    except Exception as e:
        return False, f"AI生成検証エラー: {e}"


def validate_knowledge_base():
    """ナレッジベース検証"""
    try:
        knowledge_path = Path("/workspaces/gemini_AI_Agent/knowledge_system/database/knowledge.db")
        if knowledge_path.exists():
            return True, "ナレッジベース存在確認"
        else:
            return False, "ナレッジベースが存在しません"
    except Exception as e:
        return False, f"ナレッジベース検証エラー: {e}"


if __name__ == "__main__":
    success = run_startup_validation()
    sys.exit(0 if success else 1)
