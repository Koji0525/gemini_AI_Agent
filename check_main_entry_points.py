#!/usr/bin/env python3
"""
主要なエントリーポイントファイルを確認
"""
import ast
from pathlib import Path

def analyze_file(filepath):
    """ファイルの構造を分析"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        tree = ast.parse(code)
        
        # インポート文を抽出
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"from {module} import {alias.name}")
        
        # main関数の有無
        has_main = any(
            isinstance(node, ast.FunctionDef) and node.name == 'main'
            for node in ast.walk(tree)
        )
        
        # __main__ チェックの有無
        has_main_check = 'if __name__ == "__main__"' in code
        
        return {
            'imports': imports[:10],  # 最初の10個
            'import_count': len(imports),
            'has_main': has_main,
            'has_main_check': has_main_check
        }
    except Exception as e:
        return {'error': str(e)}

def main():
    entry_points = [
        'autonomous_system.py',
        'main_hybrid_fix.py',
        'safe_wordpress_executor.py',
        'scripts/run_multi_agent.py',
        'scripts/main_automator.py'
    ]
    
    print("=" * 70)
    print("🔍 主要エントリーポイントの分析")
    print("=" * 70)
    
    for ep in entry_points:
        filepath = Path(ep)
        if not filepath.exists():
            print(f"\n❌ {ep}: ファイルが見つかりません")
            continue
        
        print(f"\n📄 {ep}")
        info = analyze_file(filepath)
        
        if 'error' in info:
            print(f"  ❌ エラー: {info['error']}")
        else:
            print(f"  📦 インポート数: {info['import_count']}")
            print(f"  🔧 main関数: {'✅' if info['has_main'] else '❌'}")
            print(f"  🚀 __main__チェック: {'✅' if info['has_main_check'] else '❌'}")
            
            if info['imports']:
                print(f"  📋 主要インポート:")
                for imp in info['imports'][:5]:
                    print(f"    - {imp}")

if __name__ == '__main__':
    main()
