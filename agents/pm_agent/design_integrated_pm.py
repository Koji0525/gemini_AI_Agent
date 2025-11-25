#!/usr/bin/env python3
"""
設計図統合版PM Agent
目標から自動的に設計図を生成し、WordPress設定を実行する
"""
import asyncio
import sys
from datetime import datetime
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from browser_control.browser_controller import BrowserController
from configuration.config_loader import ConfigLoader
from tools.sheets_manager import GoogleSheetsManager


class DesignIntegratedPMAgent:
    """設計図統合版PM Agent"""

    def __init__(self, sheets_manager: GoogleSheetsManager, browser_controller: BrowserController):
        self.sheets = sheets_manager
        self.browser = browser_controller
        self.designs = {}

    async def process_goal_with_design(self, goal_id: int) -> dict:
        """目標を設計図を含めて処理"""
        print(f"🎯 目標 {goal_id} を設計図統合で処理します")

        # 1. 目標情報を取得
        goal_info = await self._get_goal_info(goal_id)
        if not goal_info:
            return {"success": False, "error": "目標情報の取得に失敗"}

        # 2. WordPress関連目標か判定
        if not self._is_wordpress_related_goal(goal_info):
            print("ℹ️ WordPress関連目標ではないため、通常のタスク分解を実行")
            return await self._process_normal_goal(goal_info)

        # 3. 設計図を生成
        print("�� WordPress設計図を生成中...")
        design = await self._generate_wordpress_design(goal_info)

        if not design:
            print("❌ 設計図生成に失敗したため、通常のタスク分解にフォールバック")
            return await self._process_normal_goal(goal_info)

        # 4. 設計図からタスクを生成
        tasks = await self._create_tasks_from_design(design, goal_info)

        # 5. タスクを登録
        registration_result = await self._register_tasks(tasks, goal_info)

        # 6. 設計図を保存
        await self._save_design(design, goal_info)

        return {
            "success": True,
            "goal_id": goal_id,
            "design_generated": True,
            "design_info": {
                "site_type": design.get("site_type"),
                "site_name": design.get("site_name"),
                "components": len(design.get("custom_post_types", []))
                + len(design.get("taxonomies", [])),
            },
            "tasks_generated": len(tasks),
            "registration_result": registration_result,
        }

    async def _get_goal_info(self, goal_id: int) -> dict:
        """目標情報を取得"""
        try:
            spreadsheet = self.sheets.gc.open_by_key(self.sheets.spreadsheet_id)
            goal_sheet = spreadsheet.worksheet("project_goal")
            goals = goal_sheet.get_all_records()

            for goal in goals:
                if goal.get("id") == goal_id:
                    return goal

            return None
        except Exception as e:
            print(f"❌ 目標情報取得エラー: {e}")
            return None

    def _is_wordpress_related_goal(self, goal_info: dict) -> bool:
        """WordPress関連目標か判定"""
        title = goal_info.get("title", "").lower()
        description = goal_info.get("description", "").lower()

        wordpress_keywords = [
            "wordpress",
            "wp",
            "サイト",
            "website",
            "webサイト",
            "ポータル",
            "portal",
            "ブログ",
            "blog",
            "cms",
            "カスタム投稿",
            "custom post",
            "プラグイン",
            "plugin",
            "テーマ",
            "theme",
            "多言語",
            "multilingual",
        ]

        # タイトルまたは説明にWordPress関連キーワードが含まれているか
        for keyword in wordpress_keywords:
            if keyword in title or keyword in description:
                return True

        return False

    async def _generate_wordpress_design(self, goal_info: dict) -> dict:
        """WordPress設計図を生成"""
        try:
            # 設計図生成エージェントをインポート
            from agents.wordpress.wp_design_generator import WPDesignGenerator

            design_generator = WPDesignGenerator(self.browser)
            goal_description = f"{goal_info.get('title', '')} - {goal_info.get('description', '')}"

            design = await design_generator.generate_design_from_goal(goal_description)
            return design

        except Exception as e:
            print(f"❌ 設計図生成エラー: {e}")
            return None

    async def _create_tasks_from_design(self, design: dict, goal_info: dict) -> list:
        """設計図からタスクを生成"""
        tasks = []
        goal_id = goal_info.get("id", "unknown")

        # 基本設定タスク
        tasks.append(
            {
                "title": f"{design.get('site_name', 'WordPressサイト')} - 基本設定",
                "description": f"WordPressサイトの基本設定: {design.get('description', '')}",
                "goal_id": goal_id,
                "agent": "wordpress",
                "priority": "high",
                "execution_type": "wordpress",
                "estimated_hours": 2,
            }
        )

        # プラグイン設定タスク
        plugins = design.get("required_plugins", [])
        if plugins:
            tasks.append(
                {
                    "title": f"プラグイン設定: {', '.join(plugins)}",
                    "description": f"必要なプラグインのインストールと設定: {', '.join(plugins)}",
                    "goal_id": goal_id,
                    "agent": "wordpress/wp_plugin_manager",
                    "priority": "high",
                    "execution_type": "wordpress",
                    "estimated_hours": 1,
                }
            )

        # カスタム投稿タイプタスク
        cpt_list = design.get("custom_post_types", [])
        for cpt in cpt_list:
            tasks.append(
                {
                    "title": f"カスタム投稿タイプ作成: {cpt.get('name', 'unknown')}",
                    "description": f"カスタム投稿タイプ '{cpt.get('singular_name', 'unknown')}' の作成",
                    "goal_id": goal_id,
                    "agent": "wordpress/wp_cpt_agent",
                    "priority": "medium",
                    "execution_type": "wordpress",
                    "estimated_hours": 1,
                }
            )

        # タクソノミータスク
        taxonomies = design.get("taxonomies", [])
        for taxonomy in taxonomies:
            tasks.append(
                {
                    "title": f"タクソノミー作成: {taxonomy.get('name', 'unknown')}",
                    "description": f"タクソノミー '{taxonomy.get('name', 'unknown')}' の作成",
                    "goal_id": goal_id,
                    "agent": "wordpress/wp_taxonomy_agent",
                    "priority": "medium",
                    "execution_type": "wordpress",
                    "estimated_hours": 1,
                }
            )

        # ACFフィールドタスク
        for cpt in cpt_list:
            fields = cpt.get("fields", [])
            if fields:
                tasks.append(
                    {
                        "title": f"ACFフィールド設定: {cpt.get('name', 'unknown')}",
                        "description": f"カスタムフィールドの設定: {len(fields)}個のフィールド",
                        "goal_id": goal_id,
                        "agent": "wordpress/wp_acf_agent",
                        "priority": "medium",
                        "execution_type": "wordpress",
                        "estimated_hours": 2,
                    }
                )

        print(f"📋 設計図から {len(tasks)} 個のタスクを生成しました")
        return tasks

    async def _register_tasks(self, tasks: list, goal_info: dict) -> dict:
        """タスクを登録"""
        try:
            from agents.pm_agent.task_registration import TaskRegistrationAgent

            registration_agent = TaskRegistrationAgent(self.sheets)
            result = await registration_agent.register_tasks(tasks)

            return result

        except Exception as e:
            print(f"❌ タスク登録エラー: {e}")
            return {"success": False, "error": str(e)}

    async def _save_design(self, design: dict, goal_info: dict):
        """設計図を保存"""
        try:
            # 設計図をGoogle Sheetsに保存（新しいシートを作成）
            spreadsheet = self.sheets.gc.open_by_key(self.sheets.spreadsheet_id)

            # 設計図シートが存在するか確認
            try:
                design_sheet = spreadsheet.worksheet("wordpress_designs")
            except:
                # シートがなければ作成
                design_sheet = spreadsheet.add_worksheet(
                    title="wordpress_designs", rows=1000, cols=20
                )
                # ヘッダー行を設定
                design_sheet.append_rows(
                    [
                        "design_id",
                        "goal_id",
                        "site_name",
                        "site_type",
                        "generated_date",
                        "cpt_count",
                        "taxonomy_count",
                        "plugins",
                    ]
                )

            # 設計図を追加
            design_sheet.append_rows(
                [
                    f"design_{int(datetime.now().timestamp())}",
                    goal_info.get("id", "unknown"),
                    design.get("site_name", "Unknown"),
                    design.get("site_type", "unknown"),
                    datetime.now().isoformat(),
                    len(design.get("custom_post_types", [])),
                    len(design.get("taxonomies", [])),
                    ", ".join(design.get("required_plugins", [])),
                ]
            )

            print("💾 設計図をGoogle Sheetsに保存しました")

        except Exception as e:
            print(f"⚠️ 設計図のGoogle Sheets保存に失敗: {e}")


