"""
WordPressカスタム投稿タイプ作成エージェント
"""

import asyncio
import logging
from typing import Dict
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class WordPressCPTAgent:
    """カスタム投稿タイプ作成専門エージェント"""
    
    PROMPT_TEMPLATE = """あなたはWordPress開発の専門家です。

【タスク】
以下の仕様でカスタム投稿タイプを作成するPHPコードを生成してください：

{cpt_spec}

【出力要件】
1. 完全に動作するPHPコード
2. register_post_type() を使用
3. 多言語対応（Polylang互換）
4. エラーハンドリング付き
5. コメント付き

【出力形式】
```php
<?php
/**
 * カスタム投稿タイプ: {cpt_name}
 * 作成日: {date}
 */

function register_cpt_{cpt_slug}() {{
    // コード実装
}}
add_action('init', 'register_cpt_{cpt_slug}', 0);
完全なPHPコードを出力してください。
"""
    def __init__(self, browser, output_folder: Path):
        self.browser = browser
        self.output_folder = output_folder

    async def execute(self, task: Dict) -> Dict:
        """CPT作成タスクを実行"""
        task_id = task.get('task_id', 'UNKNOWN')
        description = task.get('description', '')
        
        try:
            logger.info("🔧 カスタム投稿タイプ作成開始")
            
            # CPT仕様を抽出
            cpt_spec = self._extract_cpt_spec(description)
            
            # プロンプト構築
            prompt = self.PROMPT_TEMPLATE.format(
                cpt_spec=cpt_spec,
                cpt_name=cpt_spec.get('name', 'N/A'),
                cpt_slug=cpt_spec.get('slug', 'custom_post'),
                date=datetime.now().strftime('%Y-%m-%d')
            )
            
            # プロンプト送信
            await self.browser.send_prompt(prompt)
            
            # 応答待機
            success = await self.browser.wait_for_text_generation(max_wait=180)
            
            if not success:
                return {'success': False, 'error': 'タイムアウト'}
            
            # 応答取得
            response_text = await self.browser.extract_latest_text_response()
            
            # PHP保存
            output_file = await self._save_php_code(response_text, cpt_spec['slug'], task_id)
            
            return {
                'success': True,
                'message': f'CPT作成完了: {cpt_spec["slug"]}',
                'output_file': str(output_file),
                'cpt_slug': cpt_spec['slug'],
                'task_id': task_id
            }
            
        except Exception as e:
            logger.error(f"❌ CPT作成エラー: {e}")
            return {'success': False, 'error': str(e), 'task_id': task_id}

    def _extract_cpt_spec(self, description: str) -> Dict:
        """説明からCPT仕様を抽出"""
        # M&A案件の場合
        if 'ma_case' in description.lower() or 'm&a案件' in description:
            return {
                'slug': 'ma_case',
                'name': 'M&A案件',
                'singular': 'M&A案件',
                'plural': 'M&A案件一覧'
            }
        
        # デフォルト
        return {
            'slug': 'custom_post',
            'name': 'カスタム投稿',
            'singular': 'カスタム投稿',
            'plural': 'カスタム投稿一覧'
        }

    async def _save_php_code(self, code: str, slug: str, task_id: str) -> Path:
        """PHPコードを保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"cpt_{slug}_{task_id}_{timestamp}.php"
        output_path = self.output_folder / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        logger.info(f"✅ PHP保存: {filename}")
        return output_path

#### 3-3. `wordpress/wp_dev/wp_taxonomy_agent.py`
"""
WordPressタクソノミー作成エージェント
"""

import logging
from typing import Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class WordPressTaxonomyAgent:
    """タクソノミー作成専門エージェント"""
    
    def __init__(self, browser, output_folder: Path):
        self.browser = browser
        self.output_folder = output_folder
    
    async def execute(self, task: Dict) -> Dict:
        """タクソノミー作成タスクを実行"""
        # 実装（wp_cpt_agent.py と同様のパターン）
        return {
            'success': True,
            'message': 'タクソノミー作成完了（実装中）',
            'task_id': task.get('task_id')
        }