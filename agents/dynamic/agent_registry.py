"""
Week 6: AgentRegistry - 動的エージェント登録管理システム

生成されたエージェントを登録・管理
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class AgentRegistry:
    """
    動的エージェントの登録・管理システム
    """

    def __init__(self, sheets_manager=None):
        """
        Args:
            sheets_manager: GoogleSheetsManagerインスタンス（省略時はNone）
        """
        self.sheets_manager = sheets_manager
        self.sheet_name = "agent_registry"
        self.local_registry = {}  # ローカルキャッシュ
        self.registration_count = 0

    def register_agent(
        self,
        agent_name: str,
        agent_class: str,
        version: str,
        template: str,
        description: str,
        file_path: str,
        test_file_path: str,
        quality_score: int,
        created_by: str = "System",
        dependencies: Optional[List[str]] = None,
        capabilities: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        notes: str = "",
    ) -> str:
        """
        エージェントを登録

        Args:
            agent_name: エージェント名
            agent_class: クラス名
            version: バージョン
            template: 使用したテンプレート
            description: 説明
            file_path: ファイルパス
            test_file_path: テストファイルパス
            quality_score: 品質スコア
            created_by: 作成者
            dependencies: 依存パッケージ
            capabilities: 機能リスト
            tags: タグ
            notes: 備考

        Returns:
            エージェントID
        """
        # エージェントID生成
        agent_id = self._generate_agent_id(agent_name, version)

        # 登録データ作成
        now = datetime.now().isoformat()

        agent_data = {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "agent_class": agent_class,
            "version": version,
            "template": template,
            "status": "testing",  # 初期ステータス
            "created_at": now,
            "updated_at": now,
            "created_by": created_by,
            "description": description,
            "dependencies": json.dumps(dependencies or []),
            "capabilities": json.dumps(capabilities or []),
            "tags": ",".join(tags or []),
            "file_path": file_path,
            "test_file_path": test_file_path,
            "quality_score": quality_score,
            "execution_count": 0,
            "success_count": 0,
            "failure_count": 0,
            "success_rate": "0.0%",
            "avg_execution_time": 0.0,
            "last_executed_at": "",
            "notes": notes,
        }

        # ローカルレジストリに保存
        self.local_registry[agent_id] = agent_data

        # Google Sheetsに保存（利用可能な場合）
        if self.sheets_manager:
            try:
                row_data = list(agent_data.values())
                self.sheets_manager.append_row(self.sheet_name, row_data)
                print(f"✅ エージェント登録（Sheets）: {agent_id}")
            except Exception as e:
                print(f"⚠️  Sheets登録失敗: {e}")

        self.registration_count += 1
        print(f"✅ エージェント登録（ローカル）: {agent_id}")

        return agent_id

    def update_agent_status(self, agent_id: str, status: str) -> bool:
        """
        エージェントのステータスを更新

        Args:
            agent_id: エージェントID
            status: 新しいステータス（active/inactive/testing）

        Returns:
            更新成功したか
        """
        if agent_id not in self.local_registry:
            print(f"❌ エージェントが見つかりません: {agent_id}")
            return False

        # ローカルレジストリ更新
        self.local_registry[agent_id]["status"] = status
        self.local_registry[agent_id]["updated_at"] = datetime.now().isoformat()

        # Google Sheets更新（実装省略 - 行を特定して更新が必要）

        print(f"✅ ステータス更新: {agent_id} → {status}")
        return True

    def record_execution(self, agent_id: str, success: bool, execution_time: float) -> bool:
        """
        エージェント実行を記録

        Args:
            agent_id: エージェントID
            success: 成功したか
            execution_time: 実行時間（秒）

        Returns:
            記録成功したか
        """
        if agent_id not in self.local_registry:
            print(f"❌ エージェントが見つかりません: {agent_id}")
            return False

        agent = self.local_registry[agent_id]

        # 実行カウント更新
        agent["execution_count"] += 1

        if success:
            agent["success_count"] += 1
        else:
            agent["failure_count"] += 1

        # 成功率計算
        success_rate = (agent["success_count"] / agent["execution_count"]) * 100
        agent["success_rate"] = f"{success_rate:.1f}%"

        # 平均実行時間更新
        current_avg = float(agent["avg_execution_time"])
        count = agent["execution_count"]
        new_avg = ((current_avg * (count - 1)) + execution_time) / count
        agent["avg_execution_time"] = round(new_avg, 2)

        # 最終実行日時更新
        agent["last_executed_at"] = datetime.now().isoformat()
        agent["updated_at"] = datetime.now().isoformat()

        print(f"✅ 実行記録: {agent_id} ({'成功' if success else '失敗'})")

        return True

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        エージェント情報を取得

        Args:
            agent_id: エージェントID

        Returns:
            エージェント情報（存在しない場合はNone）
        """
        return self.local_registry.get(agent_id)

    def list_agents(
        self, status: Optional[str] = None, template: Optional[str] = None, tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        エージェントリストを取得

        Args:
            status: フィルタするステータス
            template: フィルタするテンプレート
            tags: フィルタするタグ

        Returns:
            エージェントリスト
        """
        agents = list(self.local_registry.values())

        # ステータスでフィルタ
        if status:
            agents = [a for a in agents if a["status"] == status]

        # テンプレートでフィルタ
        if template:
            agents = [a for a in agents if a["template"] == template]

        # タグでフィルタ
        if tags:
            agents = [a for a in agents if any(tag in a["tags"] for tag in tags)]

        return agents

    def get_statistics(self) -> Dict[str, Any]:
        """
        レジストリ統計を取得

        Returns:
            統計情報
        """
        agents = list(self.local_registry.values())

        if not agents:
            return {
                "total_agents": 0,
                "by_status": {},
                "by_template": {},
                "avg_quality_score": 0,
                "total_executions": 0,
            }

        # ステータス別カウント
        by_status = {}
        for agent in agents:
            status = agent["status"]
            by_status[status] = by_status.get(status, 0) + 1

        # テンプレート別カウント
        by_template = {}
        for agent in agents:
            template = agent["template"]
            by_template[template] = by_template.get(template, 0) + 1

        # 平均品質スコア
        avg_quality = sum(a["quality_score"] for a in agents) / len(agents)

        # 総実行回数
        total_executions = sum(a["execution_count"] for a in agents)

        return {
            "total_agents": len(agents),
            "by_status": by_status,
            "by_template": by_template,
            "avg_quality_score": round(avg_quality, 1),
            "total_executions": total_executions,
        }

    def _generate_agent_id(self, agent_name: str, version: str) -> str:
        """
        エージェントIDを生成

        Args:
            agent_name: エージェント名
            version: バージョン

        Returns:
            エージェントID
        """
        # agent_name + version + タイムスタンプ
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        clean_name = agent_name.lower().replace(" ", "_")
        clean_version = version.replace(".", "_")

        return f"{clean_name}_v{clean_version}_{timestamp}"


# ================================================
# デモ
# ================================================


def demo_agent_registry():
    """AgentRegistryのデモンストレーション"""
    print("\n" + "=" * 70)
    print("AgentRegistry デモンストレーション")
    print("=" * 70)

    registry = AgentRegistry()

    # エージェント登録
    print("\n【エージェント登録】")
    print("-" * 70)

    agent_id1 = registry.register_agent(
        agent_name="WeatherAPIAgent",
        agent_class="Weatherapiiagent",
        version="1.0.0",
        template="simple_api_agent",
        description="Weather API calling agent",
        file_path="agents/dynamic/generated/weatherapiagent.py",
        test_file_path="tests/dynamic/generated/test_weatherapiagent.py",
        quality_score=100,
        created_by="System",
        dependencies=["aiohttp", "requests"],
        capabilities=["api_call", "http_request"],
        tags=["api", "weather", "auto-generated"],
    )

    agent_id2 = registry.register_agent(
        agent_name="DataProcessorAgent",
        agent_class="Dataprocessoragent",
        version="1.0.0",
        template="data_processor_agent",
        description="Data processing agent",
        file_path="agents/dynamic/generated/dataprocessoragent.py",
        test_file_path="tests/dynamic/generated/test_dataprocessoragent.py",
        quality_score=92,
        created_by="System",
        dependencies=["pandas", "numpy"],
        capabilities=["data_processing", "filtering", "aggregation"],
        tags=["data", "processing", "auto-generated"],
    )

    # 実行記録
    print("\n【実行記録】")
    print("-" * 70)

    registry.record_execution(agent_id1, success=True, execution_time=12.5)
    registry.record_execution(agent_id1, success=True, execution_time=10.3)
    registry.record_execution(agent_id2, success=True, execution_time=8.2)
    registry.record_execution(agent_id2, success=False, execution_time=15.0)

    # ステータス更新
    print("\n【ステータス更新】")
    print("-" * 70)

    registry.update_agent_status(agent_id1, "active")
    registry.update_agent_status(agent_id2, "active")

    # エージェント一覧
    print("\n【エージェント一覧】")
    print("-" * 70)

    active_agents = registry.list_agents(status="active")
    print(f"\nアクティブなエージェント: {len(active_agents)}個")
    for agent in active_agents:
        print(f"  - {agent['agent_name']} v{agent['version']}")
        print(f"    品質スコア: {agent['quality_score']}/100")
        print(f"    成功率: {agent['success_rate']}")
        print(f"    実行回数: {agent['execution_count']}回")

    # 統計情報
    print("\n【統計情報】")
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

    print("\n" + "=" * 70)


if __name__ == "__main__":
    demo_agent_registry()
