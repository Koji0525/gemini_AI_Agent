#!/usr/bin/env python3
"""テンプレート文字列のエラーを完全修正"""

import re

def fix_all_template_errors():
    """すべてのテンプレート文字列エラーを修正"""
    
    # task_executor_enhanced.py を修正
    with open('agents/task_executor_enhanced.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 テンプレートエラーを検出中...")
    
    # 問題のあるテンプレート文字列を修正
    template_fixes = [
        # 単一の } をエスケープ
        (r'f"アイテム追加: {item}"', '"アイテム追加: {{item}}"'),
        (r'f"全アイテム: {obj.get_items()}"', '"全アイテム: {{obj.get_items()}}"'),
        (r"f'アイテム追加: {item}'", "'アイテム追加: {{item}}'"),
        (r"f'全アイテム: {obj.get_items()}'", "'全アイテム: {{obj.get_items()}}'"),
        
        # その他のフォーマット文字列問題
        (r'f"Hello from {name}!"', '"Hello from {{name}}!"'),
        (r"f'Hello from {name}!'", "'Hello from {{name}}!'"),
        
        # 三重引用符内のフォーマット問題
        (r'f"""', '"""'),
        (r"f'''", "'''"),
    ]
    
    fixed_count = 0
    for old, new in template_fixes:
        if old in content:
            content = content.replace(old, new)
            fixed_count += 1
            print(f"✅ 修正: {old} → {new}")
    
    # _render_template メソッドを安全なバージョンに置き換え
    safe_render_method = '''
    def _render_template(self, template: str, **kwargs) -> str:
        """安全なテンプレートレンダリング - フォーマットエラーを防止"""
        try:
            # まず単一の {} をエスケープ
            safe_template = template
            safe_template = safe_template.replace('{', '{{').replace('}', '}}')
            # 次に必要な変数を元に戻す
            for key, value in kwargs.items():
                placeholder = '{{' + key + '}}'
                safe_template = safe_template.replace('{{{{' + key + '}}}}', placeholder)
            
            return safe_template.format(**kwargs)
        except Exception as e:
            print(f"❌ テンプレートレンダリングエラー: {e}")
            print(f"   テンプレート: {template[:100]}...")
            print(f"   引数: {list(kwargs.keys())}")
            return template  # エラー時は元のテンプレートを返す
'''
    
    # 既存の _render_template メソッドを置き換え
    old_render_pattern = r'def _render_template\(.*?\) -> str:.*?return template\.format\(\*\*kwargs\)'
    if re.search(old_render_pattern, content, re.DOTALL):
        content = re.sub(old_render_pattern, safe_render_method, content, flags=re.DOTALL)
        print("✅ _render_template メソッドを安全なバージョンに置き換え")
    else:
        print("❌ _render_template メソッドが見つかりません")
    
    # ファイル保存
    with open('agents/task_executor_enhanced.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"🎯 修正完了: {fixed_count}個のテンプレートエラーを修正")
    return fixed_count > 0

if __name__ == "__main__":
    fix_all_template_errors()
