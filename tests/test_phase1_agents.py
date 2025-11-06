"""
Phase 1 エージェント統合テスト
v1.15.0 - 2025-11-06
"""

import asyncio
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.code_generation.code_generation_agent import CodeGenerationAgent
from agents.testing.testing_agent import TestingAgent
from agents.error_recovery.error_recovery_agent import ErrorRecoveryAgent


async def test_code_generation():
    """CodeGenerationAgent テスト"""
    print("\n" + "=" * 60)
    print("🧪 CodeGenerationAgent テスト")
    print("=" * 60)

    agent = CodeGenerationAgent()

    task_spec = {
        "title": "簡単な計算機能",
        "description": "2つの数値を足し算する関数を作成",
        "requirements": "add(a, b)という関数を実装してください",
    }

    result = await agent.generate_code(task_spec)

    print(f"\n生成結果:")
    print(f"  構文チェック: {'✅ 正常' if result['syntax_valid'] else '❌ エラー'}")
    print(f"  品質スコア: {result['quality_score']}/10")
    print(f"  関連ナレッジ: {result['related_knowledge']}件")

    if result["code"]:
        print(f"\n生成コード（最初の10行）:")
        lines = result["code"].split("\n")[:10]
        for line in lines:
            print(f"    {line}")

    # 統計情報
    stats = agent.get_statistics()
    print(f"\n統計:")
    print(f"  総生成数: {stats['total_generations']}")
    print(f"  成功率: {stats['success_rate']:.1f}%")
    print(f"  平均品質: {stats['average_quality_score']}/10")

    return result["syntax_valid"]


async def test_testing_agent():
    """TestingAgent テスト"""
    print("\n" + "=" * 60)
    print("🧪 TestingAgent テスト")
    print("=" * 60)

    agent = TestingAgent()

    # テスト用のサンプルコード
    sample_code = '''
def add(a: int, b: int) -> int:
    """2つの数値を足し算する関数"""
    return a + b

def subtract(a: int, b: int) -> int:
    """2つの数値を引き算する関数"""
    return a - b
'''

    # 構文テスト
    result = await agent.test_code(sample_code, "syntax")
    print(f"\n構文テスト結果:")
    print(f"  合否: {'✅ 合格' if result['passed'] else '❌ 不合格'}")
    print(f"  エラー数: {len(result['errors'])}")

    # スタイルテスト
    style_result = await agent.test_code(sample_code, "style")
    print(f"\nスタイルテスト結果:")
    print(f"  警告数: {len(style_result['warnings'])}")

    # テストケース自動生成
    test_cases = await agent.generate_tests(sample_code)
    print(f"\nテストケース生成:")
    print(f"  生成数: {len(test_cases)}個")

    # 統計情報
    stats = agent.get_statistics()
    print(f"\n統計:")
    print(f"  総テスト数: {stats['total_tests']}")
    print(f"  合格率: {stats['pass_rate']:.1f}%")

    return result["passed"]


async def test_error_recovery():
    """ErrorRecoveryAgent テスト"""
    print("\n" + "=" * 60)
    print("🧪 ErrorRecoveryAgent テスト")
    print("=" * 60)

    agent = ErrorRecoveryAgent()

    # テスト用のエラー
    test_errors = [
        (ImportError("No module named 'pandas'"), "依存関係エラー"),
        (SyntaxError("invalid syntax"), "構文エラー"),
        (AttributeError("'NoneType' object has no attribute 'get'"), "API使用エラー"),
    ]

    all_diagnosed = True

    for error, description in test_errors:
        print(f"\n--- {description} のテスト ---")

        # エラー診断
        diagnosis = await agent.diagnose_error(error)
        print(f"  エラータイプ: {diagnosis['error_type']}")
        print(f"  カテゴリ: {diagnosis['category']}")
        print(f"  信頼度: {diagnosis['confidence']}%")

        # 修復適用
        strategy = diagnosis["strategy"]
        fix_result = await agent.apply_fix(error, strategy)
        print(f"  修復結果: {'✅ 成功' if fix_result['success'] else '❌ 失敗'}")
        print(f"  実行アクション: {len(fix_result['actions_taken'])}個")

        if not diagnosis.get("error_type"):
            all_diagnosed = False

    # 統計情報
    stats = agent.get_statistics()
    print(f"\n統計:")
    print(f"  総修復試行: {stats['total_recoveries']}")
    print(f"  成功率: {stats['success_rate']:.1f}%")

    return all_diagnosed


async def main():
    """メインテスト実行"""
    print("\n" + "=" * 70)
    print("🚀 Phase 1 エージェント統合テスト開始")
    print("=" * 70)

    results = []

    # 各エージェントのテスト実行
    try:
        result1 = await test_code_generation()
        results.append(("CodeGenerationAgent", result1))
    except Exception as e:
        print(f"❌ CodeGenerationAgent テスト失敗: {e}")
        results.append(("CodeGenerationAgent", False))

    try:
        result2 = await test_testing_agent()
        results.append(("TestingAgent", result2))
    except Exception as e:
        print(f"❌ TestingAgent テスト失敗: {e}")
        results.append(("TestingAgent", False))

    try:
        result3 = await test_error_recovery()
        results.append(("ErrorRecoveryAgent", result3))
    except Exception as e:
        print(f"❌ ErrorRecoveryAgent テスト失敗: {e}")
        results.append(("ErrorRecoveryAgent", False))

    # 総合結果
    print("\n" + "=" * 70)
    print("📊 テスト結果サマリー")
    print("=" * 70)

    for agent_name, passed in results:
        status = "✅ 成功" if passed else "❌ 失敗"
        print(f"{status}: {agent_name}")

    total_passed = sum(1 for _, p in results if p)
    success_rate = (total_passed / len(results) * 100) if results else 0

    print(f"\n総合成功率: {success_rate:.1f}% ({total_passed}/{len(results)})")

    if success_rate == 100:
        print("\n🎉 Phase 1 完了: すべてのエージェントが正常に動作しています")
    else:
        print("\n⚠️ 一部のエージェントに問題があります")

    return success_rate == 100


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
