#!/usr/bin/env python3
"""
インシデント情報をナレッジベースに登録
"""

incident_knowledge = {
    "title": "ファイル漏れ問題再発防止策 - INC-20251123-FILELEAK",
    "content": """... 詳細なコンテキスト ...""",
    "category": "incident_prevention",
    "tags": "git, ファイル漏れ, 再発防止, インシデント",
    "metadata": {
        "incident_id": "INC-20251123-FILELEAK",
        "occurred_date": "2025-11-23",
        "severity": "high",
        "prevention_measures": [
            "包括的コミットスクリプト",
            "ファイル漏れ検出システム",
            "多層防御体制",
        ],
    },
}

# ナレッジベース登録処理
# （既存のナレッジ登録スクリプトを呼び出す）
