"""wp_orchestrator.py - WordPress構築オーケストレーター（完全API版）"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from config.config_loader import config


class WordPressOrchestrator:
    """WordPress自動構築オーケストレーター（完全API版）"""

    def __init__(self, design_spec: Dict[str, Any], wp_credentials: Dict = None):
        self.design_spec = design_spec
        self.wp_credentials = wp_credentials or {
            "url": config.WP_URL,
            "username": config.WP_USER,
            "password": config.WP_PASS,
        }

        # API版エージェントを初期化
        self.agents = {}
        self._initialize_agents()

        self.execution_log = []
        self.current_step = 0
        self.total_steps = 0

    def _initialize_agents(self):
        """API版エージェントを初期化"""
        print("🔧 API版エージェントを初期化中...")

        try:
            # プラグインマネージャー
            from wordpress.wp_plugin_manager import WordPressPluginManager

            self.agents["plugin"] = WordPressPluginManager(self.wp_credentials)
            print("✅ プラグインマネージャー初期化完了")
        except ImportError as e:
            print(f"⚠️  プラグインマネージャーの初期化に失敗: {e}")

        try:
            # CPTエージェント
            from wordpress.wp_cpt_agent import WordPressCPTAgent

            self.agents["cpt"] = WordPressCPTAgent(self.wp_credentials)
            print("✅ CPTエージェント初期化完了")
        except ImportError as e:
            print(f"⚠️  CPTエージェントの初期化に失敗: {e}")

        try:
            # Taxonomyエージェント
            from wordpress.wp_taxonomy_agent import WordPressTaxonomyAgent

            self.agents["taxonomy"] = WordPressTaxonomyAgent(self.wp_credentials)
            print("✅ Taxonomyエージェント初期化完了")
        except ImportError as e:
            print(f"⚠️  Taxonomyエージェントの初期化に失敗: {e}")

        try:
            # ACFエージェント
            from wordpress.wp_acf_agent import WordPressACFAgent

            self.agents["acf"] = WordPressACFAgent(self.wp_credentials)
            print("✅ ACFエージェント初期化完了")
        except ImportError as e:
            print(f"⚠️  ACFエージェントの初期化に失敗: {e}")

        print(f"🎯 初期化完了: {len(self.agents)}個のAPIエージェント")

    async def execute_design(self) -> Dict[str, Any]:
        """
        設計図を実行

        Returns:
            実行結果
        """
        print("🚀 WordPress構築オーケストレーター: 設計図実行開始")
        print(f"📋 設計図: {self.design_spec.get('title', '無題')}")

        try:
            # 実行計画を作成
            execution_plan = self._create_execution_plan()
            self.total_steps = len(execution_plan)

            results = {
                "success": True,
                "total_steps": self.total_steps,
                "completed_steps": 0,
                "results": [],
                "errors": [],
            }

            # 計画を実行
            for step_number, step in enumerate(execution_plan, 1):
                self.current_step = step_number
                print(f"📝 ステップ {step_number}/{self.total_steps}: {step['description']}")

                step_result = await self._execute_step(step)
                results["results"].append(step_result)

                if step_result["success"]:
                    results["completed_steps"] += 1
                    print(f"✅ ステップ {step_number} 完了: {step_result.get('message', '成功')}")
                else:
                    results["errors"].append(
                        {
                            "step": step_number,
                            "error": step_result.get("error", "未知のエラー"),
                            "task_type": step.get("task_type"),
                        }
                    )
                    print(f"❌ ステップ {step_number} 失敗: {step_result.get('error', '未知のエラー')}")

                    # エラーが発生した場合、続行するかどうかを判断
                    if step.get("critical", True):
                        results["success"] = False
                        break

            # 実行結果をまとめる
            results["summary"] = self._generate_summary(results)

            print("🎉 WordPress構築オーケストレーター: 実行完了")
            return results

        except Exception as e:
            error_msg = f"オーケストレーター実行エラー: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "completed_steps": self.current_step,
                "total_steps": self.total_steps,
            }

    def _create_execution_plan(self) -> List[Dict[str, Any]]:
        """
        設計図から実行計画を作成

        Returns:
            実行計画
        """
        plan = []

        # 設計図からコンポーネントを抽出
        components = self.design_spec.get("components", {})

        # 1. プラグインのインストールと有効化
        plugins = components.get("plugins", [])
        for plugin in plugins:
            plan.append(
                {
                    "task_type": "plugin_installation",
                    "agent": "plugin",
                    "description": f"プラグインインストール: {plugin.get('name', '未知')}",
                    "data": {
                        "type": "plugin_installation",
                        "plugin_name": plugin.get("name"),
                        "plugin_slug": plugin.get("slug"),
                    },
                    "critical": True,
                }
            )

        # 2. カスタム投稿タイプの作成
        custom_post_types = components.get("custom_post_types", [])
        for cpt in custom_post_types:
            plan.append(
                {
                    "task_type": "create_post_type",
                    "agent": "cpt",
                    "description": f"カスタム投稿タイプ作成: {cpt.get('name', '未知')}",
                    "data": {"type": "create_post_type", "post_type_data": cpt},
                    "critical": True,
                }
            )

        # 3. カスタム分類法の作成
        taxonomies = components.get("taxonomies", [])
        for taxonomy in taxonomies:
            plan.append(
                {
                    "task_type": "create_taxonomy",
                    "agent": "taxonomy",
                    "description": f"カスタム分類法作成: {taxonomy.get('name', '未知')}",
                    "data": {
                        "type": "create_taxonomy",
                        "name": taxonomy.get("name"),
                        "slug": taxonomy.get("slug"),
                        "description": taxonomy.get("description", ""),
                        "hierarchical": taxonomy.get("hierarchical", True),
                    },
                    "critical": True,
                }
            )

        # 4. ACFフィールドグループの作成
        field_groups = components.get("field_groups", [])
        for field_group in field_groups:
            plan.append(
                {
                    "task_type": "create_field_group",
                    "agent": "acf",
                    "description": f"ACFフィールドグループ作成: {field_group.get('title', '未知')}",
                    "data": {
                        "type": "create_field_group",
                        "title": field_group.get("title"),
                        "key": field_group.get("key"),
                        "fields": field_group.get("fields", []),
                        "location": field_group.get("location", []),
                    },
                    "critical": False,  # ACFは必須ではない
                }
            )

        # 5. タームの作成（分類法に関連する）
        terms = components.get("terms", [])
        for term in terms:
            plan.append(
                {
                    "task_type": "create_term",
                    "agent": "taxonomy",
                    "description": f"ターム作成: {term.get('name', '未知')}",
                    "data": {
                        "type": "create_term",
                        "taxonomy": term.get("taxonomy"),
                        "name": term.get("name"),
                        "slug": term.get("slug"),
                        "description": term.get("description", ""),
                    },
                    "critical": False,
                }
            )

        print(f"📋 実行計画を作成: {len(plan)}ステップ")
        return plan

    async def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        個々のステップを実行

        Args:
            step: 実行ステップ

        Returns:
            実行結果
        """
        agent_type = step.get("agent")
        task_data = step.get("data", {})

        if agent_type not in self.agents:
            return {"success": False, "error": f"エージェント '{agent_type}' が見つかりません", "step": step}

        try:
            agent = self.agents[agent_type]
            result = await agent.execute(task_data)

            # 実行ログに記録
            self.execution_log.append(
                {
                    "step": self.current_step,
                    "agent": agent_type,
                    "task_type": step.get("task_type"),
                    "success": result.get("success", False),
                    "message": result.get("message", ""),
                    "error": result.get("error", ""),
                }
            )

            return result

        except Exception as e:
            error_msg = f"ステップ実行エラー: {str(e)}"

            # 実行ログに記録
            self.execution_log.append(
                {
                    "step": self.current_step,
                    "agent": agent_type,
                    "task_type": step.get("task_type"),
                    "success": False,
                    "error": error_msg,
                }
            )

            return {"success": False, "error": error_msg}

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        実行結果のサマリーを生成

        Args:
            results: 実行結果

        Returns:
            サマリー
        """
        total = results["total_steps"]
        completed = results["completed_steps"]
        success_rate = (completed / total) * 100 if total > 0 else 0

        # エージェント別の実行結果を集計
        agent_stats = {}
        for log_entry in self.execution_log:
            agent = log_entry["agent"]
            if agent not in agent_stats:
                agent_stats[agent] = {"total": 0, "success": 0}

            agent_stats[agent]["total"] += 1
            if log_entry["success"]:
                agent_stats[agent]["success"] += 1

        # 生成されたコードを収集
        generated_code = {}
        for result in results["results"]:
            if "php_code" in result:
                task_type = result.get("task_type", "unknown")
                generated_code[task_type] = result["php_code"]

        return {
            "success_rate": f"{success_rate:.1f}%",
            "completed_steps": f"{completed}/{total}",
            "agent_statistics": agent_stats,
            "generated_code_summary": {"count": len(generated_code), "types": list(generated_code.keys())},
            "errors_count": len(results["errors"]),
        }

    def get_execution_log(self) -> List[Dict[str, Any]]:
        """
        実行ログを取得

        Returns:
            実行ログ
        """
        return self.execution_log

    def get_generated_code(self) -> Dict[str, str]:
        """
        生成されたPHPコードを取得

        Returns:
            PHPコードの辞書
        """
        code_dict = {}
        for log_entry in self.execution_log:
            # ここでは実際のコード収集ロジックを実装
            # 現在はスタブ実装
            pass

        return code_dict


# テスト用の簡単な実行コード
if __name__ == "__main__":

    async def test():
        """テスト実行"""
        # テスト用の設計図
        test_design = {
            "title": "テストサイト構築",
            "components": {
                "plugins": [{"name": "Advanced Custom Fields", "slug": "advanced-custom-fields"}],
                "custom_post_types": [
                    {"name": "プロジェクト", "slug": "project", "description": "プロジェクトのカスタム投稿タイプ"}
                ],
                "taxonomies": [
                    {
                        "name": "プロジェクトカテゴリー",
                        "slug": "project-category",
                        "description": "プロジェクトの分類",
                        "hierarchical": True,
                    }
                ],
            },
        }

        # オーケストレーターを作成
        orchestrator = WordPressOrchestrator(
            test_design, {"url": "http://localhost/wordpress", "username": "admin", "password": "password"}
        )

        # 実行計画を作成（実行しない）
        plan = orchestrator._create_execution_plan()
        print(f"📋 テスト実行計画: {len(plan)}ステップ")

        for i, step in enumerate(plan, 1):
            print(f"  {i}. {step['description']}")

        print("✅ WordPressOrchestrator API版テスト完了")

    asyncio.run(test())
