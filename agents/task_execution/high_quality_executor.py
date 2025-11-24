"""
高品質タスク実行エンジン v1.1
既存システム保護型 要件定義書ver4.5 F2実装

改善内容:
- 環境変数の自動ロード処理追加
- エラーハンドリング強化
- 既存システムとの統合性確保

目標:
- 300行以上のコード/ドキュメント生成
- 5KB以上のファイルサイズ
- 品質スコア85点以上
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# プロジェクトルートを追加
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

# 環境変数の自動ロード（既存システムと同じ方式）
from dotenv import load_dotenv

env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# 既存システムのモジュールをインポート
from tools.base_data_accessor import BaseDataAccessor


class HighQualityExecutor(BaseDataAccessor):
    """
    高品質タスク実行エンジン

    既存のCompleteEngineUltimateと連携し、
    300行以上・5KB以上の高品質な成果物を生成する。

    設計原則:
    - 既存システムを破壊しない（追加のみ）
    - BaseDataAccessorを継承（既存のデータアクセス方式を踏襲）
    - 段階的な品質向上（3段階のプロンプト戦略）
    """

    def __init__(self):
        """
        初期化処理

        Raises:
            ValueError: GEMINI_API_KEYが設定されていない場合
        """
        super().__init__()

        # API KEY の取得と検証
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            # 既存システムのエラーメッセージ形式に合わせる
            error_msg = (
                "GEMINI_API_KEY が設定されていません。\n"
                "以下を確認してください:\n"
                "1. .envファイルが存在するか\n"
                "2. GEMINI_API_KEY=... の行があるか\n"
                f"3. .envファイルパス: {env_path}"
            )
            raise ValueError(error_msg)

        # 出力ディレクトリの設定
        self.output_dir = project_root / "agent_outputs" / "high_quality"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 実行統計
        self.stats = {
            "total_executions": 0,
            "success_count": 0,
            "high_quality_count": 0,  # 300行以上
            "avg_size_bytes": 0,
            "avg_quality_score": 0.0,
        }

        print(f"✅ HighQualityExecutor 初期化完了")
        print(f"📁 出力先: {self.output_dir}")
        print(f"🔑 API KEY: {'設定済み' if self.api_key else '未設定'} ({len(self.api_key)} chars)")

    def execute_task(
        self,
        task_id: str,
        task_description: str,
        required_role: str = "general",
        dependencies: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        タスクを実行（高品質版）

        Args:
            task_id: タスクID（例: "task_512"）
            task_description: タスクの説明文
            required_role: 必要なロール（例: "engineer", "researcher"）
            dependencies: 依存タスクIDのリスト
            context: 追加のコンテキスト情報

        Returns:
            実行結果の辞書
            {
                "status": "success" | "failed",
                "output_file": str,  # 生成ファイルパス
                "output_summary": str,
                "quality_score": float,
                "size_bytes": int,
                "line_count": int,
                "elapsed_time": float
            }
        """
        self.stats["total_executions"] += 1
        start_time = datetime.now()

        print(f"\n🚀 高品質タスク実行開始: {task_id}")
        print(f"📝 説明: {task_description[:100]}...")

        try:
            # 1. 依存タスクの成果物を取得（コンテキスト強化）
            dep_context = self._load_dependency_outputs(dependencies) if dependencies else {}

            # 2. ナレッジベースから類似情報を取得（既存システム連携）
            knowledge_context = self._search_knowledge(task_description)

            # 3. 統合プロンプトの生成（300行以上を強制）
            prompt = self._build_high_quality_prompt(
                task_description=task_description,
                required_role=required_role,
                dep_context=dep_context,
                knowledge_context=knowledge_context,
                additional_context=context,
            )

            # 4. Gemini APIで実行（既存システムのGemini連携を踏襲）
            result = self._execute_with_gemini(prompt, task_id)

            # 5. 品質評価（300行以上・5KB以上の確認）
            quality = self._evaluate_quality(result)

            # 6. 統計更新
            self._update_stats(quality)

            # 7. 結果の返却
            elapsed = (datetime.now() - start_time).total_seconds()

            return {
                "status": "success" if quality["meets_requirements"] else "needs_improvement",
                "output_file": str(result["file_path"]),
                "output_summary": result["summary"],
                "quality_score": quality["score"],
                "size_bytes": quality["size_bytes"],
                "line_count": quality["line_count"],
                "elapsed_time": elapsed,
                "quality_details": quality,
            }

        except Exception as e:
            print(f"❌ エラー発生: {e}")
            elapsed = (datetime.now() - start_time).total_seconds()
            return {"status": "failed", "error": str(e), "elapsed_time": elapsed}

    def _build_high_quality_prompt(
        self,
        task_description: str,
        required_role: str,
        dep_context: Dict[str, Any],
        knowledge_context: str,
        additional_context: Optional[Dict[str, Any]],
    ) -> str:
        """
        高品質成果物を生成するプロンプトを構築

        重要: 300行以上・5KB以上を必須要件として明記
        """
        prompt_parts = [
            "# タスク実行プロンプト（高品質版）",
            "",
            "## 🎯 品質要件（必須）",
            "- **最低300行以上**のコード/ドキュメントを生成すること",
            "- **最低5000バイト（5KB）以上**のファイルサイズであること",
            "- **実際に動作する**実装であること（モックではなく本物）",
            "- **詳細なコメント**と**使用例**を含めること",
            "",
            f"## 📋 タスク内容",
            f"{task_description}",
            "",
            f"## 👤 必要なロール: {required_role}",
            "",
        ]

        # 依存タスクの成果物を前提情報として追加
        if dep_context:
            prompt_parts.extend(
                [
                    "## 📚 依存タスクの成果物（前提情報）",
                    "以下のタスクの成果物を参考にしてください:",
                    "",
                ]
            )
            for dep_id, dep_output in dep_context.items():
                prompt_parts.append(f"### {dep_id}")
                prompt_parts.append(f"```\n{dep_output[:500]}...\n```")
                prompt_parts.append("")

        # ナレッジベースからの類似情報
        if knowledge_context:
            prompt_parts.extend(["## 🧠 ナレッジベースからの参考情報", knowledge_context, ""])

        # 追加コンテキスト
        if additional_context:
            prompt_parts.extend(
                [
                    "## 🔍 追加コンテキスト",
                    json.dumps(additional_context, indent=2, ensure_ascii=False),
                    "",
                ]
            )

        # 出力形式の指定（重要）
        prompt_parts.extend(
            [
                "## 📤 出力形式",
                "以下の形式で出力してください:",
                "",
                "### 1. 実装コード（Pythonファイル）",
                "- 最低300行以上",
                "- 詳細なドックストリング",
                "- 型ヒント必須",
                "- エラーハンドリング完備",
                "",
                "### 2. README.md",
                "- 使用方法",
                "- 実行例",
                "- 依存関係",
                "",
                "### 3. テストコード（pytest）",
                "- 主要機能のテスト",
                "- カバレッジ80%以上",
                "",
                "## ⚠️ 禁止事項",
                "- 抽象的な説明のみは**NG**",
                "- 「TODO」「実装予定」のような未実装コードは**NG**",
                "- 50行以下のコードは**NG**（自動で不合格）",
                "",
                "## 🚀 開始",
                "上記の要件を満たす高品質な成果物を生成してください。",
            ]
        )

        return "\n".join(prompt_parts)

    def _execute_with_gemini(self, prompt: str, task_id: str) -> Dict[str, Any]:
        """
        Gemini APIでプロンプトを実行

        既存システムのGemini連携方式を踏襲し、
        google.generativeai を使用する。
        """
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")

            print(f"🤖 Gemini APIに送信中...")
            response = model.generate_content(prompt)

            if not response.text:
                raise ValueError("Geminiからの応答が空です")

            # 生成されたテキストをファイルに保存
            output_text = response.text
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"{task_id}_{timestamp}.md"

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(output_text)

            print(f"✅ 成果物保存: {output_file}")

            # サマリー生成（最初の200文字）
            summary = output_text[:200] + "..." if len(output_text) > 200 else output_text

            return {"text": output_text, "file_path": output_file, "summary": summary}

        except Exception as e:
            print(f"❌ Gemini API実行エラー: {e}")
            raise

    def _evaluate_quality(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        成果物の品質を評価

        評価基準（既存システム保護型 要件定義書ver4.5準拠）:
        - 行数: 300行以上で85点、500行以上で100点
        - サイズ: 5KB以上で85点、10KB以上で100点
        - 実用性: コードブロックの有無、説明の詳細さ
        """
        output_text = result["text"]
        result["file_path"]

        # 行数カウント
        line_count = len(output_text.split("\n"))

        # ファイルサイズ
        size_bytes = len(output_text.encode("utf-8"))

        # 基本スコア計算
        score = 0

        # 行数スコア（最大40点）
        if line_count >= 500:
            score += 40
        elif line_count >= 300:
            score += 30
        elif line_count >= 100:
            score += 15
        else:
            score += max(0, line_count // 10)

        # サイズスコア（最大30点）
        if size_bytes >= 10000:  # 10KB以上
            score += 30
        elif size_bytes >= 5000:  # 5KB以上
            score += 20
        elif size_bytes >= 1000:  # 1KB以上
            score += 10

        # 実用性スコア（最大30点）
        code_blocks = output_text.count("```")
        has_implementation = code_blocks >= 2  # 少なくとも1つのコードブロック

        if has_implementation:
            score += 20

        if "def " in output_text or "class " in output_text:
            score += 10  # Pythonコードが含まれている

        # 要件達成判定
        meets_requirements = (line_count >= 300) and (size_bytes >= 5000) and has_implementation

        quality_level = "high" if score >= 85 else "medium" if score >= 60 else "low"

        return {
            "score": score,
            "line_count": line_count,
            "size_bytes": size_bytes,
            "code_blocks": code_blocks // 2,  # 開始と終了で2つ
            "has_implementation": has_implementation,
            "meets_requirements": meets_requirements,
            "quality_level": quality_level,
        }

    def _load_dependency_outputs(self, dependencies: List[str]) -> Dict[str, str]:
        """
        依存タスクの成果物を読み込む

        既存システムのagent_outputs/からファイルを検索
        """
        dep_context = {}

        for dep_id in dependencies:
            # 依存タスクの出力ファイルを検索
            output_dir = project_root / "agent_outputs"
            matching_files = list(output_dir.rglob(f"*{dep_id}*"))

            if matching_files:
                latest_file = max(matching_files, key=lambda p: p.stat().st_mtime)
                try:
                    with open(latest_file, "r", encoding="utf-8") as f:
                        dep_context[dep_id] = f.read()
                    print(f"📖 依存タスク読み込み: {dep_id} ({latest_file.name})")
                except Exception as e:
                    print(f"⚠️  依存タスク読み込みエラー: {dep_id} - {e}")

        return dep_context

    def _search_knowledge(self, query: str) -> str:
        """
        ナレッジベースから類似情報を検索

        既存システムのKnowledgeManagerを活用
        """
        try:
            from knowledge_system.core_agents.knowledge_manager import \
                KnowledgeManager

            km = KnowledgeManager()
            results = km.search_knowledge(query=query, limit=3)

            if results:
                context_parts = []
                for i, result in enumerate(results, 1):
                    context_parts.append(f"### 参考情報 {i}")
                    context_parts.append(f"**タイトル**: {result.get('title', 'N/A')}")
                    context_parts.append(f"**内容**: {result.get('content', 'N/A')[:200]}...")
                    context_parts.append("")

                return "\n".join(context_parts)

        except Exception as e:
            print(f"⚠️  ナレッジ検索エラー: {e}")

        return ""

    def _update_stats(self, quality: Dict[str, Any]):
        """統計情報の更新"""
        if quality["meets_requirements"]:
            self.stats["high_quality_count"] += 1

        if quality["score"] >= 60:
            self.stats["success_count"] += 1

        # 移動平均の更新
        n = self.stats["total_executions"]
        self.stats["avg_size_bytes"] = (
            self.stats["avg_size_bytes"] * (n - 1) + quality["size_bytes"]
        ) / n
        self.stats["avg_quality_score"] = (
            self.stats["avg_quality_score"] * (n - 1) + quality["score"]
        ) / n

    def get_statistics(self) -> Dict[str, Any]:
        """
        実行統計の取得

        Returns:
            統計情報の辞書
        """
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


# ==
# テスト実行
# ==
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 HighQualityExecutor v1.1 テスト実行")
    print("=" * 60)

    try:
        # 初期化テスト
        executor = HighQualityExecutor()

        # サンプルタスクの実行
        test_task = {
            "task_id": "test_512",
            "task_description": (
                "agents/observer_enhanced/static_analyzer.py を詳細に分析し、"
                "新規モジュール追加による影響範囲を特定する。"
                "具体的には、import文、依存関係、呼び出し元を完全にリストアップし、"
                "変更時のリスク評価と推奨テストケースを提示すること。"
            ),
            "required_role": "engineer",
            "dependencies": None,
        }

        print(f"\n📝 テストタスク: {test_task['task_id']}")
        print(f"説明: {test_task['task_description'][:80]}...")

        result = executor.execute_task(**test_task)

        print(f"\n" + "=" * 60)
        print("📊 実行結果")
        print("=" * 60)
        print(f"ステータス: {result['status']}")
        print(f"品質スコア: {result['quality_score']}/100")
        print(f"行数: {result['line_count']}行")
        print(f"サイズ: {result['size_bytes']:,}バイト ({result['size_bytes']/1024:.1f}KB)")
        print(f"実行時間: {result['elapsed_time']:.2f}秒")
        print(f"出力ファイル: {result['output_file']}")

        # 統計表示
        stats = executor.get_statistics()
        print(f"\n📈 統計情報")
        print(f"総実行回数: {stats['total_executions']}")
        print(f"高品質達成率: {stats['high_quality_rate']:.1f}%")
        print(f"平均スコア: {stats['avg_quality_score']:.1f}/100")

        print(f"\n✅ テスト完了")

    except Exception as e:
        print(f"\n❌ テスト失敗: {e}")
        import traceback

        traceback.print_exc()
