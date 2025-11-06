#!/usr/bin/env python3
"""
Phase 1: 基本的な設定確認スクリプト（実際の構造対応版）
WordPress接続テスト、サイト情報取得、エージェント状態確認

v1.0 - 初回実装
v1.1 - エージェント検出ロジックを実際の構造に合わせて修正
v1.2 - 実際に存在するファイルのみを確認するように修正
運用ルール準拠: 1ファイル1000行以下、PEP 8準拠
"""

import os
import sys
import asyncio
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
from dotenv import load_dotenv

# プロジェクトルートをパスに追加
sys.path.insert(0, "/workspaces/gemini_AI_Agent")

from configuration.config_loader import ConfigLoader


class ConfigValidator:
    """設定確認を実行するクラス（Phase 1）"""

    def __init__(self):
        """初期化"""
        self.config = ConfigLoader()
        self.validation_result = {
            "wp_connection": {},
            "rest_api": {},
            "site_info": {},
            "agents": {},
            "errors": [],
            "report_path": "",
        }

    async def run_validation(self) -> Dict[str, Any]:
        """
        設定確認を実行

        Returns:
            Dict: 確認結果
        """
        print("=" * 80)
        print("🚀 Phase 1: 基本的な設定確認を開始します (v1.2)")
        print("=" * 80)

        # 1. WordPress接続テスト
        print("\n📡 STEP 1: WordPress接続テスト")
        await self._test_wordpress_connection()

        # 2. サイト情報取得
        print("\n📊 STEP 2: サイト情報取得")
        await self._fetch_site_info()

        # 3. エージェント状態確認
        print("\n🤖 STEP 3: エージェント状態確認")
        await self._check_agent_status()

        # 4. 重要モジュールの確認
        print("\n🔧 STEP 4: 重要モジュール確認")
        await self._check_important_modules()

        # 5. 結果サマリー表示
        print("\n" + "=" * 80)
        print("✅ Phase 1: 設定確認が完了しました")
        print("=" * 80)
        self._print_summary()

        return self.validation_result

    async def _test_wordpress_connection(self) -> None:
        """WordPress接続テスト"""
        try:
            wp_url = self.config._config.get("WP_URL")
            wp_user = self.config._config.get("wp_user")
            wp_pass = self.config._config.get("wp_pass")

            if not all([wp_url, wp_user, wp_pass]):
                self.validation_result["wp_connection"] = {
                    "status": "failed",
                    "error": "WordPress設定が不完全です (.env を確認)",
                }
                print("❌ WordPress設定が不完全です")
                return

            # 基本的な接続テスト
            print(f"   URL: {wp_url}")
            response = requests.get(wp_url, timeout=10)

            if response.status_code == 200:
                self.validation_result["wp_connection"] = {
                    "status": "success",
                    "url": wp_url,
                    "status_code": response.status_code,
                }
                print(f"✅ WordPress接続成功 (Status: {response.status_code})")
            else:
                self.validation_result["wp_connection"] = {
                    "status": "warning",
                    "url": wp_url,
                    "status_code": response.status_code,
                    "error": f"予期しないステータスコード: {response.status_code}",
                }
                print(f"⚠️  接続成功だが予期しないステータス: {response.status_code}")

        except Exception as e:
            self.validation_result["wp_connection"] = {"status": "failed", "error": str(e)}
            print(f"❌ WordPress接続失敗: {e}")
            self.validation_result["errors"].append(f"WordPress接続: {e}")

    async def _fetch_site_info(self) -> None:
        """サイト情報取得"""
        try:
            wp_url = self.config._config.get("WP_URL")
            wp_user = self.config._config.get("wp_user")
            wp_pass = self.config._config.get("wp_pass")

            if self.validation_result["wp_connection"].get("status") != "success":
                print("⏭️  WordPress接続が成功していないため、スキップします")
                return

            # REST API エンドポイント
            api_base = f"{wp_url}/wp-json/wp/v2"
            auth = (wp_user, wp_pass)

            # REST API利用可能性チェック
            try:
                response = requests.get(api_base, auth=auth, timeout=10)
                if response.status_code in [200, 401]:  # 401も接続は成功
                    self.validation_result["rest_api"] = {
                        "available": True,
                        "limited": response.status_code == 401,
                    }
                    print(f"✅ REST API利用可能")
                    if response.status_code == 401:
                        print("   ℹ️  認証が必要な操作は制限される可能性があります")
                else:
                    self.validation_result["rest_api"] = {"available": False}
                    print(f"❌ REST API利用不可 (Status: {response.status_code})")
                    return
            except Exception as e:
                self.validation_result["rest_api"] = {"available": False}
                print(f"❌ REST APIチェック失敗: {e}")
                return

            # サイト情報を取得
            site_info = {}

            # 投稿タイプ取得
            try:
                response = requests.get(f"{api_base}/types", auth=auth, timeout=10)
                if response.status_code == 200:
                    post_types = response.json()
                    site_info["post_types"] = len(post_types)
                    print(f"   📝 投稿タイプ: {len(post_types)}個")
                else:
                    print(f"   ⚠️  投稿タイプ取得失敗 (Status: {response.status_code})")
            except Exception as e:
                print(f"   ⚠️  投稿タイプ取得エラー: {e}")

            # プラグイン情報取得（401エラーは正常動作の範囲内）
            try:
                response = requests.get(f"{wp_url}/wp-json/wp/v2/plugins", auth=auth, timeout=10)
                if response.status_code == 200:
                    plugins = response.json()
                    site_info["plugins"] = len(plugins)
                    print(f"   🔌 プラグイン: {len(plugins)}個")
                elif response.status_code == 401:
                    print(f"   ℹ️  プラグイン情報: 認証が必要（スキップ）")
                elif response.status_code == 404:
                    print(f"   ℹ️  プラグインエンドポイント未対応")
                else:
                    print(f"   ⚠️  プラグイン情報取得失敗 (Status: {response.status_code})")
            except Exception as e:
                print(f"   ⚠️  プラグイン情報取得エラー: {e}")

            # テーマ情報取得（401エラーは正常動作の範囲内）
            try:
                response = requests.get(f"{api_base}/themes", auth=auth, timeout=10)
                if response.status_code == 200:
                    themes = response.json()
                    if themes:
                        active_theme = next(
                            (t for t in themes if t.get("status") == "active"), None
                        )
                        if active_theme:
                            site_info["theme"] = {
                                "name": active_theme.get("name", "Unknown"),
                                "version": active_theme.get("version", "Unknown"),
                            }
                            print(f"   🎨 テーマ: {active_theme.get('name')}")
                elif response.status_code == 401:
                    print(f"   ℹ️  テーマ情報: 認証が必要（スキップ）")
                elif response.status_code == 404:
                    print(f"   ℹ️  テーマエンドポイント未対応")
                else:
                    print(f"   ⚠️  テーマ情報取得失敗 (Status: {response.status_code})")
            except Exception as e:
                print(f"   ⚠️  テーマ情報取得エラー: {e}")

            self.validation_result["site_info"] = site_info

        except Exception as e:
            print(f"❌ サイト情報取得失敗: {e}")
            self.validation_result["errors"].append(f"サイト情報取得: {e}")

    async def _check_agent_status(self) -> None:
        """エージェント状態確認（実際に存在するファイルのみ）"""
        try:
            agents_status = {}

            # 実装済みWordPressエージェント
            implemented_agents = [
                ("wp_design_agent", "agents/wordpress/wp_design_agent.py"),
                ("wp_design_generator", "agents/wordpress/wp_design_generator.py"),
                ("wp_orchestrator", "agents/wordpress/wp_orchestrator.py"),
            ]

            # 計画中のエージェント（未実装）
            planned_agents = [
                ("wp_cpt_agent", "agents/wordpress/specialized/wp_cpt_agent.py"),
                ("wp_taxonomy_agent", "agents/wordpress/specialized/wp_taxonomy_agent.py"),
                ("wp_acf_agent", "agents/wordpress/specialized/wp_acf_agent.py"),
                ("wp_plugin_manager", "agents/wordpress/wp_plugin_manager.py"),
                ("wp_settings_manager", "agents/wordpress/wp_settings_manager.py"),
                ("wp_auth", "agents/wordpress/wp_auth.py"),
                ("wp_post_editor", "agents/wordpress/wp_post_editor.py"),
                ("wp_post_creator", "agents/wordpress/wp_post_creator.py"),
            ]

            print("   --- 実装済みエージェント ---")
            for agent_name, agent_file in implemented_agents:
                full_path = f"/workspaces/gemini_AI_Agent/{agent_file}"
                if os.path.exists(full_path):
                    # ファイルサイズを確認（空ファイルかどうか）
                    file_size = os.path.getsize(full_path)
                    if file_size > 0:
                        agents_status[agent_name] = "initialized"
                        print(f"   ✅ {agent_name}: 利用可能 ({file_size} bytes)")
                    else:
                        agents_status[agent_name] = "empty"
                        print(f"   ⚠️  {agent_name}: ファイルが空です")
                else:
                    agents_status[agent_name] = "not_found"
                    print(f"   ❌ {agent_name}: ファイルが見つかりません")

            print("   --- 計画中エージェント（未実装） ---")
            planned_count = 0
            for agent_name, agent_file in planned_agents:
                full_path = f"/workspaces/gemini_AI_Agent/{agent_file}"
                if os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
                    if file_size > 0:
                        agents_status[agent_name] = "initialized"
                        print(f"   ✅ {agent_name}: 実装済み ({file_size} bytes)")
                    else:
                        agents_status[agent_name] = "planned"
                        print(f"   📋 {agent_name}: 未実装（空ファイル）")
                        planned_count += 1
                else:
                    agents_status[agent_name] = "planned"
                    print(f"   📋 {agent_name}: 未実装")
                    planned_count += 1

            print(f"   └─ 未実装エージェント: {planned_count}個")

            self.validation_result["agents"] = agents_status

        except Exception as e:
            print(f"❌ エージェント状態確認失敗: {e}")
            self.validation_result["errors"].append(f"エージェント確認: {e}")

    async def _check_important_modules(self) -> None:
        """重要モジュールの確認"""
        try:
            modules_status = {}

            important_modules = [
                ("SheetsManager", "tools/sheets_manager.py"),
                ("BrowserController", "browser_control/browser_controller.py"),
                ("ConfigLoader", "configuration/config_loader.py"),
                ("GeminiAPIClient", "browser_control/gemini_api_client.py"),
            ]

            for module_name, module_file in important_modules:
                full_path = f"/workspaces/gemini_AI_Agent/{module_file}"
                if os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
                    if file_size > 0:
                        modules_status[module_name] = "available"
                        print(f"   ✅ {module_name}: 利用可能 ({file_size} bytes)")
                    else:
                        modules_status[module_name] = "empty"
                        print(f"   ⚠️  {module_name}: ファイルが空です")
                else:
                    modules_status[module_name] = "not_found"
                    print(f"   ❌ {module_name}: ファイルが見つかりません")

            # 結果に追加
            if "modules" not in self.validation_result:
                self.validation_result["modules"] = {}
            self.validation_result["modules"] = modules_status

        except Exception as e:
            print(f"❌ 重要モジュール確認失敗: {e}")
            self.validation_result["errors"].append(f"モジュール確認: {e}")

    def _print_summary(self) -> None:
        """結果サマリーを表示"""
        print("\n📊 確認結果サマリー:")
        print("-" * 80)

        # WordPress接続
        wp_status = self.validation_result["wp_connection"].get("status", "unknown")
        wp_icon = "✅" if wp_status == "success" else "⚠️" if wp_status == "warning" else "❌"
        print(f"{wp_icon} WordPress接続: {wp_status}")

        # REST API
        rest_available = self.validation_result["rest_api"].get("available", False)
        rest_icon = "✅" if rest_available else "❌"
        print(f"{rest_icon} REST API: {'利用可能' if rest_available else '利用不可'}")

        # サイト情報
        site_info = self.validation_result["site_info"]
        if site_info:
            print(f"📝 投稿タイプ: {site_info.get('post_types', 0)}個")
            plugins = site_info.get("plugins", 0)
            if plugins > 0:
                print(f"🔌 プラグイン: {plugins}個")
            if "theme" in site_info:
                print(f"🎨 テーマ: {site_info['theme'].get('name')}")

        # エージェント
        agents = self.validation_result["agents"]
        if agents:
            available = sum(1 for v in agents.values() if v == "initialized")
            planned = sum(1 for v in agents.values() if v == "planned")
            total = len(agents)
            print(f"🤖 エージェント: {available}/{total}個 利用可能")
            if planned > 0:
                print(f"   └─ 未実装: {planned}個")

        # 重要モジュール
        modules = self.validation_result.get("modules", {})
        if modules:
            available_modules = sum(1 for v in modules.values() if v == "available")
            total_modules = len(modules)
            print(f"🔧 重要モジュール: {available_modules}/{total_modules}個 利用可能")

        # エラー
        if self.validation_result["errors"]:
            print(f"\n⚠️  エラー数: {len(self.validation_result['errors'])}")
            for error in self.validation_result["errors"]:
                print(f"   - {error}")

        # 総合判定
        print("\n" + "=" * 80)
        wp_ok = wp_status == "success"
        rest_ok = rest_available
        site_ok = bool(site_info.get("post_types", 0) > 0)
        agents_ok = sum(1 for v in agents.values() if v == "initialized") >= 1
        modules_ok = sum(1 for v in modules.values() if v == "available") >= 3

        if all([wp_ok, rest_ok, site_ok, agents_ok, modules_ok]):
            print("🎉 総合判定: 合格 - システムは基本的な動作が可能です")
        elif wp_ok and rest_ok and site_ok:
            print("⚠️  総合判定: 条件付き合格 - WordPress接続は正常ですが、一部機能が未実装です")
        else:
            print("❌ 総合判定: 不合格 - システムの設定を確認してください")
        print("=" * 80)


async def main():
    """メイン実行関数"""
    try:
        # .env ファイル読み込み
        env_path = "/workspaces/gemini_AI_Agent/.env"
        load_dotenv(env_path)
        print(f"✅ 環境変数を読み込みました: {env_path}\n")

        # ConfigValidator インスタンス作成
        validator = ConfigValidator()

        # Phase 1実行
        result = await validator.run_validation()

        print("\n✅ Phase 1 (v1.2) が完了しました")
        print(f"結果オブジェクト: {len(result)}個のキーを含む")

        return result

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback

        # 標準環境変数ローダー（自動追加）import sysfrom pathlib import Pathsys.path.insert(0, str(Path(__file__).parent.parent))from tools.env_loader import StandardEnvLoaderif not StandardEnvLoader.load_and_verify():    print("環境変数の読み込みに失敗しました")    sys.exit(1)

        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = asyncio.run(main())
