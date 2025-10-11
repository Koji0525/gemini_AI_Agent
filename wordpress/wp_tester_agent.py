# wp_tester_agent.py
"""
WordPress自動テストエージェント
WP-CLIとPytestを使用した自動テスト
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class WPTesterAgent:
    """
    WordPress自動テストエージェント
    
    機能:
    - WP-CLIコマンドのテスト実行
    - Pytestベースのユニットテスト
    - 統合テスト
    - テスト結果の検証と報告
    """
    
    def __init__(
        self,
        command_monitor,
        wp_path: str = "/var/www/html"
    ):
        """
        初期化
        
        Args:
            command_monitor: CommandMonitorAgent
            wp_path: WordPressのパス
        """
        self.cmd_monitor = command_monitor
        self.wp_path = Path(wp_path)
        
        # テスト結果保存ディレクトリ
        self.test_results_dir = Path("./test_results")
        self.test_results_dir.mkdir(parents=True, exist_ok=True)
        
        # 統計情報
        self.stats = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0
        }
        
        logger.info(f"✅ WPTesterAgent 初期化完了 (WP_PATH={wp_path})")
    
    async def run_tests(self, task_id: str, test_type: str = "auto") -> Dict[str, Any]:
        """
        テストを実行
        
        Args:
            task_id: タスクID
            test_type: テストタイプ (auto, unit, integration, wp-cli)
            
        Returns:
            Dict: テスト結果
        """
        start_time = datetime.now()
        
        try:
            logger.info("=" * 60)
            logger.info(f"🧪 テスト実行開始: {task_id} (タイプ={test_type})")
            logger.info("=" * 60)
            
            self.stats["total_tests"] += 1
            
            if test_type == "auto":
                # タスクIDから適切なテストを自動選択
                result = await self._run_auto_tests(task_id)
            elif test_type == "unit":
                result = await self._run_unit_tests(task_id)
            elif test_type == "integration":
                result = await self._run_integration_tests(task_id)
            elif test_type == "wp-cli":
                result = await self._run_wp_cli_tests(task_id)
            else:
                result = {
                    "passed": False,
                    "error": f"Unknown test type: {test_type}"
                }
            
            # 統計更新
            if result.get("passed"):
                self.stats["passed_tests"] += 1
            else:
                self.stats["failed_tests"] += 1
            
            execution_time = (datetime.now() - start_time).total_seconds()
            result["execution_time"] = execution_time
            
            # 結果を保存
            await self._save_test_result(task_id, result)
            
            logger.info(
                f"{'✅' if result.get('passed') else '❌'} "
                f"テスト{'成功' if result.get('passed') else '失敗'}: {task_id} "
                f"({execution_time:.2f}秒)"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"💥 テスト実行エラー: {e}", exc_info=True)
            self.stats["failed_tests"] += 1
            
            return {
                "passed": False,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds()
            }
    
    async def _run_auto_tests(self, task_id: str) -> Dict[str, Any]:
        """タスクに応じた自動テストを実行"""
        
        # タスクIDから種類を判定
        if "CPT" in task_id or "カスタム投稿タイプ" in task_id:
            return await self._test_custom_post_type(task_id)
        
        elif "ACF" in task_id or "カスタムフィールド" in task_id:
            return await self._test_acf_fields(task_id)
        
        elif "投稿" in task_id or "post" in task_id.lower():
            return await self._test_post_creation(task_id)
        
        elif "プラグイン" in task_id or "plugin" in task_id.lower():
            return await self._test_plugin_activation(task_id)
        
        else:
            # デフォルト: 基本的なWPチェック
            return await self._test_wp_health()
    
    async def _run_unit_tests(self, task_id: str) -> Dict[str, Any]:
        """ユニットテストを実行"""
        try:
            # Pytest実行
            cmd = f"pytest tests/unit/ -v --tb=short --json-report --json-report-file={self.test_results_dir / f'{task_id}_unit.json'}"
            
            result = await self.cmd_monitor.execute_command(cmd)
            
            if result.get("success"):
                # JSONレポートを読み込み
                report_file = self.test_results_dir / f"{task_id}_unit.json"
                if report_file.exists():
                    report = json.loads(report_file.read_text())
                    
                    return {
                        "passed": report.get("summary", {}).get("failed", 0) == 0,
                        "total": report.get("summary", {}).get("total", 0),
                        "passed_count": report.get("summary", {}).get("passed", 0),
                        "failed_count": report.get("summary", {}).get("failed", 0),
                        "report": report
                    }
            
            return {
                "passed": False,
                "error": result.get("stderr", "Unit test execution failed")
            }
            
        except Exception as e:
            logger.error(f"❌ ユニットテストエラー: {e}")
            return {"passed": False, "error": str(e)}
    
    async def _run_integration_tests(self, task_id: str) -> Dict[str, Any]:
        """統合テストを実行"""
        try:
            cmd = f"pytest tests/integration/ -v --tb=short"
            result = await self.cmd_monitor.execute_command(cmd)
            
            return {
                "passed": result.get("success", False),
                "output": result.get("stdout", ""),
                "error": result.get("stderr") if not result.get("success") else None
            }
            
        except Exception as e:
            logger.error(f"❌ 統合テストエラー: {e}")
            return {"passed": False, "error": str(e)}
    
    async def _run_wp_cli_tests(self, task_id: str) -> Dict[str, Any]:
        """WP-CLI基本テストを実行"""
        tests = [
            ("wp core version", "WordPressバージョン確認"),
            ("wp plugin list --status=active", "プラグイン一覧"),
            ("wp theme list --status=active", "アクティブテーマ確認"),
        ]
        
        results = []
        all_passed = True
        
        for cmd, description in tests:
            logger.info(f"🔍 テスト: {description}")
            result = await self.cmd_monitor.execute_command(cmd)
            
            passed = result.get("success", False)
            results.append({
                "test": description,
                "command": cmd,
                "passed": passed,
                "output": result.get("stdout", "")
            })
            
            if not passed:
                all_passed = False
        
        return {
            "passed": all_passed,
            "tests": results
        }
    
    # ========================================
    # 専門テスト関数
    # ========================================
    
    async def _test_custom_post_type(self, task_id: str) -> Dict[str, Any]:
        """カスタム投稿タイプのテスト"""
        try:
            # CPT一覧を取得
            cmd = "wp post-type list --format=json"
            result = await self.cmd_monitor.execute_command(cmd)
            
            if not result.get("success"):
                return {
                    "passed": False,
                    "error": "Failed to list post types"
                }
            
            # タスクIDからCPT名を推定（例: Task 54 → ma_case）
            cpt_name = self._extract_cpt_name_from_task(task_id)
            
            if cpt_name:
                # 特定のCPTをチェック
                post_types = json.loads(result.get("stdout", "[]"))
                cpt_exists = any(pt.get("name") == cpt_name for pt in post_types)
                
                if cpt_exists:
                    logger.info(f"✅ CPT '{cpt_name}' が正常に登録されています")
                    return {"passed": True, "cpt_name": cpt_name}
                else:
                    logger.warning(f"⚠️ CPT '{cpt_name}' が見つかりません")
                    return {
                        "passed": False,
                        "error": f"CPT '{cpt_name}' not found",
                        "cpt_name": cpt_name
                    }
            else:
                # 汎用チェック
                return {"passed": True, "message": "Post types list retrieved successfully"}
                
        except Exception as e:
            logger.error(f"❌ CPTテストエラー: {e}")
            return {"passed": False, "error": str(e)}
    
    async def _test_acf_fields(self, task_id: str) -> Dict[str, Any]:
        """ACFフィールドのテスト"""
        try:
            # ACFフィールドグループを取得
            cmd = "wp acf export --format=json"
            result = await self.cmd_monitor.execute_command(cmd)
            
            if not result.get("success"):
                # ACFコマンドがない場合
                logger.warning("⚠️ ACF WP-CLIコマンドが利用できません")
                return {
                    "passed": False,
                    "error": "ACF CLI not available"
                }
            
            # フィールドグループの存在確認
            field_groups = json.loads(result.get("stdout", "[]"))
            
            if field_groups and len(field_groups) > 0:
                logger.info(f"✅ ACFフィールドグループ: {len(field_groups)}個")
                return {
                    "passed": True,
                    "field_group_count": len(field_groups)
                }
            else:
                return {
                    "passed": False,
                    "error": "No ACF field groups found"
                }
                
        except Exception as e:
            logger.error(f"❌ ACFテストエラー: {e}")
            return {"passed": False, "error": str(e)}
    
    async def _test_post_creation(self, task_id: str) -> Dict[str, Any]:
        """投稿作成のテスト"""
        try:
            # テスト投稿を作成
            test_title = f"Test Post {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            cmd = f'wp post create --post_title="{test_title}" --post_content="Test content" --post_status=draft --porcelain'
            
            result = await self.cmd_monitor.execute_command(cmd)
            
            if result.get("success"):
                post_id = result.get("stdout", "").strip()
                logger.info(f"✅ テスト投稿作成成功: ID={post_id}")
                
                # 作成した投稿を削除
                delete_cmd = f"wp post delete {post_id} --force"
                await self.cmd_monitor.execute_command(delete_cmd)
                
                return {
                    "passed": True,
                    "test_post_id": post_id
                }
            else:
                return {
                    "passed": False,
                    "error": result.get("stderr", "Post creation failed")
                }
                
        except Exception as e:
            logger.error(f"❌ 投稿作成テストエラー: {e}")
            return {"passed": False, "error": str(e)}
    
    async def _test_plugin_activation(self, task_id: str) -> Dict[str, Any]:
        """プラグイン有効化のテスト"""
        try:
            # アクティブなプラグイン一覧
            cmd = "wp plugin list --status=active --format=json"
            result = await self.cmd_monitor.execute_command(cmd)
            
            if result.get("success"):
                plugins = json.loads(result.get("stdout", "[]"))
                logger.info(f"✅ アクティブなプラグイン: {len(plugins)}個")
                
                return {
                    "passed": True,
                    "active_plugin_count": len(plugins),
                    "plugins": [p.get("name") for p in plugins]
                }
            else:
                return {
                    "passed": False,
                    "error": "Failed to list plugins"
                }
                
        except Exception as e:
            logger.error(f"❌ プラグインテストエラー: {e}")
            return {"passed": False, "error": str(e)}
    
    async def _test_wp_health(self) -> Dict[str, Any]:
        """WordPress全体の健全性チェック"""
        try:
            checks = []
            
            # 1. WordPressバージョン
            result = await self.cmd_monitor.execute_command("wp core version")
            checks.append({
                "check": "WordPress Version",
                "passed": result.get("success", False),
                "value": result.get("stdout", "").strip()
            })
            
            # 2. データベース接続
            result = await self.cmd_monitor.execute_command("wp db check")
            checks.append({
                "check": "Database Connection",
                "passed": result.get("success", False)
            })
            
            # 3. テーマ
            result = await self.cmd_monitor.execute_command("wp theme list --status=active")
            checks.append({
                "check": "Active Theme",
                "passed": result.get("success", False)
            })
            
            all_passed = all(c["passed"] for c in checks)
            
            return {
                "passed": all_passed,
                "checks": checks
            }
            
        except Exception as e:
            logger.error(f"❌ 健全性チェックエラー: {e}")
            return {"passed": False, "error": str(e)}
    
    # ========================================
    # ユーティリティ
    # ========================================
    
    def _extract_cpt_name_from_task(self, task_id: str) -> Optional[str]:
        """タスクIDからCPT名を抽出"""
        # 例: Task 54 → ma_case
        if "54" in task_id or "M&A案件" in task_id:
            return "ma_case"
        
        # 他のパターンをここに追加
        
        return None
    
    async def _save_test_result(self, task_id: str, result: Dict[str, Any]):
        """テスト結果を保存"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.test_results_dir / f"{task_id}_{timestamp}.json"
            
            result_with_metadata = {
                "task_id": task_id,
                "timestamp": datetime.now().isoformat(),
                **result
            }
            
            await asyncio.to_thread(
                filename.write_text,
                json.dumps(result_with_metadata, indent=2, ensure_ascii=False)
            )
            
            logger.info(f"💾 テスト結果保存: {filename}")
            
        except Exception as e:
            logger.error(f"❌ テスト結果保存エラー: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        success_rate = 0.0
        if self.stats["total_tests"] > 0:
            success_rate = self.stats["passed_tests"] / self.stats["total_tests"]
        
        return {
            **self.stats,
            "success_rate": success_rate
        }