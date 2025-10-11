"""WordPressテスト機能（品質管理強化版）"""
import logging
import re
from datetime import datetime
from typing import Dict, List, Tuple
from playwright.async_api import Page

logger = logging.getLogger(__name__)


class WordPressTester:
    """WordPressテスト機能（品質管理強化版）"""
    
    def __init__(self, wp_url: str):
        self.wp_url = wp_url
        self.test_frameworks = {
            'php': ['PHPUnit', 'Codeception', 'WP_UnitTestCase'],
            'javascript': ['Jest', 'Mocha', 'Chai', 'Cypress'],
            'wordpress': ['WP_UnitTestCase', 'WordPress PHPUnit']
        }
    
    async def test_functionality(self, page: Page, task: Dict) -> Dict:
        """機能をテスト（品質検証強化版）"""
        try:
            logger.info("🔍 機能テストを実行中（品質検証付き）...")
            
            test_results = []
            quality_issues = []
            
            # 1. サイトの表示テスト
            site_test_result = await self._test_site_accessibility(page)
            test_results.extend(site_test_result['results'])
            quality_issues.extend(site_test_result['quality_issues'])
            
            # 2. 管理画面テスト
            admin_test_result = await self._test_admin_access(page)
            test_results.extend(admin_test_result['results'])
            quality_issues.extend(admin_test_result['quality_issues'])
            
            # 3. プラグインステータス確認
            plugin_test_result = await self._test_plugins_status(page)
            test_results.extend(plugin_test_result['results'])
            quality_issues.extend(plugin_test_result['quality_issues'])
            
            # 4. コード品質検証（タスクにテストコードが含まれる場合）
            if self._has_test_code(task):
                code_quality_result = await self._validate_test_code_quality(task)
                test_results.extend(code_quality_result['results'])
                quality_issues.extend(code_quality_result['quality_issues'])
            
            # テスト結果の集計
            summary = self._generate_test_summary(test_results, quality_issues)
            
            logger.info("\n" + "="*60)
            logger.info("📊 テスト結果サマリー")
            logger.info("="*60)
            logger.info(summary)
            
            return {
                'success': len(quality_issues) == 0,
                'summary': summary[:500],
                'full_text': summary,
                'quality_issues': quality_issues,
                'test_results': test_results
            }
            
        except Exception as e:
            logger.error(f"❌ 機能テストエラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _test_site_accessibility(self, page: Page) -> Dict:
        """サイトアクセシビリティテスト"""
        results = []
        quality_issues = []
        
        try:
            # サイトにアクセス
            await page.goto(self.wp_url, wait_until='networkidle')
            await page.wait_for_timeout(3000)
            
            # ページタイトル取得
            page_title = await page.title()
            results.append(f"✅ サイト表示OK: {page_title}")
            
            # HTTPステータスチェック
            response = await page.goto(self.wp_url)
            if response and response.status == 200:
                results.append("✅ HTTPステータス: 200 OK")
            else:
                quality_issues.append("❌ HTTPステータスが200ではありません")
                results.append("❌ HTTPステータスエラー")
            
            # スクリーンショット
            timestamp = datetime.now().strftime('%H%M%S')
            site_screenshot = f"wp_site_{timestamp}.png"
            await page.screenshot(path=site_screenshot, full_page=True)
            results.append(f"📸 サイト全体: {site_screenshot}")
            
            # ページ読み込み速度チェック
            load_time = await self._measure_page_load_time(page, self.wp_url)
            if load_time < 5000:  # 5秒以内
                results.append(f"✅ ページ読み込み速度: {load_time}ms")
            else:
                quality_issues.append(f"⚠️ ページ読み込みが遅い: {load_time}ms")
                results.append(f"⚠️ ページ読み込み速度: {load_time}ms")
            
        except Exception as e:
            quality_issues.append(f"❌ サイトアクセステスト失敗: {str(e)}")
            results.append(f"❌ サイトアクセステスト失敗: {str(e)}")
        
        return {'results': results, 'quality_issues': quality_issues}
    
    async def _test_admin_access(self, page: Page) -> Dict:
        """管理画面アクセステスト"""
        results = []
        quality_issues = []
        
        try:
            # 管理画面にアクセス
            admin_url = f"{self.wp_url}/wp-admin/"
            await page.goto(admin_url, wait_until='networkidle')
            await page.wait_for_timeout(2000)
            
            # ログインフォームの存在確認
            login_form = await page.query_selector('#loginform')
            if login_form:
                results.append("✅ 管理画面ログインフォーム確認")
            else:
                # 既にログイン済みかチェック
                admin_bar = await page.query_selector('#wpadminbar')
                if admin_bar:
                    results.append("✅ 管理画面: 既にログイン済み")
                else:
                    quality_issues.append("❌ 管理画面にアクセスできません")
                    results.append("❌ 管理画面アクセス失敗")
            
            # スクリーンショット
            timestamp = datetime.now().strftime('%H%M%S')
            admin_screenshot = f"wp_admin_{timestamp}.png"
            await page.screenshot(path=admin_screenshot)
            results.append(f"📸 管理画面: {admin_screenshot}")
            
        except Exception as e:
            quality_issues.append(f"❌ 管理画面テスト失敗: {str(e)}")
            results.append(f"❌ 管理画面テスト失敗: {str(e)}")
        
        return {'results': results, 'quality_issues': quality_issues}
    
    async def _test_plugins_status(self, page: Page) -> Dict:
        """プラグインステータステスト"""
        results = []
        quality_issues = []
        
        try:
            # プラグインページにアクセス（ログインが必要な場合）
            plugins_url = f"{self.wp_url}/wp-admin/plugins.php"
            await page.goto(plugins_url, wait_until='networkidle')
            await page.wait_for_timeout(2000)
            
            # ページタイトルでプラグインページか確認
            page_title = await page.title()
            if 'プラグイン' in page_title or 'Plugins' in page_title:
                results.append("✅ プラグイン一覧ページ確認")
                
                # アクティブなプラグイン数をチェック
                active_plugins = await page.query_selector_all('.plugins .active')
                if len(active_plugins) > 0:
                    results.append(f"✅ アクティブプラグイン: {len(active_plugins)}個")
                else:
                    quality_issues.append("⚠️ アクティブなプラグインがありません")
                    results.append("⚠️ アクティブプラグイン: 0個")
            else:
                quality_issues.append("❌ プラグインページにアクセスできません")
                results.append("❌ プラグインページアクセス失敗")
            
            # スクリーンショット
            timestamp = datetime.now().strftime('%H%M%S')
            plugins_screenshot = f"wp_plugins_{timestamp}.png"
            await page.screenshot(path=plugins_screenshot)
            results.append(f"📸 プラグイン: {plugins_screenshot}")
            
        except Exception as e:
            quality_issues.append(f"❌ プラグインテスト失敗: {str(e)}")
            results.append(f"❌ プラグインテスト失敗: {str(e)}")
        
        return {'results': results, 'quality_issues': quality_issues}
    
    async def _validate_test_code_quality(self, task: Dict) -> Dict:
        """テストコードの品質検証"""
        results = []
        quality_issues = []
        
        try:
            # タスクからテストコードを抽出
            test_code = self._extract_test_code(task)
            
            if not test_code:
                results.append("ℹ️ 検証対象のテストコードなし")
                return {'results': results, 'quality_issues': quality_issues}
            
            # 言語別の品質検証
            if self._is_php_code(test_code):
                php_validation = self._validate_php_test_code(test_code)
                results.extend(php_validation['results'])
                quality_issues.extend(php_validation['quality_issues'])
            
            elif self._is_javascript_code(test_code):
                js_validation = self._validate_javascript_test_code(test_code)
                results.extend(js_validation['results'])
                quality_issues.extend(js_validation['quality_issues'])
            
            else:
                # 一般的なテストコード検証
                general_validation = self._validate_general_test_code(test_code)
                results.extend(general_validation['results'])
                quality_issues.extend(general_validation['quality_issues'])
            
        except Exception as e:
            quality_issues.append(f"❌ テストコード検証エラー: {str(e)}")
            results.append(f"❌ テストコード検証失敗: {str(e)}")
        
        return {'results': results, 'quality_issues': quality_issues}
    
    def _validate_php_test_code(self, code: str) -> Dict:
        """PHPテストコードの検証"""
        results = []
        quality_issues = []
        
        # PHPUnitの基本構造チェック
        if 'class' not in code and 'function' not in code:
            quality_issues.append("❌ PHPテスト: クラスまたは関数が定義されていません")
            results.append("❌ PHPテスト構造: 不完全")
        
        # テストメソッドの存在チェック
        test_method_patterns = [
            r'function\s+test\w+',
            r'public\s+function\s+test\w+',
            r'public\s+function\s+test_\w+'
        ]
        
        has_test_methods = any(re.search(pattern, code) for pattern in test_method_patterns)
        if not has_test_methods:
            quality_issues.append("❌ PHPテスト: テストメソッドが定義されていません")
            results.append("❌ PHPテストメソッド: 未定義")
        else:
            results.append("✅ PHPテストメソッド: 定義済み")
        
        # アサーションの存在チェック
        assertion_patterns = [
            r'\$this->assert',
            r'assertEquals',
            r'assertTrue',
            r'assertFalse',
            r'expectException'
        ]
        
        has_assertions = any(pattern in code for pattern in assertion_patterns)
        if not has_assertions:
            quality_issues.append("❌ PHPテスト: アサーションがありません")
            results.append("❌ PHPテストアサーション: 未定義")
        else:
            results.append("✅ PHPテストアサーション: 定義済み")
        
        # PHPUnitのインポートチェック
        if 'PHPUnit' in code or 'use PHPUnit' in code:
            results.append("✅ PHPUnitフレームワーク: 検出")
        else:
            quality_issues.append("⚠️ PHPテスト: PHPUnitフレームワークが明示されていません")
            results.append("⚠️ PHPUnitフレームワーク: 未検出")
        
        return {'results': results, 'quality_issues': quality_issues}
    
    def _validate_javascript_test_code(self, code: str) -> Dict:
        """JavaScriptテストコードの検証"""
        results = []
        quality_issues = []
        
        # テストフレームワークのチェック
        frameworks = ['describe', 'it', 'test', 'expect']
        has_framework = any(framework in code for framework in frameworks)
        
        if not has_framework:
            quality_issues.append("❌ JSテスト: テストフレームワークが検出されません")
            results.append("❌ JSテストフレームワーク: 未検出")
        else:
            results.append("✅ JSテストフレームワーク: 検出")
        
        # アサーションの存在チェック
        assertion_patterns = [
            'expect',
            'assert',
            'should',
            'toBe',
            'toEqual'
        ]
        
        has_assertions = any(pattern in code for pattern in assertion_patterns)
        if not has_assertions:
            quality_issues.append("❌ JSテスト: アサーションがありません")
            results.append("❌ JSテストアサーション: 未定義")
        else:
            results.append("✅ JSテストアサーション: 定義済み")
        
        return {'results': results, 'quality_issues': quality_issues}
    
    def _validate_general_test_code(self, code: str) -> Dict:
        """一般的なテストコードの検証"""
        results = []
        quality_issues = []
        
        # テスト関連キーワードのチェック
        test_keywords = [
            'test', 'assert', 'expect', 'verify',
            'should', 'check', 'validate'
        ]
        
        has_test_keywords = any(keyword in code.lower() for keyword in test_keywords)
        if not has_test_keywords:
            quality_issues.append("❌ テストコード: テスト関連キーワードが不足しています")
            results.append("❌ テストキーワード: 不足")
        else:
            results.append("✅ テストキーワード: 検出")
        
        # 実行可能なコードかチェック（コメントのみでないか）
        lines = code.split('\n')
        code_lines = [line for line in lines if line.strip() and not line.strip().startswith(('//', '#'))]
        
        if len(code_lines) < 3:
            quality_issues.append("❌ テストコード: 実行可能なコードが不足しています")
            results.append("❌ 実行可能コード: 不足")
        else:
            results.append("✅ 実行可能コード: 十分")
        
        return {'results': results, 'quality_issues': quality_issues}
    
    def _has_test_code(self, task: Dict) -> bool:
        """タスクにテストコードが含まれているかチェック"""
        description = task.get('description', '').lower()
        if any(keyword in description for keyword in ['test', 'テスト', 'testing']):
            return True
        
        # 出力やパラメータからテストコードを探す
        output = task.get('output', '')
        parameters = task.get('parameters', '')
        
        test_indicators = ['function test', 'class Test', '@Test', 'describe(', 'it(']
        combined_text = f"{output} {parameters}".lower()
        
        return any(indicator in combined_text for indicator in test_indicators)
    
    def _extract_test_code(self, task: Dict) -> str:
        """タスクからテストコードを抽出"""
        # 出力からコードブロックを抽出
        output = task.get('output', '')
        parameters = task.get('parameters', '')
        
        # コードブロックを検索
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', output, re.DOTALL)
        if code_blocks:
            return '\n'.join(code_blocks)
        
        # パラメータからコードを抽出
        if '```' in parameters:
            param_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', parameters, re.DOTALL)
            if param_blocks:
                return '\n'.join(param_blocks)
        
        return output  # フォールバック
    
    def _is_php_code(self, code: str) -> bool:
        """PHPコードか判定"""
        php_indicators = ['<?php', 'function', 'class', '$this', '->']
        return any(indicator in code for indicator in php_indicators)
    
    def _is_javascript_code(self, code: str) -> bool:
        """JavaScriptコードか判定"""
        js_indicators = ['function', 'const', 'let', 'var', '=>', 'describe', 'it']
        return any(indicator in code for indicator in js_indicators)
    
    async def _measure_page_load_time(self, page: Page, url: str) -> float:
        """ページ読み込み時間を計測"""
        try:
            start_time = datetime.now()
            await page.goto(url, wait_until='networkidle')
            end_time = datetime.now()
            return (end_time - start_time).total_seconds() * 1000  # ミリ秒
        except:
            return 0
    
    def _generate_test_summary(self, test_results: List[str], quality_issues: List[str]) -> str:
        """テスト結果サマリーを生成"""
        summary = []
        
        summary.append("📊 テスト結果サマリー")
        summary.append("=" * 50)
        
        # テスト結果
        summary.append("\n✅ 成功テスト:")
        success_tests = [r for r in test_results if '✅' in r or 'OK' in r]
        for test in success_tests:
            summary.append(f"  • {test}")
        
        # 品質問題
        if quality_issues:
            summary.append("\n❌ 品質問題:")
            for issue in quality_issues:
                summary.append(f"  • {issue}")
        else:
            summary.append("\n🎉 品質問題: なし")
        
        # 統計
        total_tests = len(test_results)
        success_count = len(success_tests)
        issue_count = len(quality_issues)
        
        summary.append("\n📈 統計:")
        summary.append(f"  総テスト数: {total_tests}")
        summary.append(f"  成功テスト: {success_count}")
        summary.append(f"  品質問題: {issue_count}")
        
        if total_tests > 0:
            success_rate = (success_count / total_tests) * 100
            summary.append(f"  成功率: {success_rate:.1f}%")
        
        return '\n'.join(summary)