#!/usr/bin/env python3
"""
WordPressオーケストレーター - 設計図実行の統合マネージャー
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from browser_control.browser_controller import BrowserController
from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import ConfigLoader

class WordPressOrchestrator:
    """WordPress設計図実行オーケストレーター"""
    
    def __init__(self, browser_controller: BrowserController, sheets_manager: GoogleSheetsManager):
        self.browser = browser_controller
        self.sheets = sheets_manager
        self.execution_plan = {}
        self.current_design = {}
        
    async def execute_design_plan(self, design_spec: Dict[str, Any]) -> Dict[str, Any]:
        """設計図を実行するメイン関数"""
        print("🎬 WordPress設計図実行を開始します")
        
        # 1. 設計図の検証
        if not await self._validate_design(design_spec):
            return {"success": False, "error": "設計図の検証に失敗しました"}
        
        # 2. 実行計画の作成
        execution_plan = await self._create_execution_plan(design_spec)
        
        # 3. 専門エージェントの初期化
        agents = await self._initialize_specialized_agents()
        
        # 4. 実行の実行
        results = await self._execute_plan(execution_plan, agents)
        
        # 5. 結果の検証
        validation = await self._validate_results(design_spec, results)
        
        # 6. レポート生成
        report = await self._generate_execution_report(design_spec, results, validation)
        
        return report
    
    async def _validate_design(self, design_spec: Dict[str, Any]) -> bool:
        """設計図の検証"""
        print("🔍 設計図を検証中...")
        
        required_fields = ["site_type", "custom_post_types", "taxonomies", "required_plugins"]
        for field in required_fields:
            if field not in design_spec:
                print(f"❌ 必須フィールド '{field}' が設計図にありません")
                return False
        
        print("✅ 設計図の検証が完了しました")
        return True
    
    async def _create_execution_plan(self, design_spec: Dict[str, Any]) -> Dict[str, Any]:
        """設計図から実行計画を作成"""
        print("📋 実行計画を作成中...")
        
        plan = {
            "design_id": design_spec.get("site_type", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "phases": [],
            "dependencies": {}
        }
        
        # フェーズ1: 基本設定
        if design_spec.get("required_plugins"):
            plan["phases"].append({
                "name": "plugin_setup",
                "tasks": self._create_plugin_tasks(design_spec["required_plugins"]),
                "description": "必要なプラグインのインストールと有効化"
            })
        
        # フェーズ2: カスタム投稿タイプ
        if design_spec.get("custom_post_types"):
            plan["phases"].append({
                "name": "cpt_setup", 
                "tasks": self._create_cpt_tasks(design_spec["custom_post_types"]),
                "description": "カスタム投稿タイプの作成"
            })
        
        # フェーズ3: タクソノミー
        if design_spec.get("taxonomies"):
            plan["phases"].append({
                "name": "taxonomy_setup",
                "tasks": self._create_taxonomy_tasks(design_spec["taxonomies"]),
                "description": "分類（タクソノミー）の設定"
            })
        
        # フェーズ4: ACFフィールド
        cpt_list = design_spec.get("custom_post_types", [])
        acf_tasks = self._create_acf_tasks(cpt_list)
        if acf_tasks:
            plan["phases"].append({
                "name": "acf_setup",
                "tasks": acf_tasks,
                "description": "カスタムフィールドの設定"
            })
        
        print(f"✅ 実行計画を作成しました: {len(plan['phases'])}フェーズ")
        return plan
    
    def _create_plugin_tasks(self, plugins: List[str]) -> List[Dict[str, Any]]:
        """プラグイン設定タスクを作成"""
        tasks = []
        for plugin in plugins:
            tasks.append({
                "type": "plugin_installation",
                "plugin_name": plugin,
                "agent": "wp_plugin_manager",
                "priority": "high",
                "estimated_time": 5  # 分
            })
        return tasks
    
    def _create_cpt_tasks(self, custom_post_types: List[Dict]) -> List[Dict[str, Any]]:
        """カスタム投稿タイプタスクを作成"""
        tasks = []
        for cpt in custom_post_types:
            tasks.append({
                "type": "cpt_creation",
                "cpt_spec": cpt,
                "agent": "wp_cpt_agent", 
                "priority": "high",
                "estimated_time": 10
            })
        return tasks
    
    def _create_taxonomy_tasks(self, taxonomies: List[Dict]) -> List[Dict[str, Any]]:
        """タクソノミータスクを作成"""
        tasks = []
        for taxonomy in taxonomies:
            tasks.append({
                "type": "taxonomy_creation",
                "taxonomy_spec": taxonomy,
                "agent": "wp_taxonomy_agent",
                "priority": "medium",
                "estimated_time": 8
            })
        return tasks
    
    def _create_acf_tasks(self, custom_post_types: List[Dict]) -> List[Dict[str, Any]]:
        """ACFフィールドタスクを作成"""
        tasks = []
        for cpt in custom_post_types:
            fields = cpt.get("fields", [])
            if fields:
                tasks.append({
                    "type": "acf_field_creation",
                    "cpt_name": cpt.get("name"),
                    "fields": fields,
                    "agent": "wp_acf_agent",
                    "priority": "medium",
                    "estimated_time": 15
                })
        return tasks
    
    async def _initialize_specialized_agents(self) -> Dict[str, Any]:
        """専門エージェントを初期化"""
        print("🤖 専門エージェントを初期化中...")
        
        agents = {}
        
        try:
            # プラグイン管理エージェント
            from wordpress.wp_plugin_manager import WordPressPluginManager
            agents["wp_plugin_manager"] = WordPressPluginManager(self.browser)
            
            # CPTエージェント
            from wordpress.wp_dev.wp_cpt_agent import WordPressCPTAgent
            agents["wp_cpt_agent"] = WordPressCPTAgent(self.browser, Path("agent_outputs"))
            
            # タクソノミーエージェント
            from wordpress.wp_dev.wp_taxonomy_agent import WordPressTaxonomyAgent
            agents["wp_taxonomy_agent"] = WordPressTaxonomyAgent(self.browser, Path("agent_outputs"))
            
            # ACFエージェント
            from wordpress.wp_dev.wp_acf_agent import WordPressACFAgent
            agents["wp_acf_agent"] = WordPressACFAgent(self.browser, Path("agent_outputs"))
            
            print("✅ 専門エージェントの初期化が完了しました")
            
        except ImportError as e:
            print(f"❌ エージェントのインポートエラー: {e}")
        
        return agents
    
    async def _execute_plan(self, execution_plan: Dict[str, Any], agents: Dict[str, Any]) -> Dict[str, Any]:
        """実行計画を実行"""
        print("🚀 実行計画を実行中...")
        
        results = {
            "phase_results": [],
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0
        }
        
        for phase in execution_plan["phases"]:
            print(f"\n--- {phase['name']}: {phase['description']} ---")
            
            phase_result = {
                "phase_name": phase["name"],
                "task_results": [],
                "start_time": datetime.now().isoformat()
            }
            
            for task in phase["tasks"]:
                results["total_tasks"] += 1
                task_result = await self._execute_single_task(task, agents)
                phase_result["task_results"].append(task_result)
                
                if task_result.get("success"):
                    results["successful_tasks"] += 1
                else:
                    results["failed_tasks"] += 1
            
            phase_result["end_time"] = datetime.now().isoformat()
            results["phase_results"].append(phase_result)
        
        print(f"✅ 実行完了: {results['successful_tasks']}/{results['total_tasks']} タスク成功")
        return results
    
    async def _execute_single_task(self, task: Dict[str, Any], agents: Dict[str, Any]) -> Dict[str, Any]:
        """単一タスクを実行"""
        agent_type = task.get("agent")
        task_type = task.get("type")
        
        print(f"  🔧 実行中: {task_type} ({agent_type})")
        
        if agent_type not in agents:
            return {
                "success": False,
                "error": f"エージェント '{agent_type}' が見つかりません",
                "task_type": task_type
            }
        
        try:
            agent = agents[agent_type]
            result = await agent.execute(task)
            
            if result.get("success"):
                print(f"  ✅ 完了: {task_type}")
            else:
                print(f"  ❌ 失敗: {task_type} - {result.get('error', '不明なエラー')}")
            
            return result
            
        except Exception as e:
            print(f"  ❌ 実行エラー: {task_type} - {e}")
            return {
                "success": False,
                "error": str(e),
                "task_type": task_type
            }
    
    async def _validate_results(self, design_spec: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """実行結果を検証"""
        print("🔍 実行結果を検証中...")
        
        # ここでは簡易的な検証を行う
        validation = {
            "overall_success": results["failed_tasks"] == 0,
            "validation_checks": [],
            "issues_found": []
        }
        
        # 成功タスク数の検証
        if results["successful_tasks"] == results["total_tasks"]:
            validation["validation_checks"].append({
                "check": "all_tasks_completed",
                "status": "passed",
                "message": "すべてのタスクが正常に完了しました"
            })
        else:
            validation["validation_checks"].append({
                "check": "all_tasks_completed", 
                "status": "failed",
                "message": f"{results['failed_tasks']}個のタスクが失敗しました"
            })
            validation["issues_found"].append("一部のタスクが失敗しました")
        
        print("✅ 検証完了")
        return validation
    
    async def _generate_execution_report(self, design_spec: Dict[str, Any], 
                                       results: Dict[str, Any], 
                                       validation: Dict[str, Any]) -> Dict[str, Any]:
        """実行レポートを生成"""
        report = {
            "design_spec": design_spec,
            "execution_summary": {
                "total_tasks": results["total_tasks"],
                "successful_tasks": results["successful_tasks"],
                "failed_tasks": results["failed_tasks"],
                "success_rate": results["successful_tasks"] / results["total_tasks"] if results["total_tasks"] > 0 else 0
            },
            "validation_results": validation,
            "phase_details": results["phase_results"],
            "timestamp": datetime.now().isoformat(),
            "overall_success": validation["overall_success"]
        }
        
        # レポートをファイルに保存
        report_dir = Path("agent_outputs/execution_reports")
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"wp_execution_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📊 実行レポートを保存: {report_file}")
        return report

async def test_orchestrator():
    """オーケストレーターのテスト"""
    try:
        print("🎬 WordPressオーケストレーター テスト開始")
        
        # 設定読み込み
        config = ConfigLoader()
        spreadsheet_id = config.get("SPREADSHEET_ID")
        service_account_file = config.get("GOOGLE_SERVICE_ACCOUNT_FILE")
        
        # ブラウザとSheetsManagerを初期化
        browser = BrowserController()
        
        sheets = GoogleSheetsManager(spreadsheet_id, service_account_file)
        
        # オーケストレーターを作成
        orchestrator = WordPressOrchestrator(browser, sheets)
        
        # テスト用設計図
        test_design = {
            "site_type": "ma_portal",
            "site_name": "テストM&Aポータル",
            "custom_post_types": [
                {
                    "name": "ma_case",
                    "singular_name": "M&A案件",
                    "plural_name": "M&A案件",
                    "description": "M&A案件情報",
                    "fields": [
                        {"name": "price", "type": "number", "required": True},
                        {"name": "industry", "type": "text", "required": True}
                    ]
                }
            ],
            "taxonomies": [
                {
                    "name": "industry_category",
                    "post_types": ["ma_case"],
                    "hierarchical": True
                }
            ],
            "required_plugins": ["polylang", "advanced-custom-fields"]
        }
        
        # 設計図実行
        result = await orchestrator.execute_design_plan(test_design)
        
        print("🎉 テスト完了:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # クリーンアップ
        await browser.cleanup()
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_orchestrator())
