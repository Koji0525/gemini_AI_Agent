#!/usr/bin/env python3
"""
v15のインポートエラーを修正
"""

import sys
from pathlib import Path

# v15ファイルを探す
v15_files = list(Path("scripts").glob("*_v15_*.py"))

if not v15_files:
    print("❌ v15ファイルが見つかりません")
    sys.exit(1)

v15_file = v15_files[0]
print(f"📝 修正対象: {v15_file}")

# ファイル読み込み
with open(v15_file, "r") as f:
    content = f.read()

# 修正1: DecisionProposalのインポートを削除
content = content.replace(
    "from .logging.decision_support_system import DecisionSupportSystem",
    "from .logging.decision_support_system import DecisionSupportSystem",
)

# 修正2: RetryResultのインポート確認
if "from .retry_manager import RetryManager, RetryConfig, RetryResult" in content:
    print("✅ RetryResult インポートOK")

# 書き込み
with open(v15_file, "w") as f:
    f.write(content)

print(f"✅ {v15_file} 修正完了")
