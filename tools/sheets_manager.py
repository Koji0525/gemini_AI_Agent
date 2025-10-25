# sheets_manager.py
"""Google Sheets管理クラス(拡張版: Google Drive対応)"""
import gspread
from google.oauth2.service_account import Credentials
from google.auth import default
from google.auth.transport.requests import Request
from pathlib import Path
from typing import List, Dict, Optional
import logging
import re

from configuration.config_utils import config, ErrorHandler

logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    """Google Sheets管理クラス(拡張版: Google Drive対応)"""
    
    # Google API スコープの定義
    GOOGLE_SHEETS_SCOPE = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    def __init__(self, spreadsheet_id: str, service_account_file: Optional[str] = None):
        self.spreadsheet_id = spreadsheet_id
        self.service_account_file = service_account_file
        self.gc: Optional[gspread.Client] = None
        self.drive_service = None  # Google Drive API用
        self.setup_client()
    
    def setup_client(self) -> None:
        """Google Sheets クライアントの設定"""
        try:
            # === パート1: サービスアカウント認証の試行 ===
            logger.info("🔐 Google Sheetsクライアント設定中...")
            
            if self.service_account_file and Path(self.service_account_file).exists():
                # サービスアカウント認証
                creds = Credentials.from_service_account_file(
                    self.service_account_file, scopes=self.GOOGLE_SHEETS_SCOPE)
                self.gc = gspread.authorize(creds)
                
                # Google Drive API用のサービスも初期化
                self._setup_drive_service(creds)
                
                logger.info("✅ サービスアカウントで Google Sheets に接続しました")
            else:
                # === パート2: デフォルト認証へのフォールバック ===
                logger.info("🔄 サービスアカウントなし、デフォルト認証を試行...")
                
                try:
                    creds, project = default(scopes=self.GOOGLE_SHEETS_SCOPE)
                    if creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    self.gc = gspread.authorize(creds)
                    
                    # Google Drive API用
                    self._setup_drive_service(creds)
                    
                    logger.info("✅ デフォルト認証で Google Sheets に接続しました")
                except Exception as e:
                    logger.warning(f"⚠️ デフォルト認証に失敗しました: {e}")
                    logger.warning("サービスアカウントファイルが必要です")
                    self.gc = None
                    
        except Exception as e:
            ErrorHandler.log_error(e, "Google Sheets クライアント設定")
            self.gc = None
    
    def _setup_drive_service(self, creds):
        """Google Drive APIサービスを初期化"""
        try:
            from googleapiclient.discovery import build
            self.drive_service = build('drive', 'v3', credentials=creds)
            logger.info("✅ Google Drive APIサービスを初期化しました")
        except Exception as e:
            logger.warning(f"⚠️ Google Drive APIサービスの初期化に失敗: {e}")
            self.drive_service = None
    
    def _ensure_client(self) -> None:
        """クライアントが初期化されているか確認"""
        if not self.gc:
            raise Exception("Google Sheets クライアントが初期化されていません。サービスアカウントファイルを設定してください。")
    
    async def update_task_status(self, task_id: int, status: str, sheet_name: str = "pm_tasks") -> bool:
        """
        タスクのステータスを更新（ロバスト性向上版 + 超詳細ログ）
        
        Args:
            task_id: タスクID
            status: 新しいステータス
            sheet_name: シート名
            
        Returns:
            bool: 更新成功フラグ
        """
        try:
            logger.info("=" * 70)
            logger.info(f"🔄 ステータス更新処理開始")
            logger.info(f"   タスクID: {task_id}")
            logger.info(f"   新ステータス: {status}")
            logger.info(f"   対象シート: {sheet_name}")
            logger.info("=" * 70)
            
            # === パート1: クライアントとシートの準備 ===
            logger.info("📋 [ステップ1] Google Sheets クライアント確認中...")
            self._ensure_client()
            logger.info("✅ クライアント確認完了")
            
            logger.info(f"📋 [ステップ2] スプレッドシート接続中 (ID: {self.spreadsheet_id[:20]}...)")
            sheet = self.gc.open_by_key(self.spreadsheet_id)
            logger.info("✅ スプレッドシート接続成功")
            
            logger.info(f"📋 [ステップ3] シート '{sheet_name}' を開いています...")
            task_sheet = sheet.worksheet(sheet_name)
            logger.info("✅ シートを開きました")
            
            # 全データを取得
            logger.info("📋 [ステップ4] シートデータ取得中...")
            all_data = task_sheet.get_all_values()
            logger.info(f"✅ データ取得完了: {len(all_data)}行")
            
            if len(all_data) <= 1:
                logger.warning(f"⚠️ タスクシート '{sheet_name}' にデータがありません（ヘッダーのみ）")
                return False
            
            # === パート2: ヘッダー解析と列インデックスの特定 ===
            logger.info("📋 [ステップ5] ヘッダー解析中...")
            headers = all_data[0]
            logger.info(f"   ヘッダー内容: {headers}")
            
            task_id_col = None
            status_col = None
            
            for i, header in enumerate(headers):
                header_lower = header.lower().strip()
                logger.debug(f"   列{i+1}: '{header}' (小文字: '{header_lower}')")
                
                if 'task_id' in header_lower or header_lower == 'id':
                    task_id_col = i
                    logger.info(f"✅ タスクID列を検出: 列{i+1} ('{header}')")
                elif 'status' in header_lower:
                    status_col = i
                    logger.info(f"✅ ステータス列を検出: 列{i+1} ('{header}')")
            
            # タスクID列が見つからない場合のフォールバック
            if task_id_col is None:
                task_id_col = 0
                logger.warning(f"⚠️ タスクID列が見つかりません。デフォルトで列1を使用します")
            
            # ステータス列が見つからない場合は追加
            if status_col is None:
                status_col = len(headers)
                logger.warning(f"⚠️ ステータス列が見つかりません。新規追加します: 列{status_col + 1}")
                try:
                    task_sheet.update_cell(1, status_col + 1, 'status')
                    logger.info(f"✅ ステータス列を追加しました")
                except Exception as e:
                    logger.error(f"❌ ステータス列追加エラー: {e}")
                    return False
            
            # === パート3: 強化版タスク検索 ===
            logger.info(f"📋 [ステップ6] タスクID '{task_id}' を検索中...")
            logger.info(f"   検索対象列: 列{task_id_col + 1}")
            logger.info(f"   検索対象行数: {len(all_data) - 1}行（ヘッダー除く）")
            
            task_id_str = str(task_id).strip()
            task_found = False
            row_index = None
            
            # 詳細な検索実行
            available_ids = []
            for row_idx, row in enumerate(all_data[1:], start=2):
                if len(row) > task_id_col:
                    cell_value = str(row[task_id_col]).strip()
                    available_ids.append(cell_value)
                    
                    logger.debug(f"   行{row_idx}: ID='{cell_value}' (比較対象: '{task_id_str}')")
                    
                    if cell_value == task_id_str:
                        row_index = row_idx
                        task_found = True
                        logger.info(f"✅ タスクを発見: 行{row_idx}")
                        break
            
            if not task_found:
                # 詳細なデバッグ情報を出力
                logger.error(f"❌ タスクID '{task_id_str}' が見つかりません")
                logger.error(f"")
                logger.error(f"🔍 検索詳細:")
                logger.error(f"   検索したID: '{task_id_str}' (型: {type(task_id).__name__})")
                logger.error(f"   検索した列: 列{task_id_col + 1}")
                logger.error(f"   総タスク数: {len(all_data) - 1}")
                logger.error(f"")
                logger.error(f"📋 シート内の利用可能なタスクID:")
                for i, aid in enumerate(available_ids[:10], 1):
                    logger.error(f"   {i}. '{aid}'")
                if len(available_ids) > 10:
                    logger.error(f"   ... 他 {len(available_ids) - 10}件")
                logger.error(f"")
                logger.error(f"💡 確認事項:")
                logger.error(f"   1. タスクID '{task_id}' が pm_tasks シートに存在するか？")
                logger.error(f"   2. タスクIDの列が正しいか？（現在: 列{task_id_col + 1}）")
                logger.error(f"   3. タスクIDに余分な空白や特殊文字が含まれていないか？")
                
                return False
            
            # === パート4: ステータス更新 ===
            logger.info(f"📋 [ステップ7] ステータス更新実行中...")
            logger.info(f"   対象セル: 行{row_index}, 列{status_col + 1}")
            logger.info(f"   新しい値: '{status}'")
            
            try:
                # Google Sheets API でセルを更新
                task_sheet.update_cell(row_index, status_col + 1, status)
                logger.info(f"✅ API呼び出し成功")
                
                # 更新後の検証（オプション）
                import time
                time.sleep(0.5)  # API反映待ち
                
                updated_value = task_sheet.cell(row_index, status_col + 1).value
                logger.info(f"🔍 更新後の値: '{updated_value}'")
                
                if updated_value == status:
                    logger.info(f"✅ ステータス更新確認完了")
                    logger.info("=" * 70)
                    logger.info(f"🎉 タスク {task_id} のステータスを '{status}' に更新しました（行 {row_index}）")
                    logger.info("=" * 70)
                    return True
                else:
                    logger.warning(f"⚠️ 更新値が一致しません: 期待='{status}', 実際='{updated_value}'")
                    return False
                    
            except Exception as api_error:
                logger.error(f"❌ Google Sheets API エラー: {api_error}")
                logger.error(f"")
                logger.error(f"💡 考えられる原因:")
                logger.error(f"   1. サービスアカウントの権限不足")
                logger.error(f"   2. スプレッドシートが編集ロックされている")
                logger.error(f"   3. APIクォータ超過")
                logger.error(f"   4. ネットワーク接続の問題")
                import traceback
                logger.error(traceback.format_exc())
                return False
            
        except Exception as e:
            logger.error(f"❌ タスクステータス更新エラー: {e}")
            logger.error(f"")
            logger.error(f"🔧 エラーコンテキスト:")
            logger.error(f"   タスクID: {task_id}")
            logger.error(f"   ステータス: {status}")
            logger.error(f"   シート: {sheet_name}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    async def find_available_task_id(self) -> Optional[str]:
        """利用可能なタスクIDを検索（ログ削減版）"""
        try:
            # ログレベルを一時的にERRORに
            original_level = logger.level
            logger.setLevel(logging.ERROR)
            
            # タスクID検索
            task_ids = await self._search_task_ids()
            
            # ログレベルを戻す
            logger.setLevel(original_level)
            
            if task_ids:
                logger.info(f"✅ 利用可能タスク: {len(task_ids)}件")
                return task_ids[0]
            else:
                logger.warning("⚠️ 利用可能タスクなし")
                return None
        
        except Exception as e:
            logger.setLevel(original_level)
            logger.error(f"❌ タスクID検索エラー: {e}")
            return None
    
    async def _search_task_ids(self) -> List[str]:
        """内部検索（ログなし）"""
        try:
            # 既存の検索ロジック
            all_values = self.ws.get_all_values()
            
            # フィルタリング
            valid_ids = []
            for row in all_values[1:]:  # ヘッダー除外
                if len(row) >= 11:
                    task_id = row[0]
                    status = row[10]
                    
                    if task_id and task_id not in ['エージェント未登録', 'Review suggested']:
                        if status in ['pending', 'in_progress', '']:
                            valid_ids.append(task_id)
            
            return valid_ids
        
        except Exception as e:
            return []

    async def load_tasks_from_sheet(self, sheet_name: str = "pm_tasks") -> List[Dict]:
        """指定されたシートからタスクを読み込む（エラー修正版）"""
        try:
            # === パート1: シート接続と基本設定 ===
            self._ensure_client()
        
            sheet = self.gc.open_by_key(self.spreadsheet_id)
        
            try:
                task_sheet = sheet.worksheet(sheet_name)
            except gspread.exceptions.WorksheetNotFound:
                logger.error(f"❌ シート '{sheet_name}' が見つかりません")
                return []
        
            # === パート2: データ取得方法の試行（複数方式） ===
            logger.info(f"📥 シート '{sheet_name}' からデータ取得中...")
            
            try:
                # 方法1: get_all_records() を試す
                records = task_sheet.get_all_records()
                logger.info(f"✅ get_all_records() でデータ取得成功: {len(records)}行")
            except Exception as e:
                logger.warning(f"⚠️ get_all_records() 失敗: {e}")
                logger.info("🔧 代替方法でデータを取得します...")
                
                # 方法2: 生データを取得して手動で処理
                all_values = task_sheet.get_all_values()
                
                if len(all_values) <= 1:
                    logger.info("📭 データ行がありません")
                    return []
                
                # ヘッダー行を取得
                headers = all_values[0]
                logger.info(f"📋 ヘッダー: {headers}")
                
                # データ行を処理
                records = []
                for i, row in enumerate(all_values[1:], start=2):
                    if not any(row):  # 空行をスキップ
                        continue
                    
                    record = {}
                    for j, header in enumerate(headers):
                        if j < len(row) and header:  # ヘッダーが空でない場合のみ
                            record[header] = row[j]
                        elif j < len(row):
                            record[f'column_{j+1}'] = row[j]  # 空ヘッダーの場合
                    
                    records.append(record)
                
                logger.info(f"✅ 代替方法でデータ取得成功: {len(records)}行")
        
            # === パート3: レコードからタスクオブジェクトへの変換 ===
            tasks = []
            for i, record in enumerate(records, start=2):
                # タスクIDの処理を改善
                task_id = str(record.get('task_id', '')).strip()
                if not task_id and 'task_id' not in record:
                    # 最初の列をタスクIDとして使用
                    first_col = list(record.values())[0] if record else ''
                    task_id = str(first_col).strip()
                
                task = {
                    'task_id': task_id,
                    'description': record.get('task_description', record.get('description', '')),
                    'required_role': record.get('required_role', ''),
                    'status': record.get('status', ''),
                    'priority': record.get('priority', 'medium'),
                    'estimated_time': record.get('estimated_time', ''),
                    'dependencies': record.get('dependencies', ''),
                    'created_at': record.get('created_at', ''),
                    'batch_id': record.get('batch_id', ''),
                    'review_target_task_id': record.get('review_target_task_id', ''),
                    'post_action': record.get('post_action', ''),
                    'language': record.get('language', ''),
                    'polylang_lang': record.get('polylang_lang', '')
                }
                
                # 基本的な検証
                if task['description'] and task['required_role']:
                    tasks.append(task)
        
            logger.info(f"📊 タスク読み込み: {len(tasks)}件（シート: {sheet_name}）")
            
            # === パート4: デバッグ情報と結果返却 ===
            # デバッグ情報
            if tasks:
                logger.info(f"📝 最初のタスク: {tasks[0].get('description', '')[:50]}...")
            else:
                logger.info("📭 読み込まれたタスクは0件です")
                
            return tasks
        
        except Exception as e:
            logger.error(f"❌ タスク読み込みエラー（シート: {sheet_name}）: {e}")
            return []

    async def save_task_output(self, output_data: Dict):
        """タスクの出力を保存"""
        try:
            # === パート1: クライアントとシートの準備 ===
            self._ensure_client()
        
            sheet = self.gc.open_by_key(self.spreadsheet_id)
        
            # === パート2: 出力シートの存在確認と作成 ===
            # 出力シートが存在するか確認
            try:
                output_sheet = sheet.worksheet("task_outputs")
            except gspread.exceptions.WorksheetNotFound:
                # シートが存在しない場合は作成
                logger.info("'task_outputs' シートを作成します")
                output_sheet = sheet.add_worksheet(title="task_outputs", rows=1000, cols=10)
                # ヘッダーを設定
                headers = ["task_id", "summary", "full_text", "screenshot", "timestamp"]
                output_sheet.append_row(headers)
        
            # === パート3: データの保存 ===
            # データを追加
            row = [
                output_data.get('task_id', ''),
                output_data.get('summary', ''),
                output_data.get('full_text', ''),
                output_data.get('screenshot', ''),
                output_data.get('timestamp', '')
            ]
            output_sheet.append_row(row)
        
            logger.info(f"✅ タスク出力を保存: {output_data.get('task_id', '')}")
            return True
        
        except Exception as e:
            ErrorHandler.log_error(e, "タスク出力保存")
            return False
    
    def save_result_to_sheet(self, results: List[Dict], mode: str = "text") -> None:
        """
        結果をスプレッドシートに保存
        
        Args:
            results: 結果のリスト
            mode: "text" または "image"
        """
        try:
            # === パート1: クライアントとシート名の準備 ===
            self._ensure_client()
            
            sheet = self.gc.open_by_key(self.spreadsheet_id)
            
            # 結果シート名を決定
            result_sheet_name = f"result_{mode}"
            
            # === パート2: シートの存在確認と作成 ===
            # シートが存在しない場合は作成
            try:
                result_sheet = sheet.worksheet(result_sheet_name)
            except gspread.exceptions.WorksheetNotFound:
                logger.info(f"シート '{result_sheet_name}' を作成します")
                result_sheet = sheet.add_worksheet(title=result_sheet_name, rows=1000, cols=10)
                
                # ヘッダーを設定
                headers = ['Index', 'Prompt', 'Status', 'Filename', 'Timestamp', 'Error', 'Mode']
                result_sheet.append_row(headers)
            
            # === パート3: 結果データの保存 ===
            # 結果を追加
            for result in results:
                row = [
                    result.get('index', ''),
                    result.get('prompt', '')[:100],  # プロンプトは最初の100文字
                    result.get('status', ''),
                    result.get('filename', ''),
                    result.get('timestamp', ''),
                    result.get('error', ''),
                    result.get('mode', mode)
                ]
                result_sheet.append_row(row)
            
            logger.info(f"✅ {len(results)}件の結果を '{result_sheet_name}' に保存しました")
            
        except Exception as e:
            ErrorHandler.log_error(e, "結果保存")
            logger.warning("結果の保存に失敗しましたが、処理を続行します")
    
    def extract_file_id_from_url(self, url: str) -> Optional[str]:
        """
        Google DriveのURLからファイルIDを抽出
        
        対応形式:
        - https://drive.google.com/file/d/FILE_ID/view
        - https://drive.google.com/open?id=FILE_ID
        - https://docs.google.com/document/d/FILE_ID/edit
        """
        # === パート1: 正規表現パターンの定義 ===
        patterns = [
            r'/file/d/([a-zA-Z0-9_-]+)',
            r'id=([a-zA-Z0-9_-]+)',
            r'/d/([a-zA-Z0-9_-]+)',
        ]
        
        # === パート2: パターンマッチングの実行 ===
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                file_id = match.group(1)
                logger.info(f"✅ ファイルIDを抽出: {file_id}")
                return file_id
        
        logger.warning(f"⚠️ URLからファイルIDを抽出できませんでした: {url}")
        return None
    
    def read_file_from_drive(self, file_id_or_url: str) -> Optional[str]:
        """
        Google Driveからファイルをダウンロードして読み込む（超詳細ログ版）
        
        Args:
            file_id_or_url: ファイルID または Google DriveのURL
            
        Returns:
            ファイルの内容（テキスト）、失敗時はNone
        """
        try:
            logger.info("="*60)
            logger.info("【Google Drive読み込み開始】")
            logger.info("="*60)
            
            # === パート1: Drive APIサービスの確認 ===
            logger.info("【切り分け1】Drive APIサービスを確認")
            if not self.drive_service:
                logger.error("❌ Google Drive APIサービスが初期化されていません")
                logger.error("  → サービスアカウント認証を確認してください")
                return None
            logger.info("✅ Drive APIサービス: 正常")
            
            # === パート2: 入力値の解析とファイルIDの抽出 ===
            logger.info("【切り分け2】入力値を解析")
            logger.info(f"  入力: {file_id_or_url[:100]}")
            
            if file_id_or_url.startswith('http'):
                logger.info("  → URL形式と判定")
                file_id = self.extract_file_id_from_url(file_id_or_url)
                if not file_id:
                    logger.error("❌ URLからファイルIDを抽出できませんでした")
                    return None
                logger.info(f"✅ ファイルID抽出成功: {file_id}")
            else:
                file_id = file_id_or_url
                logger.info(f"  → ファイルID形式: {file_id}")
            
            # === パート3: ファイルメタデータの取得 ===
            logger.info("【切り分け3】ファイルメタデータを取得")
            try:
                from googleapiclient.http import MediaIoBaseDownload
                import io
                
                file_metadata = self.drive_service.files().get(
                    fileId=file_id, 
                    fields='name,mimeType,size,permissions'
                ).execute()
                
                file_name = file_metadata.get('name', 'Unknown')
                mime_type = file_metadata.get('mimeType', '')
                file_size = file_metadata.get('size', '0')
                
                logger.info("✅ ファイルメタデータ取得成功")
                logger.info(f"  ファイル名: {file_name}")
                logger.info(f"  MIME Type: {mime_type}")
                logger.info(f"  サイズ: {file_size} bytes")
                
            except Exception as e:
                logger.error(f"❌ ファイルメタデータ取得エラー: {e}")
                logger.error("  考えられる原因:")
                logger.error("  - ファイルIDが間違っている")
                logger.error("  - サービスアカウントに権限がない")
                logger.error("  - ファイルが削除されている")
                return None
            
            # === パート4: ファイルのダウンロード ===
            logger.info("【切り分け4】ファイルをダウンロード")
            try:
                request = self.drive_service.files().get_media(fileId=file_id)
                
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                
                done = False
                chunk_count = 0
                while not done:
                    status, done = downloader.next_chunk()
                    chunk_count += 1
                    if status:
                        progress = int(status.progress() * 100)
                        logger.debug(f"  ⏳ チャンク{chunk_count}: {progress}%")
                
                logger.info(f"✅ ダウンロード完了: {chunk_count}チャンク")
                
            except Exception as e:
                logger.error(f"❌ ダウンロードエラー: {e}")
                return None
            
            # === パート5: バイトデータからテキストへの変換 ===
            logger.info("【切り分け5】バイトデータをテキストに変換")
            try:
                content = fh.getvalue().decode('utf-8')
                logger.info(f"✅ 変換成功: {len(content)}文字")
                logger.info(f"  先頭100文字: {content[:100]}...")
                
                # 内容の検証
                if len(content) < 10:
                    logger.warning(f"⚠️ 内容が短すぎます: {len(content)}文字")
                
                return content
                
            except UnicodeDecodeError as e:
                logger.error(f"❌ UTF-8デコードエラー: {e}")
                logger.error("  → ファイルがテキスト形式ではない可能性")
                return None
            except Exception as e:
                logger.error(f"❌ 変換エラー: {e}")
                return None
            
        except Exception as e:
            logger.error(f"❌ Google Driveファイル読み込みエラー: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_current_pc_id(self) -> int:
        """スプレッドシートのB12セルからPC_IDを読み取る"""
        try:
            # === パート1: シート接続とセル読み取り ===
            self._ensure_client()
            
            sheet = self.gc.open_by_key(self.spreadsheet_id)
            setting_sheet = sheet.worksheet("setting")
            
            pc_id_value = setting_sheet.cell(12, 2).value
            
            # === パート2: 値の検証と変換 ===
            if pc_id_value:
                try:
                    pc_id = int(pc_id_value)
                    logger.info(f"✅ スプレッドシートからPC_ID={pc_id}を読み取りました(セルB12)")
                    return pc_id
                except ValueError:
                    logger.warning(f"⚠️ B12セルの値 '{pc_id_value}' を整数に変換できません。デフォルト値1を使用します")
                    return 1
            else:
                logger.warning("⚠️ B12セルが空です。デフォルト値1を使用します")
                return 1
                
        except Exception as e:
            ErrorHandler.log_error(e, "PC_ID読み取り")
            logger.warning("⚠️ PC_IDの読み取りに失敗しました。デフォルト値1を使用します")
            return 1
    
    def load_pc_settings(self, pc_id: int = 1) -> Dict[str, str]:
        """PC固有の設定をsettingシートから読み込み"""
        try:
            # === パート1: シート接続と基本設定 ===
            self._ensure_client()
        
            sheet = self.gc.open_by_key(self.spreadsheet_id)
            setting_sheet = sheet.worksheet("setting")
        
            col_index = 1 + pc_id
        
            # === パート2: 各設定値の読み込み ===
            settings = {
                'google_id': self._get_cell_value(setting_sheet, 2, col_index),
                'google_pass': self._get_cell_value(setting_sheet, 3, col_index),
                'service_mail': self._get_cell_value(setting_sheet, 4, col_index),
                'download_image_folder': self._get_cell_value(setting_sheet, 5, col_index),
                'download_text_folder': self._get_cell_value(setting_sheet, 6, col_index),
                'browser_data_dir': self._get_cell_value(setting_sheet, 7, col_index),
                'service_account_file': self._get_cell_value(setting_sheet, 8, col_index),
                'cookies_file': self._get_cell_value(setting_sheet, 9, col_index),
                'generation_mode': self._get_cell_value(setting_sheet, 10, col_index),
                'text_format': self._get_cell_value(setting_sheet, 11, col_index),
                'service_type': self._get_cell_value(setting_sheet, 13, col_index),
                'agent_output_folder': self._get_cell_value(setting_sheet, 14, col_index),
                'max_iterations': self._get_cell_value(setting_sheet, 15, col_index),
                'wp_url': self._get_cell_value(setting_sheet, 16, col_index),
                'wp_user': self._get_cell_value(setting_sheet, 17, col_index),
                'wp_pass': self._get_cell_value(setting_sheet, 18, col_index),
            }
        
            # === パート3: 設定値の検証と正規化 ===
            # generation_modeの検証
            mode = settings.get('generation_mode', '').strip().lower()
            if mode not in ['text', 'image']:
                logger.warning(f"⚠️ 不正なgeneration_mode値: '{mode}' → デフォルト 'image' を使用")
                settings['generation_mode'] = 'image'
            else:
                settings['generation_mode'] = mode
        
            # max_iterationsの検証
            try:
                max_iter = int(settings.get('max_iterations', '3'))
                if max_iter < 1 or max_iter > 10:
                    logger.warning(f"⚠️ 不正なmax_iterations値: {max_iter} → デフォルト 3 を使用")
                    settings['max_iterations'] = 3
                else:
                    settings['max_iterations'] = max_iter
            except (ValueError, TypeError):
                logger.warning(f"⚠️ max_iterationsの変換エラー → デフォルト 3 を使用")
                settings['max_iterations'] = 3
        
            logger.info(f"✅ PC_ID={pc_id} の設定を読み込みました")
            return settings
        
        except Exception as e:
            ErrorHandler.log_error(e, f"PC_ID={pc_id} の設定読み込み")
            raise

    def _get_cell_value(self, sheet, row: int, col: int) -> str:
        """セルの値を安全に取得"""
        try:
            value = sheet.cell(row, col).value
            return value if value is not None else ""
        except Exception:
            return ""
    
    def _get_column_letter(self, col_index: int) -> str:
        """列インデックスを列文字に変換(1→A, 2→B, ...)"""
        result = ""
        while col_index > 0:
            col_index -= 1
            result = chr(col_index % 26 + ord('A')) + result
            col_index //= 26
        return result
    
    def load_credentials_from_sheet(self, pc_id: int = 1) -> Dict[str, str]:
        """認証情報を読み込み(PC_ID対応版)"""
        try:
            # === パート1: 設定読み込み ===
            settings = self.load_pc_settings(pc_id)
            
            # === パート2: 認証情報の抽出 ===
            credentials = {
                'email': settings['google_id'],
                'password': settings['google_pass'],
                'service_mail': settings.get('service_mail')
            }
            
            return credentials
            
        except Exception as e:
            ErrorHandler.log_error(e, "認証情報読み込み")
            raise
    
    # sheets_manager.py に以下のメソッドを追加

    async def verify_task_exists(self, task_id: int, sheet_name: str = "pm_tasks") -> bool:
        """タスクがシートに存在するか検証（追加）"""
        try:
            self._ensure_client()
            sheet = self.gc.open_by_key(self.spreadsheet_id)
            task_sheet = sheet.worksheet(sheet_name)
        
            # 全データを取得
            all_data = task_sheet.get_all_values()
        
            if len(all_data) <= 1:
                logger.warning(f"タスクシートにデータがありません")
                return False
        
            # ヘッダー解析
            headers = all_data[0]
            task_id_col = None
        
            for i, header in enumerate(headers):
                header_lower = header.lower()
                if 'task_id' in header_lower or 'id' in header_lower:
                    task_id_col = i
                    break
        
            if task_id_col is None:
                task_id_col = 0
        
            # タスクID検索（型の不一致を考慮）
            task_id_str = str(task_id)
            for row in all_data[1:]:
                if len(row) > task_id_col:
                    cell_value = str(row[task_id_col]).strip()
                    if cell_value == task_id_str:
                        logger.info(f"✅ タスク {task_id} の存在を確認")
                        return True
        
            logger.warning(f"❌ タスク {task_id} はシートに存在しません")
            return False
        
        except Exception as e:
            logger.error(f"タスク存在確認エラー: {e}")
            return False

    def _enhanced_task_search(self, task_sheet, task_id: int, task_id_col: int) -> tuple:
        """強化版タスク検索（修正）"""
        try:
            all_data = task_sheet.get_all_values()
            task_id_str = str(task_id)
        
            # デバッグ情報の収集
            available_ids = []
            for i, row in enumerate(all_data[1:], start=2):
                if len(row) > task_id_col and row[task_id_col]:
                    cell_value = str(row[task_id_col]).strip()
                    available_ids.append(cell_value)
                    if cell_value == task_id_str:
                        return (i, True)  # (行番号, 見つかったか)
        
            logger.warning(f"🔍 検索対象ID: '{task_id_str}'")
            logger.warning(f"🔍 利用可能なタスクID: {available_ids}")
            return (None, False)
        
        except Exception as e:
            logger.error(f"タスク検索エラー: {e}")
            return (None, False)
    
    def validate_sheet_structure(self) -> bool:
        """シート構造の妥当性をチェック"""
        try:
            # === パート1: クライアントとシート一覧の取得 ===
            self._ensure_client()
            
            sheet = self.gc.open_by_key(self.spreadsheet_id)
            
            required_sheets = ["setting"]
            existing_sheets = [ws.title for ws in sheet.worksheets()]
            
            # === パート2: 必須シートの存在確認 ===
            for required_sheet in required_sheets:
                if required_sheet not in existing_sheets:
                    logger.error(f"❌ 必要なシート '{required_sheet}' が見つかりません")
                    return False
            
            # === パート3: プロンプトシートの存在確認 ===
            if "prompt_text" not in existing_sheets and "prompt" not in existing_sheets:
                logger.error("❌ プロンプトシート ('prompt_text' または 'prompt') が見つかりません")
                return False
            
            logger.info("✅ シート構造の妥当性チェック完了")
            return True
            
        except Exception as e:
            ErrorHandler.log_error(e, "シート構造チェック")
            return False

    def get_tasks(self, sheet_name: str = None) -> list:
        """
        Sheetsからタスク一覧を取得（柔軟版）
        
        Args:
            sheet_name: シート名（None の場合は 'pm_tasks' → 'tasks' の順で探す）
        
        Returns:
            list: タスクのリスト（辞書形式）
        """
        try:
            self._ensure_client()
            
            # スプレッドシートを開く
            sheet = self.gc.open_by_key(self.spreadsheet_id)
            
            # シート名が指定されていない場合、自動検索
            if sheet_name is None:
                worksheet_names = [ws.title for ws in sheet.worksheets()]
                
                if 'pm_tasks' in worksheet_names:
                    sheet_name = 'pm_tasks'
                    print(f"✅ 'pm_tasks' シートを使用します")
                elif 'tasks' in worksheet_names:
                    sheet_name = 'tasks'
                    print(f"✅ 'tasks' シートを使用します")
                else:
                    print("⚠️  'pm_tasks' も 'tasks' も見つかりません")
                    return []
            
            # シート取得
            try:
                task_sheet = sheet.worksheet(sheet_name)
            except Exception:
                print(f"⚠️  '{sheet_name}' シートが見つかりません")
                return []
            
            # 全データを取得
            all_values = task_sheet.get_all_values()
            
            if not all_values or len(all_values) < 2:
                print("⚠️  データが見つかりません")
                return []
            
            # ヘッダー行（1行目）
            headers = all_values[0]
            
            # データ行（2行目以降）
            tasks = []
            for row in all_values[1:]:
                if not row or not row[0]:  # 空行をスキップ
                    continue
                
                task = {}
                for i, header in enumerate(headers):
                    if i < len(row):
                        task[header.lower()] = row[i]
                
                tasks.append(task)
            
            print(f"✅ {len(tasks)}件のタスクを取得しました（シート: {sheet_name}）")
            return tasks
            
        except Exception as e:
            print(f"❌ タスク取得エラー: {e}")
            import traceback
            traceback.print_exc()
            return []

