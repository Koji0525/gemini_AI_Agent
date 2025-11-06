"""
ErrorRecoveryAgent - エラー自動修復エージェント
v1.15.0 - 2025-11-06

【責任範囲】
- エラーの分類と診断
- 過去のナレッジからの修復戦略検索
- 自動修復の適用
"""

import os
import json
import traceback
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path


class ErrorRecoveryAgent:
    """エラー自動修復エージェント"""

    def __init__(self, rag_engine=None):
        """
        初期化

        Args:
            rag_engine: RAGエンジンインスタンス（外部注入）
        """
        self.rag_engine = rag_engine
        self.recovery_history = []

        # エラー分類パターン
        self.error_patterns = {
            "SyntaxError": "syntax",
            "IndentationError": "syntax",
            "ImportError": "dependency",
            "ModuleNotFoundError": "dependency",
            "AttributeError": "api",
            "TypeError": "type",
            "ValueError": "value",
            "KeyError": "data",
            "FileNotFoundError": "file",
            "PermissionError": "permission",
        }

    async def diagnose_error(self, error: Exception, context: Dict = None) -> Dict:
        """
        エラーを診断

        Args:
            error: 発生したエラー
            context: エラーのコンテキスト情報

        Returns:
            診断結果
        """
        try:
            print(f"🔍 エラー診断開始: {type(error).__name__}")

            # エラー情報を抽出
            error_type = type(error).__name__
            error_message = str(error)
            error_traceback = traceback.format_exc()

            # エラー分類
            category = self.error_patterns.get(error_type, "unknown")

            # 類似エラーを検索
            similar_errors = await self._search_similar_errors(error_type, error_message)

            # 修復戦略を決定
            strategy = self._determine_strategy(error_type, category, similar_errors)

            diagnosis = {
                "error_type": error_type,
                "error_message": error_message,
                "category": category,
                "similar_errors_found": len(similar_errors),
                "strategy": strategy,
                "confidence": self._calculate_confidence(similar_errors),
                "timestamp": datetime.now().isoformat(),
            }

            print(f"✅ 診断完了: カテゴリ={category}, 信頼度={diagnosis['confidence']}%")

            return diagnosis

        except Exception as e:
            print(f"❌ 診断エラー: {e}")
            return {
                "error_type": "DiagnosisError",
                "error_message": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def apply_fix(self, error: Exception, strategy: Dict, context: Dict = None) -> Dict:
        """
        修復戦略を適用

        Args:
            error: 修復対象のエラー
            strategy: 修復戦略
            context: コンテキスト情報

        Returns:
            修復結果
        """
        try:
            print(f"🔧 修復適用開始: {strategy.get('type', 'unknown')}")

            result = {
                "strategy_applied": strategy.get("type"),
                "success": False,
                "actions_taken": [],
                "timestamp": datetime.now().isoformat(),
            }

            # 戦略タイプに応じた修復
            if strategy.get("type") == "dependency":
                fix_result = await self._fix_dependency_error(error, strategy)
            elif strategy.get("type") == "syntax":
                fix_result = await self._fix_syntax_error(error, strategy)
            elif strategy.get("type") == "api":
                fix_result = await self._fix_api_error(error, strategy)
            else:
                fix_result = await self._fix_generic_error(error, strategy)

            result.update(fix_result)

            # 履歴に記録
            self.recovery_history.append(result)

            status = "✅ 修復成功" if result["success"] else "❌ 修復失敗"
            print(f"{status}: {len(result['actions_taken'])}個のアクション実行")

            return result

        except Exception as e:
            print(f"❌ 修復適用エラー: {e}")
            return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}

    async def _search_similar_errors(self, error_type: str, error_message: str) -> List[Dict]:
        """類似エラーを検索"""
        if not self.rag_engine:
            return []

        query = f"{error_type} {error_message}"
        results = self.rag_engine.search(query, top_k=5)

        return results if results else []

    def _determine_strategy(
        self, error_type: str, category: str, similar_errors: List[Dict]
    ) -> Dict:
        """修復戦略を決定"""

        # 類似エラーから戦略を抽出
        if similar_errors:
            # 最も類似度が高いエラーの解決策を採用
            best_match = similar_errors[0]
            return {
                "type": category,
                "source": "knowledge_base",
                "solution": best_match.get("solution", ""),
                "steps": best_match.get("steps", []),
            }

        # デフォルト戦略
        default_strategies = {
            "dependency": {
                "type": "dependency",
                "source": "default",
                "solution": "パッケージのインストールまたは再インストール",
                "steps": ["pip install --upgrade <package>"],
            },
            "syntax": {
                "type": "syntax",
                "source": "default",
                "solution": "構文エラーの修正",
                "steps": ["コードの構文を確認", "インデントを修正"],
            },
            "api": {
                "type": "api",
                "source": "default",
                "solution": "APIの正しい使用方法を確認",
                "steps": ["APIドキュメントを確認", "メソッド名を修正"],
            },
        }

        return default_strategies.get(
            category,
            {
                "type": "unknown",
                "source": "default",
                "solution": "エラーの詳細調査が必要",
                "steps": ["ログを確認", "再現手順を特定"],
            },
        )

    def _calculate_confidence(self, similar_errors: List[Dict]) -> int:
        """修復の信頼度を計算（0-100）"""
        if not similar_errors:
            return 30  # ナレッジなしの場合は低信頼度

        # 類似度が高いほど信頼度も高い
        best_similarity = similar_errors[0].get("similarity", 0)

        if best_similarity > 0.9:
            return 95
        elif best_similarity > 0.8:
            return 85
        elif best_similarity > 0.7:
            return 75
        elif best_similarity > 0.6:
            return 65
        else:
            return 50

    async def _fix_dependency_error(self, error: Exception, strategy: Dict) -> Dict:
        """依存関係エラーを修復"""
        actions = []

        # エラーメッセージからパッケージ名を抽出
        error_msg = str(error)
        if "No module named" in error_msg:
            package_name = error_msg.split("'")[1]
            actions.append(f"パッケージインストール推奨: pip install {package_name}")

        return {
            "success": True,
            "actions_taken": actions,
            "recommendation": f"requirements.txtに{package_name}を追加してください",
        }

    async def _fix_syntax_error(self, error: Exception, strategy: Dict) -> Dict:
        """構文エラーを修復"""
        actions = ["構文エラーの手動修正が必要"]

        return {
            "success": False,
            "actions_taken": actions,
            "recommendation": "コードエディタで構文を確認してください",
        }

    async def _fix_api_error(self, error: Exception, strategy: Dict) -> Dict:
        """API使用エラーを修復"""
        actions = ["API使用方法の確認が必要"]

        return {
            "success": False,
            "actions_taken": actions,
            "recommendation": "APIドキュメントを参照してください",
        }

    async def _fix_generic_error(self, error: Exception, strategy: Dict) -> Dict:
        """汎用エラー修復"""
        actions = ["詳細な調査が必要"]

        return {
            "success": False,
            "actions_taken": actions,
            "recommendation": "ログとスタックトレースを確認してください",
        }

    def get_statistics(self) -> Dict:
        """修復統計を取得"""
        total = len(self.recovery_history)
        successful = sum(1 for h in self.recovery_history if h.get("success"))

        return {
            "total_recoveries": total,
            "successful_recoveries": successful,
            "failed_recoveries": total - successful,
            "success_rate": (successful / total * 100) if total > 0 else 0,
        }
