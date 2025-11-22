#!/bin/bash
# ナレッジベース表示（open削除版）

cd /workspaces/gemini_AI_Agent

python3 << PYTHON
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.knowledge_visualizer import KnowledgeVisualizer

visualizer = KnowledgeVisualizer()
html_path = visualizer.generate_report()

print(f"\n" + "=" * 80)
print(f"✅ レポート生成完了")
print("=" * 80)
print(f"\n📄 HTMLレポート:")
print(f"   {html_path}")
print(f"\n📖 ブラウザで開くには:")
print(f"   ポートパネルから「ポート転送」して、ファイルパスをブラウザに入力")
print(f"   または、VS Codeの「プレビュー」機能を使用")
print()

PYTHON

