"""
Phase 2 エージェント統合テスト

テスト対象:
- DocumentationAgent
- MonitoringAgent
- OptimizationAgent
"""

import asyncio
import os
import sys
import pytest

# パスを追加
sys.path.insert(0, os.path.abspath("."))

from agents.documentation.documentation_agent import DocumentationAgent
from agents.monitoring.monitoring_agent import MonitoringAgent
from agents.optimization.optimization_agent import OptimizationAgent


@pytest.mark.asyncio
async def test_documentation_agent():
    """DocumentationAgent のテスト"""
    print("\n" + "=" * 60)
    print("📝 DocumentationAgent テスト開始")
    print("=" * 60)

    agent = DocumentationAgent()

    # テスト用のPythonファイルを作成
    test_file = "/tmp/test_module.py"
    with open(test_file, "w") as f:
        f.write(
            '''
"""テストモジュール"""

class TestClass:
    """テストクラス"""
    
    def test_method(self, arg1: str) -> str:
        """テストメソッド"""
        return arg1

def test_function(x: int) -> int:
    """テスト関数"""
    return x * 2
'''
        )

    # ファイル解析
    result = await agent.analyze_python_file(test_file)

    print(f"✅ 解析完了: {result['file_path']}")
    print(f"  - クラス数: {len(result['classes'])}")
    print(f"  - 関数数: {len(result['functions'])}")

    assert len(result["classes"]) == 1
    assert len(result["functions"]) == 1
    assert result["classes"][0]["name"] == "TestClass"

    # タスク実行テスト
    task_result = await agent.execute({"type": "analyze", "file_path": test_file})

    assert task_result["status"] == "success"

    print("✅ DocumentationAgent テスト成功")


@pytest.mark.asyncio
async def test_monitoring_agent():
    """MonitoringAgent のテスト"""
    print("\n" + "=" * 60)
    print("📊 MonitoringAgent テスト開始")
    print("=" * 60)

    agent = MonitoringAgent()

    # メトリクス収集
    metrics = await agent.collect_metrics()

    print(f"✅ メトリクス収集完了")
    print(f"  - CPU: {metrics['cpu']['percent']:.1f}%")
    print(f"  - メモリ: {metrics['memory']['percent']:.1f}%")
    print(f"  - ディスク: {metrics['disk']['percent']:.1f}%")

    assert "cpu" in metrics
    assert "memory" in metrics
    assert "disk" in metrics

    # アラートチェック
    alerts = await agent.check_alerts(metrics)
    print(f"  - アラート数: {len(alerts)}")

    # レポート生成
    report = await agent.generate_report(duration_minutes=1)

    print(f"✅ レポート生成完了")
    print(f"  - CPU平均: {report['cpu']['avg']:.1f}%")

    assert "cpu" in report
    assert "memory" in report

    # タスク実行テスト
    task_result = await agent.execute({"type": "collect"})

    assert task_result["status"] == "success"
    assert "metrics" in task_result

    print("✅ MonitoringAgent テスト成功")


@pytest.mark.asyncio
async def test_optimization_agent():
    """OptimizationAgent のテスト"""
    print("\n" + "=" * 60)
    print("⚡ OptimizationAgent テスト開始")
    print("=" * 60)

    agent = OptimizationAgent()

    # テスト用のPythonファイルを作成（ボトルネック含む）
    test_file = "/tmp/test_performance.py"
    with open(test_file, "w") as f:
        f.write(
            """
# ネストしたループ（ボトルネック）
for i in range(1000):
    for j in range(1000):
        result = i * j

# ブロッキングI/O（ボトルネック）
with open('test.txt', 'r') as f:
    data = f.read()

# 通常の関数
def normal_function(x):
    return x + 1
"""
        )

    # パフォーマンス分析
    analysis = await agent.analyze_code_performance(test_file)

    print(f"✅ 分析完了: {analysis['file_path']}")
    print(f"  - ボトルネック数: {len(analysis['bottlenecks'])}")
    print(f"  - 最適化スコア: {analysis['optimization_score']:.1f}/100")

    for bottleneck in analysis["bottlenecks"]:
        print(f"  - {bottleneck['type']}: {bottleneck['severity']}")

    assert len(analysis["bottlenecks"]) >= 1
    assert analysis["optimization_score"] < 100

    # タスク実行テスト
    task_result = await agent.execute({"type": "analyze", "file_path": test_file})

    assert task_result["status"] == "success"
    assert "analysis" in task_result

    print("✅ OptimizationAgent テスト成功")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Phase 2 エージェント統合テスト")
    print("=" * 60)

    asyncio.run(test_documentation_agent())
    asyncio.run(test_monitoring_agent())
    asyncio.run(test_optimization_agent())

    print("\n" + "=" * 60)
    print("✅ 全テスト完了")
    print("=" * 60)
