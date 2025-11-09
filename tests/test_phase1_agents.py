"""
Phase 1 エージェント統合テスト
v1.15.0 - 2025-11-06
"""

import asyncio
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.code_generation.code_generation_agent import CodeGenerationAgent
from agents.testing.testing_agent import TestingAgent
from agents.error_recovery.error_recovery_agent import ErrorRecoveryAgent


async @pytest.mark.skipif(not os.getenv('GEMINI_API_KEY'), reason="Gemini APIキーが必要")
def test_code_generation():
    """コード生成テスト（モックを使用）"""
    from unittest.mock import patch, MagicMock
    
    # Gemini APIをモック
    with patch('agents.code_generation.code_generation_agent.GeminiAPI') as mock_gemini:
        # モックの設定
        mock_instance = MagicMock()
        mock_instance.generate_code.return_value = {
            "code": "def add(a, b):
    return a + b",
            "quality_score": 8,
            "syntax_check": True,
            "explanation": "シンプルな加算関数"
        }
        mock_gemini.return_value = mock_instance
        
        from agents.code_generation.code_generation_agent import CodeGenerationAgent
        agent = CodeGenerationAgent()
        
        # テスト実行
        result = agent.generate_code("2つの数値を加算する関数を作成してください")
        
        # アサーション
        assert "quality_score" in result
        assert result["quality_score"] == 8
        assert "def add" in result["code"]
        print(f"✅ コード生成テスト成功: 品質スコア {result['quality_score']}/10")
