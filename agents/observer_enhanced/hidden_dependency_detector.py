"""
隠れた依存関係検出器

要件定義書 FR-001 拡張機能:
- ファイルI/O依存の検出
- 環境変数依存の検出
- 外部コマンド実行の検出
- ネットワーク依存の検出
- データベース依存の検出

目標精度: 95%以上
処理時間: <50ms/file
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class HiddenDependency:
    """隠れた依存関係を表すデータクラス"""
    file_path: str
    line_number: int
    dependency_type: str  # 'file_io', 'env_var', 'subprocess', 'network', 'database'
    details: str
    severity: str  # 'low', 'medium', 'high', 'critical'


class HiddenDependencyDetector:
    """
    AST解析を用いて隠れた依存関係を検出
    
    検出対象:
    1. ファイルI/O: open(), Path(), read(), write()
    2. 環境変数: os.environ, os.getenv()
    3. subprocess: subprocess.run(), os.system()
    4. ネットワーク: requests, urllib, socket
    5. データベース: sqlite3, psycopg2など
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path('/workspaces/gemini_AI_Agent')
        
        # 検出パターン定義
        self.file_io_functions = {
            'open', 'read', 'write', 'readlines', 'writelines',
            'Path', 'glob', 'listdir', 'makedirs', 'remove'
        }
        
        self.env_var_access = {
            'getenv', 'environ', 'putenv', 'unsetenv'
        }
        
        self.subprocess_calls = {
            'system', 'popen', 'run', 'call', 'check_output',
            'Popen', 'subprocess'
        }
        
        self.network_modules = {
            'requests', 'urllib', 'http', 'socket', 'aiohttp'
        }
        
        self.database_modules = {
            'sqlite3', 'psycopg2', 'pymongo', 'mysql', 'redis'
        }
    
    def detect_file(self, file_path: Path) -> List[HiddenDependency]:
        """
        1ファイルの隠れた依存関係を検出
        
        Args:
            file_path: 解析対象のPythonファイル
            
        Returns:
            検出された隠れた依存関係のリスト
            
        処理時間: <50ms/file (目標)
        """
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            
            # AST走査
            for node in ast.walk(tree):
                # 1. ファイルI/O検出
                if isinstance(node, ast.Call):
                    deps = self._detect_file_io(node, file_path)
                    dependencies.extend(deps)
                    
                    deps = self._detect_subprocess(node, file_path)
                    dependencies.extend(deps)
                
                # 2. 環境変数アクセス検出
                if isinstance(node, (ast.Attribute, ast.Subscript)):
                    deps = self._detect_env_var(node, file_path)
                    dependencies.extend(deps)
                
                # 3. import文から外部依存検出
                if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    deps = self._detect_external_deps(node, file_path)
                    dependencies.extend(deps)
        
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
        
        return dependencies
    
    def _detect_file_io(self, node: ast.Call, file_path: Path) -> List[HiddenDependency]:
        """ファイルI/O操作を検出"""
        dependencies = []
        
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        
        if func_name in self.file_io_functions:
            # 引数からファイルパスを取得（可能なら）
            file_arg = None
            if node.args:
                first_arg = node.args[0]
                if isinstance(first_arg, ast.Constant):
                    file_arg = first_arg.value
            
            dep = HiddenDependency(
                file_path=str(file_path),
                line_number=node.lineno,
                dependency_type='file_io',
                details=f"Function: {func_name}, Target: {file_arg or 'dynamic'}",
                severity='medium' if file_arg else 'high'
            )
            dependencies.append(dep)
        
        return dependencies
    
    def _detect_env_var(self, node: ast.AST, file_path: Path) -> List[HiddenDependency]:
        """環境変数アクセスを検出"""
        dependencies = []
        
        # os.environ['KEY'] パターン
        if isinstance(node, ast.Subscript):
            if isinstance(node.value, ast.Attribute):
                if (isinstance(node.value.value, ast.Name) and 
                    node.value.value.id == 'os' and 
                    node.value.attr == 'environ'):
                    
                    var_name = None
                    if isinstance(node.slice, ast.Constant):
                        var_name = node.slice.value
                    
                    dep = HiddenDependency(
                        file_path=str(file_path),
                        line_number=node.lineno,
                        dependency_type='env_var',
                        details=f"Variable: {var_name or 'dynamic'}",
                        severity='critical' if not var_name else 'high'
                    )
                    dependencies.append(dep)
        
        # os.getenv() パターン
        if isinstance(node, ast.Attribute):
            if (isinstance(node.value, ast.Name) and 
                node.value.id == 'os' and 
                node.attr in self.env_var_access):
                
                dep = HiddenDependency(
                    file_path=str(file_path),
                    line_number=node.lineno,
                    dependency_type='env_var',
                    details=f"Function: os.{node.attr}()",
                    severity='high'
                )
                dependencies.append(dep)
        
        return dependencies
    
    def _detect_subprocess(self, node: ast.Call, file_path: Path) -> List[HiddenDependency]:
        """外部コマンド実行を検出"""
        dependencies = []
        
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        
        if func_name in self.subprocess_calls:
            # コマンド引数を取得（可能なら）
            command = None
            if node.args:
                first_arg = node.args[0]
                if isinstance(first_arg, ast.Constant):
                    command = first_arg.value
            
            dep = HiddenDependency(
                file_path=str(file_path),
                line_number=node.lineno,
                dependency_type='subprocess',
                details=f"Command: {command or 'dynamic'}",
                severity='critical'  # セキュリティリスクのため常にcritical
            )
            dependencies.append(dep)
        
        return dependencies
    
    def _detect_external_deps(self, node: ast.AST, file_path: Path) -> List[HiddenDependency]:
        """import文から外部依存を検出"""
        dependencies = []
        
        module_name = None
        if isinstance(node, ast.Import):
            module_name = node.names[0].name.split('.')[0]
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module_name = node.module.split('.')[0]
        
        if not module_name:
            return dependencies
        
        # ネットワーク依存
        if module_name in self.network_modules:
            dep = HiddenDependency(
                file_path=str(file_path),
                line_number=node.lineno,
                dependency_type='network',
                details=f"Module: {module_name}",
                severity='high'
            )
            dependencies.append(dep)
        
        # データベース依存
        if module_name in self.database_modules:
            dep = HiddenDependency(
                file_path=str(file_path),
                line_number=node.lineno,
                dependency_type='database',
                details=f"Module: {module_name}",
                severity='high'
            )
            dependencies.append(dep)
        
        return dependencies
    
    def scan_project(self) -> Dict[str, List[HiddenDependency]]:
        """
        プロジェクト全体をスキャン
        
        Returns:
            {file_path: [dependencies]} の辞書
            
        処理時間: 全ファイル数 × 50ms
        """
        results = {}
        
        python_files = list(self.project_root.rglob('*.py'))
        
        for file_path in python_files:
            # 除外パターン
            if any(x in str(file_path) for x in ['__pycache__', '.git', 'venv', 'backups', 'git_cleanup_backup']):
                continue
            
            dependencies = self.detect_file(file_path)
            if dependencies:
                results[str(file_path)] = dependencies
        
        return results
    
    def generate_report(self, dependencies: Dict[str, List[HiddenDependency]]) -> Dict:
        """
        検出結果のレポート生成
        
        Returns:
            統計情報を含むレポート
        """
        total_count = sum(len(deps) for deps in dependencies.values())
        
        by_type = {}
        by_severity = {}
        
        for deps in dependencies.values():
            for dep in deps:
                by_type[dep.dependency_type] = by_type.get(dep.dependency_type, 0) + 1
                by_severity[dep.severity] = by_severity.get(dep.severity, 0) + 1
        
        return {
            'total_dependencies': total_count,
            'files_with_dependencies': len(dependencies),
            'by_type': by_type,
            'by_severity': by_severity,
            'details': {
                file_path: [
                    {
                        'line': dep.line_number,
                        'type': dep.dependency_type,
                        'details': dep.details,
                        'severity': dep.severity
                    }
                    for dep in deps
                ]
                for file_path, deps in dependencies.items()
            }
        }


