"""
Import文抽出エンジン
AST（抽象構文木）を使用してPythonファイルのimport関係を抽出

実装ファイル: agents/observer_enhanced/import_extractor.py
行数目標: 500行
依存: ast (標準ライブラリ)
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict, Set, Optional
from dataclasses import dataclass
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ImportRelation:
    """Import関係を表すデータクラス"""
    source_file: str        # インポート元ファイル
    module: str             # インポートされるモジュール
    names: List[str]        # インポートされる名前のリスト
    import_type: str        # 'import' or 'from'
    line_number: int        # インポート文の行番号
    alias: Optional[str]    # エイリアス（as XXX）
    
    def __repr__(self):
        if self.import_type == 'import':
            return f"{self.source_file}:{self.line_number} import {self.module}"
        else:
            names_str = ', '.join(self.names)
            return f"{self.source_file}:{self.line_number} from {self.module} import {names_str}"
    
    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return {
            'source_file': self.source_file,
            'module': self.module,
            'names': self.names,
            'import_type': self.import_type,
            'line_number': self.line_number,
            'alias': self.alias
        }


class ImportExtractor:
    """
    Import文抽出エンジン
    
    使用例:
```python
    extractor = ImportExtractor()
    imports = extractor.extract_from_file('agents/pm_agent.py')
    
    for imp in imports:
        print(f"{imp.source_file} imports {imp.module}")
```
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        初期化
        
        Args:
            project_root: プロジェクトルートパス（デフォルト: 自動検出）
        """
        if project_root is None:
            self.project_root = Path('/workspaces/gemini_AI_Agent')
        else:
            self.project_root = Path(project_root)
        
        self.cache: Dict[str, List[ImportRelation]] = {}
        
        logger.info(f"ImportExtractor initialized: {self.project_root}")
    
    def extract_from_file(self, file_path: Path) -> List[ImportRelation]:
        """
        1つのファイルからimport文を抽出
        
        Args:
            file_path: Pythonファイルのパス
        
        Returns:
            ImportRelationのリスト
        
        処理時間目標: <50ms/file
        """
        file_path = Path(file_path)
        
        # キャッシュチェック
        cache_key = str(file_path)
        if cache_key in self.cache:
            logger.debug(f"Cache hit: {file_path}")
            return self.cache[cache_key]
        
        # ファイル存在確認
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return []
        
        # ファイル読み込み
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return []
        
        # AST解析
        imports = self._parse_imports(source_code, str(file_path))
        
        # キャッシュ保存
        self.cache[cache_key] = imports
        
        logger.debug(f"Extracted {len(imports)} imports from {file_path}")
        
        return imports
    
    def _parse_imports(self, source_code: str, source_file: str) -> List[ImportRelation]:
        """
        ソースコードをASTで解析してimport文を抽出
        
        Args:
            source_code: Pythonソースコード
            source_file: ファイルパス（エラー表示用）
        
        Returns:
            ImportRelationのリスト
        """
        imports = []
        
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            logger.error(f"Syntax error in {source_file}: {e}")
            return []
        
        for node in ast.walk(tree):
            # import XXX
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(ImportRelation(
                        source_file=source_file,
                        module=alias.name,
                        names=[alias.name],
                        import_type='import',
                        line_number=node.lineno,
                        alias=alias.asname
                    ))
            
            # from XXX import YYY
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ''
                names = [alias.name for alias in node.names]
                
                imports.append(ImportRelation(
                    source_file=source_file,
                    module=module,
                    names=names,
                    import_type='from',
                    line_number=node.lineno,
                    alias=None
                ))
        
        return imports
    
    def extract_from_directory(
        self, 
        directory: Path, 
        pattern: str = '**/*.py',
        exclude_patterns: Optional[List[str]] = None
    ) -> List[ImportRelation]:
        """
        ディレクトリ配下の全Pythonファイルからimport文を抽出
        
        Args:
            directory: 対象ディレクトリ
            pattern: ファイルパターン（glob形式）
            exclude_patterns: 除外パターンのリスト
        
        Returns:
            ImportRelationのリスト（全ファイル統合）
        """
        directory = Path(directory)
        
        if exclude_patterns is None:
            exclude_patterns = ['tests/**', 'backups/**', '__pycache__/**']
        
        all_imports = []
        file_count = 0
        
        logger.info(f"Scanning directory: {directory}")
        
        for file_path in directory.glob(pattern):
            # 除外パターンチェック
            should_exclude = False
            for exclude_pattern in exclude_patterns:
                if file_path.match(exclude_pattern):
                    should_exclude = True
                    break
            
            if should_exclude:
                logger.debug(f"Excluded: {file_path}")
                continue
            
            # import抽出
            imports = self.extract_from_file(file_path)
            all_imports.extend(imports)
            file_count += 1
        
        logger.info(f"Scanned {file_count} files, found {len(all_imports)} imports")
        
        return all_imports
    
    def get_imported_modules(self, imports: List[ImportRelation]) -> Set[str]:
        """
        import文リストから、インポートされているモジュール名の集合を取得
        
        Args:
            imports: ImportRelationのリスト
        
        Returns:
            モジュール名の集合
        """
        return {imp.module for imp in imports if imp.module}
    
    def get_imports_by_file(
        self, 
        imports: List[ImportRelation]
    ) -> Dict[str, List[ImportRelation]]:
        """
        ファイルごとにimport文をグループ化
        
        Args:
            imports: ImportRelationのリスト
        
        Returns:
            {ファイルパス: ImportRelationのリスト}
        """
        result = {}
        
        for imp in imports:
            if imp.source_file not in result:
                result[imp.source_file] = []
            result[imp.source_file].append(imp)
        
        return result
    
    def filter_internal_imports(
        self, 
        imports: List[ImportRelation]
    ) -> List[ImportRelation]:
        """
        プロジェクト内部のimportのみをフィルタリング
        
        Args:
            imports: ImportRelationのリスト
        
        Returns:
            内部importのみのリスト
        """
        internal_prefixes = ['agents', 'tools', 'tests']
        
        return [
            imp for imp in imports
            if any(imp.module.startswith(prefix) for prefix in internal_prefixes)
        ]
    
    def filter_external_imports(
        self, 
        imports: List[ImportRelation]
    ) -> List[ImportRelation]:
        """
        外部ライブラリのimportのみをフィルタリング
        
        Args:
            imports: ImportRelationのリスト
        
        Returns:
            外部importのみのリスト
        """
        internal_imports = self.filter_internal_imports(imports)
        internal_modules = {imp.module for imp in internal_imports}
        
        return [
            imp for imp in imports
            if imp.module not in internal_modules
        ]
    
    def get_dependency_count(
        self, 
        imports: List[ImportRelation]
    ) -> Dict[str, int]:
        """
        ファイルごとの依存関係数を取得
        
        Args:
            imports: ImportRelationのリスト
        
        Returns:
            {ファイルパス: 依存数}
        """
        imports_by_file = self.get_imports_by_file(imports)
        
        return {
            file_path: len(file_imports)
            for file_path, file_imports in imports_by_file.items()
        }
    
    def find_circular_imports(
        self, 
        imports: List[ImportRelation]
    ) -> List[List[str]]:
        """
        循環importを検出（簡易版）
        
        Args:
            imports: ImportRelationのリスト
        
        Returns:
            循環しているファイルパスのリスト
        
        Note: これは簡易実装。完全な検出にはグラフアルゴリズムが必要
        """
        # TODO: Phase 1 Day 2でGraphBuilderを使った完全実装
        logger.warning("Circular import detection is simplified in this version")
        return []
    
    def export_to_dict(self, imports: List[ImportRelation]) -> Dict:
        """
        import文リストを辞書形式でエクスポート
        
        Args:
            imports: ImportRelationのリスト
        
        Returns:
            辞書形式のデータ
        """
        return {
            'total_imports': len(imports),
            'unique_modules': len(self.get_imported_modules(imports)),
            'imports': [imp.to_dict() for imp in imports]
        }
    
    def clear_cache(self):
        """キャッシュをクリア"""
        self.cache.clear()
        logger.info("Cache cleared")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# コマンドライン実行用
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    """コマンドライン実行"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import文抽出ツール')
    parser.add_argument('file_or_dir', help='ファイルまたはディレクトリパス')
    parser.add_argument('--verbose', '-v', action='store_true', help='詳細出力')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    extractor = ImportExtractor()
    path = Path(args.file_or_dir)
    
    if path.is_file():
        imports = extractor.extract_from_file(path)
        print(f"📄 ファイル: {path}")
    elif path.is_dir():
        imports = extractor.extract_from_directory(path)
        print(f"📁 ディレクトリ: {path}")
    else:
        print(f"❌ パスが見つかりません: {path}")
        sys.exit(1)
    
    print(f"📊 総import数: {len(imports)}")
    print(f"📦 ユニークモジュール数: {len(extractor.get_imported_modules(imports))}")
    print()
    
    # 内部/外部の分類
    internal = extractor.filter_internal_imports(imports)
    external = extractor.filter_external_imports(imports)
    
    print(f"🏠 内部import: {len(internal)}")
    print(f"🌐 外部import: {len(external)}")
    print()
    
    # 詳細表示
    if args.verbose:
        print("詳細:")
        for imp in imports[:20]:  # 最初の20件
            print(f"  {imp}")


if __name__ == '__main__':
    main()

