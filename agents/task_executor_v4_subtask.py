"""
TaskExecutor v4 Sub-task - 大規模コード生成エンジン
Version: 4.0
機能: Story→Sub-task分解と大規模コード生成
"""

import asyncio
from typing import Any, Dict, List


class SubTaskDecomposer:
    """StoryをSub-taskに分解するクラス"""

    def __init__(self, knowledge_manager=None):
        self.knowledge_manager = knowledge_manager
        self.model_name = "gemini-2.5-flash"
        self.max_tokens = 32000

    async def decompose_story_to_subtasks(self, story_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Storyを3-5個のSub-taskに分解"""
        print(f"🔧 Story分解開始: {story_data.get('title', 'N/A')}")

        # プロンプト作成
        prompt = self._create_subtask_prompt(story_data)

        # ナレッジ検索（オプション）
        knowledge_context = await self._search_related_knowledge(story_data)

        # Sub-task生成（スタブ実装）
        subtasks = await self._generate_subtasks(story_data, prompt, knowledge_context)

        print(f"✅ Story分解完了: {len(subtasks)}個のSub-taskを生成")
        return subtasks

    def _create_subtask_prompt(self, story_data: Dict[str, Any]) -> str:
        """Sub-task分解用プロンプトを作成"""
        return f"""
以下のStoryを3-5個の実装Sub-taskに分解してください。

## Story情報:
タイトル: {story_data.get('title', 'N/A')}
説明: {story_data.get('description', 'N/A')}
見積もり: {story_data.get('estimation', 'N/A')}
優先度: {story_data.get('priority', 'N/A')}
カテゴリ: {story_data.get('category', 'N/A')}

## 出力形式:
各Sub-taskについて以下の情報をJSON形式で出力:
- title: Sub-taskタイトル (30文字以内)
- description: 実装内容の詳細説明 (400-600文字)
- estimated_lines: 見積もり行数 (200-400行)
- dependencies: 依存関係 (他のSub-taskタイトル)
- output_files: 出力ファイルのリスト
- technical_requirements: 技術的要件

## 注意事項:
- 各Sub-taskは200-400行のコード生成に適した単位に分割
- 実装の順序と依存関係を明確に
- テストとドキュメントを含める
- 具体的な出力ファイルを指定
"""

    async def _search_related_knowledge(self, story_data: Dict[str, Any]) -> str:
        """関連ナレッジを検索"""
        if not self.knowledge_manager:
            return "ナレッジマネージャーなし"

        try:
            keywords = [
                story_data.get("title", ""),
                story_data.get("category", ""),
                "コード生成",
                "実装パターン",
            ]

            context = ""
            for keyword in keywords:
                if keyword:
                    results = self.knowledge_manager.search_knowledge(keyword, limit=2)
                    for result in results:
                        context += (
                            f"・{result.get('title', '')}: {result.get('content', '')[:150]}...\n"
                        )

            return context if context else "関連ナレッジなし"
        except Exception as e:
            print(f"⚠️ ナレッジ検索エラー: {e}")
            return "ナレッジ検索エラー"

    async def _generate_subtasks(
        self, story_data: Dict[str, Any], prompt: str, knowledge_context: str
    ) -> List[Dict[str, Any]]:
        """Sub-taskを生成（スタブ実装）"""
        # 実際の実装ではGemini APIを呼び出す
        await asyncio.sleep(0.5)  # 擬似処理

        # テスト用のダミーSub-task
        dummy_subtasks = [
            {
                "title": "APIエンドポイントの基本実装",
                "description": "FastAPIルーターの設定と基本エンドポイントの実装。GET/POST/PUT/DELETEメソッドの定義とリクエスト/レスポンスモデルの作成。",
                "estimated_lines": 250,
                "dependencies": "",
                "output_files": ["src/api/main.py", "src/api/routes.py", "src/api/models.py"],
                "technical_requirements": "FastAPI, Pydantic, 非同期処理",
            },
            {
                "title": "データベースモデルと接続設定",
                "description": "SQLAlchemyモデルの定義とデータベース接続の設定。テーブルマッピング、リレーションシップ、マイグレーションスクリプトの作成。",
                "estimated_lines": 300,
                "dependencies": "APIエンドポイントの基本実装",
                "output_files": [
                    "src/database/models.py",
                    "src/database/connection.py",
                    "alembic/versions/initial.py",
                ],
                "technical_requirements": "SQLAlchemy, PostgreSQL, Alembic",
            },
            {
                "title": "ユーザー認証システムの実装",
                "description": "JWTベースの認証システムの実装。ユーザー登録、ログイン、パスワードハッシュ化、トークン検証機能を含む。",
                "estimated_lines": 350,
                "dependencies": "データベースモデルと接続設定",
                "output_files": [
                    "src/auth/authentication.py",
                    "src/auth/jwt_handler.py",
                    "src/auth/models.py",
                ],
                "technical_requirements": "JWT, bcrypt, セキュリティ",
            },
        ]

        return dummy_subtasks


class SubTaskMemoryManager:
    """Sub-task結果のメモリ管理クラス"""

    def __init__(self):
        self.subtask_results = {}
        self.current_story_id = None

    def store_subtask_result(self, story_id: str, subtask_id: str, result: Dict[str, Any]):
        """Sub-task結果を保存"""
        if story_id not in self.subtask_results:
            self.subtask_results[story_id] = {}

        self.subtask_results[story_id][subtask_id] = result
        print(f"💾 Sub-task結果保存: {story_id}/{subtask_id}")

    def get_story_subtasks(self, story_id: str) -> Dict[str, Any]:
        """Storyの全Sub-task結果を取得"""
        return self.subtask_results.get(story_id, {})

    def clear_story_data(self, story_id: str):
        """Storyデータをクリア"""
        if story_id in self.subtask_results:
            del self.subtask_results[story_id]
            print(f"🧹 Storyデータ削除: {story_id}")


class TaskExecutorV4SubTask:
    """TaskExecutor v4 - Sub-task実行エンジン"""

    def __init__(self, sheets_manager=None, knowledge_manager=None):
        self.sheets_manager = sheets_manager
        self.knowledge_manager = knowledge_manager

        # サブコンポーネント初期化
        self.subtask_decomposer = SubTaskDecomposer(knowledge_manager)
        self.memory_manager = SubTaskMemoryManager()

        print("✅ TaskExecutorV4SubTask 初期化完了")

    async def execute_story(self, story_data: Dict[str, Any]) -> bool:
        """Storyを実行（Sub-task分解→実行→統合準備）"""
        try:
            story_id = story_data.get("id", f"story_{hash(str(story_data))}")
            print(f"🎯 Story実行開始: {story_data.get('title', 'N/A')}")

            # 1. StoryをSub-taskに分解
            subtasks = await self.subtask_decomposer.decompose_story_to_subtasks(story_data)

            if not subtasks:
                print("❌ Sub-task分解失敗")
                return False

            # 2. 各Sub-taskを実行（スタブ）
            for i, subtask in enumerate(subtasks, 1):
                subtask_id = f"{story_id}_subtask_{i}"
                print(f"  🔧 Sub-task実行中: {subtask['title']}")

                # Sub-task実行（スタブ）
                result = await self._execute_subtask(subtask)

                # 結果を保存
                self.memory_manager.store_subtask_result(
                    story_id,
                    subtask_id,
                    {"subtask_data": subtask, "execution_result": result, "status": "completed"},
                )

            # 3. 統合準備完了
            print(f"✅ Story実行完了: {len(subtasks)}個のSub-taskを実行")
            return True

        except Exception as e:
            print(f"❌ Story実行エラー: {e}")
            return False

    async def _execute_subtask(self, subtask: Dict[str, Any]) -> Dict[str, Any]:
        """個別Sub-taskを実行（スタブ）"""
        # 実際の実装ではGemini APIを使用したコード生成
        await asyncio.sleep(1)  # 擬似処理

        return {
            "generated_code": f"# 生成コード: {subtask['title']}\n# 行数: {subtask['estimated_lines']}",
            "output_files": subtask.get("output_files", []),
            "quality_score": 0.85,
            "execution_time": 2.5,
        }

    def get_integration_data(self, story_id: str) -> Dict[str, Any]:
        """統合用データを取得"""
        return self.memory_manager.get_story_subtasks(story_id)
