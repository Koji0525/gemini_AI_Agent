#!/usr/bin/env python3
"""
PMAgent v32 Detailed - 詳細タスク分解システム (既存システム統合版)

【変更内容】
1. python-dotenvで.env自動読み込み
2. max_tokens: 8000 → 20000 (2.5倍増)
3. プロンプト強化: 500-1000文字の詳細な説明を要求
4. JSON解析堅牢化: リトライ、部分抽出、エスケープ処理追加
5. 既存システムとの互換性確保

【狙い】
- タスク説明を100文字 → 500-1000文字に拡張
- JSON解析エラーの根絶
- より実行可能な詳細タスクの生成
- .envファイルからの自動環境変数読み込み

【統合パス】
- core_agents/pm_agent_v32_detailed.py
"""

import os
import sys
import json
import logging
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# ===========================
# プロジェクトルート設定
# ===========================
# このファイルの親の親ディレクトリをプロジェクトルートとする
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# ===========================
# .env読み込み (最優先)
# ===========================
try:
    from dotenv import load_dotenv
    
    # .envファイルのパス
    env_path = project_root / '.env'
    
    if env_path.exists():
        load_dotenv(env_path)
        logger_init_msg = f"✅ .envファイル読み込み成功: {env_path}"
    else:
        logger_init_msg = f"⚠️  .envファイルが見つかりません: {env_path}"
except ImportError:
    logger_init_msg = "⚠️  python-dotenvが未インストール。pip install python-dotenv を実行してください"
except Exception as e:
    logger_init_msg = f"⚠️  .env読み込みエラー: {e}"

# ===========================
# ロギング設定
# ===========================
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)
logger.info(logger_init_msg)

# ===========================
# Gemini API設定
# ===========================
import google.generativeai as genai


