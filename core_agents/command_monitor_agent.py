# command_monitor_agent.py - ACF監視強化版
import asyncio
import re
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

class CommandMonitorAgent:
    """コマンド実行と出力監視 - ACF/WP-CLI特化版"""
    

    def __init__(self, browser_controller, sheets_manager):
        self.browser_controller = browser_controller
        self.sheets_manager = sheets_manager
    
        # 既存のエラーパターン
        self.error_patterns = [
            r'Error:', r'Exception:', r'Traceback'
        ]
    
        # === 新規追加: PHP固有のエラーパターン ===
        self.php_error_patterns = [
            r'Parse error:',
            r'Syntax error',
            r'Fatal error:',
            r'Warning:',
            r'Notice:',
            r'Undefined function',
            r'Undefined variable',
            r'Class.*not found',
            r'Call to undefined function',
            r'Cannot modify header information',
        ]
    
        # WP-CLI専用エラーパターン（強化版）
        self.wp_cli_error_patterns = [
            r'Error:\s+',
            r'Fatal error:',
            r'Plugin not found',
            r'Could not create',
            r'Database connection error',
            r'Warning:\s+[A-Z]',
            # === 新規追加: CPT登録関連エラー ===
            r'Invalid post type',
            r'Post type.*already exists',
            r'register_post_type.*failed',
            r'Permission denied',
            r'Failed to create',
        ]
    
        # === 新規追加: ACF専用エラーパターン ===
        self.acf_error_patterns = [
            r'ACF:\s+Error',
            r'Field group not found',
            r'Invalid field group',
            r'JSON decode error',
            r'acf_add_local_field_group.*failed',
            r'ACF.*not activated',
        ]
    
        self.wp_cli_success_patterns = [
            r'Success:',
            r'Plugin .* activated',
            r'Updated \d+ post',
            r'Created \d+ post',
            # === 新規追加: CPT登録成功パターン ===
            r'Post type.*registered',
            r'Custom post type.*created',
            r'Registration of.*successful',
        ]
    
        # === 新規追加: CPT警告パターン ===
        self.cpt_warning_patterns = [
            r'Post type.*already registered',
            r'Duplicate post type',
            r'Menu position conflict',
            r'Rewrite rules may need to be flushed',
        ]
    
    def _detect_errors(self, output: str) -> bool:
        """エラー検出 - ACF対応強化"""
        # 汎用エラーチェック
        for pattern in self.error_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                return True
        
        # WP-CLI専用エラーチェック
        for pattern in self.wp_cli_error_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                logger.warning(f"⚠️ WP-CLI/ACFエラー検出: {pattern}")
                return True
        
        return False
    
    def _validate_wp_cli_success(self, output: str, expected_action: str) -> bool:
        """WP-CLI実行の成功検証 - ACF対応"""
        # 成功パターンのマッチング
        for pattern in self.wp_cli_success_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                logger.info(f"✅ WP-CLI成功: {expected_action}")
                return True
        
        logger.error(f"❌ WP-CLI成功メッセージ未検出: {expected_action}")
        return False
    
    def _extract_acf_field_group_info(self, output: str) -> Optional[Dict]:
        """ACFフィールドグループ情報の抽出（新規追加）"""
        try:
            info = {}
            
            # フィールドグループキーの抽出
            key_match = re.search(r'group_([a-z0-9_]+)', output)
            if key_match:
                info['key'] = key_match.group(0)
            
            # フィールド数の抽出
            fields_match = re.search(r'(\d+)\s+field', output, re.IGNORECASE)
            if fields_match:
                info['field_count'] = int(fields_match.group(1))
            
            # エラーの抽出
            errors = self._extract_errors(output)
            if errors:
                info['errors'] = errors
            
            # 警告の抽出
            warnings = self._extract_acf_warnings(output)
            if warnings:
                info['warnings'] = warnings
            
            return info if info else None
            
        except Exception as e:
            logger.error(f"ACF情報抽出エラー: {e}")
            return None
    
    def _extract_acf_warnings(self, output: str) -> List[str]:
        """ACF警告メッセージを抽出（新規追加）"""
        warnings = []
        lines = output.split('\n')
        
        for i, line in enumerate(lines):
            for pattern in self.acf_warning_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    context = '\n'.join(lines[max(0, i-1):min(len(lines), i+2)])
                    warnings.append(context)
                    break
        
        return warnings
    
    async def execute_command(self, command: str, timeout: int = 300) -> Dict:
        """コマンドを実行して出力を監視 - ACF情報抽出追加"""
        try:
            logger.info(f"🔧 コマンド実行: {command}")
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            output = stdout.decode('utf-8', errors='ignore')
            error_output = stderr.decode('utf-8', errors='ignore')
            return_code = process.returncode
            
            # === 新規追加: ACFコマンドの特別処理 ===
            acf_info = None
            if 'wp acf' in command:
                acf_info = self._extract_acf_field_group_info(output + error_output)
                if acf_info:
                    logger.info(f"📋 ACF情報: {acf_info}")
            
            result = {
                'command': command,
                'return_code': return_code,
                'stdout': output,
                'stderr': error_output,
                'timestamp': datetime.now().isoformat(),
                'has_errors': self._detect_errors(output + error_output),
                'errors': self._extract_errors(output + error_output),
                'warnings': self._extract_warnings(output + error_output),
                'acf_info': acf_info  # ACF固有情報
            }
            
            # 結果のサマリーログ
            if result['has_errors']:
                logger.error(f"❌ コマンド実行エラー: {command}")
                for error in result['errors']:
                    logger.error(f"   {error}")
            elif result['warnings']:
                logger.warning(f"⚠️ コマンド実行警告: {command}")
                for warning in result['warnings']:
                    logger.warning(f"   {warning}")
            else:
                logger.info(f"✅ コマンド実行成功: {command}")
            
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"⏱️ コマンドタイムアウト ({timeout}秒): {command}")
            return {
                'command': command,
                'return_code': -1,
                'stdout': '',
                'stderr': f'コマンド実行タイムアウト ({timeout}秒)',
                'timestamp': datetime.now().isoformat(),
                'has_errors': True,
                'errors': [f'実行タイムアウト ({timeout}秒)'],
                'warnings': [],
                'acf_info': None
            }
        except Exception as e:
            logger.error(f"💥 コマンド実行エラー: {e}")
            return {
                'command': command,
                'return_code': -1,
                'stdout': '',
                'stderr': str(e),
                'timestamp': datetime.now().isoformat(),
                'has_errors': True,
                'errors': [str(e)],
                'warnings': [],
                'acf_info': None
            }
    
    def _extract_errors(self, output: str) -> List[str]:
        """エラーメッセージを抽出"""
        errors = []
        lines = output.split('\n')
        
        # 汎用エラー + WP-CLI/ACFエラー
        all_error_patterns = self.error_patterns + self.wp_cli_error_patterns
        
        for i, line in enumerate(lines):
            for pattern in all_error_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # エラー行とその前後2行を取得
                    start = max(0, i - 2)
                    end = min(len(lines), i + 3)
                    context = '\n'.join(lines[start:end])
                    errors.append(context)
                    break
        
        return errors
    
    def _extract_warnings(self, output: str) -> List[str]:
        """警告メッセージを抽出"""
        warnings = []
        lines = output.split('\n')
        
        warning_patterns = [r'Warning:', r'Notice:']
        
        for i, line in enumerate(lines):
            for pattern in warning_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    context = '\n'.join(lines[max(0, i-1):min(len(lines), i+2)])
                    warnings.append(context)
                    break
        
        # ACF警告も追加
        acf_warnings = self._extract_acf_warnings(output)
        warnings.extend(acf_warnings)
        
        return warnings
    
    async def monitor_acf_import_process(self, json_path: Path, timeout: int = 180) -> Dict:
        """ACFインポートプロセスの専用監視（新規追加）"""
        try:
            logger.info(f"📥 ACFインポート監視開始: {json_path}")
            
            # WP-CLIコマンド実行
            command = f"wp acf import {json_path}"
            result = await self.execute_command(command, timeout=timeout)
            
            # 成功検証
            is_success = (
                result['return_code'] == 0 and
                not result['has_errors'] and
                self._validate_wp_cli_success(result['stdout'], 'ACF import')
            )
            
            if is_success:
                logger.info("✅ ACFインポート成功")
            else:
                logger.error("❌ ACFインポート失敗")
            
            return {
                'success': is_success,
                'command_result': result,
                'acf_info': result.get('acf_info'),
                'errors': result.get('errors', []),
                'warnings': result.get('warnings', [])
            }
            
        except Exception as e:
            logger.error(f"ACFインポート監視エラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }