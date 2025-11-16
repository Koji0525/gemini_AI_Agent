#!/usr/bin/env python3
"""
AI駆動コード生成システム - コアコンポーネント
ナレッジベース統合、品質評価、フォールバック機構を備えた次世代生成器
"""
import os
import re
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class KnowledgeBaseIntegrator:
    """ナレッジベース統合クラス"""

    def __init__(self, knowledge_db_path=None):
        self.knowledge_db_path = knowledge_db_path
        self.patterns = self._load_common_patterns()

    def _load_common_patterns(self) -> Dict:
        """共通パターンの読み込み"""
        return {
            "api_patterns": [
                r"API.*(作成|実装|開発)",
                r"REST.*エンドポイント",
                r"エンドポイント.*追加",
                r"(GET|POST|PUT|DELETE).*実装",
            ],
            "data_patterns": [
                r"データ.*(処理|分析|変換)",
                r"CSV.*(読み込み|書き込み)",
                r"パンダス.*使用",
                r"データベース.*接続",
            ],
            "web_patterns": [
                r"Web.*(アプリ|サイト)",
                r"フロントエンド",
                r"HTML.*生成",
                r"Flask|Django",
            ],
            "ml_patterns": [r"機械学習", r"AI.*モデル", r"深層学習", r"分類|回帰|クラスタリング"],
        }

    def search_knowledge(self, query: str, category: str = None) -> List[Dict]:
        """ナレッジベースから関連情報を検索"""
        try:
            # ナレッジベースの検索（簡易実装）
            knowledge_file = Path(
                "/workspaces/gemini_AI_Agent/knowledge_system/database/knowledge.db"
            )
            if knowledge_file.exists():
                # 実際の実装ではSQLiteクエリを実行
                logger.info(f"🔍 ナレッジ検索: {query}")
                return self._mock_knowledge_search(query, category)
            else:
                logger.warning("ナレッジベースが未構築のため、デフォルトパターンを使用")
                return self._get_fallback_knowledge(query, category)

        except Exception as e:
            logger.error(f"ナレッジ検索エラー: {e}")
            return self._get_fallback_knowledge(query, category)

    def _mock_knowledge_search(self, query: str, category: str) -> List[Dict]:
        """モックナレッジ検索（実際の実装ではDB検索）"""
        # 開発中のモック実装
        mock_knowledge = [
            {
                "title": "FastAPIベストプラクティス",
                "content": "FastAPIではPydanticモデルを使用して...",
                "category": "api",
                "tags": "FastAPI,Python,ベストプラクティス",
                "score": 0.85,
            },
            {
                "title": "データ分析パイプライン",
                "content": "pandasを使用したデータ前処理の標準パターン...",
                "category": "data",
                "tags": "pandas,データ分析,前処理",
                "score": 0.78,
            },
        ]

        # クエリとカテゴリに基づいてフィルタリング
        results = []
        for item in mock_knowledge:
            if category and item["category"] != category:
                continue
            if query.lower() in item["title"].lower() or query.lower() in item["content"].lower():
                results.append(item)

        return results[:3]  # 上位3件を返す

    def _get_fallback_knowledge(self, query: str, category: str) -> List[Dict]:
        """フォールバックナレッジ"""
        return [
            {
                "title": "一般的な開発パターン",
                "content": "標準的な実装パターンを適用してください",
                "category": "general",
                "tags": "標準,パターン",
                "score": 0.5,
            }
        ]


