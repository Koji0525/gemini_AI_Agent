#!/usr/bin/env python3
"""
生成コード品質確認システム
Claude APIで生成されたコードの品質を自動評価
"""
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

import ast
import subprocess
from pathlib import Path
from typing import Dict, Any, List


class CodeQualityChecker:
    """コード品質チェッカー"""
    
    def __init__(self):
        self.checks = []
    
    def check_file(self, filepath: str) -> Dict[str, Any]:
        """ファイルの品質を総合評価"""
        path = Path(filepath)
        
        if not path.exists():
            return {'error': 'ファイルが見つかりません', 'filename': filepath}
        
        if not filepath.endswith('.py'):
            return {'error': 'Pythonファイルではありません', 'filename': path.name, 'score': 0, 'grade': 'N/A'}
        
        results = {
            'filepath': str(path),
            'filename': path.name,
            'checks': {},
            'score': 0,
            'grade': ''
        }
        
        # 1. 基本情報
        results['checks']['basic'] = self._check_basic(path)
        
        # 2. 構文チェック
        results['checks']['syntax'] = self._check_syntax(path)
        
        # 3. 構造チェック
        results['checks']['structure'] = self._check_structure(path)
        
        # 4. 実装度チェック
        results['checks']['implementation'] = self._check_implementation(path)
        
        # 5. 品質チェック
        results['checks']['quality'] = self._check_quality(path)
        
        # 総合スコア計算
        results['score'] = self._calculate_score(results['checks'])
        results['grade'] = self._get_grade(results['score'])
        
        return results
    
    def _check_basic(self, path: Path) -> Dict:
        """基本情報チェック"""
        stats = path.stat()
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
        
        return {
            'size_bytes': stats.st_size,
            'line_count': len(lines),
            'char_count': len(content),
            'status': 'ok'
        }
    
    def _check_syntax(self, path: Path) -> Dict:
        """構文チェック"""
        try:
            result = subprocess.run(
                ['python3', '-m', 'py_compile', str(path)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return {
                'valid': result.returncode == 0,
                'error': result.stderr if result.returncode != 0 else None,
                'status': 'ok' if result.returncode == 0 else 'error'
            }
        except Exception as e:
            return {'valid': False, 'error': str(e), 'status': 'error'}
    
    def _check_structure(self, path: Path) -> Dict:
        """構造チェック（AST解析）"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            classes = []
            functions = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    classes.append({
                        'name': node.name,
                        'methods': methods,
                        'method_count': len(methods)
                    })
                elif isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                    functions.append(node.name)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(ast.unparse(node))
            
            return {
                'class_count': len(classes),
                'function_count': len(functions),
                'import_count': len(imports),
                'classes': classes,
                'functions': functions,
                'status': 'ok'
            }
        except Exception as e:
            return {'error': str(e), 'status': 'error'}
    
    def _check_implementation(self, path: Path) -> Dict:
        """実装度チェック"""
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        total_lines = len(content.splitlines())
        todo_count = content.count('TODO')
        pass_count = content.count('pass')
        
        # 実装率の推定（簡易版）
        implementation_rate = 100.0
        if total_lines > 0:
            penalty = (todo_count * 5 + pass_count * 2)
            implementation_rate = max(0, 100 - (penalty / total_lines * 100))
        
        return {
            'todo_count': todo_count,
            'pass_count': pass_count,
            'implementation_rate': round(implementation_rate, 1),
            'status': 'good' if implementation_rate >= 80 else 'warning'
        }
    
    def _check_quality(self, path: Path) -> Dict:
        """品質チェック"""
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 品質指標
        has_docstring = '"""' in content or "'''" in content
        has_type_hints = ': ' in content and '->' in content
        has_error_handling = 'try:' in content or 'except' in content
        
        quality_score = 0
        if has_docstring:
            quality_score += 30
        if has_type_hints:
            quality_score += 30
        if has_error_handling:
            quality_score += 40
        
        return {
            'has_docstring': has_docstring,
            'has_type_hints': has_type_hints,
            'has_error_handling': has_error_handling,
            'quality_score': quality_score,
            'status': 'good' if quality_score >= 60 else 'warning'
        }
    
    def _calculate_score(self, checks: Dict) -> int:
        """総合スコアを計算"""
        score = 0
        
        # 構文チェック（30点）
        if checks['syntax'].get('valid'):
            score += 30
        
        # 構造（20点）
        structure = checks.get('structure', {})
        if structure.get('class_count', 0) > 0:
            score += 10
        if structure.get('function_count', 0) + sum(c.get('method_count', 0) for c in structure.get('classes', [])) >= 5:
            score += 10
        
        # 実装度（30点）
        impl = checks.get('implementation', {})
        impl_rate = impl.get('implementation_rate', 0)
        score += int(impl_rate * 0.3)
        
        # 品質（20点）
        quality = checks.get('quality', {})
        score += int(quality.get('quality_score', 0) * 0.2)
        
        return min(100, score)
    
    def _get_grade(self, score: int) -> str:
        """スコアから評価を取得"""
        if score >= 90:
            return 'A（優秀）'
        elif score >= 80:
            return 'B（良好）'
        elif score >= 70:
            return 'C（可）'
        elif score >= 60:
            return 'D（要改善）'
        else:
            return 'F（不可）'
    
    def print_report(self, results: Dict):
        """レポートを表示"""
        print(f"\n{'='*60}")
        print(f"📊 コード品質レポート")
        print(f"{'='*60}")
        print(f"\nファイル: {results['filename']}")
        print(f"総合スコア: {results['score']}/100")
        print(f"評価: {results['grade']}")
        
        print(f"\n📋 詳細:")
        
        # 基本情報
        basic = results['checks']['basic']
        print(f"  ファイルサイズ: {basic['size_bytes']:,} bytes")
        print(f"  行数: {basic['line_count']}")
        
        # 構文
        syntax = results['checks']['syntax']
        print(f"  構文チェック: {'✅ OK' if syntax['valid'] else '❌ NG'}")
        
        # 構造
        structure = results['checks']['structure']
        if 'class_count' in structure:
            print(f"  クラス数: {structure['class_count']}")
            print(f"  関数/メソッド数: {structure['function_count'] + sum(c.get('method_count', 0) for c in structure.get('classes', []))}")
        
        # 実装度
        impl = results['checks']['implementation']
        print(f"  実装率: {impl['implementation_rate']}%")
        print(f"  TODO数: {impl['todo_count']}")
        
        # 品質
        quality = results['checks']['quality']
        print(f"  Docstring: {'✅' if quality['has_docstring'] else '❌'}")
        print(f"  Type hints: {'✅' if quality['has_type_hints'] else '❌'}")
        print(f"  エラーハンドリング: {'✅' if quality['has_error_handling'] else '❌'}")
        
        print(f"\n{'='*60}\n")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("使用方法: python code_quality_checker.py <ファイルパス>")
        sys.exit(1)
    
    checker = CodeQualityChecker()
    results = checker.check_file(sys.argv[1])
    checker.print_report(results)
