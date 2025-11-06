#!/usr/bin/env python3
"""
SelfLearningPipeline 修正
問題: 'SelfLearningPipeline' object has no attribute 'kb_manager'
解決: __init__ で kb_manager を保存
"""

import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

# 現在のファイルを確認
print("🔍 SelfLearningPipeline の __init__ 確認")
print("=" * 60)

with open('agents/self_healing/self_learning_pipeline.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if '__init__' in line or 'self.' in line:
        if i < 30:  # 最初の30行のみ
            print(f"{i:3d}: {line.rstrip()}")

print()
print("=" * 60)
print("�� 修正実行...")

# ファイル全文を読み込んで修正
with open('agents/self_healing/self_learning_pipeline.py', 'r') as f:
    content = f.read()

# __init__ メソッドを修正
if 'self.kb_manager = kb_manager' not in content:
    # __init__ 内で sheets_manager の後に追加
    content = content.replace(
        'self.sheets_manager = sheets_manager',
        'self.sheets_manager = sheets_manager\n        self.kb_manager = kb_manager'
    )
    
    with open('agents/self_healing/self_learning_pipeline.py', 'w') as f:
        f.write(content)
    
    print("✅ SelfLearningPipeline 修正完了")
    print("   追加: self.kb_manager = kb_manager")
else:
    print("ℹ️  既に修正済み")

print("=" * 60)
