#!/usr/bin/env python3
"""
Import抽出エンジン
タスクID: P1-T001

【責任】
- Pythonファイルからimport文を抽出
- 内部/外部モジュールの分類
- 依存関係の解析
"""

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


@dataclass
class ImportInfo:
    """Import情報を保持するデータクラス"""
    module: str
    name: Optional[str] = None
    alias: Optional[str] = None
    is_from_import: bool = False
    line_number: int = 0
    file_path: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'module': self.module,
            'name': self.name,
            'alias': self.alias,
            'is_from_import': self.is_from_import,
            'line_number': self.line_number,
            'file_path': self.file_path
        }


# テスト互換性のためのエイリアス
ImportRelation = ImportInfo


class ImportExtractor:
    """Import文抽出クラス"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.internal_prefixes = {
            'agents', 'tools', 'core_agents', 'browser_control',
            'configuration', 'task_executor', 'knowledge_system',
            'automation', 'scripts', 'utils'
        }
    
    def extract_imports(self, file_path: str) -> List[Dict[str, Any]]:
        """ファイルからimport文を抽出"""
        imports = []
        path = Path(file_path)
        
        if not path.exists():
            return imports
        
        try:
            content = path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            'module': alias.name,
                            'name': None,
                            'alias': alias.asname,
                            'is_from_import': False,
                            'line_number': node.lineno,
                            'file_path': str(file_path)
                        })
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append({
                            'module': module,
                            'name': alias.name,
                            'alias': alias.asname,
                            'is_from_import': True,
                            'line_number': node.lineno,
                            'file_path': str(file_path)
                        })
        except (SyntaxError, Exception):
            pass
        
        return imports
    
    def extract_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """ファイルまたはコード文字列からimport文を抽出"""
        if '\n' in str(file_path) or 'import ' in str(file_path):
            return self._extract_from_code(str(file_path))
        else:
            return self.extract_imports(str(file_path))
    
    def _extract_from_code(self, code: str) -> List[Dict[str, Any]]:
        """コード文字列からimport文を抽出"""
        imports = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            'module': alias.name,
                            'name': None,
                            'alias': alias.asname,
                            'is_from_import': False,
                            'line_number': node.lineno,
                            'file_path': '<code>'
                        })
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append({
                            'module': module,
                            'name': alias.name,
                            'alias': alias.asname,
                            'is_from_import': True,
                            'line_number': node.lineno,
                            'file_path': '<code>'
                        })
        except (SyntaxError, Exception):
            pass
        return imports
    
    def extract_from_directory(self, directory: Path) -> List[Dict[str, Any]]:
        """ディレクトリ内の全Pythonファイルからimport文を抽出"""
        all_imports = []
        dir_path = Path(directory)
        if dir_path.exists():
            for py_file in dir_path.rglob('*.py'):
                imports = self.extract_imports(str(py_file))
                all_imports.extend(imports)
        return all_imports
    
    def get_direct_dependencies(self, file_path: str) -> List[str]:
        """直接依存しているモジュールのリストを取得"""
        imports = self.extract_imports(file_path)
        modules = set()
        for imp in imports:
            module = imp['module']
            if module:
                top_module = module.split('.')[0]
                modules.add(top_module)
        return sorted(list(modules))
    
    def filter_internal_imports(self, imports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """内部モジュールのみをフィルタ"""
        internal = []
        for imp in imports:
            module = imp.get('module', '')
            top_module = module.split('.')[0] if module else ''
            if top_module in self.internal_prefixes:
                internal.append(imp)
        return internal
    
    def filter_external_imports(self, imports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """外部モジュールのみをフィルタ"""
        external = []
        for imp in imports:
            module = imp.get('module', '')
            top_module = module.split('.')[0] if module else ''
            if top_module and top_module not in self.internal_prefixes:
                external.append(imp)
        return external
    
    def get_imports_by_file(self, imports: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """ファイルごとにimportをグループ化"""
        by_file: Dict[str, List[Dict[str, Any]]] = {}
        for imp in imports:
            file_path = imp.get('file_path', '<unknown>')
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(imp)
        return by_file
    
    def get_imported_modules(self, imports: List[Dict[str, Any]]) -> Set[str]:
        """インポートされているモジュール名のセットを取得"""
        modules = set()
        for imp in imports:
            module = imp.get('module', '')
            if module:
                modules.add(module)
        return modules


def main():
    """テスト実行"""
    extractor = ImportExtractor()
    imports = extractor.extract_imports(__file__)
    print(f"このファイルのimport数: {len(imports)}")
    for imp in imports:
        print(f"  - {imp['module']}" + (f".{imp['name']}" if imp['name'] else ""))


if __name__ == '__main__':
    main()
