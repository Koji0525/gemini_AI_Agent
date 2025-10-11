# error_classifier.py
"""
エラー分類器
エラーの複雑度と種類を判定
"""

import logging
import re
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ErrorContextModel:
    """エラーコンテキストのデータモデル"""
    error_type: str
    error_message: Optional[str] = None
    surrounding_code: Optional[str] = None
    full_traceback: Optional[str] = None


class ErrorComplexity(Enum):
    """エラー複雑度"""
    SIMPLE = "simple"      # 単純（ルールベースで対応可能）
    MEDIUM = "medium"      # 中程度（ローカルAIで対応可能）
    COMPLEX = "complex"    # 複雑（クラウドAI推奨）


class ErrorCategory(Enum):
    """エラーカテゴリ"""
    SYNTAX = "syntax"                    # 構文エラー
    IMPORT = "import"                    # インポートエラー
    RUNTIME = "runtime"                  # 実行時エラー
    LOGIC = "logic"                      # ロジックエラー
    DESIGN = "design"                    # 設計レベルの問題
    PERFORMANCE = "performance"          # パフォーマンス問題
    SECURITY = "security"                # セキュリティ問題
    UNKNOWN = "unknown"                  # 不明


class ErrorClassifier:
    """
    エラー分類器
    
    機能:
    - エラーの複雑度判定
    - エラーカテゴリの分類
    - 修正戦略の推奨
    - 信頼度スコアの算出
    """
    
    def __init__(self):
        """初期化"""
        self._init_classification_rules()
        logger.info("✅ ErrorClassifier 初期化完了")
    
    def _init_classification_rules(self):
        """分類ルールを初期化"""
        
        # 単純なエラーパターン（ルールベースで対応可能）
        self.simple_patterns = {
            "SyntaxError": ErrorCategory.SYNTAX,
            "IndentationError": ErrorCategory.SYNTAX,
            "ImportError": ErrorCategory.IMPORT,
            "ModuleNotFoundError": ErrorCategory.IMPORT,
        }
        
        # 中程度のエラーパターン
        self.medium_patterns = {
            "AttributeError": ErrorCategory.RUNTIME,
            "NameError": ErrorCategory.RUNTIME,
            "TypeError": ErrorCategory.RUNTIME,
            "ValueError": ErrorCategory.RUNTIME,
            "KeyError": ErrorCategory.RUNTIME,
            "IndexError": ErrorCategory.RUNTIME,
        }
        
        # 複雑なエラーパターン
        self.complex_patterns = {
            "RecursionError": ErrorCategory.LOGIC,
            "MemoryError": ErrorCategory.PERFORMANCE,
            "RuntimeError": ErrorCategory.LOGIC,
            "AssertionError": ErrorCategory.LOGIC,
        }
        
        # 複雑度判定の重み付け要因
        self.complexity_factors = {
            "multi_file": 2.0,           # 複数ファイルにまたがる
            "async_code": 1.5,           # 非同期コード
            "class_hierarchy": 1.8,      # クラス階層が複雑
            "external_dependency": 1.3,  # 外部依存関係
            "database_operation": 1.6,   # データベース操作
            "network_operation": 1.5,    # ネットワーク操作
            "file_operation": 1.2,       # ファイル操作
            "concurrency": 2.0,          # 並行処理
        }
    
    def classify(self, error_context: ErrorContextModel) -> Dict[str, Any]:
        """
        エラーを分類
        
        Args:
            error_context: エラーコンテキスト
            
        Returns:
            Dict: 分類結果
        """
        try:
            # 基本分類
            error_type = error_context.error_type
            category = self._classify_category(error_type)
            
            # 複雑度判定
            complexity_score = self._calculate_complexity_score(error_context)
            complexity = self._determine_complexity(complexity_score)
            
            # 信頼度計算
            confidence = self._calculate_confidence(error_context, category, complexity)
            
            # 推奨戦略
            recommended_strategy = self._recommend_strategy(complexity, confidence)
            
            result = {
                "error_type": error_type,
                "category": category.value,
                "complexity": complexity.value,
                "complexity_score": complexity_score,
                "confidence": confidence,
                "recommended_strategy": recommended_strategy,
                "factors": self._identify_complexity_factors(error_context)
            }
            
            logger.info(
                f"📊 エラー分類: {error_type} → "
                f"{category.value}/{complexity.value} "
                f"(スコア={complexity_score:.2f}, 信頼度={confidence:.2f})"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ エラー分類失敗: {e}", exc_info=True)
            
            # デフォルト値を返す
            return {
                "error_type": error_context.error_type,
                "category": ErrorCategory.UNKNOWN.value,
                "complexity": ErrorComplexity.MEDIUM.value,
                "complexity_score": 1.0,
                "confidence": 0.5,
                "recommended_strategy": "cloud_first",
                "factors": []
            }
    
    def _classify_category(self, error_type: str) -> ErrorCategory:
        """エラーカテゴリを分類"""
        
        # 単純パターンチェック
        if error_type in self.simple_patterns:
            return self.simple_patterns[error_type]
        
        # 中程度パターンチェック
        if error_type in self.medium_patterns:
            return self.medium_patterns[error_type]
        
        # 複雑パターンチェック
        if error_type in self.complex_patterns:
            return self.complex_patterns[error_type]
        
        # その他のパターンマッチング
        if "Import" in error_type or "Module" in error_type:
            return ErrorCategory.IMPORT
        
        if "Syntax" in error_type or "Indent" in error_type:
            return ErrorCategory.SYNTAX
        
        if "Runtime" in error_type:
            return ErrorCategory.RUNTIME
        
        # デフォルト
        return ErrorCategory.UNKNOWN
    
    def _calculate_complexity_score(self, error_context: ErrorContextModel) -> float:
        """複雑度スコアを計算"""
        
        base_score = 1.0
        
        # エラータイプによる基本スコア
        if error_context.error_type in self.simple_patterns:
            base_score = 0.3
        elif error_context.error_type in self.medium_patterns:
            base_score = 1.0
        elif error_context.error_type in self.complex_patterns:
            base_score = 2.0
        
        # 複雑度要因を適用
        factors = self._identify_complexity_factors(error_context)
        
        for factor in factors:
            weight = self.complexity_factors.get(factor, 1.0)
            base_score *= weight
        
        return base_score
    
    def _identify_complexity_factors(self, error_context: ErrorContextModel) -> list:
        """複雑度要因を特定"""
        factors = []
        
        # コンテキスト情報から判定
        code = error_context.surrounding_code or ""
        traceback = error_context.full_traceback or ""
        
        # 非同期コード
        if "async " in code or "await " in code:
            factors.append("async_code")
        
        # クラス階層
        if "class " in code and "super()" in code:
            factors.append("class_hierarchy")
        
        # 外部依存関係
        if "import " in code or "from " in code:
            factors.append("external_dependency")
        
        # データベース操作
        if any(db in code.lower() for db in ["sql", "database", "db.", "cursor", "query"]):
            factors.append("database_operation")
        
        # ネットワーク操作
        if any(net in code.lower() for net in ["http", "request", "socket", "api"]):
            factors.append("network_operation")
        
        # ファイル操作
        if any(file_op in code.lower() for file_op in ["open(", "file", "read(", "write("]):
            factors.append("file_operation")
        
        # 並行処理
        if any(conc in code.lower() for conc in ["thread", "process", "lock", "queue"]):
            factors.append("concurrency")
        
        # 複数ファイル（スタックトレースから判定）
        if traceback:
            file_count = len(set(re.findall(r'File "(.*?)"', traceback)))
            if file_count > 1:
                factors.append("multi_file")
        
        return factors
    
    def _determine_complexity(self, complexity_score: float) -> ErrorComplexity:
        """スコアから複雑度を決定"""
        
        if complexity_score < 0.5:
            return ErrorComplexity.SIMPLE
        elif complexity_score < 1.5:
            return ErrorComplexity.MEDIUM
        else:
            return ErrorComplexity.COMPLEX
    
    def _calculate_confidence(
        self, 
        error_context: ErrorContextModel,
        category: ErrorCategory,
        complexity: ErrorComplexity
    ) -> float:
        """分類の信頼度を計算"""
        
        confidence = 0.5  # 基本値
        
        # エラータイプが既知パターンに一致する場合は高信頼度
        if error_context.error_type in self.simple_patterns or \
           error_context.error_type in self.medium_patterns or \
           error_context.error_type in self.complex_patterns:
            confidence += 0.3
        
        # エラーメッセージが明確な場合
        if error_context.error_message and len(error_context.error_message) > 10:
            confidence += 0.1
        
        # 周辺コードが利用可能な場合
        if error_context.surrounding_code:
            confidence += 0.1
        
        # スタックトレースが利用可能な場合
        if error_context.full_traceback:
            confidence += 0.05
        
        # 信頼度を0-1に正規化
        return min(confidence, 1.0)
    
    def _recommend_strategy(self, complexity: ErrorComplexity, confidence: float) -> str:
        """推奨戦略を決定"""
        
        if complexity == ErrorComplexity.SIMPLE:
            if confidence > 0.8:
                return "local_only"
            else:
                return "local_first"
        
        elif complexity == ErrorComplexity.MEDIUM:
            if confidence > 0.7:
                return "local_first"
            else:
                return "cloud_first"
        
        else:  # COMPLEX
            if confidence > 0.6:
                return "cloud_first"
            else:
                return "cloud_only"
    
    def print_classification(self, classification: Dict[str, Any]):
        """分類結果を表示"""
        print("\n" + "=" * 60)
        print("📊 エラー分類結果")
        print("=" * 60)
        print(f"エラータイプ: {classification['error_type']}")
        print(f"カテゴリ: {classification['category']}")
        print(f"複雑度: {classification['complexity']} (スコア={classification['complexity_score']:.2f})")
        print(f"信頼度: {classification['confidence']:.1%}")
        print(f"推奨戦略: {classification['recommended_strategy']}")
        
        if classification['factors']:
            print("\n複雑度要因:")
            for factor in classification['factors']:
                print(f"  - {factor}")
        
        print("=" * 60 + "\n")


# 使用例
if __name__ == "__main__":
    # テスト用のエラーコンテキスト
    test_context = ErrorContextModel(
        error_type="ImportError",
        error_message="No module named 'nonexistent_module'",
        surrounding_code="import nonexistent_module",
        full_traceback="Traceback (most recent call last):\n  File \"test.py\", line 1, in <module>\n    import nonexistent_module\nImportError: No module named 'nonexistent_module'"
    )
    
    classifier = ErrorClassifier()
    result = classifier.classify(test_context)
    classifier.print_classification(result)