class AICodeGenerator:
    """AI駆動コード生成器"""

    def __init__(self):
        self.knowledge_integrator = KnowledgeBaseIntegrator()
        self.template_dir = Path("/workspaces/gemini_AI_Agent/agents/templates")
        self.generation_history = []

    def generate_code(self, description: str, context: Dict = None) -> Dict:
        """
        説明文からコードを生成

        Args:
            description: コード生成の説明
            context: 追加のコンテキスト情報

        Returns:
            生成結果の辞書
        """
        logger.info(f"🚀 コード生成開始: {description}")

        # ステップ1: コードタイプを検出
        code_type = self._detect_code_type(description)
        logger.info(f"📊 検出タイプ: {code_type}")

        # ステップ2: ナレッジベースから関連情報を取得
        knowledge = self.knowledge_integrator.search_knowledge(description, code_type)

        # ステップ3: コード生成（ナレッジを活用）
        generated_code = self._generate_with_knowledge(description, code_type, knowledge, context)

        # ステップ4: 品質評価
        quality_score = self._evaluate_code_quality(generated_code, description)

        # ステップ5: 履歴に保存
        self._save_to_history(description, generated_code, quality_score, code_type)

        return {
            "code": generated_code,
            "type": code_type,
            "quality_score": quality_score,
            "knowledge_used": [k["title"] for k in knowledge],
            "file_path": self._save_generated_code(generated_code, description, code_type),
        }

    def _detect_code_type(self, description: str) -> str:
        """説明文からコードタイプを検出"""
        type_scores = {}

        patterns = self.knowledge_integrator.patterns
        for code_type, type_patterns in patterns.items():
            score = 0
            for pattern in type_patterns:
                if re.search(pattern, description, re.IGNORECASE):
                    score += 1
            type_scores[code_type] = score

        # 最高スコアのタイプを返す
        best_type = max(type_scores, key=type_scores.get)
        return best_type if type_scores[best_type] > 0 else "general"

    def _generate_with_knowledge(
        self, description: str, code_type: str, knowledge: List[Dict], context: Dict
    ) -> str:
        """ナレッジを活用したコード生成"""

        # ナレッジからベストプラクティスを抽出
        best_practices = []
        for item in knowledge:
            if item["score"] > 0.7:  # 高スコアのナレッジのみ使用
                best_practices.append(item["content"])

        # コード生成のテンプレート選択
        template_content = self._get_template_content(code_type)

        # ナレッジを統合したコード生成
        code = self._integrate_knowledge_into_code(
            description, code_type, template_content, best_practices, context
        )

        return code

    def _get_template_content(self, code_type: str) -> str:
        """テンプレート内容の取得（フォールバック用）"""
        template_files = {
            "api": "api/fastapi_rest.py",
            "data": "data/pandas_pipeline.py",
            "web": "web/flask_app.py",
            "ml": "ml/scikit_learn.py",
            "cli": "cli_detailed.py",
        }

        template_path = self.template_dir / template_files.get(code_type, "cli_detailed.py")
        if template_path.exists():
            with open(template_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return self._get_basic_template()

    def _get_basic_template(self) -> str:
        """基本テンプレート"""
        return '''#!/usr/bin/env python3
"""
生成コード: {description}
"""

def main():
    """メイン関数"""
    print("✅ 生成コード実行")
    # 実装が必要なロジック

if __name__ == "__main__":
    main()
'''

    def _integrate_knowledge_into_code(
        self,
        description: str,
        code_type: str,
        template: str,
        best_practices: List[str],
        context: Dict,
    ) -> str:
        """ナレッジをコードに統合"""

        # テンプレートの基本構造を使用
        code = template.replace("{description}", description)

        # ベストプラクティスをコメントとして追加
        if best_practices:
            practices_text = "\n".join([f"# 💡 {practice}" for practice in best_practices[:2]])
            code = code.replace('"""', f'"""\n{practices_text}\n', 1)

        # コンテキストに基づいたカスタマイズ
        if context and "requirements" in context:
            req_text = "\n".join([f"# 📋 要件: {req}" for req in context["requirements"][:3]])
            code = code.replace('"""', f'"""\n{req_text}\n', 1)

        return code

    def _evaluate_code_quality(self, code: str, description: str) -> float:
        """コード品質の評価"""
        score = 0.7  # 基本スコア

        # シンプルな評価基準
        checks = [
            (len(code) > 100, 0.1),  # 最低限の長さ
            ("def " in code, 0.1),  # 関数定義がある
            ("import " in code, 0.1),  # import文がある
            ("main()" in code, 0.05),  # main関数がある
            ("class " in code, 0.05),  # クラス定義がある
        ]

        for condition, points in checks:
            if condition:
                score += points

        return min(score, 1.0)  # 最大1.0

    def _save_to_history(self, description: str, code: str, quality_score: float, code_type: str):
        """生成履歴を保存"""
        self.generation_history.append(
            {
                "description": description,
                "code_type": code_type,
                "quality_score": quality_score,
                "timestamp": self._get_timestamp(),
            }
        )

        # 履歴が一定数を超えたら古いものを削除
        if len(self.generation_history) > 100:
            self.generation_history = self.generation_history[-50:]

    def _save_generated_code(self, code: str, description: str, code_type: str) -> Path:
        """生成コードをファイルに保存"""
        output_dir = Path("/workspaces/gemini_AI_Agent/agent_outputs/ai_driven")
        output_dir.mkdir(parents=True, exist_ok=True)

        # ファイル名を生成
        safe_description = re.sub(r"[^\w\s-]", "", description)[:30]
        timestamp = self._get_timestamp()
        filename = f"ai_generated_{code_type}_{safe_description}_{timestamp}.py"
        file_path = output_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        logger.info(f"💾 生成コード保存: {file_path}")
        return file_path

    def _get_timestamp(self) -> str:
        """タイムスタンプ生成"""
        from datetime import datetime

        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def get_generation_stats(self) -> Dict:
        """生成統計を取得"""
        if not self.generation_history:
            return {}

        total_generations = len(self.generation_history)
        avg_quality = (
            sum(item["quality_score"] for item in self.generation_history) / total_generations
        )

        type_counts = {}
        for item in self.generation_history:
            type_counts[item["code_type"]] = type_counts.get(item["code_type"], 0) + 1

        return {
            "total_generations": total_generations,
            "average_quality": avg_quality,
            "type_distribution": type_counts,
        }


class TemplateLearner:
    """テンプレート学習器 - パターン自動抽出とテンプレート自動生成"""

    def __init__(self, ai_generator: AICodeGenerator):
        self.ai_generator = ai_generator
        self.learned_patterns = {}

    def analyze_generation_patterns(self):
        """生成パターンを分析"""
        stats = self.ai_generator.get_generation_stats()

        if not stats:
            logger.info("📊 分析対象の生成データがありません")
            return

        logger.info("🔍 生成パターンを分析中...")

        # タイプ別の成功パターンを分析
        for code_type, count in stats["type_distribution"].items():
            if count >= 3:  # 十分なデータがあるタイプ
                self._learn_type_patterns(code_type)

    def _learn_type_patterns(self, code_type: str):
        """特定タイプのパターンを学習"""
        # 実際の実装では生成履歴からパターンを抽出
        logger.info(f"🧠 {code_type} タイプのパターンを学習中")

        # モック学習ロジック
        learned_pattern = {
            "common_imports": self._extract_common_imports(code_type),
            "structure_pattern": self._extract_structure_pattern(code_type),
            "best_practices": self._extract_best_practices(code_type),
        }

        self.learned_patterns[code_type] = learned_pattern
        logger.info(f"✅ {code_type} パターン学習完了")

    def _extract_common_imports(self, code_type: str) -> List[str]:
        """共通importを抽出"""
        type_imports = {
            "api": ["from fastapi import FastAPI", "from pydantic import BaseModel"],
            "data": ["import pandas as pd", "import numpy as np"],
            "web": ["from flask import Flask", "from flask import render_template"],
            "ml": ["from sklearn.ensemble import RandomForestClassifier", "import pandas as pd"],
        }
        return type_imports.get(code_type, ["import os", "import sys"])

    def _extract_structure_pattern(self, code_type: str) -> str:
        """構造パターンを抽出"""
        structures = {
            "api": "FastAPI app → Pydantic models → API routes",
            "data": "Data loading → Preprocessing → Analysis → Output",
            "web": "Flask app → Routes → Templates → Static files",
            "ml": "Data loading → Preprocessing → Model training → Evaluation",
        }
        return structures.get(code_type, "Basic Python script structure")

    def _extract_best_practices(self, code_type: str) -> List[str]:
        """ベストプラクティスを抽出"""
        practices = {
            "api": ["Use Pydantic for data validation", "Implement error handling"],
            "data": ["Handle missing values appropriately", "Use vectorized operations"],
            "web": ["Use templates for HTML", "Implement CSRF protection"],
            "ml": ["Split data into train/test sets", "Use cross-validation"],
        }
        return practices.get(code_type, ["Write docstrings", "Handle exceptions"])

    def generate_new_template(self, code_type: str) -> str:
        """新しいテンプレートを生成"""
        if code_type not in self.learned_patterns:
            self._learn_type_patterns(code_type)

        patterns = self.learned_patterns[code_type]

        # 学習したパターンからテンプレートを生成
        template = self._build_template_from_patterns(code_type, patterns)

        # 新しいテンプレートを保存
        self._save_new_template(code_type, template)

        return template

    def _build_template_from_patterns(self, code_type: str, patterns: Dict) -> str:
        """パターンからテンプレートを構築"""
        imports = "\n".join(patterns["common_imports"])

        template = f'''#!/usr/bin/env python3
"""
自動生成テンプレート - {code_type}
学習されたパターンに基づく
"""

{imports}

# �� 構造パターン: {patterns['structure_pattern']}

class {code_type.title()}Generator:
    """{code_type}生成クラス"""
    
    def __init__(self):
        pass
    
    def process(self):
        """メイン処理"""
        # ベストプラクティス:
        # {' '.join(patterns['best_practices'])}
        pass

def main():
    """メイン関数"""
    generator = {code_type.title()}Generator()
    generator.process()

if __name__ == "__main__":
    main()
'''
        return template

    def _save_new_template(self, code_type: str, template: str):
        """新しいテンプレートを保存"""
        templates_dir = Path("/workspaces/gemini_AI_Agent/agents/templates/learned")
        templates_dir.mkdir(parents=True, exist_ok=True)

        template_file = templates_dir / f"learned_{code_type}.py"
        with open(template_file, "w", encoding="utf-8") as f:
            f.write(template)

        logger.info(f"💾 新しいテンプレート保存: {template_file}")


def main():
    """メインテスト"""
    print("🚀 AI駆動生成システムテスト")

    # AI生成器の初期化
    ai_generator = AICodeGenerator()

    # テストケース
    test_cases = [
        "ユーザー管理APIのエンドポイントを作成",
        "CSVファイルを読み込んでデータ分析するパイプライン",
        "機械学習モデルを訓練するスクリプト",
        "Webアプリケーションの基本構造",
    ]

    # 各テストケースを実行
    for i, description in enumerate(test_cases, 1):
        print(f"\n--- テスト {i}: {description} ---")
        result = ai_generator.generate_code(description)

        print(f"✅ 生成完了")
        print(f"   タイプ: {result['type']}")
        print(f"   品質スコア: {result['quality_score']:.2f}")
        print(f"   使用ナレッジ: {result['knowledge_used']}")
        print(f"   ファイル: {result['file_path'].name}")

    # 統計表示
    stats = ai_generator.get_generation_stats()
    print(f"\n📊 生成統計:")
    print(f"   総生成数: {stats.get('total_generations', 0)}")
    print(f"   平均品質: {stats.get('average_quality', 0):.2f}")
    print(f"   タイプ分布: {stats.get('type_distribution', {})}")

    # テンプレート学習のテスト
    print(f"\n🧠 テンプレート学習テスト")
    learner = TemplateLearner(ai_generator)
    learner.analyze_generation_patterns()

    # 新しいテンプレート生成
    for code_type in ["api", "data"]:
        new_template = learner.generate_new_template(code_type)
        print(f"✅ 新しい{code_type}テンプレート生成完了")


if __name__ == "__main__":
    main()
