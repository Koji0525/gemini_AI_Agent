#!/usr/bin/env python3
"""
エージェント連携状況テストスクリプト
"""

import os
import sys
import importlib.util
from pathlib import Path


def check_agent_module(agent_name, module_path):
    """エージェントモジュールの存在とインポートを確認"""
    print(f"\n🔍 {agent_name} の確認...")

    if not os.path.exists(module_path):
        print(f"  ❌ ファイル不存在: {module_path}")
        return False

    try:
        # モジュールを動的にインポート
        spec = importlib.util.spec_from_file_location(agent_name.lower(), module_path)
        if spec is None:
            print(f"  ❌ モジュール仕様の取得失敗")
            return False

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"  ✅ インポート成功")

        # 主要クラスの存在確認
        class_mapping = {
            "retry_manager": ["RetryManager"],
            "error_classifier": ["ErrorClassifier"],
            "self_healing_orchestrator": ["SelfHealingOrchestrator"],
            "decision_support_system": ["DecisionSupportSystem"],
            "similarity_search_engine": ["SimilaritySearchEngine"],
            "knowledge_base_manager": ["KnowledgeBaseManager"],
            "intelligent_feedback_generator": ["IntelligentFeedbackGenerator"],
            "auto_code_generator": ["AutoCodeGenerator"],
        }

        module_name = os.path.basename(module_path).replace(".py", "")
        if module_name in class_mapping:
            for class_name in class_mapping[module_name]:
                if hasattr(module, class_name):
                    print(f"  ✅ クラス存在: {class_name}")
                    # 簡単なインスタンス化テスト
                    try:
                        if class_name == "RetryManager":
                            instance = module.RetryManager(max_retries=3)
                            print(f"  ✅ {class_name} インスタンス化成功")
                        elif class_name == "ErrorClassifier":
                            instance = module.ErrorClassifier()
                            print(f"  ✅ {class_name} インスタンス化成功")
                    except Exception as e:
                        print(f"  ⚠️ {class_name} インスタンス化エラー: {e}")
                else:
                    print(f"  ❌ クラス不存在: {class_name}")

        return True

    except Exception as e:
        print(f"  ❌ インポートエラー: {e}")
        return False


def check_integration_points():
    """エージェント間の連携ポイントを確認"""
    print(f"\n🎯 エージェント連携ポイント確認...")

    integration_points = [
        # Phase 5: 自己修復基盤
        {
            "from": "TaskExecutor",
            "to": "SelfHealingOrchestrator",
            "description": "タスク実行時の自己修復ラップ",
            "files": ["scripts/task_executor.py", "agents/self_healing/core/self_healing_orchestrator.py"],
        },
        {
            "from": "SelfHealingOrchestrator",
            "to": "RetryManager",
            "description": "エラー発生時の適応的リトライ",
            "files": [
                "agents/self_healing/core/self_healing_orchestrator.py",
                "agents/self_healing/core/retry_manager.py",
            ],
        },
        {
            "from": "RetryManager",
            "to": "ErrorClassifier",
            "description": "エラー分類に基づくリトライ戦略",
            "files": ["agents/self_healing/core/retry_manager.py", "agents/self_healing/utils/error_classifier.py"],
        },
        # Phase 9: 高度な判断支援
        {
            "from": "DecisionSupportSystem",
            "to": "SimilaritySearchEngine",
            "description": "類似ケース検索による判断支援",
            "files": [
                "agents/decision_support/decision_support_system.py",
                "agents/knowledge_base/similarity_search_engine.py",
            ],
        },
        {
            "from": "DecisionSupportSystem",
            "to": "KnowledgeBaseManager",
            "description": "ナレッジベースからのパターン抽出",
            "files": [
                "agents/decision_support/decision_support_system.py",
                "agents/knowledge_base/knowledge_base_manager.py",
            ],
        },
    ]

    for point in integration_points:
        print(f"\n🔗 {point['from']} → {point['to']}")
        print(f"   📝 {point['description']}")

        from_exists = os.path.exists(point["files"][0])
        to_exists = os.path.exists(point["files"][1])

        if from_exists and to_exists:
            print(f"   ✅ 連携可能: 両ファイルが存在")

            # 実際のインポート関係を確認
            try:
                with open(point["files"][0], "r") as f:
                    content = f.read()
                    if point["to"].lower().replace("_", "") in content.lower():
                        print(f"   ✅ 参照確認: {point['files'][0]} が {point['to']} を参照")
                    else:
                        print(f"   ⚠️  参照未確認: 明示的な参照なし")
            except Exception as e:
                print(f"   ❌ ファイル読み込みエラー: {e}")
        else:
            print(f"   ❌ 連携不能: ファイル不足")
            if not from_exists:
                print(f"     - 不足: {point['files'][0]}")
            if not to_exists:
                print(f"     - 不足: {point['files'][1]}")


def main():
    print("=" * 80)
    print("🤖 自立型修復エージェントシステム 連携状況分析")
    print("=" * 80)

    # 各エージェントの基本状態を確認
    agents_to_check = [
        ("RetryManager", "agents/self_healing/core/retry_manager.py"),
        ("ErrorClassifier", "agents/self_healing/utils/error_classifier.py"),
        ("SelfHealingOrchestrator", "agents/self_healing/core/self_healing_orchestrator.py"),
        ("DecisionSupportSystem", "agents/decision_support/decision_support_system.py"),
        ("SimilaritySearchEngine", "agents/knowledge_base/similarity_search_engine.py"),
        ("KnowledgeBaseManager", "agents/knowledge_base/knowledge_base_manager.py"),
        ("IntelligentFeedbackGenerator", "agents/feedback/intelligent_feedback_generator.py"),
        ("AutoCodeGenerator", "agents/code_generation/auto_code_generator.py"),
    ]

    for agent_name, agent_path in agents_to_check:
        check_agent_module(agent_name, agent_path)

    # 連携ポイントを確認
    check_integration_points()

    print(f"\n" + "=" * 80)
    print("📊 分析完了")
    print("=" * 80)


if __name__ == "__main__":
    main()
