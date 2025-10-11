# content_writers/base_writer.py
"""ベースライターエージェント - 全言語共通機能"""
import asyncio
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseContentWriter(ABC):
    """ベースコンテンツライターAI - 全言語共通機能"""
    
    def __init__(self, browser, output_folder: Path = None):
        self.browser = browser
        self.output_folder = output_folder or Path("agent_outputs")
        self.output_folder.mkdir(exist_ok=True, parents=True)
    
    @abstractmethod
    def get_language_code(self) -> str:
        """言語コードを返す (例: ja, en, ru)"""
        pass
    
    @abstractmethod
    def get_language_name(self) -> str:
        """言語名を返す (例: 日本語, English)"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """この言語専用のシステムプロンプトを返す"""
        pass
    
    async def process_task(self, task: Dict) -> Dict:
        """コンテンツ作成タスクを処理"""
        try:
            lang_code = self.get_language_code()
            lang_name = self.get_language_name()
            
            logger.info(f"🔧 {lang_name}ライターAI: タスク処理開始")
            logger.info(f"タスク: {task['description'][:100]}...")
            
            # タスクから要件を抽出
            task_info = self._parse_task_requirements(task['description'])
            
            # プロンプトを構築
            full_prompt = self._build_prompt(task, task_info)
            
            # Geminiに送信
            logger.info(f"Geminiに{lang_name}記事作成を依頼中...")
            await self.browser.send_prompt(full_prompt)
            
            # 応答待機
            success = await self.browser.wait_for_text_generation(max_wait=120)
            
            if not success:
                return {
                    'success': False,
                    'error': f'{lang_name}ライターAI: タイムアウト'
                }
            
            # 応答を取得
            article_html = await self.browser.extract_latest_text_response()
            
            if not article_html:
                return {
                    'success': False,
                    'error': f'{lang_name}ライターAI: 記事取得失敗'
                }
            
            logger.info(f"✅ {lang_name}記事生成完了: {len(article_html)}文字")
            
            # タイトルを抽出
            article_title = self._extract_title(article_html)
            
            # 保存
            return await self._save_article(task, article_html, article_title)
            
        except Exception as e:
            logger.error(f"{self.get_language_name()}ライターAI処理エラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_prompt(self, task: Dict, task_info: Dict) -> str:
        """プロンプトを構築"""
        system_prompt = self.get_system_prompt()
        
        full_prompt = f"""{system_prompt}

【具体的な執筆依頼】
参照URL: {task_info.get('url', 'なし')}
ターゲット読者: {task_info.get('target_audience', 'ウズベキスタンのM&Aに興味があるビジネスオーナー')}
言語: {self.get_language_name()}
Polylang設定: {task.get('polylang_lang', self.get_language_code())}

【厳守事項】
1. 必ず{self.get_language_name()}のみで執筆
2. 目標文字数: 1800〜2500文字
3. 完全なHTML形式で出力
4. 記事は必ず最後まで完結させる
5. </article>タグで必ず閉じる

**{self.get_language_name()}で、HTMLタグを使用した完全な記事を最後まで書き切ってください。**"""
        
        return full_prompt
    
    def _parse_task_requirements(self, description: str) -> Dict:
        """タスク説明から要件を抽出"""
        import re
        
        # URLを抽出
        url_match = re.search(r'https?://[^\s]+', description)
        url = url_match.group(0) if url_match else ""
        
        return {
            'url': url,
            'target_audience': 'ウズベキスタンのM&Aに興味があるビジネスオーナー'
        }
    
    def _extract_title(self, html_content: str) -> str:
        """HTMLからタイトルを抽出"""
        import re
        title_match = re.search(r'<h1[^>]*>(.+?)</h1>', html_content, re.IGNORECASE | re.DOTALL)
        if title_match:
            title_html = title_match.group(1)
            title = re.sub(r'<[^>]+>', '', title_html).strip()
            return title
        return "（タイトル不明）"
    
    async def _save_article(self, task: Dict, html_content: str, title: str) -> Dict:
        """記事を保存"""
        article_data = {
            'task_id': task['task_id'],
            'title': title,
            'html_content': html_content,
            'language': self.get_language_code(),
            'language_name': self.get_language_name(),
            'polylang_lang': task.get('polylang_lang', self.get_language_code()),
            'created_at': datetime.now().isoformat(),
            'word_count': len(html_content),
            'is_complete': True
        }
        
        # JSON保存
        json_filename = f"article_{self.get_language_code()}_{task['task_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        json_output_path = self.output_folder / json_filename
        
        # HTML保存
        html_filename = f"article_{self.get_language_code()}_{task['task_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        html_output_path = self.output_folder / html_filename
        
        # JSONファイル保存
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(article_data, f, ensure_ascii=False, indent=2)
        
        # HTMLファイル保存
        with open(html_output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"記事を保存: {json_filename}, {html_filename}")
        
        summary = f"記事タイトル: {title}\n言語: {self.get_language_name()}\nPolylang: {article_data['polylang_lang']}\n文字数: {len(html_content)}"
        
        return {
            'success': True,
            'output_file': str(json_output_path.absolute()),  # 絶対パスを返す
            'html_file': str(html_output_path.absolute()),    # 絶対パスを返す
            'summary': summary,
            'full_text': html_content,
            'article_title': title,
            'content_type': 'structured_html_compact',
            'language': self.get_language_code(),
            'is_complete': article_data['is_complete']
        }


# ==========================================
# 日本語ライター
# ==========================================
class JapaneseContentWriter(BaseContentWriter):
    """日本語専用コンテンツライター"""
    
    def get_language_code(self) -> str:
        return "ja"
    
    def get_language_name(self) -> str:
        return "日本語"
    
    def get_system_prompt(self) -> str:
        return """あなたは経験豊富な日本語コンテンツライターです。

