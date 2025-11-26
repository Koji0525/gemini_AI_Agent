"""
Few-shot成功例ライブラリ

過去の成功例を検索し、プロンプトに含める。
これにより、LLMに具体例を示すことで品質向上。

Version: 1.0
Created: 2024-11-26
"""

from pathlib import Path
from typing import Any, Dict, List, Optional


class FewShotLibrary:
    """
        Few-shot成功例ライブラリ

        機能:
        - ファイルベースの成功例読み込み
        - 類似タスクの検索（今後ナレッジDB連携）
        - Few-shot形式へのフォーマット

        使用例:
    ```python
        library = FewShotLibrary()
        examples = library.search_similar('データベース接続')
        formatted = library.format_examples(examples)
    ```
    """

    def __init__(self, examples_dir: str = "prompts/examples"):
        """
        初期化

        Args:
            examples_dir: 成功例ディレクトリパス
        """
        self.examples_dir = Path(examples_dir)
        self.examples_cache = []

        # ディレクトリ存在確認
        if not self.examples_dir.exists():
            print(f"⚠️  成功例ディレクトリが存在しません: {self.examples_dir}")
            print(f"   作成します...")
            self.examples_dir.mkdir(parents=True, exist_ok=True)

        # 成功例を事前読み込み
        self._load_all_examples()

    def _load_all_examples(self):
        """全ての成功例をメモリに読み込み"""
        if not self.examples_dir.exists():
            return

        for example_file in self.examples_dir.glob("success_example_*.txt"):
            try:
                with open(example_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # メタデータ抽出（簡易版）
                example = {
                    "file_name": example_file.name,
                    "content": content,
                    "task_description": self._extract_task_description(content),
                    "output_summary": self._extract_output_summary(content),
                    "quality_score": self._extract_quality_score(content),
                }

                self.examples_cache.append(example)

            except Exception as e:
                print(f"⚠️  成功例読み込みエラー: {example_file}\n{e}")

        print(f"✅ {len(self.examples_cache)}個の成功例を読み込みました")

    def _extract_task_description(self, content: str) -> str:
        """タスク説明を抽出（簡易版）"""
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "タスク" in line or "Task:" in line:
                return lines[i + 1].strip() if i + 1 < len(lines) else ""
        return "タスク説明なし"

    def _extract_output_summary(self, content: str) -> str:
        """出力サマリーを抽出（簡易版）"""
        lines = content.split("\n")
        summary_lines = []
        in_output = False

        for line in lines:
            if "出力" in line or "Output:" in line:
                in_output = True
                continue

            if in_output:
                if line.strip().startswith("-") or line.strip().startswith("*"):
                    summary_lines.append(line.strip())
                elif line.strip() == "":
                    break

        return "\n".join(summary_lines) if summary_lines else "出力情報なし"

    def _extract_quality_score(self, content: str) -> int:
        """品質スコアを抽出（簡易版）"""
        # 今後実装: 実際のスコアを抽出
        return 95  # デフォルト

    def search_similar(self, task_description: str, top_k: int = 2) -> List[Dict]:
        """
        類似タスクの成功例を検索

        現在は簡易版（全件返す）
        今後: ベクトル検索やキーワードマッチング実装

        Args:
            task_description: タスク説明
            top_k: 取得件数

        Returns:
            成功例リスト
        """
        # 簡易版: キャッシュから上位k件を返す
        return self.examples_cache[:top_k]

    def format_examples(self, examples: List[Dict]) -> str:
        """
        Few-shot形式にフォーマット

        Args:
            examples: 成功例リスト

        Returns:
            フォーマット済み文字列
        """
        if not examples:
            return "【No Previous Success Examples Available】\n"

        formatted = "【MANDATORY REFERENCE: Previous Success Examples】\n\n"
        formatted += "These are PROVEN successful implementations. "
        formatted += "Your output MUST match or exceed this quality level.\n\n"

        for i, ex in enumerate(examples, 1):
            formatted += f"Example {i}:\n"
            formatted += f"Task: {ex['task_description']}\n"
            formatted += f"Output:\n{ex['output_summary']}\n"
            formatted += f"Quality Score: {ex['quality_score']}/100\n"
            formatted += "-" * 60 + "\n\n"

        return formatted

    def add_example(
        self,
        task_description: str,
        output_summary: str,
        quality_score: int,
        full_output: Optional[str] = None,
    ):
        """
        新しい成功例を追加

        Args:
            task_description: タスク説明
            output_summary: 出力サマリー
            quality_score: 品質スコア（0-100）
            full_output: 完全な出力（オプション）
        """
        # ファイル名生成
        example_count = len(self.examples_cache) + 1
        file_name = f"success_example_{example_count:03d}.txt"
        file_path = self.examples_dir / file_name

        # コンテンツ生成
        content = f"""# 成功例 {example_count}

【タスク】
{task_description}

【出力】
{output_summary}

【品質スコア】
{quality_score}/100

"""

        if full_output:
            content += f"""【完全な出力】
{full_output}
"""

        # ファイル書き込み
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ 成功例追加: {file_name}")

        # キャッシュ更新
        self._load_all_examples()

    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        return {
            "total_examples": len(self.examples_cache),
            "avg_quality_score": (
                sum(ex["quality_score"] for ex in self.examples_cache) / len(self.examples_cache)
                if self.examples_cache
                else 0
            ),
            "example_files": [ex["file_name"] for ex in self.examples_cache],
        }


# テスト用コード
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("FewShotLibrary テスト")
    print("=" * 60 + "\n")

    # 初期化
    library = FewShotLibrary()

    # テスト用の成功例追加
    library.add_example(
        task_description="データベース接続モジュールの実装",
        output_summary="""- main.py: 580行（接続プール、トランザクション制御）
- test_main.py: 365行（ユニット・統合テスト）
- README.md: 300行（概要、API仕様、使用例）""",
        quality_score=95,
    )

    library.add_example(
        task_description="RESTful APIサーバーの実装",
        output_summary="""- api_server.py: 720行（エンドポイント実装）
- test_api.py: 420行（APIテスト）
- README.md: 380行（APIドキュメント）""",
        quality_score=92,
    )

    print()

    # 統計情報
    stats = library.get_stats()
    print(f"統計情報: {stats}")
    print()

    # 類似検索テスト
    examples = library.search_similar("データベース", top_k=2)
    print(f"検索結果: {len(examples)}件\n")

    # フォーマットテスト
    formatted = library.format_examples(examples)
    print("Few-shotフォーマット結果:")
    print("-" * 60)
    print(formatted)
    print("-" * 60)
