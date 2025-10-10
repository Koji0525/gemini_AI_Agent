# auto_fix_agent.py
import asyncio
import ast
import tokenize
import logging
from pathlib import Path
from typing import Dict, List, Optional
import difflib

logger = logging.getLogger(__name__)

class AutoFixAgent:
    """自動修正エージェント"""
    
    FIX_SYSTEM_PROMPT = """あなたは優秀なPythonデバッグアシスタントです。

【あなたの役割】
- コマンド実行エラーを分析する
- 具体的な修正コードを提案する
- 修正の理由を説明する
- 完全な修正ファイルを提供する

【出力形式】
以下のJSON形式で出力してください：

```json
{
  "analysis": "エラーの原因分析",
  "fix_reason": "修正の理由",
  "fixed_code": "修正後の完全なコード",
  "changes": [
    {
      "file": "修正ファイル名",
      "line": 行番号,
      "original": "元のコード",
      "fixed": "修正後のコード",
      "reason": "修正理由"
    }
  ],
  "confidence": 0.8,
  "next_step": "次の実行コマンド"
}