"""
CodeGenerationAgent - LLM統合によるコード自動生成エージェント
v1.15.0 - 2025-11-06 (v1 API対応版)

【責任範囲】
- タスク仕様からのコード自動生成
- RAGエンジンによる過去のナレッジ活用
- Gemini APIを使用した高度なコード生成
- 生成コードの構文チェックと品質評価
"""

import os
import ast
import json
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import google.generativeai as genai
from pathlib import Path


class CodeGenerationAgent:
    """コード自動生成エージェント"""

    def __init__(self, rag_engine=None):
        """
        初期化

        Args:
            rag_engine: RAGエンジンインスタンス（外部注入）
        """
        self.rag_engine = rag_engine
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY が設定されていません")

        genai.configure(api_key=self.gemini_api_key)

        # モデルを初期化（実際に利用可能なモデルを確認）
        self.model = self._initialize_model()
        self.generation_history = []

    def _initialize_model(self):
        """モデルを初期化（実際の利用可能モデルから選択）"""
        print("🔍 利用可能なモデルを確認中...")

        try:
            # 実際に利用可能なモデルを取得
            available_models = []
            for model in genai.list_models():
                if "generateContent" in model.supported_generation_methods:
                    available_models.append(model.name)

            if not available_models:
                raise ValueError("利用可能なモデルが見つかりません")

            # 環境変数から優先モデルを取得
            preferred_model = os.getenv("GEMINI_MODEL", "")

            # models/ プレフィックスを追加
            if preferred_model and not preferred_model.startswith("models/"):
                preferred_model = f"models/{preferred_model}"

            # 優先モデルが利用可能かチェック
            if preferred_model in available_models:
                model_name = preferred_model
            else:
                # 利用可能な最初のモデルを使用
                model_name = available_models[0]

            print(f"✅ 使用モデル: {model_name}")
            self.current_model = model_name

            return genai.GenerativeModel(model_name)

        except Exception as e:
            print(f"❌ モデル初期化エラー: {e}")
            raise

    async def generate_code(self, task_spec: Dict) -> Dict:
        """
        タスク仕様からコードを生成

        Args:
            task_spec: タスク仕様（title, description, requirements等）

        Returns:
            生成結果（code, quality_score, suggestions等）
        """
        try:
            print(f"🤖 コード生成開始: {task_spec.get('title', 'Unknown')}")

            # Step 1: 関連ナレッジを検索
            related_knowledge = await self._search_knowledge(task_spec)

            # Step 2: プロンプトを構築
            prompt = self._build_prompt(task_spec, related_knowledge)

            # Step 3: Gemini APIでコード生成
            generated_code = await self._call_gemini(prompt)

            # Step 4: 構文チェック
            syntax_valid, syntax_error = self._check_syntax(generated_code)

            # Step 5: 品質評価
            quality_score = await self._evaluate_quality(generated_code, task_spec)

            result = {
                "code": generated_code,
                "syntax_valid": syntax_valid,
                "syntax_error": syntax_error,
                "quality_score": quality_score,
                "related_knowledge": len(related_knowledge),
                "model_used": self.current_model,
                "timestamp": datetime.now().isoformat(),
            }

            # 履歴に記録

            # 標準環境変数ローダー（自動追加）import sysfrom pathlib import Pathsys.path.insert(0, str(Path(__file__).parent.parent))from tools.env_loader import StandardEnvLoaderif not StandardEnvLoader.load_and_verify():    print("環境変数の読み込みに失敗しました")    sys.exit(1)
            self.generation_history.append(result)

            print(f"✅ コード生成完了: 品質スコア {quality_score}/10")
            return result

        except Exception as e:
            print(f"❌ コード生成エラー: {e}")
            return {
                "code": None,
                "error": str(e),
                "syntax_valid": False,
                "timestamp": datetime.now().isoformat(),
            }

    async def refine_code(self, code: str, feedback: Dict) -> Dict:
        """フィードバックに基づいてコードを改善"""
        try:
            print("🔄 コード改善開始")

            prompt = self._build_refinement_prompt(code, feedback)
            refined_code = await self._call_gemini(prompt)
            syntax_valid, syntax_error = self._check_syntax(refined_code)

            result = {
                "refined_code": refined_code,
                "syntax_valid": syntax_valid,
                "syntax_error": syntax_error,
                "improvements": feedback.get("issues", []),
                "timestamp": datetime.now().isoformat(),
            }

            print("✅ コード改善完了")
            return result

        except Exception as e:
            print(f"❌ コード改善エラー: {e}")
            return {"error": str(e)}

    async def _search_knowledge(self, task_spec: Dict) -> List[Dict]:
        """関連ナレッジを検索"""
        if not self.rag_engine:
            return []

        query = f"{task_spec.get('title', '')} {task_spec.get('description', '')}"

        try:
            results = self.rag_engine.search(query, top_k=3)
            return results if results else []
        except Exception as e:
            print(f"⚠️ ナレッジ検索エラー: {e}")
            return []

    def _build_prompt(self, task_spec: Dict, related_knowledge: List[Dict]) -> str:
        """コード生成プロンプトを構築"""
        knowledge_text = ""
        if related_knowledge:
            knowledge_text = "\n【過去の学習内容】\n"
            for i, kb in enumerate(related_knowledge, 1):
                knowledge_text += f"{i}. {kb.get('scenario', '')}\n"
                knowledge_text += f"   解決策: {kb.get('solution', '')}\n"

        prompt = f"""
あなたは優秀なPythonエンジニアです。以下の仕様に基づいて高品質なコードを生成してください。

【タスク仕様】
タイトル: {task_spec.get('title', '')}
説明: {task_spec.get('description', '')}
要件: {task_spec.get('requirements', '')}

{knowledge_text}

【コーディング規約】
1. PEP 8に準拠したコードスタイル
2. 適切なエラーハンドリング（try-except）
3. 型ヒント（Type Hints）の使用
4. docstringによる詳細なドキュメント
5. 1関数は50行以内

【出力形式】
- Pythonコードのみを出力してください
- 説明文やマークダウンは不要です
"""
        return prompt

    def _build_refinement_prompt(self, code: str, feedback: Dict) -> str:
        """コード改善プロンプトを構築"""
        issues_text = "\n".join([f"- {issue}" for issue in feedback.get("issues", [])])

        prompt = f"""
以下のコードを改善してください。

【現在のコード】
```python
{code}
```

【指摘事項】
{issues_text}

【改善要件】
1. 指摘事項をすべて解決してください
2. PEP 8に準拠してください
3. エラーハンドリングを強化してください

【出力形式】
- 改善後のPythonコードのみを出力してください
"""
        return prompt

    async def _call_gemini(self, prompt: str) -> str:
        """Gemini APIを呼び出してコード生成"""
        try:
            response = self.model.generate_content(prompt)

            code = response.text
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0]
            elif "```" in code:
                code = code.split("```")[1].split("```")[0]

            return code.strip()

        except Exception as e:
            print(f"❌ Gemini API呼び出しエラー: {e}")
            raise

    def _check_syntax(self, code: str) -> tuple:
        """構文チェック"""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, str(e)

    async def _evaluate_quality(self, code: str, task_spec: Dict) -> int:
        """コード品質を評価（0-10）"""
        score = 10

        syntax_valid, _ = self._check_syntax(code)
        if not syntax_valid:
            score -= 5

        if '"""' not in code and "'''" not in code:
            score -= 1

        if "->" not in code:
            score -= 1

        if "try:" not in code and "except" not in code:
            score -= 1

        return max(0, min(10, score))

    def get_statistics(self) -> Dict:
        """生成統計を取得"""
        total = len(self.generation_history)
        successful = sum(1 for h in self.generation_history if h.get("syntax_valid"))

        avg_quality = 0
        if total > 0:
            quality_scores = [h.get("quality_score", 0) for h in self.generation_history]
            avg_quality = sum(quality_scores) / len(quality_scores)

        return {
            "total_generations": total,
            "successful_generations": successful,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "average_quality_score": round(avg_quality, 2),
            "current_model": self.current_model,
        }
