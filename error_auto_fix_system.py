#!/usr/bin/env python3
"""
エラー自動修正システム
- タスクエラーを検出
- エラー内容を分析
- main_hybrid_fix.py で自動修正
- 修正後に再実行
- 最大3回まで試行
"""
import asyncio
import subprocess
import logging
from datetime import datetime
from pathlib import Path
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorAutoFixSystem:
    """エラー自動修正システム"""
    
    def __init__(self):
        self.max_retries = 3
        self.error_log_path = Path("error_logs")
        self.error_log_path.mkdir(exist_ok=True)
        self.fix_history = []
    
    def analyze_error(self, error_message: str) -> dict:
        """エラーを分析"""
        logger.info("🔍 エラー分析中...")
        
        analysis = {
            'type': 'unknown',
            'severity': 'medium',
            'fixable': True,
            'suggested_fix': None
        }
        
        error_lower = error_message.lower()
        
        # エラーパターンのマッチング
        if 'keyerror' in error_lower or "'description'" in error_lower:
            analysis['type'] = 'missing_key'
            analysis['severity'] = 'low'
            analysis['suggested_fix'] = 'タスクデータ構造の修正'
            
        elif 'attributeerror' in error_lower:
            analysis['type'] = 'attribute_error'
            analysis['severity'] = 'medium'
            analysis['suggested_fix'] = '属性またはメソッドの確認'
            
        elif 'importerror' in error_lower or 'modulenotfounderror' in error_lower:
            analysis['type'] = 'import_error'
            analysis['severity'] = 'high'
            analysis['suggested_fix'] = 'モジュールのインストールまたはインポートパス修正'
            
        elif 'syntaxerror' in error_lower:
            analysis['type'] = 'syntax_error'
            analysis['severity'] = 'high'
            analysis['suggested_fix'] = '構文エラーの修正'
            
        elif 'typeerror' in error_lower:
            analysis['type'] = 'type_error'
            analysis['severity'] = 'medium'
            analysis['suggested_fix'] = '型の不一致を修正'
            
        elif 'timeout' in error_lower:
            analysis['type'] = 'timeout'
            analysis['severity'] = 'low'
            analysis['suggested_fix'] = 'タイムアウト時間の延長または処理の最適化'
            
        elif 'authentication' in error_lower or 'credential' in error_lower:
            analysis['type'] = 'auth_error'
            analysis['severity'] = 'high'
            analysis['fixable'] = False
            analysis['suggested_fix'] = '認証情報の確認（手動対応必要）'
        
        logger.info(f"📊 エラータイプ: {analysis['type']}")
        logger.info(f"⚠️ 深刻度: {analysis['severity']}")
        logger.info(f"🔧 修正可能: {analysis['fixable']}")
        logger.info(f"💡 推奨修正: {analysis['suggested_fix']}")
        
        return analysis
    
    def save_error_log(self, task: dict, error: str, analysis: dict) -> Path:
        """エラーログを保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        task_id = task.get('task_id', 'unknown')
        error_file = self.error_log_path / f"error_{task_id}_{timestamp}.json"
        
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'task': task,
            'error': error,
            'analysis': analysis,
            'fix_attempts': []
        }
        
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(error_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 エラーログ保存: {error_file}")
        return error_file
    
    async def attempt_auto_fix(self, error_file: Path, attempt: int) -> dict:
        """自動修正を試行"""
        logger.info("=" * 80)
        logger.info(f"🔧 自動修正試行 {attempt}/{self.max_retries}")
        logger.info("=" * 80)
        
        try:
            # main_hybrid_fix.py を実行
            result = subprocess.run(
                ['python', 'main_hybrid_fix.py', '--error-file', str(error_file)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info("✅ 自動修正成功")
                return {
                    'success': True,
                    'output': result.stdout,
                    'attempt': attempt
                }
            else:
                logger.warning(f"⚠️ 自動修正失敗（試行{attempt}）")
                logger.warning(f"出力: {result.stderr[:200]}...")
                return {
                    'success': False,
                    'output': result.stderr,
                    'attempt': attempt
                }
                
        except subprocess.TimeoutExpired:
            logger.error("❌ 自動修正タイムアウト（5分）")
            return {
                'success': False,
                'output': 'Timeout after 5 minutes',
                'attempt': attempt
            }
        except Exception as e:
            logger.error(f"❌ 自動修正エラー: {e}")
            return {
                'success': False,
                'output': str(e),
                'attempt': attempt
            }
    
    async def fix_and_retry(self, task: dict, error: str, executor) -> dict:
        """エラー修正と再実行"""
        logger.info("\n" + "=" * 80)
        logger.info("🚑 エラー自動修正システム起動")
        logger.info("=" * 80)
        
        # 1. エラー分析
        analysis = self.analyze_error(error)
        
        # 2. エラーログ保存
        error_file = self.save_error_log(task, error, analysis)
        
        # 3. 修正不可能なエラーの場合
        if not analysis['fixable']:
            logger.error("❌ 自動修正不可能 - 手動対応が必要")
            return {
                'success': False,
                'error': error,
                'message': '手動対応が必要です',
                'analysis': analysis
            }
        
        # 4. 自動修正を試行
        for attempt in range(1, self.max_retries + 1):
            # 自動修正実行
            fix_result = await self.attempt_auto_fix(error_file, attempt)
            
            self.fix_history.append(fix_result)
            
            if fix_result['success']:
                logger.info(f"✅ 修正成功（試行{attempt}）")
                
                # 5. タスクを再実行
                logger.info("🔄 タスクを再実行中...")
                
                try:
                    retry_result = await executor.create_draft(task)
                    
                    if retry_result['success']:
                        logger.info("🎉 再実行成功！")
                        return {
                            'success': True,
                            'message': f'自動修正後に再実行成功（試行{attempt}）',
                            'fix_attempts': attempt
                        }
                    else:
                        logger.warning(f"⚠️ 再実行失敗 - 別のエラーが発生")
                        error = retry_result.get('error', 'Unknown error')
                        # 次の試行へ
                        
                except Exception as e:
                    logger.error(f"❌ 再実行エラー: {e}")
                    error = str(e)
            
            if attempt < self.max_retries:
                logger.info(f"⏳ 次の試行まで5秒待機...")
                await asyncio.sleep(5)
        
        # 6. 全ての試行が失敗
        logger.error("❌ 最大試行回数到達 - 修正失敗")
        return {
            'success': False,
            'error': error,
            'message': f'{self.max_retries}回の修正試行が全て失敗',
            'fix_history': self.fix_history
        }

# グローバルインスタンス
auto_fix_system = ErrorAutoFixSystem()

async def test_auto_fix():
    """テスト実行"""
    from wordpress_task_executor import WordPressTaskExecutor
    
    executor = WordPressTaskExecutor()
    await executor.initialize()
    
    # わざとエラーを起こすタスク
    test_task = {
        'task_id': 'TEST_ERROR',
        # 'description': 'これは意図的なエラーテスト',  # これをコメントアウトしてKeyErrorを発生させる
        'required_role': 'wp_dev'
    }
    
    try:
        result = await executor.create_draft(test_task)
        if not result['success']:
            # エラーが発生したので自動修正
            fix_result = await auto_fix_system.fix_and_retry(
                test_task,
                result['error'],
                executor
            )
            print(f"\n修正結果: {fix_result}")
    finally:
        await executor.cleanup()

if __name__ == "__main__":
    asyncio.run(test_auto_fix())
