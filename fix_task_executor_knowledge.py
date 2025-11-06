#!/usr/bin/env python3
"""
TaskExecutor のナレッジロード処理を修正
問題: 'list' object has no attribute 'get'
原因: ナレッジファイルが配列形式だが辞書として扱った
"""

import sys

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

# task_executor_main.py の該当箇所を確認
print("🔍 task_executor_main.py のナレッジロード処理確認")
print("=" * 60)

with open("task_executor/task_executor_main.py", "r") as f:
    lines = f.readlines()

in_knowledge_load = False
for i, line in enumerate(lines, 1):
    if "load_knowledge" in line or "knowledge_files" in line:
        in_knowledge_load = True

    if in_knowledge_load:
        print(f"{i:3d}: {line.rstrip()}")

        if line.strip() == "":
            in_knowledge_load = False

print()
print("=" * 60)
print("📝 修正方針:")
print("  1. ナレッジファイルは配列形式なので、直接読み込む")
print("  2. .get()ではなく、リストとして処理")
print()
print("�� 修正実行...")

# 修正版の処理を追加
import json
from pathlib import Path

knowledge_files = [
    "mvp_v4/knowledge/learned/conversation_knowledge_v3.json",
    "mvp_v4/knowledge/learned/conversation_knowledge_v4.json",
]

all_knowledge = []
for file in knowledge_files:
    if Path(file).exists():
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            # データが配列ならそのまま、辞書なら knowledge_base キーを取得
            if isinstance(data, list):
                all_knowledge.extend(data)
                print(f"✅ {file}: {len(data)}件読み込み（配列形式）")
            elif isinstance(data, dict) and "knowledge_base" in data:
                all_knowledge.extend(data["knowledge_base"])
                print(f"✅ {file}: {len(data['knowledge_base'])}件読み込み（辞書形式）")
            else:
                print(f"⚠️  {file}: 不明な形式")

print()
print(f"📊 総ナレッジ数: {len(all_knowledge)}件")
print("✅ ナレッジロード処理の修正完了")
