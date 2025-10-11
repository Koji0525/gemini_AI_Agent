import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

# 最初にロガーを設定
logger = logging.getLogger(__name__)

# 原因切り分けのためのインポートチェック
try:
    from config_utils import ErrorHandler, PathManager
    CONFIG_UTILS_AVAILABLE = True
    logger.debug("✅ config_utils インポート成功")
except ImportError as e:
    logger.error(f"❌ config_utils インポートエラー: {e}")
    CONFIG_UTILS_AVAILABLE = False
    # フォールバッククラス
    class ErrorHandler:
        @staticmethod
        def log_error(e, context):
            print(f"ERROR [{context}]: {e}")
    
    class PathManager:
        @staticmethod
        def get_safe_path(path):
            return Path(path)

try:
    from browser_controller import BrowserController
    BROWSER_CONTROLLER_AVAILABLE = True
    logger.debug("✅ browser_controller インポート成功")
except ImportError as e:
    logger.error(f"❌ browser_controller インポートエラー: {e}")
    BROWSER_CONTROLLER_AVAILABLE = False

class DesignAgent:
    """設計AI - 要件定義、設計書、アーキテクチャを作成"""
    
    DESIGN_SYSTEM_PROMPT = """あなたは経験豊富なシステム設計者です。

【あなたの役割】
- 要件定義書の作成
- システムアーキテクチャの設計
- データベーススキーマの設計
- API仕様の定義
- 技術選定と理由の説明

【設計の原則】
1. 実装可能性を最優先する
2. セキュリティを考慮する
3. スケーラビリティを意識する
4. 開発者が理解しやすい文書を作成

【出力形式】
タスクの内容に応じて、以下の形式で出力してください：

## タスク概要
（タスクの理解と目的）

## 設計内容
（具体的な設計内容）

## 技術選定
（使用する技術とその理由）

## 実装における注意点
（開発時の注意事項）

## 次のステップ
（このタスク後に行うべきこと）"""

    def __init__(self, browser_controller=None, browser=None, output_folder: Path = None):
        """
        初期化 - 引数名の互換性を確保
        
        原因切り分けのための詳細ログ:
        """
        logger.info("🔍 DesignAgent.__init__() 開始")
        logger.info(f"   browser_controller: {type(browser_controller)}")
        logger.info(f"   browser: {type(browser)}")
        logger.info(f"   output_folder: {output_folder}")
        
        # 原因1: 引数名の不一致を解決
        if browser_controller is not None:
            self.browser = browser_controller
            logger.info("✅ browser_controller を使用")
        elif browser is not None:
            self.browser = browser
            logger.info("✅ browser を使用")
        else:
            self.browser = None
            logger.warning("⚠️ ブラウザインスタンスが提供されていません")
        
        # 原因2: 出力フォルダの設定ロジック
        self.output_folder = self._setup_output_folder(output_folder)
        
        # 初期化状態の確認
        self._validate_initialization()
        
        logger.info("✅ DesignAgent.__init__() 完了")

    def _setup_output_folder(self, output_folder: Optional[Path]) -> Path:
        """出力フォルダを設定（原因切り分け付き）"""
        logger.info("🔍 出力フォルダ設定開始")
        
        # 原因3: 出力フォルダが直接指定されている場合
        if output_folder is not None:
            safe_path = PathManager.get_safe_path(output_folder) if CONFIG_UTILS_AVAILABLE else Path(output_folder)
            logger.info(f"✅ 直接指定の出力フォルダ: {safe_path}")
            return safe_path
        
        # 原因4: configから取得を試みる
        try:
            from config_utils import config
            if hasattr(config, 'AGENT_OUTPUT_FOLDER') and config.AGENT_OUTPUT_FOLDER:
                safe_path = PathManager.get_safe_path(config.AGENT_OUTPUT_FOLDER)
                logger.info(f"✅ configから取得した出力フォルダ: {safe_path}")
                return safe_path
        except Exception as e:
            logger.error(f"❌ configからの取得失敗: {e}")
        
        # 原因5: フォールバックパス
        fallback_path = Path(r"C:\Users\color\Documents\gemini_auto_generate\agent_outputs")
        fallback_path.mkdir(exist_ok=True, parents=True)
        logger.warning(f"⚠️ フォールバックフォルダを使用: {fallback_path}")
        
        return fallback_path

    def _validate_initialization(self):
        """初期化状態を検証（原因切り分け）"""
        logger.info("🔍 初期化状態検証開始")
        
        # 原因6: ブラウザコントローラーの状態確認
        if self.browser is None:
            logger.error("❌ ブラウザコントローラーが設定されていません")
        else:
            logger.info(f"✅ ブラウザコントローラー: {type(self.browser)}")
            # メソッドの存在確認
            required_methods = ['send_prompt', 'wait_for_text_generation', 'extract_latest_text_response']
            for method in required_methods:
                if hasattr(self.browser, method):
                    logger.info(f"✅ メソッド存在: {method}")
                else:
                    logger.error(f"❌ メソッド不足: {method}")
        
        # 原因7: 出力フォルダの権限確認
        try:
            test_file = self.output_folder / "test_write_permission.txt"
            test_file.write_text("test")
            test_file.unlink()
            logger.info("✅ 出力フォルダ書き込み権限: OK")
        except Exception as e:
            logger.error(f"❌ 出力フォルダ書き込み権限エラー: {e}")
        
        # 原因8: 必要なモジュールの可用性確認
        logger.info(f"✅ config_utils 可用性: {CONFIG_UTILS_AVAILABLE}")
        logger.info(f"✅ browser_controller 可用性: {BROWSER_CONTROLLER_AVAILABLE}")
        
        logger.info("🔍 初期化状態検証完了")

    async def process_task(self, task: Dict) -> Dict:
        """設計タスクを処理（詳細な原因切り分け付き）"""
        task_id = task.get('task_id', 'UNKNOWN')
        logger.info(f"\n🎯 DesignAgent.process_task() 開始: {task_id}")
        
        try:
            # 原因9: タスクデータの検証
            self._validate_task_data(task)
            
            logger.info(f"設計AI: タスク処理開始 - {task['description']}")
            
            # プロンプトを構築
            full_prompt = self._build_prompt(task)
            logger.info(f"📝 プロンプト長: {len(full_prompt)}文字")
            
            # 原因10: ブラウザ操作前の状態確認
            if not await self._pre_browser_validation():
                return {
                    'success': False,
                    'error': 'ブラウザ検証失敗'
                }
            
            # Geminiに送信
            logger.info("Geminiに設計タスクを送信中...")
            logger.info("🔄 ブラウザ操作開始...")
            
            send_success = await self.browser.send_prompt(full_prompt)
            if not send_success:
                logger.error("❌ プロンプト送信失敗")
                return {
                    'success': False,
                    'error': '設計AI: プロンプト送信失敗'
                }
            
            logger.info("✅ プロンプト送信成功")
            
            # 応答待機
            logger.info("⏳ 応答待機中...")
            success = await self.browser.wait_for_text_generation(max_wait=180)
            
            if not success:
                logger.error("❌ テキスト生成タイムアウト")
                return {
                    'success': False,
                    'error': '設計AI: タイムアウト'
                }
            
            logger.info("✅ テキスト生成完了")
            
            # 応答を取得
            response_text = await self.browser.extract_latest_text_response()
            
            if not response_text:
                logger.error("❌ 応答テキスト取得失敗")
                return {
                    'success': False,
                    'error': '設計AI: 応答取得失敗'
                }
            
            logger.info(f"✅ 応答取得完了: {len(response_text)}文字")
            logger.info(f"設計AI: 応答取得完了（{len(response_text)}文字）")
            
            # 結果をファイルに保存
            result = await self._save_results(task, response_text)
            
            logger.info(f"✅ タスク完了: {task_id}")
            return result
            
        except Exception as e:
            # 原因11: 詳細な例外情報
            error_msg = self._analyze_exception(e, task)
            ErrorHandler.log_error(e, "設計AI処理")
            
            logger.error(f"❌ タスク失敗: {task_id} - {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }

    def _validate_task_data(self, task: Dict):
        """タスクデータを検証"""
        logger.info("🔍 タスクデータ検証")
        
        required_fields = ['task_id', 'description']
        for field in required_fields:
            if field not in task:
                raise ValueError(f"必須フィールド '{field}' がありません")
            logger.info(f"✅ 必須フィールド: {field}")
        
        logger.info(f"📋 タスクID: {task.get('task_id')}")
        logger.info(f"📋 説明: {task.get('description')[:50]}...")
        logger.info(f"📋 ロール: {task.get('required_role', 'N/A')}")

    def _build_prompt(self, task: Dict) -> str:
        """プロンプトを構築"""
        return f"""{self.DESIGN_SYSTEM_PROMPT}

【タスク】
{task['description']}

上記のタスクについて、詳細な設計を行ってください。
実装可能で具体的な設計書を作成してください。"""

    async def _pre_browser_validation(self) -> bool:
        """ブラウザ操作前の検証"""
        logger.info("🔍 ブラウザ操作前検証")
        
        if self.browser is None:
            logger.error("❌ ブラウザインスタンスがありません")
            return False
        
        # ブラウザの状態確認
        if hasattr(self.browser, 'is_ready'):
            is_ready = await self.browser.is_ready()
            if not is_ready:
                logger.error("❌ ブラウザが準備できていません")
                return False
        
        logger.info("✅ ブラウザ検証: OK")
        return True

    async def _save_results(self, task: Dict, response_text: str) -> Dict:
        """結果を保存"""
        logger.info("🔍 結果保存処理")
        
        filename = f"design_{task['task_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        output_path = self.output_folder / filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# 設計書: {task['description']}\n\n")
                f.write(f"タスクID: {task['task_id']}\n")
                f.write(f"作成日時: {datetime.now().isoformat()}\n\n")
                f.write("---\n\n")
                f.write(response_text)
            
            logger.info(f"✅ 設計書保存: {output_path}")
            logger.info(f"設計書を保存: {output_path}")
            
            # サマリーを作成（最初の500文字）
            summary = response_text[:500] + "..." if len(response_text) > 500 else response_text
            
            return {
                'success': True,
                'output_file': str(output_path),
                'summary': summary,
                'full_text': response_text
            }
            
        except Exception as e:
            logger.error(f"❌ ファイル保存エラー: {e}")
            raise

    def _analyze_exception(self, e: Exception, task: Dict) -> str:
        """例外を詳細に分析"""
        error_type = type(e).__name__
        task_id = task.get('task_id', 'UNKNOWN')
        
        logger.info(f"🔍 例外分析: {error_type}")
        logger.info(f"🔍 例外メッセージ: {str(e)}")
        
        # 原因タイプに基づいたメッセージ
        if "browser" in str(e).lower() or "send_prompt" in str(e):
            return f"ブラウザ操作エラー: {str(e)}"
        elif "timeout" in str(e).lower():
            return f"タイムアウトエラー: {str(e)}"
        elif "file" in str(e).lower() or "write" in str(e):
            return f"ファイル操作エラー: {str(e)}"
        elif "import" in str(e).lower():
            return f"インポートエラー: {str(e)}"
        else:
            return f"設計タスク実行エラー ({error_type}): {str(e)}"

    # デバッグ用メソッド
    def get_status(self) -> Dict:
        """エージェントの状態を取得"""
        return {
            'browser_available': self.browser is not None,
            'output_folder': str(self.output_folder),
            'config_utils_available': CONFIG_UTILS_AVAILABLE,
            'browser_controller_available': BROWSER_CONTROLLER_AVAILABLE,
            'output_folder_writable': self._check_folder_writable()
        }

    def _check_folder_writable(self) -> bool:
        """フォルダ書き込み可能かチェック"""
        try:
            test_file = self.output_folder / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()
            return True
        except:
            return False


# テスト用コード
async def test_design_agent():
    """DesignAgentのテスト"""
    print("🧪 DesignAgent テスト開始")
    
    # モックブラウザ（実際の環境に合わせて調整）
    class MockBrowser:
        async def send_prompt(self, prompt):
            print(f"📤 モック送信: {len(prompt)}文字")
            return True
        
        async def wait_for_text_generation(self, max_wait=180):
            await asyncio.sleep(1)
            return True
        
        async def extract_latest_text_response(self):
            return "これはモック応答です。設計内容: ..."
    
    # テスト実行
    try:
        browser = MockBrowser()
        agent = DesignAgent(browser_controller=browser)
        
        test_task = {
            'task_id': 'TEST_001',
            'description': 'テスト設計タスク',
            'required_role': 'design'
        }
        
        result = await agent.process_task(test_task)
        print(f"🧪 テスト結果: {result}")
        
    except Exception as e:
        print(f"❌ テスト失敗: {e}")


if __name__ == "__main__":
    # 単体テスト
    asyncio.run(test_design_agent())