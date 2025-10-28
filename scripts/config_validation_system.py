#!/usr/bin/env python3
"""
Phase 3: 統合版 - ConfigValidation完全システム（インポート修正版）
Phase 1 (確認) + Phase 2 (ログ記録) + Markdownレポート生成

v3.0 - 初回統合実装
v3.1 - SheetsManagerインポート修正
運用ルール準拠: 1ファイル1000行以下、PEP 8準拠
"""

import os
import sys
import asyncio
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# プロジェクトルートをパスに追加
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from configuration.config_loader import ConfigLoader

# SheetsManagerの正しいインポート
try:
    from tools.sheets_manager import GoogleSheetsManager as SheetsManager
except ImportError:
    # フォールバック: クラス名が異なる可能性
    try:
        from tools.sheets_manager import SheetsManager
    except ImportError:
        print("⚠️  SheetsManagerのインポートに失敗しました")
        print("   Phase 2のログ記録はスキップされます")
        SheetsManager = None


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
            "modules": {},
            "errors": [],
            "report_path": ""
        }
    
    async def run_validation(self) -> Dict[str, Any]:
        """設定確認を実行"""
        print("=" * 80)
        print("🚀 Phase 1: 基本的な設定確認を開始します")
        print("=" * 80)
        
        await self._test_wordpress_connection()
        await self._fetch_site_info()
        await self._check_agent_status()
        await self._check_important_modules()
        
        print("\n" + "=" * 80)
        print("✅ Phase 1: 設定確認が完了しました")
        print("=" * 80)
        
        return self.validation_result
    
    async def _test_wordpress_connection(self) -> None:
        """WordPress接続テスト"""
        print("\n📡 WordPress接続テスト")
        try:
            wp_url = self.config._config.get("WP_URL")
            wp_user = self.config._config.get("wp_user")
            wp_pass = self.config._config.get("wp_pass")
            
            if not all([wp_url, wp_user, wp_pass]):
                self.validation_result["wp_connection"] = {
                    "status": "failed",
                    "error": "WordPress設定が不完全"
                }
                print("❌ WordPress設定が不完全です")
                return
            
            response = requests.get(wp_url, timeout=10)
            
            if response.status_code == 200:
                self.validation_result["wp_connection"] = {
                    "status": "success",
                    "url": wp_url,
                    "status_code": response.status_code
                }
                print(f"✅ WordPress接続成功 (Status: {response.status_code})")
            else:
                self.validation_result["wp_connection"] = {
                    "status": "warning",
                    "url": wp_url,
                    "status_code": response.status_code
                }
                print(f"⚠️  予期しないステータス: {response.status_code}")
                
        except Exception as e:
            self.validation_result["wp_connection"] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"❌ WordPress接続失敗: {e}")
            self.validation_result["errors"].append(f"WordPress接続: {e}")
    
    async def _fetch_site_info(self) -> None:
        """サイト情報取得"""
        print("\n📊 サイト情報取得")
        try:
            if self.validation_result["wp_connection"].get("status") != "success":
                print("⏭️  スキップ")
                return
            
            wp_url = self.config._config.get("WP_URL")
            wp_user = self.config._config.get("wp_user")
            wp_pass = self.config._config.get("wp_pass")
            
            api_base = f"{wp_url}/wp-json/wp/v2"
            auth = (wp_user, wp_pass)
            
            # REST API チェック
            response = requests.get(api_base, auth=auth, timeout=10)
            if response.status_code in [200, 401]:
                self.validation_result["rest_api"] = {
                    "available": True,
                    "limited": response.status_code == 401
                }
                print(f"✅ REST API利用可能")
            else:
                self.validation_result["rest_api"] = {"available": False}
                print(f"❌ REST API利用不可")
                return
            
            site_info = {}
            
            # 投稿タイプ
            response = requests.get(f"{api_base}/types", auth=auth, timeout=10)
            if response.status_code == 200:
                post_types = response.json()
                site_info["post_types"] = len(post_types)
                print(f"   📝 投稿タイプ: {len(post_types)}個")
            
            self.validation_result["site_info"] = site_info
            
        except Exception as e:
            print(f"❌ サイト情報取得失敗: {e}")
            self.validation_result["errors"].append(f"サイト情報: {e}")
    
    async def _check_agent_status(self) -> None:
        """エージェント状態確認"""
        print("\n🤖 エージェント状態確認")
        try:
            agents_status = {}
            
            implemented_agents = [
                ("wp_design_generator", "agents/wordpress/wp_design_generator.py"),
                ("wp_orchestrator", "agents/wordpress/wp_orchestrator.py"),
            ]
            
            for agent_name, agent_file in implemented_agents:
                full_path = f"/workspaces/gemini_AI_Agent/{agent_file}"
                if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
                    agents_status[agent_name] = "initialized"
                    print(f"   ✅ {agent_name}")
                else:
                    agents_status[agent_name] = "not_found"
            
            self.validation_result["agents"] = agents_status
            
        except Exception as e:
            print(f"❌ エージェント確認失敗: {e}")
    
    async def _check_important_modules(self) -> None:
        """重要モジュール確認"""
        print("\n🔧 重要モジュール確認")
        try:
            modules_status = {}
            
            important_modules = [
                ("SheetsManager", "tools/sheets_manager.py"),
                ("BrowserController", "browser_control/browser_controller.py"),
                ("ConfigLoader", "configuration/config_loader.py"),
            ]
            
            for module_name, module_file in important_modules:
                full_path = f"/workspaces/gemini_AI_Agent/{module_file}"
                if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
                    modules_status[module_name] = "available"
                    print(f"   ✅ {module_name}")
                else:
                    modules_status[module_name] = "not_found"
            
            self.validation_result["modules"] = modules_status
            
        except Exception as e:
            print(f"❌ モジュール確認失敗: {e}")


