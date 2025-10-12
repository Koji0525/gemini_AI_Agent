#!/usr/bin/env python3
"""
実際に使われているファイルを特定するツール
（import文を追跡）
"""
import ast
import os
from pathlib import Path
from collections import defaultdict

class ImportTracker:
    """import文を追跡してファイルの依存関係を可視化"""
    
    def __init__(self):
        self.root = Path(".")
        self.imports = defaultdict(set)  # ファイル -> importしているモジュール
        self.imported_by = defaultdict(set)  # モジュール -> importされているファイル
        
    def analyze_imports(self, file_path):
        """1つのファイルのimport文を解析"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
            
            return imports
        except:
            return set()
    
    def scan_project(self):
        """プロジェクト全体をスキャン"""
        print("🔍 プロジェクト全体のimport文をスキャン中...\n")
        
        for file in self.root.rglob("*.py"):
            if '__pycache__' in str(file):
                continue
            
            imports = self.analyze_imports(file)
            self.imports[str(file)] = imports
            
            # 逆引き辞書も作成
            for imp in imports:
                self.imported_by[imp].add(str(file))
    
    def find_entry_points(self):
        """エントリーポイント（メインスクリプト）を検出"""
        print("=" * 80)
        print("🚀 エントリーポイント（実行可能なメインファイル）")
        print("=" * 80)
        
        entry_points = []
        
        for file in self.root.glob("*.py"):
            if file.name.startswith(('main_', 'run_', 'test_')):
                entry_points.append(file)
        
        for i, entry in enumerate(sorted(entry_points), 1):
            print(f"{i}. {entry}")
            
        return entry_points
    
    def trace_dependencies(self, entry_point):
        """エントリーポイントから依存ファイルをたどる"""
        visited = set()
        to_visit = [str(entry_point)]
        dependencies = []
        
        while to_visit:
            current = to_visit.pop(0)
            if current in visited:
                continue
            
            visited.add(current)
            dependencies.append(current)
            
            # このファイルがimportしているモジュール
            imports = self.imports.get(current, set())
            
            # ローカルモジュールを探す
            for imp in imports:
                # モジュール名をファイルパスに変換
                possible_paths = [
                    f"{imp}.py",
                    f"{imp}/__init__.py",
                ]
                
                for path in possible_paths:
                    if Path(path).exists() and str(path) not in visited:
                        to_visit.append(str(path))
        
        return dependencies
    
    def generate_dependency_report(self):
        """依存関係レポート生成"""
        entry_points = self.find_entry_points()
        
        print("\n" + "=" * 80)
        print("📊 各エントリーポイントの依存ファイル")
        print("=" * 80)
        
        all_used_files = set()
        
        for entry in entry_points:
            deps = self.trace_dependencies(entry)
            all_used_files.update(deps)
            
            print(f"\n📦 {entry.name} が使用するファイル:")
            for dep in sorted(deps)[:10]:  # 最初の10個
                print(f"  - {dep}")
            if len(deps) > 10:
                print(f"  ... 他 {len(deps) - 10} ファイル")
        
        # 使われていないファイルを検出
        print("\n" + "=" * 80)
        print("🗑️ 使われていない可能性のあるファイル")
        print("=" * 80)
        
        all_files = set(str(f) for f in self.root.rglob("*.py") if '__pycache__' not in str(f))
        unused = all_files - all_used_files
        
        if unused:
            for file in sorted(list(unused))[:20]:  # 最初の20個
                print(f"  - {file}")
            if len(unused) > 20:
                print(f"  ... 他 {len(unused) - 20} ファイル")
        else:
            print("✅ 全てのファイルが使用されています")
        
        return {
            'used_files': list(all_used_files),
            'unused_files': list(unused)
        }

if __name__ == "__main__":
    tracker = ImportTracker()
    tracker.scan_project()
    report = tracker.generate_dependency_report()
    
    # レポート保存
    import json
    with open('dependency_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("\n💾 詳細レポートを dependency_report.json に保存しました")
