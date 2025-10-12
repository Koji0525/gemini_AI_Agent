import logging
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import sys

from drive_manager import GoogleDriveManager
from tools.sheets_manager import GoogleSheetsManager  # 既存のsheets_managerを使用

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

class JSONDriveUploaderWithSheets:
    """スプレッドシート連携版：JSONファイルをGoogle Driveにアップロード"""
    
    # スプレッドシートID
    SPREADSHEET_ID = "1jz-4t7PI71KDDdldyLNWIwUehrkADcdNiCGe94LU0b4"
    
    def __init__(self, pc_id: int = 1):
        """
        Args:
            pc_id: PC識別ID（settingシートから設定を読み込む）
        """
        self.pc_id = pc_id
        self.sheets_manager = None
        self.drive_manager = None
        self.source_folder = None
        self.old_folder = None
        self.results: List[Dict] = []
        
        self._load_configuration()
    
    def _load_configuration(self) -> None:
        """スプレッドシートから設定を読み込み"""
        try:
            logger.info(f"PC_ID={self.pc_id} の設定を読み込み中...")
            
            # まずデフォルトのサービスアカウントでシート接続
            default_service_account = r"C:\Users\color\Documents\gemini_auto_generate\service_account.json"
            
            if not Path(default_service_account).exists():
                raise FileNotFoundError(f"サービスアカウントファイルが見つかりません: {default_service_account}")
            
            self.sheets_manager = GoogleSheetsManager(
                self.SPREADSHEET_ID,
                default_service_account
            )
            
            # settingシートから設定を取得
            settings = self.sheets_manager.load_pc_settings(self.pc_id)
            
            # アップロード元フォルダ（Download_Text_Folder）
            source_folder_path = settings.get('download_text_folder')
            if not source_folder_path:
                raise ValueError("Download_Text_Folderが設定されていません")
            
            self.source_folder = Path(source_folder_path)
            self.old_folder = self.source_folder / "old"
            self.old_folder.mkdir(exist_ok=True)
            
            # サービスアカウントファイル
            service_account_file = settings.get('service_account_file', default_service_account)
            
            # Google DriveのフォルダID（固定値または設定から取得）
            # ここでは固定値を使用（必要に応じて設定シートに追加可能）
            target_folder_id = "16QVK_-z8JVmhLQuLVprOx9_DnoNc4eUc"
            
            # Google Drive Managerの初期化
            self.drive_manager = GoogleDriveManager(
                service_account_file=service_account_file,
                target_folder_id=target_folder_id
            )
            
            logger.info(f"✅ PC_ID={self.pc_id} の設定読み込み完了")
            logger.info(f"  ソースフォルダ: {self.source_folder}")
            logger.info(f"  サービスアカウント: {service_account_file}")
            
        except Exception as e:
            logger.error(f"❌ 設定読み込みエラー: {e}")
            raise
    
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
    
    def save_results_to_sheet(self) -> None:
        """アップロード結果をスプレッドシートに保存（オプション）"""
        try:
            # 結果シート名（必要に応じて）
            result_sheet_name = "upload_results"
            
            # ここに結果保存のロジックを追加可能
            # 例: self.sheets_manager.save_result_to_sheet(self.results, 'upload')
            
            logger.info("結果をスプレッドシートに保存しました")
        except Exception as e:
            logger.warning(f"結果のシート保存に失敗: {e}")
    
    def run(self) -> None:
        """アップロード処理を実行"""
        try:
            logger.info("="*60)
            logger.info("Google Drive JSONファイルアップロード開始")
            logger.info(f"PC_ID: {self.pc_id}")
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
            
            # 結果をシートに保存（オプション）
            # self.save_results_to_sheet()
            
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
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='Google Drive JSONアップローダー（スプレッドシート連携版）')
    parser.add_argument('--pc-id', type=int, default=None, help='PC識別ID（デフォルト: 環境変数またはPC_ID=1）')
    args = parser.parse_args()
    
    # PC_IDの決定
    default_pc_id = int(os.getenv('GEMINI_PC_ID', '1'))
    pc_id = args.pc_id if args.pc_id is not None else default_pc_id
    
    print("="*60)
    print("Google Drive JSONファイルアップローダー")
    print("（スプレッドシート連携版）")
    print("="*60)
    print(f"PC_ID: {pc_id}")
    print("="*60)
    
    # 実行確認
    response = input("\nアップロードを開始しますか? (y/N): ")
    if response.lower() != 'y':
        print("処理をキャンセルしました")
        return
    
    # アップロード実行
    uploader = JSONDriveUploaderWithSheets(pc_id=pc_id)
    
    try:
        uploader.run()
        print("\n✅ 処理が正常に完了しました")
    except KeyboardInterrupt:
        print("\n⚠️  処理を中断しました")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")


if __name__ == "__main__":
    main()