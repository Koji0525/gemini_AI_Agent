"""AI駆動コード生成エンジン"""

from pathlib import Path
from typing import Dict, List
import json


class AICodeGenerator:
    """Claude APIを使った高品質コード生成"""
    
    def __init__(self, knowledge_manager=None):
        self.knowledge_manager = knowledge_manager
        self.templates_dir = Path(__file__).parent / "templates"
    
    def generate_code(self, task: Dict) -> Dict[str, str]:
        """タスクから詳細コードを生成
        
        1. ナレッジベースから関連情報取得
        2. 過去の成功パターン分析
        3. Claude APIでコード生成
        4. 品質チェック
        """
        task_id = task.get("task_id", "unknown")
        description = task.get("description", "")
        task_type = self._detect_task_type(description)
        
        # ナレッジ検索
        related_knowledge = self._search_knowledge(description)
        
        # ベストプラクティス取得
        best_practices = self._get_best_practices(task_type)
        
        # プロンプト構築
        prompt = self._build_prompt(
            task=task,
            knowledge=related_knowledge,
            practices=best_practices
        )
        
        # Claude APIで生成（実装例）
        generated_code = self._call_claude_api(prompt)
        
        return {
            "main_code": generated_code["code"],
            "tests": generated_code["tests"],
            "readme": generated_code["readme"],
            "quality_score": generated_code["quality"]
        }
    
    def _detect_task_type(self, description: str) -> str:
        """タスクタイプを自動検出"""
        keywords = {
            "api": ["API", "REST", "endpoint", "FastAPI"],
            "cli": ["CLI", "コマンド", "Click"],
            "data": ["データ処理", "pandas", "分析"],
            "web": ["Web", "Flask", "Django"],
            "test": ["テスト", "pytest", "unittest"]
        }
        
        for task_type, words in keywords.items():
            if any(word in description for word in words):
                return task_type
        
        return "general"
    
    def _search_knowledge(self, description: str) -> List[Dict]:
        """ナレッジベースから関連情報取得"""
        if not self.knowledge_manager:
            return []
        
        # 過去の成功タスクを検索
        results = self.knowledge_manager.search_knowledge(
            query=description,
            limit=5
        )
        
        return results
    
    def _get_best_practices(self, task_type: str) -> List[str]:
        """タスクタイプ別のベストプラクティス"""
        practices = {
            "api": [
                "エラーハンドリングを実装",
                "OpenAPI仕様を生成",
                "認証・認可を考慮",
                "レート制限を実装"
            ],
            "cli": [
                "ヘルプ機能を充実",
                "エラーメッセージを明確に",
                "サブコマンドで機能分離",
                "設定ファイル対応"
            ],
            "data": [
                "データ検証を実装",
                "欠損値処理を明示",
                "パフォーマンス最適化",
                "ログ出力を充実"
            ]
        }
        
        return practices.get(task_type, [])
    
    def _build_prompt(self, task: Dict, knowledge: List, practices: List) -> str:
        """高品質なプロンプト構築"""
        return f"""# タスク
{task.get('description')}

# 関連する過去の成功例
{self._format_knowledge(knowledge)}

# ベストプラクティス
{chr(10).join(f'- {p}' for p in practices)}

# 要件
- 実用的で詳細な実装
- 充実したドキュメント
- エラーハンドリング
- テスト可能な設計

# 出力形式
以下の形式でコードを生成してください：
1. メインコード（200行以上）
2. テストコード
3. README（使い方、例、設定）
"""
    
    def _format_knowledge(self, knowledge: List) -> str:
        """ナレッジを整形"""
        if not knowledge:
            return "（関連する過去例なし）"
        
        return "\n".join([
            f"- {k.get('title', 'N/A')}: {k.get('summary', 'N/A')}"
            for k in knowledge[:3]
        ])
    
    def _call_claude_api(self, prompt: str) -> Dict:
        """Claude APIを呼び出し（実装例）"""
        # 実際のAPI呼び出しは別途実装
        # ここではモック
        return {
            "code": "# Generated code",
            "tests": "# Generated tests",
            "readme": "# Generated README",
            "quality": 85
        }


# TaskExecutorEnhancedへの統合例
class TaskExecutorEnhancedWithAI:
    def __init__(self):
        self.ai_generator = AICodeGenerator()
    
    def execute_task(self, task: Dict) -> Dict:
        """AI駆動でタスク実行"""
        
        # AI生成を試行
        try:
            generated = self.ai_generator.generate_code(task)
            
            # 生成されたコードを保存
            # ...
            
            return {
                "status": "completed",
                "quality_score": generated["quality_score"],
                "ai_generated": True
            }
        except Exception as e:
            # フォールバック：テンプレート使用
            return self._fallback_template_generation(task)