class TaskBreakdownEngine:
    """
    タスク分解エンジン - 詳細度強化版
    
    【特徴】
    - 500-1000文字の詳細な作業内容を生成
    - Google Docstringスタイルの構造化
    - JSON解析の堅牢性向上
    - .env自動読み込み
    
    【運用ルール準拠】
    - PEP 8準拠
    - 依存性注入の原則（APIキーは外部から注入可能）
    - 非同期処理対応（将来拡張）
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初期化
        
        Args:
            api_key: Gemini API Key (Noneの場合は環境変数から取得)
            
        Raises:
            ValueError: API Keyが設定されていない場合
        """
        # APIキーの取得（優先順位: 引数 > 環境変数）
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            error_msg = (
                "GEMINI_API_KEY が設定されていません。\n"
                "以下のいずれかの方法で設定してください:\n"
                "1. .envファイルに追加: GEMINI_API_KEY=your-api-key\n"
                "2. 環境変数として設定: export GEMINI_API_KEY=your-api-key\n"
                "3. コンストラクタで指定: TaskBreakdownEngine(api_key='your-api-key')"
            )
            raise ValueError(error_msg)
        
        # Gemini API設定
        genai.configure(api_key=self.api_key)
        
        # モデル設定: max_tokensを大幅増加
        self.model = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 20000,  # 8000 → 20000に増加
            }
        )
        
        logger.info("✅ TaskBreakdownEngine 初期化完了 (max_tokens=20000)")
    
    def breakdown_goal_to_detailed_tasks(
        self, 
        goal_description: str,
        num_tasks: int = 8
    ) -> List[Dict[str, str]]:
        """
        ゴールを詳細なタスクに分解
        
        Args:
            goal_description: ゴールの説明文
            num_tasks: 生成するタスク数 (デフォルト: 8)
        
        Returns:
            タスクリスト [{"task_name": str, "description": str}, ...]
            
        Raises:
            Exception: Gemini API呼び出しまたはJSON解析に失敗した場合
        """
        prompt = self._create_detailed_prompt(goal_description, num_tasks)
        
        try:
            # Gemini API呼び出し (リトライ機能付き)
            response = self._call_gemini_with_retry(prompt, max_retries=3)
            response_text = response.text
            
            logger.info(f"📥 Gemini APIレスポンス受信 ({len(response_text)} 文字)")
            
            # JSON抽出 (堅牢化版)
            tasks = self._extract_json_from_response(response_text)
            
            # 検証
            if not tasks or len(tasks) == 0:
                raise ValueError("タスクが生成されませんでした")
            
            # 詳細度チェック
            for task in tasks:
                desc_len = len(task.get('description', ''))
                if desc_len < 300:
                    logger.warning(
                        f"⚠️ タスク '{task.get('task_name', 'unknown')}' の "
                        f"説明が短い ({desc_len}文字)"
                    )
            
            logger.info(f"✅ {len(tasks)}件のタスクを生成しました")
            return tasks
            
        except Exception as e:
            logger.error(f"❌ タスク分解エラー: {e}")
            raise
    
    def _create_detailed_prompt(self, goal_description: str, num_tasks: int) -> str:
        """
        詳細度強化版プロンプトを作成
        
        【特徴】
        - 500-1000文字の詳細な説明を要求
        - Google Docstring形式を指定
        - 具体的な構造を例示
        
        Args:
            goal_description: ゴールの説明
            num_tasks: タスク数
            
        Returns:
            プロンプト文字列
        """
        return f"""あなたはプロジェクトマネージャーです。以下のゴールを**{num_tasks}個の具体的で詳細なタスク**に分解してください。

【ゴール】
{goal_description}

【重要な要件】
1. **各タスクの説明は必ず500文字以上、1000文字以下で記述すること**
2. **Google Docstringスタイルで構造化すること**
3. 以下の項目を必ず含めること:
   - 【目的】: なぜこのタスクが必要か (2-3行)
   - 【作業内容】: 具体的な手順 (5-10ステップ)
   - 【対象ファイル】: 操作するファイルパス (あれば)
   - 【成果物】: 何が完成するか (2-3項目)
   - 【検証方法】: 完了をどう確認するか (2-3項目)
   - 【注意事項】: リスクや制約 (あれば)

【出力形式】
以下の**JSONのみ**を出力してください。説明文やコードブロックは不要です:

[
  {{
    "task_name": "タスク名（50文字以内）",
    "description": "【目的】\\n（目的を記述）\\n\\n【作業内容】\\n1. 手順1\\n2. 手順2...\\n\\n【対象ファイル】\\n- ファイルパス1\\n- ファイルパス2\\n\\n【成果物】\\n- 成果物1\\n- 成果物2\\n\\n【検証方法】\\n- 検証1\\n- 検証2\\n\\n【注意事項】\\n- 注意点1"
  }}
]

【JSON作成時の注意】
- description内の改行は \\n でエスケープすること
- ダブルクォート内のダブルクォートは \\" でエスケープすること
- 各タスクのdescriptionは500-1000文字であること
- JSONは必ず正しい構文で閉じること

それでは、{num_tasks}個のタスクをJSON形式で生成してください:
"""
    
    def _call_gemini_with_retry(
        self, 
        prompt: str, 
        max_retries: int = 3
    ) -> Any:
        """
        Gemini API呼び出し (リトライ機能付き)
        
        Args:
            prompt: プロンプト
            max_retries: 最大リトライ回数
        
        Returns:
            Gemini APIレスポンス
        """
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"🔄 Gemini API呼び出し (試行 {attempt}/{max_retries})")
                response = self.model.generate_content(prompt)
                return response
            except Exception as e:
                logger.warning(f"⚠️ API呼び出し失敗 (試行 {attempt}): {e}")
                if attempt == max_retries:
                    raise
        
        raise Exception("Gemini API呼び出しに失敗しました")
    
    def _extract_json_from_response(self, response_text: str) -> List[Dict[str, str]]:
        """
        レスポンスからJSONを抽出 (堅牢化版)
        
        【処理の流れ】
        1. マークダウンコードブロック除去
        2. 前後の不要な文字列除去
        3. エスケープ処理の修正
        4. JSONパース
        5. 失敗時は部分JSON抽出を試行
        
        Args:
            response_text: Gemini APIからのレスポンス
        
        Returns:
            タスクリスト
        """
        logger.info("🔍 JSON抽出開始...")
        
        # ステップ1: マークダウンコードブロック除去
        cleaned = re.sub(r'```json\s*', '', response_text)
        cleaned = re.sub(r'```\s*$', '', cleaned)
        cleaned = cleaned.strip()
        
        # ステップ2: JSON配列の抽出
        match = re.search(r'\[\s*\{.*\}\s*\]', cleaned, re.DOTALL)
        if match:
            cleaned = match.group(0)
            logger.info(f"✅ JSON配列を抽出 ({len(cleaned)} 文字)")
        else:
            logger.warning("⚠️ JSON配列パターンが見つかりません。全文をパース試行")
        
        # ステップ3: JSONパース試行
        try:
            tasks = json.loads(cleaned)
            logger.info(f"✅ JSON解析成功 ({len(tasks)}件のタスク)")
            return tasks
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON解析エラー: {e}")
            logger.error(f"エラー箇所付近: {cleaned[max(0, e.pos-100):e.pos+100]}")
            
            # ステップ4: 部分JSON抽出を試行
            return self._extract_partial_json(cleaned)
    
    def _extract_partial_json(self, text: str) -> List[Dict[str, str]]:
        """
        部分的なJSONオブジェクトを抽出 (フォールバック処理)
        
        Args:
            text: JSON文字列
        
        Returns:
            抽出できたタスクリスト
        """
        logger.warning("⚠️ 部分JSON抽出モードに切り替え")
        
        tasks = []
        # 個別のタスクオブジェクトを探す
        pattern = r'\{\s*"task_name"\s*:\s*"[^"]+"\s*,\s*"description"\s*:\s*"[^"]+"\s*\}'
        matches = re.finditer(pattern, text, re.DOTALL)
        
        for match in matches:
            try:
                task_json = match.group(0)
                task = json.loads(task_json)
                tasks.append(task)
                logger.info(f"✅ タスク抽出成功: {task['task_name'][:30]}...")
            except json.JSONDecodeError:
                continue
        
        if not tasks:
            logger.error("❌ 部分JSON抽出も失敗しました")
            # 最後の手段: エラー詳細を表示
            logger.error(f"レスポンス全文:\n{text[:2000]}...")
            raise ValueError("JSONの抽出に完全に失敗しました")
        
        logger.info(f"⚠️ 部分抽出完了 ({len(tasks)}件)")
        return tasks


