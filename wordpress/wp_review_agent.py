"""
WordPressプラグイン確認レビューエージェント
"""
import asyncio
import logging
from typing import Dict, List, Optional
from browser_control.browser_controller import BrowserController
from wordpress.wp_plugin_manager import WordPressPluginManager

class WordPressReviewAgent:
    """WordPressプラグイン確認レビューエージェント"""
    
    def __init__(self, browser: BrowserController):
        self.browser = browser
        self.plugin_manager = WordPressPluginManager(browser)
        self.logger = logging.getLogger(__name__)
    
    async def review_plugin_installation(self, plugin_slug: str, expected_settings: Dict = None) -> Dict:
        """プラグインのインストールと設定をレビュー"""
        try:
            print(f"🔍 プラグイン '{plugin_slug}' のレビューを開始...")
            
            # 1. インストール状態の確認
            installation_check = await self.plugin_manager.verify_plugin_installation(plugin_slug)
            
            if not installation_check['success']:
                return {
                    "success": False,
                    "review_score": 0,
                    "issues": ["プラグインの状態確認に失敗しました"],
                    "installation_status": "unknown",
                    "recommendations": ["手動で確認してください"]
                }
            
            # レビュー結果を収集
            review_results = {
                "installation_status": installation_check,
                "checks_passed": 0,
                "total_checks": 2,  # 基本チェック数
                "issues": [],
                "recommendations": []
            }
            
            # 基本チェック
            if installation_check['installed']:
                review_results['checks_passed'] += 1
                review_results['recommendations'].append("✅ プラグインは正常にインストールされています")
            else:
                review_results['issues'].append("❌ プラグインがインストールされていません")
            
            if installation_check['active']:
                review_results['checks_passed'] += 1
                review_results['recommendations'].append("✅ プラグインは有効化されています")
            else:
                review_results['issues'].append("⚠️ プラグインはインストールされていますが有効化されていません")
            
            # 設定の確認（もし期待される設定があれば）
            if expected_settings:
                review_results['total_checks'] += len(expected_settings)
                # ここで実際の設定値を確認するロジックを追加可能
            
            # スコア計算
            success_rate = review_results['checks_passed'] / review_results['total_checks']
            review_score = int(success_rate * 10)  # 10点満点
            
            # 総合評価
            if review_score >= 9:
                overall_rating = "優秀"
            elif review_score >= 7:
                overall_rating = "良好"
            elif review_score >= 5:
                overall_rating = "平均"
            else:
                overall_rating = "要改善"
            
            return {
                "success": True,
                "review_score": review_score,
                "overall_rating": overall_rating,
                "installation_status": installation_check['status'],
                "checks_passed": review_results['checks_passed'],
                "total_checks": review_results['total_checks'],
                "issues": review_results['issues'],
                "recommendations": review_results['recommendations'],
                "details": f"プラグイン状態: {installation_check['status']}, チェック: {review_results['checks_passed']}/{review_results['total_checks']}合格"
            }
            
        except Exception as e:
            return {
                "success": False,
                "review_score": 0,
                "error": f"レビューエラー: {str(e)}",
                "issues": ["レビュープロセスでエラーが発生しました"],
                "recommendations": ["システム管理者に連絡してください"]
            }
    
    async def generate_review_report(self, plugin_task_result: Dict) -> Dict:
        """プラグインタスクの結果からレビューレポートを生成"""
        try:
            plugin_slug = plugin_task_result.get('plugin_slug')
            task_type = plugin_task_result.get('task_type')
            final_status = plugin_task_result.get('final_status', {})
            
            print(f"📊 プラグインタスクのレビューレポート生成: {plugin_slug}")
            
            # レビュー実行
            review_result = await self.review_plugin_installation(plugin_slug)
            
            # レポートを組み立て
            report = {
                "plugin_slug": plugin_slug,
                "task_type": task_type,
                "review_score": review_result.get('review_score', 0),
                "overall_rating": review_result.get('overall_rating', '不明'),
                "installation_status": final_status.get('status', 'unknown'),
                "success": review_result.get('success', False),
                "summary": f"プラグイン '{plugin_slug}' の{task_type}タスク完了 - レビュースコア: {review_result.get('review_score', 0)}/10",
                "detailed_findings": {
                    "installation_check": final_status,
                    "review_results": review_result,
                    "task_execution": plugin_task_result.get('results', {})
                },
                "issues": review_result.get('issues', []),
                "recommendations": review_result.get('recommendations', [])
            }
            
            return report
            
        except Exception as e:
            return {
                "success": False,
                "error": f"レポート生成エラー: {str(e)}",
                "review_score": 0,
                "overall_rating": "エラー"
            }
    
    async def close(self):
        """リソースを解放"""
        await self.plugin_manager.close()

