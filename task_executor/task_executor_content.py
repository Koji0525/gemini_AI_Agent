"""
task_executor_content.py
記事生成専用のタスク実行モジュール
task_executor.pyから分離
"""
import logging
from typing import Dict, List
from configuration.config_utils import ErrorHandler

logger = logging.getLogger(__name__)


class ContentTaskExecutor:
    """記事生成タスク専用の実行クラス"""
    
    def __init__(self, agents: Dict):
        self.agents = agents
    
    async def execute_writer_task(self, task: Dict, role: str) -> Dict:
        """言語別ライタータスクを実行"""
        # === パート1: タスク情報の抽出 ===
        task_language = task.get('language')
        polylang_lang = task.get('polylang_lang')
        
        # === パート2: 実行開始ヘッダー ===
        logger.info("┌" + "─"*58 + "┐")
        logger.info(f"│ ✏️ ライターAIエージェント実行中 ({role})")
        logger.info("├" + "─"*58 + "┤")
        logger.info(f"│ 言語: {task_language}")
        logger.info(f"│ Polylang: {polylang_lang}")
        logger.info("└" + "─"*58 + "┘")
        
        # === パート3: エージェントの選択と実行 ===
        if role == 'writer' or role == 'content':
            # === パート3-1: 汎用ライターの処理 ===
            logger.info("📝 汎用ライターを使用(後方互換性モード)")
            agent = self.agents.get('writer')
            if not agent:
                logger.error("❌ writerエージェントが登録されていません")
                return {
                    'success': False,
                    'error': 'writer エージェントが登録されていません'
                }
            result = await agent.process_task(task)
        else:
            # === パート3-2: 言語別ライターの処理 ===
            agent = self.agents.get(role)
            if not agent:
                logger.error(f"❌ {role}エージェントが登録されていません")
                return {
                    'success': False,
                    'error': f'未対応の言語ライター: {role}'
                }
            
            # === パート3-3: 言語確認 ===
            if task_language and hasattr(agent, 'get_language_code'):
                if agent.get_language_code() != task_language:
                    logger.warning(f"⚠️ 言語不一致: タスク={task_language}, ライター={agent.get_language_code()}")
            
            result = await agent.process_task(task)
        
        # === パート4: 結果の処理 ===
        if result.get('success'):
            logger.info(f"✅ ライターAI ({role}): タスク完了")
            # 言語情報を追加
            if hasattr(agent, 'get_language_code'):
                result['language'] = agent.get_language_code()
                result['polylang_lang'] = polylang_lang or agent.get_language_code()
        else:
            logger.error(f"❌ ライターAI ({role}): 失敗 - {result.get('error', '不明')}")
        
        return result
    
    def display_suggested_tasks(self, suggested_tasks: List[Dict]):
        """提案タスクの詳細を表示"""
        # === パート1: ヘッダー表示 ===
        print("\n" + "="*60)
        print("提案タスク詳細")
        print("="*60)

        # === パート2: 各タスクの詳細表示 ===
        for i, task in enumerate(suggested_tasks, 1):
            # === パート2-1: 優先度マークの設定 ===
            priority_mark = {
                'high': '🔴[高]',
                'medium': '🟡[中]', 
                'low': '🟢[低]'
            }.get(task.get('priority', 'medium'), '⚪[中]')
        
            # === パート2-2: 役割ラベルの設定 ===
            role_label = {
                'design': '📐[設計]',
                'dev': '💻[開発]',
                'ui': '🎨[UI]',
                'review': '✅[レビュー]',
                'wordpress': '🌐[WordPress]',
                'writer': '✏️[ライター]',
                'writer_ja': '🇯🇵[日本語]',
                'writer_en': '🇬🇧[英語]',
                'writer_ru': '🇷🇺[ロシア語]',
                'content': '📄[コンテンツ]'
            }.get(task.get('required_role', 'dev'), '📋[タスク]')
        
            # === パート2-3: タスク情報の表示 ===
            print(f"\n{i}. {priority_mark} {role_label} {task.get('description', 'N/A')}")
            print(f"   理由: {task.get('reasoning', 'N/A')}")
            print(f"   担当: {task.get('required_role', 'dev')}")
            print(f"   優先度: {task.get('priority', 'medium')}")

        # === パート3: フッター表示 ===
        print("="*60)
    
    async def edit_suggested_tasks(self, suggested_tasks: List[Dict]) -> List[Dict]:
        """提案タスクを編集"""
        try:
            # === パート1: 変数初期化 ===
            edited_tasks = []
        
            # === パート2: 各タスクの編集ループ ===
            for i, task in enumerate(suggested_tasks, 1):
                # === パート2-1: 現在のタスク情報表示 ===
                print(f"\n--- タスク {i}/{len(suggested_tasks)} の編集 ---")
                print(f"現在の内容:")
                print(f"  説明: {task.get('description', '')}")
                print(f"  担当: {task.get('required_role', 'dev')}")
                print(f"  優先度: {task.get('priority', 'medium')}")
                print(f"  理由: {task.get('reasoning', '')}")
            
                # === パート2-2: 編集オプション表示 ===
                print(f"\n編集オプション:")
                print("  (d)説明を変更 / (r)担当を変更 / (p)優先度を変更 / (e)理由を変更")
                print("  (s)このタスクをスキップ / (k)このタスクを保持 / (q)編集を終了")
            
                # === パート2-3: ユーザー入力の取得 ===
                edit_choice = input("選択: ").lower()
            
                # === パート2-4: 各選択肢の処理 ===
                if edit_choice == 'd':
                    # 説明変更
                    new_desc = input("新しい説明: ").strip()
                    if new_desc:
                        task['description'] = new_desc
                    edited_tasks.append(task)
                
                elif edit_choice == 'r':
                    # 担当変更
                    print("利用可能な担当:")
                    print("  design, dev, ui, review, wordpress, writer, writer_ja, writer_en, writer_ru, plugin")
                    new_role = input("新しい担当: ").strip()
                    valid_roles = ['design', 'dev', 'ui', 'review', 'wordpress', 'writer', 
                                'writer_ja', 'writer_en', 'writer_ru', 'writer_uz', 
                                'writer_zh', 'writer_ko', 'writer_tr', 'plugin', 'content']
                    if new_role in valid_roles:
                        task['required_role'] = new_role
                    else:
                        print("無効な担当です。変更しません。")
                    edited_tasks.append(task)
                
                elif edit_choice == 'p':
                    # 優先度変更
                    print("優先度: high, medium, low")
                    new_priority = input("新しい優先度: ").strip()
                    if new_priority in ['high', 'medium', 'low']:
                        task['priority'] = new_priority
                    else:
                        print("無効な優先度です。変更しません。")
                    edited_tasks.append(task)
                
                elif edit_choice == 'e':
                    # 理由変更
                    new_reason = input("新しい理由: ").strip()
                    if new_reason:
                        task['reasoning'] = new_reason
                    edited_tasks.append(task)
                
                elif edit_choice == 's':
                    # スキップ
                    print(f"タスク {i} をスキップしました")
                    continue
                
                elif edit_choice == 'k':
                    # 保持
                    edited_tasks.append(task)
                    print(f"タスク {i} をそのまま保持しました")
                
                elif edit_choice == 'q':
                    # 編集終了
                    print("編集を終了します")
                    break
                
                else:
                    # 不正な入力
                    print("不正な入力です。タスクをそのまま保持します。")
                    edited_tasks.append(task)
        
            # === パート3: 編集結果の表示 ===
            if edited_tasks:
                print(f"\n編集後のタスク ({len(edited_tasks)}件):")
                self.display_suggested_tasks(edited_tasks)
            
            return edited_tasks
        
        except Exception as e:
            # === パート4: 例外処理 ===
            ErrorHandler.log_error(e, "タスク編集")
            return suggested_tasks
    
    async def create_manual_tasks(self) -> List[Dict]:
        """手動でタスクを作成"""
        try:
            # === パート1: 変数初期化 ===
            manual_tasks = []
            
            # === パート2: 作成開始ヘッダー ===
            print("\n" + "="*60)
            print("手動タスク作成")
            print("="*60)
            print("新しいタスクを手動で作成します。")
            print("空の説明で終了します。")
            
            # === パート3: タスク作成ループ ===
            while True:
                # === パート3-1: タスクヘッダー表示 ===
                print(f"\n--- タスク {len(manual_tasks) + 1} ---")
                
                # === パート3-2: タスク説明の入力 ===
                description = input("タスク説明: ").strip()
                if not description:
                    break
                    
                # === パート3-3: 担当の入力 ===
                print("利用可能な担当: design, dev, ui, review, wordpress, writer, writer_ja, writer_en, writer_ru, plugin")
                role = input("担当 (デフォルト: dev): ").strip() or "dev"
                
                # === パート3-4: 優先度の入力 ===
                print("優先度: high, medium, low")
                priority = input("優先度 (デフォルト: medium): ").strip() or "medium"
                
                # === パート3-5: 理由の入力 ===
                reasoning = input("理由: ").strip()
                
                # === パート3-6: タスクオブジェクトの作成 ===
                task = {
                    'description': description,
                    'required_role': role,
                    'priority': priority,
                    'reasoning': reasoning
                }
                
                # === パート3-7: タスクリストへの追加 ===
                manual_tasks.append(task)
                print(f"タスクを追加しました (合計: {len(manual_tasks)}件)")
                
                # === パート3-8: 継続確認 ===
                more = input("さらにタスクを追加しますか? (y/n): ").lower()
                if more != 'y':
                    break
            
            # === パート4: 作成結果の表示 ===
            if manual_tasks:
                print(f"\n作成したタスク ({len(manual_tasks)}件):")
                self.display_suggested_tasks(manual_tasks)
                
            return manual_tasks
            
        except Exception as e:
            # === パート5: 例外処理 ===
            ErrorHandler.log_error(e, "手動タスク作成")
            return []