"""
既存システムへのナレッジ機能統合
既存コードを変更せずに機能追加 - 安全版
"""

import sys
from typing import Any, Optional

# プロジェクトルートをパスに追加
sys.path.append("/workspaces/gemini_AI_Agent")

try:
    from agents.knowledge_enhancer import KnowledgeEnhancer

    KNOWLEDGE_ENHANCER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ ナレッジエンハンサー利用不可: {e}")
    KNOWLEDGE_ENHANCER_AVAILABLE = False


class SafeKnowledgeIntegration:
    """
    既存システムに安全にナレッジ機能を追加するクラス
    既存のクラスを継承せず、コンポジションで機能追加
    """

    def __init__(self, target_instance: Optional[Any] = None):
        self.target_instance = target_instance

        if KNOWLEDGE_ENHANCER_AVAILABLE:
            self.enhancer = KnowledgeEnhancer()
            self.integration_enabled = True
            print("✅ セーフナレッジ統合を初期化")
        else:
            self.enhancer = None
            self.integration_enabled = False
            print("⚠️ セーフナレッジ統合: 簡易モード")

    def wrap_execute_task(self, original_execute):
        """execute_taskメソッドを安全にラップ"""
        if not self.integration_enabled or not self.enhancer:
            return original_execute

        def enhanced_execute(task_data, *args, **kwargs):
            try:
                # 実行前：ナレッジ参照
                task_desc = task_data.get("description", "")
                if task_desc:
                    knowledge_enhancement = self.enhancer.enhance_task_with_knowledge(task_desc)

                    if knowledge_enhancement["relevant_knowledge_count"] > 0:
                        print(
                            f"📚 関連ナレッジ: {knowledge_enhancement['relevant_knowledge_count']}件"
                        )

                    if knowledge_enhancement["suggestions"]:
                        for suggestion in knowledge_enhancement["suggestions"]:
                            print(f"💡 {suggestion}")

                    if knowledge_enhancement["warnings"]:
                        for warning in knowledge_enhancement["warnings"]:
                            print(f"⚠️ {warning}")

            except Exception as e:
                print(f"⚠️ ナレッジ参照エラー（実行継続）: {e}")

            # 元のメソッド実行
            result = original_execute(task_data, *args, **kwargs)

            try:
                # 実行後：ナレッジ保存
                if result and isinstance(result, dict):
                    save_success = self.enhancer.save_task_knowledge(task_data, result)
                    if save_success:
                        print("💾 実行結果をナレッジベースに保存")
            except Exception as e:
                print(f"⚠️ ナレッジ保存エラー（実行継続）: {e}")

            return result

        return enhanced_execute

    def wrap_decompose_goal(self, original_decompose):
        """decompose_goal_to_tasksメソッドを安全にラップ"""
        if not self.integration_enabled or not self.enhancer:
            return original_decompose

        def enhanced_decompose(goal_data, *args, **kwargs):
            try:
                # ゴール分解前：関連ナレッジ参照
                goal_desc = goal_data.get("goal_description", "")
                if goal_desc:
                    knowledge_enhancement = self.enhancer.enhance_task_with_knowledge(goal_desc)

                    if knowledge_enhancement["relevant_knowledge_count"] > 0:
                        print(
                            f"🎯 ゴール関連ナレッジ: {knowledge_enhancement['relevant_knowledge_count']}件"
                        )

            except Exception as e:
                print(f"⚠️ ゴールナレッジ参照エラー（実行継続）: {e}")

            # 元のメソッド実行
            return original_decompose(goal_data, *args, **kwargs)

        return enhanced_decompose


# 既存システム用簡易統合関数
def safely_integrate_knowledge(instance):
    """
    既存インスタンスに安全にナレッジ機能を統合
    """
    integration = SafeKnowledgeIntegration(instance)

    if not integration.integration_enabled:
        print("⚠️ ナレッジ統合: 簡易モード（機能制限）")
        return instance

    try:
        # execute_taskメソッドのラップ
        if hasattr(instance, "execute_task"):
            original_method = instance.execute_task
            instance.execute_task = integration.wrap_execute_task(original_method)
            print("✅ execute_taskをナレッジ統合")

        # decompose_goal_to_tasksメソッドのラップ
        if hasattr(instance, "decompose_goal_to_tasks"):
            original_method = instance.decompose_goal_to_tasks
            instance.decompose_goal_to_tasks = integration.wrap_decompose_goal(original_method)
            print("✅ decompose_goal_to_tasksをナレッジ統合")

    except Exception as e:
        print(f"⚠️ ナレッジ統合エラー（実行継続）: {e}")

    return instance


# 使用例
if __name__ == "__main__":
    print("🔧 セーフナレッジ統合テスト")

    # テスト用のダミークラス
    class TestAgent:
        def execute_task(self, task_data):
            print(f"実行: {task_data.get('description')}")
            return {"status": "completed", "output_summary": "テスト成功"}

        def decompose_goal_to_tasks(self, goal_data):
            print(f"分解: {goal_data.get('goal_description')}")
            return ["task1", "task2"]

    # 統合テスト
    test_agent = TestAgent()
    enhanced_agent = safely_integrate_knowledge(test_agent)

    # テスト実行
    test_task = {"description": "ファイル読み込み修正"}
    result = enhanced_agent.execute_task(test_task)
    print(f"実行結果: {result}")