class ConfigValidationLogger:
    """Phase 2: ログ記録クラス"""
    
    def __init__(self, sheets_manager):
        self.sheets_manager = sheets_manager
        self.base_task_id = 10000
    
    async def log_validation_result(self, validation_result: Dict[str, Any]) -> int:
        """設定確認結果をログに記録"""
        print("\n" + "=" * 80)
        print("📊 Phase 2: ログ記録を開始")
        print("=" * 80)
        
        timestamp = datetime.now().isoformat()
        quality_score = self._calculate_quality_score(validation_result)
        status = self._determine_status(quality_score)
        output_summary = self._generate_summary(validation_result)
        quality_description = self._generate_quality_description(validation_result, quality_score)
        
        print(f"\n✅ Quality Score: {quality_score}/10")
        print(f"📝 Status: {status}")
        
        # task_execution_logシートへの書き込み（簡易版）
        if self.sheets_manager is None:
            print("⏭️  SheetsManagerが利用できないため、ログ記録をスキップします")
        else:
            try:
                # 簡易的なログデータ構造
                log_data = {
                    "task_id": f"CONFIG_{int(datetime.now().timestamp())}",
                    "summary": output_summary,
                    "full_text": quality_description,
                    "screenshot": "",
                    "timestamp": timestamp
                }
                
                # save_task_outputメソッドを使用
                result = await self.sheets_manager.save_task_output(log_data)
                
                if result:
                    print("✅ task_execution_logシートへの記録完了")
                else:
                    print("⚠️  ログ記録に失敗しました")
                
            except Exception as e:
                print(f"⚠️  ログ記録エラー: {e}")
                print("   (続行します)")
        
        return quality_score
    
    def _calculate_quality_score(self, result: Dict) -> int:
        """Quality Score計算"""
        score = 10
        
        if result.get("wp_connection", {}).get("status") != "success":
            score -= 8
            return max(1, score)
        
        if not result.get("rest_api", {}).get("available"):
            score -= 5
        
        if not result.get("site_info", {}).get("post_types"):
            score -= 2
        
        agents = result.get("agents", {})
        initialized = sum(1 for v in agents.values() if v == "initialized")
        if initialized == 0:
            score -= 3
        elif initialized < 3:
            score -= 1
        
        return max(1, int(score))
    
    def _determine_status(self, quality_score: int) -> str:
        """status判定"""
        if quality_score >= 7:
            return "completed"
        elif quality_score >= 4:
            return "warning"
        else:
            return "failed"
    
    def _generate_summary(self, result: Dict) -> str:
        """サマリー生成"""
        if result.get("wp_connection", {}).get("status") != "success":
            return "WordPress接続失敗"
        
        parts = ["WordPress接続成功。"]
        
        if result.get("rest_api", {}).get("available"):
            parts.append("REST API利用可能。")
        
        site_info = result.get("site_info", {})
        if site_info.get("post_types"):
            parts.append(f"投稿タイプ{site_info['post_types']}個確認。")
        
        summary = "".join(parts)
        return summary[:100]
    
    def _generate_quality_description(self, result: Dict, quality_score: int) -> str:
        """品質説明生成"""
        parts = []
        
        if result.get("wp_connection", {}).get("status") == "success":
            parts.append("WordPress接続成功。")
        else:
            parts.append("WordPress接続失敗。")
            return "".join(parts)
        
        if result.get("rest_api", {}).get("available"):
            parts.append("REST API利用可能。")
        
        if result.get("site_info", {}).get("post_types"):
            parts.append("サイト情報取得成功。")
        
        if quality_score >= 7:
            parts.append("基本機能は使用可能。")
        else:
            parts.append("一部機能に制限あり。")
        
        return "".join(parts)


