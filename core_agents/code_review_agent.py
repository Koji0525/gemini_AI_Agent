# code_review_agent.py
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class CodeReviewAgent:
    """コードレビューAI - プログラムコードの改善を提案"""

    CODE_REVIEW_PROMPT = """あなたは優秀なソフトウェアエンジニアです。以下のプログラムコードをレビューし、改善点を提案してください。

【コード情報】
- ファイル名: {filename}
- エージェント名: {agent_name}
- コード行数: {line_count}
- ファイルサイズ: {file_size}文字

【レビュー観点】
1. バグやエラーの可能性がある部分
2. パフォーマンス改善できる部分  
3. 可読性・保守性向上の提案
4. セキュリティ上の問題
5. Pythonのベストプラクティス違反

【コード内容】
```python
{code_content}
【出力形式】

コードレビュー結果: {agent_name}
🔍 発見した問題点
問題1: [具体的な問題と場所]

問題2: [具体的な問題と場所]

💡 改善提案
提案1: [具体的な改善方法]

提案2: [具体的な改善方法]

🚀 推奨修正例

# 修正前
[問題のあるコード]

# 修正後  
[改善したコード]


📊 総合評価
[コードの品質を簡単に評価]"""


def __init__(self, browser_controller):
    self.browser = browser_controller


async def review_code(self, agent_name, code_data):
    """コードをレビューして改善提案"""
    try:
        logger.info(f"🔍 {agent_name} のコードレビュー開始")

        # プロンプト作成
        prompt = self.CODE_REVIEW_PROMPT.format(
            filename=code_data["filename"],
            agent_name=agent_name,
            line_count=code_data["content"].count("\n") + 1,
            file_size=len(code_data["content"]),
            code_content=code_data["content"][:3000],  # 最初の3000文字のみ
        )

        # AIにレビュー依頼
        await self.browser.send_prompt(prompt)
        success = await self.browser.wait_for_text_generation(max_wait=120)

        if not success:
            return None

        # 結果取得
        review_result = await self.browser.extract_latest_text_response()
        return review_result

    except Exception as e:
        logger.error(f"❌ コードレビューエラー: {e}")
        return None
