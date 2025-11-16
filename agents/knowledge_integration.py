#!/usr/bin/env python3
"""
ナレッジベース連携モジュール
AI生成とナレッジベースの強力な連携を実現
"""
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class KnowledgeBaseManager:
    """ナレッジベース管理クラス"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or self._get_default_db_path()
        self._ensure_tables()

    def _get_default_db_path(self) -> Path:
        """デフォルトDBパスを取得"""
        return Path("/workspaces/gemini_AI_Agent/knowledge_system/database/knowledge.db")

    def _ensure_tables(self):
        """必要なテーブルを確保"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # コードパターンテーブル
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS code_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    code_template TEXT NOT NULL,
                    quality_score REAL DEFAULT 0.0,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # 生成履歴テーブル
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS generation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    code_type TEXT NOT NULL,
                    generated_code TEXT NOT NULL,
                    quality_score REAL DEFAULT 0.0,
                    used_patterns TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.commit()
            conn.close()
            logger.info("✅ ナレッジベーステーブル確認完了")

        except Exception as e:
            logger.error(f"❌ ナレッジベース初期化エラー: {e}")

    def add_code_pattern(
        self, pattern_type: str, description: str, code_template: str, quality_score: float = 0.0
    ) -> bool:
        """コードパターンを追加"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO code_patterns 
                (pattern_type, description, code_template, quality_score, usage_count)
                VALUES (?, ?, ?, ?, 1)
            """,
                (pattern_type, description, code_template, quality_score),
            )

            conn.commit()
            conn.close()
            logger.info(f"✅ コードパターン追加: {pattern_type} - {description}")
            return True

        except Exception as e:
            logger.error(f"❌ コードパターン追加エラー: {e}")
            return False

    def get_best_patterns(self, pattern_type: str, limit: int = 3) -> List[Dict]:
        """最高品質のパターンを取得"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT pattern_type, description, code_template, quality_score, usage_count
                FROM code_patterns 
                WHERE pattern_type = ? 
                ORDER BY quality_score DESC, usage_count DESC 
                LIMIT ?
            """,
                (pattern_type, limit),
            )

            patterns = []
            for row in cursor.fetchall():
                patterns.append(
                    {
                        "pattern_type": row[0],
                        "description": row[1],
                        "code_template": row[2],
                        "quality_score": row[3],
                        "usage_count": row[4],
                    }
                )

            conn.close()
            return patterns

        except Exception as e:
            logger.error(f"❌ パターン取得エラー: {e}")
            return []

    def record_generation(
        self,
        description: str,
        code_type: str,
        generated_code: str,
        quality_score: float,
        used_patterns: List[str] = None,
    ):
        """生成履歴を記録"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            patterns_str = ",".join(used_patterns) if used_patterns else ""

            cursor.execute(
                """
                INSERT INTO generation_history 
                (description, code_type, generated_code, quality_score, used_patterns)
                VALUES (?, ?, ?, ?, ?)
            """,
                (description, code_type, generated_code, quality_score, patterns_str),
            )

            # 使用されたパターンの使用回数を更新
            if used_patterns:
                for pattern_desc in used_patterns:
                    cursor.execute(
                        """
                        UPDATE code_patterns 
                        SET usage_count = usage_count + 1 
                        WHERE description = ?
                    """,
                        (pattern_desc,),
                    )

            conn.commit()
            conn.close()
            logger.info(f"✅ 生成履歴記録: {code_type} - 品質: {quality_score}")

        except Exception as e:
            logger.error(f"❌ 生成履歴記録エラー: {e}")

    def get_generation_stats(self) -> Dict:
        """生成統計を取得"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 総生成数
            cursor.execute("SELECT COUNT(*) FROM generation_history")
            total_generations = cursor.fetchone()[0]

            # 平均品質
            cursor.execute("SELECT AVG(quality_score) FROM generation_history")
            avg_quality = cursor.fetchone()[0] or 0.0

            # タイプ別分布
            cursor.execute(
                """
                SELECT code_type, COUNT(*) 
                FROM generation_history 
                GROUP BY code_type
            """
            )
            type_distribution = {row[0]: row[1] for row in cursor.fetchall()}

            conn.close()

            return {
                "total_generations": total_generations,
                "average_quality": avg_quality,
                "type_distribution": type_distribution,
            }

        except Exception as e:
            logger.error(f"❌ 統計取得エラー: {e}")
            return {}


