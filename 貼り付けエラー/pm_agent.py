import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from configuration.config_utils import config, ErrorHandler
from tools.sheets_manager import GoogleSheetsManager
from browser_control.browser_controller import BrowserController

logger = logging.getLogger(__name__)

class PMAgent:
    """PM AI - プロジェクト管理とタスク分解を担当"""
    
    # PM AIのシステムプロンプト
# pm_agent.py (改善版)

    PM_SYSTEM_PROMPT = """あなたは経験豊富なプロジェクトマネージャーAIです。

【あなたの役割】
- プロジェクトの目標を分析し、達成に必要なタスクに分解する
- 各タスクに適切な担当者（AI エージェント）を割り当てる
- **多言語対応プロジェクトでは、必ず言語とPolylang設定を明記する**
- **開発タスクは原則WordPressで実装可能か検討する**
- タスクの優先順位を決定する
- 実現可能で具体的なタスクを作成する

【重要: WordPress優先開発ポリシー】
このプロジェクトは **WordPress中心の開発スタイル** を採用しています。
以下の優先順位でエージェントを選択してください:

**優先度1: WordPress実装**
- 企業検索システム → **wordpress**: Custom Post Type + カスタムフィールド + 検索フォーム
- データベース設計 → **wordpress**: WordPress標準のデータ構造を活用
- UI/画面デザイン → **wordpress**: テーマカスタマイズ、ページビルダー
- フォーム作成 → **wordpress**: プラグイン（Contact Form 7など）or カスタムフィールド

**優先度2: 高度な開発（WordPressで困難な場合のみ）**
- 複雑なアルゴリム → **dev**: カスタムプラグイン開発
- 外部API連携 → **dev**: REST API統合
- 特殊なアーキテクチャ → **design**: システム設計後にdev実装

**判断基準:**
「WordPressの標準機能やプラグインで実現できるか？」
→ YES: wordpressエージェント
→ NO: design → dev エージェント

【利用可能なAIエージェント】

**開発・設計系エージェント:**
- **design** (設計AI): システム設計、アーキテクチャ設計、要件定義書作成、データベース設計、API仕様書作成
- **dev** (開発AI): コーディング、テストコード作成、実装、複数言語対応（Python, JavaScript, PHPなど）
- **ui** (UI/UX AI): ユーザーインターフェース設計、画面設計、UX最適化

**コンテンツ作成系エージェント:**
- **writer** (汎用ライターAI): ブログ記事作成、HTML記事執筆、SEOコンテンツ作成（後方互換性のため残す）
- **writer_ja** (日本語ライターAI): 日本語記事作成、品質重視、日本のビジネスオーナー向け
- **writer_en** (英語ライターAI): 英語記事作成、SEO最適化、国際投資家向け
- **writer_ru** (ロシア語ライターAI): ロシア語記事作成、現地ビジネス向け
- **writer_uz** (ウズベク語ライターAI): ウズベク語記事作成、現地企業向け
- **writer_zh** (中国語ライターAI): 中国語記事作成、中国投資家向け
- **writer_ko** (韓国語ライターAI): 韓国語記事作成、韓国ビジネス向け
- **writer_tr** (トルコ語ライターAI): トルコ語記事作成、トルコビジネス向け
- **content** (コンテンツAI): writerのエイリアス（後方互換性）

**WordPress・プラグイン系エージェント:**
- **wordpress** (WordPressAI): WordPress投稿、記事公開、記事編集、Polylang言語設定、下書き保存
- **plugin** (プラグインAI): WordPressプラグイン管理、インストール、設定変更

**品質管理系エージェント:**
- **review** (レビューAI): 品質チェック、コードレビュー、記事レビュー、出力物評価

【重要: 言語指定のルール】
1. **記事作成タスク**には必ず以下を含める:
   - `language`: 対象言語コード (ja/en/ru/uz/zh/ko/tr)
   - `polylang_lang`: Polylangの言語設定 (ja/en/ru/uz_UZ/zh_CN/ko_KR/tr_TR)
   - `target_url`: 参照元URL（ある場合）

2. **WordPress投稿タスク**には必ず以下を含める:
   - `language`: 投稿先言語
   - `polylang_lang`: Polylang言語コード
   - `source_task_id`: 元記事のタスクID
   - `post_action`: "create" または "edit"

3. **レビュータスク**には以下を含める:
   - `review_language`: レビュー対象の言語
   - `review_target_task_id`: レビュー対象タスクID

【タスク分解の基本フロー】

**パターン1: 多言語コンテンツ作成プロジェクト**
```
1. [writer_ja] 日本語で記事作成 (language=ja, polylang_lang=ja)
2. [review] 日本語記事の品質チェック
3. [writer_en] 英語で記事作成 (language=en, polylang_lang=en)
4. [wordpress] 英語記事をWordPressに投稿 (polylang_lang=en)
5. [writer_ru] ロシア語で記事作成 (language=ru, polylang_lang=ru)
6. [wordpress] ロシア語記事をWordPressに投稿 (polylang_lang=ru)
... (他言語も同様)
```

**パターン2: ポータルサイト機能開発プロジェクト**
```
1. [design] 企業検索システムの要件定義と設計書作成
2. [design] データベーススキーマ設計（企業情報テーブル）
3. [dev] データベース実装（SQL/WordPress Custom Post Type）
4. [dev] 検索フィルタリング機能実装（業種、売上、利益で絞り込み）
5. [ui] 検索画面のUI設計とHTML/CSSコーディング
6. [dev] WordPress管理画面でのデータ入力フォーム作成
7. [review] 機能全体の品質チェックとテスト
```

**パターン3: プラグイン追加・設定プロジェクト**
```
1. [plugin] Polylangプラグインのインストールと有効化
2. [plugin] Polylangで7言語設定（ja, en, ru, uz_UZ, zh_CN, ko_KR, tr_TR）
3. [plugin] Yoast SEOプラグインのインストール
4. [plugin] Yoast SEOの多言語SEO設定
```

**パターン4: 統合開発プロジェクト（開発+コンテンツ）**
```
1. [design] ポータルサイト全体のアーキテクチャ設計
2. [dev] 企業情報管理システムの実装
3. [ui] ポータルサイトのデザイン実装
4. [writer_ja] 日本語でサイト説明文作成
5. [writer_en] 英語でサイト説明文作成
6. [wordpress] 各言語ページを投稿
7. [review] サイト全体の品質チェック
```

【出力形式】
必ずJSON形式で出力してください：
```json
{
  "project_analysis": "目標の分析結果（100文字程度）",
  "tasks": [
    {
      "task_id": 1,
      "description": "【設計】企業検索システムの要件定義書を作成",
      "required_role": "design",
      "priority": "high",
      "estimated_time": "3時間",
      "dependencies": []
    },
    {
      "task_id": 2,
      "description": "【開発】企業情報データベースをWordPress Custom Post Typeで実装",
      "required_role": "dev",
      "priority": "high",
      "estimated_time": "5時間",
      "dependencies": [1]
    },
    {
      "task_id": 3,
      "description": "【日本語】ウズベキスタンのM&A市場に関する記事を作成（https://example.com/news/123を参照）",
      "required_role": "writer_ja",
      "priority": "high",
      "estimated_time": "2時間",
      "dependencies": [],
      "language": "ja",
      "polylang_lang": "ja",
      "target_url": "https://example.com/news/123"
    },
    {
      "task_id": 4,
      "description": "【レビュー】タスク3（日本語記事）の品質チェック",
      "required_role": "review",
      "priority": "high",
      "estimated_time": "30分",
      "dependencies": [3],
      "review_language": "ja",
      "review_target_task_id": 3
    },
    {
      "task_id": 5,
      "description": "【英語】ウズベキスタンのM&A市場に関する記事を作成（タスク3の内容を英語で展開）",
      "required_role": "writer_en",
      "priority": "high",
      "estimated_time": "2時間",
      "dependencies": [4],
      "language": "en",
      "polylang_lang": "en",
      "reference_task_id": 3
    },
    {
      "task_id": 6,
      "description": "【WordPress投稿】タスク5の英語記事をWordPressに投稿（Polylang: 英語）",
      "required_role": "wordpress",
      "priority": "medium",
      "estimated_time": "30分",
      "dependencies": [5],
      "language": "en",
      "polylang_lang": "en",
      "source_task_id": 5,
      "post_action": "create"
    },
    {
      "task_id": 7,
      "description": "【UI設計】企業検索画面のデザインとHTML/CSS実装",
      "required_role": "ui",
      "priority": "medium",
      "estimated_time": "4時間",
      "dependencies": [2]
    }
  ],
  "risks": ["想定されるリスク1", "リスク2"],
  "success_criteria": ["成功基準1", "基準2"]
}
```

【重要な注意事項】
- タスク説明の冒頭に必ず【言語名】を付ける
- WordPress投稿タスクには必ず`source_task_id`を指定
- 各言語専用のライターエージェントを正しく指定する
- Polylang言語コードを正確に記載する
  - 日本語: ja
  - 英語: en
  - ロシア語: ru
  - ウズベク語: uz_UZ
  - 中国語: zh_CN
  - 韓国語: ko_KR
  - トルコ語: tr_TR
"""

    def __init__(self, sheets_manager: GoogleSheetsManager, browser_controller: BrowserController):
        self.sheets_manager = sheets_manager
        self.browser = browser_controller
        self.current_goal = None
        self.generated_tasks = []
    
    async def load_project_goal(self) -> Optional[Dict]:
        """project_goalシートから最新のアクティブな目標を読み込む"""
        try:
            logger.info("プロジェクト目標を読み込み中...")
            sheet = self.sheets_manager.gc.open_by_key(self.sheets_manager.spreadsheet_id)
            
            try:
                goal_sheet = sheet.worksheet("project_goal")
            except:
                logger.error("'project_goal'シートが見つかりません")
                logger.info("スプレッドシートに'project_goal'シートを作成してください")
                return None
            
            # 全データを取得
            all_values = goal_sheet.get_all_values()
            
            if len(all_values) <= 1:
                logger.warning("目標が設定されていません")
                return None
            
            # ヘッダー行をスキップして、最初のアクティブな目標を取得
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
            
            logger.warning("アクティブな目標が見つかりません（statusが'active'のものがありません）")
            return None
            
        except Exception as e:
            ErrorHandler.log_error(e, "目標読み込み")
            raise
    
    async def analyze_and_create_tasks(self, goal_description: str) -> Dict:
        """目標を分析してタスクを生成"""
        try:
            logger.info("="*60)
            logger.info("PM AI: タスク分解を開始します")
            logger.info("="*60)
    
            # プロンプトを構築（JSON出力を徹底 + 長さ制限）
            full_prompt = f"""{self.PM_SYSTEM_PROMPT}

    【プロジェクト目標】
    {goal_description}

    【重要な出力指示】
    1. **必ず有効なJSON形式のみで出力してください**
    2. 説明文、コメント、挨拶などは一切不要です
    3. ```json と ``` で囲む必要はありません
    4. 最初の文字が {{ で、最後の文字が }} の完全なJSON形式のみを出力してください
    5. **タスク数は最大15個まで**とし、JSONが長くなりすぎないようにしてください
    6. すべての文字列値は正しくダブルクォーテーションで囲んでください
    7. 配列やオブジェクトの最後の要素にカンマを付けないでください

    **出力するJSON形式（この形式を厳密に守ってください）:**
    {{
      "project_analysis": "プロジェクトの分析結果（200文字以内）",
      "tasks": [
        {{
          "task_id": 1,
          "description": "タスクの説明",
          "required_role": "design",
          "priority": "high",
          "estimated_time": "3時間",
          "dependencies": []
        }},
        {{
          "task_id": 2,
          "description": "別のタスク",
          "required_role": "dev",
          "priority": "medium",
          "estimated_time": "2時間",
          "dependencies": [1]
        }}
      ],
      "risks": ["リスク1", "リスク2"],
      "success_criteria": ["基準1", "基準2"]
    }}

    **再確認:**
    - 最初の文字は {{ で始まる
    - 最後の文字は }} で終わる
    - すべてのキーと文字列値はダブルクォーテーション
    - 配列の最後の要素にカンマなし
    - タスクは15個まで

    上記の目標を達成するために必要なタスクを、上記のJSON形式で出力してください。"""
    
            # Geminiに送信
            logger.info("Geminiに送信中...")
            await self.browser.send_prompt(full_prompt)
    
            # テキスト生成完了を待機
            logger.info("PM AIの分析を待機中...")
            success = await self.browser.wait_for_text_generation(max_wait=180)
    
            if not success:
                raise Exception("PM AIのタスク生成がタイムアウトしました")
    
            # 応答を取得
            response_text = await self.browser.extract_latest_text_response()
    
            if not response_text:
                raise Exception("PM AIからの応答が取得できませんでした")
    
            logger.info(f"PM AIの応答を取得しました（{len(response_text)}文字）")
    
            # デバッグ: 応答の先頭と末尾を表示
            logger.info(f"応答の先頭500文字:\n{response_text[:500]}")
            logger.info(f"応答の末尾500文字:\n{response_text[-500:]}")
    
            # JSONをパース（強化版メソッドを使用）
            task_plan = self._parse_json_response(response_text)
    
            if task_plan:
                logger.info("="*60)
                logger.info("PM AI: タスク分解完了")
                logger.info(f"生成されたタスク数: {len(task_plan.get('tasks', []))}")
                logger.info("="*60)
                self.generated_tasks = task_plan.get('tasks', [])
                return task_plan
            else:
                # パース失敗時のフォールバック
                logger.error("JSON解析に失敗しました。応答全体を保存します。")
                fallback_path = Path("pm_ai_response_error.txt")
                with open(fallback_path, 'w', encoding='utf-8') as f:
                    f.write(response_text)
                logger.info(f"応答を保存しました: {fallback_path}")
        
                # ユーザーに手動修正を促す
                logger.error("="*60)
                logger.error("❌ 自動修復も失敗しました")
                logger.error("="*60)
                logger.error("以下の対処方法を試してください:")
                logger.error("1. pm_ai_response_error.txt を開く")
                logger.error("2. JSONを手動で修正する")
                logger.error("3. 修正したJSONを pm_ai_response_fixed.json として保存")
                logger.error("4. プログラムを再実行")
            
                # 修正済みファイルが存在するか確認
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
        """応答からJSON部分を抽出してパース"""
        try:
            # ```json ... ``` で囲まれている場合
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)
            
            # 単純なJSONオブジェクト
            json_match = re.search(r'(\{.*\})', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)
            
            # パースできない場合
            logger.warning("JSONパース失敗。生テキストを確認してください")
            logger.info(f"応答の先頭500文字:\n{text[:500]}")
            return None
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析エラー: {e}")
            return None
    
    # pm_agent.py の save_tasks_to_sheet メソッドを修正

    async def save_tasks_to_sheet(self, task_plan: Dict) -> bool:
        """生成されたタスクをスプレッドシートに保存（追加方式）"""
        try:
            logger.info("タスクをスプレッドシートに保存中...")
        
            sheet = self.sheets_manager.gc.open_by_key(self.sheets_manager.spreadsheet_id)
        
            # pm_tasksシートを取得または作成
            try:
                task_sheet = sheet.worksheet("pm_tasks")
                # 既存のデータがある場合は次の行から追加
                existing_data = task_sheet.get_all_values()
                start_row = len(existing_data) + 1
            
                # ヘッダーが存在しない場合は作成
                if len(existing_data) == 0:
                    headers = [
                        "task_id", "parent_goal_id", "task_description", 
                        "required_role", "status", "priority", 
                        "estimated_time", "dependencies", "created_at", "batch_id"
                    ]
                    task_sheet.update('A1:J1', [headers])
                    start_row = 2
                
            except:
                logger.info("'pm_tasks'シートを作成します")
                task_sheet = sheet.add_worksheet(title="pm_tasks", rows=1000, cols=10)
                # ヘッダー行を作成
                headers = [
                    "task_id", "parent_goal_id", "task_description", 
                    "required_role", "status", "priority", 
                    "estimated_time", "dependencies", "created_at", "batch_id"
                ]
                task_sheet.update('A1:J1', [headers])
                start_row = 2
                existing_data = []
        
            # バッチIDを生成（この実行を識別するため）
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
            # 既存のタスクIDの最大値を取得
            existing_task_ids = []
            if len(existing_data) > 1:
                for row in existing_data[1:]:
                    if row and row[0].isdigit():
                        existing_task_ids.append(int(row[0]))
        
            next_task_id = max(existing_task_ids) + 1 if existing_task_ids else 1
        
            # タスクデータを準備
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
                    batch_id  # 同じバッチのタスクをグループ化
                ]
                rows_data.append(row)
        
            # データを追加
            if rows_data:
                end_row = start_row + len(rows_data) - 1
                task_sheet.update(f'A{start_row}:J{end_row}', rows_data)
                logger.info(f"タスク {len(rows_data)} 件を追加しました（バッチ: {batch_id}）")
        
            # プロジェクト分析とリスクも別シートに保存（こちらは上書きでよい）
            self._save_project_metadata(task_plan)
        
            return True
        
        except Exception as e:
            ErrorHandler.log_error(e, "タスク保存")
            return False
    
    # pm_agent.py の _save_project_metadata メソッドを修正

    def _save_project_metadata(self, task_plan: Dict):
        """プロジェクトのメタ情報（分析結果、リスク、成功基準）を保存（追加方式）"""
        try:
            sheet = self.sheets_manager.gc.open_by_key(self.sheets_manager.spreadsheet_id)
        
            try:
                meta_sheet = sheet.worksheet("project_metadata")
                existing_data = meta_sheet.get_all_values()
                # 既存のデータがある場合は区切り線を追加してから新しいデータを追加
                start_row = len(existing_data) + 2  # 1行空けて追加
            except:
                meta_sheet = sheet.add_worksheet(title="project_metadata", rows=100, cols=5)
                existing_data = []
                start_row = 1
        
            # バッチIDとタイムスタンプ
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
            # メタ情報を書き込み
            data = [
                ["バッチID", batch_id],
                ["目標ID", self.current_goal['goal_id'] if self.current_goal else ''],
                ["分析結果", task_plan.get('project_analysis', '')],
                ["", ""],
                ["リスク", ""],
            ]
        
            risk_row_count = 0
            for risk in task_plan.get('risks', []):
                data.append(["", risk])
                risk_row_count += 1
        
            data.append(["", ""])
            data.append(["成功基準", ""])
        
            criteria_row_count = 0
            for criteria in task_plan.get('success_criteria', []):
                data.append(["", criteria])
                criteria_row_count += 1
        
            # 区切り線を追加
            if existing_data:
                data = [["", ""], ["="*50, "="*50]] + data
        
            # データを書き込み
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
    
    parser = argparse.ArgumentParser(description='PM AI - タスク分解エージェント')
    parser.add_argument('--goal', type=str, help='直接目標を指定する（スプレッドシートを使わない場合）')
    args = parser.parse_args()
    
    print("="*60)
    print("PM AI起動中...")
    print("="*60)
    
    # 設定の読み込み
    default_service_account = r"C:\Users\color\Documents\gemini_auto_generate\service_account.json"
    service_account_file = default_service_account if Path(default_service_account).exists() else None
    
    sheets_manager = GoogleSheetsManager(config.SPREADSHEET_ID, service_account_file)
    
    # PC_IDを取得して設定を読み込み
    pc_id = sheets_manager.get_current_pc_id()
    settings = sheets_manager.load_pc_settings(pc_id)
    
    config.BROWSER_DATA_DIR = settings.get('browser_data_dir')
    config.COOKIES_FILE = settings.get('cookies_file')
    config.GENERATION_MODE = 'text'
    config.SERVICE_TYPE = 'google'
    
    # ブラウザコントローラーを初期化
    download_folder = Path(r"C:\Users\color\Documents\gemini_auto_generate\temp_texts")
    download_folder.mkdir(exist_ok=True, parents=True)
    
    browser = BrowserController(download_folder, mode='text', service='google')
    await browser.setup_browser()
    
    # Geminiにアクセス
    logger.info("Geminiにアクセス中...")
    await browser.navigate_to_gemini()
    
    # PM AIインスタンスを作成
    pm_agent = PMAgent(sheets_manager, browser)
    
    # 目標を取得
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
    
    # タスクを生成
    try:
        task_plan = await pm_agent.analyze_and_create_tasks(goal_description)
        
        # 結果を表示
        pm_agent.display_task_summary(task_plan)
        
        # スプレッドシートに保存
        save = input("\nタスクをスプレッドシートに保存しますか？ (y/n): ")
        if save.lower() == 'y':
            success = await pm_agent.save_tasks_to_sheet(task_plan)
            if success:
                print("タスクを保存しました")
            else:
                print("保存に失敗しました")
        
    except Exception as e:
        logger.error(f"PM AI実行エラー: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await browser.cleanup()
        print("\nPM AIを終了しました")

if __name__ == "__main__":
    asyncio.run(main())