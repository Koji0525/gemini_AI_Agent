#!/usr/bin/env python3
"""テンプレートの安全性を強化"""

def create_safe_template_system():
    """安全なテンプレートシステムを作成"""
    
    safe_template_code = '''
import string
from typing import Dict, Any

class SafeTemplateRenderer:
    """安全なテンプレートレンダリングクラス"""
    
    @staticmethod
    def render(template: str, **kwargs) -> str:
        """安全にテンプレートをレンダリング"""
        try:
            # 方法1: string.Template を使用（最も安全）
            try:
                return string.Template(template).safe_substitute(**kwargs)
            except:
                pass
            
            # 方法2: 手動置換（フォールバック）
            result = template
            for key, value in kwargs.items():
                placeholder = '${' + key + '}'
                if placeholder in template:
                    result = result.replace(placeholder, str(value))
            
            # 方法3: フォーマット文字列（最終手段）
            if '{' in result or '}' in result:
                # 安全にエスケープ
                result = result.replace('{', '{{').replace('}', '}}')
                for key, value in kwargs.items():
                    result = result.replace('{{' + key + '}}', str(value))
            
            return result
            
        except Exception as e:
            print(f"❌ テンプレートレンダリングエラー: {e}")
            return template

def safe_render_template(template: str, **kwargs) -> str:
    """安全なテンプレートレンダリング関数"""
    return SafeTemplateRenderer.render(template, **kwargs)
'''

    # 新しい安全なテンプレートモジュールを作成
    with open('tools/safe_template.py', 'w', encoding='utf-8') as f:
        f.write(safe_template_code)
    
    print("✅ 安全なテンプレートシステムを作成")
    
    # task_executor_enhanced.py を更新して安全なテンプレートを使用
    with open('agents/task_executor_enhanced.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # インポートを追加
    if 'from tools.safe_template import safe_render_template' not in content:
        # ファイルの先頭にインポートを追加
        import_line = 'from tools.safe_template import safe_render_template'
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('import') or line.startswith('from'):
                continue
            else:
                lines.insert(i, import_line)
                break
        content = '\n'.join(lines)
    
    # _render_template メソッドを安全なバージョンに置き換え
    safe_render_method = '''
    def _render_template(self, template: str, **kwargs) -> str:
        """安全なテンプレートレンダリング"""
        return safe_render_template(template, **kwargs)
'''
    
    old_render_pattern = r'def _render_template\(.*?\) -> str:.*?return .*?'
    if re.search(old_render_pattern, content, re.DOTALL):
        content = re.sub(old_render_pattern, safe_render_method, content, flags=re.DOTALL)
        print("✅ _render_template を安全なバージョンに置き換え")
    
    with open('agents/task_executor_enhanced.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

if __name__ == "__main__":
    create_safe_template_system()
