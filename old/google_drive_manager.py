import json
import logging
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaInMemoryUpload
from google.oauth2.service_account import Credentials
from google.auth import default

from config_utils import config, ErrorHandler

logger = logging.getLogger(__name__)

class GoogleDriveManager:
    """Google Drive管理クラス"""
    
    def __init__(self, service_account_file: Optional[str] = None):
        self.service_account_file = service_account_file
        self.drive_service = None
        self.setup_drive_client()
    
    def setup_drive_client(self) -> None:
        """Google Drive クライアントの設定"""
        try:
            scopes = ['https://www.googleapis.com/auth/drive.file']
            
            if self.service_account_file and Path(self.service_account_file).exists():
                # サービスアカウント認証
                credentials = Credentials.from_service_account_file(
                    self.service_account_file,
                    scopes=scopes
                )
                logger.info("サービスアカウントで Google Drive に接続しました")
            else:
                # デフォルト認証
                credentials, project = default(scopes=scopes)
                logger.info("デフォルト認証で Google Drive に接続しました")
            
            self.drive_service = build('drive', 'v3', credentials=credentials)
            
        except Exception as e:
            ErrorHandler.log_error(e, "Google Drive クライアント設定")
            raise
    
    def upload_text_as_json(self, text_content: str, prompt: str, filename: str, folder_id: str) -> Optional[str]:
        """テキストをJSON形式でGoogle Driveにアップロード"""
        try:
            if not self.drive_service:
                logger.error("Google Drive サービスが初期化されていません")
                return None
            
            logger.info(f"Google DriveにJSON形式でアップロード中: {filename}")
            
            # JSON形式のデータを作成
            json_data = {
                "prompt": prompt,
                "response": text_content,
                "timestamp": datetime.now().isoformat(),
                "generated_by": "Gemini AI",
                "metadata": {
                    "character_count": len(text_content),
                    "word_count": len(text_content.split()),
                    "prompt_length": len(prompt)
                }
            }
            
            # JSONを文字列に変換
            json_string = json.dumps(json_data, ensure_ascii=False, indent=2)
            json_bytes = json_string.encode('utf-8')
            
            # ファイルメタデータ
            file_metadata = {
                'name': filename,
                'parents': [folder_id],
                'mimeType': 'application/json'
            }
            
            # メモリ内アップロード
            media = MediaInMemoryUpload(
                json_bytes,
                mimetype='application/json',
                resumable=True
            )
            
            # アップロード実行
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            
            file_id = file.get('id')
            web_link = file.get('webViewLink')
            
            logger.info(f"✅ JSONアップロード成功: {filename}")
            logger.info(f"   Drive ID: {file_id}")
            logger.info(f"   リンク: {web_link}")
            
            return file_id
            
        except Exception as e:
            ErrorHandler.log_error(e, "JSON Google Driveアップロード")
            return None
    
    def upload_image_file(self, file_path: Path, folder_id: str) -> Optional[str]:
        """画像ファイルをGoogle Driveにアップロード"""
        try:
            if not self.drive_service:
                logger.error("Google Drive サービスが初期化されていません")
                return None
            
            if not file_path.exists():
                logger.error(f"ファイルが存在しません: {file_path}")
                return None
            
            logger.info(f"Google Driveに画像をアップロード中: {file_path.name}")
            
            # ファイルメタデータ
            file_metadata = {
                'name': file_path.name,
                'parents': [folder_id]
            }
            
            # MIME typeを推測
            mime_type = 'image/png'
            if file_path.suffix.lower() == '.jpg' or file_path.suffix.lower() == '.jpeg':
                mime_type = 'image/jpeg'
            elif file_path.suffix.lower() == '.gif':
                mime_type = 'image/gif'
            elif file_path.suffix.lower() == '.webp':
                mime_type = 'image/webp'
            
            media = MediaFileUpload(
                str(file_path),
                mimetype=mime_type,
                resumable=True
            )
            
            # アップロード実行
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            
            file_id = file.get('id')
            web_link = file.get('webViewLink')
            
            logger.info(f"✅ 画像アップロード成功: {file_path.name}")
            logger.info(f"   Drive ID: {file_id}")
            logger.info(f"   リンク: {web_link}")
            
            # アップロード成功後、ローカルファイルを削除（オプション）
            try:
                file_path.unlink()
                logger.info(f"   ローカルファイルを削除しました: {file_path.name}")
            except:
                pass
            
            return file_id
            
        except Exception as e:
            ErrorHandler.log_error(e, "画像 Google Driveアップロード")
            return None
    
    def get_file_info(self, file_id: str) -> Optional[Dict]:
        """ファイル情報を取得"""
        try:
            if not self.drive_service:
                return None
            
            file = self.drive_service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, size, webViewLink, createdTime'
            ).execute()
            
            return file
            
        except Exception as e:
            ErrorHandler.log_error(e, "ファイル情報取得")
            return None
    
    def list_files_in_folder(self, folder_id: str, page_size: int = 10) -> list:
        """フォルダ内のファイル一覧を取得"""
        try:
            if not self.drive_service:
                return []
            
            query = f"'{folder_id}' in parents and trashed=false"
            
            results = self.drive_service.files().list(
                q=query,
                pageSize=page_size,
                fields="files(id, name, mimeType, createdTime, webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            
            logger.info(f"フォルダ内のファイル数: {len(files)}")
            return files
            
        except Exception as e:
            ErrorHandler.log_error(e, "フォルダ一覧取得")
            return []