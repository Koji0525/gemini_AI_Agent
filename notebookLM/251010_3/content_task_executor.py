"""
content_task_executor.py - コンテンツ生成タスク専門実行モジュール
AIサイトとの対話、プロンプト送信、応答抽出、検証を担当
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

# 設定
from config_utils import ErrorHandler, config

# データ管理
from sheets_manager import GoogleSheetsManager

logger = logging.getLogger(__name__)


class ContentTaskExecutor:
    """
    コンテンツ生成タスクの専門実行モジュール
    
    ブラウザ制御を通じたAI対話、コンテンツ生成、
    抽出、検証ロジックを統合
    """
    
    def __init__(
        self,
        browser_controller,
        sheets_manager: GoogleSheetsManager
    ):
        """
        初期化
        
        Args:
            browser_controller: BrowserControllerインスタンス
            sheets_manager: GoogleSheetsManagerインスタンス
        """
        self.browser = browser_controller
        self.sheets_manager = sheets_manager
        
        # AI設定
        self.ai_sites = {
            'gemini': 'https://gemini.google.com',
            'deepseek': 'https://chat.deepseek.com',
            'claude': 'https://claude.ai'
        }
        
        # デフォルトAI
        self.default_ai = 'gemini'
        
        # タイムアウト設定
        self.default_timeout = 180.0
        self.generation_timeout = 240.0
        
        logger.info("✅ ContentTaskExecutor 初期化完了")
    
    async def execute_content_task(self, task: Dict) -> Dict:
        """
        コンテンツ生成タスクを実行
        
        Args:
            task: タスク情報辞書
            
        Returns:
            Dict: 実行結果
        """
        task_id = task.get('task_id', 'UNKNOWN')
        
        try:
            logger.info("=" * 60)
            logger.info(f"✍️ コンテンツタスク実行開始: {task_id}")
            logger.info("=" * 60)
            
            # タスクパラメータ抽出
            prompt = task.get('prompt', task.get('description', ''))
            ai_site = task.get('ai_site', self.default_ai).lower()
            output_format = task.get('output_format', 'markdown')
            
            # ブラウザチェック
            if not self.browser:
                return {
                    'success': False,
                    'error': 'ブラウザコントローラーが初期化されていません'
                }
            
            # AIサイトナビゲーション
            nav_result = await self._navigate_to_ai_site(ai_site)
            if not nav_result['success']:
                return nav_result
            
            # プロンプト送信と応答待機
            response_result = await self._send_prompt_and_wait(
                prompt, 
                timeout=self.generation_timeout
            )
            if not response_result['success']:
                return response_result
            
            # 応答テキスト抽出
            extract_result = await self._extract_response_text()
            if not extract_result['success']:
                return extract_result
            
            content = extract_result['content']
            
            # コンテンツ検証
            validation_result = self._validate_content(content, task)
            if not validation_result['valid']:
                logger.warning(f"⚠️ コンテンツ検証警告: {validation_result['message']}")
            
            # 出力ファイル保存
            output_file = await self._save_content_output(
                task_id, 
                content, 
                output_format
            )
            
            logger.info(f"✅ コンテンツタスク {task_id} 完了")
            
            return {
                'success': True,
                'content': content,
                'output_file': output_file,
                'ai_site': ai_site,
                'validation': validation_result,
                'full_text': content,
                'summary': content[:500] if len(content) > 500 else content
            }
            
        except asyncio.TimeoutError:
            logger.error(f"⏱️ コンテンツタスク {task_id} タイムアウト")
            return {
                'success': False,
                'error': f'タイムアウト ({self.generation_timeout}秒)'
            }
        
        except Exception as e:
            logger.error(f"❌ コンテンツタスク {task_id} 実行エラー")
            ErrorHandler.log_error(e, f"ContentTaskExecutor.execute_content_task({task_id})")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _navigate_to_ai_site(self, ai_site: str) -> Dict:
        """
        AIサイトにナビゲーション
        
        Args:
            ai_site: AIサイト識別子 ('gemini', 'deepseek', 'claude')
            
        Returns:
            Dict: ナビゲーション結果
        """
        try:
            logger.info(f"🌐 {ai_site.upper()} にナビゲーション中...")
            
            # サイトURL取得
            if ai_site not in self.ai_sites:
                logger.warning(f"⚠️ 未知のAIサイト: {ai_site}, デフォルト {self.default_ai} を使用")
                ai_site = self.default_ai
            
            url = self.ai_sites[ai_site]
            
            # ブラウザメソッド呼び出し
            if ai_site == 'gemini':
                if hasattr(self.browser, 'navigate_to_gemini'):
                    result = await self.browser.navigate_to_gemini()
                else:
                    result = await self.browser.navigate_to_url(url)
            elif ai_site == 'deepseek':
                if hasattr(self.browser, 'navigate_to_deepseek'):
                    result = await self.browser.navigate_to_deepseek()
                else:
                    result = await self.browser.navigate_to_url(url)
            else:
                result = await self.browser.navigate_to_url(url)
            
            if result:
                logger.info(f"✅ {ai_site.upper()} へのナビゲーション成功")
                return {'success': True}
            else:
                logger.error(f"❌ {ai_site.upper()} へのナビゲーション失敗")
                return {'success': False, 'error': f'{ai_site} へのナビゲーション失敗'}
        
        except Exception as e:
            logger.error(f"❌ AIサイトナビゲーションエラー: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _send_prompt_and_wait(
        self, 
        prompt: str, 
        timeout: float = None
    ) -> Dict:
        """
        プロンプトを送信して応答を待機
        
        Args:
            prompt: 送信するプロンプト
            timeout: タイムアウト時間（秒）
            
        Returns:
            Dict: 実行結果
        """
        try:
            if timeout is None:
                timeout = self.generation_timeout
            
            logger.info(f"📤 プロンプト送信中... (タイムアウト: {timeout}秒)")
            
            # 統合メソッド使用（存在する場合）
            if hasattr(self.browser, 'send_prompt_and_wait'):
                result = await self.browser.send_prompt_and_wait(
                    prompt, 
                    timeout=timeout
                )
                if result:
                    logger.info("✅ プロンプト送信と応答待機完了")
                    return {'success': True}
                else:
                    logger.error("❌ プロンプト送信または応答待機失敗")
                    return {'success': False, 'error': 'プロンプト送信失敗'}
            else:
                # 個別メソッド使用（後方互換性）
                if hasattr(self.browser, 'send_prompt'):
                    await self.browser.send_prompt(prompt)
                else:
                    logger.error("❌ send_prompt メソッドが見つかりません")
                    return {'success': False, 'error': 'send_prompt メソッド未実装'}
                
                # 応答待機
                if hasattr(self.browser, 'wait_for_text_generation'):
                    await self.browser.wait_for_text_generation(timeout)
                    logger.info("✅ プロンプト送信と応答待機完了")
                    return {'success': True}
                else:
                    logger.warning("⚠️ wait_for_text_generation メソッドなし - 固定待機")
                    await asyncio.sleep(30)  # フォールバック待機
                    return {'success': True}
        
        except asyncio.TimeoutError:
            logger.error(f"⏱️ プロンプト応答タイムアウト ({timeout}秒)")
            return {'success': False, 'error': 'タイムアウト'}
        
        except Exception as e:
            logger.error(f"❌ プロンプト送信エラー: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _extract_response_text(self) -> Dict:
        """
        AIからの応答テキストを抽出
        
        Returns:
            Dict: 抽出結果 {'success': bool, 'content': str}
        """
        try:
            logger.info("📥 応答テキスト抽出中...")
            
            if not hasattr(self.browser, 'extract_latest_text_response'):
                logger.error("❌ extract_latest_text_response メソッドが見つかりません")
                return {'success': False, 'error': '応答抽出メソッド未実装'}
            
            content = await self.browser.extract_latest_text_response()
            
            if not content:
                logger.warning("⚠️ 抽出されたコンテンツが空です")
                return {'success': False, 'error': '抽出コンテンツなし'}
            
            logger.info(f"✅ 応答テキスト抽出完了 ({len(content)}文字)")
            return {'success': True, 'content': content}
        
        except Exception as e:
            logger.error(f"❌ 応答テキスト抽出エラー: {e}")
            return {'success': False, 'error': str(e)}
    
    def _validate_content(self, content: str, task: Dict) -> Dict:
        """
        生成コンテンツを検証
        
        Args:
            content: 検証対象コンテンツ
            task: タスク情報
            
        Returns:
            Dict: 検証結果 {'valid': bool, 'message': str, 'warnings': list}
        """
        warnings = []
        
        # 最小文字数チェック
        min_length = task.get('min_length', 100)
        if len(content.strip()) < min_length:
            warnings.append(f'コンテンツが短すぎます（{len(content)}文字 < {min_length}文字）')
        
        # コードブロック完全性チェック
        if '```' in content:
            code_block_count = content.count('```')
            if code_block_count % 2 != 0:
                warnings.append('コードブロックが不完全です（閉じられていないブロックがあります）')
        
        # PHPコード完全性チェック
        if '<?php' in content:
            if '?>' not in content and not content.rstrip().endswith('}'):
                warnings.append('PHPコードが不完全な可能性があります')
        
        # 必須キーワードチェック
        required_keywords = task.get('required_keywords', [])
        missing_keywords = [kw for kw in required_keywords if kw.lower() not in content.lower()]
        if missing_keywords:
            warnings.append(f'必須キーワード不足: {", ".join(missing_keywords)}')
        
        valid = len(warnings) == 0
        message = '検証合格' if valid else f'{len(warnings)}件の警告'
        
        return {
            'valid': valid,
            'message': message,
            'warnings': warnings
        }
    
    async def _save_content_output(
        self, 
        task_id: str, 
        content: str, 
        output_format: str = 'markdown'
    ) -> str:
        """
        コンテンツを出力ファイルに保存
        
        Args:
            task_id: タスクID
            content: 保存するコンテンツ
            output_format: 出力形式 ('markdown', 'text', 'html')
            
        Returns:
            str: 保存されたファイルパス
        """
        try:
            # ファイル拡張子マッピング
            ext_map = {
                'markdown': '.md',
                'text': '.txt',
                'html': '.html',
                'php': '.php'
            }
            ext = ext_map.get(output_format, '.txt')
            
            # ファイル名生成
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"content_{task_id}_{timestamp}{ext}"
            
            # 出力ディレクトリ確保
            output_dir = Path(config.OUTPUT_DIR) if hasattr(config, 'OUTPUT_DIR') else Path('./outputs')
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # ファイル保存
            output_path = output_dir / filename
            
            if hasattr(self.browser, 'save_text_to_file'):
                # BrowserControllerの保存メソッド使用
                saved_path = await self.browser.save_text_to_file(
                    content,
                    str(output_path)
                )
                logger.info(f"✅ コンテンツ保存完了: {saved_path}")
                return str(saved_path)
            else:
                # 直接ファイル保存
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"✅ コンテンツ保存完了: {output_path}")
                return str(output_path)
        
        except Exception as e:
            logger.error(f"❌ コンテンツ保存エラー: {e}")
            ErrorHandler.log_error(e, "ContentTaskExecutor._save_content_output")
            return ""
    
    async def execute_multi_step_content_task(self, task: Dict) -> Dict:
        """
        複数ステップのコンテンツ生成タスクを実行
        
        例: プロンプト1 → 応答抽出 → プロンプト2 → 最終出力
        
        Args:
            task: タスク情報辞書（'steps'キーに複数ステップ定義）
            
        Returns:
            Dict: 実行結果
        """
        task_id = task.get('task_id', 'UNKNOWN')
        steps = task.get('steps', [])
        
        if not steps:
            logger.warning("⚠️ ステップ定義なし - 単一タスクとして実行")
            return await self.execute_content_task(task)
        
        try:
            logger.info("=" * 60)
            logger.info(f"🔄 マルチステップタスク実行: {task_id}")
            logger.info(f"ステップ数: {len(steps)}")
            logger.info("=" * 60)
            
            results = []
            accumulated_content = ""
            
            for i, step in enumerate(steps, 1):
                logger.info(f"\n--- ステップ {i}/{len(steps)} ---")
                
                # ステップタスク構築
                step_task = {
                    **task,  # 親タスクの属性を継承
                    'task_id': f"{task_id}_step{i}",
                    'prompt': step.get('prompt', ''),
                    'description': step.get('description', f'ステップ{i}'),
                }
                
                # 前ステップの結果を参照する場合
                if step.get('use_previous_output') and accumulated_content:
                    step_task['prompt'] = step_task['prompt'].replace(
                        '{previous_output}', 
                        accumulated_content
                    )
                
                # ステップ実行
                step_result = await self.execute_content_task(step_task)
                
                if not step_result.get('success'):
                    logger.error(f"❌ ステップ {i} 失敗")
                    return {
                        'success': False,
                        'error': f"ステップ {i} 失敗: {step_result.get('error')}",
                        'completed_steps': i - 1,
                        'step_results': results
                    }
                
                results.append(step_result)
                accumulated_content = step_result.get('content', '')
                
                logger.info(f"✅ ステップ {i} 完了")
                
                # ステップ間待機
                if i < len(steps):
                    await asyncio.sleep(2)
            
            logger.info(f"✅ 全 {len(steps)} ステップ完了")
            
            return {
                'success': True,
                'content': accumulated_content,
                'steps_completed': len(steps),
                'step_results': results,
                'full_text': accumulated_content,
                'summary': accumulated_content[:500] if len(accumulated_content) > 500 else accumulated_content
            }
        
        except Exception as e:
            logger.error(f"❌ マルチステップタスク {task_id} 実行エラー")
            ErrorHandler.log_error(e, f"ContentTaskExecutor.execute_multi_step_content_task({task_id})")
            return {
                'success': False,
                'error': str(e),
                'step_results': results
            }
    
    def display_suggested_tasks(self, tasks: List[Dict]):
        """
        提案されたタスクを表示
        
        Args:
            tasks: 提案タスクのリスト
        """
        print("\n" + "="*60)
        print("📋 提案されたコンテンツタスク:")
        print("="*60)
        for i, task in enumerate(tasks, 1):
            print(f"\n{i}. {task.get('description', 'N/A')}")
            print(f"   AI: {task.get('ai_site', 'gemini')}")
            print(f"   形式: {task.get('output_format', 'markdown')}")
            print(f"   優先度: {task.get('priority', 'medium')}")
        print("="*60)
    
    async def edit_suggested_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """
        提案タスクを編集
        
        Args:
            tasks: 編集対象のタスクリスト
            
        Returns:
            List[Dict]: 編集後のタスクリスト
        """
        edited_tasks = []
        
        for i, task in enumerate(tasks, 1):
            print(f"\n--- タスク {i}/{len(tasks)} の編集 ---")
            print(f"現在の説明: {task.get('description', 'N/A')}")
            
            edit = input("このタスクを編集しますか? (y/n/s=スキップ): ").lower()
            
            if edit == 's':
                print("このタスクをスキップします")
                continue
            elif edit == 'y':
                new_desc = input("新しい説明 (Enter=変更なし): ")
                if new_desc:
                    task['description'] = new_desc
                
                new_ai = input(f"AI (現在: {task.get('ai_site', 'gemini')}, Enter=変更なし): ")
                if new_ai:
                    task['ai_site'] = new_ai
                
                new_format = input(f"出力形式 (現在: {task.get('output_format', 'markdown')}, Enter=変更なし): ")
                if new_format:
                    task['output_format'] = new_format
            
            edited_tasks.append(task)
        
        return edited_tasks
    
    async def create_manual_tasks(self) -> List[Dict]:
        """
        手動でコンテンツタスクを作成
        
        Returns:
            List[Dict]: 作成されたタスクリスト
        """
        manual_tasks = []
        
        print("\n" + "="*60)
        print("✍️ 手動コンテンツタスク作成")
        print("="*60)
        
        while True:
            print(f"\n--- タスク {len(manual_tasks) + 1} ---")
            
            description = input("タスク説明 (Enter=完了): ")
            if not description:
                break
            
            prompt = input("プロンプト (Enter=説明と同じ): ")
            if not prompt:
                prompt = description
            
            ai_site = input("AI (gemini/deepseek/claude, Enter=gemini): ") or 'gemini'
            output_format = input("出力形式 (markdown/text/html, Enter=markdown): ") or 'markdown'
            priority = input("優先度 (high/medium/low, Enter=medium): ") or 'medium'
            
            task = {
                'description': description,
                'prompt': prompt,
                'ai_site': ai_site,
                'output_format': output_format,
                'priority': priority,
                'required_role': 'content'
            }
            
            manual_tasks.append(task)
            print(f"✅ タスク {len(manual_tasks)} 追加完了")
            
            continue_add = input("\n別のタスクを追加しますか? (y/n): ").lower()
            if continue_add != 'y':
                break
        
        print(f"\n✅ {len(manual_tasks)}件のタスクを作成しました")
        return manual_tasks