【執筆原則】
- 必ず日本語（ひらがな、カタカナ、漢字）で執筆
- ビジネスフォーマルな文体、敬語使用
- 日本のビジネスオーナー向けに最適化
- 具体的なデータと数字を含める
- 読みやすい構造化HTML

【記事構造】
<article class="mna-article">
  <h1>魅力的な日本語タイトル</h1>
  <div class="article-meta">
    <span class="publish-date">公開日: YYYY年MM月DD日</span>
  </div>
  <section class="intro">
    <h2>はじめに</h2>
    <p>記事の概要（2-3文）</p>
  </section>
  <section class="main-content">
    <h2>主要ポイント</h2>
    <p>詳細な説明</p>
  </section>
  <section class="conclusion">
    <h2>まとめ</h2>
    <p>要点のまとめ</p>
  </section>
</article>"""


# ==========================================
# 英語ライター
# ==========================================
class EnglishContentWriter(BaseContentWriter):
    """英語専用コンテンツライター"""
    
    def get_language_code(self) -> str:
        return "en"
    
    def get_language_name(self) -> str:
        return "English"
    
    def get_system_prompt(self) -> str:
        return """You are an experienced English content writer specializing in Uzbekistan M&A market.

【Writing Principles】
- Write entirely in English (business formal style)
- Target audience: International business owners and investors
- Include specific data and numbers
- SEO-optimized structure
- Clear, structured HTML format

【Article Structure】
<article class="mna-article">
  <h1>Compelling English Title</h1>
  <div class="article-meta">
    <span class="publish-date">Published: Month DD, YYYY</span>
  </div>
  <section class="intro">
    <h2>Introduction</h2>
    <p>Article overview (2-3 sentences)</p>
  </section>
  <section class="main-content">
    <h2>Key Points</h2>
    <p>Detailed explanation</p>
  </section>
  <section class="conclusion">
    <h2>Conclusion</h2>
    <p>Summary of key points</p>
  </section>
</article>"""


# ==========================================
# ロシア語ライター
# ==========================================
class RussianContentWriter(BaseContentWriter):
    """ロシア語専用コンテンツライター"""
    
    def get_language_code(self) -> str:
        return "ru"
    
    def get_language_name(self) -> str:
        return "Русский"
    
    def get_system_prompt(self) -> str:
        return """Вы опытный контент-райтер, специализирующийся на рынке слияний и поглощений Узбекистана.

【Принципы написания】
- Пишите полностью на русском языке (деловой стиль)
- Целевая аудитория: Русскоязычные бизнесмены и инвесторы
- Включайте конкретные данные и цифры
- Четкая структура HTML

【Структура статьи】
<article class="mna-article">
  <h1>Привлекательный русский заголовок</h1>
  <div class="article-meta">
    <span class="publish-date">Опубликовано: ДД месяц ГГГГ</span>
  </div>
  <section class="intro">
    <h2>Введение</h2>
    <p>Краткий обзор статьи</p>
  </section>
  <section class="main-content">
    <h2>Основные моменты</h2>
    <p>Подробное объяснение</p>
  </section>
  <section class="conclusion">
    <h2>Заключение</h2>
    <p>Резюме ключевых моментов</p>
  </section>
</article>"""