class MarkdownReportGenerator:
    """Phase 3: Markdownレポート生成"""
    
    @staticmethod
    def generate_report(validation_result: Dict[str, Any], quality_score: int) -> str:
        """Markdownレポートを生成"""
        print("\n" + "=" * 80)
        print("📄 Phase 3: Markdownレポート生成")
        print("=" * 80)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"/workspaces/gemini_AI_Agent/logs/config_validation_report_{timestamp}.md"
        
        # レポート内容生成
        report_lines = [
            "# WordPress設定確認レポート",
            f"\n**実行日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Quality Score**: {quality_score}/10",
            "\n---\n",
            "## 1. WordPress接続テスト",
        ]
        
        wp_conn = validation_result.get("wp_connection", {})
        if wp_conn.get("status") == "success":
            report_lines.append(f"✅ **成功** - {wp_conn.get('url')}")
        else:
            report_lines.append(f"❌ **失敗** - {wp_conn.get('error', '不明')}")
        
        report_lines.extend([
            "\n## 2. REST API",
        ])
        
        rest_api = validation_result.get("rest_api", {})
        if rest_api.get("available"):
            report_lines.append("✅ **利用可能**")
        else:
            report_lines.append("❌ **利用不可**")
        
        report_lines.extend([
            "\n## 3. サイト情報",
        ])
        
        site_info = validation_result.get("site_info", {})
        if site_info:
            report_lines.append(f"- 投稿タイプ: {site_info.get('post_types', 0)}個")
        
        report_lines.extend([
            "\n## 4. エージェント状態",
        ])
        
        agents = validation_result.get("agents", {})
        for agent_name, status in agents.items():
            icon = "✅" if status == "initialized" else "⚠️"
            report_lines.append(f"{icon} {agent_name}: {status}")
        
        report_lines.extend([
            "\n## 5. 重要モジュール",
        ])
        
        modules = validation_result.get("modules", {})
        for module_name, status in modules.items():
            icon = "✅" if status == "available" else "❌"
            report_lines.append(f"{icon} {module_name}: {status}")
        
        report_lines.extend([
            "\n---\n",
            "## 総合判定",
        ])
        
        if quality_score >= 7:
            report_lines.append("🎉 **合格** - システムは基本的な動作が可能です")
        elif quality_score >= 4:
            report_lines.append("⚠️  **条件付き合格** - 一部機能に制限があります")
        else:
            report_lines.append("❌ **不合格** - システムの設定を確認してください")
        
        # ファイルに保存
        os.makedirs("/workspaces/gemini_AI_Agent/logs", exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
        
        print(f"✅ レポート生成完了: {report_path}")
        
        return report_path


async def main():
    """メイン実行関数"""
    try:
        env_path = "/workspaces/gemini_AI_Agent/.env"
        load_dotenv(env_path)
        print(f"✅ 環境変数読み込み: {env_path}\n")
        
        # Phase 1: 設定確認
        validator = ConfigValidator()
        result = await validator.run_validation()
        
        # 初期Quality Score計算
        temp_logger = ConfigValidationLogger(None)
        quality_score = temp_logger._calculate_quality_score(result)
        
        # Phase 3: Markdownレポート生成
        report_generator = MarkdownReportGenerator()
        report_path = report_generator.generate_report(result, quality_score)
        result["report_path"] = report_path
        
        # Phase 2: ログ記録（SheetsManager使用）
        if SheetsManager is not None:
            try:
                config = ConfigLoader()
                sheets_manager = SheetsManager(
                    spreadsheet_id=config._config.get("SPREADSHEET_ID"),
                    service_account_file=config._config.get("GOOGLE_SERVICE_ACCOUNT_FILE")
                )
                
                logger = ConfigValidationLogger(sheets_manager)
                quality_score = await logger.log_validation_result(result)
            except Exception as e:
                print(f"⚠️  SheetsManager初期化エラー: {e}")
                print("   ログ記録はスキップされました")
        else:
            print("\n⏭️  SheetsManagerが利用できないため、Phase 2をスキップしました")
        
        print("\n" + "=" * 80)
        print("🎉 全Phase完了!")
        print(f"Quality Score: {quality_score}/10")
        print(f"レポート: {report_path}")
        print("=" * 80)
        
        return result
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = asyncio.run(main())
