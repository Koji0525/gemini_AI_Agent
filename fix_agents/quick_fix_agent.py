"""
quick_fix_agent.py - 自律型コード修正エージェント
AIからの修正コードを受け取り、ローカルファイルにパッチを適用し、テストを実行
"""

import asyncio
import logging
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

from data_models import (
    BugFixTask,
    ErrorContextModel,
    FixResult,
    ErrorSeverity
)

logger = logging.getLogger(__name__)


class QuickFixAgent:
    """
    自律型修正エージェント - セルフヒーリングシステムの中核
    
    責務:
    1. AIに修正を依頼するプロンプトを構築
    2. AIからの修正コードを検証
    3. ローカルファイルにパッチを適用
    4. 自動テストを実行して検証
    5. GitHub連携(将来実装)
    """
    
    def __init__(
        self,
        browser_controller,
        command_monitor,
        wp_tester=None
    ):
        """
        初期化
        
        Args:
            browser_controller: BrowserController (AI対話用)
            command_monitor: CommandMonitorAgent (コマンド実行用)
            wp_tester: WordPressTester (WordPress関連テスト用)
        """
        self.browser = browser_controller
        self.cmd_monitor = command_monitor
        self.wp_tester = wp_tester
        
        # バックアップディレクトリ
        self.backup_dir = Path("./backups/auto_fix")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 修正履歴
        self.fix_history: List[FixResult] = []
        
        logger.info("✅ QuickFixAgent 初期化完了")
    
    async def execute_bug_fix_task(self, bug_fix_task: BugFixTask) -> FixResult:
        """
        バグ修正タスクを実行
        
        Args:
            bug_fix_task: バグ修正タスク
            
        Returns:
            FixResult: 修正結果
        """
        start_time = datetime.now()
        task_id = bug_fix_task.task_id
        
        try:
            logger.info("=" * 60)
            logger.info(f"🔧 バグ修正タスク実行開始: {task_id}")
            logger.info("=" * 60)
            
            # ステータス更新
            bug_fix_task.status = "in_progress"
            
            # 1. AI修正プロンプトを構築
            fix_prompt = self._build_bug_fix_prompt(bug_fix_task.error_context)
            bug_fix_task.fix_prompt = fix_prompt
            
            logger.info(f"📝 修正プロンプト構築完了 ({len(fix_prompt)}文字)")
            
            # 2. AIに修正を依頼
            ai_result = await self._request_ai_fix(fix_prompt)
            
            if not ai_result['success']:
                return self._create_failed_result(
                    task_id,
                    f"AI修正依頼失敗: {ai_result.get('error')}",
                    start_time
                )
            
            generated_code = ai_result['generated_code']
            logger.info(f"🤖 AI修正コード取得完了 ({len(generated_code)}文字)")
            
            # 3. 修正コードを検証
            validation_result = self._validate_generated_code(
                generated_code,
                bug_fix_task.error_context
            )
            
            if not validation_result['valid']:
                return self._create_failed_result(
                    task_id,
                    f"AI修正コード検証失敗: {validation_result['reason']}",
                    start_time
                )
            
            logger.info("✅ AI修正コード検証合格")
            
            # 4. バックアップ作成
            backup_paths = self._create_backups(bug_fix_task.target_files)
            logger.info(f"💾 バックアップ作成完了: {len(backup_paths)}ファイル")
            
            # 5. パッチ適用
            apply_result = await self._apply_patch(
                bug_fix_task.target_files[0] if bug_fix_task.target_files else None,
                generated_code,
                bug_fix_task.error_context
            )
            
            if not apply_result['success']:
                self._restore_backups(backup_paths)
                return self._create_failed_result(
                    task_id,
                    f"パッチ適用失敗: {apply_result.get('error')}",
                    start_time
                )
            
            logger.info("✅ パッチ適用完了")
            
            # 6. 自動テスト実行
            bug_fix_task.status = "testing"
            test_result = await self._run_automated_tests(bug_fix_task)
            
            if not test_result['success']:
                logger.warning("⚠️ テスト失敗 - バックアップからロールバック")
                self._restore_backups(backup_paths)
                return self._create_failed_result(
                    task_id,
                    f"テスト失敗: {test_result.get('error')}",
                    start_time,
                    test_output=test_result.get('output'),
                    test_errors=test_result.get('errors', [])
                )
            
            logger.info("✅ 全テスト合格")
            
            # 7. 成功結果を作成
            bug_fix_task.status = "success"
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            fix_result = FixResult(
                task_id=task_id,
                success=True,
                modified_files=bug_fix_task.target_files,
                generated_code=generated_code,
                patch_content=apply_result.get('patch_content'),
                test_passed=True,
                test_output=test_result.get('output'),
                execution_time=execution_time
            )
            
            self.fix_history.append(fix_result)
            
            logger.info("=" * 60)
            logger.info(f"🎉 バグ修正完了: {task_id} ({execution_time:.2f}秒)")
            logger.info("=" * 60)
            
            return fix_result
            
        except Exception as e:
            logger.error(f"💥 バグ修正タスク実行エラー: {e}")
            bug_fix_task.status = "failed"
            
            execution_time = (datetime.now() - start_time).total_seconds()
            return self._create_failed_result(
                task_id,
                f"実行エラー: {str(e)}",
                start_time
            )
    
    def _build_bug_fix_prompt(self, error_context: ErrorContextModel) -> str:
        """
        AI修正プロンプトを構築
        
        Args:
            error_context: エラーコンテキスト
            
        Returns:
            str: AI修正プロンプト
        """
        prompt_parts = []
        
        # ヘッダー
        prompt_parts.append("以下のPythonコードにエラーが発生しています。修正されたコードを生成してください。")
        prompt_parts.append("")
        
        # エラー情報
        prompt_parts.append("【エラー情報】")
        prompt_parts.append(f"エラータイプ: {error_context.error_type}")
        prompt_parts.append(f"エラーメッセージ: {error_context.error_message}")
        prompt_parts.append(f"深刻度: {error_context.severity.value}")
        prompt_parts.append("")
        
        # エラー発生位置
        if error_context.error_location:
            prompt_parts.append("【エラー発生位置】")
            prompt_parts.append(f"ファイル: {error_context.error_location.file_path}")
            prompt_parts.append(f"行番号: {error_context.error_location.line_number}")
            if error_context.error_location.function_name:
                prompt_parts.append(f"関数: {error_context.error_location.function_name}")
            prompt_parts.append("")
        
        # 問題のあるコード
        if error_context.problematic_code:
            prompt_parts.append("【問題のある行】")
            prompt_parts.append(f"```python")
            prompt_parts.append(error_context.problematic_code)
            prompt_parts.append(f"```")
            prompt_parts.append("")
        
        # 周辺コード
        if error_context.surrounding_code:
            prompt_parts.append("【周辺コード(前後10行)】")
            prompt_parts.append(f"```python")
            prompt_parts.append(error_context.surrounding_code)
            prompt_parts.append(f"```")
            prompt_parts.append("")
        
        # スタックトレース(重要部分のみ)
        if error_context.stack_frames:
            prompt_parts.append("【スタックトレース】")
            for i, frame in enumerate(error_context.stack_frames[-3:], 1):  # 最後の3フレーム
                prompt_parts.append(f"{i}. {frame.file_path}:{frame.line_number} in {frame.function_name}")
            prompt_parts.append("")
        
        # ローカル変数(重要なもののみ)
        if error_context.local_variables:
            prompt_parts.append("【ローカル変数の状態】")
            for var_name, var_value in list(error_context.local_variables.items())[:5]:
                prompt_parts.append(f"  {var_name} = {var_value}")
            prompt_parts.append("")
        
        # タスク情報
        if error_context.task_description:
            prompt_parts.append("【実行中のタスク】")
            prompt_parts.append(error_context.task_description)
            prompt_parts.append("")
        
        # 修正要件
        prompt_parts.append("【修正要件】")
        prompt_parts.append("1. エラーの根本原因を特定してください")
        prompt_parts.append("2. 最小限の変更で修正してください")
        prompt_parts.append("3. 修正後のコードは完全で、実行可能である必要があります")
        prompt_parts.append("4. コメントで修正内容を説明してください")
        prompt_parts.append("")
        
        # 出力形式
        prompt_parts.append("【出力形式】")
        prompt_parts.append("以下の形式で出力してください:")
        prompt_parts.append("")
        prompt_parts.append("```python")
        prompt_parts.append("# 修正されたコード全体をここに記述")
        prompt_parts.append("# (周辺コードも含めて、置き換え可能な完全なコードを出力)")
        prompt_parts.append("```")
        prompt_parts.append("")
        prompt_parts.append("【重要】")
        prompt_parts.append("- コードブロックは必ず ```python ... ``` で囲んでください")
        prompt_parts.append("- 不完全なコードや省略は避けてください")
        prompt_parts.append("- インポート文も含めてください")
        
        return "\n".join(prompt_parts)
    
    async def _request_ai_fix(self, fix_prompt: str) -> Dict[str, Any]:
        """
        AIに修正を依頼
        
        Args:
            fix_prompt: 修正プロンプト
            
        Returns:
            Dict: AI応答結果
        """
        try:
            # AIにプロンプトを送信
            if not hasattr(self.browser, 'send_prompt_and_wait'):
                return {
                    'success': False,
                    'error': 'BrowserControllerにsend_prompt_and_waitメソッドがありません'
                }
            
            success = await self.browser.send_prompt_and_wait(
                fix_prompt,
                max_wait=180  # 3分
            )
            
            if not success:
                return {
                    'success': False,
                    'error': 'AIプロンプト送信または応答待機失敗'
                }
            
            # AI応答を抽出
            if not hasattr(self.browser, 'extract_latest_text_response'):
                return {
                    'success': False,
                    'error': 'BrowserControllerにextract_latest_text_responseメソッドがありません'
                }
            
            response_text = await self.browser.extract_latest_text_response()
            
            if not response_text or len(response_text) < 50:
                return {
                    'success': False,
                    'error': 'AI応答が空または短すぎます'
                }
            
            # コードブロックを抽出
            code_blocks = re.findall(r'```python\s*\n(.*?)```', response_text, re.DOTALL)
            
            if not code_blocks:
                return {
                    'success': False,
                    'error': 'AI応答にPythonコードブロックが見つかりません'
                }
            
            # 最大のコードブロックを採用
            generated_code = max(code_blocks, key=len)
            
            return {
                'success': True,
                'generated_code': generated_code,
                'full_response': response_text
            }
            
        except Exception as e:
            logger.error(f"❌ AI修正依頼エラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _validate_generated_code(
        self,
        generated_code: str,
        error_context: ErrorContextModel
    ) -> Dict[str, Any]:
        """
        AI生成コードを検証
        
        Args:
            generated_code: AI生成コード
            error_context: エラーコンテキスト
            
        Returns:
            Dict: 検証結果
        """
        # 1. 最小長チェック
        if len(generated_code.strip()) < 20:
            return {
                'valid': False,
                'reason': 'コードが短すぎます'
            }
        
        # 2. Pythonコードの基本構造チェック
        if not any(kw in generated_code for kw in ['def ', 'class ', 'import ', 'from ']):
            return {
                'valid': False,
                'reason': 'Pythonコードの基本構造が見つかりません'
            }
        
        # 3. エラー関連のキーワードがないかチェック
        if error_context.error_type == "ImportError" or error_context.error_type == "ModuleNotFoundError":
            # インポートエラーの場合、適切なインポート文があるか
            if 'import ' not in generated_code and 'from ' not in generated_code:
                return {
                    'valid': False,
                    'reason': 'インポートエラーの修正にインポート文がありません'
                }
        
        # 4. コードブロックの閉じ忘れチェック
        open_braces = generated_code.count('{')
        close_braces = generated_code.count('}')
        open_parens = generated_code.count('(')
        close_parens = generated_code.count(')')
        open_brackets = generated_code.count('[')
        close_brackets = generated_code.count(']')
        
        if (open_braces != close_braces or 
            open_parens != close_parens or 
            open_brackets != close_brackets):
            return {
                'valid': False,
                'reason': '括弧の対応が不正です'
            }
        
        # 5. 構文チェック(簡易)
        try:
            compile(generated_code, '<string>', 'exec')
        except SyntaxError as e:
            return {
                'valid': False,
                'reason': f'構文エラー: {e}'
            }
        
        return {
            'valid': True,
            'reason': '検証合格'
        }
    
    def _create_backups(self, file_paths: List[str]) -> Dict[str, str]:
        """
        ファイルのバックアップを作成
        
        Args:
            file_paths: バックアップ対象ファイルパス
            
        Returns:
            Dict: {元ファイル: バックアップパス}
        """
        backup_paths = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for file_path in file_paths:
            try:
                src = Path(file_path)
                if not src.exists():
                    logger.warning(f"⚠️ バックアップ対象が存在しません: {file_path}")
                    continue
                
                # バックアップファイル名を生成
                backup_name = f"{src.stem}_backup_{timestamp}{src.suffix}"
                backup_path = self.backup_dir / backup_name
                
                # コピー
                shutil.copy2(src, backup_path)
                backup_paths[file_path] = str(backup_path)
                
                logger.info(f"💾 バックアップ: {file_path} → {backup_path}")
                
            except Exception as e:
                logger.error(f"❌ バックアップ失敗: {file_path} - {e}")
        
        return backup_paths
    
    def _restore_backups(self, backup_paths: Dict[str, str]):
        """バックアップからファイルを復元"""
        for original_path, backup_path in backup_paths.items():
            try:
                shutil.copy2(backup_path, original_path)
                logger.info(f"♻️ 復元: {backup_path} → {original_path}")
            except Exception as e:
                logger.error(f"❌ 復元失敗: {original_path} - {e}")
    
    async def _apply_patch(
        self,
        target_file: Optional[str],
        generated_code: str,
        error_context: ErrorContextModel
    ) -> Dict[str, Any]:
        """
        生成されたコードをファイルに適用
        
        Args:
            target_file: 対象ファイルパス
            generated_code: 生成されたコード
            error_context: エラーコンテキスト
            
        Returns:
            Dict: 適用結果
        """
        try:
            if not target_file:
                # エラー位置から対象ファイルを特定
                if error_context.error_location:
                    target_file = error_context.error_location.file_path
                else:
                    return {
                        'success': False,
                        'error': '対象ファイルが特定できません'
                    }
            
            target_path = Path(target_file)
            
            if not target_path.exists():
                return {
                    'success': False,
                    'error': f'対象ファイルが存在しません: {target_file}'
                }
            
            # 元のファイル内容を読み込み
            with open(target_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # 新しい内容を書き込み
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(generated_code)
            
            logger.info(f"✅ パッチ適用完了: {target_file}")
            
            # Diff形式のパッチ内容を生成(簡易版)
            patch_content = self._generate_simple_diff(
                original_content,
                generated_code,
                target_file
            )
            
            return {
                'success': True,
                'target_file': target_file,
                'patch_content': patch_content
            }
            
        except Exception as e:
            logger.error(f"❌ パッチ適用エラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_simple_diff(
        self,
        original: str,
        modified: str,
        filename: str
    ) -> str:
        """簡易Diff形式のパッチ内容を生成"""
        lines = []
        lines.append(f"--- {filename} (original)")
        lines.append(f"+++ {filename} (modified)")
        lines.append(f"@@ -{len(original.splitlines())},{len(modified.splitlines())} @@")
        
        # 簡易的な差分表示
        orig_lines = original.splitlines()
        mod_lines = modified.splitlines()
        
        max_lines = max(len(orig_lines), len(mod_lines))
        
        for i in range(min(10, max_lines)):  # 最初の10行のみ
            if i < len(orig_lines):
                lines.append(f"- {orig_lines[i]}")
            if i < len(mod_lines):
                lines.append(f"+ {mod_lines[i]}")
        
        if max_lines > 10:
            lines.append(f"... ({max_lines - 10} more lines)")
        
        return "\n".join(lines)
    
    async def _run_automated_tests(self, bug_fix_task: BugFixTask) -> Dict[str, Any]:
        """
        自動テストを実行
        
        Args:
            bug_fix_task: バグ修正タスク
            
        Returns:
            Dict: テスト結果
        """
        try:
            error_context = bug_fix_task.error_context
            
            # テストコマンドを決定
            test_command = self._determine_test_command(error_context)
            
            if not test_command:
                logger.warning("⚠️ テストコマンドが特定できません - スキップ")
                return {
                    'success': True,
                    'output': 'テストコマンド未特定のためスキップ',
                    'errors': []
                }
            
            logger.info(f"🧪 テスト実行: {test_command}")
            
            # コマンド実行
            result = await self.cmd_monitor.execute_command(
                test_command,
                timeout=120
            )
            
            # テスト結果を評価
            if result['return_code'] == 0 and not result['has_errors']:
                return {
                    'success': True,
                    'output': result['stdout'],
                    'errors': []
                }
            else:
                return {
                    'success': False,
                    'output': result['stdout'],
                    'errors': result['errors'],
                    'error': f"テスト失敗 (return_code={result['return_code']})"
                }
            
        except Exception as e:
            logger.error(f"❌ テスト実行エラー: {e}")
            return {
                'success': False,
                'error': str(e),
                'errors': [str(e)]
            }
    
    def _determine_test_command(self, error_context: ErrorContextModel) -> Optional[str]:
        """エラーコンテキストから適切なテストコマンドを決定"""
        
        # WordPress関連のエラー
        if error_context.wp_context or 'wordpress' in str(error_context.error_location).lower():
            return "wp plugin list"  # 基本的な動作確認
        
        # Pythonモジュールのインポートエラー
        if error_context.error_category.value == "import_error":
            # インポート可能性をチェック
            if error_context.error_location:
                module_name = Path(error_context.error_location.file_path).stem
                return f"python -c 'import {module_name}'"
        
        # 一般的なPythonコード
        if error_context.error_location:
            file_path = error_context.error_location.file_path
            if file_path.endswith('.py'):
                # 構文チェック
                return f"python -m py_compile {file_path}"
        
        return None
    
    def _create_failed_result(
        self,
        task_id: str,
        error_message: str,
        start_time: datetime,
        test_output: Optional[str] = None,
        test_errors: List[str] = None
    ) -> FixResult:
        """失敗結果を作成"""
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return FixResult(
            task_id=task_id,
            success=False,
            test_passed=False,
            test_output=test_output,
            test_errors=test_errors or [],
            execution_time=execution_time,
            error_message=error_message
        )
    
    def get_fix_history(self) -> List[FixResult]:
        """修正履歴を取得"""
        return self.fix_history.copy()
    
    def get_success_rate(self) -> float:
        """修正成功率を計算"""
        if not self.fix_history:
            return 0.0
        
        success_count = sum(1 for result in self.fix_history if result.success)
        return (success_count / len(self.fix_history)) * 100