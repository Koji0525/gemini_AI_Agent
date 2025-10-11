"""
LocalLLMAgent - ローカルLLM連携エージェント

Ollama、llama.cpp、その他のローカルLLMとのインターフェースを提供し、
クラウドに依存しない自律的なコード修正を実現する。
"""

import requests
import json
import subprocess
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LocalLLMProvider(Enum):
    """ローカルLLMプロバイダー"""
    OLLAMA = "ollama"
    LLAMA_CPP = "llama_cpp"
    GPT4ALL = "gpt4all"
    CUSTOM = "custom"


@dataclass
class LocalLLMConfig:
    """ローカルLLM設定"""
    provider: LocalLLMProvider
    model_name: str
    endpoint: str = "http://localhost:11434"  # Ollamaデフォルト
    timeout: int = 60
    temperature: float = 0.7
    max_tokens: int = 4000
    context_window: int = 8192


class LocalLLMAgent:
    """
    ローカルLLM連携エージェント
    
    主な機能:
    1. Ollamaとの対話
    2. llama.cppとの連携
    3. コード修正プロンプトの構築
    4. ストリーミング対応
    5. エラーハンドリングとフォールバック
    """
    
    def __init__(self, config: Optional[LocalLLMConfig] = None):
        """
        Args:
            config: ローカルLLM設定
        """
        self.config = config or LocalLLMConfig(
            provider=LocalLLMProvider.OLLAMA,
            model_name="codellama:13b-instruct",
            endpoint="http://localhost:11434"
        )
        
        # 接続確認
        self.is_available = self._check_availability()
        
        if not self.is_available:
            logger.warning(f"Local LLM ({self.config.provider.value}) is not available")
        else:
            logger.info(f"LocalLLMAgent initialized with {self.config.provider.value} "
                       f"(model={self.config.model_name})")
    
    def _check_availability(self) -> bool:
        """ローカルLLMの利用可能性をチェック"""
        try:
            if self.config.provider == LocalLLMProvider.OLLAMA:
                # Ollamaの接続確認
                response = requests.get(
                    f"{self.config.endpoint}/api/tags",
                    timeout=5
                )
                return response.status_code == 200
            
            elif self.config.provider == LocalLLMProvider.LLAMA_CPP:
                # llama.cppサーバーの接続確認
                response = requests.get(
                    f"{self.config.endpoint}/health",
                    timeout=5
                )
                return response.status_code == 200
            
            else:
                # カスタムプロバイダーの場合は常にTrueを返す
                return True
                
        except Exception as e:
            logger.debug(f"Availability check failed: {e}")
            return False
    
    async def generate_fix(self, 
                          error_context: Dict[str, Any],
                          file_content: str,
                          file_path: str) -> Dict[str, Any]:
        """
        エラーに対する修正を生成
        
        Args:
            error_context: エラーコンテキスト
            file_content: ファイル内容
            file_path: ファイルパス
        
        Returns:
            修正結果（fixed_code, explanation, confidence）
        """
        if not self.is_available:
            return {
                "success": False,
                "error": "Local LLM is not available"
            }
        
        # プロンプトを構築
        prompt = self._build_fix_prompt(error_context, file_content, file_path)
        
        try:
            # LLMに問い合わせ
            response = await self._query_llm(prompt)
            
            # 応答を解析
            parsed = self._parse_fix_response(response)
            
            return {
                "success": True,
                "fixed_code": parsed.get("fixed_code", ""),
                "explanation": parsed.get("explanation", ""),
                "confidence": parsed.get("confidence", 0.6),
                "changes": parsed.get("changes", [])
            }
            
        except Exception as e:
            logger.error(f"Failed to generate fix: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_fix_prompt(self,
                         error_context: Dict[str, Any],
                         file_content: str,
                         file_path: str) -> str:
        """修正プロンプトを構築"""
        error_type = error_context.get("error_type", "Unknown")
        error_message = error_context.get("error_message", "")
        stack_trace = error_context.get("stack_trace", "")
        line_number = error_context.get("line_number")
        
        prompt = f"""You are an expert code debugger. Fix the following error in the code.

**Error Information:**
- Type: {error_type}
- Message: {error_message}
- File: {file_path}
{f"- Line: {line_number}" if line_number else ""}

**Stack Trace:**
```
{stack_trace[:500] if stack_trace else "N/A"}
```

**Current Code:**
```python
{file_content}
```

**Instructions:**
1. Analyze the error and identify the root cause
2. Provide the complete fixed code
3. Explain what was wrong and how you fixed it
4. Rate your confidence in the fix (0.0-1.0)

**Response Format (JSON):**
```json
{{
  "analysis": "Root cause analysis",
  "fixed_code": "Complete fixed code here",
  "explanation": "What was changed and why",
  "confidence": 0.8,
  "changes": [
    {{"line": 10, "old": "old code", "new": "new code", "reason": "why changed"}}
  ]
}}
```

Provide only the JSON response, no additional text."""
        
        return prompt
    
    async def _query_llm(self, prompt: str) -> str:
        """LLMに問い合わせ"""
        if self.config.provider == LocalLLMProvider.OLLAMA:
            return await self._query_ollama(prompt)
        elif self.config.provider == LocalLLMProvider.LLAMA_CPP:
            return await self._query_llama_cpp(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")
    
    async def _query_ollama(self, prompt: str) -> str:
        """Ollamaに問い合わせ"""
        url = f"{self.config.endpoint}/api/generate"
        
        payload = {
            "model": self.config.model_name,
            "prompt": prompt,
            "temperature": self.config.temperature,
            "options": {
                "num_predict": self.config.max_tokens,
                "num_ctx": self.config.context_window
            },
            "stream": False
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                raise Exception(f"Ollama returned status {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            raise Exception(f"Ollama request timed out after {self.config.timeout}s")
        except Exception as e:
            raise Exception(f"Ollama request failed: {e}")
    
    async def _query_llama_cpp(self, prompt: str) -> str:
        """llama.cppサーバーに問い合わせ"""
        url = f"{self.config.endpoint}/completion"
        
        payload = {
            "prompt": prompt,
            "temperature": self.config.temperature,
            "n_predict": self.config.max_tokens,
            "stop": ["```\n\n", "###"]
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("content", "")
            else:
                raise Exception(f"llama.cpp returned status {response.status_code}")
                
        except requests.exceptions.Timeout:
            raise Exception(f"llama.cpp request timed out after {self.config.timeout}s")
        except Exception as e:
            raise Exception(f"llama.cpp request failed: {e}")
    
    def _parse_fix_response(self, response: str) -> Dict[str, Any]:
        """LLM応答を解析"""
        try:
            # JSON部分を抽出
            json_match = self._extract_json(response)
            
            if json_match:
                parsed = json.loads(json_match)
                
                # 必須フィールドを検証
                if "fixed_code" in parsed:
                    return parsed
            
            # JSONが見つからない場合は、コードブロックを抽出
            code_blocks = self._extract_code_blocks(response)
            
            if code_blocks:
                return {
                    "fixed_code": code_blocks[0],
                    "explanation": "Extracted from response",
                    "confidence": 0.5,
                    "changes": []
                }
            
            raise ValueError("Could not parse fix response")
            
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            raise
    
    def _extract_json(self, text: str) -> Optional[str]:
        """テキストからJSON部分を抽出"""
        import re
        
        # ```json ... ``` パターンを探す
        json_pattern = r'```json\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, text, re.DOTALL)
        
        if match:
            return match.group(1)
        
        # 裸のJSON（{ ... }）を探す
        brace_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        match = re.search(brace_pattern, text, re.DOTALL)
        
        if match:
            return match.group(0)
        
        return None
    
    def _extract_code_blocks(self, text: str) -> List[str]:
        """テキストからコードブロックを抽出"""
        import re
        
        # ```python ... ``` または ``` ... ``` パターン
        pattern = r'```(?:python)?\s*(.*?)\s*```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        return [m.strip() for m in matches if m.strip()]
    
    def generate_code_review(self, code: str, context: str = "") -> Dict[str, Any]:
        """
        コードレビューを生成
        
        Args:
            code: レビュー対象のコード
            context: コンテキスト情報
        
        Returns:
            レビュー結果
        """
        if not self.is_available:
            return {"success": False, "error": "Local LLM is not available"}
        
        prompt = f"""Review the following code and provide feedback.

{f"Context: {context}" if context else ""}

**Code:**
```python
{code}
```

**Review aspects:**
1. Potential bugs or errors
2. Code quality and best practices
3. Performance considerations
4. Security issues
5. Suggestions for improvement

**Response Format (JSON):**
```json
{{
  "issues": [
    {{"severity": "high/medium/low", "line": 10, "description": "Issue description", "suggestion": "How to fix"}}
  ],
  "overall_quality": 7.5,
  "summary": "Overall assessment"
}}
```"""
        
        try:
            response = requests.post(
                f"{self.config.endpoint}/api/generate",
                json={
                    "model": self.config.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                review_text = result.get("response", "")
                
                # 応答を解析
                json_match = self._extract_json(review_text)
                if json_match:
                    return {
                        "success": True,
                        "review": json.loads(json_match)
                    }
            
            return {
                "success": False,
                "error": "Failed to parse review"
            }
            
        except Exception as e:
            logger.error(f"Code review failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def suggest_refactoring(self, code: str, goal: str) -> Dict[str, Any]:
        """
        リファクタリングを提案
        
        Args:
            code: 対象コード
            goal: リファクタリングの目標
        
        Returns:
            リファクタリング提案
        """
        if not self.is_available:
            return {"success": False, "error": "Local LLM is not available"}
        
        prompt = f"""Refactor the following code to achieve: {goal}

**Current Code:**
```python
{code}
```

**Requirements:**
1. Maintain the same functionality
2. Improve code structure and readability
3. Follow Python best practices
4. Add docstrings if missing

**Response Format (JSON):**
```json
{{
  "refactored_code": "Complete refactored code",
  "changes_made": ["List of changes"],
  "benefits": ["Benefits of refactoring"],
  "confidence": 0.85
}}
```"""
        
        try:
            response = requests.post(
                f"{self.config.endpoint}/api/generate",
                json={
                    "model": self.config.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                refactor_text = result.get("response", "")
                
                json_match = self._extract_json(refactor_text)
                if json_match:
                    return {
                        "success": True,
                        "refactoring": json.loads(json_match)
                    }
            
            return {
                "success": False,
                "error": "Failed to parse refactoring"
            }
            
        except Exception as e:
            logger.error(f"Refactoring failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_available_models(self) -> List[str]:
        """利用可能なモデル一覧を取得"""
        if not self.is_available:
            return []
        
        try:
            if self.config.provider == LocalLLMProvider.OLLAMA:
                response = requests.get(
                    f"{self.config.endpoint}/api/tags",
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    models = data.get("models", [])
                    return [m.get("name") for m in models]
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """
        モデルをダウンロード（Ollama）
        
        Args:
            model_name: モデル名
        
        Returns:
            成功したかどうか
        """
        if self.config.provider != LocalLLMProvider.OLLAMA:
            logger.warning("Model pulling is only supported for Ollama")
            return False
        
        try:
            logger.info(f"Pulling model: {model_name}")
            
            response = requests.post(
                f"{self.config.endpoint}/api/pull",
                json={"name": model_name},
                stream=True,
                timeout=600  # 10分
            )
            
            if response.status_code == 200:
                # ストリーミング応答を処理
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        status = data.get("status")
                        
                        if status:
                            logger.info(f"Pull status: {status}")
                        
                        if data.get("error"):
                            logger.error(f"Pull error: {data['error']}")
                            return False
                
                logger.info(f"Successfully pulled model: {model_name}")
                return True
            else:
                logger.error(f"Pull failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to pull model: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """現在のモデル情報を取得"""
        if not self.is_available:
            return {"available": False}
        
        try:
            if self.config.provider == LocalLLMProvider.OLLAMA:
                response = requests.post(
                    f"{self.config.endpoint}/api/show",
                    json={"name": self.config.model_name},
                    timeout=5
                )
                
                if response.status_code == 200:
                    return {
                        "available": True,
                        "provider": self.config.provider.value,
                        "model": self.config.model_name,
                        "details": response.json()
                    }
            
            return {
                "available": True,
                "provider": self.config.provider.value,
                "model": self.config.model_name
            }
            
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return {"available": False, "error": str(e)}


# 使用例
if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    
    # ローカルLLMエージェントを作成
    agent = LocalLLMAgent(
        config=LocalLLMConfig(
            provider=LocalLLMProvider.OLLAMA,
            model_name="codellama:13b-instruct",
            endpoint="http://localhost:11434"
        )
    )
    
    if not agent.is_available:
        print("⚠️  Local LLM is not available. Please start Ollama server:")
        print("   ollama serve")
        print("\n   Or install and run Ollama from: https://ollama.ai")
        exit(1)
    
    # 利用可能なモデル一覧
    print("\n=== Available Models ===")
    models = agent.list_available_models()
    for model in models:
        print(f"- {model}")
    
    # モデル情報
    print("\n=== Model Info ===")
    info = agent.get_model_info()
    print(json.dumps(info, indent=2))
    
    # サンプルエラーコンテキスト
    error_context = {
        "error_type": "NameError",
        "error_message": "name 'calculate_total' is not defined",
        "line_number": 15,
        "stack_trace": "Traceback (most recent call last):\n  File 'app.py', line 15, in process_data\n    result = calculate_total(items)"
    }
    
    file_content = """def process_data(items):
    # Process items and calculate total
    result = calculate_total(items)
    return result

def main():
    items = [1, 2, 3, 4, 5]
    total = process_data(items)
    print(f"Total: {total}")
"""
    
    # 修正を生成
    async def test_fix():
        print("\n=== Generating Fix ===")
        result = await agent.generate_fix(
            error_context=error_context,
            file_content=file_content,
            file_path="app.py"
        )
        
        if result["success"]:
            print(f"\n✅ Fix generated (confidence: {result['confidence']})")
            print(f"\nExplanation: {result['explanation']}")
            print(f"\nFixed Code:\n{result['fixed_code']}")
        else:
            print(f"\n❌ Fix failed: {result['error']}")
    
    asyncio.run(test_fix())
