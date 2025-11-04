# dev_agent.py
"""開発AI - コード生成とテストコード、WordPress専用機能の作成（引数診断強化版）"""
import asyncio
import logging
import inspect
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import re
import json

from configuration.config_utils import ErrorHandler, PathManager
from browser_control.browser_controller import BrowserController

logger = logging.getLogger(__name__)


class DevAgent:
    """開発AI - コード生成とテストコード、WordPress専用機能の作成"""

    def __init__(
        self,
        browser: BrowserController = None,
        browser_controller: BrowserController = None,
        output_folder: Path = None,
    ):
        """
        初期化メソッド（複数引数名対応版）

        Args:
            browser: BrowserController インスタンス
            browser_controller: BrowserController インスタンス（互換性用）
            output_folder: 出力フォルダパス
        """
        # 引数診断ログ
        logger.info("🔍 DevAgent 初期化診断:")
        logger.info(f"   - browser: {browser is not None}")
        logger.info(f"   - browser_controller: {browser_controller is not None}")
        logger.info(f"   - output_folder: {output_folder}")

        # browser_controller を優先し、次に browser を使用
        if browser_controller is not None:
            self.browser = browser_controller
            logger.info("✅ browser_controller を使用")
        elif browser is not None:
            self.browser = browser
            logger.info("✅ browser を使用")
        else:
            logger.error("❌ browser_controller も browser も提供されていません")
            self.browser = None

        # 出力フォルダの設定
        if output_folder is None:
            from configuration.config_utils import config

            if config.AGENT_OUTPUT_FOLDER:
                self.output_folder = PathManager.get_safe_path(config.AGENT_OUTPUT_FOLDER)
                logger.info(f"Agent出力先（B14から取得）: {self.output_folder}")
            else:
                # フォールバック: デフォルトパス
                self.output_folder = Path.home() / "Documents" / "gemini_auto_generate" / "agent_outputs"
                self.output_folder.mkdir(exist_ok=True, parents=True)
                logger.warning(f"B14が空のため、デフォルトフォルダを使用: {self.output_folder}")
        else:
            self.output_folder = output_folder

        self.design_docs = {}  # 設計書を参照できるようにする

        # 初期化完了ログ
        logger.info(f"✅ DevAgent 初期化完了:")
        logger.info(f"   - browser: {self.browser is not None}")
        logger.info(f"   - output_folder: {self.output_folder}")

    # 既存のプロンプト定義は変更なし...
    DEV_SYSTEM_PROMPT = """あなたは経験豊富なソフトウェアエンジニアです。..."""

    WORDPRESS_CPT_PROMPT = """あなたはWordPress開発の専門家です。..."""

    async def process_task(self, task: Dict) -> Dict:
        """開発タスクを処理（引数診断強化版）"""
        try:
            # 引数状態の診断
            self._diagnose_agent_state(task)

            logger.info(f"開発AI: タスク処理開始 - {task['description']}")

            # WordPress カスタム投稿タイプ作成タスクか判定
            if self._is_wordpress_cpt_task(task):
                return await self._process_wordpress_cpt_task(task)

            # WordPress タクソノミー作成タスクか判定
            if self._is_wordpress_taxonomy_task(task):
                return await self._process_wordpress_taxonomy_task(task)

            # 通常の開発タスク
            return await self._process_general_task(task)

        except Exception as e:
            ErrorHandler.log_error(e, "開発AI処理")
            return {"success": False, "error": str(e)}

    def _diagnose_agent_state(self, task: Dict):
        """エージェント状態の診断"""
        logger.info("🔍 DevAgent 状態診断:")
        logger.info(f"   - タスクID: {task.get('task_id', 'N/A')}")
        logger.info(f"   - タスク説明: {task.get('description', 'N/A')[:100]}...")
        logger.info(f"   - browser インスタンス: {self.browser is not None}")
        logger.info(f"   - output_folder 存在: {self.output_folder.exists() if self.output_folder else False}")

        # 重要なメソッドの存在確認
        required_methods = ["send_prompt", "wait_for_text_generation", "extract_latest_text_response"]
        if self.browser:
            for method in required_methods:
                has_method = hasattr(self.browser, method) and callable(getattr(self.browser, method))
                logger.info(f"   - browser.{method}: {'✅' if has_method else '❌'}")

        # 引数シグネチャの診断
        try:
            init_signature = inspect.signature(self.__init__)
            params = list(init_signature.parameters.keys())
            logger.info(f"   - __init__ パラメータ: {params}")
        except Exception as e:
            logger.warning(f"   - シグネチャ診断エラー: {e}")

    def _is_wordpress_cpt_task(self, task: Dict) -> bool:
        """WordPressカスタム投稿タイプ作成タスクか判定"""
        description = task.get("description", "").lower()
        keywords = ["custom post type", "カスタム投稿タイプ", "cpt", "register_post_type", "投稿タイプ"]
        return any(kw in description for kw in keywords)

    def _is_wordpress_taxonomy_task(self, task: Dict) -> bool:
        """WordPressタクソノミー作成タスクか判定"""
        description = task.get("description", "").lower()
        keywords = ["taxonomy", "タクソノミー", "カスタム分類", "register_taxonomy"]
        return any(kw in description for kw in keywords)

    async def _process_wordpress_cpt_task(self, task: Dict) -> Dict:
        """WordPressカスタム投稿タイプ作成タスクを処理"""
        try:
            # ブラウザ状態の確認
            if not self.browser:
                return {"success": False, "error": "DevAgent: browser_controller が初期化されていません"}

            logger.info("=" * 60)
            logger.info("WordPress カスタム投稿タイプ作成タスク")
            logger.info("=" * 60)

            # タスクから情報を抽出
            cpt_info = self._extract_cpt_info(task)

            logger.info(f"投稿タイプスラッグ: {cpt_info['slug']}")
            logger.info(f"表示名（単数）: {cpt_info['singular_name']}")
            logger.info(f"表示名（複数）: {cpt_info['plural_name']}")

            # プロンプトを構築
            full_prompt = self._build_wordpress_cpt_prompt(task, cpt_info)

            # Geminiに送信
            logger.info("Geminiに要件定義書作成タスクを送信中...")
            await self.browser.send_prompt(full_prompt)

            # 応答待機（要件定義書は長いので300秒）
            logger.info("⏱️ 待機時間: 300秒（要件定義書作成）")

            # ブラウザメソッドの互換性対応
            if hasattr(self.browser, "wait_for_text_generation"):
                success = await self.browser.wait_for_text_generation(max_wait=300)
            elif hasattr(self.browser, "_wait_for_generation_complete"):
                success = await self.browser._wait_for_generation_complete()
            else:
                logger.error("❌ 利用可能な待機メソッドが見つかりません")
                return {"success": False, "error": "利用可能な待機メソッドが見つかりません"}

            if not success:
                return {"success": False, "error": "開発AI: タイムアウト（要件定義書作成: 300秒）"}

            # 応答を取得
            response_text = await self.browser.extract_latest_text_response()

            if not response_text:
                return {"success": False, "error": "開発AI: 応答取得失敗"}

            logger.info(f"開発AI: 応答取得完了（{len(response_text)}文字）")

            # 結果を保存
            output_files = self._save_wordpress_cpt_code(response_text, task, cpt_info)

            # サマリーを作成
            summary = f"""✅ WordPressカスタム投稿タイプ作成完了

【投稿タイプ情報】
- スラッグ: {cpt_info['slug']}
- 表示名: {cpt_info['singular_name']} / {cpt_info['plural_name']}
- サポート機能: {', '.join(cpt_info['supports'])}

【生成ファイル】
"""
            for file_info in output_files:
                summary += f"- {file_info['type']}: {file_info['path'].name}\n"

            summary += f"\n【次のステップ】\n"
            summary += f"1. functions.php または専用プラグインに追加\n"
            summary += f"2. パーマリンク設定を保存（設定 > パーマリンク設定）\n"
            summary += f"3. 管理画面で「{cpt_info['menu_name']}」メニューを確認\n"

            return {
                "success": True,
                "output_files": output_files,
                "summary": summary,
                "full_text": response_text,
                "cpt_slug": cpt_info["slug"],
            }

        except Exception as e:
            ErrorHandler.log_error(e, "WordPressカスタム投稿タイプ作成")
            return {"success": False, "error": str(e)}

    # 既存のメソッドは変更なし...
    def _extract_cpt_info(self, task: Dict) -> Dict:
        """タスクからカスタム投稿タイプの情報を抽出"""
        # 実装は変更なし...
        pass

    def _build_wordpress_cpt_prompt(self, task: Dict, cpt_info: Dict) -> str:
        """WordPressカスタム投稿タイプ用のプロンプトを構築"""
        # 実装は変更なし...
        pass

    def _save_wordpress_cpt_code(self, text: str, task: Dict, cpt_info: Dict) -> list:
        """WordPressカスタム投稿タイプのコードを保存"""
        # 実装は変更なし...
        pass

    def _extract_php_code(self, text: str) -> Optional[str]:
        """テキストからPHPコードを抽出"""
        # 実装は変更なし...
        pass

    async def _process_wordpress_taxonomy_task(self, task: Dict) -> Dict:
        """WordPressタクソノミー作成タスクを処理"""
        # 実装は変更なし...
        pass

    async def _process_general_task(self, task: Dict) -> Dict:
        """通常の開発タスクを処理"""
        try:
            # ブラウザ状態の確認
            if not self.browser:
                return {"success": False, "error": "DevAgent: browser_controller が初期化されていません"}

            logger.info("通常の開発タスクとして処理")

            # 対応する設計書があれば読み込む
            design_context = self._load_design_context(task)

            # プロンプトを構築
            full_prompt = f"""{self.DEV_SYSTEM_PROMPT}

【タスク】
{task['description']}"""

            if design_context:
                full_prompt += f"""

【設計書（参考）】
{design_context}"""

            full_prompt += """

上記のタスクについて、完全に動作するコードを実装してください。
エラーハンドリングとコメントを含めてください。"""

            # Geminiに送信
            logger.info("Geminiに開発タスクを送信中...")
            await self.browser.send_prompt(full_prompt)

            # タスクの種類によって待機時間を調整
            description = task.get("description", "").lower()

            if any(word in description for word in ["要件定義", "設計書", "アーキテクチャ", "仕様書"]):
                max_wait = 300  # 要件定義書などは5分
                logger.info("📋 要件定義・設計書タスク - 待機時間を300秒に延長")
            else:
                max_wait = 180  # 通常は3分

            # ブラウザメソッドの互換性対応
            if hasattr(self.browser, "wait_for_text_generation"):
                success = await self.browser.wait_for_text_generation(max_wait=max_wait)
            elif hasattr(self.browser, "_wait_for_generation_complete"):
                success = await self.browser._wait_for_generation_complete()
            else:
                logger.error("❌ 利用可能な待機メソッドが見つかりません")
                return {"success": False, "error": "利用可能な待機メソッドが見つかりません"}

            if not success:
                return {"success": False, "error": "開発AI: タイムアウト"}

            # 応答を取得
            response_text = await self.browser.extract_latest_text_response()

            if not response_text:
                return {"success": False, "error": "開発AI: 応答取得失敗"}

            logger.info(f"開発AI: 応答取得完了（{len(response_text)}文字）")

            # コードをファイルに保存
            filename = f"code_{task['task_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            output_path = self.output_folder / filename

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"# コード: {task['description']}\n\n")
                f.write(f"タスクID: {task['task_id']}\n")
                f.write(f"作成日時: {datetime.now().isoformat()}\n\n")
                f.write("---\n\n")
                f.write(response_text)

            logger.info(f"コードを保存: {output_path}")

            # コード部分を抽出して個別ファイルに保存
            self._extract_and_save_code(response_text, task)

            # サマリーを作成
            summary = response_text[:500] + "..." if len(response_text) > 500 else response_text

            return {"success": True, "output_file": str(output_path), "summary": summary, "full_text": response_text}

        except Exception as e:
            ErrorHandler.log_error(e, "開発AI処理")
            return {"success": False, "error": str(e)}

    def _load_design_context(self, task: Dict) -> str:
        """対応する設計書があれば読み込む"""
        try:
            # design_*.md ファイルを探す
            design_files = list(self.output_folder.glob(f"design_{task['task_id']}_*.md"))

            if design_files:
                # 最新のファイルを読み込む
                latest_design = sorted(design_files)[-1]
                with open(latest_design, "r", encoding="utf-8") as f:
                    content = f.read()
                logger.info(f"設計書を読み込みました: {latest_design.name}")
                return content[:2000]  # 最初の2000文字のみ

            return ""
        except Exception as e:
            logger.warning(f"設計書読み込みエラー: {e}")
            return ""

    def _extract_and_save_code(self, text: str, task: Dict):
        """コードブロックを抽出して個別ファイルに保存"""
        try:
            # ```言語 ... ``` パターンを抽出
            code_blocks = re.findall(r"```(\w+)\n(.*?)```", text, re.DOTALL)

            for i, (lang, code) in enumerate(code_blocks):
                # ファイル拡張子を決定
                ext_map = {
                    "python": ".py",
                    "javascript": ".js",
                    "typescript": ".ts",
                    "html": ".html",
                    "css": ".css",
                    "java": ".java",
                    "cpp": ".cpp",
                    "c": ".c",
                    "php": ".php",
                    "ruby": ".rb",
                    "go": ".go",
                    "rust": ".rs",
                }
                ext = ext_map.get(lang.lower(), ".txt")

                # ファイルに保存
                code_filename = f"code_{task['task_id']}_{i+1}{ext}"
                code_path = self.output_folder / code_filename

                with open(code_path, "w", encoding="utf-8") as f:
                    f.write(code)

                logger.info(f"コードファイルを保存: {code_filename}")

        except Exception as e:
            logger.warning(f"コード抽出エラー: {e}")
