"""人間とのコミュニケーション用シート作成"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))

from tools.sheets_manager import GoogleSheetsManager
from tools.safe_sheets_wrapper import SafeSheetsWrapper

sheets = GoogleSheetsManager()
safe_sheets = SafeSheetsWrapper(sheets)

# human_commands シート（人間→AI）
print("📝 human_commands シート準備中...")
headers = [["command_id", "timestamp", "command", "status"]]
safe_sheets.safe_append("human_commands", headers)
print("✅ human_commands シート準備完了")

# agent_questions シート（AI→人間）
print("📝 agent_questions シート準備中...")
headers = [["question_id", "timestamp", "question", "context", "status"]]
safe_sheets.safe_append("agent_questions", headers)
print("✅ agent_questions シート準備完了")
