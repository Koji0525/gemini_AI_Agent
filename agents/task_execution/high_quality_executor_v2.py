"""
高品質タスク実行エンジン v2.0
既存システム保護型 要件定義書ver4.5 F2実装

目標:
- 300行以上のコード/ドキュメント生成
- 5KB以上のファイルサイズ
- 品質スコア85点以上
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# プロジェクトルート設定
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))


# 環境変数の確実な読み込み
def load_env_with_fallback():
    """環境変数を確実に読み込む（3段階フォールバック）"""
    from dotenv import load_dotenv

    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
        print(f"✅ .env読み込み: {env_path}")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key and env_path.exists():
        # 直接読み込み
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    key = line.strip().split("=", 1)[1].strip('"').strip("'")
                    os.environ["GEMINI_API_KEY"] = key
                    print(f"✅ 手動設定: {len(key)} chars")
                    break


load_env_with_fallback()

from tools.base_data_accessor import BaseDataAccessor


class HighQualityExecutorV2(BaseDataAccessor):
    """高品質タスク実行エンジン v2.0"""

    AVAILABLE_MODELS = [
        "gemini-2.0-flash-exp",
        "gemini-1.5-pro-latest",
        "gemini-1.5-flash-latest",
    ]

    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """初期化"""
        super().__init__()

        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEYが設定されていません\n"
                f".envファイル: {project_root / '.env'}\n"
                "確認: cat .env | grep GEMINI_API_KEY"
            )

        self.model_name = model_name
        self.output_dir = project_root / "agent_outputs" / "high_quality"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.stats = {
            "total_executions": 0,
            "success_count": 0,
            "high_quality_count": 0,
            "avg_size_bytes": 0,
            "avg_quality_score": 0.0,
            "model_used": model_name,
        }

        print(f"✅ HighQualityExecutor v2.0 初期化完了")
        print(f"📁 出力先: {self.output_dir}")
        print(f"🔑 API KEY: 設定済み ({len(self.api_key)} chars)")
        print(f"🤖 モデル: {self.model_name}")

    def execute_task(
        self,
        task_id: str,
        task_description: str,
        required_role: str = "general",
        dependencies: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """タスクを実行（高品質版）"""
        self.stats["total_executions"] += 1
        start_time = datetime.now()

        print(f"\n{'='*60}")
        print(f"🚀 タスク実行: {task_id}")
        print(f"{'='*60}")
        print(f"📝 説明: {task_description[:100]}...")
        print(f"🔄 リトライ: {retry_count}/{max_retries}")

        try:
            # 1. 依存タスクの読み込み
            dep_context = self._load_dependency_outputs(dependencies) if dependencies else {}

            # 2. ナレッジ検索
            knowledge_context = self._search_knowledge(task_description)

            # 3. プロンプト生成
            prompt = self._build_high_quality_prompt(
                task_description=task_description,
                required_role=required_role,
                dep_context=dep_context,
                knowledge_context=knowledge_context,
                additional_context=context,
                retry_count=retry_count,
            )

            # 4. Gemini実行
            result = self._execute_with_gemini(prompt, task_id)

            # 5. 品質評価
            quality = self._evaluate_quality(result)

            # 6. リトライ判定
            if not quality["meets_requirements"] and retry_count < max_retries:
                print(f"\n⚠️ 品質不足 (スコア: {quality['score']}/100)")
                print(f"🔄 リトライ: {retry_count + 1}/{max_retries}")
                time.sleep(2)

                return self.execute_task(
                    task_id=task_id,
                    task_description=task_description,
                    required_role=required_role,
                    dependencies=dependencies,
                    context=context,
                    retry_count=retry_count + 1,
                    max_retries=max_retries,
                )

            # 7. 統計更新
            self._update_stats(quality)

            # 8. 結果返却
            elapsed = (datetime.now() - start_time).total_seconds()
            final_status = "success" if quality["meets_requirements"] else "needs_improvement"

            result_dict = {
                "status": final_status,
                "output_file": str(result["file_path"]),
                "output_summary": result["summary"],
                "quality_score": quality["score"],
                "size_bytes": quality["size_bytes"],
                "line_count": quality["line_count"],
                "elapsed_time": elapsed,
                "retry_count": retry_count,
                "quality_details": quality,
            }

            print(f"\n{'='*60}")
            print(f"📊 実行結果")
            print(f"{'='*60}")
            print(f"✅ ステータス: {final_status}")
            print(f"📊 品質: {quality['score']}/100")
            print(f"📏 行数: {quality['line_count']}")
            print(f"💾 サイズ: {quality['size_bytes']:,}B ({quality['size_bytes']/1024:.1f}KB)")
            print(f"⏱️ 時間: {elapsed:.2f}秒")
            print(f"{'='*60}")

            return result_dict

        except Exception as e:
            print(f"\n❌ エラー: {e}")
            import traceback

            traceback.print_exc()

            elapsed = (datetime.now() - start_time).total_seconds()
            return {
                "status": "failed",
                "error": str(e),
                "elapsed_time": elapsed,
                "retry_count": retry_count,
                "quality_score": 0,
                "size_bytes": 0,
                "line_count": 0,
            }

    def _build_high_quality_prompt(
        self,
        task_description,
        required_role,
        dep_context,
        knowledge_context,
        additional_context,
        retry_count,
    ):
        """高品質プロンプト生成"""
        prompt_parts = [
            "# タスク実行プロンプト（高品質版 v2.0）",
            "",
            "## 🎯 品質要件（必須）",
            "- **最低300行以上**のコード生成",
            "- **最低5KB以上**のファイルサイズ",
            "- **実装可能なコード**（モックNG）",
            "- **Googleドックストリング形式**",
            "",
        ]

        if retry_count == 0:
            prompt_parts.append("## 📝 方針: 詳細型（初回）")
        elif retry_count == 1:
            prompt_parts.append("## 📝 方針: ステップバイステップ型（2回目）")
        else:
            prompt_parts.append("## 📝 方針: 実装重視型（3回目・コード量最優先）")

        prompt_parts.extend(
            [
                "",
                f"## 📋 タスク: {task_description}",
                f"## 👤 ロール: {required_role}",
                "",
                "## 📤 出力形式",
                "```python",
                '"""モジュール説明"""',
                "import ...",
                "class ClassName:",
                "    pass",
                "```",
                "",
                "## ⚠️ 禁止",
                "- 50行以下のコードNG",
                "- TODOコメントNG",
                "- 抽象的な説明のみNG",
            ]
        )

        return "\n".join(prompt_parts)

    def _execute_with_gemini(self, prompt, task_id):
        """Gemini API実行"""
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)

            print(f"🤖 Gemini送信... (モデル: {self.model_name})")

            generation_config = {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 8192,
            }

            response = model.generate_content(prompt, generation_config=generation_config)

            if not response.text:
                raise ValueError("Gemini応答が空")

            output_text = response.text
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"{task_id}_{timestamp}.md"

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(output_text)

            print(f"✅ 保存: {output_file.name}")
            print(f"📏 サイズ: {len(output_text):,}文字")

            summary = output_text[:200] + "..." if len(output_text) > 200 else output_text

            return {"text": output_text, "file_path": output_file, "summary": summary}

        except Exception as e:
            print(f"❌ Gemini実行エラー: {e}")
            if "404" in str(e):
                print(f"\n💡 利用可能モデル:")
                for m in self.AVAILABLE_MODELS:
                    print(f"  - {m}")
            raise

    def _evaluate_quality(self, result):
        """品質評価"""
        output_text = result["text"]
        line_count = len(output_text.split("\n"))
        size_bytes = len(output_text.encode("utf-8"))

        score = 0

        # 行数スコア（最大40点）
        if line_count >= 500:
            score += 40
        elif line_count >= 300:
            score += 30
        elif line_count >= 100:
            score += 15

        # サイズスコア（最大30点）
        if size_bytes >= 10000:
            score += 30
        elif size_bytes >= 5000:
            score += 20
        elif size_bytes >= 1000:
            score += 10

        # 実装スコア（最大30点）
        code_blocks = output_text.count("```")
        has_implementation = code_blocks >= 2

        if has_implementation:
            score += 15
        if "def " in output_text or "class " in output_text:
            score += 10
        if "Args:" in output_text and "Returns:" in output_text:
            score += 5

        meets_requirements = (line_count >= 300) and (size_bytes >= 5000) and has_implementation
        quality_level = "high" if score >= 85 else "medium" if score >= 60 else "low"

        return {
            "score": score,
            "line_count": line_count,
            "size_bytes": size_bytes,
            "code_blocks": code_blocks // 2,
            "has_implementation": has_implementation,
            "meets_requirements": meets_requirements,
            "quality_level": quality_level,
        }

    def _load_dependency_outputs(self, dependencies):
        """依存タスク読み込み"""
        dep_context = {}
        for dep_id in dependencies:
            output_dir = project_root / "agent_outputs"
            matching_files = list(output_dir.rglob(f"*{dep_id}*"))
            if matching_files:
                latest_file = max(matching_files, key=lambda p: p.stat().st_mtime)
                try:
                    with open(latest_file, "r", encoding="utf-8") as f:
                        dep_context[dep_id] = f.read()
                    print(f"📖 依存タスク: {dep_id}")
                except Exception:
                    print(f"⚠️ 読み込みエラー: {dep_id}")
        return dep_context

    def _search_knowledge(self, query):
        """ナレッジ検索"""
        try:
            from knowledge_system.core_agents.knowledge_manager import \
                KnowledgeManager

            km = KnowledgeManager()
            results = km.search_knowledge(query=query, limit=3)
            if results:
                context_parts = []
                for i, result in enumerate(results, 1):
                    context_parts.append(f"### 参考{i}")
                    context_parts.append(f"**{result.get('title', 'N/A')}**")
                    context_parts.append(f"{result.get('content', 'N/A')[:200]}...")
                return "\n".join(context_parts)
        except Exception as e:
            print(f"⚠️ ナレッジ検索エラー: {e}")
        return ""

    def _update_stats(self, quality):
        """統計更新"""
        if quality["meets_requirements"]:
            self.stats["high_quality_count"] += 1
        if quality["score"] >= 60:
            self.stats["success_count"] += 1

        n = self.stats["total_executions"]
        self.stats["avg_size_bytes"] = (
            self.stats["avg_size_bytes"] * (n - 1) + quality["size_bytes"]
        ) / n
        self.stats["avg_quality_score"] = (
            self.stats["avg_quality_score"] * (n - 1) + quality["score"]
        ) / n

    def get_statistics(self):
        """統計取得"""
        return {
            **self.stats,
            "high_quality_rate": (
                self.stats["high_quality_count"] / self.stats["total_executions"] * 100
                if self.stats["total_executions"] > 0
                else 0
            ),
            "success_rate": (
                self.stats["success_count"] / self.stats["total_executions"] * 100
                if self.stats["total_executions"] > 0
                else 0
            ),
        }


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 HighQualityExecutor v2.0 テスト")
    print("=" * 60)

    try:
        executor = HighQualityExecutorV2(model_name="gemini-2.0-flash-exp")

        test_task = {
            "task_id": "test_ml_pipeline",
            "task_description": "機械学習パイプラインクラスを実装。データ前処理、特徴量エンジニアリング、モデル訓練・評価、ハイパーパラメータ最適化、結果可視化、エラーハンドリング完備。最低300行以上。",
            "required_role": "ml_engineer",
        }

        result = executor.execute_task(**test_task)

        stats = executor.get_statistics()
        print(f"\n📈 統計:")
        print(f"  高品質達成率: {stats['high_quality_rate']:.1f}%")
        print(f"  平均スコア: {stats['avg_quality_score']:.1f}/100")

        if result["status"] == "success":
            print(f"\n✅ テスト成功")

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()
