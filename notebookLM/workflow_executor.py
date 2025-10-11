"""
workflow_executor.py - 複雑なワークフロー実行モジュール
マルチステップ・マルチエージェント連携タスクを統合管理
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# 設定
from config_utils import ErrorHandler, config

# データ管理
from sheets_manager import GoogleSheetsManager

# 既存のTaskExecutor
from task_executor import TaskExecutor

logger = logging.getLogger(__name__)


class WorkflowExecutor:
    """
    複雑なワークフロー実行モジュール
    
    複数ステップ、マルチエージェント連携、
    レビュー→修正サイクル、多言語展開などを統合管理
    """
    
    def __init__(
        self,
        task_executor: TaskExecutor,
        sheets_manager: GoogleSheetsManager,
        browser_controller=None
    ):
        """
        初期化
        
        Args:
            task_executor: 既存のTaskExecutorインスタンス
            sheets_manager: GoogleSheetsManagerインスタンス
            browser_controller: BrowserControllerインスタンス(オプション)
        """
        self.task_executor = task_executor
        self.sheets_manager = sheets_manager
        self.browser = browser_controller
        
        # ワークフロー統計
        self.workflow_stats = {
            'total_workflows': 0,
            'completed': 0,
            'failed': 0,
            'partial_success': 0
        }
        
        logger.info("✅ WorkflowExecutor 初期化完了")
    
    async def execute_workflow_task(self, task: Dict) -> Dict:
        """
        ワークフローのメインエントリポイント
        
        Args:
            task: タスク情報辞書
            
        Returns:
            Dict: 実行結果
        """
        task_id = task.get('task_id', 'UNKNOWN')
        workflow_type = self._determine_workflow_type(task)
        
        self.workflow_stats['total_workflows'] += 1
        
        try:
            logger.info("=" * 60)
            logger.info(f"🔄 ワークフロー実行開始: {task_id}")
            logger.info(f"ワークフロータイプ: {workflow_type}")
            logger.info("=" * 60)
            
            result = None
            
            # ワークフロータイプ別実行
            if workflow_type == 'multilingual':
                result = await self._execute_multilingual_workflow(task)
            elif workflow_type == 'review_cycle':
                result = await self._execute_review_cycle_workflow(task)
            elif workflow_type == 'sequential':
                result = await self._execute_sequential_workflow(task)
            elif workflow_type == 'parallel':
                result = await self._execute_parallel_workflow(task)
            elif workflow_type == 'conditional':
                result = await self._execute_conditional_workflow(task)
            else:
                # デフォルトシーケンシャル実行
                result = await self._execute_sequential_workflow(task)
            
            # 統計更新
            if result and result.get('success'):
                self.workflow_stats['completed'] += 1
            elif result and result.get('partial_success'):
                self.workflow_stats['partial_success'] += 1
            else:
                self.workflow_stats['failed'] += 1
            
            return result
        
        except Exception as e:
            logger.error(f"❌ ワークフロー {task_id} 実行エラー")
            ErrorHandler.log_error(e, f"WorkflowExecutor.execute_workflow_task({task_id})")
            self.workflow_stats['failed'] += 1
            return {
                'success': False,
                'error': str(e)
            }
    
    def _determine_workflow_type(self, task: Dict) -> str:
        """
        ワークフロータイプを判定
        
        Args:
            task: タスク情報辞書
            
        Returns:
            str: ワークフロータイプ
        """
        description = task.get('description', '').lower()
        
        # 多言語ワークフロー
        if any(kw in description for kw in ['多言語', '翻訳', 'multilingual', 'translation']):
            return 'multilingual'
        
        # レビューサイクルワークフロー
        if any(kw in description for kw in ['レビュー→修正', 'review cycle', 'iterative review']):
            return 'review_cycle'
        
        # 並列ワークフロー
        if any(kw in description for kw in ['並列', '同時', 'parallel', 'concurrent']):
            return 'parallel'
        
        # 条件分岐ワークフロー
        if any(kw in description for kw in ['条件', '分岐', 'conditional', 'if-then']):
            return 'conditional'
        
        # デフォルトはシーケンシャル
        return 'sequential'
    
    async def _execute_multilingual_workflow(self, task: Dict) -> Dict:
        """
        多言語コンテンツ生成ワークフロー（Polylang連携強化版）
            
        1. 日本語記事生成
        2. 英語翻訳
        3. その他言語翻訳（オプション）
        4. WordPress多言語投稿（Polylang連携）
            
        Args:
            task: タスク情報辞書
                
        Returns:
            Dict: 実行結果
        """
        task_id = task.get('task_id', 'UNKNOWN')
            
        try:
            logger.info("🌍 多言語ワークフロー実行（Polylang連携版）")
                
            # ターゲット言語リスト
            target_languages = task.get('target_languages', ['ja', 'en'])
            base_language = task.get('base_language', 'ja')
                
            # Polylang言語コードマッピング
            polylang_lang_codes = {
                'ja': 'ja',
                'en': 'en',
                'uz': 'uz_UZ',  # ウズベク語
                'ru': 'ru_RU',  # ロシア語
                'tr': 'tr_TR',  # トルコ語
                'zh': 'zh_CN',  # 中国語
                'ko': 'ko_KR'   # 韓国語
            }
                
            results = {}
            contents = {}
            post_ids = {}  # 投稿IDを保存（Polylang連携用）
                
            # ========================================
            # ステップ1: 基本言語でコンテンツ生成
            # ========================================
            logger.info(f"--- ステップ1: {base_language} コンテンツ生成 ---")
                
            base_task = {
                **task,
                'task_id': f"{task_id}_base_{base_language}",
                'language': base_language,
                'required_role': 'content'
            }
                
            base_result = await self.task_executor.execute_task(base_task)
                
            if not base_result:
                return {
                    'success': False,
                    'error': f'{base_language} コンテンツ生成失敗'
                }
                
            results[base_language] = base_result
                
            # 基本コンテンツ取得
            base_content = ""
            if hasattr(base_result, 'get'):
                base_content = base_result.get('full_text', base_result.get('content', ''))
                
            contents[base_language] = base_content
                
            # ========================================
            # ステップ2: 他言語への翻訳
            # ========================================
            for lang in target_languages:
                if lang == base_language:
                    continue
                    
                logger.info(f"--- ステップ2-{lang}: {lang} 翻訳 ---")
                    
                translation_task = {
                    'task_id': f"{task_id}_translate_{lang}",
                    'description': f'{base_language}から{lang}に翻訳',
                    'prompt': f'以下のコンテンツを{lang}に翻訳してください:\n\n{base_content}',
                    'required_role': 'content',
                    'language': lang,
                    'source_language': base_language,
                    'target_language': lang,
                    'source_text': base_content
                }
                    
                translate_result = await self.task_executor.execute_task(translation_task)
                    
                results[lang] = translate_result
                    
                if translate_result and hasattr(translate_result, 'get'):
                    translated_content = translate_result.get('full_text', translate_result.get('content', ''))
                    contents[lang] = translated_content
                else:
                    logger.warning(f"⚠️ {lang} 翻訳失敗")
                    
                await asyncio.sleep(2)
                
            # ========================================
            # ステップ3: WordPress多言語投稿（Polylang連携強化版）
            # ========================================
            if task.get('auto_publish', False):
                logger.info("--- ステップ3: WordPress多言語投稿（Polylang連携） ---")
                    
                # 3-1: 基本言語の投稿を作成
                base_lang_code = polylang_lang_codes.get(base_language, base_language)
                base_wp_task = {
                    'task_id': f"{task_id}_publish_{base_language}",
                    'description': f'{base_language} コンテンツをWordPressに投稿',
                    'required_role': 'wordpress',
                    'language': base_language,
                    'polylang_lang': base_lang_code,
                    'post_action': 'create',
                    'post_title': task.get('post_title', f'記事_{base_language}'),
                    'post_content': contents.get(base_language, ''),
                    'post_status': 'draft'  # 下書きで作成
                }
                    
                base_publish_result = await self.task_executor.execute_task(base_wp_task)
                results[f'{base_language}_publish'] = base_publish_result
                    
                # 投稿IDを取得
                if base_publish_result and hasattr(base_publish_result, 'get'):
                    base_post_id = base_publish_result.get('post_id')
                    if base_post_id:
                        post_ids[base_language] = base_post_id
                        logger.info(f"✅ {base_language} 投稿ID: {base_post_id}")
                    
                await asyncio.sleep(2)
                    
                # 3-2: 翻訳投稿を作成し、Polylangで連携
                for lang, content in contents.items():
                    if lang == base_language or not content:
                        continue
                        
                    lang_code = polylang_lang_codes.get(lang, lang)
                        
                    wp_task = {
                        'task_id': f"{task_id}_publish_{lang}",
                        'description': f'{lang} コンテンツをWordPressに投稿（Polylang連携）',
                        'required_role': 'wordpress',
                        'language': lang,
                        'polylang_lang': lang_code,
                        'post_action': 'create',
                        'post_title': task.get('post_title', f'記事_{lang}'),
                        'post_content': content,
                        'post_status': 'draft',
                        # ========================================
                        # 🆕 Polylang連携パラメータ（新規追加）
                        # ========================================
                        'polylang_link_to': post_ids.get(base_language),  # 基本言語の投稿IDとリンク
                        'polylang_translation_group': task_id  # 翻訳グループID
                    }
                        
                    publish_result = await self.task_executor.execute_task(wp_task)
                    results[f'{lang}_publish'] = publish_result
                        
                    # 投稿IDを取得
                    if publish_result and hasattr(publish_result, 'get'):
                        post_id = publish_result.get('post_id')
                        if post_id:
                            post_ids[lang] = post_id
                            logger.info(f"✅ {lang} 投稿ID: {post_id}")
                        
                    await asyncio.sleep(2)
                    
                # ========================================
                # 🆕 ステップ3-3: Polylang翻訳リンクの設定（新規追加）
                # ========================================
                if len(post_ids) > 1:
                    logger.info("--- ステップ3-3: Polylang翻訳リンク設定 ---")
                        
                    polylang_link_task = {
                        'task_id': f"{task_id}_polylang_link",
                        'description': 'Polylang翻訳リンクを設定',
                        'required_role': 'wordpress',
                        'action': 'polylang_link_translations',
                        'post_ids': post_ids,  # {'ja': 123, 'en': 124, ...}
                        'translation_group': task_id
                    }
                        
                    link_result = await self.task_executor.execute_task(polylang_link_task)
                    results['polylang_link'] = link_result
                        
                    if link_result and hasattr(link_result, 'get') and link_result.get('success'):
                        logger.info("✅ Polylang翻訳リンク設定完了")
                    else:
                        logger.warning("⚠️ Polylang翻訳リンク設定失敗（手動で設定が必要）")
                
            # ========================================
            # 結果集約
            # ========================================
            success_count = sum(1 for r in results.values() if r and (r is True or (hasattr(r, 'get') and r.get('success'))))
            total_count = len(results)
                
            logger.info(f"✅ 多言語ワークフロー完了: {success_count}/{total_count} 成功")
                
            return {
                'success': success_count == total_count,
                'partial_success': success_count > 0 and success_count < total_count,
                'results': results,
                'contents': contents,
                'post_ids': post_ids,  # 投稿ID情報を追加
                'summary': f'{success_count}/{total_count} 言語で成功（投稿数: {len(post_ids)}）',
                'full_text': '\n\n---\n\n'.join([f'[{lang}]\n{content}' for lang, content in contents.items()])
            }
            
        except Exception as e:
            logger.error(f"❌ 多言語ワークフローエラー: {e}")
            ErrorHandler.log_error(e, "WorkflowExecutor._execute_multilingual_workflow")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute_review_cycle_workflow(self, task: Dict) -> Dict:
        """
        レビュー→修正サイクルワークフロー
        
        1. コンテンツ生成
        2. レビュー実行
        3. 修正指示に基づいて再生成
        4. 最終承認まで繰り返し
        
        Args:
            task: タスク情報辞書
            
        Returns:
            Dict: 実行結果
        """
        task_id = task.get('task_id', 'UNKNOWN')
        max_iterations = task.get('max_review_iterations', 3)
        
        try:
            logger.info("🔄 レビューサイクルワークフロー実行")
            
            iteration = 0
            current_content = None
            review_history = []
            
            while iteration < max_iterations:
                iteration += 1
                logger.info(f"--- レビューサイクル {iteration}/{max_iterations} ---")
                
                # ステップ1: コンテンツ生成（初回）または修正（2回目以降）
                if iteration == 1:
                    logger.info("初回コンテンツ生成")
                    content_task = {
                        **task,
                        'task_id': f"{task_id}_content_v{iteration}",
                        'required_role': 'content'
                    }
                else:
                    logger.info("レビューフィードバックに基づく修正")
                    last_review = review_history[-1]
                    feedback = last_review.get('feedback', '')
                    
                    content_task = {
                        **task,
                        'task_id': f"{task_id}_content_v{iteration}",
                        'prompt': f'{task.get("prompt", "")}\n\n前回のレビューフィードバック:\n{feedback}\n\n上記フィードバックを反映して修正してください。',
                        'required_role': 'content'
                    }
                
                content_result = await self.task_executor.execute_task(content_task)
                
                if not content_result:
                    logger.error("コンテンツ生成失敗")
                    break
                
                if hasattr(content_result, 'get'):
                    current_content = content_result.get('full_text', content_result.get('content', ''))
                else:
                    current_content = str(content_result)
                
                # ステップ2: レビュー実行
                logger.info("レビュー実行")
                review_task = {
                    'task_id': f"{task_id}_review_v{iteration}",
                    'description': 'コンテンツレビュー',
                    'required_role': 'review',
                    'review_target_task_id': f"{task_id}_content_v{iteration}",
                    'content_to_review': current_content
                }
                
                review_result = await self.task_executor.execute_task(review_task)
                
                if not review_result or not hasattr(review_result, 'get'):
                    logger.warning("レビュー実行失敗 - サイクル終了")
                    break
                
                review_history.append(review_result)
                
                # ステップ3: 承認判定
                approved = review_result.get('approved', False)
                
                if approved:
                    logger.info(f"✅ レビュー承認 (反復{iteration}回)")
                    return {
                        'success': True,
                        'content': current_content,
                        'iterations': iteration,
                        'review_history': review_history,
                        'full_text': current_content,
                        'summary': f'{iteration}回の反復で承認'
                    }
                else:
                    logger.info(f"🔄 修正が必要 - 次の反復へ")
                    await asyncio.sleep(2)
            
            # 最大反復回数到達
            logger.warning(f"⚠️ 最大反復回数({max_iterations})到達 - 最終版を返却")
            
            return {
                'success': False,
                'partial_success': True,
                'content': current_content,
                'iterations': iteration,
                'review_history': review_history,
                'full_text': current_content,
                'summary': f'{iteration}回反復したが承認されず',
                'error': '最大反復回数到達'
            }
        
        except Exception as e:
            logger.error(f"❌ レビューサイクルワークフローエラー: {e}")
            ErrorHandler.log_error(e, "WorkflowExecutor._execute_review_cycle_workflow")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute_sequential_workflow(self, task: Dict) -> Dict:
        """
        シーケンシャルワークフロー（順次実行）
        
        Args:
            task: タスク情報辞書
            
        Returns:
            Dict: 実行結果
        """
        task_id = task.get('task_id', 'UNKNOWN')
        steps = task.get('steps', [])
        
        if not steps:
            logger.warning("ステップ定義なし - 単一タスクとして実行")
            result = await self.task_executor.execute_task(task)
            return {'success': bool(result), 'result': result}
        
        try:
            logger.info(f"📋 シーケンシャルワークフロー実行 ({len(steps)}ステップ)")
            
            results = []
            accumulated_output = {}
            
            for i, step in enumerate(steps, 1):
                logger.info(f"--- ステップ {i}/{len(steps)}: {step.get('description', 'N/A')} ---")
                
                # ステップタスク構築
                step_task = {
                    **task,
                    **step,  # ステップ設定で上書き
                    'task_id': f"{task_id}_step{i}",
                }
                
                # 前ステップの出力を参照
                if step.get('use_previous_output') and accumulated_output:
                    prev_output = accumulated_output.get(f'step{i-1}', '')
                    if 'prompt' in step_task:
                        step_task['prompt'] = step_task['prompt'].replace(
                            '{previous_output}',
                            str(prev_output)
                        )
                
                # ステップ実行
                step_result = await self.task_executor.execute_task(step_task)
                
                results.append(step_result)
                accumulated_output[f'step{i}'] = step_result
                
                # 失敗時の処理
                if not step_result or (hasattr(step_result, 'get') and not step_result.get('success')):
                    if step.get('continue_on_failure', False):
                        logger.warning(f"⚠️ ステップ {i} 失敗したが継続")
                    else:
                        logger.error(f"❌ ステップ {i} 失敗 - ワークフロー中断")
                        return {
                            'success': False,
                            'error': f'ステップ {i} 失敗',
                            'completed_steps': i - 1,
                            'results': results
                        }
                
                logger.info(f"✅ ステップ {i} 完了")
                await asyncio.sleep(1)
            
            logger.info(f"✅ 全 {len(steps)} ステップ完了")
            
            return {
                'success': True,
                'steps_completed': len(steps),
                'results': results,
                'accumulated_output': accumulated_output,
                'full_text': str(accumulated_output)
            }
        
        except Exception as e:
            logger.error(f"❌ シーケンシャルワークフローエラー: {e}")
            ErrorHandler.log_error(e, "WorkflowExecutor._execute_sequential_workflow")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute_parallel_workflow(self, task: Dict) -> Dict:
        """
        並列ワークフロー（複数タスク同時実行）
        
        Args:
            task: タスク情報辞書
            
        Returns:
            Dict: 実行結果
        """
        task_id = task.get('task_id', 'UNKNOWN')
        parallel_tasks = task.get('parallel_tasks', [])
        
        if not parallel_tasks:
            logger.warning("並列タスク定義なし")
            return {'success': False, 'error': '並列タスクが定義されていません'}
        
        try:
            logger.info(f"⚡ 並列ワークフロー実行 ({len(parallel_tasks)}タスク)")
            
            # 並列タスクリスト構築
            coroutines = []
            for i, parallel_task in enumerate(parallel_tasks, 1):
                parallel_task_config = {
                    **task,
                    **parallel_task,
                    'task_id': f"{task_id}_parallel{i}"
                }
                coroutines.append(
                    self.task_executor.execute_task(parallel_task_config)
                )
            
            # 並列実行
            results = await asyncio.gather(*coroutines, return_exceptions=True)
            
            # 結果分析
            success_count = sum(
                1 for r in results 
                if r and not isinstance(r, Exception) and (r is True or (hasattr(r, 'get') and r.get('success')))
            )
            
            logger.info(f"✅ 並列ワークフロー完了: {success_count}/{len(results)} 成功")
            
            return {
                'success': success_count == len(results),
                'partial_success': success_count > 0 and success_count < len(results),
                'results': results,
                'summary': f'{success_count}/{len(results)} タスク成功'
            }
        
        except Exception as e:
            logger.error(f"❌ 並列ワークフローエラー: {e}")
            ErrorHandler.log_error(e, "WorkflowExecutor._execute_parallel_workflow")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute_conditional_workflow(self, task: Dict) -> Dict:
        """
        条件分岐ワークフロー
        
        Args:
            task: タスク情報辞書
            
        Returns:
            Dict: 実行結果
        """
        task_id = task.get('task_id', 'UNKNOWN')
        
        try:
            logger.info("🔀 条件分岐ワークフロー実行")
            
            # 条件評価タスク実行
            condition_task = task.get('condition_task')
            if not condition_task:
                return {'success': False, 'error': '条件タスクが定義されていません'}
            
            condition_result = await self.task_executor.execute_task(condition_task)
            
            # 条件評価
            condition_met = self._evaluate_condition(condition_result, task.get('condition'))
            
            # 分岐実行
            if condition_met:
                logger.info("✅ 条件成立 - then分岐実行")
                then_task = task.get('then_task')
                if then_task:
                    result = await self.task_executor.execute_task(then_task)
                    return {'success': True, 'branch': 'then', 'result': result}
            else:
                logger.info("❌ 条件不成立 - else分岐実行")
                else_task = task.get('else_task')
                if else_task:
                    result = await self.task_executor.execute_task(else_task)
                    return {'success': True, 'branch': 'else', 'result': result}
            
            return {'success': True, 'branch': 'none'}
        
        except Exception as e:
            logger.error(f"❌ 条件分岐ワークフローエラー: {e}")
            ErrorHandler.log_error(e, "WorkflowExecutor._execute_conditional_workflow")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _evaluate_condition(self, result: Any, condition: Dict) -> bool:
        """
        条件を評価
        
        Args:
            result: 評価対象の結果
            condition: 条件定義辞書
            
        Returns:
            bool: 条件成立フラグ
        """
        if not condition:
            return True
        
        condition_type = condition.get('type', 'success')
        
        if condition_type == 'success':
            return result and (result is True or (hasattr(result, 'get') and result.get('success')))
        elif condition_type == 'contains':
            target_text = condition.get('text', '')
            if hasattr(result, 'get'):
                content = result.get('full_text', result.get('content', ''))
                return target_text.lower() in content.lower()
        elif condition_type == 'length':
            min_length = condition.get('min_length', 0)
            if hasattr(result, 'get'):
                content = result.get('full_text', result.get('content', ''))
                return len(content) >= min_length
        
        return False
    
    def get_workflow_stats(self) -> Dict:
        """ワークフロー統計情報を取得"""
        return self.workflow_stats.copy()