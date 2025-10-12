import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from configuration.config_utils import config, ErrorHandler
from tools.sheets_manager import GoogleSheetsManager
from browser_control.browser_controller import BrowserController
from core_agents.pm_system_prompts import PM_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class PMAgent:
    """PM AI - プロジェクト管理とタスク分解を担当"""
    
    def __init__(self, sheets_manager: GoogleSheetsManager, browser_controller: BrowserController):
        self.sheets_manager = sheets_manager
        self.browser = browser_controller
        self.current_goal = None
        self.generated_tasks = []
        self.system_prompt = PM_SYSTEM_PROMPT
    
    async def load_project_goal(self) -> Optional[Dict]:
        """project_goalシートから最新のアクティブな目標を読み込む"""
        try:
            logger.info("プロジェクト目標を読み込み中...")
            sheet = self.sheets_manager.gc.open_by_key(self.sheets_manager.spreadsheet_id)
            
            try:
                goal_sheet = sheet.worksheet("project_goal")
            except:
                logger.error("'project_goal'シートが見つかりません")
                return None
            
            all_values = goal_sheet.get_all_values()
            
            if len(all_values) <= 1:
                logger.warning("目標が設定されていません")
                return None
            
            for row in all_values[1:]:
                if len(row) >= 3 and row[2].lower() == 'active':
                    goal = {
                        'goal_id': row[0],
                        'description': row[1],
                        'status': row[2],
                        'created_at': row[3] if len(row) > 3 else ''
                    }
                    logger.info(f"目標を読み込みました: {goal['description']}")
                    self.current_goal = goal
                    return goal
            
            logger.warning("アクティブな目標が見つかりません")
            return None
            
        except Exception as e:
            ErrorHandler.log_error(e, "目標読み込み")
            raise
    async def analyze_and_create_tasks(self, goal_description: str) -> Dict:
        """目標を分析してタスクを生成"""
        try:
            # === パート1: 開始ヘッダー表示 ===
            logger.info("="*60)
            logger.info("PM AI: タスク分解を開始します")
            logger.info("="*60)
    
            # === パート2: プロンプト構築 ===
            full_prompt = f"""{self.system_prompt}

    【プロジェクト目標】
    {goal_description}

    【重要な出力指示】
    1. **必ず有効なJSON形式のみで出力してください**
    2. 説明文、コメント、挨拶などは一切不要です
    3. 最初の文字が {{ で、最後の文字が }} の完全なJSON形式のみを出力してください
    4. **タスク数は最大15個まで**とし、JSONが長くなりすぎないようにしてください
    5. すべての文字列値は正しくダブルクォーテーションで囲んでください

    上記の目標を達成するために必要なタスクを、JSON形式で出力してください。"""
    
            # === パート3: Geminiへの送信 ===
            logger.info("Geminiに送信中...")
            await self.browser.send_prompt(full_prompt)
    
            # === パート4: 応答待機 ===
            logger.info("PM AIの分析を待機中...")
            success = await self.browser.wait_for_text_generation(max_wait=180)
    
            if not success:
                raise Exception("PM AIのタスク生成がタイムアウトしました")
    
            # === パート5: 応答テキストの抽出 ===
            response_text = await self.browser.extract_latest_text_response()
    
            if not response_text:
                raise Exception("PM AIからの応答が取得できませんでした")
    
            logger.info(f"PM AIの応答を取得しました（{len(response_text)}文字）")
            logger.info(f"応答の先頭500文字:\n{response_text[:500]}")
            logger.info(f"応答の末尾500文字:\n{response_text[-500:]}")
    
            # === パート6: JSONレスポンスの解析 ===
            task_plan = self._parse_json_response(response_text)
    
            if task_plan:
                # === パート7: 成功時の処理 ===
                logger.info("="*60)
                logger.info("PM AI: タスク分解完了")
                logger.info(f"生成されたタスク数: {len(task_plan.get('tasks', []))}")
                logger.info("="*60)
                self.generated_tasks = task_plan.get('tasks', [])
                return task_plan
            else:
                # === パート8: JSON解析失敗時のフォールバック処理 ===
                logger.error("JSON解析に失敗しました。応答全体を保存します。")
                fallback_path = Path("pm_ai_response_error.txt")
                with open(fallback_path, 'w', encoding='utf-8') as f:
                    f.write(response_text)
                logger.info(f"応答を保存しました: {fallback_path}")
        
                logger.error("="*60)
                logger.error("❌ 自動修復も失敗しました")
                logger.error("="*60)
        
                # === パート9: 修正済みファイルのチェック ===
                fixed_path = Path("pm_ai_response_fixed.json")
                if fixed_path.exists():
                    logger.info("修正済みファイルを検出しました!")
                    try:
                        with open(fixed_path, 'r', encoding='utf-8') as f:
                            task_plan = json.load(f)
                        logger.info(f"✅ 修正済みJSONを読み込みました: タスク数={len(task_plan.get('tasks', []))}")
                        self.generated_tasks = task_plan.get('tasks', [])
                        return task_plan
                    except Exception as e:
                        logger.error(f"修正済みファイルの読み込みに失敗: {e}")
        
                raise Exception("PM AIの応答をJSON形式でパースできませんでした")
    
        except Exception as e:
            ErrorHandler.log_error(e, "タスク生成")
            raise
        
        
    def _parse_json_response(self, text: str) -> Optional[Dict]:
        """応答からJSON部分を抽出してパース（強化版）"""
        try:
            # === パート1: 入力検証 ===
            if not text:
                logger.warning("空の応答テキスト")
                return None
            
            # === パート2: 解析開始ヘッダー ===
            logger.info("="*60)
            logger.info("JSON解析開始")
            logger.info("="*60)
            logger.info(f"応答全体の長さ: {len(text)}文字")
            
            import re
            
            # === パート3: パターン1 - ```json ... ``` 形式の検出 ===
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                logger.info("✅ パターン1: ```json...``` 形式を検出")
                try:
                    result = json.loads(json_str)
                    logger.info(f"✅ JSON解析成功（パターン1）: タスク数={len(result.get('tasks', []))}")
                    return result
                except json.JSONDecodeError as e:
                    logger.warning(f"パターン1でJSON解析失敗: {e}")
            
            # === パート4: パターン2 - 中括弧のバランスを考慮した抽出 ===
            start_idx = text.find('{')
            if start_idx != -1:
                logger.info(f"✅ '{{' を位置 {start_idx} で検出")
                
                # === パート5: バランスの取れたJSONオブジェクトの検出 ===
                brace_count = 0
                in_string = False
                escape_next = False
                
                for i, char in enumerate(text[start_idx:], start=start_idx):
                    if escape_next:
                        escape_next = False
                        continue
                    
                    if char == '\\':
                        escape_next = True
                        continue
                    
                    if char == '"' and not escape_next:
                        in_string = not in_string
                        continue
                    
                    if not in_string:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                # === パート6: 完全なJSONオブジェクトの抽出と解析 ===
                                potential_json = text[start_idx:i+1]
                                logger.info(f"✅ 完全なJSONオブジェクトを抽出: {len(potential_json)}文字")
                                
                                try:
                                    result = json.loads(potential_json)
                                    logger.info(f"✅ JSON解析成功: タスク数={len(result.get('tasks', []))}")
                                    return result
                                except json.JSONDecodeError as e:
                                    # === パート7: 解析エラーの詳細ログ ===
                                    logger.error(f"❌ JSON解析エラー: {e}")
                                    logger.error(f"エラー位置: line {e.lineno}, column {e.colno}")
                                    
                                    error_pos = e.pos if hasattr(e, 'pos') else 0
                                    context_start = max(0, error_pos - 100)
                                    context_end = min(len(potential_json), error_pos + 100)
                                    logger.error(f"エラー周辺のテキスト:\n{potential_json[context_start:context_end]}")
                                    
                                    # === パート8: JSON修復の試行 ===
                                    repaired_json = self._attempt_json_repair(potential_json, e)
                                    if repaired_json:
                                        return repaired_json
            
            # === パート9: パターン3 - テキスト全体をJSONとして解析 ===
            logger.info("パターン3: テキスト全体をJSONとして解析")
            try:
                result = json.loads(text)
                logger.info(f"✅ JSON解析成功（全体解析）: タスク数={len(result.get('tasks', []))}")
                return result
            except json.JSONDecodeError as e:
                logger.error(f"❌ 全体解析も失敗: {e}")
            
            # === パート10: 全パターン失敗時のエラーログ ===
            logger.error("="*60)
            logger.error("❌ すべてのJSON解析パターンが失敗")
            logger.error("="*60)
            logger.error(f"応答の先頭500文字:\n{text[:500]}")
            logger.error(f"応答の末尾500文字:\n{text[-500:]}")
            
            return None
            
        except Exception as e:
            # === パート11: 予期しない例外の処理 ===
            logger.error(f"❌ JSON解析で予期しないエラー: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def _attempt_json_repair(self, json_str: str, error: json.JSONDecodeError) -> Optional[Dict]:
        """壊れたJSONの修復を試みる"""
        try:
            # === パート1: 修復開始 ===
            logger.info("🔧 JSON修復を試みます...")
            
            error_pos = error.pos if hasattr(error, 'pos') else len(json_str)
            
            # === パート2: 修復試行1 - デリミタエラーの修正 ===
            if "Expecting ',' delimiter" in str(error) or "Expecting ':' delimiter" in str(error):
                last_complete_task = json_str.rfind('},', 0, error_pos)
                if last_complete_task > 0:
                    repaired = json_str[:last_complete_task + 1] + '], "risks": [], "success_criteria": []}'
                    logger.info(f"修復試行1: 位置{last_complete_task}で切り捨て")
                    try:
                        result = json.loads(repaired)
                        logger.info(f"✅ 修復成功! タスク数={len(result.get('tasks', []))}")
                        return result
                    except:
                        pass
            
            # === パート3: 修復試行2 - 行ベースの切り捨て ===
            lines = json_str.split('\n')
            error_line = error.lineno if hasattr(error, 'lineno') else len(lines)
            
            if error_line > 0 and error_line <= len(lines):
                truncated_lines = lines[:error_line-1]
                truncated = '\n'.join(truncated_lines)
                open_braces = truncated.count('{') - truncated.count('}')
                
                repaired = truncated
                if ',"tasks":[' in repaired and not repaired.rstrip().endswith(']'):
                    repaired += ']'
                
                # === パート4: 開いた中括弧を閉じる ===
                for _ in range(open_braces):
                    repaired += '}'
                
                logger.info("修復試行2: 不完全な部分を削除して閉じる")
                try:
                    result = json.loads(repaired)
                    logger.info(f"✅ 修復成功! タスク数={len(result.get('tasks', []))}")
                    return result
                except:
                    pass
            
            # === パート5: 修復失敗 ===
            logger.warning("❌ JSON修復に失敗")
            return None
            
        except Exception as e:
            logger.error(f"JSON修復中のエラー: {e}")
            return None
        
    async def save_tasks_to_sheet(self, task_plan: Dict) -> bool:
        """生成されたタスクをスプレッドシートに保存（追加方式）"""
        try:
            # === パート1: 保存開始 ===
            logger.info("タスクをスプレッドシートに保存中...")
        
            sheet = self.sheets_manager.gc.open_by_key(self.sheets_manager.spreadsheet_id)
        
            try:
                # === パート2: 既存シートの読み込み ===
                task_sheet = sheet.worksheet("pm_tasks")
                existing_data = task_sheet.get_all_values()
                start_row = len(existing_data) + 1
            
                if len(existing_data) == 0:
                    # === パート3: 新規シートのヘッダー作成 ===
                    headers = [
                        "task_id", "parent_goal_id", "task_description", 
                        "required_role", "status", "priority", 
                        "estimated_time", "dependencies", "created_at", "batch_id"
                    ]
                    task_sheet.update('A1:J1', [headers])
                    start_row = 2
                
            except:
                # === パート4: シートが存在しない場合の作成 ===
                logger.info("'pm_tasks'シートを作成します")
                task_sheet = sheet.add_worksheet(title="pm_tasks", rows=1000, cols=10)
                headers = [
                    "task_id", "parent_goal_id", "task_description", 
                    "required_role", "status", "priority", 
                    "estimated_time", "dependencies", "created_at", "batch_id"
                ]
                task_sheet.update('A1:J1', [headers])
                start_row = 2
                existing_data = []
        
            # === パート5: バッチIDの生成 ===
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
            # === パート6: 既存タスクIDの収集 ===
            existing_task_ids = []
            if len(existing_data) > 1:
                for row in existing_data[1:]:
                    if row and row[0].isdigit():
                        existing_task_ids.append(int(row[0]))
        
            # === パート7: 次のタスクIDの決定 ===
            next_task_id = max(existing_task_ids) + 1 if existing_task_ids else 1
        
            # === パート8: タスクデータの準備 ===
            tasks = task_plan.get('tasks', [])
            rows_data = []
        
            for i, task in enumerate(tasks):
                row = [
                    next_task_id + i,
                    self.current_goal['goal_id'] if self.current_goal else '',
                    task.get('description', ''),
                    task.get('required_role', 'dev'),
                    'pending',
                    task.get('priority', 'medium'),
                    task.get('estimated_time', ''),
                    ','.join(map(str, task.get('dependencies', []))),
                    datetime.now().isoformat(),
                    batch_id
                ]
                rows_data.append(row)
        
            # === パート9: スプレッドシートへの書き込み ===
            if rows_data:
                end_row = start_row + len(rows_data) - 1
                task_sheet.update(f'A{start_row}:J{end_row}', rows_data)
                logger.info(f"タスク {len(rows_data)} 件を追加しました（バッチ: {batch_id}）")
        
            # === パート10: メタデータの保存 ===
            self._save_project_metadata(task_plan)
        
            return True
        
        except Exception as e:
            ErrorHandler.log_error(e, "タスク保存")
            return False
    
    def _save_project_metadata(self, task_plan: Dict):
        """プロジェクトのメタ情報（分析結果、リスク、成功基準）を保存（追加方式）"""
        try:
            sheet = self.sheets_manager.gc.open_by_key(self.sheets_manager.spreadsheet_id)
        
            try:
                meta_sheet = sheet.worksheet("project_metadata")
                existing_data = meta_sheet.get_all_values()
                start_row = len(existing_data) + 2
            except:
                meta_sheet = sheet.add_worksheet(title="project_metadata", rows=100, cols=5)
                existing_data = []
                start_row = 1
        
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
            data = [
                ["バッチID", batch_id],
                ["目標ID", self.current_goal['goal_id'] if self.current_goal else ''],
                ["分析結果", task_plan.get('project_analysis', '')],
                ["", ""],
                ["リスク", ""],
            ]
        
            for risk in task_plan.get('risks', []):
                data.append(["", risk])
        
            data.append(["", ""])
            data.append(["成功基準", ""])
        
            for criteria in task_plan.get('success_criteria', []):
                data.append(["", criteria])
        
            if existing_data:
                data = [["", ""], ["="*50, "="*50]] + data
        
            end_row = start_row + len(data) - 1
            meta_sheet.update(f'A{start_row}:B{end_row}', data)
            logger.info("プロジェクトメタデータを保存しました")
        
        except Exception as e:
            logger.warning(f"メタデータ保存に失敗: {e}")
    
    def display_task_summary(self, task_plan: Dict):
        """タスク概要を表示"""
        print("\n" + "="*60)
        print("PM AIによるタスク分解結果")
        print("="*60)
        
        print(f"\n【プロジェクト分析】")
        print(task_plan.get('project_analysis', ''))
        
        print(f"\n【生成されたタスク: {len(task_plan.get('tasks', []))}件】")
        for i, task in enumerate(task_plan.get('tasks', []), 1):
            role_icon = {
                'design': '📐',
                'dev': '💻',
                'ui': '🎨',
                'review': '✅'
            }.get(task.get('required_role', 'dev'), '📋')
            
            priority_icon = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(task.get('priority', 'medium'), '⚪')
            
            print(f"{i}. {priority_icon} {role_icon} {task.get('description', '')}")
            print(f"   担当: {task.get('required_role', 'dev')} | 優先度: {task.get('priority', 'medium')}")
            if task.get('dependencies'):
                print(f"   依存: タスク {task.get('dependencies')}")
            print()
        
        if task_plan.get('risks'):
            print(f"\n【想定リスク】")
            for risk in task_plan.get('risks', []):
                print(f"- {risk}")
        
        if task_plan.get('success_criteria'):
            print(f"\n【成功基準】")
            for criteria in task_plan.get('success_criteria', []):
                print(f"- {criteria}")
        
        print("="*60)

async def main():
    """PM AI単体テスト用のメイン関数"""
    import argparse
        
    # === パート1: 引数解析 ===
    parser = argparse.ArgumentParser(description='PM AI - タスク分解エージェント')
    parser.add_argument('--goal', type=str, help='直接目標を指定する（スプレッドシートを使わない場合）')
    args = parser.parse_args()
        
    # === パート2: 起動ヘッダー ===
    print("="*60)
    print("PM AI起動中...")
    print("="*60)
        
    # === パート3: サービスアカウント設定 ===
    default_service_account = r"C:\Users\color\Documents\gemini_auto_generate\service_account.json"
    service_account_file = default_service_account if Path(default_service_account).exists() else None
        
    # === パート4: シートマネージャー初期化 ===
    sheets_manager = GoogleSheetsManager(config.SPREADSHEET_ID, service_account_file)
        
    # === パート5: PC設定の読み込み ===
    pc_id = sheets_manager.get_current_pc_id()
    settings = sheets_manager.load_pc_settings(pc_id)
        
    config.BROWSER_DATA_DIR = settings.get('browser_data_dir')
    config.COOKIES_FILE = settings.get('cookies_file')
    config.GENERATION_MODE = 'text'
    config.SERVICE_TYPE = 'google'
        
    # === パート6: ダウンロードフォルダ設定 ===
    download_folder = Path(r"C:\Users\color\Documents\gemini_auto_generate\temp_texts")
    download_folder.mkdir(exist_ok=True, parents=True)
        
    # === パート7: ブラウザコントローラーの初期化 ===
    browser = BrowserController(download_folder, mode='text', service='google')
    await browser.setup_browser()
        
    logger.info("Geminiにアクセス中...")
    await browser.navigate_to_gemini()
        
    # === パート8: PMエージェントの初期化 ===
    pm_agent = PMAgent(sheets_manager, browser)
        
    # === パート9: 目標の取得（コマンドライン or シート）===
    if args.goal:
        goal_description = args.goal
        logger.info(f"コマンドラインから目標を取得: {goal_description}")
    else:
        goal = await pm_agent.load_project_goal()
        if not goal:
            print("\nエラー: アクティブな目標が見つかりません")
            print("スプレッドシートの'project_goal'シートにstatusが'active'の目標を設定してください")
            await browser.cleanup()
            return
        goal_description = goal['description']
        
    try:
        # === パート10: タスク計画の生成 ===
        task_plan = await pm_agent.analyze_and_create_tasks(goal_description)
            
        # === パート11: タスク概要の表示 ===
        pm_agent.display_task_summary(task_plan)
            
        # === パート12: ユーザー確認と保存 ===
        save = input("\nタスクをスプレッドシートに保存しますか？ (y/n): ")
        if save.lower() == 'y':
            success = await pm_agent.save_tasks_to_sheet(task_plan)
            if success:
                print("タスクを保存しました")
            else:
                print("保存に失敗しました")
            
    except Exception as e:
        # === パート13: 例外処理 ===
        logger.error(f"PM AI実行エラー: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # === パート14: クリーンアップ ===
        await browser.cleanup()
        print("\nPM AIを終了しました")

if __name__ == "__main__":
    asyncio.run(main())
