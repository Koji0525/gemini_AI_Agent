"""
Week 6: 動的エージェント生成システム 最終統合デモ

全コンポーネントを統合した完全なエンドツーエンドデモ
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import asyncio
from dotenv import load_dotenv
from agents.dynamic import AgentGenerator, AgentTestGenerator, create_test_case, SandboxRunner, AgentRegistry

load_dotenv()

# Google Sheets連携（オプション）
try:
    from tools.sheets_manager import GoogleSheetsManager

    SHEETS_AVAILABLE = True
except ImportError:
    SHEETS_AVAILABLE = False


async def complete_workflow_demo():
    """
    完全なワークフローのデモンストレーション

    フロー:
    1. エージェント生成
    2. テスト生成
    3. 品質検証
    4. レジストリ登録
    5. 実行シミュレーション
    6. 統計表示
    """

    print("\n" + "=" * 70)
    print("🚀 Week 6: 動的エージェント生成システム 最終統合デモ")
    print("=" * 70)

    print("\n本デモでは完全なエンドツーエンドワークフローを実証します:")
    print("  1. AgentGenerator - エージェント自動生成")
    print("  2. TestGenerator - テスト自動生成")
    print("  3. SandboxRunner - 品質検証")
    print("  4. AgentRegistry - レジストリ登録")
    print("  5. 実行シミュレーション")
    print("  6. 統計・分析")

    # Google Sheets連携の初期化
    sheets_manager = None
    if SHEETS_AVAILABLE:
        spreadsheet_id = os.getenv("SPREADSHEET_ID")
        if spreadsheet_id:
            try:
                sheets_manager = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)
                print("\n✅ Google Sheets連携: 有効")
            except Exception as e:
                print(f"\n⚠️  Google Sheets連携エラー: {e}")

    if not sheets_manager:
        print("\n⚠️  Google Sheets連携: 無効（ローカルモード）")

    # コンポーネント初期化
    agent_gen = AgentGenerator()
    test_gen = AgentTestGenerator()
    sandbox = SandboxRunner()
    registry = AgentRegistry(sheets_manager=sheets_manager)

    # ================================================
    # シナリオ1: WeatherAPIAgent
    # ================================================

    print("\n" + "=" * 70)
    print("【シナリオ1】WeatherAPIAgent - 完全なライフサイクル")
    print("=" * 70)

    print("\n【フェーズ1】エージェント生成")
    print("-" * 70)

    agent_config_1 = {
        "version": "1.0.0",
        "description": "Weather API calling agent for real-time weather data",
        "author": "System",
    }

    agent_code_1 = agent_gen.generate_from_template(
        template_name="simple_api_agent", agent_name="WeatherAPIAgent", config=agent_config_1
    )

    agent_filepath_1 = agent_gen.save_agent(agent_code_1, "WeatherAPIAgent")
    print(f"✅ エージェント生成: {agent_filepath_1}")
    print(f"   コード行数: {len(agent_code_1.split(chr(10)))}行")

    print("\n【フェーズ2】テスト生成")
    print("-" * 70)

    test_cases_1 = [
        create_test_case(
            name="valid_weather_request",
            description="Test valid weather API request",
            inputs={"url": "https://api.openweathermap.org/data/2.5/weather"},
            expected_success=True,
        ),
        create_test_case(
            name="invalid_url_format",
            description="Test with invalid URL",
            inputs={"url": "not-a-valid-url"},
            expected_success=False,
        ),
        create_test_case(
            name="missing_required_param",
            description="Test without required URL parameter",
            inputs={},
            expected_success=False,
        ),
    ]

    test_code_1 = test_gen.generate_test_suite(
        agent_name="WeatherAPIAgent", agent_class="Weatherapiagent", test_cases=test_cases_1
    )

    test_filepath_1 = test_gen.save_test_file(test_code_1, "WeatherAPIAgent")
    print(f"✅ テスト生成: {test_filepath_1}")
    print(f"   基本テスト: 6個")
    print(f"   カスタムテスト: {len(test_cases_1)}個")
    print(f"   合計: {6 + len(test_cases_1)}個")

    print("\n【フェーズ3】品質検証")
    print("-" * 70)

    # モックテスト結果（実際の実行をシミュレート）
    mock_result_1 = {"success": True, "execution_time": 11.8, "test_results": {"total": 9, "passed": 9, "failed": 0}}

    quality_1 = sandbox.validate_agent_quality(mock_result_1)

    print(f"承認: {'✅ YES' if quality_1['approved'] else '❌ NO'}")
    print(f"品質スコア: {quality_1['quality_score']}/100")
    print(f"成功率: {quality_1['success_rate']}")
    print(f"実行時間: {quality_1['execution_time']}秒")
    print(f"合格テスト: {quality_1['passed_tests']}/{quality_1['total_tests']}")

    print("\n【フェーズ4】レジストリ登録")
    print("-" * 70)

    if quality_1["approved"]:
        agent_id_1 = registry.register_agent(
            agent_name="WeatherAPIAgent",
            agent_class="Weatherapiagent",
            version="1.0.0",
            template="simple_api_agent",
            description="Weather API calling agent for real-time weather data",
            file_path=agent_filepath_1,
            test_file_path=test_filepath_1,
            quality_score=quality_1["quality_score"],
            created_by="System",
            dependencies=["aiohttp", "requests"],
            capabilities=["api_call", "http_request", "weather_data"],
            tags=["api", "weather", "auto-generated"],
        )

        # ステータスを active に更新
        registry.update_agent_status(agent_id_1, "active")

        print(f"✅ レジストリ登録完了: {agent_id_1}")
        print(f"   ステータス: active")

    # ================================================
    # シナリオ2: DataProcessorAgent
    # ================================================

    print("\n" + "=" * 70)
    print("【シナリオ2】DataProcessorAgent - 完全なライフサイクル")
    print("=" * 70)

    print("\n【フェーズ1】エージェント生成")
    print("-" * 70)

    agent_config_2 = {"version": "1.0.0", "description": "Data processing and transformation agent", "author": "System"}

    agent_code_2 = agent_gen.generate_from_template(
        template_name="data_processor_agent", agent_name="DataProcessorAgent", config=agent_config_2
    )

    agent_filepath_2 = agent_gen.save_agent(agent_code_2, "DataProcessorAgent")
    print(f"✅ エージェント生成: {agent_filepath_2}")
    print(f"   コード行数: {len(agent_code_2.split(chr(10)))}行")

    print("\n【フェーズ2】テスト生成")
    print("-" * 70)

    test_cases_2 = [
        create_test_case(
            name="filter_operation",
            description="Test data filtering",
            inputs={"data": [1, 2, 3, 4, 5], "operation": "filter"},
            expected_success=True,
        ),
        create_test_case(
            name="transform_operation",
            description="Test data transformation",
            inputs={"data": [1, 2, 3], "operation": "transform"},
            expected_success=True,
        ),
        create_test_case(
            name="aggregate_operation",
            description="Test data aggregation",
            inputs={"data": [1, 2, 3, 4, 5], "operation": "aggregate"},
            expected_success=True,
        ),
    ]

    test_code_2 = test_gen.generate_test_suite(
        agent_name="DataProcessorAgent", agent_class="Dataprocessoragent", test_cases=test_cases_2
    )

    test_filepath_2 = test_gen.save_test_file(test_code_2, "DataProcessorAgent")
    print(f"✅ テスト生成: {test_filepath_2}")
    print(f"   基本テスト: 6個")
    print(f"   カスタムテスト: {len(test_cases_2)}個")
    print(f"   合計: {6 + len(test_cases_2)}個")

    print("\n【フェーズ3】品質検証")
    print("-" * 70)

    mock_result_2 = {"success": True, "execution_time": 9.2, "test_results": {"total": 9, "passed": 8, "failed": 1}}

    quality_2 = sandbox.validate_agent_quality(mock_result_2)

    print(f"承認: {'✅ YES' if quality_2['approved'] else '❌ NO'}")
    print(f"品質スコア: {quality_2['quality_score']}/100")
    print(f"成功率: {quality_2['success_rate']}")
    print(f"実行時間: {quality_2['execution_time']}秒")
    print(f"合格テスト: {quality_2['passed_tests']}/{quality_2['total_tests']}")

    print("\n【フェーズ4】レジストリ登録")
    print("-" * 70)

    if quality_2["approved"]:
        agent_id_2 = registry.register_agent(
            agent_name="DataProcessorAgent",
            agent_class="Dataprocessoragent",
            version="1.0.0",
            template="data_processor_agent",
            description="Data processing and transformation agent",
            file_path=agent_filepath_2,
            test_file_path=test_filepath_2,
            quality_score=quality_2["quality_score"],
            created_by="System",
            dependencies=["pandas", "numpy"],
            capabilities=["data_processing", "filtering", "transformation", "aggregation"],
            tags=["data", "processing", "auto-generated"],
        )

        registry.update_agent_status(agent_id_2, "active")

        print(f"✅ レジストリ登録完了: {agent_id_2}")
        print(f"   ステータス: active")

    # ================================================
    # フェーズ5: 実行シミュレーション
    # ================================================

    print("\n" + "=" * 70)
    print("【フェーズ5】実行シミュレーション")
    print("=" * 70)

    print("\nエージェントの実行をシミュレートします...")

    # WeatherAPIAgent の実行記録
    print("\n  WeatherAPIAgent:")
    registry.record_execution(agent_id_1, success=True, execution_time=12.3)
    print("    - 実行1: ✅ 成功 (12.3秒)")

    registry.record_execution(agent_id_1, success=True, execution_time=10.5)
    print("    - 実行2: ✅ 成功 (10.5秒)")

    registry.record_execution(agent_id_1, success=True, execution_time=11.8)
    print("    - 実行3: ✅ 成功 (11.8秒)")

    # DataProcessorAgent の実行記録
    print("\n  DataProcessorAgent:")
    registry.record_execution(agent_id_2, success=True, execution_time=9.2)
    print("    - 実行1: ✅ 成功 (9.2秒)")

    registry.record_execution(agent_id_2, success=True, execution_time=8.7)
    print("    - 実行2: ✅ 成功 (8.7秒)")

    registry.record_execution(agent_id_2, success=False, execution_time=15.4)
    print("    - 実行3: ❌ 失敗 (15.4秒)")

    registry.record_execution(agent_id_2, success=True, execution_time=9.1)
    print("    - 実行4: ✅ 成功 (9.1秒)")

    # ================================================
    # フェーズ6: 統計・分析
    # ================================================

    print("\n" + "=" * 70)
    print("【フェーズ6】統計・分析")
    print("=" * 70)

    # レジストリ統計
    print("\n【レジストリ統計】")
    print("-" * 70)

    stats = registry.get_statistics()

    print(f"\n総エージェント数: {stats['total_agents']}")
    print(f"平均品質スコア: {stats['avg_quality_score']}/100")
    print(f"総実行回数: {stats['total_executions']}")

    print("\nステータス別:")
    for status, count in stats["by_status"].items():
        print(f"  - {status}: {count}")

    print("\nテンプレート別:")
    for template, count in stats["by_template"].items():
        print(f"  - {template}: {count}")

    # 個別エージェント情報
    print("\n【個別エージェント詳細】")
    print("-" * 70)

    for aid in [agent_id_1, agent_id_2]:
        agent = registry.get_agent(aid)
        if agent:
            print(f"\n  {agent['agent_name']} v{agent['version']}")
            print(f"    ステータス: {agent['status']}")
            print(f"    品質スコア: {agent['quality_score']}/100")
            print(f"    実行回数: {agent['execution_count']}回")
            print(f"    成功率: {agent['success_rate']}")
            print(f"    平均実行時間: {agent['avg_execution_time']}秒")

    # コンポーネント別統計
    print("\n【コンポーネント別統計】")
    print("-" * 70)

    print("\n  AgentGenerator:")
    gen_stats = agent_gen.get_statistics()
    print(f"    - 総生成数: {gen_stats['total_generated']}")
    print(f"    - テンプレート数: {gen_stats['templates_available']}")

    print("\n  TestGenerator:")
    test_stats = test_gen.get_statistics()
    print(f"    - 総生成数: {test_stats['total_generated']}")

    print("\n  SandboxRunner:")
    sandbox_stats = sandbox.get_statistics()
    print(f"    - 総実行数: {sandbox_stats['total_executions']}")
    print(f"    - 成功率: {sandbox_stats['success_rate']}")

    # 最終サマリー
    print("\n" + "=" * 70)
    print("📊 Week 6 最終サマリー")
    print("=" * 70)

    summary = {
        "生成エージェント": stats["total_agents"],
        "平均品質スコア": f"{stats['avg_quality_score']}/100",
        "総実行回数": stats["total_executions"],
        "レジストリ登録": f"{stats['total_agents']}個",
        "アクティブエージェント": stats["by_status"].get("active", 0),
    }

    print()
    for key, value in summary.items():
        print(f"  {key}: {value}")

    if sheets_manager:
        print(f"\n💡 agent_registryシートで詳細を確認:")
        print(f"   https://docs.google.com/spreadsheets/d/{os.getenv('SPREADSHEET_ID')}")

    print("\n" + "=" * 70)
    print("🎉 Week 6: 動的エージェント生成システム 完全統合デモ完了")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(complete_workflow_demo())
