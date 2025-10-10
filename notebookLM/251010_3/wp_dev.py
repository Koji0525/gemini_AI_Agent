"""
WordPress開発タスクルーター
各専門エージェントへタスクを振り分ける
"""

import asyncio
import logging
from typing import Dict, Optional
from pathlib import Path

from config_utils import ErrorHandler

logger = logging.getLogger(__name__)


class WordPressDevAgent:
    """
    WordPress開発タスクのメインルーター
    タスク内容に応じて専門エージェントに振り分ける
    """
    
    def __init__(self, browser, output_folder: Path = None):
        self.browser = browser
        self.output_folder = output_folder or Path('./outputs/wordpress')
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        # 専門エージェントの初期化
        self._init_specialized_agents()
        
        logger.info("✅ WordPressDevAgent 初期化完了")
    
    def _init_specialized_agents(self):
        """専門エージェントを初期化"""
        try:
            from wordpress.wp_dev import (
                WordPressRequirementsAgent,
                WordPressCPTAgent,
                WordPressTaxonomyAgent,
                WordPressACFAgent
            )
            
            self.requirements_agent = WordPressRequirementsAgent(
                self.browser, 
                self.output_folder
            )
            self.cpt_agent = WordPressCPTAgent(
                self.browser,
                self.output_folder
            )
            self.taxonomy_agent = WordPressTaxonomyAgent(
                self.browser,
                self.output_folder
            )
            self.acf_agent = WordPressACFAgent(
                self.browser,
                self.output_folder
            )
            
            logger.info("✅ 全専門エージェント初期化完了")
            
        except ImportError as e:
            logger.error(f"❌ 専門エージェントのインポート失敗: {e}")
            self.requirements_agent = None
            self.cpt_agent = None
            self.taxonomy_agent = None
            self.acf_agent = None
    
    async def execute(self, task: Dict) -> Dict:
        """
        タスクを適切な専門エージェントに振り分けて実行
        
        Args:
            task: タスク情報辞書
            
        Returns:
            Dict: 実行結果
        """
        task_id = task.get('task_id', 'UNKNOWN')
        description = task.get('description', '').lower()
        
        try:
            logger.info(f"🔧 WordPress開発タスク実行: {task_id}")
            logger.info(f"説明: {description}")
            
            # タスクタイプを判定
            task_type = self._determine_task_type(description)
            logger.info(f"タスクタイプ: {task_type}")
            
            # 適切なエージェントに振り分け
            if task_type == 'requirements':
                if not self.requirements_agent:
                    return self._agent_not_available('WordPressRequirementsAgent')
                return await self.requirements_agent.execute(task)
            
            elif task_type == 'cpt':
                if not self.cpt_agent:
                    return self._agent_not_available('WordPressCPTAgent')
                return await self.cpt_agent.execute(task)
            
            elif task_type == 'taxonomy':
                if not self.taxonomy_agent:
                    return self._agent_not_available('WordPressTaxonomyAgent')
                return await self.taxonomy_agent.execute(task)
            
            elif task_type == 'acf':
                if not self.acf_agent:
                    return self._agent_not_available('WordPressACFAgent')
                return await self.acf_agent.execute(task)
            
            else:
                return {
                    'success': False,
                    'error': f'未対応のタスクタイプ: {task_type}',
                    'task_id': task_id
                }
        
        except Exception as e:
            logger.error(f"❌ WordPress開発タスクエラー: {e}")
            ErrorHandler.log_error(e, f"WordPressDevAgent.execute({task_id})")
            return {
                'success': False,
                'error': str(e),
                'task_id': task_id
            }
    
    def _determine_task_type(self, description: str) -> str:
        """タスクタイプを判定"""
        # 要件定義
        if any(kw in description for kw in [
            '要件定義', 'requirements', '仕様書', '設計書',
            'ポータルサイト', 'cocoon', 'polylang'
        ]):
            return 'requirements'
        
        # カスタム投稿タイプ
        if any(kw in description for kw in [
            'custom post type', 'cpt', 'カスタム投稿',
            'ma_case', '投稿タイプ作成'
        ]):
            return 'cpt'
        
        # タクソノミー
        if any(kw in description for kw in [
            'タクソノミー', 'taxonomy', 'カテゴリ作成',
            'industry_category', 'タグ'
        ]):
            return 'taxonomy'
        
        # ACF
        if any(kw in description for kw in [
            'acf', 'advanced custom fields', 'カスタムフィールド',
            'フィールドグループ', 'フィールド設計'
        ]):
            return 'acf'
        
        return 'unknown'
    
    def _agent_not_available(self, agent_name: str) -> Dict:
        """エージェント利用不可エラー"""
        return {
            'success': False,
            'error': f'{agent_name} が利用できません。wordpress/wp_dev/ を確認してください。'
        }