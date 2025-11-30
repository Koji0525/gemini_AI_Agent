#!/usr/bin/env python3
"""
重複メソッド/クラス検知ツール
- 同じ名前のメソッド/クラスを検出
- プロジェクト全体をスキャン
- オブザーバーダッシュボードに統合
"""

import ast
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class DuplicateDetector:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        self.exclude_dirs = {
            'myenv', 'venv', '.venv', 'env',
            '__pycache__', '.git', '.pytest_cache',
            'node_modules', 'dist', 'build',
            'archived_orchestrators_*'
        }
        
        self.classes = defaultdict(list)
        self.methods = defaultdict(list)
        self.functions = defaultdict(list)
    
    def should_exclude(self, path):
        """除外ディレクトリチェック"""
        for exclude in self.exclude_dirs:
            if exclude.endswith('*'):
                if exclude[:-1] in str(path):
                    return True
            elif exclude in path.parts:
                return True
        return False
    
    def analyze_file(self, file_path):
        """単一ファイルを解析"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                relative_path = file_path.relative_to(self.root_dir)
                
                if isinstance(node, ast.ClassDef):
                    self.classes[node.name].append({
                        'file': str(relative_path),
                        'line': node.lineno,
                        'type': 'class'
                    })
                
                elif isinstance(node, ast.FunctionDef):
                    # クラス内メソッドか独立関数か判定
                    parent = getattr(node, '_parent', None)
                    
                    if isinstance(parent, ast.ClassDef):
                        full_name = f"{parent.name}.{node.name}"
                        self.methods[full_name].append({
                            'file': str(relative_path),
                            'line': node.lineno,
                            'class': parent.name,
                            'method': node.name,
                            'type': 'method'
                        })
                    else:
                        self.functions[node.name].append({
                            'file': str(relative_path),
                            'line': node.lineno,
                            'type': 'function'
                        })
            
            # 親ノード情報追加（メソッド判定用）
            for node in ast.walk(tree):
                for child in ast.iter_child_nodes(node):
                    child._parent = node
            
        except (SyntaxError, UnicodeDecodeError):
            pass  # 構文エラーやバイナリファイルはスキップ
    
    def scan_project(self):
        """プロジェクト全体をスキャン"""
        python_files = [
            f for f in self.root_dir.rglob('*.py')
            if not self.should_exclude(f)
        ]
        
        print(f"🔍 {len(python_files)}個のPythonファイルをスキャン中...")
        
        for i, file_path in enumerate(python_files, 1):
            if i % 100 == 0:
                print(f"  {i}/{len(python_files)}...")
            
            self.analyze_file(file_path)
        
        print(f"✅ スキャン完了")
    
    def find_duplicates(self):
        """重複を検出"""
        duplicates = {
            'classes': {},
            'methods': {},
            'functions': {},
            'summary': {}
        }
        
        # クラス重複
        for name, locations in self.classes.items():
            if len(locations) > 1:
                duplicates['classes'][name] = locations
        
        # メソッド重複
        for name, locations in self.methods.items():
            if len(locations) > 1:
                duplicates['methods'][name] = locations
        
        # 関数重複
        for name, locations in self.functions.items():
            if len(locations) > 1:
                duplicates['functions'][name] = locations
        
        # サマリー
        duplicates['summary'] = {
            'total_classes': len(self.classes),
            'duplicate_classes': len(duplicates['classes']),
            'total_methods': len(self.methods),
            'duplicate_methods': len(duplicates['methods']),
            'total_functions': len(self.functions),
            'duplicate_functions': len(duplicates['functions']),
            'scan_timestamp': datetime.now().isoformat()
        }
        
        return duplicates
    
    def save_report(self, output_file='duplicate_report.json'):
        """レポート保存"""
        duplicates = self.find_duplicates()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(duplicates, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 レポート保存: {output_file}")
        print(f"\n📊 サマリー:")
        print(f"  重複クラス: {duplicates['summary']['duplicate_classes']}個")
        print(f"  重複メソッド: {duplicates['summary']['duplicate_methods']}個")
        print(f"  重複関数: {duplicates['summary']['duplicate_functions']}個")
        
        return duplicates
    
    def print_duplicates(self):
        """重複を表示"""
        duplicates = self.find_duplicates()
        
        if duplicates['classes']:
            print("\n⚠️  重複クラス:")
            for name, locations in duplicates['classes'].items():
                print(f"\n  クラス: {name} ({len(locations)}箇所)")
                for loc in locations:
                    print(f"    - {loc['file']}:{loc['line']}")
        
        if duplicates['methods']:
            print("\n⚠️  重複メソッド:")
            for name, locations in list(duplicates['methods'].items())[:10]:
                print(f"\n  メソッド: {name} ({len(locations)}箇所)")
                for loc in locations:
                    print(f"    - {loc['file']}:{loc['line']}")
        
        if duplicates['functions']:
            print("\n⚠️  重複関数:")
            for name, locations in list(duplicates['functions'].items())[:10]:
                print(f"\n  関数: {name} ({len(locations)}箇所)")
                for loc in locations:
                    print(f"    - {loc['file']}:{loc['line']}")

if __name__ == '__main__':
    detector = DuplicateDetector()
    detector.scan_project()
    detector.save_report()
    detector.print_duplicates()