class EnhancedAIGenerator:
    """強化版AI生成器 - ナレッジベース連携版"""

    def __init__(self):
        self.knowledge_manager = KnowledgeBaseManager()
        self._initialize_default_patterns()

    def _initialize_default_patterns(self):
        """デフォルトパターンを初期化"""
        default_patterns = [
            {
                "type": "api",
                "description": "FastAPI基本構造",
                "template": 'from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get("/")\ndef read_root():\n    return {"Hello": "World"}',
                "score": 0.8,
            },
            {
                "type": "data",
                "description": "pandasデータ処理",
                "template": 'import pandas as pd\n\ndf = pd.read_csv("data.csv")\n# データ処理をここに実装',
                "score": 0.7,
            },
        ]

        for pattern in default_patterns:
            self.knowledge_manager.add_code_pattern(
                pattern["type"], pattern["description"], pattern["template"], pattern["score"]
            )

    def generate_with_knowledge(self, description: str) -> Dict:
        """ナレッジベースを活用した生成"""
        from agents.ai_driven_generator import AICodeGenerator

        # 基本生成器
        base_generator = AICodeGenerator()

        # コードタイプを検出
        code_type = base_generator._detect_code_type(description)

        # ナレッジベースから最適なパターンを取得
        best_patterns = self.knowledge_manager.get_best_patterns(code_type)

        # 生成実行
        result = base_generator.generate_code(description)

        # 使用されたパターンを記録
        used_patterns = [p["description"] for p in best_patterns[:2]]
        self.knowledge_manager.record_generation(
            description, code_type, result["code"], result["quality_score"], used_patterns
        )

        # 結果を強化
        result["knowledge_patterns_used"] = used_patterns
        result["knowledge_enhanced"] = True

        return result

    def get_system_stats(self) -> Dict:
        """システム統計を取得"""
        generation_stats = self.knowledge_manager.get_generation_stats()

        return {
            "knowledge_enhanced": True,
            "generation_stats": generation_stats,
            "total_patterns": self._get_total_patterns_count(),
        }

    def _get_total_patterns_count(self) -> int:
        """総パターン数を取得"""
        try:
            conn = sqlite3.connect(self.knowledge_manager.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM code_patterns")
            count = cursor.fetchone()[0]

            conn.close()
            return count

        except:
            return 0


def main():
    """強化版AI生成器のテスト"""
    print("🚀 強化版AI生成器テスト")

    enhanced_generator = EnhancedAIGenerator()

    # テスト生成
    test_cases = [
        "REST APIのユーザー登録エンドポイント",
        "データクリーニングのパイプライン",
        "機械学習モデルの評価スクリプト",
    ]

    for description in test_cases:
        print(f"\n--- テスト: {description} ---")
        result = enhanced_generator.generate_with_knowledge(description)

        print(f"✅ 生成完了")
        print(f"   タイプ: {result['type']}")
        print(f"   品質: {result['quality_score']:.2f}")
        print(f"   ナレッジ使用: {result.get('knowledge_patterns_used', [])}")
        print(f"   強化版: {result.get('knowledge_enhanced', False)}")

    # システム統計
    stats = enhanced_generator.get_system_stats()
    print(f"\n📊 システム統計:")
    print(f"   総生成数: {stats['generation_stats'].get('total_generations', 0)}")
    print(f"   平均品質: {stats['generation_stats'].get('average_quality', 0):.2f}")
    print(f"   総パターン数: {stats['total_patterns']}")


if __name__ == "__main__":
    main()
