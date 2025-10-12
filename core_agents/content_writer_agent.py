# content_writer_agent.py
import asyncio
import logging
import json
from pathlib import Path
from typing import Dict
from datetime import datetime

from configuration.config_utils import ErrorHandler, PathManager
from browser_control.browser_controller import BrowserController

logger = logging.getLogger(__name__)

class ContentWriterAgent:
    """強化版コンテンツライターAI - コンパクトな構造化HTML記事を生成"""
    
    CONTENT_WRITER_PROMPT = """あなたは経験豊富なコンテンツライターです。ウズベキスタンのM&A市場に関する専門知識を持っています。

【あなたの役割】
- 指定されたURLの記事を読み、ウズベキスタンのM&Aに興味があるビジネスオーナー向けに有益な記事を作成
- ブログにそのまま掲載できる高品質の構造化HTML記事を執筆
- SEOを意識した構成とキーワード配置
- 多言語対応（日本語/英語/ロシア語など）

【執筆の原則】
1. 「了解しました！」などの挨拶は一切不要
2. 最初から完全なHTML形式で出力
3. 数字や重要な部分は<strong>タグで強調
4. 適切な見出し構造（h2, h3）と段落で読みやすく
5. リストを活用した構造化
6. ターゲット読者（ビジネスオーナー、投資家）の関心に合わせた内容

【記事の長さ】
- 目標文字数: 1800〜3500文字、2000~3000文字程度が最もベスト
- コンパクトで価値の高い内容に集中
- 冗長な説明を避け、重要なポイントのみを記載

【出力形式 - シンプルなHTML構造】
以下のHTML構造で出力してください：

<article class="mna-article">
  <h1>記事タイトル - 魅力的でSEOを意識</h1>
  
  <div class="article-meta">
    <span class="publish-date">公開日: YYYY年MM月DD日</span>
    <span class="target-region">対象地域: ウズベキスタン</span>
  </div>
  
  <section class="intro">
    <h2>はじめに</h2>
    <p>この記事のテーマと価値を簡潔に説明（2-3文）</p>
  </section>
  
  <section class="main-content">
    <h2>主要ポイント</h2>
    <p>重要な情報を簡潔に説明（3-4段落）</p>
    
    <div class="key-points">
      <h3>注目すべき点</h3>
      <ul>
        <li><strong>ポイント1</strong>: 簡潔な説明</li>
        <li><strong>ポイント2</strong>: 簡潔な説明</li>
        <li><strong>ポイント3</strong>: 簡潔な説明</li>
      </ul>
    </div>
  </section>
  
  <section class="business-value">
    <h2>ビジネス機会</h2>
    <p>ウズベキスタンのM&A市場における具体的な機会（2-3段落）</p>
  </section>
  
  <section class="conclusion">
    <h2>まとめ</h2>
    <p>要点を2-3文でまとめる</p>
  </section>
  
  <div class="article-footer">
    <p><strong>参照元</strong>: <a href="元記事URL" target="_blank">元記事タイトル</a></p>
  </div>
</article>

【重要な制約】
- 各セクションは簡潔に（1セクションあたり200-300文字）
- 冗長な表現を避ける
- 必ず最後（</article>タグ）まで完結させる
"""

    def __init__(self, browser: BrowserController, output_folder: Path = None):
        self.browser = browser
        if output_folder is None:
            from configuration.config_utils import config
            if config.AGENT_OUTPUT_FOLDER:
                self.output_folder = PathManager.get_safe_path(config.AGENT_OUTPUT_FOLDER)
            else:
                self.output_folder = Path(r"C:\Users\color\Documents\gemini_auto_generate\agent_outputs")
                self.output_folder.mkdir(exist_ok=True, parents=True)
        else:
            self.output_folder = output_folder
    
    async def process_task(self, task: Dict) -> Dict:
        """コンテンツ作成タスクを処理 - コンパクトな構造化HTML出力"""
        try:
            logger.info(f"🔧 強化版コンテンツライターAI: タスク処理開始")
            logger.info(f"タスク: {task['description'][:100]}...")
            
            # タスクから要件を抽出
            task_info = self._parse_task_requirements(task['description'])
            
            # タスクに明示的な言語フィールドがある場合は優先
            if 'language' in task and task['language']:
                task_info['language'] = task['language']
                logger.info(f"📌 タスクフィールドから言語を取得: {task_info['language']}")
            
            logger.info(f"  URL: {task_info['url'][:60] if task_info['url'] else '(URLなし)'}...")
            logger.info(f"  言語: {task_info['language']}")
            logger.info(f"  ターゲット: {task_info['target_audience']}")
            
            # 言語別のプロンプト調整
            language_specific_prompt = self._get_language_specific_prompt(task_info['language'])
            
            # プロンプトを構築（コンパクト版）
            full_prompt = f"""{self.CONTENT_WRITER_PROMPT}

{language_specific_prompt}

【具体的な執筆依頼】
参照URL: {task_info['url']}
ターゲット読者: {task_info['target_audience']}
言語: {task_info['language']}

【厳守事項】
1. 上記URLの記事を読み、{task_info['target_audience']}向けに有益な記事を作成
2. 目標文字数: 1500〜1800文字（これを絶対に超えない）
3. 完全なHTML形式で出力（マークダウン不可）
4. 見出し構造（h1, h2, h3）を適切に使用
5. 重要な数字は<strong>タグで強調
6. 記事全体を{task_info['language']}で執筆
7. 各セクションは簡潔に（1セクション200-300文字）

【最重要】
- 記事は必ず完結させる（途中で終わらない）
- </article>タグで必ず閉じる
- conclusionセクションとarticle-footerを必ず含める
- 長すぎる記事は途中で切れる可能性があるため、コンパクトに書く

**1800文字以内で、HTMLタグを使用した完全な記事を最後まで書き切ってください。**"""
            
            # Geminiに送信
            logger.info("Geminiにコンパクトな構造化HTML記事作成を依頼中...")
            logger.info(f"  目標文字数: 1500〜1800文字")
            logger.info(f"  プロンプト長: {len(full_prompt)}文字")
            await self.browser.send_prompt(full_prompt)
            
            # 応答待機（コンパクトなので短めでOK）
            success = await self.browser.wait_for_text_generation(max_wait=120)
            
            if not success:
                return {
                    'success': False,
                    'error': 'コンテンツライターAI: タイムアウト'
                }
            
            # 応答を取得
            article_html = await self.browser.extract_latest_text_response()
            
            if not article_html:
                return {
                    'success': False,
                    'error': 'コンテンツライターAI: 記事取得失敗'
                }
            
            logger.info(f"✅ 構造化HTML記事生成完了: {len(article_html)}文字")
            
            # HTMLの完全性をチェック
            if not self._validate_html_completeness(article_html):
                logger.warning("⚠️ 記事が途中で途切れている可能性があります")
            
            # タイトルを抽出（最初の<h1>タグ）
            import re
            title_match = re.search(r'<h1[^>]*>(.+?)</h1>', article_html, re.IGNORECASE | re.DOTALL)
            article_title = title_match.group(1).strip() if title_match else "（タイトル不明）"
            
            logger.info(f"  記事タイトル: {article_title}")
            
            # JSON形式でメタデータとともに保存
            article_data = {
                'task_id': task['task_id'],
                'title': article_title,
                'html_content': article_html,
                'language': task_info['language'],
                'target_audience': task_info['target_audience'],
                'source_url': task_info['url'],
                'created_at': datetime.now().isoformat(),
                'word_count': len(article_html),
                'content_type': 'structured_html_compact',
                'is_complete': self._validate_html_completeness(article_html)
            }
            
            # JSONファイルとして保存
            json_filename = f"article_{task['task_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            json_output_path = self.output_folder / json_filename
            
            with open(json_output_path, 'w', encoding='utf-8') as f:
                json.dump(article_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"構造化記事をJSON保存: {json_filename}")
            
            # HTMLファイルも別途保存（確認用）
            html_filename = f"article_{task['task_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            html_output_path = self.output_folder / html_filename
            
            with open(html_output_path, 'w', encoding='utf-8') as f:
                f.write("<!DOCTYPE html>\n")
                f.write("<html lang='ja'>\n")
                f.write("<head>\n")
                f.write("<meta charset='UTF-8'>\n")
                f.write("<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n")
                f.write(f"<title>{article_title}</title>\n")
                f.write("<style>\n")
                f.write("body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.8; margin: 40px; max-width: 800px; margin: 0 auto; padding: 40px; }\n")
                f.write("h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 15px; font-size: 28px; }\n")
                f.write("h2 { color: #34495e; margin-top: 35px; font-size: 22px; border-left: 4px solid #3498db; padding-left: 10px; }\n")
                f.write("h3 { color: #16a085; font-size: 18px; margin-top: 20px; }\n")
                f.write(".article-meta { background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 25px 0; font-size: 14px; }\n")
                f.write(".key-points { background: #e8f4fd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #3498db; }\n")
                f.write(".article-footer { margin-top: 50px; padding-top: 25px; border-top: 2px solid #ddd; color: #666; }\n")
                f.write("ul { line-height: 1.8; }\n")
                f.write("li { margin-bottom: 10px; }\n")
                f.write("strong { color: #e74c3c; }\n")
                f.write("p { margin-bottom: 15px; }\n")
                f.write("</style>\n")
                f.write("</head>\n")
                f.write("<body>\n")
                f.write(article_html)
                f.write("</body>\n")
                f.write("</html>\n")
            
            logger.info(f"HTMLプレビューも保存: {html_filename}")
            
            # サマリーを作成
            article_preview = self._extract_text_preview(article_html)
            
            summary = f"記事タイトル: {article_title}\n言語: {task_info['language']}\n文字数: {len(article_html)}\n完全性: {'✅ 完全' if article_data['is_complete'] else '⚠️ 不完全'}\nプレビュー: {article_preview}"
            
            return {
                'success': True,
                'output_file': str(json_output_path),
                'html_file': str(html_output_path),
                'summary': summary,
                'full_text': article_html,
                'article_title': article_title,
                'content_type': 'structured_html_compact',
                'language': task_info['language'],
                'is_complete': article_data['is_complete']
            }
            
        except Exception as e:
            ErrorHandler.log_error(e, "強化版コンテンツライターAI処理")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _validate_html_completeness(self, html_content: str) -> bool:
        """HTMLが完全かどうかをチェック"""
        import re
        
        # 必須要素がすべて含まれているかチェック
        required_elements = [
            r'<article[^>]*>',           # 開始タグ
            r'</article>',                # 終了タグ
            r'<section[^>]*class="conclusion"',  # まとめセクション
            r'<div[^>]*class="article-footer"'   # フッター
        ]
        
        for pattern in required_elements:
            if not re.search(pattern, html_content, re.IGNORECASE):
                logger.warning(f"⚠️ 必須要素が見つかりません: {pattern}")
                return False
        
        return True
    
    def _get_language_specific_prompt(self, language: str) -> str:
        """言語別の追加プロンプトを返す"""
        prompts = {
            "日本語": """
【日本語記事の特徴】
- 必ず日本語（ひらがな、カタカナ、漢字を含む自然な日本語）で執筆
- 敬語を使用し、ビジネスフォーマルな文体を維持
- 具体的なデータとともに説明を展開
- ウズベキスタンのM&A市場における日本企業の視点を重視
- 読者（日本のビジネスオーナー）が理解しやすい表現を使用
- 1500〜1800文字以内にまとめる

【執筆時の注意点】
- 英語や他言語は固有名詞・専門用語以外では使用しない
- 数字は半角、単位は全角（例: 6%、100億円）
- 各セクションは簡潔に200-300文字程度
- 記事は必ず最後（</article>タグ）まで完結させる
""",
            "English": """
【English Article Features】
- Write entirely in English (no Japanese characters except proper nouns)
- Use business formal English throughout
- Include specific data and examples
- Focus on investment opportunities in Uzbekistan's M&A market
- Target international business owners and investors
- Keep article between 1500-1800 characters
- Complete the article with proper conclusion and footer sections
""",
            "Русский (ロシア語)": """
【Русскоязычная статья особенности】
- Пишите полностью на русском языке
- Используйте деловой русский язык
- Включите конкретные данные и примеры
- Акцент на возможностях слияний и поглощений в Узбекистане
- Целевая аудитория - русскоязычные инвесторы
- Объём статьи: 1500-1800 символов
- Завершите статью полноценным заключением
"""
        }
        return prompts.get(language, prompts["日本語"])
    
    def _extract_text_preview(self, html_content: str) -> str:
        """HTMLからテキストプレビューを抽出"""
        import re
        # HTMLタグを除去
        text = re.sub(r'<[^>]+>', ' ', html_content)
        # 連続する空白を単一スペースに
        text = re.sub(r'\s+', ' ', text)
        # 先頭200文字を返す
        return text.strip()[:200] + "..." if len(text) > 200 else text
    
    def _parse_task_requirements(self, description: str) -> Dict[str, str]:
        """タスク説明から要件を抽出（日本語デフォルト版）"""
        import re
        
        # URLを抽出
        url_match = re.search(r'https?://[^\s]+', description)
        url = url_match.group(0) if url_match else ""
        
        # === 言語検出ロジック（日本語デフォルト戦略） ===
        # 基本方針: 明示的な指定がない限り、常に日本語で生成
        language = "日本語"  # 絶対的なデフォルト
        
        # 明示的な言語指定パターン（非常に厳格に）
        explicit_lang_patterns = {
            "English": [
                r'英語で(?:作成|記事|執筆|書)',
                r'write in english',
                r'in english(?:\s+language)?',
                r'create.*in english',
                r'言語[：:]\s*(?:英語|English)'
            ],
            "Русский (ロシア語)": [
                r'ロシア語で(?:作成|記事|執筆|書)',
                r'на русском(?:\s+языке)?',
                r'in russian',
                r'言語[：:]\s*(?:ロシア語|русский)'
            ],
            "中文": [
                r'中国語で(?:作成|記事|執筆|書)',
                r'中文で(?:作成|記事|執筆|書)',
                r'in chinese',
                r'用中文',
                r'言語[：:]\s*(?:中国語|中文|Chinese)'
            ],
            "한국어": [
                r'韓国語で(?:作成|記事|執筆|書)',
                r'한국어로',
                r'in korean',
                r'言語[：:]\s*(?:韓国語|한국어)'
            ],
            "Türkçe": [
                r'トルコ語で(?:作成|記事|執筆|書)',
                r'türkçe(?:\'de)?',
                r'in turkish',
                r'言語[：:]\s*(?:トルコ語|Türkçe)'
            ],
            "O'zbek": [
                r'ウズベク語で(?:作成|記事|執筆|書)',
                r'o\'zbek tilida',
                r'in uzbek',
                r'言語[：:]\s*(?:ウズベク語|O\'zbek)'
            ]
        }
        
        # 明示的な言語指定をチェック
        explicit_lang_found = False
        for lang, patterns in explicit_lang_patterns.items():
            for pattern in patterns:
                if re.search(pattern, description, re.IGNORECASE):
                    language = lang
                    explicit_lang_found = True
                    logger.info(f"✅ 明示的な言語指定を検出: {language}")
                    logger.info(f"   マッチしたパターン: {pattern}")
                    break
            if explicit_lang_found:
                break
        
        # 明示的な指定がなかった場合
        if not explicit_lang_found:
            logger.info("📌 明示的な言語指定なし → デフォルトの日本語を使用")
            
            # 補助的な判定（極端なケースのみ）
            # キリル文字が大半を占める場合のみロシア語と判定
            cyrillic_count = len(re.findall(r'[А-Яа-яЁё]', description))
            total_chars = len(re.sub(r'\s', '', description))
            
            # ハングルが大半を占める場合のみ韓国語と判定
            hangul_count = len(re.findall(r'[가-힣]', description))
            
            if total_chars > 0:
                if cyrillic_count > total_chars * 0.3:  # 30%以上がキリル文字
                    language = "Русский (ロシア語)"
                    logger.info(f"🔍 キリル文字が多数（{cyrillic_count}/{total_chars}）: ロシア語")
                elif hangul_count > total_chars * 0.3:  # 30%以上がハングル
                    language = "한국어"
                    logger.info(f"🔍 ハングルが多数（{hangul_count}/{total_chars}）: 韓国語")
                else:
                    # それ以外は全て日本語（ひらがな・カタカナ・漢字・英数字混在含む）
                    logger.info("📝 デフォルト言語確定: 日本語")
        
        # ターゲット読者を抽出
        target_patterns = [
            r'(.+?)向けに',
            r'(.+?)向けの',
            r'ターゲット[：:]\s*(.+)',
            r'for (.+?) considering',
            r'для (.+?),',
            r'対象読者[：:]\s*(.+)'
        ]
        target_audience = ""
        for pattern in target_patterns:
            match = re.search(pattern, description)
            if match:
                target_audience = match.group(1).strip()
                break
        
        if not target_audience:
            target_audience = "ウズベキスタンのM&Aに興味があるビジネスオーナー"
        
        # 特別な要件を抽出
        requirements = []
        if '構造化' in description or 'HTML' in description.upper():
            requirements.append("構造化HTML形式で出力")
        if 'データ' in description or '数字' in description:
            requirements.append("具体的なデータと数字を含める")
        if '事例' in description or 'ケーススタディ' in description:
            requirements.append("実際の事例やケーススタディを含める")
        
        logger.info(f"📝 最終決定言語: {language}")
        logger.info(f"🎯 ターゲット読者: {target_audience}")
        
        def _get_translation_prompt(self, source_language: str, target_language: str) -> str:
            """翻訳タスク用の追加プロンプト"""
            return f"""
        【翻訳タスクの指示】
        これは翻訳タスクです。以下の指示に厳密に従ってください：

        1. 元の記事の内容を{target_language}に正確に翻訳
        2. HTML構造とフォーマットを維持
        3. 文化的な違いを考慮した自然な表現を使用
        4. 専門用語は正確に翻訳
        5. 数字やデータはそのまま保持

        翻訳元言語: {source_language}
        翻訳先言語: {target_language}

        **重要: 翻訳後の記事は完全なHTML形式で、必ず</article>タグで終了すること**
        """
        
        return {
            'url': url,
            'language': language,
            'target_audience': target_audience,
            'requirements': '、'.join(requirements) if requirements else "標準的な構造化記事"
        }