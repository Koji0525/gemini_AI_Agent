"""
PMAgent v33 Epic - 大規模Epic分解エージェント
Version: 33.0
機能: Epic→Story分解、ナレッジ連携、スプレッドシート統合
"""

import asyncio
from typing import Any, Dict, List


class EpicTaskGenerator:
    """EpicをStoryに分解するジェネレーター"""

    def __init__(self, knowledge_manager=None):
        self.knowledge_manager = knowledge_manager
        self.model_name = "gemini-2.5-flash"
        self.max_tokens = 32000
        print(f"✅ EpicTaskGenerator 初期化: {self.model_name}, max_tokens={self.max_tokens}")

    async def generate_epic_breakdown(self, prompt: str) -> List[Dict[str, Any]]:
        """EpicをStoryに分解（スタブ実装）"""
        try:
            print("🤖 Epic分解実行中...")
            await asyncio.sleep(1)  # 擬似処理

            # テスト用のダミーStory
            dummy_stories = [
                {
                    "title": "バックエンドAPI基盤の構築",
                    "description": "FastAPIを使用したRESTful APIの設計と実装。ユーザー認証、JWTトークン管理、APIエンドポイントの設計を含む。データベース接続プールの設定と非同期処理の最適化を実施。詳細なエラーハンドリングとロギング機能を実装。",
                    "estimation": "3日",
                    "priority": "高",
                    "dependencies": "",
                    "category": "バックエンド",
                },
                {
                    "title": "データベーススキーマ設計",
                    "description": "PostgreSQLを使用したデータベース設計。テーブル正規化、インデックス設計、リレーションシップ定義。マイグレーションスクリプトの作成とデータ整合性の確保。パフォーマンスチューニングとバックアップ戦略の策定。",
                    "estimation": "2日",
                    "priority": "高",
                    "dependencies": "バックエンドAPI基盤",
                    "category": "データベース",
                },
            ]

            return dummy_stories

        except Exception as e:
            print(f"❌ Epic分解エラー: {e}")
            return []

    async def _call_gemini_api(self, prompt: str):
        """Gemini API呼び出し（スタブ）"""
        print(f"📝 プロンプト長: {len(prompt)}文字")
        return []


class PMAgentV33Epic:
    """PMAgent v33 - Epic分解エージェント"""

    def __init__(self, sheets_manager=None, knowledge_manager=None):
        self.sheets_manager = sheets_manager
        self.knowledge_manager = knowledge_manager
        self.epic_generator = EpicTaskGenerator(knowledge_manager=knowledge_manager)

        # SafeSheetsWrapper初期化
        from tools.safe_sheets_wrapper import SafeSheetsWrapper

        self.safe_sheets = SafeSheetsWrapper(sheets_manager) if sheets_manager else None

        print("✅ PMAgentV33Epic 初期化完了")

    async def decompose_epic_to_stories(self, epic_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """EpicをStoryに分解するメインメソッド"""
        print(f"🔧 Epic分解開始: {epic_data.get('title', 'N/A')}")

        try:
            # ナレッジ検索
            knowledge_context = await self._search_knowledge(epic_data)

            # Epic分解プロンプト作成
            prompt = self._create_epic_breakdown_prompt(epic_data, knowledge_context)

            # Gemini API呼び出し
            stories = await self.epic_generator.generate_epic_breakdown(prompt)

            print(f"✅ Epic分解完了: {len(stories)}個のStoryを生成")
            return stories

        except Exception as e:
            print(f"❌ Epic分解エラー: {e}")
            return []

    def _create_epic_breakdown_prompt(
        self, epic_data: Dict[str, Any], knowledge_context: str
    ) -> str:
        """Epic分解用のプロンプトを作成"""
        prompt = f"""
以下のEpicを8-12個の詳細なStoryに分解してください。

## Epic情報:
タイトル: {epic_data.get('title', 'N/A')}
説明: {epic_data.get('description', 'N/A')}
規模: {epic_data.get('scale', 'N/A')}
技術スタック: {epic_data.get('tech_stack', 'N/A')}
期限: {epic_data.get('deadline', 'N/A')}

## 関連ナレッジ:
{knowledge_context}

## 出力形式:
各Storyについて以下の情報をJSON形式で出力:
- title: Storyタイトル (50文字以内)
- description: 詳細説明 (2,500-3,000文字)
- estimation: 見積もり (例: "3日")
- priority: 優先度 ("高", "中", "低")
- dependencies: 依存関係 (他のStoryタイトル)
- category: カテゴリ ("バックエンド", "フロントエンド", "データベース", "テスト", "デプロイ")

## 注意事項:
- 各descriptionは2,500-3,000文字で詳細に記述
- 技術的な具体性を持たせる
- テストとデプロイを含める
- 依存関係を明確に
"""
        return prompt

    async def _search_knowledge(self, epic_data: Dict[str, Any]) -> str:
        """関連ナレッジを検索"""
        try:
            if self.knowledge_manager:
                # Epicのキーワードからナレッジ検索
                keywords = [
                    epic_data.get("title", ""),
                    epic_data.get("tech_stack", ""),
                    "大規模開発",
                    "エージェント開発",
                ]

                context = ""
                for keyword in keywords:
                    if keyword:
                        results = self.knowledge_manager.search_knowledge(keyword, limit=2)
                        for result in results:
                            context += f"・{result.get('title', '')}: {result.get('content', '')[:200]}...\n"

                return context if context else "関連ナレッジなし"
        except Exception as e:
            print(f"⚠️ ナレッジ検索エラー: {e}")

        return "ナレッジ検索なし"

    def write_stories_to_sheet(self, stories: List[Dict[str, Any]], epic_id: str) -> bool:
        """Storyをpm_tasksシートに書き込み"""
        try:
            if not self.safe_sheets:
                print("❌ SafeSheetsWrapperが初期化されていません")
                return False

            # Storyデータをシート形式に変換
            rows = []
            for i, story in enumerate(stories, 1):
                row = [
                    f"{epic_id}_story_{i}",  # task_id
                    story.get("title", ""),
                    story.get("description", ""),
                    story.get("estimation", ""),
                    story.get("priority", "中"),
                    "pending",  # status
                    "",  # assigned_to
                    "",  # start_date
                    "",  # end_date
                    story.get("dependencies", ""),
                    story.get("category", ""),
                    epic_id,  # goal_id
                    "",  # output_files
                ]
                rows.append(row)

            # pm_tasksシートに追加
            success = self.safe_sheets.safe_append("pm_tasks", rows)

            if success:
                print(f"✅ {len(rows)}個のStoryをpm_tasksに書き込み")
            else:
                print("❌ pm_tasks書き込み失敗")

            return success

        except Exception as e:
            print(f"❌ Story書き込みエラー: {e}")
            return False