async def test_design_integrated_pm():
    """設計図統合PM Agentのテスト"""
    try:
        print("�� 設計図統合PM Agent テスト開始")

        # 設定読み込み
        config = ConfigLoader()
        spreadsheet_id = config.get("SPREADSHEET_ID")
        service_account_file = config.get("GOOGLE_SERVICE_ACCOUNT_FILE")

        # ブラウザとSheetsManagerを初期化
        browser = BrowserController()

        sheets = GoogleSheetsManager(spreadsheet_id, service_account_file)

        # 設計図統合PM Agentを作成
        pm_agent = DesignIntegratedPMAgent(sheets, browser)

        # テスト用の目標ID（実際の目標IDに置き換える）
        test_goal_id = 4  # 仮の目標ID

        # 設計図統合で目標を処理
        result = await pm_agent.process_goal_with_design(test_goal_id)

        print("📊 処理結果:")
        print(f"  成功: {result.get('success', False)}")
        print(f"  設計図生成: {result.get('design_generated', False)}")
        if result.get("design_generated"):
            design_info = result.get("design_info", {})
            print(f"  サイト名: {design_info.get('site_name')}")
            print(f"  コンポーネント数: {design_info.get('components')}")
        print(f"  生成タスク数: {result.get('tasks_generated', 0)}")

        # クリーンアップ
        await browser.cleanup()

    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_design_integrated_pm())
