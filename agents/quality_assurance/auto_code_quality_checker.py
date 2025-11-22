"""
自動コード品質チェッカー
生成されたコードの品質を多角的に評価
"""

import sys
import os
import subprocess
import re
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class AutoCodeQualityChecker:
    """自動コード品質チェッカー"""
    
    def __init__(self):
        self.checks = []
        
    def check_all(self, output_path: str) -> Dict:
        """全チェックを実行"""
        print(f"\n{'=' * 80}")
        print(f"🔍 自動コード品質チェック")
        print('=' * 80)
        print(f"対象: {output_path}")
        print()
        
        results = {
            'overall_score': 0,
            'checks': {},
            'passed': True,
            'warnings': [],
            'errors': []
        }
        
        output_dir = Path(output_path)
        
        # 1. 構文チェック
        syntax_result = self._check_syntax(output_dir)
        results['checks']['syntax'] = syntax_result
        
        # 2. インポートチェック
        import_result = self._check_imports(output_dir)
        results['checks']['imports'] = import_result
        
        # 3. コーディング規約チェック
        style_result = self._check_coding_style(output_dir)
        results['checks']['style'] = style_result
        
        # 4. 複雑度チェック
        complexity_result = self._check_complexity(output_dir)
        results['checks']['complexity'] = complexity_result
        
        # 5. ドキュメントチェック
        doc_result = self._check_documentation(output_dir)
        results['checks']['documentation'] = doc_result
        
        # 総合スコア計算
        scores = [r['score'] for r in results['checks'].values()]
        results['overall_score'] = sum(scores) / len(scores)
        
        # 合否判定
        results['passed'] = results['overall_score'] >= 7.0
        
        # サマリー表示
        self._print_summary(results)
        
        return results
    
    def _check_syntax(self, output_dir: Path) -> Dict:
        """構文チェック"""
        print("  📝 構文チェック...")
        
        result = {
            'name': '構文チェック',
            'score': 10.0,
            'details': [],
            'passed': True
        }
        
        for py_file in output_dir.glob("*.py"):
            try:
                subprocess.run(
                    ['python3', '-m', 'py_compile', str(py_file)],
                    check=True,
                    capture_output=True,
                    text=True
                )
                result['details'].append(f"✅ {py_file.name}: OK")
            except subprocess.CalledProcessError as e:
                result['score'] = 0
                result['passed'] = False
                result['details'].append(f"❌ {py_file.name}: 構文エラー")
                result['details'].append(f"   {e.stderr}")
        
        print(f"     スコア: {result['score']:.1f}/10")
        return result
    
    def _check_imports(self, output_dir: Path) -> Dict:
        """インポートチェック"""
        print("  📦 インポートチェック...")
        
        result = {
            'name': 'インポートチェック',
            'score': 10.0,
            'details': [],
            'passed': True
        }
        
        for py_file in output_dir.glob("*.py"):
            content = py_file.read_text()
            
            # import文を抽出
            imports = re.findall(r'^(?:from|import)\s+(\S+)', content, re.MULTILINE)
            
            # 標準ライブラリ以外のインポートをチェック
            external_imports = []
            for imp in imports:
                module = imp.split('.')[0]
                if module not in ['sys', 'os', 're', 'json', 'datetime', 'pathlib', 'typing']:
                    external_imports.append(module)
            
            if external_imports:
                result['details'].append(f"⚠️  {py_file.name}: 外部ライブラリ {external_imports}")
                result['score'] -= 2
            else:
                result['details'].append(f"✅ {py_file.name}: 標準ライブラリのみ")
        
        print(f"     スコア: {result['score']:.1f}/10")
        return result
    
    def _check_coding_style(self, output_dir: Path) -> Dict:
        """コーディング規約チェック"""
        print("  🎨 コーディング規約チェック...")
        
        result = {
            'name': 'コーディング規約',
            'score': 10.0,
            'details': [],
            'passed': True
        }
        
        for py_file in output_dir.glob("*.py"):
            content = py_file.read_text()
            
            # 基本的なチェック
            lines = content.split('\n')
            
            # 1行の長さチェック
            long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 100]
            if long_lines:
                result['score'] -= 1
                result['details'].append(f"⚠️  {py_file.name}: 長い行 {len(long_lines)}箇所")
            
            # docstringチェック
            if '"""' in content or "'''" in content:
                result['details'].append(f"✅ {py_file.name}: docstring あり")
            else:
                result['score'] -= 2
                result['details'].append(f"⚠️  {py_file.name}: docstring なし")
        
        print(f"     スコア: {result['score']:.1f}/10")
        return result
    
    def _check_complexity(self, output_dir: Path) -> Dict:
        """複雑度チェック"""
        print("  🧩 複雑度チェック...")
        
        result = {
            'name': '複雑度',
            'score': 10.0,
            'details': [],
            'passed': True
        }
        
        for py_file in output_dir.glob("*.py"):
            content = py_file.read_text()
            
            # 簡易的な複雑度チェック
            # 関数の長さをチェック
            functions = re.findall(r'def \w+.*?(?=\ndef |\nclass |\Z)', content, re.DOTALL)
            
            long_functions = [f for f in functions if len(f.split('\n')) > 50]
            if long_functions:
                result['score'] -= 2
                result['details'].append(f"⚠️  {py_file.name}: 長い関数 {len(long_functions)}個")
            else:
                result['details'].append(f"✅ {py_file.name}: 適切な関数サイズ")
        
        print(f"     スコア: {result['score']:.1f}/10")
        return result
    
    def _check_documentation(self, output_dir: Path) -> Dict:
        """ドキュメントチェック"""
        print("  📚 ドキュメントチェック...")
        
        result = {
            'name': 'ドキュメント',
            'score': 10.0,
            'details': [],
            'passed': True
        }
        
        # README.md存在チェック
        readme = output_dir / "README.md"
        if readme.exists():
            result['details'].append("✅ README.md あり")
            
            # README.mdの内容チェック
            content = readme.read_text()
            if len(content) > 500:
                result['details'].append("✅ README.md 詳細")
            else:
                result['score'] -= 2
                result['details'].append("⚠️  README.md 簡潔すぎる")
        else:
            result['score'] = 0
            result['passed'] = False
            result['details'].append("❌ README.md なし")
        
        print(f"     スコア: {result['score']:.1f}/10")
        return result
    
    def _print_summary(self, results: Dict):
        """サマリー表示"""
        print()
        print("=" * 80)
        print("📊 品質チェック結果サマリー")
        print("=" * 80)
        
        for check_name, check_result in results['checks'].items():
            status = "✅" if check_result['passed'] else "❌"
            print(f"{status} {check_result['name']}: {check_result['score']:.1f}/10")
        
        print()
        print(f"総合スコア: {results['overall_score']:.1f}/10")
        print(f"合否: {'✅ 合格' if results['passed'] else '❌ 不合格'}")
        print("=" * 80)

