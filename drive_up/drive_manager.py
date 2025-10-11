import logging
import pickle
import re
from pathlib import Path
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
import io

logger = logging.getLogger(__name__)

class GoogleDriveManager:
    """Google Drive操作を管理するクラス（OAuth2認証版・読み書き対応）"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    def __init__(self, target_folder_id: str = None, credentials_file: str = None, 
                 token_file: str = "token.pickle", service_account_file: str = None):
        """
        Args:
            target_folder_id: アップロード先のGoogle DriveフォルダID
            credentials_file: OAuth2クライアントシークレットJSONファイルのパス（初回のみ必要）
            token_file: 認証トークン保存ファイル
            service_account_file: サービスアカウントJSONファイル（優先）
        """
        self.target_folder_id = target_folder_id
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service_account_file = service_account_file
        self.service = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Google Drive APIの認証（サービスアカウント優先、OAuth2フォールバック）"""
        try:
            logger.info("Google Drive API認証中...")
            
            # 優先: サービスアカウント認証
            if self.service_account_file and Path(self.service_account_file).exists():
                logger.info("サービスアカウントで認証中...")
                from oauth2client.service_account import ServiceAccountCredentials
                
                creds = ServiceAccountCredentials.from_json_keyfile_name(
                    self.service_account_file,
                    scopes=self.SCOPES
                )
                self.service = build('drive', 'v3', credentials=creds)
                logger.info("✅ サービスアカウントでGoogle Drive API認証成功")
                return
            
            # フォールバック: OAuth2認証
            creds = None
            
            # トークンファイルが存在すれば読み込む
            if Path(self.token_file).exists():
                logger.info("保存された認証情報を読み込み中...")
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            # 認証情報が無効または存在しない場合
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("認証情報を更新中...")
                    creds.refresh(Request())
                else:
                    # 初回認証：ブラウザで認証
                    if not self.credentials_file or not Path(self.credentials_file).exists():
                        raise FileNotFoundError(
                            f"OAuth2クライアントシークレットファイルが見つかりません: {self.credentials_file}\n"
                            "Google Cloud ConsoleでOAuth2クライアントIDを作成してください。"
                        )
                    
                    logger.info("ブラウザで認証を開始します...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                
                # 認証情報を保存
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
                logger.info(f"認証情報を保存しました: {self.token_file}")
            
            self.service = build('drive', 'v3', credentials=creds)
            logger.info("✅ OAuth2でGoogle Drive API認証成功")
            
        except Exception as e:
            logger.error(f"❌ 認証エラー: {e}")
            raise
    
    def extract_file_id_from_url(self, url: str) -> Optional[str]:
        """
        Google DriveのURLからファイルIDを抽出
        
        対応形式:
        - https://drive.google.com/file/d/FILE_ID/view
        - https://drive.google.com/open?id=FILE_ID
        - https://docs.google.com/document/d/FILE_ID/edit
        """
        patterns = [
            r'/file/d/([a-zA-Z0-9_-]+)',
            r'id=([a-zA-Z0-9_-]+)',
            r'/d/([a-zA-Z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                file_id = match.group(1)
                logger.info(f"✅ ファイルIDを抽出: {file_id}")
                return file_id
        
        logger.warning(f"URLからファイルIDを抽出できませんでした: {url}")
        return None
    
    def read_file(self, file_id_or_url: str) -> Optional[str]:
        """
        Google Driveからファイルを読み込む
        
        Args:
            file_id_or_url: ファイルID または Google DriveのURL
            
        Returns:
            ファイルの内容（テキスト）、失敗時はNone
        """
        try:
            # URLの場合はファイルIDを抽出
            if file_id_or_url.startswith('http'):
                file_id = self.extract_file_id_from_url(file_id_or_url)
                if not file_id:
                    return None
            else:
                file_id = file_id_or_url
            
            logger.info(f"📥 Google Driveからファイルを読み込み中... (ID: {file_id})")
            
            # ファイル情報を取得
            try:
                file_metadata = self.service.files().get(
                    fileId=file_id, 
                    fields='name,mimeType,size'
                ).execute()
                
                file_name = file_metadata.get('name', 'Unknown')
                mime_type = file_metadata.get('mimeType', '')
                file_size = file_metadata.get('size', 0)
                
                logger.info(f"📄 ファイル名: {file_name}")
                logger.info(f"📊 MIME Type: {mime_type}")
                logger.info(f"📏 サイズ: {file_size} bytes")
                
            except Exception as e:
                logger.warning(f"ファイル情報取得エラー: {e}")
            
            # ファイルの内容をダウンロード
            request = self.service.files().get_media(fileId=file_id)
            
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.debug(f"⏳ ダウンロード進捗: {progress}%")
            
            # バイトデータをテキストに変換
            content = fh.getvalue().decode('utf-8')
            
            logger.info(f"✅ Google Driveから読み込み完了: {len(content)}文字")
            logger.info(f"先頭100文字: {content[:100]}...")
            
            return content
            
        except HttpError as e:
            logger.error(f"❌ ファイル読み込みエラー (HTTP): {e}")
            return None
        except Exception as e:
            logger.error(f"❌ ファイル読み込みエラー: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def upload_file(self, file_path: Path, folder_id: Optional[str] = None) -> Optional[str]:
        """
        ファイルをGoogle Driveにアップロード
        
        Args:
            file_path: アップロードするファイルのパス
            folder_id: アップロード先フォルダID（Noneの場合はデフォルトフォルダ）
        
        Returns:
            アップロード成功時はファイルID、失敗時はNone
        """
        try:
            target_folder = folder_id or self.target_folder_id
            
            if not target_folder:
                logger.error("アップロード先フォルダIDが指定されていません")
                return None
            
            file_metadata = {
                'name': file_path.name,
                'parents': [target_folder]
            }
            
            media = MediaFileUpload(
                str(file_path),
                mimetype='application/json',
                resumable=True
            )
            
            logger.info(f"📤 アップロード中: {file_path.name}")
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, size, webViewLink'
            ).execute()
            
            file_id = file.get('id')
            file_size = file.get('size', 0)
            web_link = file.get('webViewLink', '')
            
            logger.info(f"✅ アップロード成功: {file_path.name} ({int(file_size):,} bytes)")
            logger.info(f"🔗 リンク: {web_link}")
            logger.info(f"📋 ファイルID: {file_id}")
            
            return file_id
            
        except HttpError as e:
            logger.error(f"❌ アップロードエラー ({file_path.name}): {e}")
            return None
        except Exception as e:
            logger.error(f"❌ 予期しないエラー ({file_path.name}): {e}")
            return None
    
    def check_file_exists(self, filename: str, folder_id: Optional[str] = None) -> bool:
        """
        指定フォルダ内に同名ファイルが存在するかチェック
        
        Args:
            filename: チェックするファイル名
            folder_id: 検索対象フォルダID
        
        Returns:
            存在する場合True
        """
        try:
            target_folder = folder_id or self.target_folder_id
            query = f"name='{filename}' and '{target_folder}' in parents and trashed=false"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            files = results.get('files', [])
            return len(files) > 0
            
        except Exception as e:
            logger.warning(f"ファイル存在チェックエラー: {e}")
            return False
    
    def get_folder_info(self, folder_id: Optional[str] = None) -> Dict:
        """
        フォルダ情報を取得
        
        Args:
            folder_id: フォルダID
        
        Returns:
            フォルダ情報の辞書
        """
        try:
            target_folder = folder_id or self.target_folder_id
            
            if not target_folder:
                return {}
            
            folder = self.service.files().get(
                fileId=target_folder,
                fields='id, name, webViewLink'
            ).execute()
            
            return {
                'id': folder.get('id'),
                'name': folder.get('name'),
                'url': folder.get('webViewLink')
            }
        except Exception as e:
            logger.error(f"フォルダ情報取得エラー: {e}")
            return {}