#!/usr/bin/env python3
import os
import re
from pathlib import Path

def optimize_template(template_path):
    """テンプレートを最適化"""
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 標準的なフォーマットに統一
    optimizations = [
        # インデント統一
        (r'    """.*?"""', lambda m: '        ' + m.group(0).lstrip()),
        # 余分な空白除去
        (r'\n\s*\n\s*\n', '\n\n'),
        # 標準的なクラス構造
        (r'class \w+:\s*""".*?"""\s*def __init__', standard_class_structure),
    ]
    
    for pattern, replacement in optimizations:
        if callable(replacement):
            content = replacement(pattern, content)
        else:
            content = re.sub(pattern, replacement, content)
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)

def standard_class_structure(pattern, content):
    """標準的なクラス構造に変換"""
    def replacer(match):
        class_block = match.group(0)
        # 既に標準形式なら変更しない
        if 'def __init__(self):' in class_block:
            return class_block
        # コンストラクタを追加
        return class_block.replace('class \\1:', 'class \\1:\\n    def __init__(self):\\n        pass')
    
    return re.sub(pattern, replacer, content)

# 全テンプレート最適化
templates_dir = Path("/workspaces/gemini_AI_Agent/agents/templates")
for template in templates_dir.glob("*.py"):
    optimize_template(template)
    print(f"✅ {template.name} を最適化")
