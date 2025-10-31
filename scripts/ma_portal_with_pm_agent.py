#!/usr/bin/env python3
"""
M&Aポータル構築 with PM Agent連携
変更理由: 自律型エージェントシステムを開発アシスタントとして活用
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from wordpress.wp_dev.wp_simple_agents import SimpleCPTAgent, SimpleACFAgent, SimplePostCreator
from tools.sheets_manager import GoogleSheetsManager


class MAPortalWithPMAgent:
    """PM Agent連携版 M&Aポータル構築"""

    def __init__(self):
        self.sheets = GoogleSheetsManager()
        self.cpt_agent = SimpleCPTAgent()
        self.acf_agent = SimpleACFAgent()
        self.post_creator = SimplePostCreator()

    def run_full_workflow(self):
        """完全な構築ワークフロー"""
        print("🚀 M&Aポータル構築ワークフロー開始")
        print("=" * 70)

        # Step 1: WordPress接続確認
        print("\n📡 Step 1: WordPress接続確認")
        if not self.cpt_agent.test_connection():
            print("❌ WordPress接続失敗 - 処理を中止")
            return False

        print("✅ WordPress接続成功")

        # Step 2: カスタム投稿タイプ作成（手動実装案を提示）
        print("\n📄 Step 2: カスタム投稿タイプ作成")
        cpt_result = self.cpt_agent.create_ma_company_cpt()

        if cpt_result["success"]:
            print("\n以下のコードを functions.php に追加してください:")
            print("-" * 70)
            print(cpt_result["php_code"])
            print("-" * 70)

        # Step 3: カスタムフィールド設定
        print("\n📝 Step 3: カスタムフィールド設定")
        acf_result = self.acf_agent.create_ma_fields()

        if acf_result["success"]:
            print("\nACFプラグインで以下のフィールドを設定:")
            for field_name, field_config in acf_result["fields"].items():
                print(f"  • {field_config['label']} ({field_config['type']})")

        # Step 4: デモデータ作成
        print("\n📊 Step 4: デモ企業データ作成")
        demo_companies = self._get_demo_companies()

        print(f"\n{len(demo_companies)}社のデモデータを準備:")
        for company in demo_companies:
            print(f"  • {company['title']}")

        # Step 5: pm_tasks にタスク登録（PM Agent連携）
        print("\n📋 Step 5: pm_tasks にタスク登録")
        self._register_tasks_to_pm()

        print("\n" + "=" * 70)
        print("✅ ワークフロー完了")
        print("=" * 70)

        print("\n📝 次のアクション:")
        print("  1. functions.php にPHPコードを追加")
        print("  2. ACFプラグインでフィールド設定")
        print("  3. カスタム投稿タイプ「M&A企業情報」でデモデータ入力")
        print("  4. 検索機能の実装")

        return True

    def _get_demo_companies(self):
        """デモ企業データ"""
        return [
            {
                "title": "テックカンパニーA",
                "industry": "IT・ソフトウェア",
                "location": "東京都渋谷区",
                "capital": 10000,
                "employees": 50,
                "revenue": 100000,
                "deal_type": "売却希望",
                "content": "AIを活用したSaaSプロダクトを展開する成長企業。直近3年の売上成長率は年平均40%。",
            },
            {
                "title": "製造業B",
                "industry": "製造業",
                "location": "愛知県名古屋市",
                "capital": 5000,
                "employees": 30,
                "revenue": 50000,
                "deal_type": "売却希望",
                "content": "精密部品製造で高いシェアを持つ中堅企業。自動車業界向けが主力。",
            },
            {
                "title": "サービスC",
                "industry": "サービス業",
                "location": "大阪府大阪市",
                "capital": 3000,
                "employees": 20,
                "revenue": 30000,
                "deal_type": "買収希望",
                "content": "介護・福祉サービスで地域に根ざした事業展開。施設数拡大を検討。",
            },
            {
                "title": "小売店D",
                "industry": "小売業",
                "location": "福岡県福岡市",
                "capital": 2000,
                "employees": 15,
                "revenue": 20000,
                "deal_type": "売却希望",
                "content": "地域密着型のスーパーマーケットチェーン。店舗数5店舗。",
            },
            {
                "title": "建設E",
                "industry": "建設業",
                "location": "北海道札幌市",
                "capital": 15000,
                "employees": 80,
                "revenue": 150000,
                "deal_type": "買収希望",
                "content": "公共工事を中心とした総合建設会社。事業エリア拡大を検討。",
            },
        ]

    def _register_tasks_to_pm(self):
        """pm_tasks にタスクを登録（PM Agent連携）"""

        tasks = [
            {
                "task_id": "MA_PORTAL_1",
                "task_description": "カスタム投稿タイプ ma_company を functions.php に実装",
                "status": "pending",
                "required_role": "wordpress",
                "priority": "high",
            },
            {
                "task_id": "MA_PORTAL_2",
                "task_description": "ACFでカスタムフィールド（所在地、資本金、従業員数、年商、希望条件）を設定",
                "status": "pending",
                "required_role": "wordpress",
                "priority": "high",
            },
            {
                "task_id": "MA_PORTAL_3",
                "task_description": "デモ企業データ5社を入力",
                "status": "pending",
                "required_role": "content",
                "priority": "medium",
            },
            {
                "task_id": "MA_PORTAL_4",
                "task_description": "検索フォームと検索結果表示ページを実装",
                "status": "pending",
                "required_role": "dev",
                "priority": "high",
            },
        ]

        try:
            # 既存のpm_tasksを読み込み
            existing_data = self.sheets.read_range("pm_tasks")

            if not existing_data:
                headers = ["task_id", "task_description", "status", "required_role", "priority"]
                new_data = [headers]
            else:
                new_data = existing_data

            # タスクを追加
            for task in tasks:
                new_data.append(
                    [
                        task["task_id"],
                        task["task_description"],
                        task["status"],
                        task["required_role"],
                        task["priority"],
                    ]
                )

            # pm_tasksに書き込み
            self.sheets.write_range("pm_tasks", new_data)

            print(f"✅ {len(tasks)}件のタスクを pm_tasks に登録")

        except Exception as e:
            print(f"⚠️ pm_tasks登録エラー: {e}")


def main():
    print("🚀 M&Aポータル構築（PM Agent連携版）")

    builder = MAPortalWithPMAgent()
    builder.run_full_workflow()


if __name__ == "__main__":
    main()
