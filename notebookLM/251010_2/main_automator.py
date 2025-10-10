import asyncio
import time
import json
from pathlib import Path
from typing import List, Dict, Optional
import logging
from datetime import datetime

# ===== 最優先: ログ設定を他のインポートより前に実行 =====
# config_utilsをインポートすると自動的にログ設定が実行される
from config_utils import config, ErrorHandler, FileNameGenerator, PathManager

# これで他のモジュールをインポート
from sheets_manager import GoogleSheetsManager
from browser_controller import BrowserController

logger = logging.getLogger(__name__)

class GeminiAutomator:
    """メインのGemini自動化クラス（拡張版:画像・テキスト両対応・ローカル保存・DeepSeek対応）"""
    
    def __init__(self, pc_id: int = None, auto_detect_pc_id: bool = True):
        """
        初期化
        
        Args:
            pc_id: 明示的に指定するPC_ID（Noneの場合は自動検出）
            auto_detect_pc_id: Trueの場合、スプレッドシートのB12セルからPC_IDを読み取る
        """
        # まず、サービスアカウントファイルでシートマネージャーを初期化
        default_service_account = r"C:\Users\color\Documents\gemini_auto_generate\service_account.json"
        service_account_file = default_service_account if Path(default_service_account).exists() else None
        
        self.sheets_manager = GoogleSheetsManager(config.SPREADSHEET_ID, service_account_file)
        
        # PC_IDの決定（優先順位）
        # 1. 明示的に指定されたpc_id
        # 2. スプレッドシートのB12セルから読み取り（auto_detect_pc_id=Trueの場合）
        # 3. 環境変数
        # 4. デフォルト値(1)
        if pc_id is not None:
            self.pc_id = pc_id
            logger.info(f"PC_IDを明示的指定から取得: {self.pc_id}")
        elif auto_detect_pc_id:
            try:
                self.pc_id = self.sheets_manager.get_current_pc_id()
                logger.info(f"PC_IDをスプレッドシート(B12)から取得: {self.pc_id}")
            except Exception as e:
                logger.warning(f"スプレッドシートからのPC_ID取得に失敗: {e}")
                import os
                self.pc_id = int(os.getenv('GEMINI_PC_ID', '1'))
                logger.info(f"PC_IDを環境変数/デフォルトから取得: {self.pc_id}")
        else:
            import os
            self.pc_id = int(os.getenv('GEMINI_PC_ID', '1'))
            logger.info(f"PC_IDを環境変数/デフォルトから取得: {self.pc_id}")
        
        # PC固有の設定を読み込み
        self.load_pc_configuration()
        self.mode = config.GENERATION_MODE or "image"
        self.service = config.SERVICE_TYPE or "google"
        
        # ダウンロードフォルダの設定（スプレッドシートB5/B6から取得）
        if self.mode == "text":
            # テキストモードの場合はB6の設定を使用
            if config.DOWNLOAD_TEXT_FOLDER:
                self.download_folder = PathManager.get_safe_path(config.DOWNLOAD_TEXT_FOLDER)
                logger.info(f"テキスト保存先（B6から取得）: {self.download_folder}")
            else:
                # フォールバック: ローカル一時フォルダ
                base_temp_folder = Path(r"C:\Users\color\Documents\gemini_auto_generate")
                self.download_folder = PathManager.get_safe_path(str(base_temp_folder / "temp_texts"))
                logger.warning(f"B6が空のため、デフォルトフォルダを使用: {self.download_folder}")
        else:
            # 画像モードの場合はB5の設定を使用
            if config.DOWNLOAD_IMAGE_FOLDER:
                self.download_folder = PathManager.get_safe_path(config.DOWNLOAD_IMAGE_FOLDER)
                logger.info(f"画像保存先（B5から取得）: {self.download_folder}")
            else:
                # フォールバック: ローカル一時フォルダ
                base_temp_folder = Path(r"C:\Users\color\Documents\gemini_auto_generate")
                self.download_folder = PathManager.get_safe_path(str(base_temp_folder / "temp_images"))
                logger.warning(f"B5が空のため、デフォルトフォルダを使用: {self.download_folder}")
        
        self.browser_controller = BrowserController(self.download_folder, self.mode, self.service)
        self.credentials: Optional[Dict[str, str]] = None
        self.prompts: List[str] = []
        self.results: List[Dict] = []
        self.generate_unique_filename = lambda idx: FileNameGenerator.generate_unique_filename(idx, mode=self.mode)
    
    def load_pc_configuration(self) -> None:
        """PC固有の設定を読み込み"""
        try:
            logger.info(f"PC_ID={self.pc_id} の設定を読み込み中...")
            settings = self.sheets_manager.load_pc_settings(self.pc_id)
            config.BROWSER_DATA_DIR = settings.get('browser_data_dir')
            config.SERVICE_ACCOUNT_FILE = settings.get('service_account_file')
            config.COOKIES_FILE = settings.get('cookies_file')
            config.GENERATION_MODE = settings.get('generation_mode', 'image')
            config.TEXT_FORMAT = settings.get('text_format', 'txt')
            config.DOWNLOAD_IMAGE_FOLDER = settings.get('download_image_folder')
            config.DOWNLOAD_TEXT_FOLDER = settings.get('download_text_folder')
            config.AGENT_OUTPUT_FOLDER = settings.get('agent_output_folder')
            config.MAX_ITERATIONS = settings.get('max_iterations', 3)
        
            # サービスタイプの取得
            service_type = settings.get('service_type', '').strip().lower()
            if service_type in ['deepseek', 'google', 'gemini']:
                if service_type == 'gemini':
                    service_type = 'google'
                config.SERVICE_TYPE = service_type
            else:
                config.SERVICE_TYPE = 'google'
        
            logger.info(f"PC_ID={self.pc_id} の設定読み込み完了")
            logger.info(f"  サービス: {config.SERVICE_TYPE}")
            logger.info(f"  モード: {config.GENERATION_MODE}")
            logger.info(f"  テキスト形式: {config.TEXT_FORMAT}")
            logger.info(f"  Browser Data: {config.BROWSER_DATA_DIR}")
            logger.info(f"  画像フォルダ (B5): {config.DOWNLOAD_IMAGE_FOLDER}")
            logger.info(f"  テキストフォルダ (B6): {config.DOWNLOAD_TEXT_FOLDER}")
            logger.info(f"  Agent出力先 (B14): {config.AGENT_OUTPUT_FOLDER}")
            logger.info(f"  最大反復回数 (B15): {config.MAX_ITERATIONS}")
            if config.SERVICE_ACCOUNT_FILE and Path(config.SERVICE_ACCOUNT_FILE).exists():
                self.sheets_manager = GoogleSheetsManager(config.SPREADSHEET_ID, config.SERVICE_ACCOUNT_FILE)
        except Exception as e:
            ErrorHandler.log_error(e, "PC設定読み込み")
            raise
    
    async def initialize(self) -> None:
        """初期化処理"""
        try:
            logger.info("初期化処理開始...")
            if not self.sheets_manager.validate_sheet_structure():
                raise Exception("Google Sheetsの構造が正しくありません")
            self.credentials = self.sheets_manager.load_credentials_from_sheet(self.pc_id)
            
            # credentialsをbrowser_controllerに渡す
            self.browser_controller.credentials = self.credentials
            
            prompt_sheet_name = "prompt_text" if self.mode == "text" else "prompt_text"
            self.prompts = self.sheets_manager.load_prompts_from_sheet(prompt_sheet_name)
            if not self.prompts:
                raise Exception("処理するプロンプトがありません")
            await self.browser_controller.setup_browser()
            logger.info("初期化処理完了")
        except Exception as e:
            ErrorHandler.log_error(e, "初期化処理")
            raise
    
    async def login_process(self) -> None:
        """ログイン処理（サービス別）"""
        try:
            logger.info("ログイン処理開始...")
            
            if self.service == "deepseek":
                # DeepSeekはGoogleアカウントでログイン
                logger.info("DeepSeekサービスを使用します")
                is_logged_in = await self.browser_controller.check_google_login_status()
                if not is_logged_in:
                    logger.info("Googleアカウントにログインしてください（DeepSeek用）")
                    logger.info(f"ID: {self.credentials.get('email', 'N/A')}")
                    input("Googleログイン完了後、Enterキーを押してください: ")
                    is_logged_in = await self.browser_controller.check_google_login_status()
                    if not is_logged_in:
                        logger.warning("ログインが確認できませんが、処理を続行します")
                else:
                    logger.info("既にGoogleアカウントにログイン済みです")
                
                await self.browser_controller.navigate_to_deepseek()
            else:
                # Google/Geminiの場合
                logger.info("Geminiサービスを使用します")
                is_logged_in = await self.browser_controller.check_google_login_status()
                if not is_logged_in:
                    logger.info("Googleアカウントにログインが必要です")
                    logger.info(f"ID: {self.credentials.get('email', 'N/A')}")
                    input("ログイン完了後、Enterキーを押してください: ")
                    is_logged_in = await self.browser_controller.check_google_login_status()
                    if not is_logged_in:
                        logger.warning("ログインが確認できませんが、処理を続行します")
                else:
                    logger.info("既にGoogleアカウントにログイン済みです")
                
                await self.browser_controller.navigate_to_gemini()
            
            logger.info("ログイン処理完了")
        except Exception as e:
            ErrorHandler.log_error(e, "ログイン処理")
            raise
    
    async def process_single_prompt_image(self, prompt: str, index: int) -> bool:
        """画像モードでプロンプトを処理"""
        try:
            logger.info(f"\n--- プロンプト {index}/{len(self.prompts)} を処理中（画像モード）---")
            logger.info(f"プロンプト: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
            result = {
                'index': index, 'prompt': prompt, 'status': 'processing',
                'filename': None, 'timestamp': datetime.now().isoformat(),
                'error': None, 'mode': 'image'
            }
            try:
                await self.browser_controller.send_prompt(prompt)
                if await self.browser_controller.wait_for_image_generation():
                    filename = await self.browser_controller.download_latest_image(index)
                    if filename:
                        result['status'] = 'success'
                        result['filename'] = filename
                        save_path = self.download_folder / filename
                        logger.info(f"プロンプト {index} の処理に成功")
                        logger.info(f"保存先: {save_path}")
                        return True
                    else:
                        result['status'] = 'download_failed'
                        result['error'] = 'ダウンロードに失敗'
                else:
                    result['status'] = 'generation_failed'
                    result['error'] = '画像生成に失敗またはタイムアウト'
            except Exception as e:
                result['status'] = 'error'
                result['error'] = str(e)
                ErrorHandler.log_error(e, f"プロンプト {index} 処理")
            return False
        except Exception as e:
            ErrorHandler.log_error(e, f"プロンプト {index} 処理")
            return False
        finally:
            self.results.append(result)
    
    async def process_single_prompt_text(self, prompt: str, index: int, max_retries: int = 2) -> bool:
        """テキストモードでプロンプトを処理"""
        try:
            logger.info(f"\n--- プロンプト {index}/{len(self.prompts)} を処理中（テキストモード）---")
            logger.info(f"プロンプト: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
            result = {
                'index': index, 'prompt': prompt, 'status': 'processing',
                'filename': None, 'timestamp': datetime.now().isoformat(),
                'error': None, 'mode': 'text'
            }
            for attempt in range(1, max_retries + 1):
                try:
                    logger.info(f"試行 {attempt}/{max_retries}")
                    await self.browser_controller.send_prompt(prompt)
                    if await self.browser_controller.wait_for_text_generation():
                        response_text = await self.browser_controller.extract_latest_text_response()
                        if response_text:
                            # フォーマットに応じてファイル名と保存形式を変更
                            text_format = config.TEXT_FORMAT or 'txt'
                            
                            if text_format == 'json':
                                # JSON形式
                                filename = self.generate_unique_filename(index)
                                filename = filename.replace('.txt', '.json')
                                json_data = {"response": response_text}
                                save_path = self.download_folder / filename
                                try:
                                    with open(save_path, 'w', encoding='utf-8') as f:
                                        json.dump(json_data, f, ensure_ascii=False, indent=2)
                                    if save_path.exists():
                                        file_size = save_path.stat().st_size
                                        result['status'] = 'success'
                                        result['filename'] = filename
                                        logger.info(f"✅ JSON保存成功: {filename} ({file_size:,} bytes)")
                                        logger.info(f"保存先: {save_path}")
                                        return True
                                except Exception as e:
                                    result['status'] = 'save_failed'
                                    result['error'] = f'JSON保存エラー: {str(e)}'
                                    logger.error(f"JSON保存エラー: {e}")
                            else:
                                # TXT形式（デフォルト）
                                filename = self.generate_unique_filename(index)
                                save_path = self.download_folder / filename
                                try:
                                    with open(save_path, 'w', encoding='utf-8') as f:
                                        f.write(response_text)
                                    if save_path.exists():
                                        file_size = save_path.stat().st_size
                                        result['status'] = 'success'
                                        result['filename'] = filename
                                        logger.info(f"✅ テキスト保存成功: {filename} ({file_size:,} bytes)")
                                        logger.info(f"保存先: {save_path}")
                                        return True
                                except Exception as e:
                                    result['status'] = 'save_failed'
                                    result['error'] = f'テキスト保存エラー: {str(e)}'
                                    logger.error(f"テキスト保存エラー: {e}")
                        else:
                            result['status'] = 'extraction_failed'
                            result['error'] = 'テキスト抽出に失敗'
                    else:
                        result['status'] = 'generation_failed'
                        result['error'] = 'テキスト生成に失敗またはタイムアウト'
                    if attempt < max_retries:
                        logger.info(f"5秒後に再試行します...")
                        await asyncio.sleep(5)
                    else:
                        break
                except Exception as e:
                    result['status'] = 'error'
                    result['error'] = str(e)
                    ErrorHandler.log_error(e, f"プロンプト {index} 処理（試行 {attempt}）")
                    if attempt < max_retries:
                        await asyncio.sleep(5)
                    else:
                        break
            return False
        except Exception as e:
            ErrorHandler.log_error(e, f"プロンプト {index} 処理")
            return False
        finally:
            self.results.append(result)
    
    async def run_automation(self) -> None:
        """自動化処理の実行"""
        try:
            logger.info("=== Gemini自動化処理を開始 ===")
            logger.info(f"PC_ID: {self.pc_id}")
            logger.info(f"モード: {self.mode.upper()}")
            logger.info(f"保存先: ローカルフォルダ")
            logger.info(f"保存パス: {self.download_folder.absolute()}")
            await self.initialize()
            await self.login_process()
            if self.browser_controller.page:
                await self.browser_controller.page.screenshot(path="gemini_initial.png")
            successful_count = 0
            failed_prompts = []
            for i, prompt in enumerate(self.prompts, 1):
                try:
                    if self.mode == "text":
                        success = await self.process_single_prompt_text(prompt, i)
                    else:
                        success = await self.process_single_prompt_image(prompt, i)
                    if success:
                        successful_count += 1
                    else:
                        failed_prompts.append(f"{i}: {prompt[:50]}...")
                    if i < len(self.prompts):
                        await asyncio.sleep(8)
                except Exception as e:
                    logger.error(f"プロンプト {i} の処理中にエラー: {e}")
                    failed_prompts.append(f"{i}: {prompt[:50]}... (エラー)")
                    continue
            try:
                self.sheets_manager.save_result_to_sheet(self.results, self.mode)
            except Exception as e:
                logger.warning(f"結果のシート保存に失敗: {e}")
            self.generate_final_report(successful_count, failed_prompts)
        except Exception as e:
            ErrorHandler.log_error(e, "自動化処理の重大なエラー")
            try:
                if self.browser_controller.page:
                    await self.browser_controller.page.screenshot(path="final_error.png")
            except:
                pass
            raise
        finally:
            await self.browser_controller.cleanup()
    
    def generate_final_report(self, successful: int, failed_prompts: list):
        """最終レポートの生成"""
        logger.info(f"\n{'='*50}")
        logger.info("処理完了レポート")
        logger.info(f"{'='*50}")
        logger.info(f"PC_ID: {self.pc_id}")
        logger.info(f"モード: {self.mode.upper()}")
        logger.info(f"成功: {successful}/{len(self.prompts)} 件")
        logger.info(f"失敗: {len(failed_prompts)} 件")
        logger.info(f"成功率: {successful/len(self.prompts)*100:.1f}%")
        logger.info(f"保存先: {self.download_folder.absolute()}")
        if failed_prompts:
            logger.info("\n失敗したプロンプト:")
            for failed in failed_prompts:
                logger.info(f"  - {failed}")

async def main():
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='Gemini自動生成（ローカル保存版）')
    parser.add_argument('--pc-id', type=int, default=None, help='PC_IDを明示的に指定（指定しない場合はスプレッドシートのB12セルから自動取得）')
    parser.add_argument('--no-auto-detect', action='store_true', help='スプレッドシートからのPC_ID自動取得を無効化')
    args = parser.parse_args()
    
    print("=== Gemini 自動生成スクリプト（ローカル保存版）===")
    if args.pc_id is not None:
        print(f"PC_ID: {args.pc_id} (明示的指定)")
        automator = GeminiAutomator(pc_id=args.pc_id, auto_detect_pc_id=False)
    elif args.no_auto_detect:
        default_pc_id = int(os.getenv('GEMINI_PC_ID', '1'))
        print(f"PC_ID: {default_pc_id} (環境変数/デフォルト)")
        automator = GeminiAutomator(pc_id=default_pc_id, auto_detect_pc_id=False)
    else:
        print("PC_ID: スプレッドシート(B12セル)から自動取得")
        automator = GeminiAutomator(auto_detect_pc_id=True)
    
    try:
        await automator.run_automation()
        print("\n処理が正常に完了しました")
    except KeyboardInterrupt:
        print("\n処理を中断しました")
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        logger.error(f"メイン処理エラー: {e}")

if __name__ == "__main__":
    asyncio.run(main())