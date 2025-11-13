#!/usr/bin/env python3
"""
既存実装の分析スクリプト
"""

import os


def analyze_self_healing():
    """SelfHealingAgentの実装状況を分析"""

    agent_path = "agents/self_healing/self_healing_agent.py"

    if not os.path.exists(agent_path):
        print("❌ SelfHealingAgentが見つかりません")
        return

    with open(agent_path, "r") as f:
        content = f.read()

    # 実装状況の分析
    implemented_features = []

    if "class SelfHealingAgent" in content:
        implemented_features.append("✅ メインクラス実装済み")

    if "class ErrorClassifier" in content:
        implemented_features.append("✅ ErrorClassifier実装済み（内部クラス）")

    if "class RetryManager" in content:
        implemented_features.append("✅ RetryManager実装済み（内部クラス）")

    if "detect_and_heal" in content:
        implemented_features.append("✅ detect_and_healメソッド実装済み")

    if "decide_healing_strategy" in content:
        implemented_features.append("✅ 修復戦略決定ロジック実装済み")

    if "execute_healing" in content:
        implemented_features.append("✅ 修復実行ロジック実装済み")

    # 不足している機能の分析
    missing_features = []

    if "knowledge_manager" not in content:
        missing_features.append("❌ KnowledgeManager連携未実装")

    if "record_healing" not in content or "healing_log" not in content:
        missing_features.append("❌ 修復ログ記録未実装")

    if "CompleteEngineUltimate" not in content:
        missing_features.append("❌ CompleteEngine連携未実装")

    print("🔍 SelfHealingAgent 実装状況分析")
    print("=" * 50)
    print("\n✅ 実装済み機能:")
    for feature in implemented_features:
        print(f"  {feature}")

    print("\n❌ 不足機能（連携未実装）:")
    for feature in missing_features:
        print(f"  {feature}")

    print(f"\n📊 実装進捗: {len(implemented_features)}/8 機能")
    print(f"🔄 連携進捗: {len([f for f in implemented_features if '連携' in f])}/3 連携")


if __name__ == "__main__":
    analyze_self_healing()
