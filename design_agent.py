import asyncio
import logging
from pathlib import Path
from typing import Dict
from datetime import datetime

from config_utils import ErrorHandler, PathManager
from browser_controller import BrowserController

logger = logging.getLogger(__name__)

class DesignAgent:
    """設計AI - 要件定義、設計書、アーキテクチャを作成"""
    
    DESIGN_SYSTEM_PROMPT = """あなたは経験豊富なシステム設計者です。

【あなたの役割】
- 要件定義書の作成
- システムアーキテクチャの設計
- データベーススキーマの設計
- API仕様の定義
- 技術選定と理由の説明

【設計の原則】
1. 実装可能性を最優先する
2. セキュリティを考慮する
3. スケーラビリティを意識する
4. 開発者が理解しやすい文書を作成

【出力形式】
タスクの内容に応じて、以下の形式で出力してください：

## タスク概要
（タスクの理解と目的）

## 設計内容
（具体的な設計内容）

## 技術選定
（使用する技術とその理由）

## 実装における注意点
（開発時の注意事項）

## 次のステップ
（このタスク後に行うべきこと）"""

    # design_agent.py の __init__ メソッドを修正

    def __init__(self, browser: BrowserController, output_folder: Path = None):
        self.browser = browser
        # 出力フォルダが指定されていない場合はB14から取得
        if output_folder is None:
            from config_utils import config
            if config.AGENT_OUTPUT_FOLDER:
                self.output_folder = PathManager.get_safe_path(config.AGENT_OUTPUT_FOLDER)
                logger.info(f"Agent出力先（B14から取得）: {self.output_folder}")
            else:
                # フォールバック: デフォルトパス
                self.output_folder = Path(r"C:\Users\color\Documents\gemini_auto_generate\agent_outputs")
                self.output_folder.mkdir(exist_ok=True, parents=True)
                logger.warning(f"B14が空のため、デフォルトフォルダを使用: {self.output_folder}")
        else:
            self.output_folder = output_folder
    
    async def process_task(self, task: Dict) -> Dict:
        """設計タスクを処理"""
        try:
            logger.info(f"設計AI: タスク処理開始 - {task['description']}")
            
            # プロンプトを構築
            full_prompt = f"""{self.DESIGN_SYSTEM_PROMPT}

【タスク】
{task['description']}

上記のタスクについて、詳細な設計を行ってください。
実装可能で具体的な設計書を作成してください。"""
            
            # Geminiに送信
            logger.info("Geminiに設計タスクを送信中...")
            await self.browser.send_prompt(full_prompt)
            
            # 応答待機
            success = await self.browser.wait_for_text_generation(max_wait=180)
            
            if not success:
                return {
                    'success': False,
                    'error': '設計AI: タイムアウト'
                }
            
            # 応答を取得
            response_text = await self.browser.extract_latest_text_response()
            
            if not response_text:
                return {
                    'success': False,
                    'error': '設計AI: 応答取得失敗'
                }
            
            logger.info(f"設計AI: 応答取得完了（{len(response_text)}文字）")
            
            # 結果をファイルに保存
            filename = f"design_{task['task_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            output_path = self.output_folder / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# 設計書: {task['description']}\n\n")
                f.write(f"タスクID: {task['task_id']}\n")
                f.write(f"作成日時: {datetime.now().isoformat()}\n\n")
                f.write("---\n\n")
                f.write(response_text)
            
            logger.info(f"設計書を保存: {output_path}")
            
            # サマリーを作成（最初の500文字）
            summary = response_text[:500] + "..." if len(response_text) > 500 else response_text
            
            return {
                'success': True,
                'output_file': str(output_path),
                'summary': summary,
                'full_text': response_text
            }
            
        except Exception as e:
            ErrorHandler.log_error(e, "設計AI処理")
            return {
                'success': False,
                'error': str(e)
            }