class PMAgentV32Detailed:
    """
    PMAgent v32 Detailed - メインクラス (既存システム統合版)
    
    【設計思想】
    - 依存性注入の原則: SheetsManager等は外部から注入
    - インターフェース統一: 既存pm_agentと互換性確保
    - 非同期処理対応: async/awaitで将来拡張可能
    
    【運用ルール準拠】
    - 1000行以下に抑制
    - PEP 8準拠
    - Docstring完備
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初期化
        
        Args:
            api_key: Gemini API Key (オプション)
        """
        self.task_breakdown = TaskBreakdownEngine(api_key=api_key)
        logger.info("✅ PMAgentV32Detailed 初期化完了")
    
    def decompose_goal(
        self, 
        goal_description: str, 
        num_tasks: int = 8
    ) -> List[Dict[str, str]]:
        """
        ゴールをタスクに分解 (公開インターフェース)
        
        【既存システムとの互換性】
        このメソッド名は既存のpm_agent.pyと互換性があります
        
        Args:
            goal_description: ゴールの説明
            num_tasks: タスク数
            
        Returns:
            タスクリスト
        """
        logger.info("🚀 ゴール分解開始")
        logger.info(f"📝 ゴール: {goal_description[:100]}...")
        
        try:
            tasks = self.task_breakdown.breakdown_goal_to_detailed_tasks(
                goal_description=goal_description,
                num_tasks=num_tasks
            )
            
            # 結果表示
            logger.info("=" * 60)
            logger.info("📊 生成されたタスク:")
            for i, task in enumerate(tasks, 1):
                task_name = task.get('task_name', 'NO NAME')
                desc = task.get('description', '')
                desc_len = len(desc)
                logger.info(f"{i}. {task_name} ({desc_len}文字)")
            logger.info("=" * 60)
            
            return tasks
            
        except Exception as e:
            logger.error(f"❌ ゴール分解エラー: {e}", exc_info=True)
            raise


def main():
    """
    テスト実行
    
    【使い方】
    ```bash
    # 単体テスト
    python3 core_agents/pm_agent_v32_detailed.py
    
    # 環境変数設定が必要な場合
    export GEMINI_API_KEY='your-api-key'
    python3 core_agents/pm_agent_v32_detailed.py
    ```
    """
    print("=" * 60)
    print("PMAgent v32 Detailed - テスト実行")
    print("=" * 60)
    
    # テストゴール
    test_goal = """
    既存システムの完全理解と詳細要件定義の作成。
    
    既存のアーキテクチャ、データフロー、テストスイートを徹底的に調査し、
    新規開発における制約条件と活用可能な資産を明確化する。
    特に、既存資産100%活用戦略を確実にするため、各コンポーネントの
    具体的な動作、設定、制限事項を洗い出す。
    """
    
    try:
        agent = PMAgentV32Detailed()
        tasks = agent.decompose_goal(test_goal, num_tasks=8)
        
        print("\n✅ タスク生成成功!")
        print(f"生成件数: {len(tasks)}件")
        
        # 詳細度チェック
        total_chars = sum(len(t.get('description', '')) for t in tasks)
        avg_chars = total_chars / len(tasks) if tasks else 0
        print(f"平均文字数: {avg_chars:.0f}文字")
        
        # サンプル表示
        if tasks:
            print(f"\n【サンプル】最初のタスク:")
            print(f"タスク名: {tasks[0].get('task_name', 'N/A')}")
            print(f"説明: {tasks[0].get('description', 'N/A')[:200]}...")
        
    except ValueError as e:
        print(f"\n❌ 設定エラー: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ エラー発生: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())