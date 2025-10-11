"""
WordPress ACF設計・設定エージェント
"""

import logging
from typing import Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class WordPressACFAgent:
    """ACF設計・設定専門エージェント"""
    
    def __init__(self, browser, output_folder: Path):
        self.browser = browser
        self.output_folder = output_folder
    
    async def execute(self, task: Dict) -> Dict:
        """ACFタスクを実行"""
        # 実装（wp_cpt_agent.py と同様のパターン）
        return {
            'success': True,
            'message': 'ACF設定完了（実装中）',
            'task_id': task.get('task_id')
        }
        
"""
専門エージェントの修正パターン例
（wp_acf_agent.py, wp_cpt_agent.py などに適用）

❌ エラーが発生するパターン（修正前）
✅ 安全なパターン（修正後）
"""

# ========================================
# ❌ エラーパターン1: 条件分岐外での変数参照
# ========================================

# --- 修正前（エラーが発生） ---
async def save_generated_code_BAD_EXAMPLE(self, task_id: str, content: str, output_type: str):
    """❌ このパターンはエラーが発生します"""
    
    # 条件分岐内でのみ変数を定義
    if output_type == 'php':
        php_filename = f"template_{task_id}.php"
    elif output_type == 'json':
        json_filename = f"acf_{task_id}.json"
    
    # ここで変数を参照すると、条件に合致しなかった場合にエラー！
    # UnboundLocalError: cannot access local variable 'php_filename' where it is not associated with a value
    await self.browser.save_text_to_file(content, php_filename)  # ❌ エラー発生箇所


# --- 修正後（安全） ---
async def save_generated_code_GOOD_EXAMPLE(self, task_id: str, content: str, output_type: str):
    """✅ このパターンは安全です"""
    
    # === 方法1: 最初に変数を初期化 ===
    final_filename = None  # 最初に初期化（重要！）
    
    if output_type == 'php':
        final_filename = f"template_{task_id}.php"
    elif output_type == 'json':
        final_filename = f"acf_{task_id}.json"
    else:
        # デフォルト値を設定（どの条件にも合致しない場合）
        final_filename = f"output_{task_id}.txt"
    
    # 安全に参照可能
    if final_filename:
        await self.browser.save_text_to_file(content, final_filename)
    else:
        logger.error("❌ ファイル名が決定できませんでした")


# ========================================
# ❌ エラーパターン2: 複雑な条件分岐
# ========================================

# --- 修正前（エラーリスク高） ---
async def process_and_save_BAD(self, task: dict, generated_content: str):
    """❌ 複雑な条件でエラーリスクが高い"""
    
    task_type = task.get('type')
    
    if task_type == 'cpt' and 'ma_case' in task.get('description', ''):
        output_filename = 'ma_case_template.php'
    elif task_type == 'acf' and 'json' in task.get('format', ''):
        output_filename = 'acf_fields.json'
    
    # 上記の条件に合致しない場合、output_filenameが未定義！
    save_result = await self._save_file(output_filename, generated_content)  # ❌ エラー


# --- 修正後（安全） ---
async def process_and_save_GOOD(self, task: dict, generated_content: str):
    """✅ デフォルト値で安全に処理"""
    
    task_type = task.get('type')
    task_id = task.get('task_id', 'unknown')
    
    # === デフォルト値を最初に設定 ===
    output_filename = f"output_{task_id}.txt"  # デフォルト
    
    if task_type == 'cpt' and 'ma_case' in task.get('description', ''):
        output_filename = f"ma_case_template_{task_id}.php"
    elif task_type == 'acf' and 'json' in task.get('format', ''):
        output_filename = f"acf_fields_{task_id}.json"
    
    # 常にoutput_filenameが定義されているので安全
    save_result = await self._save_file(output_filename, generated_content)  # ✅ 安全


# ========================================
# ✅ 推奨パターン: 親クラスのヘルパーメソッド使用
# ========================================

class WordPressACFAgent:
    """ACF設計エージェント（修正例）"""
    
    def __init__(self, browser, output_folder, parent_agent=None):
        self.browser = browser
        self.output_folder = output_folder
        self.parent_agent = parent_agent  # 親のWordPressDevAgentへの参照
    
    async def execute(self, task: dict):
        """タスク実行"""
        task_id = task.get('task_id', 'unknown')
        
        try:
            # AIでコンテンツ生成
            generated_content = await self._generate_acf_fields(task)
            
            # === 推奨: 親エージェントの安全なヘルパーを使用 ===
            if self.parent_agent and hasattr(self.parent_agent, 'safe_save_code_file'):
                save_result = await self.parent_agent.safe_save_code_file(
                    content=generated_content,
                    task_id=task_id,
                    file_type='json',  # or 'php'
                    custom_filename=None  # 自動生成
                )
                
                if save_result['success']:
                    logger.info(f"✅ 保存成功: {save_result['filepath']}")
                    return {
                        'success': True,
                        'output_file': save_result['filepath']
                    }
                else:
                    logger.error(f"❌ 保存失敗: {save_result['error']}")
                    return {
                        'success': False,
                        'error': save_result['error']
                    }
            else:
                # === フォールバック: 自前で安全に処理 ===
                return await self._safe_save_fallback(task_id, generated_content)
        
        except Exception as e:
            logger.error(f"❌ 実行エラー: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _safe_save_fallback(self, task_id: str, content: str):
        """安全なフォールバック保存"""
        # 変数を最初に初期化
        filename = None
        saved_path = None
        
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # ファイル名決定
            filename = f"acf_output_{task_id}_{timestamp}.json"
            output_path = self.output_folder / filename
            
            # 保存実行
            if hasattr(self.browser, 'save_text_to_file'):
                saved_path = await self.browser.save_text_to_file(
                    content,
                    str(output_path)
                )
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                saved_path = str(output_path)
            
            return {
                'success': True,
                'output_file': saved_path
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"保存エラー: {e}"
            }


# ========================================
# 🔧 実際の修正手順（各専門エージェントファイルで実行）
# ========================================

"""
1. wordpress/wp_dev/__init__.py を確認し、親エージェントの参照を渡す:

   from .wp_acf_agent import WordPressACFAgent
   
   # 初期化時に親エージェントを渡す
   def create_agents(browser, output_folder, parent):
       acf_agent = WordPressACFAgent(
           browser, 
           output_folder,
           parent_agent=parent  # 追加
       )
       return acf_agent

2. 各専門エージェント（wp_acf_agent.py など）内のファイル保存ロジックを探す:
   
   検索キーワード:
   - "filename" + "if" または "elif"
   - "save" + "file"
   - ".php" または ".json"

3. 上記のパターンに従って修正:
   
   修正前:
   ```python
   if condition:
       php_filename = "something.php"
   
   await save(php_filename)  # ❌ エラー
   ```
   
   修正後:
   ```python
   php_filename = None  # 最初に初期化
   
   if condition:
       php_filename = "something.php"
   else:
       php_filename = "default.txt"  # デフォルト値
   
   if php_filename:
       await save(php_filename)  # ✅ 安全
   ```

4. または、親のヘルパーメソッドを使用:
   
   ```python
   result = await self.parent_agent.safe_save_code_file(
       content=generated_code,
       task_id=task_id,
       file_type='php'
   )
   ```
"""