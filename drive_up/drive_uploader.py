import logging
import shutil
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import sys

from drive_manager import GoogleDriveManager

# ロガー設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('drive_upload.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class JSONDriveUploader:
    """JSONファイルをGoogle Driveにアップロードし、ローカルファイルを移動"""
    
    def __init__(
        self,
        source_folder: str,
        target_folder_id: str,
        credentials_file: str = None
    ):
        """
        Args:
            source_folder: アップロード元のローカルフォルダパス
            target_folder_id: Google Driveのアップロード先フォルダID
            credentials_file: OAuth2クライアントシークレットJSONファイルのパス
        """
        self.source_folder = Path(source_folder)
        self.old_folder = self.source_folder / "old"
        self.target_folder_id = target_folder_id
        
        # credentialsファイルのデフォルトパス
        if not credentials_file:
            credentials_file = r"C:\Users\color\Documents\gemini_auto_generate\credentials.json"
        
        # oldフォルダがなければ作成
        self.old_folder.mkdir(exist_ok=True)
        
        # Google Drive Managerの初期化（OAuth2認証）
        self.drive_manager = GoogleDriveManager(
            target_folder_id=target_folder_id,
            credentials_file=credentials_file,
            token_file="token.pickle"
        )
        
        self.results: List[Dict] = []
    
    def get_json_files(self) -> List[Path]:
        """アップロード対象のJSONファイルを取得"""
        json_files = []
        
        for file_path in self.source_folder.glob("*.json"):
            if file_path.is_file():
                json_files.append(file_path)
        
        logger.info(f"📁 検出されたJSONファイル: {len(json_files)}件")
        return json_files
    
    def move_to_old(self, file_path: Path) -> bool:
        """ファイルをoldフォルダに移動"""
        try:
            destination = self.old_folder / file_path.name
            
            # 同名ファイルが既に存在する場合、タイムスタンプを付加
            if destination.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                stem = destination.stem
                suffix = destination.suffix
                destination = self.old_folder / f"{stem}_{timestamp}{suffix}"
            
            shutil.move(str(file_path), str(destination))
            logger.info(f"📦 移動完了: {file_path.name} -> old/{destination.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ ファイル移動エラー ({file_path.name}): {e}")
            return False
    
    def upload_single_file(self, file_path: Path) -> bool:
        """1つのJSONファイルをアップロード"""
        result = {
            'filename': file_path.name,
            'size': file_path.stat().st_size,
            'upload_status': 'pending',
            'move_status': 'pending',
            'timestamp': datetime.now().isoformat(),
            'error': None
        }
        
        try:
            # アップロード
            file_id = self.drive_manager.upload_file(file_path)
            
            if file_id:
                result['upload_status'] = 'success'
                result['file_id'] = file_id
                
                # アップロード成功したらoldフォルダに移動
                if self.move_to_old(file_path):
                    result['move_status'] = 'success'
                    return True
                else:
                    result['move_status'] = 'failed'
                    result['error'] = 'ファイル移動に失敗'
            else:
                result['upload_status'] = 'failed'
                result['error'] = 'アップロードに失敗'
            
            return False
            
        except Exception as e:
            result['upload_status'] = 'error'
            result['error'] = str(e)
            logger.error(f"❌ 処理エラー ({file_path.name}): {e}")
            return False
        finally:
            self.results.append(result)
    
    def run(self) -> None:
        """アップロード処理を実行"""
        try:
            logger.info("="*60)
            logger.info("Google Drive JSONファイルアップロード開始")
            logger.info("="*60)
            logger.info(f"📂 ソースフォルダ: {self.source_folder.absolute()}")
            logger.info(f"📂 移動先フォルダ: {self.old_folder.absolute()}")
            
            # フォルダ情報取得
            folder_info = self.drive_manager.get_folder_info()
            if folder_info:
                logger.info(f"☁️  アップロード先: {folder_info.get('name', 'Unknown')}")
                logger.info(f"🔗 URL: {folder_info.get('url', 'N/A')}")
            
            # JSONファイル取得
            json_files = self.get_json_files()
            
            if not json_files:
                logger.warning("⚠️  アップロード対象のJSONファイルが見つかりません")
                return
            
            # アップロード処理
            logger.info(f"\n{'='*60}")
            logger.info("アップロード処理開始")
            logger.info(f"{'='*60}\n")
            
            successful_count = 0
            failed_files = []
            
            for i, file_path in enumerate(json_files, 1):
                logger.info(f"[{i}/{len(json_files)}] 処理中: {file_path.name}")
                
                if self.upload_single_file(file_path):
                    successful_count += 1
                else:
                    failed_files.append(file_path.name)
            
            # 最終レポート
            self.generate_report(successful_count, len(json_files), failed_files)
            
        except Exception as e:
            logger.error(f"❌ 重大なエラー: {e}")
            raise
    
    def generate_report(self, successful: int, total: int, failed_files: List[str]):
        """処理結果レポートを生成"""
        logger.info(f"\n{'='*60}")
        logger.info("処理完了レポート")
        logger.info(f"{'='*60}")
        logger.info(f"✅ 成功: {successful}/{total} 件")
        logger.info(f"❌ 失敗: {len(failed_files)} 件")
        logger.info(f"📊 成功率: {successful/total*100:.1f}%")
        
        if failed_files:
            logger.info("\n失敗したファイル:")
            for filename in failed_files:
                logger.info(f"  - {filename}")
        
        logger.info(f"\n詳細ログ: drive_upload.log")
        logger.info("="*60)


def main():
    """メイン処理"""
    # 設定値（必要に応じて変更してください）
    SOURCE_FOLDER = r"C:\Users\color\Documents\gemini_auto_generate\temp_texts"
    TARGET_FOLDER_ID = "16QVK_-z8JVmhLQuLVprOx9_DnoNc4eUc"  # Google DriveのフォルダID
    CREDENTIALS_FILE = r"C:\Users\color\Documents\gemini_auto_generate\credentials.json"  # OAuth2認証ファイル
    
    # パスの存在チェック
    if not Path(SOURCE_FOLDER).exists():
        logger.error(f"❌ ソースフォルダが見つかりません: {SOURCE_FOLDER}")
        return
    
    if not Path(CREDENTIALS_FILE).exists():
        logger.error(f"❌ OAuth2クライアントシークレットファイルが見つかりません: {CREDENTIALS_FILE}")
        logger.error("Google Cloud ConsoleでOAuth2クライアントIDを作成し、credentials.jsonとして保存してください")
        logger.error("参照: https://developers.google.com/drive/api/quickstart/python")
        return
    
    print("="*60)
    print("Google Drive JSONファイルアップローダー（OAuth2認証版）")
    print("="*60)
    print(f"ソース: {SOURCE_FOLDER}")
    print(f"フォルダID: {TARGET_FOLDER_ID}")
    print("="*60)
    
    # 実行確認
    response = input("\nアップロードを開始しますか? (y/N): ")
    if response.lower() != 'y':
        print("処理をキャンセルしました")
        return
    
    # アップロード実行
    uploader = JSONDriveUploader(
        source_folder=SOURCE_FOLDER,
        target_folder_id=TARGET_FOLDER_ID,
        credentials_file=CREDENTIALS_FILE
    )
    
    try:
        uploader.run()
        print("\n✅ 処理が正常に完了しました")
    except KeyboardInterrupt:
        print("\n⚠️  処理を中断しました")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")


if __name__ == "__main__":
    main()