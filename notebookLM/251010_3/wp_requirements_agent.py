"""
WordPress要件定義書作成エージェント
"""

import asyncio
import logging
from typing import Dict
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class WordPressRequirementsAgent:
    """WordPress要件定義書作成専門エージェント"""
    
    PROMPT_TEMPLATE = """あなたはWordPress開発の専門家で、要件定義のプロフェッショナルです。

【あなたの役割】
ウズベキスタンのM&Aポータルサイトの要件定義書を作成してください。

【プロジェクト情報】
- **サイト名**: ウズベキスタンM&Aポータル
- **目的**: M&A案件情報の多言語発信と企業マッチング
- **WordPressテーマ**: Cocoon（日本製の無料高機能テーマ）
- **多言語プラグイン**: Polylang
- **対応言語**: 日本語、英語、ロシア語、ウズベク語、中国語、韓国語、トルコ語（7言語）

【要件定義書の構成】
必ず以下の構造で出力してください：

# 1.0 プロジェクト概要
## 1.1 プロジェクト名
## 1.2 目的・背景
## 1.3 対象ユーザー
## 1.4 成功指標（KPI）

# 2.0 システム構成
## 2.1 技術スタック
## 2.2 サーバー要件
## 2.3 開発・本番環境

# 3.0 機能要件
## 3.1 カスタム投稿タイプ
### 3.1.1 M&A案件（ma_case）
### 3.1.2 企業情報（company）
### 3.1.3 ニュース（news）

## 3.2 カスタムタクソノミー
### 3.2.1 業種分類（industry）
### 3.2.2 地域（region）
### 3.2.3 案件タイプ（deal_type）

## 3.3 ACFカスタムフィールド
### M&A案件用フィールド

## 3.4 検索・フィルター機能

## 3.5 多言語機能（Polylang）

## 3.6 ユーザー管理・権限

## 3.7 問い合わせ機能

## 3.8 SEO対策

## 3.9 セキュリティ

## 3.10 パフォーマンス最適化

# 4.0 非機能要件

# 5.0 画面設計

# 6.0 データ構造

# 7.0 実装計画

# 8.0 運用保守

# 9.0 コスト見積もり

# 10.0 リスクと対策

【出力形式】
- 上記の構成に従って、**完全で詳細な要件定義書**を生成してください。
- すべてのセクションを埋めること
- 具体的な仕様を記載すること
- JSONデータ構造を含めること
- 実装可能なレベルの詳細度で記述すること

【重要】
- 出力は20,000文字以上の詳細な要件定義書にすること
- コードブロックは完全に閉じること（```で開始・終了）
- すべての章立てを網羅すること
- Cocoonテーマの機能を最大限活用すること
- Polylangの多言語対応を徹底すること
"""
    
    def __init__(self, browser, output_folder: Path):
        self.browser = browser
        self.output_folder = output_folder
    
    async def execute(self, task: Dict) -> Dict:
        """要件定義書作成タスクを実行"""
        task_id = task.get('task_id', 'UNKNOWN')
        
        try:
            logger.info("=" * 60)
            logger.info("📋 WordPress要件定義書作成開始")
            logger.info("=" * 60)
            
            # プロンプト送信
            await self.browser.send_prompt(self.PROMPT_TEMPLATE)
            
            # 応答待機（要件定義書は長いので300秒）
            logger.info("⏱️ 待機時間: 300秒（要件定義書作成）")
            success = await self.browser.wait_for_text_generation(max_wait=300)
            
            if not success:
                return {
                    'success': False,
                    'error': 'タイムアウト（300秒）',
                    'task_id': task_id
                }
            
            # 応答取得
            response_text = await self.browser.extract_latest_text_response()
            
            if not response_text:
                return {
                    'success': False,
                    'error': '応答取得失敗',
                    'task_id': task_id
                }
            
            logger.info(f"✅ 応答取得完了（{len(response_text)}文字）")
            
            # ファイル保存
            output_file = await self._save_requirements(response_text, task_id)
            
            return {
                'success': True,
                'message': f'要件定義書作成完了: {output_file.name}',
                'output_file': str(output_file),
                'content_length': len(response_text),
                'task_id': task_id
            }
            
        except Exception as e:
            logger.error(f"❌ 要件定義書作成エラー: {e}")
            return {
                'success': False,
                'error': str(e),
                'task_id': task_id
            }
    
    async def _save_requirements(self, text: str, task_id: str) -> Path:
        """要件定義書を保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"requirements_wordpress_{task_id}_{timestamp}.md"
        output_path = self.output_folder / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# WordPress要件定義書\n\n")
            f.write(f"作成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
            f.write(f"タスクID: {task_id}\n\n")
            f.write("---\n\n")
            f.write(text)
        
        logger.info(f"✅ 要件定義書保存: {filename}")
        return output_path