def main():
    """テスト実行"""
    detector = HiddenDependencyDetector()
    
    print("🔍 隠れた依存関係検出開始...")
    
    # プロジェクト全体スキャン
    dependencies = detector.scan_project()
    
    # レポート生成
    report = detector.generate_report(dependencies)
    
    print("\n" + "=" * 60)
    print("📊 検出結果サマリー")
    print("=" * 60)
    print(f"総検出数: {report['total_dependencies']}")
    print(f"対象ファイル数: {report['files_with_dependencies']}")
    print("\n【依存タイプ別】")
    for dep_type, count in report['by_type'].items():
        print(f"  {dep_type}: {count}")
    print("\n【重要度別】")
    for severity, count in report['by_severity'].items():
        print(f"  {severity}: {count}")
    
    # 重要度Criticalのみ詳細表示（最大10件）
    print("\n" + "=" * 60)
    print("⚠️  Critical依存関係の詳細 (上位10件)")
    print("=" * 60)
    critical_count = 0
    for file_path, deps in dependencies.items():
        critical_deps = [d for d in deps if d.severity == 'critical']
        if critical_deps and critical_count < 10:
            print(f"\n📄 {file_path}")
            for dep in critical_deps[:2]:  # ファイルごとに最大2件
                print(f"  Line {dep.line_number}: {dep.dependency_type} - {dep.details}")
                critical_count += 1
                if critical_count >= 10:
                    break


if __name__ == '__main__':
    try:
        main()
    except BrokenPipeError:
        # BrokenPipeError対策（パイプで出力を制限した時のエラーを無視）
        sys.stderr.close()
