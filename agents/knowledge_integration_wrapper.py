"""
既存システムへのナレッジ機能統合ラッパー
既存コードを変更せずに機能追加
"""

from knowledge_enhancer import KnowledgeEnhancer


class KnowledgeIntegrationWrapper:
    """
    既存システムにナレッジ機能を追加するラッパー
    既存のクラスを継承せず、コンポジションで機能追加
    """

    def __init__(self, target_instance):
        self.target_instance = target_instance
        self.enhancer = KnowledgeEnhancer()
        self._original_methods = {}

        # 既存インスタンスを強化
        self._enhance_existing_instance()

    def _enhance_existing_instance(self):
        """既存インスタンスにナレッジ機能を追加"""
        try:
            # メソッドの追加
            if hasattr(self.target_instance, "execute_task"):
                self._wrap_execute_task()

            if hasattr(self.target_instance, "decompose_goal_to_tasks"):
                self._wrap_decompose_goal()

            print(f"✅ インスタンス強化完了: {type(self.target_instance).__name__}")

        except Exception as e:
            print(f"⚠️ インスタンス強化エラー: {e}")

    def _wrap_execute_task(self):
        """execute_taskメソッドをラップ"""
        original_execute = self.target_instance.execute_task

        def enhanced_execute(task_data, *args, **kwargs):
            # 実行前：ナレッジ参照
            task_desc = task_data.get("description", "")
            knowledge_enhancement = self.enhancer.enhance_task_with_knowledge(task_desc)

            print(f"📚 タスク実行前ナレッジ参照:")
            print(f"   関連ナレッジ: {knowledge_enhancement['relevant_knowledge_count']}件")
            if knowledge_enhancement["suggestions"]:
                print(f"   提案: {knowledge_enhancement['suggestions']}")
            if knowledge_enhancement["warnings"]:
                print(f"   警告: {knowledge_enhancement['warnings']}")

            # 元のメソッド実行
            result = original_execute(task_data, *args, **kwargs)

            # 実行後：ナレッジ保存
            if result and isinstance(result, dict):
                save_success = self.enhancer.save_task_knowledge(task_data, result)
                if save_success:
                    print("💾 実行結果をナレッジベースに保存")

            return result

        # メソッド置き換え
        self.target_instance.execute_task = enhanced_execute
        self._original_methods["execute_task"] = original_execute

    def _wrap_decompose_goal(self):
        """decompose_goal_to_tasksメソッドをラップ"""
        original_decompose = self.target_instance.decompose_goal_to_tasks

        def enhanced_decompose(goal_data, *args, **kwargs):
            # ゴール分解前：関連ナレッジ参照
            goal_desc = goal_data.get("goal_description", "")
            knowledge_enhancement = self.enhancer.enhance_task_with_knowledge(goal_desc)

            print(f"�� ゴール分解前ナレッジ参照:")
            print(f"   関連ナレッジ: {knowledge_enhancement['relevant_knowledge_count']}件")

            # 元のメソッド実行
            result = original_decompose(goal_data, *args, **kwargs)

            return result

        # メソッド置き換え
        self.target_instance.decompose_goal_to_tasks = enhanced_decompose
        self._original_methods["decompose_goal_to_tasks"] = original_decompose


# 既存システム用簡易統合関数
def integrate_knowledge_to_existing_system():
    """
    既存システム全体にナレッジ機能を統合
    既存コードを変更せずに使用可能
    """
    integration_points = [
        "agents.complete_engine_ultimate.CompleteEngineUltimate",
        "task_executor.task_executor.TaskExecutor",
        "core_agents.integrated_controller_fixed.IntegratedControllerFixed",
        "agents.autonomous_engine.AutonomousEngine",
    ]

    integrated_instances = []

    for point in integration_points:
        try:
            module_path, class_name = point.rsplit(".", 1)
            module = __import__(module_path, fromlist=[class_name])
            getattr(module, class_name)

            # 既存のインスタンスを取得する方法はコンテキスト依存
            # 実際の使用時は適切なインスタンスを渡す
            print(f"✅ 統合準備完了: {class_name}")
            integrated_instances.append(class_name)

        except Exception as e:
            print(f"⚠️ 統合準備失敗 {point}: {e}")

    return integrated_instances


# 使用例
if __name__ == "__main__":
    print("🔧 ナレッジ統合ラッパー動作テスト")

    # 統合ポイント確認
    integrated = integrate_knowledge_to_existing_system()
    print(f"統合可能クラス: {integrated}")

    # エンハンサー単体テスト
    enhancer = KnowledgeEnhancer()
    test_result = enhancer.enhance_task_with_knowledge("テストタスク")
    print(f"エンハンサー動作: {test_result['relevant_knowledge_count']}件の関連ナレッジ")
