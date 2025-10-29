"""
Week 6: 動的エージェント生成システム完全統合デモ

AgentGenerator → TestGenerator → SandboxRunner
の完全なワークフローを実証
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import asyncio
from agents.dynamic import (
    AgentGenerator,
    TestGenerator,
    create_test_case,
    SandboxRunner
)


async def demo_scenario_1_weather_api_agent():
    """
    シナリオ1: WeatherAPIAgentの生成と検証
    
    フロー:
    1. エージェント生成
    2. テスト生成
    3. テスト実行（スキップ - デモなので）
    4. 品質検証（モック）
    """
    print("\n" + "="*70)
    print("【シナリオ1】WeatherAPIAgent 生成と検証")
    print("="*70)
    
    # Step 1: エージェント生成
    print("\n【Step 1】エージェント生成")
    print("-"*70)
    
    agent_generator = AgentGenerator()
    
    agent_config = {
        'version': '1.0.0',
        'description': 'Weather API calling agent',
        'author': 'System'
    }
    
    agent_code = agent_generator.generate_from_template(
        template_name='simple_api_agent',
        agent_name='WeatherAPIAgent',
        config=agent_config
    )
    
    agent_filepath = agent_generator.save_agent(agent_code, 'WeatherAPIAgent')
    print(f"✅ エージェント生成完了: {agent_filepath}")
    print(f"   コード行数: {len(agent_code.split(chr(10)))}行")
    
    # Step 2: テスト生成
    print("\n【Step 2】テスト生成")
    print("-"*70)
    
    test_generator = TestGenerator()
    
    # カスタムテストケース定義
    test_cases = [
        create_test_case(
            name='valid_weather_api_call',
            description='Test valid weather API call',
            inputs={'url': 'https://api.openweathermap.org/data/2.5/weather'},
            expected_success=True
        ),
        create_test_case(
            name='invalid_url',
            description='Test with invalid URL',
            inputs={'url': 'invalid-url'},
            expected_success=False
        ),
        create_test_case(
            name='missing_url',
            description='Test with missing URL parameter',
            inputs={},
            expected_success=False
        )
    ]
    
    test_code = test_generator.generate_test_suite(
        agent_name='WeatherAPIAgent',
        agent_class='WeatherAPIAgent',
        test_cases=test_cases
    )
    
    test_filepath = test_generator.save_test_file(test_code, 'WeatherAPIAgent')
    print(f"✅ テスト生成完了: {test_filepath}")
    print(f"   テストコード行数: {len(test_code.split(chr(10)))}行")
    print(f"   基本テスト: 6個")
    print(f"   カスタムテスト: {len(test_cases)}個")
    print(f"   合計テスト数: {6 + len(test_cases)}個")
    
    # Step 3: 品質検証（モック結果で実証）
    print("\n【Step 3】品質検証")
    print("-"*70)
    
    runner = SandboxRunner()
    
    # モックのテスト結果（実際の実行をシミュレート）
    mock_test_results = {
        'success': True,
        'execution_time': 12.5,
        'test_results': {
            'total': 9,
            'passed': 9,
            'failed': 0
        }
    }
    
    quality = runner.validate_agent_quality(mock_test_results)
    
    print(f"承認: {'✅ YES' if quality['approved'] else '❌ NO'}")
    print(f"品質スコア: {quality['quality_score']}/100")
    print(f"成功率: {quality['success_rate']}")
    print(f"実行時間: {quality['execution_time']}秒")
    print(f"合格テスト: {quality['passed_tests']}/{quality['total_tests']}")
    print(f"理由: {quality['reason']}")
    
    return {
        'agent_name': 'WeatherAPIAgent',
        'agent_filepath': agent_filepath,
        'test_filepath': test_filepath,
        'quality': quality
    }


async def demo_scenario_2_data_processor_agent():
    """
    シナリオ2: DataProcessorAgentの生成と検証
    """
    print("\n" + "="*70)
    print("【シナリオ2】DataProcessorAgent 生成と検証")
    print("="*70)
    
    # Step 1: エージェント生成
    print("\n【Step 1】エージェント生成")
    print("-"*70)
    
    agent_generator = AgentGenerator()
    
    agent_config = {
        'version': '1.0.0',
        'description': 'Data processing and transformation agent',
        'author': 'System'
    }
    
    agent_code = agent_generator.generate_from_template(
        template_name='data_processor_agent',
        agent_name='DataProcessorAgent',
        config=agent_config
    )
    
    agent_filepath = agent_generator.save_agent(agent_code, 'DataProcessorAgent')
    print(f"✅ エージェント生成完了: {agent_filepath}")
    print(f"   コード行数: {len(agent_code.split(chr(10)))}行")
    
    # Step 2: テスト生成
    print("\n【Step 2】テスト生成")
    print("-"*70)
    
    test_generator = TestGenerator()
    
    test_cases = [
        create_test_case(
            name='filter_operation',
            description='Test data filtering',
            inputs={
                'data': [1, 2, 3, 4, 5],
                'operation': 'filter'
            },
            expected_success=True
        ),
        create_test_case(
            name='transform_operation',
            description='Test data transformation',
            inputs={
                'data': [1, 2, 3],
                'operation': 'transform'
            },
            expected_success=True
        ),
        create_test_case(
            name='aggregate_operation',
            description='Test data aggregation',
            inputs={
                'data': [1, 2, 3, 4, 5],
                'operation': 'aggregate'
            },
            expected_success=True
        )
    ]
    
    test_code = test_generator.generate_test_suite(
        agent_name='DataProcessorAgent',
        agent_class='DataProcessorAgent',
        test_cases=test_cases
    )
    
    test_filepath = test_generator.save_test_file(test_code, 'DataProcessorAgent')
    print(f"✅ テスト生成完了: {test_filepath}")
    print(f"   テストコード行数: {len(test_code.split(chr(10)))}行")
    print(f"   基本テスト: 6個")
    print(f"   カスタムテスト: {len(test_cases)}個")
    print(f"   合計テスト数: {6 + len(test_cases)}個")
    
    # Step 3: 品質検証
    print("\n【Step 3】品質検証")
    print("-"*70)
    
    runner = SandboxRunner()
    
    mock_test_results = {
        'success': True,
        'execution_time': 8.2,
        'test_results': {
            'total': 9,
            'passed': 8,
            'failed': 1
        }
    }
    
    quality = runner.validate_agent_quality(mock_test_results)
    
    print(f"承認: {'✅ YES' if quality['approved'] else '❌ NO'}")
    print(f"品質スコア: {quality['quality_score']}/100")
    print(f"成功率: {quality['success_rate']}")
    print(f"実行時間: {quality['execution_time']}秒")
    print(f"合格テスト: {quality['passed_tests']}/{quality['total_tests']}")
    print(f"理由: {quality['reason']}")
    
    return {
        'agent_name': 'DataProcessorAgent',
        'agent_filepath': agent_filepath,
        'test_filepath': test_filepath,
        'quality': quality
    }


async def demo_statistics_summary():
    """
    統計情報のサマリー表示
    """
    print("\n" + "="*70)
    print("【統計サマリー】システム全体の統計")
    print("="*70)
    
    # AgentGenerator統計
    agent_gen = AgentGenerator()
    print("\n【AgentGenerator統計】")
    print("-"*70)
    print(f"利用可能なテンプレート: {len(agent_gen.list_templates())}種類")
    print(f"テンプレート一覧:")
    for template in agent_gen.list_templates():
        print(f"  - {template}")
    
    # TestGenerator統計
    test_gen = TestGenerator()
    print("\n【TestGenerator統計】")
    print("-"*70)
    print("自動生成される基本テスト:")
    print("  1. test_agent_initialization")
    print("  2. test_metadata_structure")
    print("  3. test_required_params")
    print("  4. test_statistics_tracking")
    print("  5. test_validate_input_missing_params")
    print("  6. test_execute_with_invalid_input")
    
    # SandboxRunner統計
    runner = SandboxRunner()
    print("\n【SandboxRunner統計】")
    print("-"*70)
    print("品質検証基準:")
    print("  - テスト合格率: 70点満点")
    print("  - パフォーマンス: 30点満点")
    print("  - 承認基準: 80点以上")
    print("  - 推奨実行時間: 30秒以内")


async def demo_workflow_visualization():
    """
    ワークフローの可視化
    """
    print("\n" + "="*70)
    print("【ワークフロー可視化】")
    print("="*70)
    
    workflow = """
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│              動的エージェント生成ワークフロー                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

