
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
