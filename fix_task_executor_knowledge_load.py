#!/usr/bin/env python3
"""
TaskExecutor のナレッジロード処理を修正
"""

import sys

sys.path.insert(0, "/workspaces/gemini_AI_Agent")

print("🔧 TaskExecutor ナレッジロード修正")
print("=" * 60)

# task_executor_main.py を読み込み
with open("task_executor/task_executor_main.py", "r", encoding="utf-8") as f:
    content = f.read()

# 問題のある箇所を修正
if "'list' object has no attribute 'get'" in content or "knowledge_files" in content:
    # ナレッジロード部分を安全な実装に置き換え
    old_pattern = """            data = json.load(f)
            self.knowledge_base.extend(data.get('knowledge_base', []))"""

    new_pattern = """            data = json.load(f)
            # データ形式を判定して適切に処理
            if isinstance(data, list):
                self.knowledge_base.extend(data)
            elif isinstance(data, dict) and 'knowledge_base' in data:
                self.knowledge_base.extend(data['knowledge_base'])"""

    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)

        with open("task_executor/task_executor_main.py", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ ナレッジロード処理を修正しました")
    else:
        print("ℹ️  既に修正済みか、パターンが見つかりません")
else:
    print("ℹ️  問題のあるコードが見つかりません")

print("=" * 60)