1. 要件定義
   ├─ エージェント名
   ├─ 機能説明
   └─ 必要なテンプレート
         ↓
2. AgentGenerator
   ├─ テンプレート選択
   ├─ プレースホルダー置換
   └─ Pythonコード生成
         ↓
3. TestGenerator
   ├─ 基本テスト生成（6種類）
   ├─ カスタムテスト追加
   └─ pytest形式で出力
         ↓
4. SandboxRunner
   ├─ サンドボックス実行
   ├─ pytest実行
   └─ 結果解析
         ↓
5. 品質検証
   ├─ テスト合格率（70点）
   ├─ パフォーマンス（30点）
   └─ 承認判定（80点以上）
         ↓
6. 承認/却下
   ├─ ✅ 承認 → エージェント登録
   └─ ❌ 却下 → 改善または破棄

"""
    print(workflow)


async def main():
    """メインデモ"""
    
    print("\n" + "="*70)
    print("🚀 Week 6: 動的エージェント生成システム 完全統合デモ")
    print("="*70)
    
    print("\n本デモでは以下を実証します:")
    print("  1. AgentGenerator - エージェント自動生成")
    print("  2. TestGenerator - テスト自動生成")
    print("  3. SandboxRunner - 品質検証")
    print("  4. 統合ワークフロー")
    
    # ワークフロー可視化
    await demo_workflow_visualization()
    
    # シナリオ1: WeatherAPIAgent
    result1 = await demo_scenario_1_weather_api_agent()
    
    # シナリオ2: DataProcessorAgent
    result2 = await demo_scenario_2_data_processor_agent()
    
    # 統計サマリー
    await demo_statistics_summary()
    
    # 最終結果
    print("\n" + "="*70)
    print("【最終結果】")
    print("="*70)
    
    results = [result1, result2]
    
    print("\n生成されたエージェント:")
    for i, result in enumerate(results, 1):
        status = "✅ 承認" if result['quality']['approved'] else "❌ 却下"
        print(f"\n  {i}. {result['agent_name']}")
        print(f"     ステータス: {status}")
        print(f"     品質スコア: {result['quality']['quality_score']}/100")
        print(f"     エージェントファイル: {result['agent_filepath']}")
        print(f"     テストファイル: {result['test_filepath']}")
    
    # 成功率計算
    approved_count = sum(1 for r in results if r['quality']['approved'])
    success_rate = (approved_count / len(results)) * 100
    
    print(f"\n承認率: {approved_count}/{len(results)} ({success_rate:.0f}%)")
    
    print("\n" + "="*70)
    print("🎉 Week 6 Day 3: 完全統合デモ完了")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
