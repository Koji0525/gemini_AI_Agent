"""WordPressユーティリティ (Google Drive対応版)
このモジュールは、WordPressタスクの処理に必要な各種ユーティリティクラスを提供します。
主な機能:
- タスク内容の取得（Google Drive、JSON、ローカルファイル対応）
- タスクタイプの分析と判定
- WordPressプラグイン・設定管理
- HTMLクリーニング・最適化
"""

import re
import logging
from typing import Optional, Tuple, Dict, List
from pathlib import Path
import json

# ロガーの初期化
logger = logging.getLogger(__name__)


# ============================================================================
# TaskContentFetcher: タスク内容取得クラス
# ============================================================================

class TaskContentFetcher:
    """タスク内容取得ユーティリティ (Google Drive対応)
    
    複数のソースから記事コンテンツを取得する機能を提供:
    1. Google Driveリンク（最優先）
    2. JSONファイルパス
    3. ローカルMarkdownファイル
    4. task_logシート（フォールバック）
    """
    
    @staticmethod
    def extract_task_id(description: str) -> Optional[int]:
        """説明文からtask_idを抽出
        
        対応形式:
        - task_id 39
        - task id 39
        - タスクID 39
        
        Args:
            description: タスク説明文
            
        Returns:
            抽出されたtask_id、見つからない場合はNone
        """
        # 複数のパターンでtask_idを検索
        patterns = [
            r'task[_\s]+id[\s　]*(\d+)',  # task_id, task id形式
            r'タスク[\s　]*ID[\s　]*(\d+)',  # 日本語形式
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                task_id = int(match.group(1))
                logger.info(f"✅ task_id抽出: {task_id}")
                return task_id
        
        logger.debug("task_idが見つかりませんでした")
        return None

    @staticmethod
    async def get_task_content(sheets_manager, task_id: int) -> Optional[str]:
        """指定されたtask_idの記事内容を取得(超堅牢版)
        
        優先順位:
        1. task_execution_log シートの Google Drive リンク(最優先)
        2. task_execution_log シートの output_data カラム(JSONファイルパス)
        3. task_execution_log シートのローカルマークダウンファイルパス
        4. task_log シート(フォールバック)
        
        Args:
            sheets_manager: GoogleSheetsManagerインスタンス
            task_id: タスクID
            
        Returns:
            記事内容(テキスト)、失敗時はNone
        """
        try:
            logger.info("="*60)
            logger.info(f"【記事取得開始】task_id={task_id}")
            logger.info("="*60)
            
            # === パート1: sheets_managerの検証 ===
            if not TaskContentFetcher._validate_sheets_manager(sheets_manager):
                return None
            
            # === パート2: スプレッドシートを開く ===
            sheet = TaskContentFetcher._open_spreadsheet(sheets_manager)
            if not sheet:
                return None
            
            # === パート3: task_execution_logから取得を試みる ===
            logger.info("\n【優先度1】task_execution_logから取得を試みます")
            content = await TaskContentFetcher._get_from_execution_log(
                sheet, task_id, sheets_manager
            )
            
            if content:
                logger.info(f"✅ 記事取得成功: {len(content)}文字")
                return content
            
            # === パート4: フォールバック - task_logから取得 ===
            logger.info("\n【優先度2】task_logから取得を試みます(フォールバック)")
            content = await TaskContentFetcher._get_from_task_log(
                sheet, task_id
            )
            
            if content:
                logger.info(f"✅ 記事取得成功(task_log): {len(content)}文字")
                return content
            
            logger.error("❌ すべての方法で記事取得に失敗しました")
            return None
            
        except Exception as e:
            logger.error(f"❌ task_id {task_id} の内容取得エラー: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def _validate_sheets_manager(sheets_manager) -> bool:
        """sheets_managerの妥当性を検証
        
        Args:
            sheets_manager: GoogleSheetsManagerインスタンス
            
        Returns:
            検証成功時True、失敗時False
        """
        if not sheets_manager:
            logger.error("❌ sheets_managerが設定されていません")
            return False
        
        if not sheets_manager.gc:
            logger.error("❌ Google Sheetsクライアントが初期化されていません")
            return False
        
        logger.info("✅ sheets_manager検証完了")
        return True

    @staticmethod
    def _open_spreadsheet(sheets_manager):
        """スプレッドシートを開く
        
        Args:
            sheets_manager: GoogleSheetsManagerインスタンス
            
        Returns:
            スプレッドシートオブジェクト、失敗時None
        """
        logger.info(f"📊 スプレッドシートを開く: {sheets_manager.spreadsheet_id}")
        try:
            sheet = sheets_manager.gc.open_by_key(sheets_manager.spreadsheet_id)
            logger.info("✅ スプレッドシート接続成功")
            return sheet
        except Exception as e:
            logger.error(f"❌ スプレッドシート接続失敗: {e}")
            return None

    @staticmethod
    async def _get_from_execution_log(sheet, task_id: int, sheets_manager) -> Optional[str]:
        """task_execution_log シートから取得(超詳細ログ版)
        
        優先順位:
        1. Google Driveリンク
        2. output_data(JSONファイルパス)
        3. ローカルマークダウンファイル
        
        Args:
            sheet: スプレッドシートオブジェクト
            task_id: タスクID
            sheets_manager: GoogleSheetsManagerインスタンス
            
        Returns:
            記事内容、失敗時None
        """
        try:
            # === パート1: シートを開く ===
            logger.debug("【切り分け1】task_execution_logシートを開く")
            try:
                execution_log_sheet = sheet.worksheet("task_execution_log")
                logger.info("✅ task_execution_logシート発見")
            except Exception as e:
                logger.warning(f"❌ task_execution_logシートが見つかりません: {e}")
                return None
            
            # === パート2: シートデータを取得 ===
            logger.debug("【切り分け2】シートデータを取得")
            execution_log_data = execution_log_sheet.get_all_values()
            
            if len(execution_log_data) == 0:
                logger.warning("❌ task_execution_logシートが空です")
                return None
            
            logger.info(f"✅ {len(execution_log_data)}行のデータを取得")
            
            # === パート3: ヘッダー行を解析してカラムインデックスを特定 ===
            column_indices = TaskContentFetcher._parse_header_columns(execution_log_data[0])
            if column_indices['task_id_col'] is None:
                logger.warning("❌ task_id カラムが見つかりません")
                return None
            
            # === パート4: 対象のtask_idを検索 ===
            logger.debug(f"【切り分け6】task_id={task_id}を検索中...")
            for row_idx, row in enumerate(execution_log_data[1:], start=2):
                if len(row) <= column_indices['task_id_col']:
                    continue
                
                try:
                    task_id_in_row = int(row[column_indices['task_id_col']])
                except (ValueError, IndexError):
                    continue
                
                if task_id_in_row == task_id:
                    logger.info(f"✅ task_id {task_id} を行 {row_idx} で発見")
                    logger.debug(f"行内容: {row[:min(len(row), 10)]}...")
                    
                    # === パート5: データソースから記事を取得 ===
                    content = await TaskContentFetcher._fetch_content_from_sources(
                        row, column_indices, sheets_manager
                    )
                    
                    if content:
                        return content
                    
                    logger.warning(f"❌ task_id {task_id} のデータがすべて空です")
                    return None
            
            logger.warning(f"❌ task_id {task_id} が task_execution_log に見つかりませんでした")
            return None
            
        except Exception as e:
            logger.error(f"❌ task_execution_log からの取得エラー: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def _parse_header_columns(headers: List[str]) -> Dict[str, Optional[int]]:
        """ヘッダー行を解析してカラムインデックスを特定
        
        Args:
            headers: ヘッダー行のリスト
            
        Returns:
            カラムインデックスの辞書
        """
        logger.debug("【切り分け3】ヘッダー行を解析")
        logger.debug(f"ヘッダー: {headers}")
        
        column_indices = {
            'task_id_col': None,
            'output_data_col': None,
            'markdown_file_col': None,
            'drive_link_col': None
        }
        
        logger.debug("【切り分け4】カラムインデックスを特定")
        for i, header in enumerate(headers):
            header_lower = header.lower().strip()
            
            if 'task_id' in header_lower or 'タスクid' in header_lower:
                column_indices['task_id_col'] = i
                logger.debug(f"  → task_id列: {i}")
            elif 'output_data' in header_lower or 'full_text' in header_lower or '出力データ' in header_lower or '出力' in header_lower:
                column_indices['output_data_col'] = i
                logger.debug(f"  → output_data列: {i}")
            elif 'drive' in header_lower or 'link' in header_lower or 'url' in header_lower or 'リンク' in header_lower:
                column_indices['drive_link_col'] = i
                logger.debug(f"  → drive_link列: {i}")
            elif 'markdown' in header_lower or 'file' in header_lower or 'ファイル' in header_lower:
                column_indices['markdown_file_col'] = i
                logger.debug(f"  → markdown列: {i}")
        
        logger.debug(f"【切り分け5】カラム特定結果")
        for key, value in column_indices.items():
            logger.debug(f"  {key}: {value}")
        
        return column_indices

    @staticmethod
    async def _fetch_content_from_sources(
        row: List[str], 
        column_indices: Dict[str, Optional[int]], 
        sheets_manager
    ) -> Optional[str]:
        """複数のソースから記事内容を取得（優先順位付き）
        
        Args:
            row: データ行
            column_indices: カラムインデックス辞書
            sheets_manager: GoogleSheetsManagerインスタンス
            
        Returns:
            記事内容、失敗時None
        """
        # 優先度1: Google Driveリンク
        content = await TaskContentFetcher._fetch_from_drive_link(
            row, column_indices, sheets_manager
        )
        if content:
            return content
        
        # 優先度2: output_data(JSONファイルまたは直接テキスト)
        content = TaskContentFetcher._fetch_from_output_data(
            row, column_indices
        )
        if content:
            return content
        
        # 優先度3: ローカルマークダウンファイル
        content = TaskContentFetcher._fetch_from_markdown_file(
            row, column_indices
        )
        if content:
            return content
        
        return None

    @staticmethod
    async def _fetch_from_drive_link(
        row: List[str], 
        column_indices: Dict[str, Optional[int]], 
        sheets_manager
    ) -> Optional[str]:
        """Google Driveリンクから記事を取得
        
        Args:
            row: データ行
            column_indices: カラムインデックス辞書
            sheets_manager: GoogleSheetsManagerインスタンス
            
        Returns:
            記事内容、失敗時None
        """
        logger.debug("【切り分け7】Google Driveリンクをチェック")
        drive_link_col = column_indices.get('drive_link_col')
        
        if drive_link_col is not None and len(row) > drive_link_col:
            drive_link = row[drive_link_col].strip()
            logger.debug(f"  drive_link列の値: '{drive_link}'")
            
            if drive_link and len(drive_link) > 0:
                logger.info(f"🔗 Google Drive リンクを発見")
                logger.debug(f"  URL: {drive_link[:80]}...")
                
                # Google Driveから読み込み
                logger.debug("【切り分け8】Google Driveから記事を読み込み中...")
                content = sheets_manager.read_file_from_drive(drive_link)
                
                if content:
                    logger.info(f"✅ Google Driveから記事取得成功")
                    logger.debug(f"  文字数: {len(content)}")
                    logger.debug(f"  先頭100文字: {content[:100]}...")
                    return content
                else:
                    logger.warning("❌ Google Driveからの読み込みに失敗")
            else:
                logger.debug("  → drive_link列が空")
        else:
            logger.debug("  → drive_link列なし")
        
        return None

    @staticmethod
    def _fetch_from_output_data(
        row: List[str], 
        column_indices: Dict[str, Optional[int]]
    ) -> Optional[str]:
        """output_dataカラムから記事を取得（JSONまたは直接テキスト）
        
        Args:
            row: データ行
            column_indices: カラムインデックス辞書
            
        Returns:
            記事内容、失敗時None
        """
        logger.debug("【切り分け9】output_dataをチェック")
        output_data_col = column_indices.get('output_data_col')
        
        if output_data_col is not None and len(row) > output_data_col:
            output_data = row[output_data_col].strip()
            logger.debug(f"  output_data列の長さ: {len(output_data)}文字")
            
            if output_data and len(output_data) > 0:
                # JSONファイルパスかどうかを判定
                if output_data.endswith('.json'):
                    logger.info(f"  → JSONファイルと判定: {output_data}")
                    return TaskContentFetcher._read_json_file(output_data)
                else:
                    # 通常のテキストとして扱う
                    logger.info(f"✅ output_data から記事取得(直接)")
                    logger.debug(f"  先頭100文字: {output_data[:100]}...")
                    return output_data
            else:
                logger.debug("  → output_data列が空")
        else:
            logger.debug("  → output_data列なし")
        
        return None

    @staticmethod
    def _read_json_file(json_path_str: str) -> Optional[str]:
        """JSONファイルから記事を読み込む
        
        Args:
            json_path_str: JSONファイルパス
            
        Returns:
            記事内容、失敗時None
        """
        json_path = Path(json_path_str)
        
        # 絶対パスでない場合、候補パスを試す
        if not json_path.is_absolute():
            candidates = [
                Path.cwd() / json_path.name,
                Path.home() / "Documents" / "gemini_AI_Agent" / "agent_outputs" / json_path.name,
                Path.home() / "Documents" / "gemini_auto_generate" / "agent_outputs" / json_path.name,
            ]
            for candidate in candidates:
                if candidate.exists():
                    json_path = candidate
                    break
        
        if json_path.exists():
            logger.info(f"  → JSONファイル読み込み: {json_path}")
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                # html_contentを取得
                html_content = json_data.get('html_content', '')
                if html_content:
                    logger.info(f"✅ JSONからHTML記事取得成功: {len(html_content)}文字")
                    logger.debug(f"  先頭100文字: {html_content[:100]}...")
                    return html_content
                else:
                    logger.warning("❌ JSONにhtml_contentがありません")
            except Exception as e:
                logger.error(f"❌ JSONファイル読み込みエラー: {e}")
        else:
            logger.warning(f"❌ JSONファイルが見つかりません: {json_path}")
        
        return None

    @staticmethod
    def _fetch_from_markdown_file(
        row: List[str], 
        column_indices: Dict[str, Optional[int]]
    ) -> Optional[str]:
        """ローカルマークダウンファイルから記事を取得
        
        Args:
            row: データ行
            column_indices: カラムインデックス辞書
            
        Returns:
            記事内容、失敗時None
        """
        logger.debug("【切り分け10】ローカルファイルをチェック")
        markdown_file_col = column_indices.get('markdown_file_col')
        
        if markdown_file_col is not None and len(row) > markdown_file_col:
            markdown_path = row[markdown_file_col]
            logger.debug(f"  markdown列の値: '{markdown_path}'")
            
            if markdown_path and len(markdown_path.strip()) > 0:
                content = TaskContentFetcher._read_local_markdown_file(markdown_path)
                if content:
                    return content
            else:
                logger.debug("  → markdown列が空")
        else:
            logger.debug("  → markdown列なし")
        
        return None

    @staticmethod
    async def _get_from_task_log(sheet, task_id: int) -> Optional[str]:
        """task_log シートから取得(フォールバック)
        
        Args:
            sheet: スプレッドシートオブジェクト
            task_id: タスクID
            
        Returns:
            記事内容、失敗時None
        """
        try:
            task_log_sheet = sheet.worksheet("task_log")
            task_log_data = task_log_sheet.get_all_values()
            
            if len(task_log_data) == 0:
                return None
            
            headers = task_log_data[0]
            
            # カラムインデックスを特定
            task_id_col = None
            output_data_col = None
            
            for i, header in enumerate(headers):
                if 'task_id' in header.lower():
                    task_id_col = i
                elif 'output_data' in header.lower() or 'full_text' in header.lower():
                    output_data_col = i
            
            # デフォルト値を設定
            if task_id_col is None:
                task_id_col = 1
            
            if output_data_col is None:
                output_data_col = len(headers) - 1
            
            # task_idを検索
            for row_idx, row in enumerate(task_log_data[1:], start=2):
                if len(row) <= task_id_col:
                    continue
                
                try:
                    task_id_in_row = int(row[task_id_col])
                except (ValueError, IndexError):
                    continue
                
                if task_id_in_row == task_id:
                    logger.info(f"✅ task_id {task_id} を task_log の行 {row_idx} で発見")
                    
                    if output_data_col and len(row) > output_data_col:
                        full_text = row[output_data_col]
                        if full_text and len(full_text) > 0:
                            logger.info(f"✅ task_log から取得 ({len(full_text)}文字)")
                            return full_text
            
            return None
            
        except Exception as e:
            logger.error(f"task_log からの取得エラー: {e}")
            return None

    @staticmethod
    def _read_local_markdown_file(file_path: str) -> Optional[str]:
        """ローカルのマークダウンファイルを読み込む(強化版)
        
        Args:
            file_path: ファイルパス
            
        Returns:
            ファイル内容、失敗時None
        """
        try:
            logger.debug("【ローカルファイル読み込み】")
            logger.debug(f"  ファイルパス: {file_path}")
            
            path = Path(file_path.strip())
            
            # 絶対パスの場合
            if path.is_absolute():
                logger.debug("  → 絶対パスとして処理")
                if path.exists():
                    logger.debug(f"  → ファイル存在確認: OK")
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    logger.info(f"✅ ファイル読み込み成功: {len(content)}文字")
                    logger.debug(f"  先頭100文字: {content[:100]}...")
                    
                    # タイトルと本文を抽出
                    content = TaskContentFetcher._extract_title_and_body(content)
                    
                    return content
                else:
                    logger.warning(f"❌ ファイルが見つかりません: {path}")
                    return None
            
            # 相対パスの場合、候補パスを試す
            logger.debug("  → 相対パスとして処理")
            candidates = [
                Path.cwd() / path,
                Path.home() / "Documents" / "gemini_auto_generate" / "agent_outputs" / path.name,
                Path.home() / "Documents" / "AI_Agent" / "agent_outputs" / path.name,
                Path.home() / "Documents" / "gemini_AI_Agent" / "agent_outputs" / path.name,
            ]
            
            logger.debug(f"  候補パス数: {len(candidates)}")
            
            for i, candidate in enumerate(candidates, 1):
                logger.debug(f"  候補{i}: {candidate}")
                if candidate.exists():
                    logger.info(f"  → ファイル発見: {candidate}")
                    path = candidate
                    break
            
            if not path.exists():
                logger.warning(f"❌ すべての候補でファイルが見つかりません")
                for candidate in candidates:
                    logger.warning(f"  試行: {candidate}")
                return None
            
            logger.info(f"📄 ファイル読み込み中: {path}")
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"✅ ファイル読み込み成功: {len(content)}文字")
            logger.debug(f"  先頭100文字: {content[:100]}...")
            
            # タイトルと本文を抽出
            content = TaskContentFetcher._extract_title_and_body(content)
            
            return content
            
        except Exception as e:
            logger.error(f"❌ ファイル読み込みエラー: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def _extract_title_and_body(content: str) -> str:
        """マークダウンファイルからタイトルと本文を抽出
        
        <!-- メタデータ --> や <!-- コメント --> を除去し、
        タイトル(# で始まる行)と本文のみを抽出
        
        Args:
            content: 元のマークダウンコンテンツ
            
        Returns:
            クリーニングされたコンテンツ
        """
        try:
            lines = content.split('\n')
            result_lines = []
            in_comment = False
            
            for line in lines:
                # HTMLコメント開始
                if '<!--' in line:
                    in_comment = True
                    continue
                
                # HTMLコメント終了
                if '-->' in line:
                    in_comment = False
                    continue
                
                # コメント内はスキップ
                if in_comment:
                    continue
                
                # 空行が連続する場合は1つだけにする
                if line.strip() == '':
                    if result_lines and result_lines[-1].strip() == '':
                        continue
                
                result_lines.append(line)
            
            # 先頭と末尾の空行を削除
            while result_lines and result_lines[0].strip() == '':
                result_lines.pop(0)
            
            while result_lines and result_lines[-1].strip() == '':
                result_lines.pop()
            
            cleaned_content = '\n'.join(result_lines)
            
            logger.debug(f"【記事クリーンアップ完了】")
            logger.debug(f"  元の文字数: {len(content)}")
            logger.debug(f"  処理後の文字数: {len(cleaned_content)}")
            logger.debug(f"  先頭100文字: {cleaned_content[:100]}...")
            
            return cleaned_content
            
        except Exception as e:
            logger.warning(f"記事クリーンアップエラー: {e}")
            return content


# ============================================================================
# TaskTypeAnalyzer: タスクタイプ分析クラス
# ============================================================================

class TaskTypeAnalyzer:
    """タスク内容からタイプを判定
    
    タスクの説明文を解析して、適切なタスクタイプを返す。
    """

    @staticmethod
    def analyze(description: str) -> str:
        """タスク内容からタイプを判定
        
        Args:
            description: タスク説明文
            
        Returns:
            タスクタイプ文字列
        """
        description_lower = description.lower()
        
        # 新しい判定ルールを追加
        if 'polylang' in description_lower and '言語' in description_lower:
            return 'edit_post'
        
        if '投稿' in description and '探して' in description and (
            '変更' in description or '編集' in description or '書き換え' in description
        ):
            return 'edit_post'
        
        if 'プラグイン' in description and (
            '変更' in description or '設定' in description
        ) and 'インストール' not in description:
            return 'plugin_settings'
        
        if 'プラグイン' in description and 'インストール' in description:
            return 'plugin_install'
        
        if 'テーマ' in description or 'theme' in description_lower:
            return 'theme_change'
        
        if '設定' in description or 'setting' in description_lower:
            return 'setting_change'
        
        if ('投稿' in description or '記事' in description or 'post' in description_lower) and (
            '作成' in description or '保存' in description
        ):
            return 'content_create'
        
        if 'テスト' in description or 'test' in description_lower:
            return 'test_functionality'
        
        return 'generic'


# ============================================================================
# WordPressConfig: WordPress設定クラス
# ============================================================================

class WordPressConfig:
    """WordPress設定クラス
    
    WordPress関連の設定値を一元管理する。
    - WordPress URL
    - Polylang言語コード
    - ACFフィールドタイプ
    - 推奨プラグイン
    - M&A案件デフォルトフィールド
    - FacetWPデフォルト設定
    """
    
    # WordPress URLの設定(実際のサイトURLに変更してください)
    WORDPRESS_URL = "https://your-site.com"
    
    # Polylang言語コード定義
    POLYLANG_LANGS = {
        'ja': 'ja',           # 日本語
        'en': 'en',           # 英語
        'ru': 'ru',           # ロシア語
        'uz': 'uz_UZ',        # ウズベク語
        'zh': 'zh_CN',        # 中国語(簡体字)
        'ko': 'ko_KR',        # 韓国語
        'tr': 'tr_TR'         # トルコ語
    }
    
    # ACFフィールドタイプ定義
    ACF_FIELD_TYPES = {
        # テキスト系
        'text': 'テキスト(1行)',
        'textarea': 'テキストエリア(複数行)',
        'number': '数値',
        'email': 'メールアドレス',
        'url': 'URL',
        'password': 'パスワード',
        
        # 選択系
        'select': 'セレクトメニュー',
        'checkbox': 'チェックボックス',
        'radio': 'ラジオボタン',
        'true_false': '真偽値',
        
        # 日付時刻系
        'date_picker': '日付選択',
        'date_time_picker': '日付時刻選択',
        'time_picker': '時刻選択',
        
        # ファイル系
        'file': 'ファイル',
        'image': '画像',
        'gallery': 'ギャラリー',
        
        # リレーション系
        'post_object': '投稿オブジェクト',
        'relationship': 'リレーションシップ',
        'taxonomy': 'タクソノミー',
        'user': 'ユーザー',
        
        # レイアウト系
        'repeater': 'リピーター',
        'flexible_content': 'フレキシブルコンテンツ',
        'group': 'グループ',
        
        # その他
        'wysiwyg': 'WYSIWYGエディタ',
        'oembed': 'oEmbed',
        'google_map': 'Googleマップ',
        'color_picker': 'カラーピッカー'
    }
    
    # WordPressプラグイン定義
    WORDPRESS_PLUGINS = {
        # 必須プラグイン
        'required': [
            {
                'name': 'Advanced Custom Fields PRO',
                'slug': 'advanced-custom-fields-pro',
                'version': '6.2+',
                'purpose': 'カスタムフィールド管理',
                'priority': 'critical'
            },
            {
                'name': 'Custom Post Type UI',
                'slug': 'custom-post-type-ui',
                'version': '1.15+',
                'purpose': 'カスタム投稿タイプ管理',
                'priority': 'critical'
            },
            {
                'name': 'Polylang Pro',
                'slug': 'polylang-pro',
                'version': '3.5+',
                'purpose': '多言語対応',
                'priority': 'critical'
            }
        ],
        
        # 推奨プラグイン(検索強化)
        'search': [
            {
                'name': 'FacetWP',
                'slug': 'facetwp',
                'purpose': '絞り込み検索',
                'priority': 'high'
            },
            {
                'name': 'Relevanssi',
                'slug': 'relevanssi',
                'purpose': '検索精度向上',
                'priority': 'high'
            },
            {
                'name': 'SearchWP',
                'slug': 'searchwp',
                'purpose': '検索機能強化',
                'priority': 'medium'
            }
        ],
        
        # 推奨プラグイン(ユーザー管理)
        'user_management': [
            {
                'name': 'User Role Editor',
                'slug': 'user-role-editor',
                'purpose': 'ユーザーロール管理',
                'priority': 'high'
            },
            {
                'name': 'Members',
                'slug': 'members',
                'purpose': '権限管理',
                'priority': 'medium'
            }
        ],
        
        # 推奨プラグイン(セキュリティ)
        'security': [
            {
                'name': 'Wordfence Security',
                'slug': 'wordfence',
                'purpose': '総合セキュリティ',
                'priority': 'high'
            },
            {
                'name': 'iThemes Security',
                'slug': 'ithemes-security-pro',
                'purpose': 'セキュリティ強化',
                'priority': 'medium'
            }
        ],
        
        # 推奨プラグイン(パフォーマンス)
        'performance': [
            {
                'name': 'WP Rocket',
                'slug': 'wp-rocket',
                'purpose': 'キャッシュ・最適化',
                'priority': 'high'
            },
            {
                'name': 'Autoptimize',
                'slug': 'autoptimize',
                'purpose': 'CSS/JS最適化',
                'priority': 'medium'
            }
        ]
    }
    
    # M&A案件デフォルトフィールド設定
    MA_CASE_DEFAULT_FIELDS = {
        'case_id': {
            'type': 'text',
            'label': '案件ID',
            'required': True
        },
        'ma_scheme': {
            'type': 'select',
            'label': 'M&Aスキーム',
            'choices': ['株式譲渡', '事業譲渡', '合併', '会社分割'],
            'required': True
        },
        'desired_price': {
            'type': 'number',
            'label': '希望価格',
            'min': 0,
            'step': 1000000,
            'required': False
        },
        'industry_category': {
            'type': 'taxonomy',
            'label': '業種',
            'taxonomy': 'industry_category',
            'required': True
        },
        'region': {
            'type': 'taxonomy',
            'label': '地域',
            'taxonomy': 'region',
            'required': True
        },
        'established_year': {
            'type': 'number',
            'label': '設立年',
            'min': 1900,
            'max': 2025,
            'required': False
        },
        'employees': {
            'type': 'number',
            'label': '従業員数',
            'min': 0,
            'required': False
        },
        'annual_revenue': {
            'type': 'number',
            'label': '年商',
            'min': 0,
            'required': False
        },
        'annual_profit': {
            'type': 'number',
            'label': '年間利益',
            'required': False
        },
        'reason_for_sale': {
            'type': 'textarea',
            'label': '売却理由',
            'required': False
        },
        'strengths': {
            'type': 'textarea',
            'label': '強み',
            'required': False
        }
    }
    
    # FacetWPデフォルト設定
    FACETWP_DEFAULT_FACETS = [
        {
            'name': '業種フィルター',
            'type': 'checkboxes',
            'source': 'tax/industry_category',
            'label': '業種で絞り込む'
        },
        {
            'name': '価格帯フィルター',
            'type': 'slider',
            'source': 'cf/desired_price',
            'label': '希望価格',
            'min': 0,
            'max': 1000000000,
            'step': 10000000,
            'format': '¥{value}'
        },
        {
            'name': '地域フィルター',
            'type': 'dropdown',
            'source': 'tax/region',
            'label': '地域で絞り込む'
        },
        {
            'name': '従業員数フィルター',
            'type': 'slider',
            'source': 'cf/employees',
            'label': '従業員数',
            'min': 0,
            'max': 1000,
            'step': 10
        }
    ]


# ============================================================================
# TaskRouter: タスク振り分けクラス
# ============================================================================

class TaskRouter:
    """タスクの振り分けを行うユーティリティクラス
    
    タスクの内容を解析して、適切なタイプ(M&A/記事生成/レビュー/デフォルト)を判定する。
    """
    
    # M&A関連の強力なキーワード
    MA_STRONG_KEYWORDS = [
        'custom post type', 'カスタム投稿タイプ', 'cpt',
        'acf設定', 'acf', 'カスタムフィールド', 'custom field',
        'taxonomy', 'タクソノミー', 'カテゴリ作成',
        'm&a案件', 'ma_case', 'ma case',
        '企業検索', '案件管理', '案件投稿',
        'facetwp', 'facet', '絞り込み検索',
        'user role', 'ユーザーロール', '権限管理'
    ]
    
    # 記事生成関連のキーワード
    CONTENT_KEYWORDS = [
        '記事作成', '記事執筆', 'article', 'content creation',
        '【日本語】', '【英語】', '【ロシア語】', '【ウズベク語】',
        '【中国語】', '【韓国語】', '【トルコ語】',
        'ブログ', 'blog post', 'seo記事'
    ]
    
    # 記事生成系エージェント
    CONTENT_AGENTS = [
        'writer', 'writer_ja', 'writer_en', 'writer_ru',
        'writer_uz', 'writer_zh', 'writer_ko', 'writer_tr',
        'content'
    ]
    
    # M&A関連パラメータキー
    MA_PARAMETER_KEYS = [
        'cpt_slug', 'cpt_labels', 'cpt_supports',
        'acf_field_group_name', 'acf_fields', 'acf_location_rules',
        'taxonomy_slug', 'taxonomy_labels', 'taxonomy_post_types',
        'facets', 'role_slug', 'role_name'
    ]
    
    # 記事生成関連パラメータキー
    CONTENT_PARAMETER_KEYS = [
        'language', 'polylang_lang', 'seo_keywords',
        'target_audience', 'target_url', 'article_type'
    ]
    
    @staticmethod
    def determine_task_type(task: dict) -> str:
        """タスクのタイプを判定
        
        Args:
            task: タスク辞書
            
        Returns:
            'ma' - M&A/企業検索タスク
            'content' - 記事生成タスク
            'review' - レビュータスク
            'default' - その他のタスク
        """
        description = task.get('description', '').lower()
        agent = task.get('required_role', '').lower()
        parameters = task.get('parameters', {})
        
        # 1. レビュータスクの判定(最優先)
        if agent == 'review' or 'review_target_task_id' in parameters:
            return 'review'
        
        # 2. M&A関連タスクの判定
        # 2-1. 強力なキーワードマッチング
        if any(keyword in description for keyword in TaskRouter.MA_STRONG_KEYWORDS):
            logger.debug(f"M&Aタスク判定: キーワードマッチ")
            return 'ma'
        
        # 2-2. パラメータ判定
        if any(key in parameters for key in TaskRouter.MA_PARAMETER_KEYS):
            logger.debug(f"M&Aタスク判定: パラメータマッチ")
            return 'ma'
        
        # 2-3. エージェントと説明の組み合わせ
        if agent in ['wordpress', 'plugin']:
            # WordPressエージェントで特定の機能
            if any(word in description for word in ['設定', '作成', 'setup', 'configure']):
                logger.debug(f"M&Aタスク判定: WordPressエージェント+設定")
                return 'ma'
        
        # 3. 記事生成タスクの判定
        # 3-1. エージェント判定(最も確実)
        if agent in TaskRouter.CONTENT_AGENTS:
            logger.debug(f"記事生成タスク判定: エージェントマッチ")
            return 'content'
        
        # 3-2. パラメータ判定
        if any(key in parameters for key in TaskRouter.CONTENT_PARAMETER_KEYS):
            logger.debug(f"記事生成タスク判定: パラメータマッチ")
            return 'content'
        
        # 3-3. キーワード判定
        if any(keyword in description for keyword in TaskRouter.CONTENT_KEYWORDS):
            logger.debug(f"記事生成タスク判定: キーワードマッチ")
            return 'content'
        
        # 4. その他のタスク
        logger.debug(f"デフォルトタスク判定")
        return 'default'
    
    @staticmethod
    def is_ma_task(task: dict) -> bool:
        """M&A関連タスクかどうかを判定
        
        Args:
            task: タスク辞書
            
        Returns:
            M&Aタスクの場合True
        """
        return TaskRouter.determine_task_type(task) == 'ma'
    
    @staticmethod
    def is_content_task(task: dict) -> bool:
        """記事生成タスクかどうかを判定
        
        Args:
            task: タスク辞書
            
        Returns:
            記事生成タスクの場合True
        """
        return TaskRouter.determine_task_type(task) == 'content'
    
    @staticmethod
    def is_review_task(task: dict) -> bool:
        """レビュータスクかどうかを判定
        
        Args:
            task: タスク辞書
            
        Returns:
            レビュータスクの場合True
        """
        return TaskRouter.determine_task_type(task) == 'review'


# ============================================================================
# グローバルインスタンスの作成
# ============================================================================

# グローバルインスタンスを作成
wp_config = WordPressConfig()
task_router = TaskRouter()


# ============================================================================
# PluginNameExtractor: プラグイン名抽出クラス
# ============================================================================

class PluginNameExtractor:
    """タスク説明からプラグイン名を抽出"""

    @staticmethod
    def extract(description: str) -> str:
        """タスク説明からプラグイン名を抽出
        
        Args:
            description: タスク説明文
            
        Returns:
            抽出されたプラグイン名
        """
        # 「」『』で囲まれた部分を抽出
        match = re.search(r'[「『](.+?)[」』]', description)
        if match:
            return match.group(1)
        
        # 見つからない場合は説明の先頭50文字を返す
        return description[:50]


# ============================================================================
# HTMLCleaner: HTMLクリーニングクラス
# ============================================================================

class HTMLCleaner:
    """HTML記事のクリーニングユーティリティ
    
    WordPress投稿用にHTMLを最適化・クリーニングする機能を提供。
    - 不正なネストの修正
    - WordPressクラスの追加
    - Gutenbergブロック対応
    - タイトル・本文の分離
    """
        
    @staticmethod
    def clean_html_content(html_content: str) -> str:
        """HTMLコンテンツをクリーニング - WordPress用に最適化
        
        Args:
            html_content: 元のHTMLコンテンツ
            
        Returns:
            クリーニングされたHTML
        """
        try:
            logger.info("WordPress用にHTMLをクリーニング中...")
            
            # 基本的なクリーニング
            cleaned = html_content
            
            # 1. 不正なネストを修正
            cleaned = re.sub(r'<p>\s*<div', '<div', cleaned)
            cleaned = re.sub(r'</div>\s*</p>', '</div>', cleaned)
            cleaned = re.sub(r'<p>\s*</p>', '', cleaned)
            
            # 2. 適切な改行を追加(読みやすさのため)
            cleaned = re.sub(r'></(h1|h2|h3|h4|h5|h6|p|div|section|article)>', r'></\1>\n\n', cleaned)
            cleaned = re.sub(r'<(h1|h2|h3|h4|h5|h6|p|div|section|article)([^>]*)>', r'<\1\2>\n', cleaned)
            
            # 3. 連続する空白を単一スペースに
            cleaned = re.sub(r'\s+', ' ', cleaned)
            
            # 4. タグ間の空白を正規化
            cleaned = re.sub(r'>\s+<', '> <', cleaned)
            
            # 5. WordPress用のクラスを追加
            cleaned = HTMLCleaner._add_wordpress_classes(cleaned)
            
            # 6. セマンティックな構造を確認
            lines = cleaned.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # 明らかに不正な行をスキップ
                if line in ['<p><div', '</div></p>']:
                    continue
                    
                cleaned_lines.append(line)
            
            cleaned = '\n'.join(cleaned_lines)
            
            logger.info(f"HTMLクリーニング完了: {len(html_content)} → {len(cleaned)}文字")
            return cleaned
            
        except Exception as e:
            logger.error(f"HTMLクリーニングエラー: {e}")
            return html_content
    
    @staticmethod
    def _add_wordpress_classes(html_content: str) -> str:
        """WordPress用のクラスを追加してスタイルを適用
        
        Args:
            html_content: 元のHTMLコンテンツ
            
        Returns:
            WordPressクラスが追加されたHTML
        """
        try:
            # 見出しにWordPressのクラスを追加
            html_content = re.sub(r'<h1([^>]*)>', r'<h1\1 class="wp-block-heading has-large-font-size">', html_content)
            html_content = re.sub(r'<h2([^>]*)>', r'<h2\1 class="wp-block-heading has-large-font-size">', html_content)
            html_content = re.sub(r'<h3([^>]*)>', r'<h3\1 class="wp-block-heading has-medium-font-size">', html_content)
            
            # 段落にクラスを追加
            html_content = re.sub(r'<p([^>]*)>', r'<p\1 class="wp-block-paragraph">', html_content)
            
            # セクションにクラスを追加
            html_content = re.sub(r'<section([^>]*)>', r'<section\1 class="wp-block-group">', html_content)
            html_content = re.sub(r'<article([^>]*)>', r'<article\1 class="wp-block-group">', html_content)
            html_content = re.sub(r'<div class="article-meta"', r'<div class="wp-block-group article-meta"', html_content)
            html_content = re.sub(r'<div class="intro"', r'<div class="wp-block-group intro"', html_content)
            html_content = re.sub(r'<div class="main-content"', r'<div class="wp-block-group main-content"', html_content)
            
            return html_content
            
        except Exception as e:
            logger.error(f"WordPressクラス追加エラー: {e}")
            return html_content
        
    @staticmethod
    def validate_html_structure(html_content: str) -> bool:
        """HTML構造の基本的な検証
        
        Args:
            html_content: 検証するHTMLコンテンツ
            
        Returns:
            構造が正しい場合True
        """
        try:
            # 基本的なタグのバランスをチェック
            open_tags = len(re.findall(r'<(\w+)[^>]*>', html_content))
            close_tags = len(re.findall(r'</(\w+)>', html_content))
                
            # divタグのバランスを特別にチェック
            div_open = html_content.count('<div')
            div_close = html_content.count('</div>')
                
            logger.info(f"HTML構造検証: タグ{open_tags}/{close_tags}, div{div_open}/{div_close}")
                
            # divタグのバランスが取れているか
            if div_open != div_close:
                logger.warning(f"divタグのバランスが取れていません: {div_open} != {div_close}")
                return False
                    
            return True
                
        except Exception as e:
            logger.error(f"HTML検証エラー: {e}")
            return False
        
    @staticmethod
    def extract_title_from_html(html_content: str) -> Tuple[str, str]:
        """HTMLからタイトルと本文を分離
        
        Args:
            html_content: 元のHTMLコンテンツ
            
        Returns:
            (タイトル, クリーニングされたHTML本文)のタプル
        """
        try:
            logger.info("HTMLからタイトルを抽出中...")
                
            # 複数のパターンでタイトルを検索
            title_patterns = [
                r'<h1[^>]*>(.*?)</h1>',
                r'<title[^>]*>(.*?)</title>',
                r'<h2[^>]*>(.*?)</h2>',
                r'<h3[^>]*>(.*?)</h3>'
            ]
                
            for pattern in title_patterns:
                match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
                if match:
                    title_html = match.group(1)
                    # HTMLタグを除去してタイトルを取得
                    title = re.sub(r'<[^>]+>', '', title_html).strip()
                        
                    if title and len(title) > 5:  # 最低5文字以上
                        logger.info(f"✅ HTMLからタイトル抽出成功: {title}")
                            
                        # タイトル部分を除去した本文を作成
                        body = re.sub(pattern, '', html_content, flags=re.IGNORECASE | re.DOTALL)
                        body = body.strip()
                            
                        # 本文をクリーニング
                        body = HTMLCleaner.clean_html_content(body)
                            
                        return title, body
                
            logger.warning("❌ HTMLからタイトルを抽出できませんでした")
            return "タイトル不明", HTMLCleaner.clean_html_content(html_content)
                
        except Exception as e:
            logger.error(f"HTMLタイトル抽出エラー: {e}")
            return "タイトル抽出エラー", html_content
        
    @staticmethod
    def prepare_html_for_wordpress(html_content: str) -> Tuple[str, str]:
        """WordPress用にHTMLを準備(改善版)
        
        Args:
            html_content: 元のHTMLコンテンツ
            
        Returns:
            (タイトル, WordPress用HTML本文)のタプル
        """
        try:
            logger.info("WordPress用にHTMLを準備中...")
            
            # タイトルと本文を分離
            title, body = HTMLCleaner.extract_title_from_html(html_content)
            
            # HTMLをWordPress用に最適化
            wp_html = HTMLCleaner._optimize_for_wordpress_gutenberg(body)
            
            logger.info(f"✅ WordPress用HTML準備完了: タイトル='{title}', 本文={len(wp_html)}文字")
            return title, wp_html
            
        except Exception as e:
            logger.error(f"WordPress用HTML準備エラー: {e}")
            return "HTML処理エラー", html_content
        
    @staticmethod
    def _optimize_for_wordpress(html_content: str) -> str:
        """WordPress用にHTMLを最適化
        
        Args:
            html_content: 元のHTMLコンテンツ
            
        Returns:
            最適化されたHTML
        """
        try:
            optimized = html_content
                
            # 1. セマンティックなタグを維持
            # 2. 不正なネストを修正
            optimized = re.sub(r'<p>\s*<(div|section|article)', r'<\1', optimized)
            optimized = re.sub(r'</(div|section|article)>\s*</p>', r'</\1>', optimized)
                
            # 3. 空の段落を削除
            optimized = re.sub(r'<p>\s*</p>', '', optimized)
                
            # 4. 連続する改行を整理
            optimized = re.sub(r'\n\s*\n', '\n\n', optimized)
                
            # 5. 基本的なHTML構造を確保
            if not optimized.strip().startswith('<'):
                optimized = f'<div class="article-content">\n{optimized}\n</div>'
                
            return optimized
                
        except Exception as e:
            logger.error(f"HTML最適化エラー: {e}")
            return html_content
    
    @staticmethod
    def _optimize_for_wordpress_gutenberg(html_content: str) -> str:
        """Gutenbergエディタ用にHTMLを最適化
        
        Args:
            html_content: 元のHTMLコンテンツ
            
        Returns:
            Gutenberg最適化されたHTML
        """
        try:
            # まず基本クリーニング
            optimized = HTMLCleaner.clean_html_content(html_content)
            
            # Gutenbergブロック用の構造を追加
            optimized = HTMLCleaner._wrap_in_gutenberg_blocks(optimized)
            
            # 最終的な改行調整
            optimized = re.sub(r'\n\s*\n', '\n\n', optimized)
            optimized = optimized.strip()
            
            return optimized
            
        except Exception as e:
            logger.error(f"Gutenberg最適化エラー: {e}")
            return html_content
    
    @staticmethod
    def _wrap_in_gutenberg_blocks(html_content: str) -> str:
        """
        HTMLをGutenbergブロックでラップ
        """
        try:
            blocks = []
            lines = html_content.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 見出しブロック
                if line.startswith('<h1') or line.startswith('<h2') or line.startswith('<h3'):
                    blocks.append(f'<!-- wp:heading -->\n{line}\n<!-- /wp:heading -->')
                
                # 段落ブロック
                elif line.startswith('<p'):
                    blocks.append(f'<!-- wp:paragraph -->\n{line}\n<!-- /wp:paragraph -->')
                
                # グループブロック(セクション、記事メタなど)
                elif line.startswith('<section') or line.startswith('<article') or line.startswith('<div class="wp-block-group"'):
                    if line.startswith('</section') or line.startswith('</article') or line.startswith('</div'):
                        blocks.append(line)
                    else:
                        blocks.append(f'<!-- wp:group -->\n{line}')
                
                # その他の要素
                else:
                    blocks.append(line)
            
            # 閉じタグの処理
            result = []
            for block in blocks:
                if any(tag in block for tag in ['</section>', '</article>', '</div>']):
                    result.append(f'{block}\n<!-- /wp:group -->')
                else:
                    result.append(block)
            
            return '\n\n'.join(result)
            
        except Exception as e:
            logger.error(f"Gutenbergブロックラップエラー: {e}")
            return html_content
        
    @staticmethod
    def is_valid_html(html_content: str) -> bool:
        """
        HTMLが有効かチェック
        """
        try:
            # 基本的なチェック
            if not html_content or len(html_content.strip()) < 10:
                return False
                
            # HTMLタグの存在をチェック
            if '<' not in html_content or '>' not in html_content:
                return False
                
            # 基本的なタグのバランスをチェック
            return HTMLCleaner.validate_html_structure(html_content)
                
        except Exception as e:
            logger.error(f"HTML有効性チェックエラー: {e}")
            return False