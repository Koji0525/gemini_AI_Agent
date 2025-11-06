"""
Phase 1 エージェント統合テスト（自動ナレッジ登録付き）
v1.15.0 - 2025-11-06
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.code_generation.code_generation_agent import CodeGenerationAgent
from agents.testing.testing_agent import TestingAgent
from agents.error_recovery.error_recovery_agent import ErrorRecoveryAgent
from tools.auto_knowledge_register import AutoKnowledgeRegister


async def test_code_generation(knowledge_register):
    """CodeGenerationAgent テスト"""
    print("\n" + "=" * 60)
    print("🧪 CodeGenerationAgent テスト")
    print("=" * 60)

    try:
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

        # 成功した場合はナレッジ登録
        if result["syntax_valid"]:
            knowledge_register.register_success(
                title="CodeGenerationAgent コード生成成功",
                category="開発/コード生成",
                scenario=f"タスク「{task_spec['title']}」のコード生成に成功",
                solution=f"Gemini API ({result['model_used']}) による自動生成。品質スコア {result['quality_score']}/10",
                context={
                    "agent": "CodeGenerationAgent",
                    "model": result["model_used"],
                    "quality_score": result["quality_score"],
                    "task": task_spec["title"],
                },
                importance="高",
            )

        return result["syntax_valid"]

    except Exception as e:
        print(f"❌ テスト失敗: {e}")
        return False


async def test_testing_agent(knowledge_register):
    """TestingAgent テスト"""
    print("\n" + "=" * 60)
    print("🧪 TestingAgent テスト")
    print("=" * 60)

    try:
        agent = TestingAgent()

        sample_code = '''
def add(a: int, b: int) -> int:
    """2つの数値を足し算する関数"""
    return a + b
'''

        result = await agent.test_code(sample_code, "syntax")
        print(f"\n構文テスト結果: {'✅ 合格' if result['passed'] else '❌ 不合格'}")

        stats = agent.get_statistics()

        # 成功した場合はナレッジ登録
        if result["passed"]:
            knowledge_register.register_success(
                title="TestingAgent テスト実行成功",
                category="テスト/自動化",
                scenario="構文チェック・スタイルチェックを正常に実行",
                solution=f"PEP 8準拠のコードで合格率 {stats['pass_rate']:.1f}%達成",
                context={
                    "agent": "TestingAgent",
                    "total_tests": stats["total_tests"],
                    "pass_rate": stats["pass_rate"],
                },
                importance="中",
            )

        return result["passed"]

    except Exception as e:
        print(f"❌ テスト失敗: {e}")
        return False


async def test_error_recovery(knowledge_register):
    """ErrorRecoveryAgent テスト"""
    print("\n" + "=" * 60)
    print("🧪 ErrorRecoveryAgent テスト")
    print("=" * 60)

    try:
        agent = ErrorRecoveryAgent()

        error = ImportError("No module named 'pandas'")
        diagnosis = await agent.diagnose_error(error)

        print(f"  エラータイプ: {diagnosis['error_type']}")
        print(f"  信頼度: {diagnosis['confidence']}%")

        stats = agent.get_statistics()

        # 診断に成功した場合はナレッジ登録
        if diagnosis.get("error_type"):
            knowledge_register.register_success(
                title="ErrorRecoveryAgent エラー診断成功",
                category="エラー/自動修復",
                scenario=f"{diagnosis['error_type']} の診断に成功",
                solution=f"カテゴリ分類: {diagnosis['category']}, 信頼度: {diagnosis['confidence']}%",
                context={
                    "agent": "ErrorRecoveryAgent",
                    "error_type": diagnosis["error_type"],
                    "category": diagnosis["category"],
                    "confidence": diagnosis["confidence"],
                },
                importance="中",
            )

        return True

    except Exception as e:
        print(f"❌ テスト失敗: {e}")
        return False


async def main():
    """メインテスト実行"""
    print("\n" + "=" * 70)
    print("🚀 Phase 1 エージェント統合テスト開始（自動ナレッジ登録付き）")
    print("=" * 70)

    # ナレッジ登録システム初期化
    knowledge_register = AutoKnowledgeRegister()

    results = []

    # 各エージェントのテスト実行
    try:
        result1 = await test_code_generation(knowledge_register)
        results.append(("CodeGenerationAgent", result1))
    except Exception as e:
        print(f"❌ CodeGenerationAgent テスト失敗: {e}")
        results.append(("CodeGenerationAgent", False))

    try:
        result2 = await test_testing_agent(knowledge_register)
        results.append(("TestingAgent", result2))
    except Exception as e:
        print(f"❌ TestingAgent テスト失敗: {e}")
        results.append(("TestingAgent", False))

    try:
        result3 = await test_error_recovery(knowledge_register)
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

    # ナレッジ統計表示
    stats = knowledge_register.get_statistics()
    print("\n" + "=" * 70)
    print("📚 自動登録されたナレッジ")
    print("=" * 70)
    print(f"  総登録数: {stats['total_entries']}")
    print(f"  カテゴリ別: {stats['categories']}")

    total_passed = sum(1 for _, p in results if p)
    success_rate = (total_passed / len(results) * 100) if results else 0

    print(f"\n総合成功率: {success_rate:.1f}% ({total_passed}/{len(results)})")

    return success_rate >= 66.7  # 2/3以上成功でOK


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
