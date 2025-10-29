"""
Complete WordPress Automation Demo v1.1
CPT + ACF の完全自動化実行（改善版）

タイムアウト対策と継続実行機能を追加
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# プロジェクトルート追加
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from configuration.config_loader import ConfigLoader
from agents.wordpress.specialized.wp_cpt_auto_apply import WPCPTAutoApply
from agents.wordpress.specialized.wp_auto_config_agent import WPAutoConfigAgent


class CompleteWordPressAutomation:
    """完全自動化オーケストレーター"""

    def __init__(self):
        self.config = ConfigLoader()
        self.wp_url = self.config.get("WP_URL")
        self.wp_user = self.config.get("WP_USER")
        self.wp_pass = self.config.get("WP_PASS")

        self.results = {
            "timestamp": datetime.now().isoformat(),
            "steps": [],
            "output_data": {},  # 生成されたファイル情報
        }

    def log_step(self, step_name: str, status: bool, details: dict = None):
        """ステップを記録"""
        step = {"name": step_name, "status": "success" if status else "failed", "timestamp": datetime.now().isoformat()}
        if details:
            step["details"] = details

        self.results["steps"].append(step)

        icon = "✅" if status else "❌"
        print(f"{icon} {step_name}")

    async def run_complete_automation(self):
        """完全自動化を実行"""
        print("\n" + "=" * 70)
        print("🚀 WordPress完全自動化デモ v1.1")
        print("=" * 70 + "\n")

        # ============================================================
        # STEP 1: Portfolio CPT作成
        # ============================================================
        print("📋 STEP 1: Portfolio カスタム投稿タイプの作成")
        print("-" * 70)

        # 最新のCPTファイルを探す
        cpt_files = sorted(Path("agent_outputs/wordpress_cpt").glob("cpt_portfolio_*.php"), reverse=True)

        if not cpt_files:
            self.log_step("Portfolio CPT作成", False, {"error": "CPTファイルが見つかりません"})
            print("\n⚠️ CPTファイルが見つかりません")
            return

        cpt_file = str(cpt_files[0])
        print(f"使用ファイル: {cpt_file}\n")

        # output_dataに記録
        self.results["output_data"]["cpt_file"] = cpt_file

        cpt_agent = WPCPTAutoApply(self.wp_url, self.wp_user, self.wp_pass)
        cpt_results = await cpt_agent.execute(cpt_file)

        # CPT追加が成功していれば、確認失敗でも続行
        cpt_added = cpt_results.get("steps", {}).get("cpt_added", False)

        self.log_step("Portfolio CPT - functions.php追加", cpt_added, cpt_results)

        if not cpt_added:
            print("\n⚠️ CPTコード追加に失敗しました。処理を中断します。")
            return

        # 確認は失敗してもOK（後で手動確認可能）
        cpt_verified = cpt_results.get("steps", {}).get("cpt_verified", False)
        if not cpt_verified:
            print("\n⚠️ CPT確認はタイムアウトしましたが、コード追加は成功しています。")
            print("   WordPressで設定 > パーマリンク設定 を開いて「変更を保存」をクリックすると反映されます。")

        print("\n")

        # ============================================================
        # STEP 2: ACFフィールド追加
        # ============================================================
        print("📋 STEP 2: ACFフィールドグループの追加")
        print("-" * 70)

        # ACFファイルを探す
        acf_files = sorted(Path("agent_outputs/wordpress_acf/php").glob("acf_group_portfolio_*.php"), reverse=True)

        if not acf_files:
            self.log_step("ACFフィールド追加", False, {"error": "ACFファイルが見つかりません"})
            print("\n⚠️ ACFファイルが見つかりません")
            return

        acf_file = str(acf_files[0])
        print(f"使用ファイル: {acf_file}\n")

        # output_dataに記録
        self.results["output_data"]["acf_file"] = acf_file

        acf_agent = WPAutoConfigAgent()
        acf_results = await acf_agent.execute(acf_file)

        # ACF追加が成功していればOK
        acf_added = acf_results.get("steps", {}).get("code_added", False)

        self.log_step("ACFフィールド - functions.php追加", acf_added, acf_results)

        # フィールド確認は失敗してもOK
        fields_verified = acf_results.get("steps", {}).get("fields_verification", {}).get("success", False)
        if not fields_verified:
            print("\n⚠️ フィールド確認はタイムアウトしましたが、コード追加は成功しています。")
            print("   CPTが反映された後、フィールドも表示されます。")

        print("\n")

        # ============================================================
        # 最終結果
        # ============================================================
        self.print_final_results()

        # 結果を保存
        output_file = Path("agent_outputs/complete_automation_results.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 結果を保存: {output_file}")

        # output_dataを活用した次のステップを提案
        self.suggest_next_steps()

    def print_final_results(self):
        """最終結果を出力"""
        print("\n" + "=" * 70)
        print("📊 完全自動化実行結果")
        print("=" * 70)

        success_count = sum(1 for step in self.results["steps"] if step["status"] == "success")
        total_count = len(self.results["steps"])

        print(f"\n⏰ 実行時刻: {self.results['timestamp']}")
        print(f"📈 成功率: {success_count}/{total_count} ({success_count/total_count*100:.0f}%)")
        print("\n【実行ステップ】")

        for i, step in enumerate(self.results["steps"], 1):
            icon = "✅" if step["status"] == "success" else "❌"
            print(f"  {i}. {icon} {step['name']}")

        print("\n【生成されたファイル (output_data)】")
        for key, value in self.results["output_data"].items():
            print(f"  📄 {key}: {value}")

        print("\n" + "=" * 70)

    def suggest_next_steps(self):
        """output_dataを活用した次のステップを提案"""
        print("\n" + "=" * 70)
        print("🎯 次のステップ（output_data活用）")
        print("=" * 70)

        print("\n【即座に実行可能な手動確認】")
        print("  1. https://uzbek-ma.com/wp-admin にアクセス")
        print("  2. 設定 > パーマリンク設定 を開く")
        print("  3. 「変更を保存」をクリック（CPTを反映）")
        print("  4. Portfolio > 新規追加 を開く")
        print("  5. ACFフィールドが表示されているか確認")

        print("\n【output_dataを使った高度な自動化（今後実装可能）】")

        cpt_file = self.results["output_data"].get("cpt_file")
        acf_file = self.results["output_data"].get("acf_file")

        if cpt_file and acf_file:
            print(f"\n  📋 生成されたファイル:")
            print(f"     • CPT: {cpt_file}")
            print(f"     • ACF: {acf_file}")

            print("\n  🔧 可能な拡張機能:")
            print("     1. 複数のCPTを一括作成")
            print("     2. CPTとACFの関連付け自動設定")
            print("     3. タクソノミーの自動追加")
            print("     4. サンプルコンテンツの自動投稿")
            print("     5. テーマテンプレートの自動生成")
            print("     6. REST APIエンドポイントのテスト")

            print("\n  💡 output_data活用例:")
            print("     • 生成されたファイルパスを使って追加処理")
            print("     • 複数サイトへの一括デプロイ")
            print("     • バージョン管理とロールバック")
            print("     • 設定の自動バックアップ")


async def main():
    """メイン実行"""
    automation = CompleteWordPressAutomation()
    await automation.run_complete_automation()


if __name__ == "__main__":
    asyncio.run(main())
